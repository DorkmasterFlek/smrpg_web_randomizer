from typing import Sequence

from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import (
    SOUTHEAST,
    SOUTHWEST,
    NORTHEAST,
    NORTHWEST,
)
from ...types.physical_objects import (
    BossNPC,
    PixelShift,
    SpriteAnimation,
    SpriteAnimationCollection,
    StatueNPC,
)
from ..rooms.npcs import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.arguments.sequence_speeds import (
    FAST,
    VERY_FAST,
    FASTER,
    FASTEST,
)
from copy import deepcopy

# Object is too high up: increase eye_height
# Object is too low: decrease eye_height


class HammerBroLargeObject(BossNPC):
    """Hammer Bro object"""

    _base = HAMMER_BRO_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 5
    _kitchen_prep = 4
    _ship_beckon = 5
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class HammerBroSmallObject(BossNPC):
    """Small Hammer Bro object"""

    _base = HAMMER_BRO_SMALL_NPC
    _eye_height = 16
    _evil_palette = [
        0x393939,
        0xA5A5AD,
        0x736B7B,
        0xFFFFFF,
        0x000010,
        0xF8A8A8,
        0xF88888,
        0xC80808,
        0xD00808,
        0xF05858,
        0xC00808,
        0xE80808,
        0x580000,
        0x280000,
        0x100000,
    ]


class HammerBroStatueObject(StatueNPC):
    """Hammer Bro statue object"""

    _base = HAMMER_BRO_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-8, 1),
    }


class Croco1Object(BossNPC):
    """Croco 1 object"""

    _base = CROCO_1_NPC
    _eye_height = 16
    _evil_palette = [
        0xBDD6CE,
        0x8CC694,
        0xF86868,
        0xFFFFFF,
        0x7B8484,
        0xF85050,
        0xF80808,
        0xC00000,
        0xE80000,
        0xD80000,
        0xB00000,
        0x800000,
        0x700000,
        0x580000,
        0x181818,
    ]
    _tower_entrance_horizontal_shift = 9
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 6
    _dojo_challenge = 6
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 6
    _keep_summon = 6
    _chandelier_challenge = 6
    _factory_pierce = 4
    _endgame_challenge = 6


class Croco2Object(BossNPC):
    """Croco 2 object"""

    _base = CROCO_2_NPC
    _eye_height = 16
    _evil_palette = [
        0xBDD6CE,
        0x8CC694,
        0xF86868,
        0xFFFFFF,
        0x7B8484,
        0xF85050,
        0xF80808,
        0xC00000,
        0xE80000,
        0xD80000,
        0xB00000,
        0x800000,
        0x700000,
        0x580000,
        0x181818,
    ]
    _tower_entrance_horizontal_shift = 9
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 6
    _dojo_challenge = 6
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 6
    _keep_summon = 6
    _chandelier_challenge = 6
    _factory_pierce = 4
    _endgame_challenge = 6


class CrocoStatueObject(StatueNPC):
    """Croco statue object"""

    _base = CROCO_STATUE_NPC
    _facing_shifts = {
        NORTHWEST: PixelShift(-2, 3),
        SOUTHEAST: PixelShift(-3, 3),
        NORTHEAST: PixelShift(-8, 3)
    }


class MackSmallObject(BossNPC):
    """Small Mack object"""

    _base = MACK_SMALL_NPC
    _eye_height = 20
    _tower_entrance_horizontal_shift = -3
    _evil_palette = [
        0x383838,
        0x181818,
        0x282838,
        0x787878,
        0x202020,
        0xB0B8A8,
        0x181818,
        0xF8F8F8,
        0x504040,
        0x000000,
        0x706878,
        0xE8E8E8,
        0xE82020,
        0xF8F8F8,
        0xE01010,
    ]


class MackMediumObject(BossNPC):
    """Medium Mack object"""

    _base = MACK_MEDIUM_NPC


class MackBattleObject(BossNPC):
    """Battle Mack object"""

    _base = MACK_NPC
    _recoil = 2
    _tower_crying = 3
    _bandits_way_distracted = 0
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 4
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 4
    _endgame_challenge = 4
    _look_at_ceiling_mold_id = 5
    _look_at_ceiling = 8


class MackStatueObject(StatueNPC):
    """Mack statue object"""

    _base = MACK_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-3, 0),
    }


class PandoriteSmallObject(BossNPC):
    """Small Pandorite object"""

    _base = PANDORITE_SMALL_NPC
    _evil_palette = [
        0xFFF7DE,
        0xFFFF63,
        0xFFEF63,
        0x00FFAD,
        0xFFEF00,
        0xFFE7B5,
        0xF7BD8C,
        0xE7A531,
        0xF80000,
        0xC00000,
        0xEF0000,
        0xA00000,
        0x089400,
        0x085A00,
        0x680000,
    ]
    _eye_height = 5
    _crown_height = 1


class PandoriteLargeObject(BossNPC):
    """Large Pandorite object"""

    _base = PANDORITE_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 3
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class MimicStatueObject(StatueNPC):
    """Mimic statue object"""

    _base = MIMIC_STATUEL_NPC
    _eye_height = 4
    _crown_height = 1


class Belome1SmallObject(BossNPC):
    """Small Belome 1 object"""

    _tower_entrance_horizontal_shift = 3
    _eye_height = 12
    _evil_palette = [
        0xF84848,
        0xE00000,
        0xF8A8A8,
        0x680000,
        0xFFFFFF,
        0x181818,
        0xFFB510,
        0x280000,
        0xFFD608,
        0xFFFFB5,
        0x5A2100,
        0xCE8408,
        0xFFD663,
        0xF03030,
        0x210000,
    ]

    _base = BELOME_SMALL_NPC


class Belome1LargeObject(BossNPC):
    """Large Belome 1 object"""

    _base = BELOME_ST_TIME_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF8A8A8,
        0xFFD663,
        0xF84848,
        0xFFB510,
        0xFFFFB5,
        0xFFD608,
        0xE00000,
        0xCE8408,
        0x5A2100,
        0xF03030,
        0x680000,
        0x280000,
        0x210000,
        0x181818,
    ]
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 4
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class Belome2SmallObject(BossNPC):
    """Small Belome 2 object"""

    _base = BELOME_2_SMALL_NPC
    _tower_entrance_horizontal_shift = 3
    _eye_height = 12
    _evil_palette = [
        0xF84848,
        0xE00000,
        0xF8A8A8,
        0x680000,
        0xFFFFFF,
        0x181818,
        0xFFB510,
        0x280000,
        0xFFD608,
        0xFFFFB5,
        0x5A2100,
        0xCE8408,
        0xFFD663,
        0xF03030,
        0x210000,
    ]


