import pickle

from django.tasks import TaskResultStatus
from django.urls import reverse

from randomizer.logic.check_list import CHECK_ROWS
from randomizer.logic.offset_preview import get_ordered_lists
import binascii
import json
import logging
import os
import random
import string
import tempfile
import shutil

import Wii
import nlzss

from django.conf import settings
from django.core.cache import cache
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponse,
    HttpResponseNotFound,
    QueryDict,
)
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from randomizer.types.flags import FlagError
from randomizer.logic.validation import validate_settings, SettingsValidationError
from randomizer.types.flag_categories import CATEGORIES, PRESETS
from randomizer.types.patch import PatchJSONEncoder

from .models import Seed, Patch
from .forms import GenerateForm
from .main import VERSION
from .tasks import generate_seed_task
from .types.settings import Settings
from .types.flags import Flag, CategorizationFlag, CategorizationFlagWithOrdinance, BooleanFlag, RangeFlag, SelectOneFlag

logger = logging.getLogger(__name__)

class EmptyMixin:
    pass

if settings.LOGIN_REQUIRED:
    MixinClass = LoginRequiredMixin
else:
    MixinClass = EmptyMixin


def _build_flag_json_data(f: type[Flag], letter, flag_to_subcategory: dict[type[Flag], str] | None = None):
    flag = f()

    d = {
        "subcategory": letter,
        "id": flag.id,
        "modes": flag.modes.copy(),
        "type": flag.type,
    }
    if isinstance(flag, (CategorizationFlag, CategorizationFlagWithOrdinance)):
        d["options"] = flag.options_dict
        d["default"] = flag.default_dict
    elif isinstance(flag, SelectOneFlag):
        d["choices"] = flag.choices_dict
        d["default"] = flag.default_dict
    elif isinstance(flag, RangeFlag):
        d["default"] = flag.default
        d["min"] = flag.min_value
        d["max"] = flag.max_value
    elif isinstance(flag, BooleanFlag):
        d["default"] = flag.default
    else:
        raise NotImplementedError("Unknown flag type: {}".format(type(flag)))

    if flag._requires_all:
        d["requires_all"] = _serialize_requirements(flag._requires_all, flag_to_subcategory)
    if flag._requires_any:
        d["requires_any"] = _serialize_requirements(flag._requires_any, flag_to_subcategory)
    if flag._disabled_if_all:
        d["disabled_if_all"] = _serialize_requirements(flag._disabled_if_all, flag_to_subcategory)

    return d


def _serialize_requirements(requirements: list, flag_to_subcategory: dict[type[Flag], str] | None = None) -> list:
    """Serialize flag requirements to JSON-compatible format."""
    result = []
    for req in requirements:
        flag_inst, required_value = req
        req_data = {"flag_id": flag_inst.id}

        if flag_to_subcategory:
            flag_class = type(flag_inst)
            if flag_class in flag_to_subcategory:
                req_data["subcategory"] = flag_to_subcategory[flag_class]

        if isinstance(flag_inst, BooleanFlag):
            req_data["type"] = "boolean"
            req_data["value"] = required_value
        elif isinstance(flag_inst, SelectOneFlag):
            req_data["type"] = "select_one"
            req_data["values"] = [v.name for v in required_value] if isinstance(required_value, list) else [required_value.name]

        result.append(req_data)
    return result


FLAG_TO_SUBCATEGORY: dict[type[Flag], str] = {}
for category in CATEGORIES:
    for subcategory in category().subcategories:
        sub_inst = subcategory()
        for flag in sub_inst.flags:
            FLAG_TO_SUBCATEGORY[flag] = sub_inst.id

FLAGS = []
for category in CATEGORIES:
    for subcategory in category().subcategories:
        sub_inst = subcategory()
        for flag in sub_inst.flags:
            FLAGS.append(_build_flag_json_data(flag, sub_inst.id, FLAG_TO_SUBCATEGORY))


