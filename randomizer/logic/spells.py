# Spell randomization logic.

from . import utils
from .patch import Patch

STARTING_FP = 10


class Spell:
    """Class representing a magic spell to be randomized."""
    BASE_ADDRESS = 0x3a20f1
    BASE_NAME_ADDRESS = 0x3a137f

    def __init__(self, index, name, fp, power, hitrate):
        """
        :type index: int
        :type name: str
        :type fp: int
        :type power: int
        :type hitrate: int
        """
        self.index = index
        self.name = name
        self.fp = utils.Stat(fp, 1, 99)
        self.power = utils.Stat(power)
        self.hitrate = utils.Stat(hitrate, 1, 100)

    def randomize(self):
        """Perform randomization for this spell."""
        self.fp.shuffle()

        # Don't shuffle power or hitrate for Geno Boost, it causes problems if it deals damage.
        if self.index == 0x11:
            self.power.value = 0
            self.hitrate.value = 100
        else:
            self.power.shuffle()
            self.hitrate.shuffle()

    def get_patch(self):
        """Get patch for this spell.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # FP is byte 3, power is byte 6, hit rate is byte 7.  Each spell is 12 bytes.
        base_addr = self.BASE_ADDRESS + (self.index * 12)
        patch.add_data(base_addr + 2, self.fp.as_bytes())
        patch.add_data(base_addr + 5, self.power.as_bytes())
        patch.add_data(base_addr + 6, self.hitrate.as_bytes())

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

