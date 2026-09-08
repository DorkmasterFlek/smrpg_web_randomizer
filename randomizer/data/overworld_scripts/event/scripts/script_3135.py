# E3135_SEWERS_GENERIC_LOADER
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
	Set7000ToCurrentLevel(),
    
    JmpIfVarNotEqualsConst(PRIMARY_TEMP_7000, R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS, ["EVENT_3135_jmp_if_bit_set_711"]),
    JmpIfBitClear(LANDS_END_GROTTO_BARREL_FLIPPED, ["kero_room_loader_check_save_bit"]),
	JmpIfObjectTriggerEnabledInSpecificLevel(
		NPC_1,
		R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS,
		["kero_room_loader_check_save_bit"],
	),
    RemoveObjectFromCurrentLevel(NPC_1),
	SummonObjectToCurrentLevel(NPC_8),
    
	
	JmpIfObjectTriggerDisabledInSpecificLevel(
		NPC_8,
		R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS,
		["EVENT_3135_jmp_if_bit_set_711"],
	),
    
    ResumeActionScript(NPC_8),
    
    
	
    JmpIfVarNotEqualsConst(PRIMARY_TEMP_7000, R333_KERO_SEWERS_ENTRANCE, ["event_3135_init"], identifier="EVENT_3135_jmp_if_bit_set_711"),
	ActionQueueAsync(target=NPC_1, subscript=[
		A_WalkEastPixels(11),
		A_WalkNortheastPixels(4),
		A_SetSpriteSequence(index=1, is_sequence=True, looping=True),
		A_SetVRAMPriority(NORMAL_PRIORITY)
	], identifier="event_3135_id_check_2"),
    
	ClearBit(TEMP_707C_5, "event_3135_init"),
	SetVarToConst(TIMER_701C, 300),
	StopBackgroundEvent(TIMER_701C),
	JmpIfVarEqualsConst(CURRENT_OVERWORLD_MARKER_ID, OW14_KERO_SEWERS, ["EVENT_3135_jmp_if_bit_set_7"]),
    SetBit(SIGNAL_RING_DIRECTIONAL_BIT),
	JmpToSubroutine(["EVENT_3134_summon_to_level_0"]),
	SetVarToConst(CURRENT_OVERWORLD_MARKER_ID, OW14_KERO_SEWERS),
	Jmp(["EVENT_3135_jmp_if_bit_clear_9"]),
	JmpIfBitSet(TEMP_7042_0, ["EVENT_3135_jmp_if_bit_clear_9"], identifier="EVENT_3135_jmp_if_bit_set_7"),
	JmpToSubroutine(["EVENT_3134_summon_to_level_0"]),
	JmpIfBitClear(SEWER_WATER_LEVEL, ["EVENT_3135_reset_priority_set_14"], identifier="EVENT_3135_jmp_if_bit_clear_9"),
	Set7000ToCurrentLevel(),
	JmpIfVarEqualsConst(PRIMARY_TEMP_7000, R062_KERO_SEWERS_AREA_01_WATER_ROOM_WSAVE, ["kero_room_loader_check_save_bit"]),
	PrioritySet(mainscreen=[LAYER_L1, LAYER_L2, NPC_SPRITES], subscreen=[], colour_math=[]),
	Jmp(["kero_room_loader_check_save_bit"]),
	ResetPrioritySet(identifier="EVENT_3135_reset_priority_set_14"),
    



	JmpIfBitClear(TEMP_7044_7, ["EVENT_3135_fade"], identifier="kero_room_loader_check_save_bit"),
    
    Set7000ToCurrentLevel(),
	JmpIfVarEqualsConst(PRIMARY_TEMP_7000, R333_KERO_SEWERS_ENTRANCE, ["EVENT_3135_jmp_if_bit_set_71"]),
    JmpIfVarEqualsConst(PRIMARY_TEMP_7000, R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS, ["EVENT_3135_jmp_if_bit_set_71"]),
    JmpIfVarEqualsConst(PRIMARY_TEMP_7000, R062_KERO_SEWERS_AREA_01_WATER_ROOM_WSAVE, ["EVENT_3135_jmp_if_bit_set_71"]),
    Jmp(["EVENT_3135_fade"]),
    SetBit(SIGNAL_RING_DIRECTIONAL_BIT, identifier="EVENT_3135_jmp_if_bit_set_71"),
	RunEventAsSubroutine(E0015_STANDARD_ROOM_LOADER, identifier="EVENT_3135_fade"),
	JmpIfBitClear(SIGNAL_RING_DIRECTIONAL_BIT, ["EVENT_3135_ret_22"], identifier="kero_Sewer_signal_ring_path"),
    ClearBit(SIGNAL_RING_DIRECTIONAL_BIT),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_3135_ret_22"]),
	RunEventAsSubroutine(E3891_SEWERS_STAR_PIECE_SIGNAL),
	Return(identifier="EVENT_3135_ret_22"),
])
