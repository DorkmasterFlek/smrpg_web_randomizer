"""Graphical adjustments driven by character recruitment order.

Extracted from the apply_shuffler_results orchestrator.
"""

from __future__ import annotations
from randomizer.data.rooms.npcs import BOWSER_ENDING

from typing import TYPE_CHECKING
from randomizer.data.rooms.npcs import (
    ALLY_CLONE_NPC,
    BOWSER_STATUE_NPC,
    BOWSER_WALKING_DOWN_LEFT_NPC_2,
    EMPTY_NPC,
    GENO_STATUE_NPC,
    GENO_WALKING_DOWN_LEFT_NPC_2_CLONEABLE,
    MALLOW_WALKING_DOWN_LEFT_NPC_2,
    MARIO_STATUE_NPC,
    MARIO_WALKING_DOWN_LEFT_NPC,
    TOADSTOOL_STATUE_NPC,
    TOADSTOOL_WALKING_DOWN_LEFT_LOW_VRAM,
    TOAD_STATUE_NPC,
)
from randomizer.data.sprites.subs.bowser.sprite_132 import (sprite as BOWSER_132)
from randomizer.data.sprites.subs.bowser.sprite_135 import (sprite as BOWSER_135)
from randomizer.data.sprites.subs.bowser.sprite_136 import (sprite as BOWSER_136)
from randomizer.data.sprites.subs.bowser.sprite_621 import (sprite as BOWSER_621)
from randomizer.data.sprites.subs.bowser.sprite_96 import (sprite as BOWSER_96)
from randomizer.data.sprites.subs.bowser.sprite_969 import (sprite as BOWSER_969)
from randomizer.data.sprites.subs.bowser.sprite_970 import (sprite as BOWSER_970)
from randomizer.data.sprites.subs.bowser.sprite_971 import (sprite as BOWSER_971)
from randomizer.data.sprites.subs.bowser.sprite_972 import (sprite as BOWSER_972)
from randomizer.data.sprites.subs.bowser.sprite_973 import (sprite as BOWSER_973)
from randomizer.data.sprites.subs.bowser.sprite_974 import (sprite as BOWSER_974)
from randomizer.data.sprites.subs.bowser.sprite_975 import (sprite as BOWSER_975)
from randomizer.data.sprites.subs.geno.sprite_132 import (sprite as GENO_132)
from randomizer.data.sprites.subs.geno.sprite_135 import (sprite as GENO_135)
from randomizer.data.sprites.subs.geno.sprite_136 import (sprite as GENO_136)
from randomizer.data.sprites.subs.geno.sprite_621 import (sprite as GENO_621)
from randomizer.data.sprites.subs.geno.sprite_96 import (sprite as GENO_96)
from randomizer.data.sprites.subs.geno.sprite_983 import (sprite as GENO_983)
from randomizer.data.sprites.subs.geno.sprite_984 import (sprite as GENO_984)
from randomizer.data.sprites.subs.geno.sprite_985 import (sprite as GENO_985)
from randomizer.data.sprites.subs.geno.sprite_986 import (sprite as GENO_986)
from randomizer.data.sprites.subs.geno.sprite_987 import (sprite as GENO_987)
from randomizer.data.sprites.subs.geno.sprite_988 import (sprite as GENO_988)
from randomizer.data.sprites.subs.geno.sprite_989 import (sprite as GENO_989)
from randomizer.data.sprites.subs.mallow.sprite_132 import (sprite as MALLOW_132)
from randomizer.data.sprites.subs.mallow.sprite_135 import (sprite as MALLOW_135)
from randomizer.data.sprites.subs.mallow.sprite_136 import (sprite as MALLOW_136)
from randomizer.data.sprites.subs.mallow.sprite_621 import (sprite as MALLOW_621)
from randomizer.data.sprites.subs.mallow.sprite_96 import (sprite as MALLOW_96)
from randomizer.data.sprites.subs.mallow.sprite_976 import (sprite as MALLOW_976)
from randomizer.data.sprites.subs.mallow.sprite_977 import (sprite as MALLOW_977)
from randomizer.data.sprites.subs.mallow.sprite_978 import (sprite as MALLOW_978)
from randomizer.data.sprites.subs.mallow.sprite_979 import (sprite as MALLOW_979)
from randomizer.data.sprites.subs.mallow.sprite_980 import (sprite as MALLOW_980)
from randomizer.data.sprites.subs.mallow.sprite_981 import (sprite as MALLOW_981)
from randomizer.data.sprites.subs.mallow.sprite_982 import (sprite as MALLOW_982)
from randomizer.data.sprites.subs.peach.sprite_132 import (sprite as TOADSTOOL_132)
from randomizer.data.sprites.subs.peach.sprite_135 import (sprite as TOADSTOOL_135)
from randomizer.data.sprites.subs.peach.sprite_136 import (sprite as TOADSTOOL_136)
from randomizer.data.sprites.subs.peach.sprite_621 import (sprite as TOADSTOOL_621)
from randomizer.data.sprites.subs.peach.sprite_96 import (sprite as TOADSTOOL_96)
from randomizer.data.sprites.subs.peach.sprite_962 import (sprite as TOADSTOOL_962)
from randomizer.data.sprites.subs.peach.sprite_963 import (sprite as TOADSTOOL_963)
from randomizer.data.sprites.subs.peach.sprite_964 import (sprite as TOADSTOOL_964)
from randomizer.data.sprites.subs.peach.sprite_965 import (sprite as TOADSTOOL_965)
from randomizer.data.sprites.subs.peach.sprite_966 import (sprite as TOADSTOOL_966)
from randomizer.data.sprites.subs.peach.sprite_967 import (sprite as TOADSTOOL_967)
from randomizer.data.sprites.subs.peach.sprite_968 import (sprite as TOADSTOOL_968)
from randomizer.data.variables.dialog_names import (
    DI1163_BOOSTER_TOWER_DOOR_OPEN,
    DI2320_TOADSTOOL_ROOM_HINT,
)
from randomizer.data.variables.event_palette_names import (
    EPAL0085_MALLOW_ENDING,
    EPAL0086_GENO_ENDING,
    EPAL0104_GOLD_TOAD,
    EPAL0108_MALLOW_STATUE,
    EPAL0109_GENO_PEACH_STATUE,
    EPAL0111_GOLD_MARIO_BOWSER,
    EPAL0140_BOWSER_ENDING,
    EPAL0141_TOADSTOOL_ENDING,
)
from randomizer.data.variables.event_script_names import (E1331_TOWER_BREAK_DOWN_DOOR)
from randomizer.data.variables.room_names import (
    R179_SUNKEN_SHIP_POSTKC_AREA_06_MARIO_MIRROR_ROOM,
    R202_BOOSTER_TOWER_ENTRANCE,
    R315_SEASIDE_TOWN_DURING_YARIDOVICH_BEACH,
    R341_NIMBUS_LAND_GARROS_HOUSE,
    R496_FACTORY_GROUNDS_FIGHT_WITH_SMITHY_USES_SLEDGE,
)
from randomizer.data.variables.sprite_names import (
    SPR0031_ALT_PROTAGONIST_1,
    SPR0032_ALT_PROTAGONIST_2,
    SPR0033_ALT_PROTAGONIST_3,
    SPR0034_ALT_PROTAGONIST_4,
    SPR0035_ALT_PROTAGONIST_5,
    SPR0036_ALT_PROTAGONIST_6,
    SPR0037_ALT_PROTAGONIST_7,
    SPR0096_MARIO_DOLL_SURPRISED,
    SPR0132_MOLEVILLE_MINE_CART,
    SPR0135_MINE_CART_BAD_PALETTE,
    SPR0136_MARIO_IN_MINE_CART,
    SPR0621_OLD_CLASSIC_MARIO,
)
from randomizer.logic.palette_rows import (npc_palette_rows)
from randomizer.logic.progression.prizelocations import (MushroomWayCharacter, StartingCharacter1)
from randomizer.types.ally import (SpriteAnimationState)
from randomizer.types.flags import (BoosterTowerGate, BoosterTowerGating)
from randomizer.types.prize import (CharacterPrize)
from randomizer.types.prizelocation import (CharacterRecruitmentLocation)
from randomizer.types.room import (Room)
from randomizer.utils.event_script_snippets.tower_access_scripts import (
    bowser_script,
    bowser_self_script,
    geno_script,
    geno_self_script,
    mallow_script,
    mallow_self_script,
    mario_script,
    mario_self_script,
    toadstool_script,
    toadstool_self_script,
)
from smrpgpatchbuilder.datatypes.levels.classes import (BaseRoomObject)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.arguments import (NORMAL)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import (
    A_SetSpriteSequence,
    A_SetWalkingSpeed,
    A_TransferXYZFPixels,
    A_WalkNortheastSteps,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments import (
    EAST,
    MARIO_PALETTE,
    NPC_PALETTE_ROW_1,
    NPC_PALETTE_ROW_2,
    NPC_PALETTE_ROW_3,
    NPC_PALETTE_ROW_4,
    NPC_PALETTE_ROW_6,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (
    NPC_0,
    NPC_3,
    NPC_4,
    NPC_6,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
    ActionQueueSync,
    PaletteSet,
    PaletteSetMorphs,
)
from smrpgpatchbuilder.datatypes.scripts_common.classes import (IdentifierException)
from typing import (cast)

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld



def apply_booster_tower_gating_graphics(world: GameWorld) -> None:

    # Booster Tower gating animation
    # On paper this could go into setup/gating.py, but script insertion depends on who the starting character is, which can be random
    tower_door_room = world.rooms._rooms[R202_BOOSTER_TOWER_ENTRANCE]
    assert tower_door_room is not None, f"Room {R202_BOOSTER_TOWER_ENTRANCE} not found"
    tower_npc_0 = tower_door_room.get_npc_by_target_id(NPC_0)
    assert tower_npc_0 is not None, f"NPC_0 not found in room {R202_BOOSTER_TOWER_ENTRANCE}"
    tower_npc_3 = tower_door_room.get_npc_by_target_id(NPC_3)
    assert tower_npc_3 is not None, f"NPC_3 not found in room {R202_BOOSTER_TOWER_ENTRANCE}"
    tower_npc_4 = tower_door_room.get_npc_by_target_id(NPC_4)
    assert tower_npc_4 is not None, f"NPC_4 not found in room {R202_BOOSTER_TOWER_ENTRANCE}"
    if not world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.GENO):
        tower_npc_3._npc = EMPTY_NPC
    if not world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.TOADSTOOL):
        tower_npc_4._npc = EMPTY_NPC

    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MARIO):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN, """ You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n a pretty good jumper for that.[await]""")
        if world.overworld_character.ally.index == 0:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                mario_self_script.contents
            )
        else:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                mario_script.contents
            )
            tower_npc_0._npc = MARIO_WALKING_DOWN_LEFT_NPC
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MALLOW):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN, """ You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n some pretty magical fluff for that.[await]""")
        if world.overworld_character.ally.index == 4:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                mallow_self_script.contents
            )
        else:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                mallow_script.contents
            )
            tower_npc_0._npc = MALLOW_WALKING_DOWN_LEFT_NPC_2
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.GENO):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN,""" You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n a pretty strong gun for that.[await]""")
        if world.overworld_character.ally.index == 3:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                geno_self_script.contents
            )
        else:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                geno_script.contents
            )
            tower_npc_0._npc = GENO_WALKING_DOWN_LEFT_NPC_2_CLONEABLE
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.BOWSER):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN,""" You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n a REALLY strong person for that.[await]""")
        if world.overworld_character.ally.index == 2:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                bowser_self_script.contents
            )
        else:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                bowser_script.contents
            )
            tower_npc_0._npc = BOWSER_WALKING_DOWN_LEFT_NPC_2
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.TOADSTOOL):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN,""" You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n a pyrotechnician for that.[await]""")
        if world.overworld_character.ally.index == 1:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                toadstool_self_script.contents
            )
        else:
            world.event_scripts.get_script_by_id(E1331_TOWER_BREAK_DOWN_DOOR).set_contents(
                toadstool_script.contents
            )
            tower_npc_0._npc = TOADSTOOL_WALKING_DOWN_LEFT_LOW_VRAM
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.PUNCHINELLO):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN,""" You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n someone famous for that.[await]""")
    elif world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MINES):
        world.overworld_dialogs.replace_dialog(DI1163_BOOSTER_TOWER_DOOR_OPEN,""" You can\u2019t get inside Booster\u2019s\n Tower very easily. You\u2019ll need\n to get there via minecart.[await]""")


