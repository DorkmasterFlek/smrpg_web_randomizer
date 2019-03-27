# Data module for areas and location data and base classes for key item/chest shuffle..

from enum import Enum, auto
from inspect import isclass

from randomizer.data import items
from randomizer.logic import utils
from randomizer.logic.patch import Patch


class Area(Enum):
    MariosPad = auto()
    MushroomWay = auto()
    MushroomKingdom = auto()
    BanditsWay = auto()
    KeroSewers = auto()
    MidasRiver = auto()
    TadpolePond = auto()
    RoseWay = auto()
    RoseTown = auto()
    RoseTownClouds = auto()
    ForestMaze = auto()
    Moleville = auto()
    MolevilleMines = auto()
    BoosterPass = auto()
    BoosterTower = auto()
    PipeVault = auto()
    YosterIsle = auto()
    Marrymore = auto()
    SeasideTown = auto()
    Sea = auto()
    SunkenShip = auto()
    LandsEnd = auto()
    BelomeTemple = auto()
    MonstroTown = auto()
    BeanValley = auto()
    NimbusLand = auto()
    BarrelVolcano = auto()
    BowsersKeep = auto()
    Factory = auto()


class ItemLocation:
    """Base class for an item location, either a key item or quest reward or chest."""
    area = Area.MariosPad
    addresses = []
    item = None
    missable = False
    access = 0

    def __init__(self, world):
        """

        Args:
            world (randomizer.logic.main.GameWorld):

        """
        self.world = world

    def __str__(self):
        if isinstance(self.item, items.Item):
            item_str = self.item.name
        elif isclass(self.item):
            item_str = self.item.__name__
        else:
            item_str = str(self.item)
        return '<{}: item {}>'.format(self.__class__.__name__, item_str)

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

    def item_allowed(self, item):
        """

        Args:
            item(randomizer.data.items.Item): Item to check.

        Returns:
            bool: True if the given item is allowed to be placed in this spot, False otherwise.

        """
        # If this is a missable location, it cannot contain a key item.
        if self.missable and not utils.isclass_or_instance(item, items.ChestReward) and item.is_key:
            return False

        # Normal locations can be anything except an invincibility star.
        return not utils.isclass_or_instance(item, items.InvincibilityStar)

    @property
    def has_item(self):
        return self.item is not None


class BowserRoom:
    relative_room_id = 0
    next_room_address = 0
    next_coord_address = 0
    start_x = 0
    start_y = 0
    start_z = 0
    backward_exit_byte = 0
    backward_event_byte = 0
    change_event_byte = 0
    change_event = 0
    is_final = False
class BowserDoorQuiz(BowserRoom):
    relative_room_id = 0xD0
    next_room_address = 0x1E234F
    next_coord_address = 0x1E2351
    change_event_byte = 0x20ED2E
    start_x = 3
    start_y = 106
class BowserDoorBarrel(BowserRoom):
    relative_room_id = 0xCF
    next_room_address = 0x1E2356
    next_coord_address = 0x1E2358
    change_event_byte = 0x20EDD3
    start_x = 2
    start_y = 55
class BowserDoorMarathon(BowserRoom):
    relative_room_id = 0xD2
    next_room_address = 0x1E22ED
    next_coord_address = 0x1E22EF
    change_event_byte = 0x20FC11
    start_x = 12
    start_y = 97
    is_final = True
class BowserDoorCoin(BowserRoom):
    relative_room_id = 0xD3
    next_room_address = 0x1E235D
    next_coord_address = 0x1E235F
    change_event_byte = 0x20F0EE
    start_x = 22
    start_y = 83
class BowserDoorButton(BowserRoom):
    relative_room_id = 0xD1
    next_room_address = 0x1E2364
    next_coord_address = 0x1E2366
    change_event_byte = 0x20F2A4
    start_x = 22
    start_y = 33
class BowserDoorSolitaire(BowserRoom):
    relative_room_id = 0xD4
    next_room_address = 0x1E22F4
    next_coord_address = 0x1E22F6
    change_event_byte = 0x20FC1D
    start_x = 22
    start_y = 123
    is_final = True
