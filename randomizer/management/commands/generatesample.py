import datetime
import random
import time

from django.core.management.base import BaseCommand

from randomizer.logic.main import GameWorld, Settings, VERSION


class Command(BaseCommand):
    help = 'Generate a statistical sampling of seeds to compare randomization spreads.'

    def add_arguments(self, parser):
        """Add optional arguments.

        Args:
            parser (argparse.ArgumentParser): Parser

        """
        parser.add_argument('-s', '--samples', dest='samples', default=10000, type=int,
                            help='Number of samples to generate.  Default: %(default)s')

        parser.add_argument('-o', '--output', dest='output_file', default='sample.csv',
                            help='Output file name.  Default: %(default)s')

        # TODO: Add mode argument once open mode is a thing.

    def handle(self, *args, **options):
        sysrand = random.SystemRandom()
        start = time.time()
        self.stdout.write("Generating {} samples of version {}".format(options['samples'], VERSION))
        self.stdout.write("Writing to output file: {}".format(options['output_file']))

        for i in range(options['samples']):
            # Generate random full standard seed.
            seed = sysrand.getrandbits(32)
            world = GameWorld(seed, Settings())
            world.randomize()

            # TODO: Write CSV info

            # Print running count of how many seeds we generated every 10 seeds, and on the last one.
            num_gen = i + 1
            if num_gen % 10 == 0 or num_gen == options['samples']:
                elapsed = int(round(time.time() - start))
                self.stdout.write("Generated {} samples, elapsed time {}".format(
                    num_gen, datetime.timedelta(seconds=elapsed)), ending='\r')

        # Blank line for newline.
        self.stdout.write('')
