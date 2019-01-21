import collections
import csv
import datetime
import random
import time

from django.core.management.base import BaseCommand

from randomizer.data.keys import get_default_key_item_locations
from randomizer.logic.main import GameWorld, Settings, VERSION, FLAGS

# Flag string for all flags at max level.
ALL_FLAGS = ''
for flag in FLAGS:
    ALL_FLAGS += flag.letter
    if flag.levels > 1:
        ALL_FLAGS += str(flag.levels)


class Command(BaseCommand):
    help = 'Generate a statistical sampling of seeds to compare randomization spreads.'

    def add_arguments(self, parser):
        """Add optional arguments.

        Args:
            parser (argparse.ArgumentParser): Parser

        """
        parser.add_argument('-s', '--samples', dest='samples', default=10000, type=int,
                            help='Number of samples to generate.  Default: %(default)s')

        parser.add_argument('-o', '--output', dest='output_file', default='sample',
                            help='Output file name prefix.  Default: %(default)s')

        parser.add_argument('-m', '--mode', dest='mode', default='open', choices=['standard', 'open'],
                            help='Mode to use for samples.  Default: %(default)s')

        parser.add_argument('-f', '--flags', dest='flags', default='',
                            help='Flags string (from website).  If not provided, all flags will be used.')

    def handle(self, *args, **options):
        sysrand = random.SystemRandom()
        start = time.time()

        flags = options['flags']
        if not options['flags']:
            flags = ALL_FLAGS

        self.stdout.write("Generating {} samples of version {}, {} mode, flags {!r}".format(
            options['samples'], VERSION, options['mode'], flags))

        # Parse custom flags from flag string argument.
        flags_dict = {}
        current_flag = None
        current_char = None
        for char in flags:
            if not char.isdigit() and char != current_char:
                current_char = char
                l = [f for f in FLAGS if f.letter == current_char]
                if l:
                    current_flag = l[0]

            if char.isdigit():
                flags_dict[current_flag.field] = int(char)
            else:
                flags_dict[current_flag.field] = 1

        stars_file = '{}_stars.csv'.format(options['output_file'])
        self.stdout.write("Star Locations: {}".format(stars_file))
        star_stats = {}

        key_items_file = '{}_key_items.csv'.format(options['output_file'])
        self.stdout.write("Key Item Locations: {}".format(key_items_file))
        key_item_stats = {}

        for i in range(options['samples']):
            # Generate random full standard seed.
            seed = sysrand.getrandbits(32)
            world = GameWorld(seed, Settings(options['mode'], custom_flags=flags_dict))
            try:
                world.randomize()
            except Exception:
                elapsed = int(round(time.time() - start))
                self.stdout.write("Generated {} samples, elapsed time {}".format(
                    i, datetime.timedelta(seconds=elapsed)))
                self.stdout.write("ERROR generating seed {}".format(world.seed))
                raise

            # Record star piece shuffle stats.
            for location in world.boss_locations:
                star_stats.setdefault(location.name, 0)
                if location.has_star:
                    star_stats[location.name] += 1

            # Record key item stats.
            for location in world.key_locations:
                key_item_stats.setdefault(location.item.__name__, collections.defaultdict(int))
                key_item_stats[location.item.__name__][location.name] += 1

            # Print running count of how many seeds we generated every 10 seeds, and on the last one.
            num_gen = i + 1
            if num_gen % 10 == 0 or num_gen == options['samples']:
                elapsed = int(round(time.time() - start))
                self.stdout.write("Generated {} samples, elapsed time {}".format(
                    num_gen, datetime.timedelta(seconds=elapsed)), ending='\r')

        # Blank line for newline.
        self.stdout.write('')

        # Write star piece shuffle stats.
        with open(stars_file, 'w') as f:
            writer = csv.writer(f)
            header = ['Boss', 'Has Star']
            writer.writerow(header)

            keys = list(star_stats.keys())
            keys.sort()
            for boss in keys:
                row = [boss, '{:.2f}%'.format(star_stats[boss] / options['samples'] * 100)]
                writer.writerow(row)

        # Write key item shuffle stats.
        with open(key_items_file, 'w') as f:
            writer = csv.writer(f)
            locations = get_default_key_item_locations()
            header = ['Item'] + [l.name for l in locations]
            writer.writerow(header)

            keys = list(key_item_stats.keys())
            keys.sort()
            for item in keys:
                counts = key_item_stats[item]
                row = [item] + ['{:.2f}%'.format(counts[l.name] / options['samples'] * 100) for l in locations]
                writer.writerow(row)
