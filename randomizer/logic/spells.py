# Spell randomization logic.

from . import utils
from .patch import Patch

STARTING_FP = 10


class Spell:
    """Class representing a magic spell to be randomized."""
    BASE_ADDRESS = 0x3a20f1
    BASE_NAME_ADDRESS = 0x3a137f

    def __init__(self, index, name, fp, power, hitrate, instant_ko):
        """
        :type index: int
        :type name: str
        :type fp: int
        :type power: int
        :type hitrate: int
        :type instant_ko: bool
        """
        self.index = index
        self.name = name
        self.fp = fp
        self.power = power
        self.hitrate = hitrate
        self.instant_ko = instant_ko

    def randomize(self):
        """Perform randomization for this spell."""
        self.fp = utils.mutate_normal(self.fp, minimum=1, maximum=99)

        # Don't shuffle power or hitrate for Geno Boost, it causes problems if it deals damage.
        if self.index == 0x11:
            self.power = 0
            self.hitrate = 100
        else:
            self.power = utils.mutate_normal(self.power)

            # If the spell is instant death, cap hit rate at 99% so items that protect from this actually work.
            # Protection forces the attack to miss, but 100% hit rate can't "miss" so it hits anyway.
            if self.instant_ko:
                max_hit_rate = 99
            else:
                max_hit_rate = 100
            self.hitrate = utils.mutate_normal(self.hitrate, minimum=1, maximum=max_hit_rate)

    def get_patch(self):
        """Get patch for this spell.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # FP is byte 3, power is byte 6, hit rate is byte 7.  Each spell is 12 bytes.
        base_addr = self.BASE_ADDRESS + (self.index * 12)
        patch.add_data(base_addr + 2, utils.ByteField(self.fp).as_bytes())
        data = utils.ByteField(self.power).as_bytes()
        data += utils.ByteField(self.hitrate).as_bytes()
        patch.add_data(base_addr + 5, data)

        # Add updated name.
        base_addr = self.BASE_NAME_ADDRESS + (self.index * 15)
        name = self.name.ljust(15)
        patch.add_data(base_addr, name)

        return patch


def randomize_spells(world):
    """Randomize everything for spells for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    if world.settings.randomize_spell_stats:
        # Randomize spell stats.
        for spell in world.spells:
            spell.randomize()

        # Randomize starting FP if we're randomizing spell stats.
        world.starting_fp = utils.mutate_normal(world.starting_fp, minimum=1, maximum=99)

        # If we're generating a debug mode seed for testing, set max FP to start.
        if world.settings.debug_mode:
            world.starting_fp = 99