class Belome2LargeObject(BossNPC):
    """Large Belome 2 object"""

    _base = GOLDEN_BELOME_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF8A8A8,
        0xFFD663,
        0xF84848,
        0xFFB510,
        0xFFFFB5,
        0xF84848,
        0xE00000,
        0xCE8408,
        0xF03030,
        0xF03030,
        0x680000,
        0x280000,
        0xCE8408,
        0x210000,
    ]
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 4
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class Belome3SmallObject(BossNPC):
    """Small Belome 3 object"""

    _base = BELOME_3_SMALL_NPC
    _tower_entrance_horizontal_shift = 3
    _eye_height = 12
    _evil_palette = [
        0xF84848,
        0xE00000,
        0xF8A8A8,
        0x680000,
        0xFFFFFF,
        0x181818,
        0xFFB510,
        0x280000,
        0xFFD608,
        0xFFFFB5,
        0x5A2100,
        0xCE8408,
        0xFFD663,
        0xF03030,
        0x210000,
    ]


class Belome3LargeObject(BossNPC):
    """Large Belome 3 object"""

    _base = BELOME_3_LARGE_2_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF8A8A8,
        0xF84848,
        0xFFB510,
        0xF84848,
        0xFFFFB5,
        0xFFFFB5,
        0xE00000,
        0xCE8408,
        0x5A2100,
        0xCE8408,
        0x680000,
        0x280000,
        0x210000,
        0x280000,
    ]
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 4
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class BelomeSmallStatueObject(StatueNPC):
    """Small Belome statue object"""

    _facing_shifts = {
        SOUTHWEST: PixelShift(-4, 0),
    }

    _base = BELOME_SMALL_STATUE
    _evil_palette = [
        0xF84848,
        0xFFD608,
        0xF8A8A8,
        0x5A2100,
        0xFFFFFF,
        0x181818,
        0xF84848,
        0x280000,
        0xF84848,
        0xF8A8A8,
        0x5A2100,
        0xE00000,
        0xF84848,
        0x5A2100,
        0x210000,
    ]


class BowyerSmallObject(BossNPC):
    """Small Bowyer object"""

    _base = BOWYER_SMALL_NPC
    _eye_height = 19
    _evil_palette = [
        0x303030,
        0x181818,
        0x101010,
        0x000000,
        0x000018,
        0xA00000,
        0xF80000,
        0x401010,
        0xFFFFFF,
        0xBDBDCE,
        0x7B1842,
        0x6B7363,
        0xFF73E7,
        0xF80000,
        0xA80000,
    ]


class BowyerStatueObject(StatueNPC):
    """Bowyer statue object"""

    _base = BOWYER_STATUE_NPC


class BowyerLargeObject(BossNPC):
    """Large Bowyer object"""

    _base = BOWYER_NPC_BATTLE

    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


# Punchinello
class PunchinelloSmallObject(BossNPC):
    """Small Punchinello object."""

    _base = PUNCHINELLO_SMALL_NPC
    _eye_height = 16
    _evil_palette = [
        0x181818,
        0x101010,
        0x000000,
        0xA81818,
        0xF80000,
        0x480000,
        0x580000,
        0x808068,
        0xFFFFFF,
        0xD0D8C0,
        0xB5B58C,
        0xF7EF63,
        0x9C6300,
        0x303030,
        0x000000,
    ]


class PunchinelloLargeObject(BossNPC):
    """Large Punchinello object."""

    _base = PUNCHINELLO_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF7EF63,
        0xD0D8C0,
        0xB5B58C,
        0x808068,
        0xF80000,
        0x9C6300,
        0x303030,
        0x480000,
        0x480000,
        0x181818,
        0xA81818,
        0x101010,
        0x580000,
        0x000000,
    ]
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 5
    _statue_intro = 5
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class Punchinello2LargeObject(BossNPC):
    """Large Punchinello object."""

    _base = PUNCHINELLO_POSTGAME_2_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF7EF63,
        0xD0D8C0,
        0xB5B58C,
        0x808068,
        0xF80000,
        0x9C6300,
        0x303030,
        0x480000,
        0x480000,
        0x181818,
        0xA81818,
        0x101010,
        0x580000,
        0x000000,
    ]
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 5
    _statue_intro = 5
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


# Dodo
class DodoSmallObject(BossNPC):
    """Small Dodo object."""

    _base = DODO_SMALL_NPC
    _eye_height = 14
    _evil_palette = [
        0x181818,
        0xF8F828,
        0x4A524A,
        0xC8A008,
        0x883800,
        0x8C8C8C,
        0xE7DEDE,
        0xFFFFFF,
        0x737373,
        0xADADAD,
        0x292910,
        0xE00808,
        0x800008,
        0xFFFFFF,
        0x480000,
    ]


class DodoLargeObject(BossNPC):
    """Large Dodo object."""

    _base = DODO_NPC
    _recoil = 2
    _tower_crying = 6
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 6
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 4
    _keep_challenge = 4
    _keep_summon = 3
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4
    _look_at_ceiling_mold_id = 25
    _look_at_ceiling = 5
    _look_at_camera = 5


# Birdetta
class BirdettaSmallObject(BossNPC):
    """Small Birdetta object."""

    _base = BIRDETTA_SMALL_NPC
    _eye_height = 18
    _tower_entrance_horizontal_shift = 3
    _evil_palette = [
        0xA85818,
        0xF87820,
        0x002000,
        0x005000,
        0x007038,
        0x000000,
        0x00F8C8,
        0x181818,
        0x00D058,
        0x00F858,
        0xF8F8F8,
        0x00A048,
        0x909090,
        0x484848,
        0x806060,
    ]


class BirdettaLargeObject(BossNPC):
    """Large Birdetta object."""

    _base = BIRDETTA_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


# Czar Dragon
class CzarDragonSmallObject(BossNPC):
    """Small Czar Dragon object."""

    _base = CZAR_DRAGON_SMALL_NPC
    _eye_height = 16
    _tower_entrance_horizontal_shift = 5
    _evil_palette = [
        0xF0F8F8,
        0x00B0B8,
        0x88F8F8,
        0x002828,
        0x08C8C8,
        0x007070,
        0x40F0F0,
        0x009090,
        0x003838,
        0x08C8C8,
        0x002828,
        0x003030,
        0x009090,
        0x006868,
        0x003838,
    ]


