# E2364_TOWER_TOP_FLOOR_CHEST_ROOM_LOADER
# pyright: reportWildcardImportFromLibrary=false

from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import EventScript
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.colours import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.controller_inputs import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.coords import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.intro_title_text import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.layers import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.palette_types import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.scenes import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.tutorials import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.palette_rows import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.arguments import *
from ....variables.action_script_names import *
from ....variables.battlefield_names import *
from ....variables.dialog_names import *
from ....variables.event_script_names import *
from ....variables.music_names import *
from ....variables.overworld_area_names import *
from ....variables.overworld_sfx_names import *
from ....variables.pack_names import *
from ....variables.room_names import *
from ....variables.shop_names import *
from ....variables.variable_names import *
from ....items import *
from ....packets import *
from ....spells.spells import *
from ....variables.event_palette_names import *

script = EventScript([
	ActionQueueSync(target=NPC_1, subscript=[
		A_SetWalkingSpeed(FASTEST),
		A_WalkSouthPixels(8),
		A_SetWalkingSpeed(NORMAL),
		A_FaceSouthwest()
	]),
	ActionQueueSync(target=NPC_2, subscript=[
		A_SetWalkingSpeed(FASTEST),
		A_WalkSouthPixels(8),
		A_SetWalkingSpeed(NORMAL),
		A_FaceSouthwest()
	]),
	ActionQueueSync(target=NPC_5, subscript=[
		A_WalkSouthPixels(10),
	]),
	ActionQueueSync(target=NPC_0, subscript=[
		A_WalkNorthwestPixels(1),
		A_WalkSouthwestPixels(3)
	]),
	ActionQueueSync(target=NPC_4, subscript=[
		A_WalkSouthPixels(4)
	]),
	JmpIfBitClear(TEMP_7044_7, ["EVENT_2364_fade_in_from_black_async_10"]),
	RunEventAsSubroutine(E0081_MARIO_LANDS_SUBROUTINE),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_2364_ret_11"]),
	RunEventAsSubroutine(E3899_BOOSTER_TOWER_STAR_PIECE_SIGNAL),
	Jmp(["EVENT_2364_ret_11"]),
    
	FadeInFromBlack(sync=False, identifier="EVENT_2364_fade_in_from_black_async_10"),
	JmpIfBitClear(STAR_PIECE_GRANT_DIRECTIONAL_BIT, ["EVENT_2364_ret_11"]),
    
	SetVarToConst(PRIMARY_TEMP_7000, 528),
	RunEventAsSubroutine(E0178_NPC_QUEST_1_CONTAINER),
	RunEventAsSubroutine(E1202_POSTGAME_TOWER_CURTAIN_BOSS_UNLOCKS),
	SetVarToConst(PRIMARY_TEMP_7000, 528),
	JmpToEvent(E0167_BOSS_GRANT_STAR_PIECE),
    
	Return(identifier="EVENT_2364_ret_11")
])