class BowserDoorInvisible(BowserRoom):
    relative_room_id = 0x42
    next_room_address = 0x1E2317
    next_coord_address = 0x1E2319
    change_event_byte = 0x20F38C
    start_x = 8
    start_y = 115
    start_z = 2
class BowserDoorXY(BowserRoom):
    relative_room_id = 0xCA
    next_room_address = 0x1E231E
    next_coord_address = 0x1E2320
    change_event_byte = 0x20F38F
    start_x = 7
    start_y = 117
    start_z = 2
    backward_exit_byte = 0x1D46F1
    backward_event_byte = 0x20FB8B
class BowserDoorDonkey(BowserRoom):
    relative_room_id = 0xC8
    next_room_address = 0x1E22FB
    next_coord_address = 0x1E22FD
    change_event_byte = 0x20FB75
    start_x = 22
    start_y = 123
    is_final = True
    backward_exit_byte = 0x1D46D6
class BowserDoorZ(BowserRoom):
    relative_room_id = 0x41
    next_room_address = 0x1E2325
    next_coord_address = 0x1E2327
    change_event_byte = 0x20F392
    start_x = 4
    start_y = 58
    start_z = 5
class BowserDoorCannonball(BowserRoom):
    relative_room_id = 0xC9
    next_room_address = 0x1E232C
    next_coord_address = 0x1E232E
    change_event_byte = 0x20F395
    start_x = 2
    start_y = 57
    backward_exit_byte = 0x1D46DF
    backward_event_byte = 0x20FB82
class BowserDoorRotating(BowserRoom):
    relative_room_id = 0xC7
    next_room_address = 0x1E2302
    next_coord_address = 0x1E2304
    change_event_byte = 0x20FB6C
    start_x = 6
    start_y = 47
    start_z = 1
    is_final = True
    backward_exit_byte = 0x1D46CD
class BowserDoorTerraCotta(BowserRoom):
    relative_room_id = 0xCB
    next_room_address = 0x1E2333
    next_coord_address = 0x1E2335
    change_event_byte = 0x20F398
    start_x = 2
    start_y = 63
class BowserDoorAlleyRat(BowserRoom):
    relative_room_id = 0xCC
    next_room_address = 0x1E233A
    next_coord_address = 0x1E233C
    change_event_byte = 0x20F39B
    start_x = 2
    start_y = 63
class BowserDoorBobomb(BowserRoom):
    relative_room_id = 0xCD
    next_room_address = 0x1E2309
    next_coord_address = 0x1E230B
    change_event_byte = 0x20FBDE
    start_x = 2
    start_y = 63
    is_final = True
class BowserDoorGuGoomba(BowserRoom):
    relative_room_id = 0xCE
    next_room_address = 0x1E2341
    next_coord_address = 0x1E2343
    change_event_byte = 0x20F39E
    start_x = 2
    start_y = 63
class BowserDoorChewy(BowserRoom):
    relative_room_id = 0x78
    next_room_address = 0x1E2348
    next_coord_address = 0x1E234A
    change_event_byte = 0x20F3A1
    start_x = 2
    start_y = 63
class BowserDoorSparky(BowserRoom):
    relative_room_id = 0x79
    next_room_address = 0x1E2310
    next_coord_address = 0x1E2312
    change_event_byte = 0x20F703
    start_x = 2
    start_y = 63
    is_final = True



# *** Helper functions to check access to certain areas.

def can_access_mines_back(inventory):
    """

    Args:
        inventory (randomizer.logic.keys.Inventory):

    Returns:
        bool: True if this location is accessible with the given inventory, False otherwise.

    """
    # Bambino Bomb is needed to access this location.
    return inventory.has_item(items.BambinoBomb)


def can_access_birdo(inventory):
    """

    Args:
        inventory (randomizer.logic.keys.Inventory):

    Returns:
        bool: True if this location is accessible with the given inventory, False otherwise.

    """
    # Castle Key 1 is needed to access this location.
    return inventory.has_item(items.CastleKey1)


def can_clear_nimbus_castle(inventory):
    """

    Args:
        inventory (randomizer.logic.keys.Inventory):

    Returns:
        bool: True if this location is accessible with the given inventory, False otherwise.

    """
    # Castle Key 2 is needed to access this location, plus defeating Birdo.
    return can_access_birdo(inventory) and inventory.has_item(items.CastleKey2)