class CzarDragonMediumObject(BossNPC):
    """Medium Czar Dragon object."""

    _base = CZAR_DRAGON_BODY_NPC


class CzarDragonLargeObject(BossNPC):
    """Large Czar Dragon object."""

    _base = CZAR_DRAGON_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


# Boomer
class BoomerSmallObject(BossNPC):
    """Small Boomer object."""

    _base = BOOMER_SMALL_NPC
    _evil_palette = [
        0x000078,
        0x423131,
        0x1000BD,
        0x9C8C8C,
        0x000021,
        0x100808,
        0x6B636B,
        0x4284CE,
        0x212121,
        0x635A39,
        0x2929F7,
        0xEFC6C6,
        0xFFFFFF,
        0x000000,
        0x000000,
    ]


class BoomerLargeObject(BossNPC):
    """Large Boomer object."""

    _base = BOOMER_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


# Exor
class ExorSmallObject(BossNPC):
    """Small Exor object."""

    _base = EXOR_SMALL_NPC
    _evil_palette = [
        0xF8C0C0,
        0xF86868,
        0xC00000,
        0xF80000,
        0xD80000,
        0x000000,
        0xB80000,
        0xF80000,
        0xF85050,
        0xC00000,
        0x980000,
        0x480000,
        0xF88080,
        0xB00000,
        0xD00000,
    ]
    _eye_height = 8


# Domino
class DominoSmallObject(BossNPC):
    """Small Domino object."""

    _base = DOMINO_SMALL_NPC
    _eye_height = 12
    _evil_palette = [
        0xF7E710,
        0x52FFBD,
        0x9C734A,
        0xFFFF94,
        0xFFFFDE,
        0x089431,
        0x001000,
        0xC80808,
        0xA00808,
        0xE80808,
        0x680000,
        0xC80808,
        0xF02828,
        0x392908,
        0x181818,
    ]


# Cloaker
class CloakerLargeObject(BossNPC):
    """Large Cloaker object."""

    _base = CLOAKER_ST_TIME_NPC
    _recoil = 2
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 4
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 4
    _endgame_challenge = 3


# Smithy
class SmithySmallObject(BossNPC):
    """Small Smithy object."""

    _base = SMITHY_SMALL_NPC
    _eye_height = 11
    _tower_entrance_horizontal_shift = -2
    _evil_palette = [
        0x080000,
        0x7B848C,
        0xF80000,
        0x391008,
        0x212121,
        0x6B6B63,
        0xA80000,
        0x525A6B,
        0xFFFFFF,
        0xBDBDAD,
        0xA81010,
        0xCEEFFF,
        0x4A4A42,
        0x000000,
        0x000000,
    ]


class SmithyLargeObject(BossNPC):
    """Large Smithy object."""

    _base = SMITHY_LOWER_NPC
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_peck = 3
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


# Culex
class CulexSmallObject(BossNPC):
    """Small Culex object."""

    _base = CULEX_SMALL_NPC
    _eye_height = 13
    _evil_palette = [
        0x180808,
        0x585858,
        0x383838,
        0x101010,
        0xC69C4A,
        0xFFD66B,
        0x000000,
        0x9C2918,
        0x522110,
        0xBD6329,
        0xF81818,
        0x380000,
        0xA80000,
        0x780000,
        0xF8A8A8,
    ]


class CulexLargeObject(BossNPC):
    """Large Culex object."""

    _base = CULEX_NPC
    _evil_palette = [
        0x180808,
        0x585858,
        0x383838,
        0x101010,
        0xC69C4A,
        0xFFD66B,
        0x000000,
        0x9C2918,
        0x522110,
        0xBD6329,
        0xF81818,
        0x380000,
        0xA80000,
        0x780000,
        0xF8A8A8,
    ]
    _recoil = 2
    _tower_crying = 2
    _bandits_way_distracted = 2
    _chapel_laugh = 2
    _statue_intro = 2
    _statue_flustered = 2


# Bundt
class BundtSmallObject(BossNPC):
    """Small Bundt object."""

    _base = BUNDT_OBJECT_NPC
    _eye_height = 13
    _evil_palette = [
        0xFFFFFF,
        0xF8B8B8,
        0xF85050,
        0xF88080,
        0xF80000,
        0xF83030,
        0xF80808,
        0xF80000,
        0xB80000,
        0xF80000,
        0x700000,
        0xC80000,
        0x480000,
        0xF88888,
        0x300000,
    ]


class BundtLargeObject(BossNPC):
    """Large Bundt object."""

    _base = BUNDT_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF85050,
        0xF88080,
        0xF88080,
        0xF88080,
        0xF83030,
        0xB80000,
        0xB80000,
        0xB80000,
        0x700000,
        0x700000,
        0xC80000,
        0x480000,
        0xF85050,
        0x300000,
    ]
    _recoil = 2
    _tower_crying = 3
    _bandits_way_distracted = 3
    _mines_punch = 4
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 3
    _kitchen_prep = 4
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 4
    _endgame_challenge = 4


class Bundt2LargeObject(BossNPC):
    """Large Bundt object."""

    _base = BUNDT_2_LARGE_2_NPC
    _evil_palette = [
        0xFFFFFF,
        0xF85050,
        0xF88080,
        0xF88080,
        0xF88080,
        0xF83030,
        0xB80000,
        0xB80000,
        0xB80000,
        0x700000,
        0x700000,
        0xC80000,
        0x480000,
        0xF85050,
        0x300000,
    ]
    _recoil = 2
    _tower_crying = 3
    _bandits_way_distracted = 3
    _mines_punch = 4
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 3
    _kitchen_prep = 4
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 4
    _endgame_challenge = 4


