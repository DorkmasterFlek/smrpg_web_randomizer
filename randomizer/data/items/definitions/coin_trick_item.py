from randomizer.types.item import (Accessory)
from smrpgpatchbuilder.datatypes.items.enums import (ItemPrefix)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (MARIO)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.party_character import (
    PartyCharacter,
)


class CoinTrickItem(Accessory):
    """Coin Trick item class"""
    _item_name: str = "Coin Trick"
    _prefix = ItemPrefix.RING

    _item_id: int = 88
    _description: str = " Doubles the\n coins you win\n in battle"
    _equip_chars: list[PartyCharacter] = [MARIO]
    _price: int = 36
    _inflict_type = None

    _arbitrary_value: int = 2


__all__ = ["CoinTrickItem"]
