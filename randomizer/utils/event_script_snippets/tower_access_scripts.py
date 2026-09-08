# Tower Access Event Scripts
# Converted from randomizer/data_old/eventscripts/utils/tower_access/
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
from randomizer.data.variables.overworld_sfx_names import *
from randomizer.data.variables.room_names import *
from randomizer.data.variables.variable_names import (
    BAMBINO_BOMB_UNKNOWN,
    TOWER_OPENED,
    TOWER_CHARACTER_RECRUITED,
    TEMP_7043_4,
)


# Mario opens tower as not main character
mario_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ClearSolidityBits(cant_pass_walls=True),
        A_WalkToXYCoords(x=4, y=114),
        A_FaceEast(),
        A_SetAllSpeeds(NORMAL),
    ]),
    SummonObjectToCurrentLevelAtMariosCoords(NPC_0),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_FixedFCoordOn(),
        A_Pause(30),
        A_Pause(15),
        A_SetSequenceSpeed(SLOW),
        A_SequenceLoopingOn(),
        A_Pause(15),
        A_SetSequenceSpeed(NORMAL),
        A_Pause(15),
        A_SetSequenceSpeed(FAST),
        A_Pause(15),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(45),
        A_SetWalkingSpeed(VERY_FAST),
        A_FixedFCoordOn(),
        A_WalkNortheastSteps(2),
        A_SequenceLoopingOff(),
        A_JumpToHeight(height=105),
        A_WalkNortheastSteps(2),
        A_FloatingOn(),
    ]),
    Pause(10),
    PlaySound(sound=SO066_KICK_BALL_SHELL, channel=6),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_FloatingOff(),
        A_JumpToHeight(height=30, silent=True),
        A_WalkSouthwestSteps(1),
        A_SetWalkingSpeed(FAST),
        A_WalkSouthwestSteps(1),
        A_SetWalkingSpeed(NORMAL),
        A_WalkSouthwestPixels(16),
        A_FixedFCoordOff(),
    ]),
    Pause(60),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetSequenceSpeed(NORMAL),
        A_SetSpriteSequence(index=10, sprite_offset=2, is_sequence=True, looping=False),
        A_Pause(80),
        A_ResetProperties(),
        A_FaceSouthwest(),
    ]),
    Pause(10),
    ActionQueueSync(target=MARIO, subscript=[
        A_WalkToXYCoords(x=5, y=116),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetWalkingSpeed(NORMAL),
        A_SetSequenceSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=116),
        A_VisibilityOff(),
    ]),
    RemoveObjectFromCurrentLevel(NPC_0),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Mario opens tower as main character
mario_self_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_FixedFCoordOn(),
        A_Pause(30),
        A_Pause(15),
        A_SetSequenceSpeed(SLOW),
        A_SequenceLoopingOn(),
        A_Pause(15),
        A_SetSequenceSpeed(NORMAL),
        A_Pause(15),
        A_SetSequenceSpeed(FAST),
        A_Pause(15),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(45),
        A_SetWalkingSpeed(VERY_FAST),
        A_FixedFCoordOn(),
        A_WalkNortheastSteps(2),
        A_SequenceLoopingOff(),
        A_JumpToHeight(height=105),
        A_WalkNortheastSteps(2),
        A_FloatingOn(),
    ]),
    Pause(10),
    PlaySound(sound=SO066_KICK_BALL_SHELL, channel=6),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    ActionQueueAsync(target=MARIO, subscript=[
        A_FloatingOff(),
        A_JumpToHeight(height=30, silent=True),
        A_WalkSouthwestSteps(1),
        A_SetWalkingSpeed(FAST),
        A_WalkSouthwestSteps(1),
        A_SetWalkingSpeed(NORMAL),
        A_WalkSouthwestPixels(16),
        A_FixedFCoordOff(),
    ]),
    Pause(60),
    ActionQueueAsync(target=MARIO, subscript=[
        A_FixedFCoordOff(),
        A_SetAllSpeeds(NORMAL),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetSpriteSequence(index=10, sprite_offset=2, is_sequence=True, looping=False),
        A_Pause(80),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Geno opens tower as not main character
geno_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueSync(target=NPC_3, subscript=[
        A_WalkNorthPixels(7),
        A_WalkWestPixels(6),
    ]),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ClearSolidityBits(cant_pass_walls=True),
        A_WalkToXYCoords(x=4, y=114),
        A_FaceEast(),
        A_SetAllSpeeds(NORMAL),
    ]),
    Pause(25),
    SummonObjectToCurrentLevelAtMariosCoords(NPC_0),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_SetSpriteSequence(index=2, sprite_offset=3, is_sequence=True, looping=False),
        A_Pause(34)
    ]),
    ActionQueueAsync(target=NPC_3, subscript=[
        A_VisibilityOn(),
        A_SetSpriteSequence(index=0, is_sequence=True, looping=True),
        A_SequenceLoopingOn(),
        A_SetSequenceSpeed(VERY_FAST),
        A_SetWalkingSpeed(VERY_FAST),
        A_WalkNortheastSteps(2),
        A_PlaySound(sound=SO075_ROCKETING_BLAST, channel=6),
        A_WalkNortheastSteps(4),
    ]),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    RemoveObjectFromCurrentLevel(NPC_3),
    Pause(60),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetSequenceSpeed(NORMAL),
        A_SetSpriteSequence(index=10, sprite_offset=1, is_sequence=True, looping=False),
        A_Pause(80),
        A_ResetProperties(),
        A_FaceSouthwest(),
    ]),
    Pause(10),
    ActionQueueAsync(target=MARIO, subscript=[
        A_WalkToXYCoords(x=5, y=116),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_WalkToXYCoords(x=5, y=116),
    ]),
    RemoveObjectFromCurrentLevel(NPC_0),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Geno opens tower by himself (when Geno is the sole character or starts)
