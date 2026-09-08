# E0641_MARRYMORE_ANTECHAMBER_LOADER_EXTENSION
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
	ActionQueueAsync(target=NPC_1, subscript=[
		A_SetPriority(3),
		A_SetVRAMPriority(MARIO_OVERLAPS_ON_ALL_SIDES),
		A_TransferXYZFPixels(x=0, y=3, z=0, direction=EAST)
	]),
	ApplySolidityModToLevel(permanent=True, room_id=R153_MARRYMORE_CHAPEL_ENTRANCE_TO_SANCTUARY, mod_id=0),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_641_run_event_as_subroutine_7"]),
	FadeInFromBlack(sync=False),
	JmpIfBitSet(MARRYMORE_LIBERATED, ["EVENT_641_fade_in_from_black_async_10"]),
	SetBit(SANCTUARY_LOCKED),
	Return(),
	RunEventAsSubroutine(E0081_MARIO_LANDS_SUBROUTINE, identifier="EVENT_641_run_event_as_subroutine_7"),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_641_ret_11"]),
	RunEventAsSubroutine(E3902_MARRYMORE_STAR_PIECE_SIGNAL),
	Return(identifier="EVENT_641_ret_11"),
    JmpIfBitClear(STAR_PIECE_GRANT_DIRECTIONAL_BIT, ["EVENT_641_ret_11"], identifier="EVENT_641_fade_in_from_black_async_10"),
    JmpIfBitSet(POSTGAME_CHAPEL_COMPLETE, ["EVENT_641_ret_11"]),
    SetBit(POSTGAME_CHAPEL_COMPLETE),
	SetVarToConst(PRIMARY_TEMP_7000, 529),
	RunEventAsSubroutine(E0181_NPC_QUEST_4_CONTAINER),
	RunEventAsSubroutine(E1205_POSTGAME_CHAPEL_BOSS_UNLOCKS),
	SetVarToConst(PRIMARY_TEMP_7000, 529),
	JmpToEvent(E0167_BOSS_GRANT_STAR_PIECE),
    
])
