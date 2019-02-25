# Key item randomization data for open mode.

from randomizer.logic import utils
from randomizer.logic.patch import Patch
from . import items


class KeyItemLocation:
    """Class for randomizing which key item is gotten in different locations."""
    addresses = []
    item = None

    def __str__(self):
        return '<{}: item {}>'.format(self.__class__.__name__, self.item.__name__)

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
            patch.add_data(addr, utils.ByteField(self.item.index).as_bytes())

        return patch

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory(Inventory): Current inventory of collected items.

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
            item: Item class to check for.

        Returns:
            bool: True if inventory contains this item, False otherwise.

        """
        return any([i for i in self if i == item])


# ********************************** Actual location classes.
class MariosPad(KeyItemLocation):
    addresses = [0x1e620a]
    item = items.DryBonesFlag


class Croco1(KeyItemLocation):
    addresses = [0x1e94e1]
    item = items.RareFrogCoin


class MushroomKingdom(KeyItemLocation):
    addresses = [0x1e6608]
    item = items.CricketPie

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Rare frog coin is needed to access this location.
        return inventory.has_item(items.RareFrogCoin)


class RoseTown(KeyItemLocation):
    addresses = [0x1e6221, 0x1e6238]
    item = items.GreaperFlag


class CricketJamChest(KeyItemLocation):
    addresses = [0x1e6256, 0x1e6261]
    item = items.CricketJam


class MelodyBay1(KeyItemLocation):
    addresses = [0x1e627b]
    item = items.AltoCard


class MelodyBay2(KeyItemLocation):
    addresses = [0x1e6290]
    item = items.AltoCard

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Songs must be played in order, and Bambino Bomb is needed to access this location (beat minecart minigame).
        return MelodyBay1.can_access(inventory) and inventory.has_item(items.BambinoBomb)


class MelodyBay3(KeyItemLocation):
    addresses = [0x1e62a7]
    item = items.AltoCard

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
    item = items.BigBooFlag


class Croco2(KeyItemLocation):
    addresses = [0x1e95ae]
    item = items.BambinoBomb


class BoosterTowerAncestors(KeyItemLocation):
    addresses = [0x1e62da]
    item = items.ElderKey


class BoosterTowerCheckerboard(KeyItemLocation):
    addresses = [0x1e62f9]
    item = items.RoomKey


class SeasideTown(KeyItemLocation):
    addresses = [0x1e630d]
    item = items.ShedKey


class MonstroTown(KeyItemLocation):
    addresses = [0x1e6321]
    item = items.TempleKey


class Seed(KeyItemLocation):
    addresses = [0x1e6335]
    item = items.Seed


class NimbusLandCastleKey(KeyItemLocation):
    addresses = [0x1e6355]
    item = items.CastleKey1


class Birdo(KeyItemLocation):
    addresses = [0x20a3b0]
    item = items.CastleKey2

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 1 is needed to access this location.
        return inventory.has_item(items.CastleKey1)


class Fertilizer(KeyItemLocation):
    addresses = [0x1e6399]
    item = items.Fertilizer

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 2 is needed to access this location, plus defeating Birdo.
        return Birdo.can_access(inventory) and inventory.has_item(items.CastleKey2)


# ********************* Default lists for the world.

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
