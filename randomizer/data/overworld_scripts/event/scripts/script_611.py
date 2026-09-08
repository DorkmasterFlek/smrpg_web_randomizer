# E0611_MARRYMORE_INN_LOBBY_LOADER
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
	FadeOutMusicToVolume(duration=1, volume=96),
	JmpIfBitSet(TEMP_704C_0, ["EVENT_611_action_queue_95"]),
	JmpIfBitSet(TEMP_7042_6, ["EVENT_611_jmp_if_bit_clear_26"]),
	JmpIfBitSet(TEMP_7042_5, ["EVENT_611_action_queue_22"]),
	JmpIfBitSet(TEMP_7042_0, ["EVENT_611_jmp_if_bit_set_14"]),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_611_run_event_as_subroutine_8"]),
	FadeInFromBlack(sync=False),
	Return(),
	RunEventAsSubroutine(E0081_MARIO_LANDS_SUBROUTINE, identifier="EVENT_611_run_event_as_subroutine_8"),
	RunEventAsSubroutine(E3588_SIGNAL_RING_ACTIVATOR),
	JmpIfBitClear(SIGNAL_RING_BIT, ["EVENT_611_jmp_if_bit_set_12"]),
	RunEventAsSubroutine(E3902_MARRYMORE_STAR_PIECE_SIGNAL),
	JmpIfBitSet(TEMP_7044_4, ["EVENT_611_jmp_if_bit_set_19"], identifier="EVENT_611_jmp_if_bit_set_12"),
	Return(),
	JmpIfBitSet(TEMP_7042_4, ["EVENT_611_jmp_if_bit_set_16"], identifier="EVENT_611_jmp_if_bit_set_14"),
	RemoveObjectFromCurrentLevel(NPC_5),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_611_run_event_as_subroutine_8"], identifier="EVENT_611_jmp_if_bit_set_16"),
	FadeInFromBlack(sync=False),
	Return(),
	JmpIfBitSet(EMPLOYMENT_704C_2, ["EVENT_256_ret_0"], identifier="EVENT_611_jmp_if_bit_set_19"),
	RunBackgroundEvent(event_id=E0623_MARRYMORE_INN_EMPLOYED_GUEST_LEAVES, return_on_level_exit=True),
	Return(),
	ActionQueueAsync(target=NPC_5, subscript=[
		A_TransferToXYZF(x=6, y=62, z=0, direction=EAST),
		A_FaceNortheast()
	], identifier="EVENT_611_action_queue_22"),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_611_run_event_as_subroutine_8"]),
	FadeInFromBlack(sync=False),
	Return(),
	JmpIfBitClear(TEMP_7042_5, ["EVENT_611_jmp_if_bit_clear_28"], identifier="EVENT_611_jmp_if_bit_clear_26"),
	ActionQueueAsync(target=NPC_1, subscript=[
		A_TransferToXYZF(x=6, y=62, z=0, direction=EAST),
		A_FaceNortheast()
	]),
	JmpIfBitClear(TEMP_704C_0, ["EVENT_611_jmp_if_bit_clear_30"], identifier="EVENT_611_jmp_if_bit_clear_28"),
	ActionQueueAsync(target=NPC_5, subscript=[
		A_TransferToXYZF(x=6, y=63, z=0, direction=EAST),
		A_FaceNorthwest()
	]),
	JmpIfBitClear(TEMP_7042_5, ["EVENT_611_jmp_if_bit_set_16"], identifier="EVENT_611_jmp_if_bit_clear_30"),
	FadeInFromBlack(sync=False),
	ActionQueueAsync(target=MARIO, subscript=[
		A_Walk1StepSouthwest()
	]),
	Pause(10),
	CopyVarToVar(from_var=TEMP_70AC, to_var=PRIMARY_TEMP_7000),
	Inc(PRIMARY_TEMP_7000),
	JmpIfBitSet(MARRYMORE_UNKNOWN_709F_6, ["EVENT_611_run_dialog_79"]),
	RunDialog(dialog_id=DI2509_100_COINS_FOR_EVERY_EXTRA_DAY, above_object=NPC_1, closable=True, sync=False, multiline=True, use_background=True),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=SECONDARY_TEMP_7024),
	Dec(SECONDARY_TEMP_7024),
	SetVarToConst(TEMP_7026, 0),
	SetObjectMemoryToVar(SECONDARY_TEMP_7024),
	StoreCoinCountTo7000(),
	CompareVarToConst(PRIMARY_TEMP_7000, 100),
	JmpIfComparisonResultIsLesser(["EVENT_611_set_bit_61"]),
	SetVarToConst(PRIMARY_TEMP_7000, 100),
	Dec7000FromCoins(),
	Inc(TEMP_7026),
	PlaySound(sound=SO013_COIN, channel=6),
	Pause(20),
	EndLoop(),
	ActionQueueSync(target=MARIO, subscript=[
		A_SetSpriteSequence(index=6, is_mold=True, is_sequence=True, looping=True),
		A_Pause(120),
		A_ResetProperties()
	]),
	CopyVarToVar(from_var=TEMP_7026, to_var=PRIMARY_TEMP_7000),
	RunDialog(dialog_id=DI1003_THEY_TOOK_ALL_COINS, above_object=BOWSER, closable=False, sync=True, multiline=True, use_background=False, bit_6=True),
	RememberLastObject(),
	SetBit(TEMP_7043_1),
	ClearBit(TEMP_7042_6),
	SetSyncActionScript(NPC_1, A0323_MARRYMORE_INNKEEPER_OVERSTAY_TAKE_COINS),
	SetSyncActionScript(NPC_5, A0891_MARRYMORE_BELLHOP_AFTER_PAYING_FOR_OVERSTAY),
	SetVarToConst(TEMP_70AC, 0),
	Return(),
	SetBit(TEMP_704C_0, identifier="EVENT_611_set_bit_61"),
	ClearBit(TEMP_7042_6),
	RunDialog(dialog_id=DI1001_YOURE_BROKE_NEED_TO_WORK_REMAINING, above_object=NPC_1, closable=True, sync=False, multiline=True, use_background=True),
	CopyVarToVar(from_var=SECONDARY_TEMP_7024, to_var=PRIMARY_TEMP_7000),
	DecVarFrom7000(TEMP_7026),
	CopyVarToVar(from_var=PRIMARY_TEMP_7000, to_var=TEMP_70AC),
	ActionQueueAsync(target=MARIO, subscript=[
		A_SetSpriteSequence(index=0, sprite_offset=3, is_sequence=True, looping=True)
	]),
	SetSyncActionScript(NPC_1, A0322_MARRYMORE_INNKEEPER_OVERSTAY_MAKES_YOU_WORK, identifier="EVENT_611_set_action_script_68"),
	FadeOutToBlack(sync=True, duration=90),
	PauseScriptUntilEffectDone(),
	EnterArea(room_id=R007_MARRYMORE_INN_1F, face_direction=SOUTHEAST, x=3, y=55, z=0),
	ActionQueueSync(target=MARIO, subscript=[
		A_ResetProperties(),
		A_SequenceLoopingOn(),
		A_SetSequenceSpeed(SLOW)
	]),
	ActionQueueSync(target=NPC_5, subscript=[
		A_TransferToXYZF(x=6, y=63, z=0, direction=EAST),
		A_FaceNorthwest()
	]),
	FadeInFromBlack(sync=True, duration=90),
	PauseScriptUntilEffectDone(),
	Pause(120),
	RunBackgroundEvent(event_id=E0617_MARIO_AS_BELLHOP_MAIN_EVENT, return_on_level_exit=True),
	Return(),
	RunDialog(dialog_id=DI2479_100_COINS_FOR_EVERY_EXTRA_DAY, above_object=NPC_1, closable=False, sync=False, multiline=True, use_background=True, identifier="EVENT_611_run_dialog_79"),
	RunDialog(dialog_id=DI2480_CANT_AFFORD_HOTEL_DEBT, above_object=NPC_1, closable=True, sync=False, multiline=True, use_background=True),
	StoreCoinCountTo7000(),
	Dec7000FromCoins(),
	StoreFrogCoinCountTo7000(),
	Dec7000FromFrogCoins(),
	PlaySound(sound=SO013_COIN, channel=6),
	Pause(60),
	PlaySound(sound=SO094_FROG_COIN, channel=6),
	Pause(60),
	RunDialog(dialog_id=DI2478_LOST_ALL_COINS_AND_FROG_COINS, above_object=BOWSER, closable=True, sync=False, multiline=True, use_background=False),
	SetBit(TEMP_704C_0),
	ClearBit(TEMP_7042_6),
	ActionQueueAsync(target=MARIO, subscript=[
		A_SetSpriteSequence(index=0, sprite_offset=3, is_sequence=True, looping=True)
	]),
	SetVarToConst(TEMP_70AC, 200),
	Jmp(["EVENT_611_set_action_script_68"]),
	ActionQueueSync(target=NPC_5, subscript=[
		A_TransferToXYZF(x=6, y=63, z=0, direction=EAST),
		A_FaceNorthwest()
	], identifier="EVENT_611_action_queue_95"),
	JmpIfBitSet(GUEST_DROPPED_OFF, ["EVENT_611_jmp_if_bit_set_107"]),
	CopyVarToVar(from_var=TEMP_70B8, to_var=PRIMARY_TEMP_7000),
	JmpIfVarEqualsConst(PRIMARY_TEMP_7000, 3, ["EVENT_611_action_queue_106"]),
	ActionQueueAsync(target=NPC_7, subscript=[
		A_TransferToXYZF(x=4, y=60, z=0, direction=EAST),
		A_FaceSoutheast()
	]),
	Jmp(["EVENT_611_jmp_if_bit_set_107"]),
	ActionQueueAsync(target=NPC_6, subscript=[
		A_TransferToXYZF(x=4, y=60, z=0, direction=EAST),
		A_FaceSoutheast()
	], identifier="EVENT_611_action_queue_106"),
	JmpIfBitSet(TEMP_7044_7, ["EVENT_611_run_event_as_subroutine_8"], identifier="EVENT_611_jmp_if_bit_set_107"),
	FadeInFromBlack(sync=False, identifier="EVENT_611_fade_in_from_black_async_108"),
	Return()
])
