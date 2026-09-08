#A0639_ROSE_TOWN_ARROW_THAT_FREEZES_TOAD_BY_INN
# pyright: reportWildcardImportFromLibrary=false

from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.coords import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.arguments import *
from ....variables.action_script_names import *
from ....variables.event_script_names import *
from ....variables.overworld_sfx_names import *
from ....variables.room_names import *
from ....variables.variable_names import *
from ....packets import *
from ....items import *

script = ActionScript([
	A_CopyVarToVar(from_var=ROSE_TOWN_FROZEN_TOAD_X, to_var=PRIMARY_TEMP_700C),
	A_CopyVarToVar(from_var=PRIMARY_TEMP_700C, to_var=X_COORD_2),
	A_CopyVarToVar(from_var=ROSE_TOWN_FROZEN_TOAD_Y, to_var=PRIMARY_TEMP_700C),
	A_CopyVarToVar(from_var=PRIMARY_TEMP_700C, to_var=Y_COORD_2),
	A_SetVarToConst(Z_COORD_2, 32),
	A_UnknownCommand(bytearray([0x9A])),
	A_JmpIfBitSet(TEMP_7043_0, ["ACTION_639_transfer_xyzf_pixels_9"]),
	A_TransferXYZFPixels(x=212, y=6, z=30, direction=NORTHEAST),
	A_Jmp(["ACTION_639_visibility_on_10"]),
	A_TransferXYZFPixels(x=244, y=14, z=30, direction=NORTHEAST, identifier="ACTION_639_transfer_xyzf_pixels_9"),
	A_VisibilityOn(identifier="ACTION_639_visibility_on_10"),
	A_Jmp(["ACTION_638_set_bit_4"])
])
