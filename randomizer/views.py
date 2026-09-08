from randomizer.logic.check_list import CHECK_ROWS
from randomizer.logic.offset_preview import get_ordered_lists
import base64
import binascii
import hashlib
import json
import logging
import os
import queue
import random
import string
import tempfile
import shutil
import threading
from collections.abc import Iterator

import Wii
import nlzss

from django.conf import settings
from django.db import transaction
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponse,
    HttpResponseNotFound,
    QueryDict,
    StreamingHttpResponse,
)
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from randomizer.types.flags import FlagError
from randomizer.logic.validation import SettingsValidationError
from randomizer.types.flag_categories import CATEGORIES, PRESETS
from randomizer.types.patch import PatchJSONEncoder

from .models import Seed, Patch
from .forms import GenerateForm
from .main import create, VERSION
from .logic.generate import build_world_for, ensure_sprite_render_variants, save_seed
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
    return_patch_data = True

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

            world = build_world_for(
                seed, s, debug_mode=debug_mode, debug_bps_patches=debug_bps_patches
            )
            patches = {"US": world.get_patch()}
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
            "hash": world.hash,
            "mode": "open",
            "debug_mode": debug_mode,
            "flag_string": world.settings.flag_string,
            "file_select_character": world.file_select_character,
            "file_select_hash": world.file_select_hash,
            "permalink": reverse(
                "randomizer:patch-from-hash", kwargs={"hash": world.hash}
            ),
            "race_mode": race_mode,
            "spoiler": world.spoiler if not race_mode else {},
            "forced_overrides": world.settings.forced_overrides,
        }

        with transaction.atomic():
            s = save_seed(world, seed, debug_mode=debug_mode, race_mode=race_mode)

            for region in patches:
                patch_dump = json.dumps({}, cls=PatchJSONEncoder)
                h = hashlib.sha1()
                h.update(patch_dump.encode())
                Patch.objects.update_or_create(
                    seed=s,
                    region=region,
                    defaults={"sha1": h.hexdigest(), "patch": patch_dump},
                )

        ensure_sprite_render_variants(s, seed, world, debug_mode=debug_mode)

        if self.return_patch_data:
            result["patch"] = patches["US"]

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


class GenerateStreamView(MixinClass, View):
    """Generate a seed with real-time progress updates via Server-Sent Events (SSE)."""

    def post(self, request):
        form = GenerateForm(request.POST)
        if not form.is_valid():
            error_msg = "; ".join(
                f"{k}: {', '.join(str(e) for e in v)}"
                for k, v in form.errors.items()
            ) if form.errors else "Validation failed"
            return JsonResponse({"error": error_msg}, status=400)

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

        def generate_events() -> Iterator[bytes]:
            progress_queue: queue.Queue = queue.Queue()
            result_holder: dict = {}

            def on_progress(message: str, percent: int):
                progress_queue.put({"stage": message, "percent": percent})

            def run_generation():
                full_flag_string = (data["flags"] or "") + "     " + (data["cosmetics"] or "")
                try:
                    s = Settings()
                    s.set_from_flag_string(full_flag_string.strip())
                    s.debug_mode = debug_mode
                    s.prize_offset = prize_offset
                    s.mimic_offset = mimic_offset
                    s.offset_slots = offset_slots
                    s.offset_mimics = offset_mimics
                    s.offset_coins = offset_coins
                    s.offset_star_pieces = offset_star_pieces
                    s.offset_invisible_flags = offset_invisible_flags

                    world = build_world_for(
                        seed, s, debug_mode=debug_mode,
                        debug_bps_patches=debug_bps_patches,
                        progress_callback=on_progress,
                    )

                    patch = world.get_patch()

                    result_holder["success"] = True
                    result_holder["data"] = {
                        "logic": VERSION,
                        "seed": seed,
                        "hash": world.hash,
                        "mode": "open",
                        "debug_mode": debug_mode,
                        "flag_string": world.settings.flag_string,
                        "file_select_character": world.file_select_character,
                        "file_select_hash": world.file_select_hash,
                        "permalink": reverse(
                            "randomizer:patch-from-hash", kwargs={"hash": world.hash}
                        ),
                        "race_mode": race_mode,
                        "spoiler": world.spoiler if not race_mode else {},
                        "patch": patch,
                    }

                    with transaction.atomic():
                        seed_obj = save_seed(
                            world, seed, debug_mode=debug_mode, race_mode=race_mode
                        )

                        patch_dump = json.dumps({}, cls=PatchJSONEncoder)
                        h = hashlib.sha1()
                        h.update(patch_dump.encode())
                        Patch.objects.update_or_create(
                            seed=seed_obj,
                            region="US",
                            defaults={"sha1": h.hexdigest(), "patch": patch_dump},
                        )

                    ensure_sprite_render_variants(
                        seed_obj, seed, world, debug_mode=debug_mode
                    )

                except (FlagError, SettingsValidationError) as e:
                    logger.error("Settings error during generation: %s", e.args[0])
                    result_holder["error"] = e.args[0]
                except Exception as e:
                    logger.exception(
                        "Error during generation - seed: %r, flags: %r",
                        seed,
                        full_flag_string.strip(),
                    )
                    result_holder["error"] = str(e)
                finally:
                    progress_queue.put({"done": True})

            thread = threading.Thread(target=run_generation)
            thread.start()

            while True:
                try:
                    event = progress_queue.get(timeout=30)
                    if event.get("done"):
                        break
                    yield f"data: {json.dumps(event)}\n\n".encode()
                except queue.Empty:
                    yield b": keepalive\n\n"

            if result_holder.get("error"):
                yield f"data: {json.dumps({'error': result_holder['error']})}\n\n".encode()
            else:
                result_data = result_holder.get("data", {})
                yield f"data: {json.dumps({'complete': True, 'data': result_data}, cls=PatchJSONEncoder)}\n\n".encode()

        response = StreamingHttpResponse(
            generate_events(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

    def get(self, request, *args, **kwargs):
        """Handle GET requests: return 400 error."""
        msg = "GenerateStreamView GET method not allowed"
        logger.error(msg)
        return HttpResponseBadRequest(msg.encode())


class GenerateFromHashView(MixinClass, View):
    @staticmethod
    def get(request, hash, region):
        """Get a previously generated patch via hash value."""
        if region == "EU":
            region = "US"

        try:
            s = Seed.objects.get(hash=hash)
        except Seed.DoesNotExist:
            return HttpResponseNotFound("No record for hash {0!r}".format(hash))

        try:
            p = Patch.objects.get(seed=s, region=region)
        except Patch.DoesNotExist:
            return HttpResponseNotFound(
                "No patch found for hash {0!r}, region {1!r}".format(hash, region)
            )

        result = {
            "logic": s.version,
            "seed": s.seed,
            "hash": s.hash,
            "mode": s.mode,
            "debug_mode": s.debug_mode,
            "flag_string": s.flags,
            "file_select_character": s.file_select_char,
            "file_select_hash": s.file_select_hash,
            "patch": json.loads(p.patch),
            "race_mode": s.race_mode,
            "spoiler": s.spoiler,
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

    return_patch_data = False

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