geno_self_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),

    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueSync(target=NPC_3, subscript=[
        A_WalkNorthPixels(7),
        A_WalkWestPixels(6),
    ]),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_SetSpriteSequence(index=2, sprite_offset=4, is_sequence=True, looping=False),
        A_Pause(34)
    ]),
    ActionQueueAsync(target=NPC_3, subscript=[
        A_VisibilityOn(),
        A_SetSpriteSequence(index=0, is_sequence=True, looping=True),
        A_SequenceLoopingOn(),
        A_SetSequenceSpeed(VERY_FAST),
        A_SetWalkingSpeed(VERY_FAST),
        A_WalkNortheastSteps(2),
        A_PlaySound(sound=SO075_ROCKETING_BLAST, channel=6),
        A_WalkNortheastSteps(4),
    ]),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    RemoveObjectFromCurrentLevel(NPC_3),
    Pause(60),
    ActionQueueAsync(target=MARIO, subscript=[
        A_FixedFCoordOff(),
        A_SetAllSpeeds(NORMAL),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetSpriteSequence(index=10, sprite_offset=2, is_sequence=True, looping=False),
        A_Pause(80),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    Pause(10),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Bowser opens tower when Mario is the one who triggers the door
bowser_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ClearSolidityBits(cant_pass_walls=True),
        A_WalkToXYCoords(x=4, y=114),
        A_FaceEast(),
        A_SetAllSpeeds(NORMAL),
    ]),
    Pause(25),
    SummonObjectToCurrentLevelAtMariosCoords(NPC_0),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(15),
        A_FaceSouthwest(),
        A_Pause(15),
        A_SetSequenceSpeed(SLOW),
        A_SequenceLoopingOn(),
        A_Pause(15),
        A_SetSequenceSpeed(NORMAL),
        A_Pause(15),
        A_SetSequenceSpeed(FAST),
        A_Pause(15),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(45),
        A_SetWalkingSpeed(VERY_FAST),
        A_FixedFCoordOn(),
        A_WalkNortheastSteps(3),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SequenceLoopingOff(),
        A_SequencePlaybackOff(),
        A_SetWalkingSpeed(VERY_FAST),
        A_WalkNortheastPixels(18),
        A_WalkSouthwestPixels(12),
        A_WalkNortheastPixels(8),
        A_WalkSouthwestPixels(6),
        A_WalkNortheastPixels(4),
        A_WalkSouthwestPixels(4),
    ]),
    Pause(5),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    PlaySound(sound=SO021_RUMBLING, channel=6),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    Pause(60),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetSequenceSpeed(NORMAL),
        A_SetSpriteSequence(index=10, sprite_offset=1, is_sequence=True, looping=False),
        A_Pause(60),
        A_ResetProperties(),
        A_FaceSouthwest(),
    ]),
    ActionQueueSync(target=MARIO, subscript=[
        A_WalkToXYCoords(x=5, y=116),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_FixedFCoordOff(),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetWalkingSpeed(NORMAL),
        A_SetSequenceSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=116),
        A_VisibilityOff(),
    ]),
    RemoveObjectFromCurrentLevel(NPC_0),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Bowser opens tower by himself (when Bowser is the sole character or starts)
