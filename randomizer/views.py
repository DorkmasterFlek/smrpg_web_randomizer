import binascii
import hashlib
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
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, QueryDict
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView

from .models import Seed, Patch
from .forms import GenerateForm
from .logic.flags import CATEGORIES, PRESETS
from .logic.main import GameWorld, Settings, VERSION
from .logic.patch import PatchJSONEncoder

# Get an instance of a logger
logger = logging.getLogger(__name__)


def _build_flag_json_data(flag, parent_modes=None):
    """

    Args:
        flag (randomizer.logic.flags.Flag): Flag class to build JSON data for.
        parent_modes (list[str]): Modes of the parent flag to restrict the child to.

    Returns:
        dict: Flag data.

    """
    modes = flag.modes.copy()
    if parent_modes is not None:
        modes = list(set(modes) & set(parent_modes))

    d = {
        'value': flag.value,
        'modes': modes,
        'choices': [],
        'options': [],
    }
    for choice in flag.choices:
        d['choices'].append(_build_flag_json_data(choice, parent_modes=modes))
    for option in flag.options:
        d['options'].append(_build_flag_json_data(option, parent_modes=modes))

    return d


# Build JSON representation of flag hierarchy.
FLAGS = []
for category in CATEGORIES:
    for flag in category.flags:
        FLAGS.append(_build_flag_json_data(flag))


