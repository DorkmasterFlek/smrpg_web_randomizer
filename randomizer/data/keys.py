# Key item randomization data for open mode.

from . import items
from .locations import Area, ItemLocation


class KeyItemLocation(ItemLocation):
    """Class for randomizing which key item is gotten in different locations."""
    pass


# ********************************** Actual location classes.
class MariosBed(KeyItemLocation):
    area = Area.MariosPad
    addresses = [0x1e620f]
    item = items.DryBonesFlag


class Croco1(KeyItemLocation):
    area = Area.BanditsWay
    addresses = [0x1e94e1]
    item = items.RareFrogCoin


class MushroomKingdomShop(KeyItemLocation):
    area = Area.MushroomKingdom
    addresses = [0x1e6610]
    item = items.CricketPie

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (randomizer.logic.keys.Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Rare frog coin is needed to access this location.
        return inventory.has_item(items.RareFrogCoin)


class RoseTownSign(KeyItemLocation):
    area = Area.RoseTown
    addresses = [0x1e6226, 0x1e623d]
    item = items.GreaperFlag


class CricketJamChest(KeyItemLocation):
    area = Area.KeroSewers
    addresses = [0x1e625b, 0x1e6266]
    item = items.CricketJam


class MelodyBaySong1(KeyItemLocation):
    area = Area.TadpolePond
    addresses = [0x1e6280]
    item = items.AltoCard


class MelodyBaySong2(KeyItemLocation):
    area = Area.TadpolePond
    addresses = [0x1e6295]
    item = items.AltoCard

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (randomizer.logic.keys.Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Songs must be played in order, and Bambino Bomb is needed to access this location (beat minecart minigame).
        return MelodyBaySong1.can_access(inventory) and inventory.has_item(items.BambinoBomb)


class MelodyBaySong3(KeyItemLocation):
    area = Area.TadpolePond
    addresses = [0x1e62ac]
    item = items.AltoCard

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (randomizer.logic.keys.Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Songs must be played in order.
        return MelodyBaySong2.can_access(inventory)


class YosterIsleGoal(KeyItemLocation):
    area = Area.YosterIsle
    addresses = [0x1e62c5]
    item = items.BigBooFlag


class Croco2(KeyItemLocation):
    area = Area.MolevilleMines
    addresses = [0x1e95ae]
    item = items.BambinoBomb


class BoosterTowerAncestors(KeyItemLocation):
    area = Area.BoosterTower
    addresses = [0x1e62df]
    item = items.ElderKey


class BoosterTowerCheckerboard(KeyItemLocation):
    area = Area.BoosterTower
    addresses = [0x1e62fe]
    item = items.RoomKey


class SeasideTownKey(KeyItemLocation):
    area = Area.SeasideTown
    addresses = [0x1e6312]
    item = items.ShedKey


class MonstroTownKey(KeyItemLocation):
    area = Area.MonstroTown
    addresses = [0x1e6326]
    item = items.TempleKey


class Seed(KeyItemLocation):
    area = Area.BeanValley
    addresses = [0x1e633a]
    item = items.Seed


class NimbusLandCastleKey(KeyItemLocation):
    area = Area.NimbusLand
    addresses = [0x1e635a]
    item = items.CastleKey1


class Birdo(KeyItemLocation):
    area = Area.NimbusLand
    addresses = [0x1e6378]
    item = items.CastleKey2

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (randomizer.logic.keys.Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 1 is needed to access this location.
        return inventory.has_item(items.CastleKey1)


class Fertilizer(KeyItemLocation):
    area = Area.NimbusLand
    addresses = [0x1e63a1]
    item = items.Fertilizer

    @staticmethod
    def can_access(inventory):
        """

        Args:
            inventory (randomizer.logic.keys.Inventory):

        Returns:
            bool: True if this location is accessible with the given inventory, False otherwise.

        """
        # Castle Key 2 is needed to access this location, plus defeating Birdo.
        return Birdo.can_access(inventory) and inventory.has_item(items.CastleKey2)


# ********************* Default lists for the world.

def get_default_key_item_locations(world):
    """Gets default key item locations.

    Args:
        world (randomizer.logic.main.GameWorld):

    Returns:
        list[ItemLocation]: List of default key item locations.

    """
    return [
        MariosBed(world),
        Croco1(world),
        MushroomKingdomShop(world),
        RoseTownSign(world),
        CricketJamChest(world),
        MelodyBaySong1(world),
        MelodyBaySong2(world),
        MelodyBaySong3(world),
        YosterIsleGoal(world),
        Croco2(world),
        BoosterTowerAncestors(world),
        BoosterTowerCheckerboard(world),
        SeasideTownKey(world),
        MonstroTownKey(world),
        Seed(world),
        NimbusLandCastleKey(world),
        Birdo(world),
        Fertilizer(world),
    ]