bowser_self_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(15),
        A_FaceSouthwest(),
        A_Pause(15),
        A_SetSequenceSpeed(SLOW),
        A_SequenceLoopingOn(),
        A_Pause(15),
        A_SetSequenceSpeed(NORMAL),
        A_Pause(15),
        A_SetSequenceSpeed(FAST),
        A_Pause(15),
        A_SetSequenceSpeed(VERY_FAST),
        A_Pause(45),
        A_SetWalkingSpeed(VERY_FAST),
        A_FixedFCoordOn(),
        A_WalkNortheastSteps(3),
    ]),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SequenceLoopingOff(),
        A_SequencePlaybackOff(),
        A_SetWalkingSpeed(VERY_FAST),
        A_WalkNortheastPixels(18),
        A_WalkSouthwestPixels(12),
        A_WalkNortheastPixels(8),
        A_WalkSouthwestPixels(6),
        A_WalkNortheastPixels(4),
        A_WalkSouthwestPixels(4),
    ]),
    Pause(5),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    PlaySound(sound=SO021_RUMBLING, channel=6),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    Pause(60),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetSequenceSpeed(NORMAL),
        A_FixedFCoordOff(),
        A_SetAllSpeeds(NORMAL),
        A_SetSpriteSequence(index=10, sprite_offset=2, is_sequence=True, looping=False),
        A_Pause(60),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Mallow opens tower when Mario is the one who triggers the door
mallow_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ClearSolidityBits(cant_pass_walls=True),
        A_WalkToXYCoords(x=4, y=114),
        A_FaceEast(),
        A_SetAllSpeeds(NORMAL),
    ]),
    Pause(25),
    SummonObjectToCurrentLevelAtMariosCoords(NPC_0),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_Pause(30),
        A_SetSpriteSequence(index=12, is_sequence=True, mirror_sprite=True, looping=True),
        A_FaceNortheast(),
        A_PlaySound(sound=SO068_MALLOW_YELLING_AT_CROCO, channel=4),
        A_Pause(60),
        A_SetWalkingSpeed(FAST),
        A_SequenceLoopingOn(),
        A_WalkNortheastSteps(4),
        A_Pause(90),
        A_StopSound(),
        A_SequenceLoopingOff(),
        A_SetSpriteSequence(index=28, is_mold=True, is_sequence=True, mirror_sprite=True),
    ]),
    Pause(10),
    PlaySound(sound=SO016_OPEN_DOOR, channel=6),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_Pause(90),
        A_ResetProperties(),
        A_FaceSouthwest(),
        A_Pause(90),
        A_SetSpriteSequence(index=7,  is_mold=True, is_sequence=True),
        A_Pause(30),
        A_ResetProperties(),
    ]),
    Pause(10),
    ActionQueueSync(target=MARIO, subscript=[
        A_WalkToXYCoords(x=5, y=116),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetWalkingSpeed(NORMAL),
        A_SetSequenceSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=116),
        A_VisibilityOff(),
    ]),
    RemoveObjectFromCurrentLevel(NPC_0),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Mallow opens tower by himself (when Mallow is the sole character or starts)
mallow_self_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_Pause(30),
        A_SetSpriteSequence(index=8, sprite_offset=5, is_sequence=True, mirror_sprite=True, looping=True),
        A_FaceNortheast(),
        A_PlaySound(sound=SO068_MALLOW_YELLING_AT_CROCO, channel=4),
        A_Pause(60),
        A_SetWalkingSpeed(FAST),
        A_SequenceLoopingOn(),
        A_WalkNortheastSteps(4),
        A_Pause(90),
        A_StopSound(),
        A_SequenceLoopingOff(),
        A_SetSpriteSequence(index=30, sprite_offset=5, is_mold=True, is_sequence=True, mirror_sprite=True),
    ]),
    Pause(10),
    PlaySound(sound=SO016_OPEN_DOOR, channel=6),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    ActionQueueAsync(target=MARIO, subscript=[
        A_Pause(90),
        A_FixedFCoordOff(),
        A_SetAllSpeeds(NORMAL),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_FaceNorthwest(),
        A_Pause(10),
        A_SetSpriteSequence(index=7, mirror_sprite=True, is_mold=True, is_sequence=True),
        A_Pause(60),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
        A_SetWalkingSpeed(NORMAL),
    ]),
    Pause(10),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Toadstool opens tower when Mario is the one who triggers the door
