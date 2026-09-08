from randomizer.types.item import (Accessory)
from smrpgpatchbuilder.datatypes.items.enums import (ItemPrefix)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (
    BOWSER,
    GENO,
    MALLOW,
    MARIO,
    TOADSTOOL,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.party_character import (
    PartyCharacter,
)


class ExpBoosterItem(Accessory):
    """Exp Booster item class"""
    _item_name: str = "Exp. Booster"
    _prefix = ItemPrefix.RING

    _item_id: int = 80
    _description: str = " Doubles Exp.\n when equipped"
    _equip_chars: list[PartyCharacter] = [MARIO, TOADSTOOL, BOWSER, GENO, MALLOW]
    _price: int = 22
    _inflict_type = None

    _arbitrary_value: int = 10


__all__ = ["ExpBoosterItem"]
