from randomizer.types.item import (Accessory)
from smrpgpatchbuilder.datatypes.items.enums import (ItemPrefix)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (MARIO)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.party_character import (
    PartyCharacter,
)


class JumpShoesItem(Accessory):
    """Jump Shoes item class"""
    _item_name: str = "Jump Shoes"
    _prefix = ItemPrefix.RING

    _item_id: int = 76
    _description: str = "Use jump attacks\nagainst any foe"
    _equip_chars: list[PartyCharacter] = [MARIO]
    _speed: int = 2
    _defense: int = 1
    _magic_attack: int = 5
    _magic_defense: int = 1
    _price: int = 30
    _inflict_type = None

    _arbitrary_value: int = 1


__all__ = ["JumpShoesItem"]
