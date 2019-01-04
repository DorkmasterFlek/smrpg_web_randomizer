# Key item randomization logic.

import random

from . import utils
from .patch import Patch


class KeyItemLocation:
    """Class for randomizing which key item is gotten in different locations."""
    addresses = []
    item = None

    def __str__(self):
        return '<{}: item {}>'.format(self.__class__.__name__, self.item)

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self.__class__.__name__

    def get_patch(self):
        """

        Returns:
            randomizer.logic.patch.Patch: Patch data

        """
        patch = Patch()

        for addr in self.addresses:
            patch.add_data(addr, utils.ByteField(self.item).as_bytes())

        return patch

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (list[randomizer.logic.items.Item]):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        return True

    @property
    def has_item(self):
        return self.item is not None


class Inventory(list):
    """List subclass for item inventory during key item shuffle logic."""

    def has_item(self, item):
        """

        Args:
            item(int): Item to check for.

        Returns:
            bool: True if inventory contains this item, False otherwise.

        """
        return any([i for i in self if i == item])


# ********************************** Actual location classes.
class MariosPad(KeyItemLocation):
    addresses = [0x1e620a]
    item = 162


class Croco1(KeyItemLocation):
    addresses = [0x1e94e1]
    item = 128


class MushroomKingdom(KeyItemLocation):
    addresses = [0x1e6608]
    item = 130

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Rare frog coin is needed to access this location.
        return inventory.has_item(128)


class RoseTown(KeyItemLocation):
    addresses = [0x1e6221, 0x1e6238]
    item = 163


class CricketJamChest(KeyItemLocation):
    addresses = [0x1e6256, 0x1e6261]
    item = 166


class MelodyBay1(KeyItemLocation):
    addresses = [0x1e627b]
    item = 151


class MelodyBay2(KeyItemLocation):
    addresses = [0x1e6290]
    item = 151

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Songs must be played in order, and Bambino Bomb is needed to access this location (beat minecart minigame).
        return MelodyBay1.can_access(inventory) and inventory.has_item(135)


class MelodyBay3(KeyItemLocation):
    addresses = [0x1e62a7]
    item = 151

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Songs must be played in order.
        return MelodyBay2.can_access(inventory)


class YosterIsle(KeyItemLocation):
    addresses = [0x1e62c0]
    item = 161


class Croco2(KeyItemLocation):
    addresses = [0x1e95ae]
    item = 135


class BoosterTowerAncestors(KeyItemLocation):
    addresses = [0x1e62da]
    item = 141


class BoosterTowerCheckerboard(KeyItemLocation):
    addresses = [0x1e62f9]
    item = 140


class SeasideTown(KeyItemLocation):
    addresses = [0x1e630d]
    item = 142


class MonstroTown(KeyItemLocation):
    addresses = [0x1e6321]
    item = 124


class Seed(KeyItemLocation):
    addresses = [0x1e6335]
    item = 158


class NimbusLandCastleKey(KeyItemLocation):
    addresses = [0x1e6355]
    item = 132


class Birdo(KeyItemLocation):
    addresses = [0x1e6370]
    item = 134

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 1 is needed to access this location.
        return inventory.has_item(132)


class Fertilizer(KeyItemLocation):
    addresses = [0x1e6399]
    item = 159

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 2 is needed to access this location, plus defeating Birdo.
        return Birdo.can_access(inventory) and inventory.has_item(134)


def get_default_key_item_locations():
    """Gets default key item locations.

    Returns:
        list[KeyItemLocation]: List of default key item locations.

    """
    return [
        MariosPad(),
        Croco1(),
        MushroomKingdom(),
        RoseTown(),
        CricketJamChest(),
        MelodyBay1(),
        MelodyBay2(),
        MelodyBay3(),
        YosterIsle(),
        Croco2(),
        BoosterTowerAncestors(),
        BoosterTowerCheckerboard(),
        SeasideTown(),
        MonstroTown(),
        Seed(),
        NimbusLandCastleKey(),
        Birdo(),
        Fertilizer(),
    ]


def _item_location_filter(world, location):
    """Filter function for key item locations based on whether Seed/Fertilizer are included.

    Args:
        world (randomizer.logic.main.GameWorld):
        location (KeyItemLocation):

    Returns:
        bool:
    """
    if isinstance(location, (Seed, Fertilizer)) and world.settings.randomize_key_items < 2:
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
        base_inventory = Inventory()

    remaining_fill_items = Inventory(items)

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
    my_items = Inventory()
    if collected is not None:
        my_items.extend(collected)

    available_locations = [l for l in world.key_locations if l.has_item]

    # Search all locations and collect items until we can't get any more.
    while True:
        search_locations = [l for l in available_locations if l.can_access(my_items)]
        available_locations = [l for l in available_locations if l not in search_locations]
        found_items = Inventory([l.item for l in search_locations])
        my_items.extend(found_items)
        if len(found_items) == 0:
            break

    return my_items


def randomize_key_items(world):
    """

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Shuffle key item locations.
        if world.settings.randomize_key_items:
            locations_to_fill = [l for l in world.key_locations if _item_location_filter(world, l)]
            # TODO: Add shuffle type flag for key items...
            required_items = Inventory([l.item for l in locations_to_fill if l.item in (128, 132, 134, 135)])
            extra_items = Inventory([l.item for l in locations_to_fill if l.item not in required_items])

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
            expected_items = Inventory([l.item for l in world.key_locations])
            collected_items = _collect_items(world)
            if len(collected_items) != len(expected_items):
                raise ValueError("Can't get all collectable items in world: {}".format(world.key_locations))