# Johnny (Jonathan Jones)
class JohnnySmallObject(BossNPC):
    """Small Johnny object."""

    _base = JONATHAN_JONES_NPC_2
    _eye_height = 19
    _tower_entrance_horizontal_shift = -3
    _tower_crying = 10
    _bandits_way_distracted = 10
    _mines_punch = 10
    _tower_bullet = 10
    _tower_toss = 10
    _chapel_laugh = 10
    _kitchen_prep = 10
    _ship_beckon = 10
    _ship_chair = 10
    _dojo_challenge = 10
    _statue_intro = 10
    _statue_flustered = 10
    _keep_challenge = 10
    _keep_summon = 10
    _chandelier_challenge = 10
    _factory_pierce = 10
    _endgame_challenge = 10
    _tpose_mold_id = 10
    _tpose = 11
    _evil_palette = [
        0xFFFFFF,
        0xEFFF42,
        0xFFCE94,
        0xA59442,
        0xB55A39,
        0x7B3118,
        0x524A21,
        0x423939,
        0x6B3921,
        0xA50000,
        0x310010,
        0x5A634A,
        0x422921,
        0x5A0000,
        0x181818,
    ]


class JohnnyLargeObject(BossNPC):
    """Large Johnny object."""

    _base = JOHNNY_NPC
    _evil_palette = [
        0xFFFFFF,
        0x7B3118,
        0xEFFF42,
        0x524A21,
        0x423939,
        0xFFCE94,
        0xA59442,
        0xB55A39,
        0xA50000,
        0x5A634A,
        0x310010,
        0xA59442,
        0xB55A39,
        0x5A0000,
        0x181818,
    ]
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 5
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


class Johnny2LargeObject(BossNPC):
    """Large Johnny object."""

    _base = JOHNNY_2_LARGE_2_NPC
    _evil_palette = [
        0xFFFFFF,
        0x7B3118,
        0xEFFF42,
        0x524A21,
        0x423939,
        0xFFCE94,
        0xA59442,
        0xB55A39,
        0xA50000,
        0x5A634A,
        0x310010,
        0xA59442,
        0xB55A39,
        0x5A0000,
        0x181818,
    ]
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 5
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


# Valentina
class ValentinaSmallObject(BossNPC):
    """Small Valentina object."""

    _base = VALENTINA_NPC_2
    _eye_height = 16
    _evil_palette = [
        0xF8F8F8,
        0xF87800,
        0xB84800,
        0xF81010,
        0xA00000,
        0x500000,
        0x70F8F8,
        0xF8B0D8,
        0xB06880,
        0xC0B880,
        0x807050,
        0x584828,
        0x282828,
        0x000000,
        0x181818,
    ]
    _recoil = 10
    _tower_crying = 10
    _bandits_way_distracted = 10
    _mines_punch = 2
    _tower_bullet = 2
    _tower_toss = 10
    _chapel_laugh = 2
    _ship_beckon = 10
    _ship_chair = 10
    _dojo_challenge = 2
    _statue_intro = 2
    _statue_flustered = 10
    _keep_challenge = 2
    _keep_summon = 2
    _chandelier_challenge = 2
    _factory_pierce = 2
    _endgame_challenge = 2
    _look_at_ceiling_mold_id = 8
    _look_at_ceiling = 10


class ValentinaLargeObject(BossNPC):
    """Large Valentina object."""

    _base = VALENTINA_NPC_5
    _recoil = 2
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 3
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


# Knife Guy
class KnifeGuySmallObject(BossNPC):
    """Small Knife Guy object."""

    _base = KNIFE_GUY_JUGGLER_STILL_RED_BALLS_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 11
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 11
    _kitchen_prep = 3
    _ship_beckon = 3
    _ship_chair = 11
    _dojo_challenge = 2
    _statue_intro = 2
    _statue_flustered = 5
    _keep_challenge = 2
    _keep_summon = 5
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 2


class KnifeGuyLargeObject(BossNPC):
    """Large Knife Guy object."""

    _base = KNIFE_GUY_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 4
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 4
    _endgame_challenge = 3


# Grate Guy
class GrateGuySmallObject(BossNPC):
    """Small Grate Guy object."""

    _base = GRATE_GUY_FROM_CASINO_NPC
    _eye_height = 16
    _evil_palette = [
        0xFFFFFF,
        0xADBDAD,
        0x8C8484,
        0x6B5263,
        0xF8F8F8,
        0xB8B8B8,
        0x888888,
        0x484848,
        0x101010,
        0xF80000,
        0xE80000,
        0xC00000,
        0x800000,
        0x380000,
        0x181818,
    ]
    _bandits_way_distracted = 0
    _mines_punch = 2
    _tower_bullet = 2
    _tower_toss = 2
    _chapel_laugh = 0
    _kitchen_prep = 2
    _ship_beckon = 3
    _ship_chair = 0
    _dojo_challenge = 0
    _statue_intro = 0
    _keep_challenge = 0
    _keep_summon = 2
    _chandelier_challenge = 0
    _factory_pierce = 2
    _endgame_challenge = 0


class GrateGuyLargeObject(BossNPC):
    """Large Grate Guy object."""

    _base = GRATE_GUY_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 4
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 4
    _endgame_challenge = 3


# Mokura
class MokuraLargeObject(BossNPC):
    """Large Mokura object."""

    _base = MOKURA_NPC


class MokuraSmallObject(BossNPC):
    """Small Mokura object."""

    _base = MOKURA_S_CLOUD_BLUE_NPC_2
    _eye_height = 1
    _crown_height = 1
    _evil_palette = [
        0xF8F0F0,
        0xF8D8D8,
        0xF8C0C0,
        0xF8A8A8,
        0xF88888,
        0xF87070,
        0xF85050,
        0xF82020,
        0xF82020,
        0xF80000,
        0xE00000,
        0x000000,
        0x000000,
        0x000000,
        0x300000,
    ]


# Yaridovich
class YaridovichLargeObject(BossNPC):
    """Large Yaridovich object."""

    _base = YARIDOVICH_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


# Missing Small/Medium Classes


class MagikoopaSmallObject(BossNPC):
    """Small Magikoopa object."""

    _base = RED_MAGIKOOPA_NPC
    _mines_punch = 10
    _tower_bullet = 10
    _tower_toss = 10
    _kitchen_prep = 10
    _ship_beckon = 10
    _dojo_challenge = 10
    _statue_intro = 10
    _statue_peck = 10
    _keep_challenge = 10
    _keep_summon = 10
    _chandelier_challenge = 10
    _factory_pierce = 10
    _endgame_challenge = 10
    _evil_palette = [
        0xFFFFFF,
        0xB59C9C,
        0x7B5A63,
        0xB56329,
        0xC60029,
        0x8C0029,
        0x5A0018,
        0x310042,
        0x00FF00,
        0xFFFF00,
        0xFFB500,
        0x8C3900,
        0xDE0800,
        0x4A1000,
        0x181818,
    ]
    _eye_height = 14


