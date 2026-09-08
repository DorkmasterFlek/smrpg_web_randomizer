from __future__ import annotations
from typing import TYPE_CHECKING
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import *
from randomizer.data.variables.room_names import *
from randomizer.data.variables.event_script_names import *
from randomizer.data.variables.action_script_names import *
from randomizer.data.variables.pack_names import *
from randomizer.logic.progression.prizes import *
from randomizer.types.flags import *
from randomizer.logic.progression.prizelocations.access import (can_dodge_lands_end_enemies, expect_good_movement, not_earlygame, expect_halfway_decent_movement, almost_earlygame, is_midgame, expect_ok_movement, lategame)
from randomizer.types.logic import (Inventory)
from randomizer.types.prize import (SlotsPrize)
from randomizer.types.prizelocation import (KeyItemLocation, ShuffleLocationSelector, TreasureChestLocationRow3, WorldAreaEnum)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (NPC_8)
if TYPE_CHECKING:
    from randomizer.types.gameworld import (GameWorld)


class KeroSewersBeforeBelomeUpperAfterFlipLocation(
    KeyItemLocation, TreasureChestLocationRow3
):
    _originally_held = CricketJamPrize
    _rooms = [R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS]
    _npc_ids = [NPC_8]
    _id = ShuffleLocationSelector.KERO_SEWERS_BEFORE_BELOME_UPPER_2
    _world_area = WorldAreaEnum.KERO_SEWERS
    _blacklist = [
        EXPStarPrize,
        SecondMimicFightLauncher,
        ThirdMimicFightLauncher,
        SlotsPrize
    ]
    _hint = [
        # SetVarToConst(PRIMARY_TEMP_7000, 45),
        # RunDialog(
            # dialog_id=DI2010_DEBUG_7000,
            # above_object=BOWSER,
            # closable=True,
            # sync=False,
            # multiline=True,
            # use_background=True,
        # ),
        JmpIfObjectTriggerDisabledInSpecificLevel(
            NPC_8,
            R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS,
            ["next"],
        ),
        JmpIfBitSet(LANDS_END_GATED, ["next"]),
        JmpIfBitClear(LANDS_END_GROTTO_BARREL_FLIPPED, ["lands_end_grotto_hint_text"]),
        Jmp(["kero_sewers_hint_text"]),
    ]
    _access_conditions = "This check is the second time you open this chest. Requires flipping the barrel in Land's End."

    def can_access(self, inventory: Inventory, world: GameWorld) -> bool:
        return can_dodge_lands_end_enemies(world, inventory)


__all__ = ["KeroSewersBeforeBelomeUpperAfterFlipLocation"]
