# E3724_NIMBUS_CASTLE_OUTER_CELLAR_LOADER
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
	SetVarToConst(CURRENT_OVERWORLD_MARKER_ID, OW49_NIMBUS_LAND),
	ActionQueueSync(target=NPC_0, subscript=[
		A_TransferXYZFPixels(x=0, y=0, z=2, direction=EAST)
	]),
	JmpIfBitSet(NIMBUS_LAND_LIBERATED, ["EVENT_3724_jmp_if_bit_set_5"]),
	ActionQueueSync(target=MARIO, subscript=[
		A_SetSpriteSequence(index=28, sprite_offset=2, is_mold=True, is_sequence=True, looping=True),
		A_Pause(1),
		A_ResetProperties()
	]),
	ActionQueueAsync(target=NPC_2, subscript=[
		A_TransferXYZFPixels(x=0, y=0, z=2, direction=EAST)
	]),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_3724_run_event_as_subroutine_8"], identifier="EVENT_3724_jmp_if_bit_set_5"),
	FadeInFromBlack(sync=False),
	Return(),
	RunEventAsSubroutine(E0081_MARIO_LANDS_SUBROUTINE, identifier="EVENT_3724_run_event_as_subroutine_8"),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_3724_ret_9"]),
	RunEventAsSubroutine(E3912_NIMBUS_STAR_PIECE_SIGNAL),
	Return(identifier="EVENT_3724_ret_9")
])
