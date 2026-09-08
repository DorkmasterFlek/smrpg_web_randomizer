# E0520_ROSE_TOWN_OCCUPIED_EXTERIOR_PINK_TOAD
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
	JmpIfBitSet(FREEZE_ROSE_TOWN_NPC_2, ["EVENT_520_run_dialog_29"]),
	PauseActionScript(NPC_2),
	Set7016701BToObjectXYZ(target=NPC_2, bit_7=True),
	CopyVarToVar(from_var=X_COORD_2, to_var=PRIMARY_TEMP_7000),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=ROSE_TOWN_FROZEN_TOAD_X),
	CopyVarToVar(from_var=Y_COORD_2, to_var=PRIMARY_TEMP_7000),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=ROSE_TOWN_FROZEN_TOAD_Y),
	StartAsyncEmbeddedActionScript(target=NPC_2, prefix=0xF1, subscript=[
		A_ClearSolidityBits(cant_pass_walls=True),
		A_ClearSolidityBits(bit_4=True, cant_pass_npcs=True, cant_walk_through=True, bit_7=True),
		A_FixedFCoordOn(),
		A_SetWalkingSpeed(SLOW),
		A_WalkTo70167018()
	]),
	RunDialog(dialog_id=DI0788_SOME_JERK_IN_THE_FOREST, above_object=MEM_70A8, closable=True, sync=False, multiline=True, use_background=True),
	ActionQueueAsync(target=NPC_2, subscript=[
		A_FixedFCoordOff(),
		A_SetSolidityBits(cant_walk_through=True),
		A_FaceMario()
	]),
	JmpIfBitSet(TEMP_7044_3, ["EVENT_520_resume_action_script_27"]),
	ActionQueueAsync(target=NPC_2, subscript=[
		A_UnknownCommand(bytearray([0xFD, 0x24, 0x07, 0x00])),
		A_Mem700CAndConst(0x00C0),
		A_CopyVarToVar(from_var=PRIMARY_TEMP_700C, to_var=TEMP_702A),
		A_JmpIfVarEqualsConst(PRIMARY_TEMP_700C, 0, ["EVENT_520_action_queue_11_SUBSCRIPT_face_northwest_7"]),
		A_JmpIfVarEqualsConst(PRIMARY_TEMP_700C, 64, ["EVENT_520_action_queue_11_SUBSCRIPT_set_700C_to_object_coord_9"]),
		A_JmpIfVarEqualsConst(PRIMARY_TEMP_700C, 128, ["EVENT_520_action_queue_11_SUBSCRIPT_face_southeast_14"]),
		A_JmpIfVarEqualsConst(PRIMARY_TEMP_700C, 192, ["EVENT_520_action_queue_11_SUBSCRIPT_set_700C_to_object_coord_9"]),
		A_FaceNorthwest(identifier="EVENT_520_action_queue_11_SUBSCRIPT_face_northwest_7"),
		A_Jmp(["EVENT_520_action_queue_12"]),
		A_Set700CToObjectCoord(target_npc=NPC_2, coord=COORD_X, pixel=True, bit_7=True, identifier="EVENT_520_action_queue_11_SUBSCRIPT_set_700C_to_object_coord_9"),
		A_CopyVarToVar(from_var=PRIMARY_TEMP_700C, to_var=TEMP_702C),
		A_CompareVarToConst(TEMP_702C, 4),
		A_JmpIfComparisonResultIsGreaterOrEqual(["EVENT_520_action_queue_11_SUBSCRIPT_face_northwest_7"]),
		A_Jmp(["EVENT_520_action_queue_11_SUBSCRIPT_face_southeast_14"]),
		A_FaceSoutheast(identifier="EVENT_520_action_queue_11_SUBSCRIPT_face_southeast_14"),
		A_SetBit(TEMP_7043_0)
	]),
	ActionQueueSync(target=NPC_2, subscript=[
		A_SetWalkingSpeed(SLOW),
		A_ClearSolidityBits(cant_pass_walls=True),
		A_Walk1StepFDirection(),
		A_Set700CToObjectCoord(target_npc=NPC_2, coord=COORD_F),
		A_JmpIfVarEqualsConst(PRIMARY_TEMP_700C, 5, ["EVENT_520_action_queue_12_SUBSCRIPT_object_memory_clear_bit_6"]),
		A_SetSpriteSequence(index=10, is_sequence=True, looping=True, mirror_sprite=True),
		A_ObjectMemoryClearBit(arg_1=0x08, bits=[3, 4], identifier="EVENT_520_action_queue_12_SUBSCRIPT_object_memory_clear_bit_6")
	], identifier="EVENT_520_action_queue_12"),
	SetAsyncActionScript(NPC_7, A0639_ROSE_TOWN_ARROW_THAT_FREEZES_TOAD_BY_INN),
	RememberLastObject(),
	Set70107015ToObjectXYZ(target=NPC_2, bit_7=True),
	CopyVarToVar(from_var=X_COORD_2, to_var=PRIMARY_TEMP_7000),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=ROSE_TOWN_FROZEN_TOAD_X),
	JmpIfBitSet(TEMP_7043_0, ["EVENT_520_add_const_to_var_25"]),
	CopyVarToVar(from_var=Y_COORD_2, to_var=PRIMARY_TEMP_7000, identifier="EVENT_520_copy_var_to_var_19"),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=ROSE_TOWN_FROZEN_TOAD_Y),
	SetSyncActionScript(NPC_2, A0015_DO_NOTHING),
	ClearBit(TEMP_7043_0),
	SetBit(FREEZE_ROSE_TOWN_NPC_2),
	Return(),
	AddConstToVar(ROSE_TOWN_FROZEN_TOAD_X, 128, identifier="EVENT_520_add_const_to_var_25"),
	Jmp(["EVENT_520_copy_var_to_var_19"]),
	ResumeActionScript(NPC_2, identifier="EVENT_520_resume_action_script_27"),
	Return(),
	RunDialog(dialog_id=DI0813_CANT_MOVE, above_object=MEM_70A8, closable=True, sync=False, multiline=True, use_background=True, identifier="EVENT_520_run_dialog_29"),
	Return()
])
