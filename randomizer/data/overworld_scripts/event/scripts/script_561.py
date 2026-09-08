# E0561_PLACE_LINK_IN_ROSE_TOWN
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
	JmpIfBitClear(TEMP_7042_0, ["EVENT_561_action_queue_2"]),
	JmpToSubroutine(["EVENT_273_set_bit_91"]),
	ActionQueueAsync(target=NPC_0, subscript=[
		A_SetPriority(2)
	], identifier="EVENT_561_action_queue_2"),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_561_set_bit_7"]),
	FadeInFromBlack(sync=False),
	Return(),
	SetBit(SIGNAL_RING_DIRECTIONAL_BIT, identifier="EVENT_561_set_bit_7"),
	StopSound(identifier="EVENT_561_run_event_as_subroutine_8"),
	FadeOutMusicToVolume(duration=1, volume=96),
	RunEventAsSubroutine(E0081_MARIO_LANDS_SUBROUTINE),
	JmpIfBitClear(SIGNAL_RING_DIRECTIONAL_BIT, ["EVENT_561_ret_13"]),
    ClearBit(SIGNAL_RING_DIRECTIONAL_BIT),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_561_ret_13"]),
	RunEventAsSubroutine(E3895_ROSE_TOWN_STAR_PIECE_SIGNAL),
	Return(identifier="EVENT_561_ret_13")
])
