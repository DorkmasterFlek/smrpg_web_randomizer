import json
import random

from django.core.management.base import BaseCommand
from .generatesample import ALL_FLAGS

from randomizer.logic.main import GameWorld, Settings


class Command(BaseCommand):
    help = 'Generate a statistical sampling of seeds to compare randomization spreads.'

    def add_arguments(self, parser):
        """Add optional arguments.

        Args:
            parser (argparse.ArgumentParser): Parser

        """

        parser.add_argument('-r', '--rom', dest='rom', required=True,
                            help='Path to a Mario RPG rom')

        parser.add_argument('-s', '--seed', dest='seed', type=int, default=0,
                            help='Seed')

        parser.add_argument('-o', '--output', dest='output_file', default='sample',
                            help='Output file name prefix')

        parser.add_argument('-m', '--mode', dest='mode', default='open', choices=['linear', 'open'],
                            help='Mode to use for rom.  Default: %(default)s')

        parser.add_argument('-f', '--flags', dest='flags', default=ALL_FLAGS,
                            help='Flags string (from website). If not provided, all flags will be used.')

    def handle(self, *args, **options):
        settings = Settings(options['mode'], flag_string=options['flags'])
        seed = options['seed']

        # If seed is not provided, generate a 32 bit seed integer using the CSPRNG.
        if not seed:
            r = random.SystemRandom()
            seed = r.getrandbits(32)
            del r

        self.stdout.write("Generating seed: {}".format(seed))
        world = GameWorld(seed, settings)

        world.randomize()

        patch = world.build_patch()

        rom = bytearray(open(options['rom'], 'rb').read())
        base_patch = json.load(open('randomizer/static/randomizer/patches/open_mode.json'))
        for ele in base_patch:
            key = list(ele)[0]
            bytes = ele[key]
            addr = int(key)
            for byte in bytes:
                rom[addr] = byte
                addr += 1

        for addr in patch.addresses:
            bytes = patch.get_data(addr)
            for byte in bytes:
                rom[addr] = byte
                addr += 1

        checksum = sum(rom) & 0xFFFF
        rom[0x7FDC] = (checksum ^ 0xFFFF) & 0xFF
        rom[0x7FDD] = (checksum ^ 0xFFFF) >> 8
        rom[0x7FDE] = checksum & 0xFF
        rom[0x7FDF] = checksum >> 8

        open(options['output_file'], 'wb').write(rom)
        self.stdout.write("Wrote output file: {}".format(options['output_file']))
        spoiler_fname = options['output_file'] + '.spoiler'
        json.dump(world.spoiler, open(spoiler_fname, 'w'))
        self.stdout.write("Wrote spoiler file: {}".format(spoiler_fname))
