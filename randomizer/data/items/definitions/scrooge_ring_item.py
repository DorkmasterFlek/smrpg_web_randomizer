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


class ScroogeRingItem(Accessory):
    """Scrooge Ring item class"""
    _item_name: str = "Scrooge Ring"
    _prefix = ItemPrefix.RING

    _item_id: int = 79
    _description: str = " Cuts FP use\n in half\n during battle"
    _equip_chars: list[PartyCharacter] = [MARIO, TOADSTOOL, BOWSER, GENO, MALLOW]
    _price: int = 50
    _inflict_type = None

    _arbitrary_value: int = 1

    _remake_name = "Flower Ring"


__all__ = ["ScroogeRingItem"]