class ClerkSmallObject(BossNPC):
    """Small Clerk object."""

    _base = FACTORY_CLERK_GREEN_NPC_2
    _eye_height = 11
    _tower_entrance_horizontal_shift = 4
    _recoil = 3
    _tower_crying = 2
    _bandits_way_distracted = 2
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 2
    _kitchen_prep = 3
    _ship_beckon = 2
    _dojo_challenge = 2
    _statue_intro = 2
    _statue_flustered = 3
    _keep_challenge = 2
    _keep_summon = 3
    _chandelier_challenge = 2
    _factory_pierce = 3
    _endgame_challenge = 2
    _look_at_ceiling_mold_id = 1
    _look_at_ceiling = 2
    _evil_palette = [
        0xE7EFEF,
        0xBDC6CE,
        0x9C9C9C,
        0x736B6B,
        0x525252,
        0x424242,
        0x313131,
        0x383838,
        0x181818,
        0xF81818,
        0xC00000,
        0x980000,
        0x312118,
        0x300000,
        0x101010,
    ]


class ManagerSmallObject(BossNPC):
    """Small Manager object."""

    _base = FACTORY_MANAGER_BLUE_NPC
    _eye_height = 11
    _tower_entrance_horizontal_shift = 4
    _recoil = 3
    _tower_crying = 2
    _bandits_way_distracted = 2
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 2
    _kitchen_prep = 3
    _ship_beckon = 2
    _dojo_challenge = 2
    _statue_intro = 2
    _statue_flustered = 3
    _keep_challenge = 2
    _keep_summon = 3
    _chandelier_challenge = 2
    _factory_pierce = 3
    _endgame_challenge = 2
    _look_at_ceiling_mold_id = 1
    _look_at_ceiling = 2
    _evil_palette = [
        0xE7EFEF,
        0xBDC6CE,
        0x9C9C9C,
        0x736B6B,
        0x525252,
        0x424242,
        0x313131,
        0x383838,
        0x181818,
        0xF81818,
        0xC00000,
        0x980000,
        0x312118,
        0x300000,
        0x101010,
    ]


class DirectorSmallObject(BossNPC):
    """Small Director object."""

    _base = FACTORY_DIRECTOR_RED_NPC
    _eye_height = 11
    _tower_entrance_horizontal_shift = 4
    _recoil = 3
    _tower_crying = 2
    _bandits_way_distracted = 2
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 2
    _kitchen_prep = 3
    _ship_beckon = 2
    _dojo_challenge = 2
    _statue_intro = 2
    _statue_flustered = 3
    _keep_challenge = 2
    _keep_summon = 3
    _chandelier_challenge = 2
    _factory_pierce = 3
    _endgame_challenge = 2
    _look_at_ceiling_mold_id = 1
    _look_at_ceiling = 2
    _evil_palette = [
        0xE7EFEF,
        0xBDC6CE,
        0x9C9C9C,
        0x736B6B,
        0x525252,
        0x424242,
        0x313131,
        0x383838,
        0x181818,
        0xF81818,
        0xC00000,
        0x980000,
        0x312118,
        0x300000,
        0x101010,
    ]


class HidonSmallObject(BossNPC):
    """Small Hidon object."""

    _base = HIDON_SMALL_NPC
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFF7DE,
        0xFFFF63,
        0xFFEF63,
        0x00FFAD,
        0xFFEF00,
        0xFFE7B5,
        0xF7BD8C,
        0xE7A531,
        0xF80000,
        0xC00000,
        0xEF0000,
        0xA00000,
        0x089400,
        0x085A00,
        0x680000,
    ]


class ChesterSmallObject(BossNPC):
    """Small Chester object."""

    _base = CHESTER_SMALL_NPC
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFF7DE,
        0xFFFF63,
        0xFFEF63,
        0x00FFAD,
        0xFFEF00,
        0xFFE7B5,
        0xF7BD8C,
        0xE7A531,
        0xF80000,
        0xC00000,
        0xEF0000,
        0xA00000,
        0x089400,
        0x085A00,
        0x680000,
    ]


class BoxBoySmallObject(BossNPC):
    """Small Box Boy object."""

    _base = BOX_BOY_SMALL_NPC
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFF7DE,
        0xFFFF63,
        0xFFEF63,
        0x00FFAD,
        0xFFEF00,
        0xFFE7B5,
        0xF7BD8C,
        0xE7A531,
        0xF80000,
        0xC00000,
        0xEF0000,
        0xA00000,
        0x089400,
        0x085A00,
        0x680000,
    ]


# Missing Large Classes


class ClerkLargeObject(BossNPC):
    """Large Clerk object."""

    _base = CLERK_LARGE_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class ClerkBattleObject(BossNPC):
    """Battle Clerk object."""

    _base = CLERK_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class ManagerLargeObject(BossNPC):
    """Large Manager object."""

    _base = MANAGER_LARGE_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class ManagerBattleObject(BossNPC):
    """Battle Manager object."""

    _base = MANAGER_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class DirectorBattleObject(BossNPC):
    """Battle Director object."""

    _base = DIRECTOR_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class DirectorLargeObject(BossNPC):
    """Large Director object."""

    _base = DIRECTOR_LARGE_NPC
    _recoil = 2
    _tower_crying = 5
    _bandits_way_distracted = 5
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 4
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class HidonLargeObject(BossNPC):
    """Large Hidon object."""

    _base = HIDON_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 3
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3
    _statue_peck = 3


class ChesterLargeObject(BossNPC):
    """Large Chester object."""

    _base = CHESTER_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 3
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class BoxBoyLargeObject(BossNPC):
    """Large Box Boy object."""

    _base = BOX_BOY_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 3
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class MagikoopaLargeObject(BossNPC):
    """Large Magikoopa object."""

    _base = MAGIKOOPA_LARGE_NPC
    _recoil = 2
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 4
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 3
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


class DominoLargeObject(BossNPC):
    """Large Domino object."""

    _base = DOMINO_LARGE_NPC
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 3
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class MackLargeObject(BossNPC):
    """Large Mack object."""

    _base = MACK_LARGE_NPC
    _recoil = 2
    _tower_crying = 3
    _bandits_way_distracted = 0
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 4
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 4
    _endgame_challenge = 4
    _look_at_ceiling_mold_id = 5
    _look_at_ceiling = 8


# Missing Statue Classes


