# Key item randomization logic for open mode.

import random

from randomizer.data import keys
from . import flags, utils


def _item_location_filter(world, location):
    """Filter function for key item locations based on whether Seed/Fertilizer are included.

    Args:
        world (randomizer.logic.main.GameWorld):
        location (KeyItemLocation):

    Returns:
        bool:
    """
    if (isinstance(location, (keys.Seed, keys.Fertilizer)) and
            not world.settings.is_flag_enabled(flags.IncludeSeedFertilizer)):
        return False
    return True


def _place_items(world, items, locations, base_inventory=None):
    """Place the given list of items within the given locations, and optionally a given starting inventory.

    Args:
        world (randomizer.logic.main.GameWorld):
        items (Inventory):
        locations (list[KeyItemLocation]):
        base_inventory (Inventory):

    """
    if base_inventory is None:
        base_inventory = keys.Inventory()

    remaining_fill_items = keys.Inventory(items)

    if len(remaining_fill_items) > len([l for l in locations if not l.has_item]):
        raise ValueError("Trying to fill more items than available locations")

    # For each required item, place it assuming we can get all other items.
    for item in items:
        # Get items we can get assuming we have everything but the one we're placing.
        remaining_fill_items.remove(item)
        assumed_items = _collect_items(world, remaining_fill_items + base_inventory)

        fillable_locations = [l for l in locations if not l.has_item and l.can_access(assumed_items)]
        if not fillable_locations:
            raise ValueError("No available locations for {}, {}".format(item, remaining_fill_items))

        # Place item in the first fillable location.
        fillable_locations[0].item = item


def _collect_items(world, collected=None):
    """Collect the available items in the world.

    Args:
        world (randomizer.logic.main.GameWorld):
        collected (Inventory): Already collected items to start.

    Returns:
        Inventory: Collected items.

    """
    my_items = keys.Inventory()
    if collected is not None:
        my_items.extend(collected)

    available_locations = [l for l in world.key_locations if l.has_item]

    # Search all locations and collect items until we can't get any more.
    while True:
        search_locations = [l for l in available_locations if l.can_access(my_items)]
        available_locations = [l for l in available_locations if l not in search_locations]
        found_items = keys.Inventory([l.item for l in search_locations])
        my_items.extend(found_items)
        if len(found_items) == 0:
            break

    return my_items


def randomize_all(world):
    """

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Shuffle key item locations.
        if world.settings.is_flag_enabled(flags.KeyItemShuffle):
            locations_to_fill = [l for l in world.key_locations if _item_location_filter(world, l)]
            required_items = keys.Inventory([l.item for l in locations_to_fill if
                                             l.item.shuffle_type == utils.ItemShuffleType.Required])
            extra_items = keys.Inventory([l.item for l in locations_to_fill if
                                          l.item.shuffle_type == utils.ItemShuffleType.Extra])

            # Sanity check to make sure we're filling the right number of spots.
            if len(locations_to_fill) != len(required_items) + len(extra_items):
                raise ValueError("Locations length doesn't match number of items.")

            # Clear existing items to start.
            for location in locations_to_fill:
                location.item = None

            # Shuffle locations, required items and extra items.
            random.shuffle(locations_to_fill)
            random.shuffle(required_items)
            random.shuffle(extra_items)

            # Place required items first.
            _place_items(world, required_items, locations_to_fill)

            # Reverse remaining empty locations, then fill extra items.
            locations_to_fill = [l for l in locations_to_fill if not l.has_item]
            locations_to_fill.reverse()
            _place_items(world, extra_items, locations_to_fill)

            # Sanity check to make sure we can collect all the items.
            expected_items = keys.Inventory([l.item for l in world.key_locations])
            collected_items = _collect_items(world)
            if len(collected_items) != len(expected_items):
                raise ValueError("Can't get all collectable items in world: {}".format(world.key_locations))
