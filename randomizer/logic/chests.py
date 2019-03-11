# Chest randomization logic.

import random

from randomizer.data import items, locations
from randomizer.logic import flags


def _intershuffle_chests(chests):
    """Shuffle the contents of the provided list of chests between each other.

    Args:
        chests(list[randomizer.data.chests.Chest]):

    """
    chests_to_shuffle = chests[:]
    random.shuffle(chests_to_shuffle)

    for chest in chests_to_shuffle:
        # Get other chests in this group that are able to swap items and pick one.
        options = [swap for swap in chests if swap != chest and chest.item_allowed(swap.item) and
                   swap.item_allowed(chest.item)]
        if options:
            swap = random.choice(options)
            chest.item, swap.item = swap.item, chest.item


def randomize_all(world):
    """

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Check chest shuffle mode.
        shuffle_mode = world.settings.get_flag_choice(flags.ChestShuffleFlag)

        # Same area shuffle.
        if shuffle_mode is flags.ChestShuffle1:
            for area in locations.Area:
                group = [chest for chest in world.chest_locations if chest.area == area]
                if group:
                    _intershuffle_chests(group)

        # TODO: More chest shuffle modes here.

        # Empty chests.
        elif shuffle_mode is flags.ChestShuffleEmpty:
            for chest in world.chest_locations:
                if chest.item_allowed(items.YouMissed):
                    chest.item = items.YouMissed
