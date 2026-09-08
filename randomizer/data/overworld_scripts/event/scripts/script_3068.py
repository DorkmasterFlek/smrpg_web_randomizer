# E3068_EMPTY
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
	DisableObjectTrigger(MEM_70A8),
	RemoveObjectFromCurrentLevel(MEM_70A8),
	PlaySound(sound=SO014_FLOWER, channel=6),
	MoveScriptToBackgroundThread2(),
	EnableControlsUntilReturn([LEFT, RIGHT, DOWN, UP, X, A, Y, B]),
	RestoreAllHP(),
	RestoreAllFP(),
	TintLayers(layers=[LAYER_L1, LAYER_L2, LAYER_L3, LAYER_L4, NPC_SPRITES, BACKGROUND], red=64, green=160, blue=64, speed=3, bit_15=True),
	TintLayers(layers=[LAYER_L1, LAYER_L2, LAYER_L3, LAYER_L4, NPC_SPRITES, BACKGROUND], red=0, green=0, blue=0, speed=3, bit_15=True),
	ResetPrioritySet(),
	MoveScriptToMainThread(),
	Return()
])