def apply_protagonist_sprite_swaps(world: GameWorld) -> None:
    # put the right character clone in the sunken ship mirror room
    # and also sub character sprites in overworld where appropriate
    # some other edge case logic for character-specific stuff could go here too
    clone_room = world.rooms._rooms[R179_SUNKEN_SHIP_POSTKC_AREA_06_MARIO_MIRROR_ROOM]
    assert clone_room is not None, f"Room {R179_SUNKEN_SHIP_POSTKC_AREA_06_MARIO_MIRROR_ROOM} not found"
    clone_room_npc_0 = clone_room.get_npc_by_target_id(NPC_0)
    assert clone_room_npc_0 is not None, f"NPC_0 not found in room {R179_SUNKEN_SHIP_POSTKC_AREA_06_MARIO_MIRROR_ROOM}"

    
    starter = cast(CharacterPrize, world.get_location(StartingCharacter1).prize).ally
    # Always have sprites available for the file select menu
    if starter.index == 1:
        world.sprites.sprites[SPR0031_ALT_PROTAGONIST_1] = TOADSTOOL_962
        world.sprites.sprites[SPR0032_ALT_PROTAGONIST_2] = TOADSTOOL_963
        world.sprites.sprites[SPR0033_ALT_PROTAGONIST_3] = TOADSTOOL_964
    elif starter.index == 2:
        world.sprites.sprites[SPR0031_ALT_PROTAGONIST_1] = BOWSER_969
        world.sprites.sprites[SPR0032_ALT_PROTAGONIST_2] = BOWSER_970
        world.sprites.sprites[SPR0033_ALT_PROTAGONIST_3] = BOWSER_971
    elif starter.index == 3:
        world.sprites.sprites[SPR0031_ALT_PROTAGONIST_1] = GENO_983
        world.sprites.sprites[SPR0032_ALT_PROTAGONIST_2] = GENO_984
        world.sprites.sprites[SPR0033_ALT_PROTAGONIST_3] = GENO_985
    elif starter.index == 4:
        world.sprites.sprites[SPR0031_ALT_PROTAGONIST_1] = MALLOW_976
        world.sprites.sprites[SPR0032_ALT_PROTAGONIST_2] = MALLOW_977
        world.sprites.sprites[SPR0033_ALT_PROTAGONIST_3] = MALLOW_978

    # Fully commit to the bit if you've changed your overworld character altogether
    if world.overworld_character.ally.index > 0:
        if world.overworld_character.ally.index == 1:
            world.sprites.sprites[SPR0096_MARIO_DOLL_SURPRISED] = TOADSTOOL_96
            world.sprites.sprites[SPR0132_MOLEVILLE_MINE_CART] = TOADSTOOL_132
            world.sprites.sprites[SPR0135_MINE_CART_BAD_PALETTE] = TOADSTOOL_135
            world.sprites.sprites[SPR0136_MARIO_IN_MINE_CART] = TOADSTOOL_136
            world.sprites.sprites[SPR0621_OLD_CLASSIC_MARIO] = TOADSTOOL_621
            world.sprites.sprites[SPR0034_ALT_PROTAGONIST_4] = TOADSTOOL_965
            world.sprites.sprites[SPR0035_ALT_PROTAGONIST_5] = TOADSTOOL_966
            world.sprites.sprites[SPR0036_ALT_PROTAGONIST_6] = TOADSTOOL_967
            world.sprites.sprites[SPR0037_ALT_PROTAGONIST_7] = TOADSTOOL_968
            world.update_dialog(DI2320_TOADSTOOL_ROOM_HINT, " Hello, Princess![await][pause] Did you forget\n something in your room?[await]")
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
        elif world.overworld_character.ally.index == 2:
            world.sprites.sprites[SPR0096_MARIO_DOLL_SURPRISED] = BOWSER_96
            world.sprites.sprites[SPR0132_MOLEVILLE_MINE_CART] = BOWSER_132
            world.sprites.sprites[SPR0135_MINE_CART_BAD_PALETTE] = BOWSER_135
            world.sprites.sprites[SPR0136_MARIO_IN_MINE_CART] = BOWSER_136
            world.sprites.sprites[SPR0621_OLD_CLASSIC_MARIO] = BOWSER_621
            world.sprites.sprites[SPR0034_ALT_PROTAGONIST_4] = BOWSER_972
            world.sprites.sprites[SPR0035_ALT_PROTAGONIST_5] = BOWSER_973
            world.sprites.sprites[SPR0036_ALT_PROTAGONIST_6] = BOWSER_974
            world.sprites.sprites[SPR0037_ALT_PROTAGONIST_7] = BOWSER_975
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_from_row(NPC_PALETTE_ROW_3)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_to_row(NPC_PALETTE_ROW_3)
        elif world.overworld_character.ally.index == 3:
            world.sprites.sprites[SPR0096_MARIO_DOLL_SURPRISED] = GENO_96
            world.sprites.sprites[SPR0132_MOLEVILLE_MINE_CART] = GENO_132
            world.sprites.sprites[SPR0135_MINE_CART_BAD_PALETTE] = GENO_135
            world.sprites.sprites[SPR0136_MARIO_IN_MINE_CART] = GENO_136
            world.sprites.sprites[SPR0621_OLD_CLASSIC_MARIO] = GENO_621
            world.sprites.sprites[SPR0034_ALT_PROTAGONIST_4] = GENO_986
            world.sprites.sprites[SPR0035_ALT_PROTAGONIST_5] = GENO_987
            world.sprites.sprites[SPR0036_ALT_PROTAGONIST_6] = GENO_988
            world.sprites.sprites[SPR0037_ALT_PROTAGONIST_7] = GENO_989
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
        elif world.overworld_character.ally.index == 4:
            world.sprites.sprites[SPR0096_MARIO_DOLL_SURPRISED] = MALLOW_96
            world.sprites.sprites[SPR0132_MOLEVILLE_MINE_CART] = MALLOW_132
            world.sprites.sprites[SPR0135_MINE_CART_BAD_PALETTE] = MALLOW_135
            world.sprites.sprites[SPR0136_MARIO_IN_MINE_CART] = MALLOW_136
            world.sprites.sprites[SPR0621_OLD_CLASSIC_MARIO] = MALLOW_621
            world.sprites.sprites[SPR0034_ALT_PROTAGONIST_4] = MALLOW_979
            world.sprites.sprites[SPR0035_ALT_PROTAGONIST_5] = MALLOW_980
            world.sprites.sprites[SPR0036_ALT_PROTAGONIST_6] = MALLOW_981
            world.sprites.sprites[SPR0037_ALT_PROTAGONIST_7] = MALLOW_982
            world.event_scripts.get_command_by_identifier("midas_palette_1", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_2", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_3", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_4", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_5", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
            world.event_scripts.get_command_by_identifier("midas_palette_6", PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)
        clone_room_npc_0._npc = ALLY_CLONE_NPC
    else:
        world.event_scripts.delete_command_by_identifier("midas_palette_1")
        world.event_scripts.delete_command_by_identifier("midas_palette_2")
        world.event_scripts.delete_command_by_identifier("midas_palette_3")
        world.event_scripts.delete_command_by_identifier("midas_palette_4")
        world.event_scripts.delete_command_by_identifier("midas_palette_5")
        world.event_scripts.delete_command_by_identifier("midas_palette_6")

    # Room 496 ending cutscene: pick the first non-Bowser slot among the four
    # character recruit positions (19/20/21/22) and demote it to cannot_clone=False
    # so the partition orchestrator can place it in a clone buffer.
    #
    # KILL-SWITCH: set R496_DEMOTE_FIRST_NON_BOWSER = False to disable.
    # When disabled, all four slots stay cannot_clone=True per the room source file,
    # and the orchestrator at update_changed_room_partitions handles buffer/min_vram
    # sizing entirely on its own.
    #
    # NOTE on buffer space: the demoted NPC's clone-buffer slot needs enough
    # main_buffer_space to fit any non-walk sequences declared in the room's
    # npc_expected_animations for that slot. That sizing is computed by
    # _recalculate_room_partition in partition_calculator.py (step ~568+,
    # npc_expected_animations consumer block), which adjusts the buffer's
    # main_buffer_space field based on each animation state's max_sequence_vram.
    # If that step is undersizing the buffer, fix is in partition_calculator.py
    # NOT here - this hook only flips the cannot_clone bit.
    R496_DEMOTE_FIRST_NON_BOWSER = False
    if R496_DEMOTE_FIRST_NON_BOWSER:
        r496 = world.rooms._rooms[R496_FACTORY_GROUNDS_FIGHT_WITH_SMITHY_USES_SLEDGE]
        if r496 is not None:
            bowser_sprite_id = BOWSER_ENDING.sprite_id
            candidate_slots = (19, 20, 21, 22)
            for slot in candidate_slots:
                if slot >= len(r496.objects):
                    continue
                obj = r496.objects[slot]
                if obj._npc.sprite_id == bowser_sprite_id:
                    continue  # Bowser must stay cannot_clone (non-gridplane sprite)
                obj.set_cannot_clone(False)
                break  # only demote one slot


def _apply_seaside_boss_palette_morph_row(world: GameWorld) -> None:
    """Point seaside_palette_morph_1 at whichever CGRAM row R315's boss NPC got.

    The morph recolours object 6 (the fake elder who turns into the boss), so
    it must target that object's palette row. Rows are handed out per distinct
    palette in object order, so the row depends on how many palettes objects
    0-5 claim - which changes once boss/henchman substitution has swapped their
    NPCs, and again when a palette declares extra rows (the palette-swap merge
    gives a carrier extra_palette_source_offset=1 + a row count, and those rows
    sit adjacent to its own).

    Runs before finalize_world grows ally_sprite_buffer_size for the chosen
    protagonist, so the projected size is used instead of the current one -
    Bowser needs two rows and pushes every NPC row down by one.
    """
    room = world.rooms._rooms[R315_SEASIDE_TOWN_DURING_YARIDOVICH_BEACH]
    assert isinstance(room, Room), (
        f"Room {R315_SEASIDE_TOWN_DURING_YARIDOVICH_BEACH} not found"
    )
    projection = room.project_ally_sprite_buffer_size(world)
    ally_buffer_size = None if projection is None else min(3, projection[0])

    obj = room.get_npc_by_target_id(NPC_6)
    palette = world.get_sprite(int(obj._npc.sprite_id)).palette_id
    row = npc_palette_rows(world, room, ally_buffer_size).get(palette)
    assert row is not None, (
        f"R315 NPC_6 palette {palette} has no CGRAM row - it can only be missing "
        "if the object shares the protagonist's palette, which the boss NPC never does"
    )
    world.event_scripts.get_command_by_identifier(
        "seaside_palette_morph_1", PaletteSetMorphs
    ).set_row(row)


def apply_recruitment_palette_adjustments(world: GameWorld) -> None:
    # Update the "hide from Toad" animation to use the overworld character's
    # defend mold, so the correct sprite frame shows when cowering.
    ally = world.overworld_character.ally
    defend_mold = ally._sprites_primary.get(SpriteAnimationState.DEFEND_MOLD)
    if defend_mold is not None:
        hide_cmd = world.event_scripts.get_subscript_command_by_identifier(
            "EVENT_273_hide_from_toad_subscript",
            "EVENT_273_hide_from_toad",
            A_SetSpriteSequence,
        )
        hide_cmd.set_index(defend_mold[1])
        hide_cmd = world.event_scripts.get_subscript_command_by_identifier(
            "crouch_for_coin_aq",
            "crouch_for_coin",
            A_SetSpriteSequence,
        )
        hide_cmd.set_index(defend_mold[1])
    # Dojo post-battle "challenge hold": freeze MARIO on the final mold of the
    # protagonist's challenge sequence so they stay in the fighting pose through
    # the deescalate cutscene.
    challenge = ally._sprites_primary[SpriteAnimationState.CHALLENGE]
    challenge_offset = challenge[0]
    challenge_seq = challenge[1]
    challenge_base_sprite = 0 if ally.index == 0 else SPR0031_ALT_PROTAGONIST_1
    challenge_sprite = world.get_sprite(challenge_base_sprite + challenge_offset)
    challenge_final_mold = challenge_sprite.animation.properties.sequences[challenge_seq].frames[-1].mold_id
    if ally.index != 0:
        # nimbus cutscene
        world.event_scripts.get_command_by_identifier("EVENT_738_action_queue_63_SUBSCRIPT", ActionQueueSync).set_subscript([
            A_SetWalkingSpeed(NORMAL),
            A_WalkNortheastSteps(3),
            A_TransferXYZFPixels(x=252, y=254, z=0, direction=EAST),
            A_SetSpriteSequence(index=challenge[1], sprite_offset=challenge[0], is_sequence=True, looping=False),
        ])

    # masher animation
    if ally.index != 0:
        world.event_scripts.get_subscript_command_by_identifier("tower_lean_back_aq", "tower_lean_back_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("tower_lean_back_aq", "tower_lean_back_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("tower_lean_back_aq", "tower_lean_back_full", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("main_hall_lean_back_aq", "main_hall_lean_back", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("main_hall_lean_back_aq", "main_hall_lean_back_surprised", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.SHOCKED_SHADOW_BACKWARDS)[1])
        world.event_scripts.get_subscript_command_by_identifier("green_kid_lean_forward_aq", "green_kid_lean_back_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("green_kid_lean_forward_aq", "green_kid_lean_forward_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_FORWARD)[1])
        world.event_scripts.get_subscript_command_by_identifier("green_kid_lean_forward_aq", "green_kid_lean_forward_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_FORWARD)[1])
        world.event_scripts.get_subscript_command_by_identifier("EVENT_3717_action_queue_6", "EVENT_3717_fan_lean_back_full", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("EVENT_3717_action_queue_6", "EVENT_3717_fan_lean_back_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("EVENT_3717_action_queue_6", "EVENT_3717_fan_lean_back_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("EVENT_3717_action_queue_6", "EVENT_3717_fan_lean_forward_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_FORWARD)[1])
        world.event_scripts.get_subscript_command_by_identifier("tadpole_thinking_aq", "tadpole_thinking", A_SetSpriteSequence).set_sprite_offset(ally._sprites_primary.get(SpriteAnimationState.THINKING)[0])
        world.event_scripts.get_subscript_command_by_identifier("tadpole_thinking_aq", "tadpole_thinking", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.THINKING)[1])
        world.event_scripts.get_subscript_command_by_identifier("keep_fall_thinking_aq", "keep_fall_thinking", A_SetSpriteSequence).set_sprite_offset(ally._sprites_primary.get(SpriteAnimationState.THINKING)[0])
        world.event_scripts.get_subscript_command_by_identifier("keep_fall_thinking_aq", "keep_fall_thinking", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.THINKING)[1])
        world.event_scripts.get_subscript_command_by_identifier("keep_heal_arms_raised_aq", "keep_heal_arms_raised", A_SetSpriteSequence).set_sprite_offset(ally._sprites_primary.get(SpriteAnimationState.ARMS_RAISED)[0])
        world.event_scripts.get_subscript_command_by_identifier("keep_heal_arms_raised_aq", "keep_heal_arms_raised", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.ARMS_RAISED)[1])
        world.event_scripts.get_subscript_command_by_identifier("climb_mold_aq_1", "climb_mold_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.CLIMB_MOLD_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("climb_mold_aq_2", "climb_mold_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.CLIMB_MOLD_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("climb_mold_aq_3", "climb_mold_3", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.CLIMB_MOLD_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("climb_mold_aq_4", "climb_mold_4", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.CLIMB_MOLD_2)[1])
        world.event_scripts.get_subscript_command_by_identifier("neutral_blackjack_aq_1", "neutral_blackjack_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.NEUTRAL_BLACKJACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("neutral_blackjack_aq_2", "neutral_blackjack_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.NEUTRAL_BLACKJACK)[1])
        world.event_scripts.get_subscript_command_by_identifier("EVENT_2630_action_queue_365", "neutral_blackjack_3", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.NEUTRAL_BLACKJACK)[1])
        # bandits way anim - ally.index is sprite/area-object order
        # (Geno = 3), but Set7000ToIDOfMemberInSlot reports the party roster
        # in menu order (Geno = 2). Convert so the script's protagonist check
        # matches; otherwise a non-Mario protagonist gets cloned.
        # ending_protag_lean_back_1/2 target the Mario NPC (NPC_19) in R496, which
        # always uses sprite 0 (Mario) regardless of starter character. The script
        # source already hardcodes the correct mold (index=23, sprite_offset=2),
        # so don't overwrite with the starter's mold_id - that would render
        # Toadstool's/Bowser's/etc. lean-back mold using Mario's sprite 2 layout
        # and produce a garbled mold.
        # world.event_scripts.get_subscript_command_by_identifier("ending_protag_lean_back_1_aq", "ending_protag_lean_back_1", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])
        # world.event_scripts.get_subscript_command_by_identifier("ending_protag_lean_back_2_aq", "ending_protag_lean_back_2", A_SetSpriteSequence).set_index(ally._sprites_primary.get(SpriteAnimationState.LEAN_BACK)[1])

    # script_3885 darken-layers preserve_rows depend on the overworld character.
    # The protagonist palette gets loaded into MARIO_PALETTE row regardless of
    # ally_buffer state, AND the same character is also in NPC_PALETTE_ROW_1 (or
    # whichever row their recruit slot uses). For non-Mario starters, preserving
    # MARIO_PALETTE leaves the recruit-slot version of the protagonist character
    # un-darkened too because the palette colors match. For Mario starter, the
    # recruit-slot version (Toadstool at NPC_PALETTE_ROW_1) is the marrymore
    # character, who should also stay un-darkened during this scene.
    overworld_ally = world.overworld_character.ally
    if overworld_ally.index == 0:  # Mario protagonist
        ending_darken_preserve = [MARIO_PALETTE, NPC_PALETTE_ROW_1]
    else:                          # non-Mario protagonist
        ending_darken_preserve = [NPC_PALETTE_ROW_1, NPC_PALETTE_ROW_4]
    # for darken_id in ("ending_darken_1", "ending_darken_2"):
    #     cmd = world.event_scripts.get_command_by_identifier(darken_id, DarkenLayersExceptPaletteRows)
    #     cmd.set_preserve_rows(ending_darken_preserve)

    # script_3951 (R375 ending credits) per-NPC palette-row swap is handled
    # in renders.py via _apply_r375_protagonist_palette_rows, called from
    # apply_ending_characters.

    _apply_seaside_boss_palette_morph_row(world)

    # Set palettes that change when the protagonist changes.
    if ally.index == 2: # bowser shifts a lot of stuff...
        world.event_scripts.get_command_by_identifier("mallow_statue_palette_set", PaletteSet).set_from_row(NPC_PALETTE_ROW_4)
        world.event_scripts.get_command_by_identifier("mallow_statue_palette_set", PaletteSet).set_to_row(NPC_PALETTE_ROW_4)
        world.event_scripts.get_subscript_command_by_identifier("keep_heal_arms_raised_aq", "keep_heal_arms_raised", A_SetSpriteSequence).set_mirror_sprite(False)
        bowser_palette_rows: list[tuple[str, int]] = [
            ("kamek_palette", NPC_PALETTE_ROW_3),
            ("infinite_coin_chest_palette", NPC_PALETTE_ROW_2),
            ("kamek_palette_2", NPC_PALETTE_ROW_3),
            ("infinite_coin_chest_palette_2", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_1", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_2", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_3", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_4", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_5", NPC_PALETTE_ROW_2),
            ("kamek_palette_br_6", NPC_PALETTE_ROW_2),
            ("kamek_palette_3", NPC_PALETTE_ROW_3),
        ]
        for identifier, row in bowser_palette_rows:
            try:
                command = world.event_scripts.get_command_by_identifier(identifier)
            except IdentifierException:
                continue
            if isinstance(command, PaletteSetMorphs):
                command.set_row(row)
            elif isinstance(command, PaletteSet):
                command.set_from_row(row)
                command.set_to_row(row)
            else:
                raise TypeError(
                    f"{identifier} is {type(command).__name__}, expected a palette command"
                )
    # statue minigame
    if ally.index in [1, 3]:
        world.event_scripts.get_command_by_identifier("protagonist_becomes_gold", PaletteSet).set_palette_set_starts_at(EPAL0109_GENO_PEACH_STATUE)
    elif ally.index == 4:
        world.event_scripts.get_command_by_identifier("protagonist_becomes_gold", PaletteSet).set_palette_set_starts_at(EPAL0108_MALLOW_STATUE)
    # don't do anything for mario/bowser, they both use #111
    # set default palettes for reset reasons
    resets = ["remove_statue_palette_1", "remove_statue_palette_2", "hot_spring_reset_palette"]
    for reset in resets:
        if ally.index == 1:
            world.event_scripts.get_command_by_identifier(reset, PaletteSet).set_palette_set_starts_at(EPAL0141_TOADSTOOL_ENDING)
        elif ally.index == 2:
            world.event_scripts.get_command_by_identifier(reset, PaletteSet).set_palette_set_starts_at(EPAL0140_BOWSER_ENDING)
        elif ally.index == 3:
            world.event_scripts.get_command_by_identifier(reset, PaletteSet).set_palette_set_starts_at(EPAL0086_GENO_ENDING)
        elif ally.index == 4:
            world.event_scripts.get_command_by_identifier(reset, PaletteSet).set_palette_set_starts_at(EPAL0085_MALLOW_ENDING)

    # Garros's house statue (room 341 NPC 4) reflects whoever was recruited at Mushroom Way.
    # Recruit ally indices: 0=Mario, 1=Toadstool, 2=Bowser, 3=Geno, 4=Mallow.
    # No prize at all → location is filled with the Toad placeholder (e.g. fewer recruits than slots).
    if MushroomWayCharacter in world.locations:
        mw_loc = cast(CharacterRecruitmentLocation, world.get_location(MushroomWayCharacter))
        statue_npc = None
        statue_palette = None
        if mw_loc.prize is None:
            statue_npc = TOAD_STATUE_NPC
            statue_palette = EPAL0104_GOLD_TOAD
        else:
            mw_index = cast(CharacterPrize, mw_loc.prize).ally.index
            statue_npc_by_index = {
                0: MARIO_STATUE_NPC,
                1: TOADSTOOL_STATUE_NPC,
                2: BOWSER_STATUE_NPC,
                3: GENO_STATUE_NPC,
            }
            statue_palette_by_index = {
                0: EPAL0111_GOLD_MARIO_BOWSER,
                1: EPAL0109_GENO_PEACH_STATUE,
                2: EPAL0111_GOLD_MARIO_BOWSER,
                3: EPAL0109_GENO_PEACH_STATUE,
            }
            statue_npc = statue_npc_by_index.get(mw_index)
            statue_palette = statue_palette_by_index.get(mw_index)
        if statue_npc is not None:
            statue_obj = world.get_room(R341_NIMBUS_LAND_GARROS_HOUSE).get_npc_by_target_id(NPC_4)
            cast(BaseRoomObject, statue_obj)._npc = statue_npc
        if statue_palette is not None:
            world.event_scripts.get_command_by_identifier("mallow_statue_palette_set", PaletteSet).set_palette_set_starts_at(statue_palette)


__all__ = ['apply_booster_tower_gating_graphics', 'apply_protagonist_sprite_swaps', 'apply_recruitment_palette_adjustments']
