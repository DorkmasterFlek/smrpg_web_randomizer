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


class SignalRingItem(Accessory):
    """Signal Ring item class"""
    _item_name: str = "Signal Ring"
    _prefix = ItemPrefix.RING

    _item_id: int = 93
    _description: str = "Noise indicates\na hidden chest."
    _equip_chars: list[PartyCharacter] = [MARIO, TOADSTOOL, BOWSER, GENO, MALLOW]
    _speed: int = 10
    _price: int = 600
    _inflict_type = None

    _arbitrary_value: int = 50


__all__ = ["SignalRingItem"]
