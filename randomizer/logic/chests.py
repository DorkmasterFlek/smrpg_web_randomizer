# Chest randomization logic.

from randomizer.data import items
from randomizer.logic import flags


def randomize_all(world):
    """

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Check chest shuffle mode.
        shuffle_mode = world.settings.get_flag_choice(flags.ChestShuffleFlag)

        # TODO: Same area shuffle.
        if shuffle_mode is flags.ChestShuffle1:
            pass

        # TODO: More chest shuffle modes here.

        # Empty chests.
        elif shuffle_mode is flags.ChestShuffleEmpty:
            for chest in world.chest_locations:
                chest.item = items.YouMissed
