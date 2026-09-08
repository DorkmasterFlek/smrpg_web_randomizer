# E0529_ROSE_TOWN_OCCUPIED_EXTERIOR_LOADER
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
	UnknownCommand(bytearray([0xFD, 0x47])),
	CloseDialog(),
	FadeOutMusicToVolume(duration=1, volume=127),
	ActionQueueSync(target=NPC_3, subscript=[
		A_SetSpriteSequence(index=10, is_sequence=True, looping=True, mirror_sprite=True),
		A_SetPriority(2),
		A_ObjectMemoryClearBit(arg_1=0x08, bits=[3, 4])
	]),
	ActionQueueSync(target=NPC_4, subscript=[
		A_SetPriority(2),
		A_JmpIfBitSet(UNKNOWN_ROSE_TOWN_7060_0, ["EVENT_529_action_queue_4_SUBSCRIPT_transfer_to_xyzf_4"]),
		A_ClearSolidityBits(bit_4=True, cant_pass_npcs=True, cant_walk_through=True, bit_7=True),
		A_Jmp(["EVENT_529_action_queue_5"]),
		A_TransferToXYZF(x=12, y=47, z=2, direction=EAST, identifier="EVENT_529_action_queue_4_SUBSCRIPT_transfer_to_xyzf_4"),
		A_SetSpriteSequence(index=10, is_sequence=True, looping=True),
		A_ObjectMemoryClearBit(arg_1=0x08, bits=[3, 4])
	]),
	ActionQueueSync(target=NPC_0, subscript=[
		A_ObjectMemoryClearBit(arg_1=0x08, bits=[3, 4]),
		A_JmpIfBitClear(FREEZE_ROSE_TOWN_NPC_1, ["EVENT_529_action_queue_6"]),
		A_SetPriority(2)
	], identifier="EVENT_529_action_queue_5"),
	ActionQueueSync(target=NPC_6, subscript=[
		A_SetSpriteSequence(index=10, is_sequence=True, looping=True),
		A_SetPriority(3)
	], identifier="EVENT_529_action_queue_6"),
	ActionQueueSync(target=NPC_7, subscript=[
		A_SetSpriteSequence(index=1, is_mold=True, is_sequence=True, looping=True),
		A_SetPriority(3)
	]),
	ActionQueueSync(target=NPC_8, subscript=[
		A_SetSpriteSequence(index=1, is_mold=True, is_sequence=True, looping=True),
		A_SetPriority(3)
	]),
	JmpIfBitSet(FREEZE_ROSE_TOWN_NPC_1, ["EVENT_529_jmp_if_bit_set_14"]),
	ActionQueueAsync(target=SCREEN_FOCUS, subscript=[
		A_SetWalkingSpeed(FASTEST),
		A_WalkNortheastSteps(2)
	]),
	ActionQueueSync(target=NPC_0, subscript=[
		A_TransferXYZFPixels(x=240, y=8, z=0, direction=EAST),
		A_SetWalkingSpeed(SLOW),
		A_SetSequenceSpeed(FAST),
		A_Walk1StepNortheast(),
		A_SetPriority(2)
	]),
	SetSyncActionScript(NPC_7, A0637_ROSE_TOWN_INITIAL_ARROW),
	SetBit(FREEZE_ROSE_TOWN_NPC_1),
	JmpIfBitSet(FREEZE_ROSE_TOWN_NPC_2, ["EVENT_529_copy_var_to_var_18"], identifier="EVENT_529_jmp_if_bit_set_14"),
	ActionQueueSync(target=NPC_2, subscript=[
		A_SetSolidityBits(cant_pass_walls=True)
	]),
	SetSyncActionScript(NPC_2, A0021_STAND_STILL_AND_MOVE_RANDOM_DIRECTIONS),
	Jmp(["EVENT_529_fade_in_from_black_async_31"]),
	CopyVarToVar(from_var=ROSE_TOWN_FROZEN_TOAD_X, to_var=PRIMARY_TEMP_7000, identifier="EVENT_529_copy_var_to_var_18"),
	JmpIf7000AnyBitsSet(bits=[7], destinations=["EVENT_529_copy_var_to_var_27"]),
	ClearBit(TEMP_7043_2),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=X_COORD_2, identifier="EVENT_529_copy_var_to_var_20"),
	CopyVarToVar(from_var=ROSE_TOWN_FROZEN_TOAD_Y, to_var=PRIMARY_TEMP_7000),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=Y_COORD_2),
	SetVarToConst(Z_COORD_2, 2),
	ActionQueueAsync(target=NPC_2, subscript=[
		A_ObjectMemoryClearBit(arg_1=0x08, bits=[3, 4]),
		A_UnknownCommand(bytearray([0x9A])),
		A_JmpIfBitSet(TEMP_7043_2, ["EVENT_529_action_queue_24_SUBSCRIPT_set_sprite_sequence_6"]),
		A_FaceNorthwest(),
		A_TransferXYZFPixels(x=240, y=248, z=0, direction=EAST),
		A_Jmp(["EVENT_529_action_queue_24_SUBSCRIPT_fixed_f_coord_on_8"]),
		A_SetSpriteSequence(index=10, is_sequence=True, looping=True, mirror_sprite=True, identifier="EVENT_529_action_queue_24_SUBSCRIPT_set_sprite_sequence_6"),
		A_TransferXYZFPixels(x=16, y=8, z=0, direction=EAST),
		A_FixedFCoordOn(identifier="EVENT_529_action_queue_24_SUBSCRIPT_fixed_f_coord_on_8")
	]),
	Jmp(["EVENT_529_fade_in_from_black_async_31"]),
	CopyVarToVar(from_var=ROSE_TOWN_FROZEN_TOAD_X, to_var=PRIMARY_TEMP_7000, identifier="EVENT_529_copy_var_to_var_27"),
	Mem7000AndConst(0x007F),
	SetBit(TEMP_7043_2),
	Jmp(["EVENT_529_copy_var_to_var_20"]),
	RunEventAsSubroutine(E1094_ROSE_TOWN_OCCUPIED_EXTERIOR_SHUFFLED_NPC_ANIMATION_LOADER, identifier="EVENT_529_fade_in_from_black_async_31"),
	FadeInFromBlack(sync=False),
	JmpIfBitClear(SIGNAL_RING_DIRECTIONAL_BIT, ["EVENT_529_run_background_event_36"]),
    ClearBit(SIGNAL_RING_DIRECTIONAL_BIT),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_529_run_background_event_36"]),
	RunEventAsSubroutine(E3895_ROSE_TOWN_STAR_PIECE_SIGNAL),
	RunBackgroundEvent(event_id=E0530_ROSE_TOWN_OCCUPIED_BACKGROUND_1, return_on_level_exit=True, identifier="EVENT_529_run_background_event_36"),
	RunBackgroundEvent(event_id=E0551_ROSE_TOWN_OCCUPIED_MODS, return_on_level_exit=True, bit_6=True),
	JmpIfBitSet(FREEZE_ROSE_TOWN_NPC_1, ["EVENT_256_ret_0"]),
	Pause(10),
	Return()
])