class NimbusLandStatueObject(StatueNPC):
    """Nimbus Land statue object."""

    _base = VALENTINA_STATUE_NPC
    _facing_shifts = {
        SOUTHEAST: PixelShift(-3, 0),
        NORTHWEST: PixelShift(-2, 0),
        NORTHEAST: PixelShift(-5, 0),
    }


class BelomeStatueObject(StatueNPC):
    """Belome statue object."""

    _base = GOLDEN_BELOME_NPC
    _recoil = 2
    _tower_crying = 4
    _bandits_way_distracted = 4
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 4
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3


class BoosterObject(BossNPC):
    """Booster object."""

    _base = BOOSTER_NPC
    _recoil = 4
    _tower_crying = 13
    _bandits_way_distracted = 2
    _mines_punch = 3
    _tower_bullet = 5
    _tower_toss = 3
    _chapel_laugh = 2
    _kitchen_prep = 2
    _ship_beckon = 2
    _ship_chair = 2
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 4
    _keep_challenge = 3
    _keep_summon = 5
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 5
    _look_at_ceiling_mold_id = 6
    _tpose_mold_id = 12
    _tpose = 15
    _look_at_ceiling = 6
    _evil_palette = [
        0xFFFFFF,
        0xADADCE,
        0xEF5252,
        0xC62129,
        0x8C0000,
        0x4A0000,
        0xF80000,
        0x600000,
        0x6B8CFF,
        0xFFCE94,
        0xB58452,
        0x7B5229,
        0x393131,
        0x5A5273,
        0x181818,
    ]


class BoosterStatueObject(StatueNPC):
    """Booster statue object."""

    _base = BOOSTER_STATUE_NPC


class JohnnyStatueObject(StatueNPC):
    """Johnny statue object."""

    _base = JOHNNY_STATUE_NPC
    _facing_shifts = {
        NORTHWEST: PixelShift(-6, 0),
        NORTHEAST: PixelShift(-2, 0),
    }


class MagikoopaStatueObject(StatueNPC):
    """Magikoopa statue object."""

    _base = MAGIKOOPA_STATUE_NPC
    _facing_shifts = {
        SOUTHEAST: PixelShift(2, 0),
        NORTHWEST: PixelShift(-3, 0),
        NORTHEAST: PixelShift(3, 0),
    }


class ShovelKnightStatueObject(StatueNPC):
    """Shovel Knight statue object (Clerk/Manager/Director)."""

    _base = SHOVEL_KNIGHT_STATUE_NPC
    _facing_shifts = {
        SOUTHEAST: PixelShift(-6, 0),
        NORTHWEST: PixelShift(-5, 0),
        NORTHEAST: PixelShift(-2, 0),
    }


class YaridovichStatueObject(StatueNPC):
    """Yaridovich statue object."""

    _base = YARIDOVICH_STATUE_NPC


class GrateGuyStatueObject(StatueNPC):
    """Grate Guy statue object."""

    _base = GRATE_GUY_STATUE_NPC
    _facing_shifts = {
        NORTHEAST: PixelShift(-5, 0),
        NORTHWEST: PixelShift(-2, 0),
        SOUTHEAST: PixelShift(-5, 0),
    }


class JinxStatueObject(StatueNPC):
    """Jinx statue object."""

    _base = JINX_STATUE_NPC
    _facing_shifts = {
        NORTHEAST: PixelShift(-2, -1),
        NORTHWEST: PixelShift(3, -1),
        SOUTHEAST: PixelShift(-2, -2),
    }


class MokuraStatueObject(StatueNPC):
    """Mokura statue object."""

    _base = MOKURA_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(0, -1),
    }


class TerrapinObject(BossNPC):
    """Terrapin object."""

    _base = TERRAPIN_NPC
    _recoil = 2
    _tower_crying = 8
    _bandits_way_distracted = 8
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 8
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 8
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 4
    _endgame_challenge = 4
    _look_at_camera = 6
    _evil_palette = [
        0xFFFFFF,
        0xFFEF73,
        0xC69431,
        0x734A08,
        0x423910,
        0xDE845A,
        0xB51839,
        0x5A0000,
        0x290000,
        0xE7E7EF,
        0xBDBDC6,
        0x73737B,
        0x4A4242,
        0x312939,
        0x181818,
    ]


class TerrapinStatueObject(StatueNPC):
    """Terrapin statue object."""

    _base = TERRAPIN_STATUE_NPC


class PiranhaPlantObject(BossNPC):
    """Piranha Plant object."""

    _base = PIRANHA_PLANT_NPC_3
    _eye_height = 14
    _recoil = 2
    _tower_crying = 7
    _bandits_way_distracted = 7
    _mines_punch = 4
    _tower_bullet = 8
    _tower_toss = 8
    _chapel_laugh = 7
    _kitchen_prep = 3
    _ship_beckon = 3
    _ship_chair = 7
    _dojo_challenge = 3
    _statue_intro = 7
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 8
    _chandelier_challenge = 3
    _factory_pierce = 4
    _endgame_challenge = 3
    _tpose_mold_id = 3
    _tpose = 5
    _evil_palette = [
        0xFFFFFF,
        0xD6D6D6,
        0xA5A5AD,
        0x7B7B73,
        0x636B63,
        0x4A4A4A,
        0x212929,
        0x008400,
        0x003900,
        0xFF00FF,
        0xC600C6,
        0x730073,
        0x290029,
        0x00D600,
        0x181818,
    ]


class PiranhaPlantStatueObject(StatueNPC):
    """Piranha Plant statue object."""

    _base = PIRANHA_PLANT_STATUE_NPC


class MegasmilaxLargeObject(BossNPC):
    """Large Megasmilax object."""

    _base = MEGASMILAX_NPC
    _recoil = 2
    _tower_crying = 3
    _bandits_way_distracted = 3
    _mines_punch = 3
    _tower_bullet = 5
    _tower_toss = 5
    _chapel_laugh = 3
    _kitchen_prep = 3
    _ship_beckon = 4
    _dojo_challenge = 4
    _statue_intro = 4
    _statue_flustered = 2
    _keep_challenge = 4
    _keep_summon = 4
    _chandelier_challenge = 4
    _factory_pierce = 3
    _endgame_challenge = 4


