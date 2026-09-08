# E2399_ABYSS_ROOM_1_LOADER
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
	SetVarToConst(CURRENT_OVERWORLD_MARKER_ID, OW05_GATE),
	SetVarToConst(FACTORY_FALL_1, 219),
	ActionQueueAsync(target=NPC_0, subscript=[
		A_WalkNorthwestPixels(12)
	]),
	JmpIfBitSet(ABYSS_ENTRANCE_DIRECTIONAL_BIT, ["EVENT_2399_fade_in_music_7"]),
	ClearBit(ABYSS_ENTRANCE_DIRECTIONAL_BIT),
	FadeInFromBlack(sync=False),
	Return(),
	FadeInMusic(M0067_WEAPONSFACTORY, identifier="EVENT_2399_fade_in_music_7"),
	ClearBit(ABYSS_ENTRANCE_DIRECTIONAL_BIT),
	FreezeCamera(),
	PlaySound(sound=SO019_LONG_FALL, channel=6),
	ActionQueueSync(target=SCREEN_FOCUS, subscript=[
		A_SetWalkingSpeed(FASTEST),
		A_WalkToXYCoords(x=2, y=10)
	]),
	ActionQueueAsync(target=MARIO, subscript=[
		A_FloatingOff(),
		A_TransferToXYZF(x=4, y=25, z=21, direction=EAST),
		A_WalkSouthPixels(8)
	]),
	FadeInFromBlack(sync=False),
	ActionQueueAsync(target=MARIO, subscript=[
		A_FloatingOn(),
		A_JumpToHeight(height=0, silent=True),
		A_SetSpriteSequence(index=0, sprite_offset=1, is_sequence=True, looping=True),
		A_Pause(1, identifier="EVENT_2399_action_queue_13_SUBSCRIPT_pause_3"),
		A_JmpIfMarioInAir(["EVENT_2399_action_queue_13_SUBSCRIPT_pause_3"]),
		A_PlaySound(sound=SO058_INSERT, channel=4)
	]),
	SetAsyncActionScript(MARIO, A0395_PLAYER_RESET_PROPERTIES_AND_SOLIDITY),
	UnfreezeCamera(),
	JmpIfBitClear(SIGNAL_RING_DIRECTIONAL_BIT, ["EVENT_2399_ret_20"]),
    ClearBit(SIGNAL_RING_DIRECTIONAL_BIT),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_2399_ret_20"]),
	RunEventAsSubroutine(E3915_FACTORY_STAR_PIECE_SIGNAL),
	Return(identifier="EVENT_2399_ret_20")
])
