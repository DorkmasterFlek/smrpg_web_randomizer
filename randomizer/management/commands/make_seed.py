import json

from django.core.management.base import BaseCommand
from .generatesample import ALL_FLAGS

from randomizer.logic.main import GameWorld, Settings, VERSION

help = 'Generate a statistical sampling of seeds to compare randomization spreads.'
class Command(BaseCommand):
    def add_arguments(self, parser):
        """Add optional arguments.

        Args:
            parser (argparse.ArgumentParser): Parser

        """

        parser.add_argument('-r', '--rom', dest='rom',
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
        json.dump(world.spoiler, open(options['output_file'] + '.spoiler', 'w'))