class BlooberObject(BossNPC):
    """Bloober object."""

    _base = BLOOBER_NPC
    _eye_height = 7
    _tower_entrance_horizontal_shift = 2
    _recoil = 2
    _tower_crying = 0
    _bandits_way_distracted = 0
    _mines_punch = 3
    _tower_bullet = 3
    _tower_toss = 3
    _chapel_laugh = 0
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 5
    _statue_peck = 3
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 3
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3
    _tpose_mold_id = 1
    _tpose = 6
    _evil_palette = [
        0xF80000,
        0xF80000,
        0xF00000,
        0xF00000,
        0xE80000,
        0xE00000,
        0xC00000,
        0xA00000,
        0x900000,
        0x780000,
        0x600000,
        0x300000,
        0x000000,
        0x000000,
        0x180000,
    ]


class BlooberStatueObject(StatueNPC):
    """Bloober statue object."""

    _base = BLOOBER_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(3, 0),
    }


class FactoryChiefStatueObject(StatueNPC):
    """Factory Chief statue object."""

    _base = FACTORY_CHIEF_STATUE_NPC
    _facing_shifts = {
        SOUTHEAST: PixelShift(-3, 0),
        NORTHEAST: PixelShift(-9, 0),
    }


class FactoryChiefObject(BossNPC):
    """Factory Chief object."""

    _base = FACTORY_CHIEF_NPC
    _recoil = 2
    _mines_punch = 4
    _tower_bullet = 4
    _tower_toss = 4
    _chapel_laugh = 5
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 3
    _statue_peck = 4
    _statue_flustered = 2
    _keep_challenge = 3
    _keep_summon = 4
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 3
    _look_at_ceiling_mold_id = 17
    _look_at_ceiling = 5
    _evil_palette = [
        0xADB5AD,
        0xFF6329,
        0xF74210,
        0xAD5A29,
        0xFFFFFF,
        0x526352,
        0xFF00FF,
        0xC61810,
        0x941008,
        0x293110,
        0x311008,
        0x001000,
        0x210000,
        0x001000,
        0x000000,
    ]


class AxemRedObject(BossNPC):
    """Axem Red object."""

    _base = AXEM_RED_NPC_2_LOW_VRAM
    _eye_height = 15
    _recoil = 2
    _mines_punch = 5
    _tower_bullet = 8
    _tower_toss = 8
    _kitchen_prep = 8
    _ship_beckon = 5
    _dojo_challenge = 5
    _statue_intro = 5
    _statue_peck = 8
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 5
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5
    _evil_palette = [
        0xFFFFFF,
        0xD6D6DE,
        0xADADB5,
        0x73737B,
        0x4A4242,
        0x293131,
        0xADADB5,
        0x73737B,
        0x524A4A,
        0x313131,
        0xCECED6,
        0x9C9CA5,
        0x6B6B73,
        0x313139,
        0x181818,
    ]


class AxemRedStatueObject(StatueNPC):
    """Axem Red statue object."""

    _base = AXEM_RED_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-5, 0),
    }


class BundtStatueObject(StatueNPC):
    """Bundt statue object."""

    _base = BUNDT_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-3, 0),
    }


class CountDownGridplaneObject(BossNPC):
    """Count Down gridplane object."""

    _base = COUNT_DOWN_GRIDPLANE_NPC
    _eye_height = 10
    _tower_entrance_horizontal_shift = 3
    _evil_palette = [
        0x2858F8,
        0xD06870,
        0xE04838,
        0x1848F8,
        0x484878,
        0xE82008,
        0x1028A8,
        0x4858C8,
        0x000000,
        0x382828,
        0x982820,
        0x402008,
        0xF8A820,
        0xF8D820,
        0x98A0B0,
    ]


class CountDownStatueObject(StatueNPC):
    """Count Down statue object."""

    _base = COUNT_DOWN_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(2, 0),
    }


class PunchinelloStatueObject(StatueNPC):
    """Punchinello statue object."""

    _base = PUNCHINELLO_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-1, 0),
    }


class DodoStatueObject(StatueNPC):
    """Dodo statue object."""

    _base = DODO_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-3, 0),
    }


class BirdettaStatueObject(StatueNPC):
    """Birdetta statue object."""

    _base = BIRDETTA_STATUE_NPC


class CzarStatueObject(StatueNPC):
    """Czar Dragon statue object."""

    _base = CZAR_DRAGON_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-7, 1),
    }


class BoomerStatueObject(StatueNPC):
    """Boomer statue object."""

    _base = BOOMER_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-5, 0),
    }


class ExorStatueObject(StatueNPC):
    """Exor statue object."""

    _base = EXOR_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-5, 0),
    }


class DominoStatueObject(StatueNPC):
    """Domino statue object."""

    _base = DOMINO_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-7, 0),
    }


class SmithyStatueObject(StatueNPC):
    """Smithy statue object."""

    _base = SMITHY_STATUE_NPC
    _facing_shifts = {
        SOUTHWEST: PixelShift(-7, 2),
    }


class CulexStatueObject(StatueNPC):
    """Culex statue object."""

    _base = CULEX_STATUE_NPC


class MallowStatueObject(StatueNPC):
    """Mallow statue object."""

    _base = MALLOW_STATUE_NPC


class MachineYaridOverworldObject(BossNPC):
    """Machine Made Yaridovich overworld object."""

    _base = MACHINE_YARID_OVERWORLD_NPC


class SmithyBodyOverworldObject(BossNPC):
    """Smithy body overworld object."""

    _base = SMITHY_BODY_OVERWORLD_NPC


class BoomerOverworldObject(BossNPC):
    """Boomer overworld object."""

    _base = BOOMER_RED_NPC
    _ship_beckon = 1
    _dojo_challenge = 1
    _statue_intro = 1
    _statue_flustered = 1
    _keep_challenge = 1
    _chandelier_challenge = 1
    _endgame_challenge = 1


class YaridovichSmallObject(BossNPC):
    """Small Yaridovich object."""

    _base = SEASIDE_TOWN_FAKE_ELDER_GREEN_NPC
    _eye_height = 9
    _tower_entrance_horizontal_shift = 3
    _evil_palette = [
        0xFFFFFF,
        0xFFCEA5,
        0xB57B5A,
        0xBD4A42,
        0x8C1810,
        0x310800,
        0xE79C00,
        0xC66B00,
        0x943900,
        0xCECECE,
        0xADCE94,
        0x7B9C42,
        0x427300,
        0x294A00,
        0x181818,
    ]


class YaridOverworldObject(BossNPC):
    """Yaridovich overworld object."""

    _base = YARIDOVICH_OUT_OF_BATTLE_NPC


