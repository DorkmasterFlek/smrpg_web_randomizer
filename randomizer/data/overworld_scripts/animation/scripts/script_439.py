#A0439_ROSE_WAY_LAKITU
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
	A_ObjectMemorySetBit(arg_1=0x0D, bits=[6]),
	A_Pause(2),
	A_SetWalkingSpeed(SLOW),
	A_JmpIfVarEqualsConst(TEMP_70AE, 0, ["ACTION_439_visibility_off_57"]),
	A_KillAllSubroutineSlots(),
	A_UnknownCommand(bytearray([0xC8, 0x87])),
	A_SetVarToConst(Z_COORD_2, 12),
	A_UnknownCommand(bytearray([0x98])),
	A_SetVRAMPriority(OBJECT_OVERLAPS_MARIO_ON_ALL_SIDES),
	A_SetPriority(3),
	A_JmpIfVarEqualsConst(TEMP_70AE, 25, ["ACTION_439_db_19"]),
	A_ToggleSubroutineSlots(mask=0x04),
	A_EmbeddedAnimationRoutine(bytearray([0x28, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x08, 0x00, 0x01, 0x00, 0x00, 0x00, 0x04, 0x80])),
	A_SetSpriteSequence(index=6, is_sequence=True, looping=True, mirror_sprite=True),
	A_WalkToXYCoords(x=3, y=101, identifier="ACTION_439_walk_to_xy_coords_14"),
	A_WalkToXYCoords(x=8, y=93),
	A_WalkToXYCoords(x=14, y=104),
	A_WalkToXYCoords(x=8, y=93),
	A_JmpIfVarNotEqualsConst(TEMP_70AE, 25, ["ACTION_439_walk_to_xy_coords_14"]),
	A_UnknownCommand(bytearray([0xC8, 0x80]), identifier="ACTION_439_db_19"),
	A_WalkTo70167018(),
	A_KillAllSubroutineSlots(),
	A_ResetProperties(),
	A_FixedFCoordOff(),
	A_FaceMario(),
	A_Set700CToObjectCoord(target_npc=DUMMY_0X07, coord=COORD_F),
	A_Inc(PRIMARY_TEMP_700C),
	A_Mem700CAndConst(0x0007),
	A_CompareVarToConst(PRIMARY_TEMP_700C, 4),
	A_JmpIfComparisonResultIsGreaterOrEqual(["ACTION_439_set_animation_speed_44"]),
	A_SetSequenceSpeed(SLOW),
	A_FaceSoutheast(),
	A_SetSpriteSequence(index=3, looping=False, mirror_sprite=True),
	A_UnknownCommand(bytearray([0xC7, 0x07])),
	A_SetBit(TEMP_7044_7),
	A_Pause(48),
	A_CreatePacketAt7010WithEvent(packet=P028_MUSHROOM_THROWN_SOUTHWEST, event_id=E3068_EMPTY, destinations=["ACTION_439_reset_properties_37"]),
	A_ResetProperties(identifier="ACTION_439_reset_properties_37"),
	A_SetSequenceSpeed(NORMAL),
	A_Pause(128),
	A_SetWalkingSpeed(FAST),
	A_WalkToXYCoords(x=18, y=73),
	A_VisibilityOff(),
	A_ReturnQueue(),
	A_SetSequenceSpeed(SLOW, identifier="ACTION_439_set_animation_speed_44"),
	A_FaceSouthwest(),
	A_SetSpriteSequence(index=3, looping=False),
	A_UnknownCommand(bytearray([0xC7, 0x07])),
	A_Pause(48),
	A_CreatePacketAt7010WithEvent(packet=P028_MUSHROOM_THROWN_SOUTHWEST, event_id=E3068_EMPTY, destinations=["ACTION_439_reset_properties_50"]),
	A_ResetProperties(identifier="ACTION_439_reset_properties_50"),
	A_SetSequenceSpeed(NORMAL),
	A_Pause(128),
	A_SetWalkingSpeed(FAST),
	A_WalkToXYCoords(x=0, y=73),
	A_VisibilityOff(),
	A_ReturnQueue(),
	A_VisibilityOff(identifier="ACTION_439_visibility_off_57"),
	A_ObjectMemorySetBit(arg_1=0x30, bits=[4]),
	A_ReturnQueue()
])