class RandomizerView(TemplateView):
    """
    Base class for views that generate a ROM, i.e. randomizer and patch-from-hash views.
    This gets common context data.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = VERSION
        context['debug_enabled'] = settings.DEBUG
        context['beta_site'] = settings.BETA
        context['categories'] = CATEGORIES
        context['presets'] = PRESETS
        context['flags'] = FLAGS

        return context


class AboutView(RandomizerView):
    template_name = 'randomizer/about.html'


class HowToPlayView(RandomizerView):
    template_name = 'randomizer/how_to_play.html'


class OptionsView(RandomizerView):
    template_name = 'randomizer/options.html'


class ResourcesView(RandomizerView):
    template_name = 'randomizer/resources.html'


class GuideView(RandomizerView):
    template_name = 'randomizer/guide.html'


class UpdatesView(RandomizerView):
    template_name = 'randomizer/updates.html'


class RandomizeView(RandomizerView):
    template_name = 'randomizer/randomize.html'


class HashView(RandomizerView):
    template_name = 'randomizer/patch_from_hash.html'


class GenerateView(FormView):
    form_class = GenerateForm
    return_patch_data = True

    def form_valid(self, form):
        data = form.cleaned_data

        # Debug mode is only allowed if the server is running in debug mode for development.
        if not settings.DEBUG:
            data['debug_mode'] = False

        # If seed is provided, use it.  Otherwise generate a random seed (10 digits max).
        # For non-numeric values, take the CRC32 checksum of it.
        seed = data['seed']
        if seed:
            if seed.isdigit():
                seed = int(seed)
                if seed < 1 or seed > 0xFFFFFFFF:
                    seed = None
            else:
                seed = binascii.crc32(seed.encode())

        # If seed is not provided, generate a 32 bit seed integer using the CSPRNG.
        if not seed:
            r = random.SystemRandom()
            seed = r.getrandbits(32)
            del r

        mode = data['mode'] or 'open'
        debug_mode = bool(data['debug_mode'])
        race_mode = bool(data['race_mode'])

        # Build game world, randomize it, and generate the patch.
        world = GameWorld(seed, Settings(mode, debug_mode, data['flags'] or ''))

        try:
            world.randomize()
            patches = {'US': world.build_patch()}
        except Exception:
            logger.error("ERROR form data: {!r}, generated seed: {!r}".format(data, seed))
            raise

        # Send back patch data.
        result = {
            'logic': VERSION,
            'seed': seed,
            'hash': world.hash,
            'mode': mode,
            'debug_mode': debug_mode,
            'flag_string': world.settings.flag_string,
            'file_select_character': world.file_select_character,
            'file_select_hash': world.file_select_hash,
            'permalink': reverse('randomizer:patch-from-hash', kwargs={'hash': world.hash}),
            'race_mode': race_mode,
            'spoiler': world.spoiler if not race_mode else {},
        }

        # Save patch to the database (don't need to save EU since it's the same as US).
        with transaction.atomic():
            # If there's an existing seed with the same hash, replace it.
            try:
                s = Seed.objects.get(hash=world.hash)
            except Seed.DoesNotExist:
                pass
            else:
                s.delete()

            s = Seed(hash=world.hash, seed=seed, version=VERSION, mode=mode, debug_mode=debug_mode,
                     flags=world.settings.flag_string, file_select_char=world.file_select_character,
                     file_select_hash=world.file_select_hash, race_mode=race_mode, spoiler=world.spoiler)
            s.save()

            for region, patch in patches.items():
                patch_dump = json.dumps(patch, cls=PatchJSONEncoder)
                h = hashlib.sha1()
                h.update(patch_dump.encode())
                p = Patch(seed=s, region=region, sha1=h.hexdigest(), patch=patch_dump)
                p.save()

        # Check if we're including the patch data in the response.
        if self.return_patch_data:
            result['patch'] = patches['US']  # Patch for EU version is the same as US.

        return JsonResponse(result, encoder=PatchJSONEncoder)

    def form_invalid(self, form):
        msg = "{} form error: ".format(self.__class__.__name__) + '; '.join(form.errors)
        logger.error(msg)
        return HttpResponseBadRequest(msg.encode())

    def get(self, request, *args, **kwargs):
        """Handle GET requests: return 400 error."""
        msg = "{} GET method not allowed".format(self.__class__.__name__)
        logger.error(msg)
        return HttpResponseBadRequest(msg.encode())


class GenerateFromHashView(View):
    @staticmethod
    def get(request, hash, region):
        """Get a previously generated patch via hash value."""
        # EU patch is actually the US one.
        if region == 'EU':
            region = 'US'

        try:
            s = Seed.objects.get(hash=hash)
        except Seed.DoesNotExist:
            return HttpResponseNotFound("No record for hash {0!r}".format(hash))

        try:
            p = Patch.objects.get(seed=s, region=region)
        except Patch.DoesNotExist:
            return HttpResponseNotFound("No patch found for hash {0!r}, region {1!r}".format(hash, region))

        result = {
            'logic': s.version,
            'seed': s.seed,
            'hash': s.hash,
            'mode': s.mode,
            'debug_mode': s.debug_mode,
            'flag_string': s.flags,
            'file_select_character': s.file_select_char,
            'file_select_hash': s.file_select_hash,
            'patch': json.loads(p.patch),
            'race_mode': s.race_mode,
            'spoiler': s.spoiler,
        }
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class PackingView(View):
    @staticmethod
    def post(request):
        """Pack uploaded ROM into the provided WAD file as downloaded file."""
        if not request.FILES.get('rom'):
            return HttpResponseBadRequest("ROM file not provided")
        elif not request.FILES.get('wad'):
            return HttpResponseBadRequest("WAD file not provided")

        with tempfile.TemporaryDirectory() as dumpdir:
            romfile = os.path.join(dumpdir, 'rom.sfc')
            with open(romfile, 'wb') as f:
                shutil.copyfileobj(request.FILES['rom'], f)

            # Compress ROM file for US and EU (not JP)
            rom_to_copy = romfile
            if request.POST.get('region') in ('US', 'EU'):
                romcompressed = os.path.join(dumpdir, 'rom_compressed.sfc')
                nlzss.encode_file(romfile, romcompressed)
                rom_to_copy = romcompressed

            # Dump WAD file
            wadf = Wii.WAD.load(request.FILES['wad'].read())
            wadf.dumpDir(dumpdir)

            # Dump U8 archive
            u8file = os.path.join(dumpdir, '00000005.app')
            u8unpackdir = u8file + '_unpacked'
            u8archive = Wii.U8.loadFile(u8file)
            u8archive.dumpDir(u8unpackdir)

            # Copy randomized ROM over
            for f in os.listdir(u8unpackdir):
                if f.lower().endswith(".rom"):
                    wadrom = os.path.join(u8unpackdir, f)
                    shutil.copyfile(rom_to_copy, wadrom)
                    break

            # Put U8 archive back together
            newu8 = Wii.U8.loadDir(u8unpackdir)
            newu8.dumpFile(u8file)

            # Build new WAD
            newwadfile = os.path.join(dumpdir, 'smrpg_randomized.wad')
            newwad = Wii.WAD.loadDir(dumpdir)

            # Make new channel title with seed (sync for all languages).
            # Read title from ROM and make sure it's in the correct spot.  If not, leave the title alone.
            with open(romfile, 'rb') as f:
                f.seek(0x7fc0)
                title = f.read(20).strip()
                title = title.ljust(20)

            if not title.startswith(b'SMRPG-R'):
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            try:
                seed = int(title[7:].strip())
            except ValueError:
                return HttpResponseBadRequest("Bad ROM title {!r}".format(title))

            # Read first content file data to find the channel title data and update it.
            if newwad.contents[0][0x80:0x84] != b'IMET':
                return HttpResponseBadRequest("Can't find IMET in WAD contents file")

            imetpos = 0x80
            content = bytearray(newwad.contents[0])

            # Channel names start 29 bytes after the "IMET" string, and there are 7 of them in a row.
            jpos = imetpos + 29
            for i in list(range(7)):
                for j, char in enumerate(title):
                    pos = jpos + (i * 84) + (j * 2)
                    content[pos] = char

            # Update MD5 hash for this content file.
            data = content[64:1584]
            data += b'\x00' * 16
            md5 = Wii.Crypto.createMD5Hash(data)
            for i in range(16):
                content[1584 + i] = md5[i]

            newwad.contents[0] = bytes(content)

            # Generate random title ID for the WAD that doesn't conflict with existing channels.
            choices = list(string.ascii_letters + string.digits)
            # The first character of the four byte title ID should exclude existing ones to avoid conflicts.
            first_char_choices = list(set(choices) -
                                      {'C', 'D', 'E', 'F', 'G', 'H', 'J', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'W', 'X'})
            first_char_choices.sort()

            random.seed(seed)
            new_id = bytearray([0x00, 0x01, 0x00, 0x01, ord(random.choice(first_char_choices))])
            for i in range(3):
                new_id.append(ord(random.choice(choices)))

            tid = int.from_bytes(new_id, 'big')
            newwad.tmd.setTitleID(tid)
            newwad.tik.setTitleID(tid)

            newwad.dumpFile(newwadfile, fakesign=False)

            # Return new WAD file
            response = HttpResponse(open(newwadfile, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="smrpg.wad"'
            return response


# ************** API views

@method_decorator(csrf_exempt, name='dispatch')
class APIGenerateView(GenerateView):
    """Use same fields and response as the generate view, but don't include the patch data."""
    return_patch_data = False

    def get_form_kwargs(self):
        """Parse JSON body in post request and fake form fields to reuse the form view."""
        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = QueryDict(mutable=True)
            try:
                data = json.loads(self.request.body)
                for key, value in data.items():
                    kwargs['data'][key] = value
            except json.JSONDecodeError:
                logger.error("APIGenerateView got bad request body: {!r}".format(self.request.body))
        return kwargs


class APIFlags(View):
    @staticmethod
    def get(request):
        data = {
            'flags': FLAGS,
        }
        return JsonResponse(data)