class BowyerOverworldObject(BossNPC):
    """Bowyer overworld object."""

    _base = BOWYER_NPC_LARGE


# Postgame bosses - Small versions
class Punchinello2SmallObject(BossNPC):
    """Small Punchinello 2 object."""

    _base = PUNCHINELLO_2_SMALL_NPC
    _eye_height = 16
    _evil_palette = [
        0x181818,
        0x101010,
        0x000000,
        0xA81818,
        0xF80000,
        0x480000,
        0x580000,
        0x808068,
        0xFFFFFF,
        0xD0D8C0,
        0xB5B58C,
        0xF7EF63,
        0x9C6300,
        0x303030,
        0x000000,
    ]


class Booster2SmallObject(BossNPC):
    """Small Booster 2 object."""

    _base = BOOSTER_2_SMALL_NPC
    _evil_palette = [
        0xFFFFFF,
        0xADADCE,
        0xEF5252,
        0xC62129,
        0x8C0000,
        0x4A0000,
        0xF80000,
        0x600000,
        0x6B8CFF,
        0xFFCE94,
        0xB58452,
        0x7B5229,
        0x393131,
        0x5A5273,
        0x181818,
    ]
    _recoil = 4
    _tower_crying = 13
    _bandits_way_distracted = 2
    _mines_punch = 3
    _tower_bullet = 5
    _tower_toss = 3
    _chapel_laugh = 2
    _kitchen_prep = 2
    _ship_beckon = 2
    _ship_chair = 2
    _dojo_challenge = 3
    _statue_intro = 4
    _statue_peck = 3
    _statue_flustered = 4
    _keep_challenge = 3
    _keep_summon = 5
    _chandelier_challenge = 3
    _factory_pierce = 3
    _endgame_challenge = 5
    _look_at_ceiling_mold_id = 6
    _tpose_mold_id = 12
    _tpose = 15
    _look_at_ceiling = 6
    _eye_height = 15


class Bundt2SmallObject(BossNPC):
    """Small Bundt 2 object."""

    _base = BUNDT_2_SMALL_NPC
    _eye_height = 13
    _evil_palette = [
        0xFFFFFF,
        0xF8B8B8,
        0xF85050,
        0xF88080,
        0xF80000,
        0xF83030,
        0xF80808,
        0xF80000,
        0xB80000,
        0xF80000,
        0x700000,
        0xC80000,
        0x480000,
        0xF88888,
        0x300000,
    ]


class Johnny2SmallObject(BossNPC):
    """Small Johnny 2 object."""

    _base = JOHNNY_2_SMALL_NPC
    _eye_height = 19
    _tower_entrance_horizontal_shift = -3
    _tower_crying = 10
    _bandits_way_distracted = 10
    _mines_punch = 10
    _tower_bullet = 10
    _tower_toss = 10
    _chapel_laugh = 10
    _kitchen_prep = 10
    _ship_beckon = 10
    _ship_chair = 10
    _dojo_challenge = 10
    _statue_intro = 10
    _statue_flustered = 10
    _keep_challenge = 10
    _keep_summon = 10
    _chandelier_challenge = 10
    _factory_pierce = 10
    _endgame_challenge = 10
    _tpose_mold_id = 10
    _tpose = 11
    _evil_palette = [
        0xFFFFFF,
        0xEFFF42,
        0xFFCE94,
        0xA59442,
        0xB55A39,
        0x7B3118,
        0x524A21,
        0x423939,
        0x6B3921,
        0xA50000,
        0x310010,
        0x5A634A,
        0x422921,
        0x5A0000,
        0x181818,
    ]


class Jinx1SmallObject(BossNPC):
    """Small Jinx 1 object."""

    _base = JINX_1
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFFFFF,
        0xE7B56B,
        0x9C5242,
        0x6B294A,
        0x5A1829,
        0xC60000,
        0x6B0000,
        0x310000,
        0xFFFF00,
        0xF80000,
        0x480000,
        0x181818,
        0xE7DEDE,
        0x9C8C8C,
        0x181818,
    ]
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class Jinx2SmallObject(BossNPC):
    """Small Jinx 2 object."""

    _base = JINX_2
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFFFFF,
        0xE7B56B,
        0x9C5242,
        0x6B294A,
        0x5A1829,
        0xC60000,
        0x6B0000,
        0x310000,
        0xFFFF00,
        0xF80000,
        0x480000,
        0x181818,
        0xE7DEDE,
        0x9C8C8C,
        0x181818,
    ]
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class Jinx3SmallObject(BossNPC):
    """Small Jinx 3 object."""

    _base = JINX_3
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFFFFF,
        0xE7B56B,
        0x9C5242,
        0x6B294A,
        0x5A1829,
        0xC60000,
        0x6B0000,
        0x310000,
        0xFFFF00,
        0xF80000,
        0x480000,
        0x181818,
        0xE7DEDE,
        0x9C8C8C,
        0x181818,
    ]
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class Jinx4SmallObject(BossNPC):
    """Small Jinx 4 object."""

    _base = JINX_4
    _eye_height = 5
    _crown_height = 1
    _evil_palette = [
        0xFFFFFF,
        0xE7B56B,
        0x9C5242,
        0x6B294A,
        0x5A1829,
        0xC60000,
        0x6B0000,
        0x310000,
        0xFFFF00,
        0xF80000,
        0x480000,
        0x181818,
        0xE7DEDE,
        0x9C8C8C,
        0x181818,
    ]
    _recoil = 2
    _mines_punch = 3
    _tower_bullet = 4
    _tower_toss = 3
    _kitchen_prep = 3
    _ship_beckon = 3
    _dojo_challenge = 3
    _statue_intro = 5
    _statue_flustered = 2
    _keep_challenge = 5
    _keep_summon = 4
    _chandelier_challenge = 5
    _factory_pierce = 3
    _endgame_challenge = 5


class Culex3DSmallObject(BossNPC):
    """Small Culex 3D object."""

    _base = CULEX_2_SMALL_NPC
    _eye_height = 13
    _evil_palette = [
        0x180808,
        0x585858,
        0x383838,
        0x101010,
        0xC69C4A,
        0xFFD66B,
        0x000000,
        0x9C2918,
        0x522110,
        0xBD6329,
        0xF81818,
        0x380000,
        0xA80000,
        0x780000,
        0xF8A8A8,
    ]
