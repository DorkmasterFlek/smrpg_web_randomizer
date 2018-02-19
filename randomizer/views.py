import base64
import binascii
import hashlib
import json
import os
import random
import tempfile
import shutil

import Wii
import nlzss

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView

from .models import Seed, Patch
from .forms import GenerateForm
from .logic_old import randomizer


class AboutView(TemplateView):
    template_name = 'randomizer/about.html'


class OptionsView(TemplateView):
    template_name = 'randomizer/options.html'


class UpdatesView(TemplateView):
    template_name = 'randomizer/updates.html'


class RandomizeView(TemplateView):
    template_name = 'randomizer/randomize.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = randomizer.VERSION
        return context


class HashView(TemplateView):
    template_name = 'randomizer/patch_from_hash.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['version'] = randomizer.VERSION
        return context


class GenerateView(FormView):
    form_class = GenerateForm

    def form_valid(self, form):
        data = form.cleaned_data

        # If seed is provided, use it.  Otherwise generate a random seed (10 digits max).
        seed = data['seed']
        if seed:
            if seed.isdigit():
                seed = int(seed)
                if seed < 1:
                    seed = None
            else:
                seed = binascii.crc32(seed.encode())

        if not seed:
            random.seed()
            seed = random.getrandbits(32)

        mode = data['mode']

        # Compute hash based on seed and selected options.  Use first 10 characters for convenience.
        h = hashlib.md5()
        h.update(randomizer.VERSION.to_bytes(1, 'big'))  # This only works up to version 255, then it needs 2 bytes.
        h.update(seed.to_bytes(4, 'big'))
        h.update(mode.encode('utf-8'))
        if mode == 'custom':
            h.update(str(data['randomize_character_stats']).encode('utf-8'))
            h.update(str(data['randomize_drops']).encode('utf-8'))
            h.update(str(data['randomize_enemy_formations']).encode('utf-8'))
            h.update(str(data['randomize_monsters']).encode('utf-8'))
            h.update(str(data['randomize_shops']).encode('utf-8'))
            h.update(str(data['randomize_equipment']).encode('utf-8'))
            h.update(str(data['randomize_spell_stats']).encode('utf-8'))
            h.update(str(data['randomize_spell_lists']).encode('utf-8'))

        hash = base64.b64encode(h.digest()).decode().replace('+', '').replace('/', '')[:10]

        # Randomize!
        custom_flags = {}
        for key in (
                'randomize_character_stats',
                'randomize_drops',
                'randomize_enemy_formations',
                'randomize_monsters',
                'randomize_shops',
                'randomize_equipment',
                'randomize_spell_stats',
                'randomize_spell_lists',
        ):
            custom_flags[key] = data[key]

        # FIXME: Old version of the randomizer!
        patches = randomizer.randomize_for_web(seed, mode, data['randomize_character_stats'], data['randomize_drops'],
                                               data['randomize_enemy_formations'], data['randomize_monsters'],
                                               data['randomize_shops'], data['randomize_equipment'],
                                               data['randomize_spell_stats'], data['randomize_spell_lists'])

        # Send back patch data.
        result = {
            'logic': randomizer.VERSION,
            'seed': seed,
            'hash': hash,
            'mode': mode,
            'custom_flags': custom_flags,
        }

        # Save patch to the database (don't need to save EU since it's the same as US).
        with transaction.atomic():
            # If there's an existing seed with the same hash, replace it.
            try:
                s = Seed.objects.get(hash=hash)
            except Seed.DoesNotExist:
                pass
            else:
                s.delete()

            s = Seed(hash=hash, seed=seed, version=randomizer.VERSION, mode=mode, flags=json.dumps(custom_flags))
            s.save()

            for region, patch in patches.items():
                patch_dump = json.dumps(patch)
                h = hashlib.sha1()
                h.update(patch_dump.encode())
                p = Patch(seed=s, region=region, sha1=h.hexdigest(), patch=patch_dump)
                p.save()

        if data['region'] == 'EU':
            result['patch'] = patches['US']  # Patch for EU version is the same as US.
        else:
            result['patch'] = patches[data['region']]
        return JsonResponse(result)

    def form_invalid(self, form):
        msg = "ERRORS: " + '; '.join(form.errors)
        return HttpResponseBadRequest(msg.encode())


class GenerateFromHashView(View):
    def get(self, request, hash, region):
        """Get a previously generated patch via hash value."""
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
            'hash': s.hash,
            'mode': s.mode,
            'custom_flags': json.loads(s.flags),
            'patch': json.loads(p.patch),
        }
        return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
class PackingView(View):
    def post(self, request):
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
            newwad.dumpFile(newwadfile, fakesign=False)

            # Return new WAD file
            response = HttpResponse(open(newwadfile, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="smrpg.wad"'
            return response