def _build_categories_for_template() -> list[dict]:
    """Build category data structure for the options template."""
    result = []
    for category_cls in CATEGORIES:
        cat_inst = category_cls()
        cat_data = {
            "name": cat_inst.name,
            "subcategories": [],
            "flags": [],
        }

        for subcategory_cls in cat_inst.subcategories:
            sub_inst = subcategory_cls()
            sub_data = {
                "name": sub_inst.name,
                "flags": [],
            }
            for flag_cls in sub_inst.flags:
                flag_inst = flag_cls()
                sub_data["flags"].append({
                    "name": flag_inst.name,
                    "description": flag_inst.description,
                    "id": flag_inst.id,
                })
            cat_data["subcategories"].append(sub_data)

        for flag_cls in cat_inst.flags:
            flag_inst = flag_cls()
            cat_data["flags"].append({
                "name": flag_inst.name,
                "description": flag_inst.description,
                "id": flag_inst.id,
            })

        result.append(cat_data)
    return result


CATEGORIES_FOR_TEMPLATE = _build_categories_for_template()


class RandomizerView(MixinClass, TemplateView):
    """Base class for views that generate a ROM, i.e. randomizer and patch-from-hash views. This gets common context data."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["version"] = VERSION
        context["debug_enabled"] = settings.DEBUG
        context["beta_site"] = settings.BETA
        context["categories"] = CATEGORIES
        context["presets"] = PRESETS
        context["flags"] = FLAGS

        if settings.DEBUG:
            context["offset_preview_data"] = json.dumps(get_ordered_lists())

        return context


class AboutView(RandomizerView):
    template_name = "randomizer/about.html"


class HowToPlayView(RandomizerView):
    template_name = "randomizer/how_to_play.html"


class OptionsView(RandomizerView):
    template_name = "randomizer/options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = CATEGORIES_FOR_TEMPLATE
        return context


class ResourcesView(RandomizerView):
    template_name = "randomizer/resources.html"


class ChecksView(RandomizerView):
    template_name = "randomizer/checks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checks"] = CHECK_ROWS
        return context


class ContributeView(RandomizerView):
    template_name = "randomizer/contribute.html"


class CommunityView(RandomizerView):
    template_name = "randomizer/community.html"


class RemakeView(RandomizerView):
    template_name = "randomizer/_remake_rando.html"


class GuideView(RandomizerView):
    template_name = "randomizer/guide.html"


class UpdatesView(RandomizerView):
    template_name = "randomizer/updates.html"


class RandomizeView(RandomizerView):
    template_name = "randomizer/randomize.html"


class HashView(RandomizerView):
    template_name = "randomizer/patch_from_hash.html"


class GenerateView(MixinClass, FormView):
    form_class = GenerateForm

    def form_valid(self, form):
        data = form.cleaned_data

        if not settings.DEBUG:
            data["debug_mode"] = False

        seed = data["seed"]

        if seed:
            if seed.isdigit():
                seed = int(seed)
                if seed < 1 or seed > 0xFFFFFFFF:
                    seed = None
            else:
                seed = binascii.crc32(seed.encode())

        if not seed:
            r = random.SystemRandom()
            seed = r.getrandbits(32)
            del r

        debug_mode = bool(data["debug_mode"])
        race_mode = bool(data["race_mode"])
        debug_bps_patches = bool(data.get("debug_bps_patches", False)) and settings.DEBUG
        prize_offset = data.get("prize_offset") if settings.DEBUG else None
        mimic_offset = data.get("mimic_offset") if settings.DEBUG else None
        offset_slots = bool(data.get("offset_slots"))
        offset_mimics = bool(data.get("offset_mimics"))
        offset_coins = bool(data.get("offset_coins"))
        offset_star_pieces = bool(data.get("offset_star_pieces"))
        offset_invisible_flags = bool(data.get("offset_invisible_flags"))

        try:
            s = Settings()
            full_flag_string = (data["flags"] or "") + "     " + (data["cosmetics"] or "")
            s.set_from_flag_string(full_flag_string.strip())
            s.debug_mode = debug_mode
            s.prize_offset = prize_offset
            s.mimic_offset = mimic_offset
            s.offset_slots = offset_slots
            s.offset_mimics = offset_mimics
            s.offset_coins = offset_coins
            s.offset_star_pieces = offset_star_pieces
            s.offset_invisible_flags = offset_invisible_flags
            validate_settings(s)

            debug_flags = {}
            if debug_mode:
                debug_flags = {
                    'debug_bps_patches': debug_bps_patches,
                    'prize_offset': prize_offset,
                    'mimic_offset': mimic_offset,
                    'offset_slots': offset_slots,
                    'offset_mimics': offset_mimics,
                    'offset_coins': offset_coins,
                    'offset_star_pieces': offset_star_pieces,
                    'offset_invisible_flags': offset_invisible_flags,
                }

            task_result = generate_seed_task.enqueue(seed, full_flag_string, debug_flags)
        except (FlagError, SettingsValidationError) as e:
            result = {
                "error": e.args[0],
            }
            return JsonResponse(result, encoder=PatchJSONEncoder)
        except Exception:
            logger.error(
                "ERROR form data: {!r}, generated seed: {!r}".format(data, seed)
            )
            raise

        result = {
            "logic": VERSION,
            "seed": seed,
            "mode": "open",
            "debug_mode": debug_mode,
            "flag_string": s.flag_string,
            "race_mode": race_mode,
            "seed_id": str(task_result.id),
        }

        return JsonResponse(result, encoder=PatchJSONEncoder)

    def form_invalid(self, form):
        msg = "{} form error: ".format(self.__class__.__name__) + "; ".join(form.errors)
        logger.error(msg)
        return HttpResponseBadRequest(msg.encode())

    def get(self, request, *args, **kwargs):
        """Handle GET requests: return 400 error."""
        msg = "{} GET method not allowed".format(self.__class__.__name__)
        logger.error(msg)
        return HttpResponseBadRequest(msg.encode())


class GenerateStatusView(MixinClass, View):
    @staticmethod
    def get(request, seed_id):
        result = {}

        # Check task status.
        task_result = generate_seed_task.get_result(seed_id)

        # Finished, get patch.
        if task_result.status == TaskResultStatus.SUCCESSFUL:
            patch = Patch.objects.select_related('seed').get(pk=task_result.return_value)
            result['complete'] = True
            result['data'] = {
                "logic": VERSION,
                "seed": patch.seed.seed,
                "hash": patch.seed.hash,
                "mode": "race" if patch.seed.race_mode else "open",
                "debug_mode": patch.seed.debug_mode,
                "flag_string": patch.seed.flags,
                "file_select_character": patch.seed.file_select_char,
                "file_select_hash": patch.seed.file_select_hash,
                "permalink": reverse("randomizer:patch-from-hash", kwargs={"hash": patch.seed.hash}),
                "race_mode": patch.seed.race_mode,
                "spoiler": patch.seed.spoiler if not patch.seed.race_mode else {},
                "patch": pickle.loads(patch.patch),
            }

        # Failed
        elif task_result.status == TaskResultStatus.FAILED:
            result['error'] = 'Seed generation failed'

        # In progress, check cache for status update.
        # If it's waiting for processing, it might not be in there yet.
        else:
            key = f'task-status-{task_result.id}'
            data = cache.get(key)
            if isinstance(data, dict):
                result['stage'] = data.get('message', '')
                result['percent'] = data.get('percent', 0)
            else:
                result['stage'] = 'Starting generation...'
                result['percent'] = 0

        return JsonResponse(result)


class GenerateFromHashView(MixinClass, View):
    @staticmethod
    def get(request, hash):
        """Get a previously generated patch via hash value."""

        try:
            s = Seed.objects.get(hash=hash)
        except Seed.DoesNotExist:
            return HttpResponseNotFound("No record for hash {0!r}".format(hash))

        result = {
            "logic": s.version,
            "seed": s.seed,
            "hash": s.id,
            "mode": "race" if s.race_mode else "open",
            "debug_mode": s.debug_mode,
            "flag_string": s.flags,
            "file_select_character": s.file_select_char,
            "file_select_hash": s.file_select_hash,
            "patch": [],
            "race_mode": s.race_mode,
            "spoiler": s.spoiler if not s.race_mode else {},
        }
        return JsonResponse(result)


@method_decorator(csrf_exempt, name="dispatch")
class PackingView(MixinClass, View):
    @staticmethod
    def post(request):
        """Pack uploaded ROM into the provided WAD file as downloaded file."""
        if not request.FILES.get("rom"):
            return HttpResponseBadRequest("ROM file not provided")
        elif not request.FILES.get("wad"):
            return HttpResponseBadRequest("WAD file not provided")

        with tempfile.TemporaryDirectory() as dumpdir:
            romfile = os.path.join(dumpdir, "rom.sfc")
            with open(romfile, "wb") as f:
                shutil.copyfileobj(request.FILES["rom"], f)

            rom_to_copy = romfile
            if request.POST.get("region") in ("US", "EU"):
                romcompressed = os.path.join(dumpdir, "rom_compressed.sfc")
                nlzss.encode_file(romfile, romcompressed)
                rom_to_copy = romcompressed

            wadf = Wii.WAD.load(request.FILES["wad"].read()) # type: ignore
            wadf.dumpDir(dumpdir)

            u8file = os.path.join(dumpdir, "00000005.app")
            u8unpackdir = u8file + "_unpacked"
            u8archive = Wii.U8.loadFile(u8file) # type: ignore
            u8archive.dumpDir(u8unpackdir)

            for f in os.listdir(u8unpackdir):
                if f.lower().endswith(".rom"):
                    wadrom = os.path.join(u8unpackdir, f)
                    shutil.copyfile(rom_to_copy, wadrom)
                    break

            newu8 = Wii.U8.loadDir(u8unpackdir) # type: ignore
            newu8.dumpFile(u8file)

            newwadfile = os.path.join(dumpdir, "smrpg_randomized.wad")
            newwad = Wii.WAD.loadDir(dumpdir) # type: ignore

            with open(romfile, "rb") as f:
                f.seek(0x7FC0)
                title = f.read(20).strip()
                title = title.ljust(20)

            if not title.startswith(b"SMRPG-R"):
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            try:
                seed = int(title[7:].strip())
            except ValueError:
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            if newwad.contents[0][0x80:0x84] != b"IMET":
                return HttpResponseBadRequest("Can't find IMET in WAD contents file")

            imetpos = 0x80
            content = bytearray(newwad.contents[0])

            jpos = imetpos + 29
            for i in list(range(7)):
                for j, char in enumerate(title):
                    pos = jpos + (i * 84) + (j * 2)
                    content[pos] = char

            data = content[64:1584]
            data += b"\x00" * 16
            md5 = Wii.Crypto.createMD5Hash(data) # type: ignore
            for i in range(16):
                content[1584 + i] = md5[i]

            newwad.contents[0] = bytes(content)

            choices = list(string.ascii_letters + string.digits)
            first_char_choices = list(
                set(choices)
                - {
                    "C",
                    "D",
                    "E",
                    "F",
                    "G",
                    "H",
                    "J",
                    "L",
                    "M",
                    "N",
                    "P",
                    "Q",
                    "R",
                    "S",
                    "W",
                    "X",
                }
            )
            first_char_choices.sort()

            random.seed(seed)
            new_id = bytearray(
                [0x00, 0x01, 0x00, 0x01, ord(random.choice(first_char_choices))]
            )
            for i in range(3):
                new_id.append(ord(random.choice(choices)))

            tid = int.from_bytes(new_id, "big")
            newwad.tmd.setTitleID(tid)
            newwad.tik.setTitleID(tid)

            newwad.dumpFile(newwadfile, fakesign=False)

            response = HttpResponse(
                open(newwadfile, "rb"), content_type="application/octet-stream"
            )
            response["Content-Disposition"] = 'attachment; filename="smrpg.wad"'
            return response




@method_decorator(csrf_exempt, name="dispatch")
class APIGenerateView(GenerateView):
    """Use same fields and response as the generate view, but don't include the patch data."""

    def get_form_kwargs(self):
        """Parse JSON body in post request and fake form fields to reuse the form view."""
        kwargs = super().get_form_kwargs()
        if self.request.method in ("POST", "PUT"):
            kwargs["data"] = QueryDict(mutable=True)
            try:
                data = json.loads(self.request.body)
                for key, value in data.items():
                    kwargs["data"][key] = value
            except json.JSONDecodeError:
                logger.error(
                    "APIGenerateView got bad request body: {!r}".format(
                        self.request.body
                    )
                )
        return kwargs


class APIFlags(MixinClass, View):
    @staticmethod
    def get(request):
        data = {
            "flags": FLAGS,
        }
        return JsonResponse(data)