toadstool_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ClearSolidityBits(cant_pass_walls=True),
        A_WalkToXYCoords(x=4, y=114),
        A_FaceEast(),
        A_SetAllSpeeds(NORMAL),
    ]),
    Pause(25),
    SummonObjectToCurrentLevelAtMariosCoords(NPC_0),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_Pause(30),
        A_WalkNortheastSteps(4),
        A_Pause(20),
        A_SetSpriteSequence(index=12, sprite_offset=1, is_sequence=True),
        A_Pause(15),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_Pause(15),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_Pause(10),
        A_FixedFCoordOn(),
        A_SetBit(TEMP_7043_4),
        A_WalkSouthwestSteps(2),
        A_FixedFCoordOff(),
    ]),
    Pause(200),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
	SetBit(BAMBINO_BOMB_UNKNOWN),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_ResetProperties(),
        A_FaceSouthwest(),
        A_Pause(40),
        A_SetSpriteSequence(index=2, is_sequence=True),
        A_Pause(40),
        A_SetSequenceSpeed(NORMAL),
        A_ResetProperties(),
    ]),
    Pause(10),
	ClearBit(BAMBINO_BOMB_UNKNOWN),
    ActionQueueSync(target=MARIO, subscript=[
        A_WalkToXYCoords(x=5, y=116),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    ActionQueueAsync(target=NPC_0, subscript=[
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_SetWalkingSpeed(NORMAL),
        A_SetSequenceSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=116),
        A_VisibilityOff(),
    ]),
    RemoveObjectFromCurrentLevel(NPC_0),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])


# Toadstool opens tower by herself (when Toadstool is the sole character or starts)
toadstool_self_script = EventScript([
    # Tower's already been opened
    JmpIfBitSet(TOWER_OPENED, ["tower_ret"]),
    # Don't have the right character yet
    JmpIfBitClear(TOWER_CHARACTER_RECRUITED, ["tower_ret"]),
    # Do have the right character
    EnableControlsUntilReturn([]),
    RemoveObjectFromCurrentLevel(NPC_1),
    ActionQueueAsync(target=MARIO, subscript=[
        A_SetWalkingSpeed(NORMAL),
        A_WalkToXYCoords(x=5, y=115),
        A_FaceNortheast(),
        A_Pause(30),
        A_WalkNortheastSteps(4),
        A_Pause(20),
        A_SetSpriteSequence(index=12, sprite_offset=2, is_sequence=True),
        A_Pause(15),
    ]),
    ActionQueueAsync(target=MARIO, subscript=[
        A_Pause(15),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_Pause(10),
        A_FixedFCoordOn(),
        A_SetBit(TEMP_7043_4),
        A_WalkSouthwestSteps(2),
        A_FixedFCoordOff(),
    ]),
    ApplySolidityModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=0, permanent=True),
    ApplyTileModToLevel(room_id=R202_BOOSTER_TOWER_ENTRANCE, mod_id=32, use_alternate=True),
    RemoveObjectFromCurrentLevel(NPC_2),
    RemoveObjectFromSpecificLevel(NPC_2, R202_BOOSTER_TOWER_ENTRANCE),
    Pause(200),
	SetBit(BAMBINO_BOMB_UNKNOWN),
    ActionQueueAsync(target=MARIO, subscript=[
        A_ResetProperties(),
        A_FixedFCoordOff(),
        A_SetAllSpeeds(NORMAL),
        A_SequenceLoopingOn(),
        A_SequencePlaybackOn(),
        A_FaceSouthwest(),
        A_Pause(40),
        A_SetSpriteSequence(index=5, sprite_offset=5, is_sequence=True),
        A_Pause(40),
        A_SetSequenceSpeed(NORMAL),
        A_ResetProperties(),
        A_FaceNortheast(),
        A_SetSolidityBits(cant_pass_walls=True),
    ]),
    SetBit(TOWER_OPENED),
    Return(identifier="tower_ret"),
])
