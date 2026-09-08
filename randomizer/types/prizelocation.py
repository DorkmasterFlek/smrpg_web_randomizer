from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Generic, cast
from uuid import uuid4
from enum import StrEnum
import random
from copy import deepcopy

from smrpgpatchbuilder.datatypes.overworld_scripts.arguments import NPC_12
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.controller_inputs import B

from randomizer.data.variables.dialog_names import DI2010_DEBUG_7000
from randomizer.logic.progression.prizes import (
    BoomerBossFight,
    SmithyBossFight,
    FirstMimicFightLauncher,
    InfiniteCoinsPrize,
    SecondMimicFightLauncher,
    ThirdMimicFightLauncher,
)

from .prize import (
    FPFlowerPrize,
    MimicFightInitiatorPrize,
    Prize,
    EXPStarPrize,
    BossFightPrize,
    BossFightHenchman,
    CharacterPrize,
    SlotsPrize,
    StarPiecePrize,
    ItemPrize,
    SpellPrize,
    KeyPrize,
)
from smrpgpatchbuilder.datatypes.battles.formations_packs.types.classes import (
    Formation,
    FormationMember,
)
from ..utils.event_script_snippets.es_slot_machine import create_slot_machine_script
from ..utils.npcs import set_npc_direction_if_swse_only
from ..logic.shufflers.enemies import generate_formation_coordinates

from ..data.variables.event_script_names import *
from ..data.variables.action_script_names import *
from ..data.variables.variable_names import (
    BATTLE_PACK_ID,
    BOOSTER_HILL_FLOWER_COUNTER,
    LANDS_END_GROTTO_BARREL_FLIPPED,
    MIMIC_1_CLEARED,
    MIMIC_2_CLEARED,
    PRIMARY_TEMP_7000,
    MUSHROOM_KINGDOM_OCCUPIED
)
from ..data.variables.battlefield_names import *
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (
    EventScript,
    UsableEventScriptCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.classes import (
    ActionScript,
    UsableActionScriptCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
    DisableObjectTriggerInSpecificLevel,
    EnableControlsUntilReturn,
    JmpIfBitClear,
    JmpIfBitSet,
    Return,
    Inc,
    JmpIfVarEqualsConst,
    RunDialog,
    StartBattleAtBattlefield,
    StartBattleWithPackAt700E,
    SetVarToConst,
    JmpToEvent,
    ActionQueueAsync,
    Set7000ToCurrentLevel,
    SetBit,
    Jmp,
    RemoveObjectAt70A8FromCurrentLevel,
    RemoveObjectFromCurrentLevel,
    ActionQueueSync,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import (
    A_UnknownCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import MEM_70A8
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.flag import Flag
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import (
    A_SetSpriteSequence,
    A_WalkEastPixels,
    A_WalkWestPixels,
    A_WalkNorthPixels,
    A_WalkSouthPixels,
    A_ReturnQueue,
    A_ShiftXYPixels,
    A_FixedFCoordOn,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types import (
    AreaObject,
    Battlefield,
)
from smrpgpatchbuilder.datatypes.levels.classes import (
    RegularNPC,
    EventInitiator,
    VramStore,
    RegularClone,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import (
    SOUTHEAST,
    SOUTHWEST,
    NORTHEAST,
    NORTHWEST,
)
from .base import CategorizationOption
from .packet_type import PacketType
from ..data.rooms.npcs import (
    EMPTY_NPC_3,
    EXPLOSION_NPC,
    FLOWER_NPC_2,
    FROG_COIN_NPC,
    STATIC_FROG_COIN_NPC,
)
from ..data.variables.room_names import *
from ..data.variables.variable_names import (
    INVISIBLE_FLAG_1_FOUND,
    INVISIBLE_FLAG_2_FOUND,
    INVISIBLE_FLAG_3_FOUND,
    SHIP_PACKET_AUTOTERM_DIALOG,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.packet import Packet
from ..data.physical_objects.items import DefaultItem
from ..types.prize import TOriginallyHeld

from ..types.physical_objects import PixelShift

if TYPE_CHECKING:
    from ..types.logic import Inventory
    from ..types.gameworld import GameWorld
    from ..types.enemy import Enemy
    from ..types.physical_objects import ItemNPC, BossNPC, HenchmanNPC
    from ..types.flags import BooleanFlag

# Flag + prize classes formerly fetched via a lazy dispatcher.
# flags.py is a leaf module now, so these import cleanly at module scope.
from .flags import (
    CategorizationFlag,
    WinCondition,
    WinConditions,
    KeyItemsAnywhere,
    SpellsAnywhere,
    StarPieceAvailability,
    ShuffleItems,
    ShuffleHillFlowers,
    DisperseStarPieces,
    RestrictSpecialEquips,
    BanditsWayGate,
    BanditsWayGating,
    KeroSewersGate,
    KeroSewersGating,
    PipeVaultGate,
    PipeVaultGating,
    Moleville1Gate,
    Moleville1Gating,
    BoosterTowerGate,
    BoosterTowerGating,
    BoosterHillGate,
    BoosterHillGating,
    MarrymoreGate,
    MarrymoreGating,
    SeaGate,
    SeaGating,
    YaridovichGate,
    YaridovichGating,
    LandsEndGate,
    LandsEndGating,
    MonstroTownGate,
    MonstroTownGating,
    NimbusGate,
    NimbusGating,
    BarrelVolcanoGate,
    BarrelVolcanoGating,
    BowsersKeepGate,
    BowsersKeepGating,
    FactoryGate,
    FactoryGating,
    AnnoyingChests,
)
from randomizer.logic.progression.prizes import (
    SmithyBossFight,
    MimicFightInitiatorPrize,
    RegularFireworksPrize,
    FirstMimicFightLauncher,
    SecondMimicFightLauncher,
    ThirdMimicFightLauncher,
    HammerBrosFight,
    MackBossFight,
    BowyerBossFight,
    PunchinelloBossFight,
    KnifeGuyGrateGuyBossFight,
    BundtBossFight,
    JohnnyBossFight,
    YaridovichBossFight,
    Belome2BossFight,
    MegasmilaxBossFight,
    ValentinaBossFight,
    AxemRangersBossFight,
    ExorBossFight,
    KamekBossFight,
    CountdownBossFight,
    DryBonesFlagPrize,
    GreaperFlagPrize,
    BigBooFlagPrize,
)
from ..data.variables.event_script_names import (
            E1189_HENCHMAN_BATTLE_PACK_SELECTOR,
        )
from ..utils.npcs import min_vram_from_sequence_for_sprite
from .prize import BossFightPrize
from smrpgpatchbuilder.datatypes.levels.classes import (
            BattlePackNPC,
            BattlePackClone,
        )
from smrpgpatchbuilder.datatypes.levels.classes import BattlePackNPC
from randomizer.types.flags import MimicsAnywhere
from randomizer.types.flags import SpellsAnywhere
from randomizer.types.flags import ItemQuality, ItemQualityOptions
from randomizer.types.flags import (CharacterLearnedSpells, SlotsAnywhere)
import random as _random


class ShuffleLocationSelector(CategorizationOption):
    """Enumeration for enabling and disabling locations"""

    STARTER_CHARACTER_1 = "Starter character 1"
    STARTER_CHARACTER_2 = "Starter character 2"
    STARTER_CHARACTER_3 = "Starter character 3"
    STARTER_CHARACTER_4 = "Starter character 4"
    STARTER_CHARACTER_5 = "Starter character 5"
    MARIOS_PAD_STARTER_1 = "Starter item 1"
    MARIOS_PAD_STARTER_2 = "Starter item 2"
    MARIOS_PAD_STARTER_3 = "Starter item 3"
    MARIOS_PAD_STARTER_4 = "Starter item 4"
    POSTGAME_VOUCHER = "Toad's postgame item grant"
    MUSHROOM_WAY_1 = "Mushroom Way first chest"
    MUSHROOM_WAY_2 = "Mushroom Way second chest"
    MUSHROOM_WAY_3 = "Mushroom Way flower jump left chest"
    MUSHROOM_WAY_4 = "Mushroom Way second room right chest"
    REMAKE_1 = "Mushroom Way left freestanding item"
    REMAKE_2 = "Mushroom Way right freestanding item"
    TOAD_RESCUE_1 = "Mushroom Way first Toad reward"
    TOAD_RESCUE_2 = "Mushroom Way second Toad reward"
    MUSHROOM_WAY_BOSS_FIGHT = "Mushroom Way boss fight"
    MUSHROOM_WAY_STAR_PIECE = "Mushroom Way boss Star Piece"
    HAMMER_BROS_REWARD = "Mushroom Way boss item reward"
    MUSHROOM_WAY_CHARACTER = "Mushroom Way character join"
    MUSHROOM_KINGDOM_HALLWAY = "Mushroom Kingdom castle main hallway chest"
    MUSHROOM_KINGDOM_VAULT_1 = "Mushroom Kingdom vault left chest (liberated)"
    MUSHROOM_KINGDOM_VAULT_2 = "Mushroom Kingdom vault right chest (liberated)"
    MUSHROOM_KINGDOM_VAULT_3 = "Mushroom Kingdom vault middle chest (liberated)"
    MUSHROOM_KINGDOM_VAULT_4 = "Mushroom Kingdom vault left chest (occupied)"
    MUSHROOM_KINGDOM_VAULT_5 = "Mushroom Kingdom vault right chest (occupied)"
    MUSHROOM_KINGDOM_VAULT_6 = "Mushroom Kingdom vault middle chest (occupied)"
    INVASION_EASTERN_GUARD = "Mushroom Kingdom eastern guard rescue (invasion)"
    WALLET_GUY_1 = "Wallet exchange reward 1"
    WALLET_GUY_2 = "Wallet exchange reward 2"
    MUSHROOM_KINGDOM_STORE = "Mushroom Kingdom shop free item"
    MUSHROOM_KINGDOM_STORE_EXCHANGE = "Mushroom Kingdom shop Rare Frog Coin exchange"
    MUSHROOM_KINGDOM_STORE_BASEMENT_1 = "Mushroom Kingdom shop basement left chest"
    MUSHROOM_KINGDOM_STORE_BASEMENT_2 = "Mushroom Kingdom shop basement right chest"
    PEACH_SURPRISE = "Mushroom Kingdom Toadstool's room chair item"
    INVASION_TOAD_RESCUE = (
        "Mushroom Kingdom Toadstool's room toad rescue item (invasion)"
    )
    INVASION_FAMILY = "Mushroom Kingdom invasion family rescue"
    INVASION_GUEST_ROOM = "Mushroom Kingdom invasion guest room"
    INVASION_BOSS_FIGHT = "Mushroom Kingdom boss fight"
    INVASION_STAR_PIECE = "Mushroom Kingdom invasion boss Star Piece"
    MUSHROOM_KINGDOM_INN = "Mushroom Kingdom gameboy kid"
    BANDITS_WAY_1 = "Bandit's Way flower chest"
    BANDITS_WAY_COIN_1 = "Bandit's Way 1st coin"
    BANDITS_WAY_COIN_2 = "Bandit's Way 2nd coin"
    BANDITS_WAY_COIN_3 = "Bandit's Way 3rd coin"
    BANDITS_WAY_2 = "Bandit's Way long room chest"
    BANDITS_WAY_STAR_CHEST = "Bandit's Way star chest"
    BANDITS_WAY_DOG_JUMP = "Bandit's Way dog jump chest"
    BANDITS_WAY_CROCO = "Bandit's Way Croco chase chest"
    BANDITS_WAY_BOSS_FIGHT = "Bandit's Way boss fight"
    BANDITS_WAY_STAR_PIECE = "Bandit's Way boss Star Piece"
    CROCO_1_REWARD = "Bandit's Way boss item reward 1"
    CROCO_1_REWARD_2 = "Bandit's Way boss item reward 2"
    KERO_SEWERS_PANDORITE_ROOM = "Kero Sewers stairway room left chest"
    PANDORITE_CHEST = "Kero Sewers stairway room right chest"
    PANDORITE_BOSS_FIGHT = "Mimic Chest #1 boss fight"
    PANDORITE_BOSS = "Mimic Chest #1 Star Piece"
    PANDORITE_REWARD_1 = "Mimic Chest #1 drop reward"
    PANDORITE_REWARD_2 = "Mimic Chest #1 reload reward"
    KERO_SEWERS_STAR_CHEST = "Kero Sewers four rat room chest"
    KERO_SEWERS_BEFORE_BELOME_LOWER = "Kero Sewers before boss lower chest"
    KERO_SEWERS_BEFORE_BELOME_UPPER_1 = (
        "Kero Sewers before boss upper chest, before Land's End"
    )
    KERO_SEWERS_BEFORE_BELOME_UPPER_2 = (
        "Kero Sewers before boss upper chest, after Land's End"
    )
    KERO_SEWERS_BOSS = "Kero Sewers boss"
    KERO_SEWERS_STAR_PIECE = "Kero Sewers boss Star Piece"
    MIDAS_RIVER_FIRST_TIME = "Midas River first play reward"
    MIDAS_RIVER_LEFT_CAVE = "Midas River upper left tunnel freestanding frog coin"
    MIDAS_RIVER_BOTTOM_LEFT_CAVE = (
        "Midas River bottom left tunnel freestanding frog coin"
    )
    MIDAS_RIVER_BOTTOM_RIGHT_CAVE = (
        "Midas River bottom right tunnel freestanding flower"
    )
    CRICKET_PIE_REWARD = "Tadpole Pond Cricket Pie exchange"
    CRICKET_JAM_REWARD = "Tadpole Pond Cricket Jam exchange"
    MELODY_BAY_1 = "Melody Bay song 1 reward"
    MELODY_BAY_2 = "Melody Bay song 2 reward"
    MELODY_BAY_3 = "Melody Bay song 3 reward"
    ROSE_WAY_PLATFORM = "Rose Way swinging Shy Guy chest"
    ROSE_WAY_FLOWER = "Rose Way freestanding flower"
    ROSE_WAY_MUSHROOM = "Rose Way freestanding mushroom"
    ROSE_WAY_COIN_1 = "Rose Way freestanding coin 1"
    ROSE_WAY_COIN_2 = "Rose Way freestanding coin 2"
    ROSE_WAY_COIN_3 = "Rose Way freestanding coin 3"
    ROSE_WAY_COIN_4 = "Rose Way freestanding coin 4"
    ROSE_WAY_COIN_5 = "Rose Way freestanding coin 5"
    ROSE_WAY_FIVE_CHESTS_1 = "Rose Way five-chest area top middle chest"
    ROSE_WAY_FIVE_CHESTS_2 = "Rose Way five-chest area bottom left chest"
    ROSE_WAY_FIVE_CHESTS_3 = "Rose Way five-chest top right chest"
    ROSE_WAY_FIVE_CHESTS_4 = "Rose Way five-chest top left chest"
    ROSE_WAY_FIVE_CHESTS_5 = "Rose Way five-chest bottom right chest"
    ROSE_TOWN_STORE_1 = "Rose Town shop right chest"
    ROSE_TOWN_STORE_2 = "Rose Town shop left chest"
    GARDENER_CLOUD_1 = "Rose Town gardener right chest"
    GARDENER_CLOUD_2 = "Rose Town gardener left chest"
    ROSE_TOWN_TOAD = "Rose Town Inn Toad gift"
    GAZ = "Rose Town Gaz gift"
    ROSE_TOWN_TREASURE_HOUSE_1 = "Rose Town upper house left chest"
    ROSE_TOWN_TREASURE_HOUSE_2 = "Rose Town upper house right chest"
    ROSE_TOWN_TREASURE_HOUSE_MAZE_REWARD = "Rose Town upper house Maze Secret prize"
    ROSE_TOWN_TREASURE_HOUSE_3 = "Rose Town upper house top floor chest"
    FOREST_MAZE_1 = "Forest Maze 1st room chest"
    FOREST_MAZE_2 = "Forest Maze first chest after underground"
    FOREST_MAZE_UNDERGROUND_1 = "Forest Maze wiggler chest"
    FOREST_MAZE_UNDERGROUND_2 = "Forest Maze bottom right stump chest"
    FOREST_MAZE_UNDERGROUND_3 = "Forest Maze middle left stump chest"
    FOREST_MAZE_RED_ESSENCE = "Forest Maze before maze chest"
    FOREST_MAZE_SECRET_1 = "Forest Maze secret top right chest"
    FOREST_MAZE_SECRET_2 = "Forest Maze secret bottom right chest"
    FOREST_MAZE_SECRET_3 = "Forest Maze secret top middle chest"
    FOREST_MAZE_SECRET_4 = "Forest Maze secret bottom middle chest"
    FOREST_MAZE_SECRET_5 = "Forest Maze secret left chest"
    FOREST_MAZE_CHARACTER = "Forest Maze character recruit"
    FOREST_MAZE_BOSS = "Forest Maze boss"
    FOREST_MAZE_STAR_PIECE = "Forest Maze boss Star Piece"
    PIPE_VAULT_SLIDE_1 = "Pipe Vault slide room back chest"
    PIPE_VAULT_SLIDE_2 = "Pipe Vault slide room middle chest"
    PIPE_VAULT_SLIDE_3 = "Pipe Vault slide room front chest"
    PIPE_VAULT_SLIDE_COIN_1 = "Pipe Vault slide room freestanding coin 1"
    PIPE_VAULT_SLIDE_COIN_2 = "Pipe Vault slide room freestanding coin 2"
    PIPE_VAULT_SLIDE_COIN_3 = "Pipe Vault slide room freestanding coin 3"
    PIPE_VAULT_SLIDE_COIN_4 = "Pipe Vault slide room freestanding coin 4"
    PIPE_VAULT_SLIDE_COIN_5 = "Pipe Vault slide room freestanding coin 5"
    PIPE_VAULT_SLIDE_FROG_COIN = "Pipe Vault slide room freestanding frog coin"
    PIPE_VAULT_NIPPERS_1 = "Pipe Vault nipper room first chest"
    PIPE_VAULT_NIPPERS_2 = "Pipe Vault nipper room second chest"
    GOOMBA_THUMPING_1 = "Pipe Vault Goomba Thumpin first prize"
    GOOMBA_THUMPING_2 = "Pipe Vault Goomba Thumpin second prize"
    YOSTER_ISLE_ENTRANCE = "Yo'ster Isle entrance chest"
    YOSTER_ISLE_RACE_COOKIE = "Yo'ster Isle race-starting cookies"
    YOSTER_ISLE_RACE_REWARD_1 = "Yo'ster Isle first race prize item 1"
    YOSTER_ISLE_RACE_REWARD_2 = "Yo'ster Isle first race prize item 3"
    YOSTER_ISLE_RACE_REWARD_3 = "Yo'ster Isle first race prize item 2"
    CROCO_FLUNKIE_1 = "Moleville Mines trampoline bandit"
    CROCO_FLUNKIE_2 = "Moleville Mines left bandit"
    CROCO_FLUNKIE_3 = "Moleville Mines right bandit"
    CROCO_2_ITEM = "Moleville Mines first boss item"
    MOLEVILLE_MINES_BOSS_FIGHT_1 = "Moleville Mines first boss fight"
    MOLEVILLE_MINES_BOSS_1 = "Moleville Mines first boss Star Piece"
    MOLEVILLE_MINES_SHY_GUY = "Moleville Mines shy guy cart"
    MOLEVILLE_MINES_STAR_CHEST = "Moleville Mines two-level traintrack room chest"
    MOLEVILLE_MINES_COINS = "Moleville Mines near final train tracks chest"
    MOLEVILLE_MINES_PUNCHINELLO_1 = "Moleville Mines before boss left chest"
    MOLEVILLE_MINES_PUNCHINELLO_2 = "Moleville Mines before boss upper chest"
    MOLEVILLE_MINES_BOSS_FIGHT = "Moleville Mines second boss fight"
    MOLEVILLE_MINES_BOSS_2 = "Moleville Mines second boss Star Piece"
    MOLEVILLE_MINES_CHARACTER = "Moleville Mines character recruit"
    MOLEVILLE_MINES_BOSS_FIGHT_3 = "Moleville Mines postgame boss fight"
    MOLEVILLE_MINES_BOSS_3 = "Moleville Mines postgame boss Star Piece"
    MOLEVILLE_MINES_POSTGAME_DROP = "Moleville Mines postgame prize"
    PURTEND_STORE = "Pur-tend Store"
    COOKIE_TRADER = "Carbo Cookie Trader"
    BUCKET_GIRL = "Moleville bucket girl"
    TREASURE_SELLER_1 = "Moleville first treasure shop item"
    TREASURE_SELLER_2 = "Moleville second treasure shop item"
    TREASURE_SELLER_3 = "Moleville third treasure shop item"
    FIREWORKS_SHOP = "Moleville fireworks shop item"
    BOOSTER_PASS_1 = "Booster Pass main area left chest"
    BOOSTER_PASS_2 = "Booster Pass main area right chest"
    BOOSTER_PASS_BUSH = "Booster Pass main area bush check"
    BOOSTER_PASS_FLOWER = "Booster Pass freestanding flower"
    BOOSTER_PASS_SECRET_1 = "Booster Pass secret middle chest"
    BOOSTER_PASS_SECRET_2 = "Booster Pass secret right chest"
    BOOSTER_PASS_SECRET_3 = "Booster Pass secret left chest"
    BOOSTER_TOWER_SPOOKUM = "Booster Tower first stairway chest"
    BOOSTER_TOWER_THWOMP = "Booster Tower upper thwomp room chest"
    BOOSTER_TOWER_KNIFE_GUY = "Booster Tower Knife Guy reward"
    BOOSTER_TOWER_KNIFE_GUY_2 = "Booster Tower Knife Guy maxed out reward (if fixed)"
    BOOSTER_TOWER_ROOM_KEY = "Booster Tower checkerboard room item"
    BOOSTER_TOWER_FROG_COIN_1 = (
        "Booster Tower checkerboard room freestanding frog coin 1"
    )
    BOOSTER_TOWER_FROG_COIN_2 = (
        "Booster Tower checkerboard room freestanding frog coin 2"
    )
    BOOSTER_TOWER_FROG_COIN_3 = (
        "Booster Tower checkerboard room freestanding frog coin 3"
    )
    BOOSTER_TOWER_FROG_COIN_4 = (
        "Booster Tower checkerboard room freestanding frog coin 4"
    )
    BOOSTER_TOWER_COIN_1 = "Booster Tower checkerboard room freestanding coin 1"
    BOOSTER_TOWER_COIN_2 = "Booster Tower checkerboard room freestanding coin 2"
    BOOSTER_TOWER_COIN_3 = "Booster Tower checkerboard room freestanding coin 3"
    BOOSTER_TOWER_COIN_4 = "Booster Tower checkerboard room freestanding coin 4"
    BOOSTER_TOWER_COIN_5 = "Booster Tower checkerboard room freestanding coin 5"
    BOOSTER_TOWER_COIN_6 = "Booster Tower checkerboard room freestanding coin 6"
    BOOSTER_TOWER_COIN_7 = "Booster Tower checkerboard room freestanding coin 7"
    BOOSTER_TOWER_COIN_8 = "Booster Tower checkerboard room freestanding coin 8"
    BOOSTER_TOWER_COIN_9 = "Booster Tower checkerboard room freestanding coin 9"
    BOOSTER_TOWER_MASHER = "Booster Tower Masher chest"
    BOOSTER_TOWER_PARACHUTE = "Booster Tower parachute room chest"
    BOOSTER_TOWER_PARACHUTE_CREVICE = "Booster Tower parachute room stair crevice"
    BOOSTER_TOWER_ZOOM_SHOES = "Booster Tower Room Key chest"
    BOOSTER_TOWER_TOP_1 = "Booster Tower top floor lower chest"
    BOOSTER_TOWER_TOP_2 = "Booster Tower top floor upper chest"
    BOOSTER_TOWER_TOP_3 = "Booster Tower top floor corner chest"
    BOOSTER_TOWER_RAILWAY = "Booster Tower railway room crevice" 
    BOOSTER_TOWER_PORTRAITS = "Booster Tower portrait prize"
    BOOSTER_TOWER_CHOMP = "Booster Tower Elder Key room"
    BOOSTER_TOWER_CURTAIN_GAME = "Booster Tower curtain prize"
    BOOSTER_TOWER_MARIO_DOLL = "Booster Tower doll above curtains"
    BOOSTER_TOWER_BOSS_1 = "Booster Tower curtain room boss fight"
    BOOSTER_TOWER_STAR_PIECE_1 = "Booster Tower curtain room boss Star Piece"
    BOOSTER_TOWER_BOSS_2 = "Booster Tower balcony boss fight"
    BOOSTER_TOWER_STAR_PIECE_2 = "Booster Tower balcony boss Star Piece"
    BOOSTER_TOWER_BOSS_3 = "Booster Tower postgame boss fight"
    BOOSTER_TOWER_STAR_PIECE_3 = "Booster Tower postgame boss Star Piece"
    BOOSTER_TOWER_POSTGAME_DROP = "Booster Tower postgame prize"
    BOOSTER_HILL_FLOWER_1 = "Booster Hill flower 1"
    BOOSTER_HILL_FLOWER_2 = "Booster Hill flower 2"
    BOOSTER_HILL_FLOWER_3 = "Booster Hill flower 3"
    BOOSTER_HILL_FLOWER_4 = "Booster Hill flower 4"
    BOOSTER_HILL_FLOWER_5 = "Booster Hill flower 5"
    BOOSTER_HILL_FLOWER_6 = "Booster Hill flower 6"
    BOOSTER_HILL_FLOWER_7 = "Booster Hill flower 7"
    BOOSTER_HILL_FLOWER_8 = "Booster Hill flower 8"
    BOOSTER_HILL_FLOWER_9 = "Booster Hill flower 9"
    BOOSTER_HILL_FLOWER_10 = "Booster Hill flower 10"
    BOOSTER_HILL_FLOWER_11 = "Booster Hill flower 11"
    BOOSTER_HILL_FLOWER_12 = "Booster Hill flower 12"
    BOOSTER_HILL_FLOWER_13 = "Booster Hill flower 13"
    BOOSTER_HILL_FLOWER_14 = "Booster Hill flower 14"
    BOOSTER_HILL_FLOWER_15 = "Booster Hill flower 15"
    BOOSTER_HILL_FLOWER_16 = "Booster Hill flower 16"
    MARRYMORE_PRIZE_1 = "Marrymore Suite total stays prize 1"
    MARRYMORE_PRIZE_2 = "Marrymore Suite total stays prize 2"
    MARRYMORE_PRIZE_3 = "Marrymore Suite total stays prize 3"
    MARRYMORE_PRIZE_4 = "Marrymore Suite total stays prize 4"
    MARRYMORE_PRIZE_5 = "Marrymore Suite total stays prize 5"
    MARRYMORE_PRIZE_6 = "Marrymore Suite total stays prize 6"
    MARRYMORE_BIG_TIP = "Marrymore Inn elderly guest tip (on the way out)"
    MARRYMORE_INN = "Marrymore Inn regular room chest"
    MARRYMORE_SNIFIT_1 = "Marrymore Snifit 1 chapel item"
    MARRYMORE_SNIFIT_2 = "Marrymore Snifit 2 chapel item"
    MARRYMORE_SNIFIT_3 = "Marrymore Snifit 3 chapel item"
    MARRYMORE_ALTAR = "Marrymore altar chapel item"
    MARRYMORE_BOSS_FIGHT = "Marrymore boss fight"
    MARRYMORE_STAR_PIECE = "Marrymore boss Star Piece"
    MARRYMORE_CHARACTER = "Marrymore character join"
    MARRYMORE_POSTGAME_BOSS_FIGHT = "Marrymore postgame boss fight"
    MARRYMORE_POSTGAME_STAR_PIECE = "Marrymore postgame boss Star Piece"
    MARRYMORE_POSTGAME_ITEM_DROP = "Marrymore postgame prize"
    STAR_HILL_STAR_PIECE_1 = "Star Hill freestanding Star Piece"
    FROG_DISCIPLE_1 = "Disciple shop first item"
    FROG_DISCIPLE_2 = "Disciple shop second item"
    FROG_DISCIPLE_3 = "Disciple shop third item"
    FROG_DISCIPLE_4 = "Disciple shop fourth item"
    FROG_DISCIPLE_5 = "Disciple shop fifth item"
    SEASIDE_TOWN_BOSS_FIGHT = "Seaside Town boss fight"
    SEASIDE_TOWN_BOSS = "Seaside Town boss Star Piece"
    SEASIDE_TOWN_BOSS_PRIZE = "Seaside Town boss prize"
    SEASIDE_TOWN_RESCUE = "Seaside Town shed rescue"
    SEA_STAR_CHEST = "Sea starslap room chest"
    SEA_SAVE_ROOM_1 = "Sea save room back chest"
    SEA_SAVE_ROOM_2 = "Sea save room middle chest"
    SEA_SAVE_ROOM_3 = "Sea save room front chest"
    SEA_WHIRLPOOL_CHEST = "Sea whirlpool room chest"
    SUNKEN_SHIP_RAT_STAIRS = "Sunken Ship first stairway chest"
    SUNKEN_SHIP_RAT_STAIRS_FLOWER = "Sunken Ship first stairway freestanding flower"
    SUNKEN_SHIP_SHOP = "Sunken Ship shop area chest"
    SUNKEN_SHIP_TRAMPOLINE_PUZZLE = "Sunken Ship trampoline puzzle prize"
    SUNKEN_SHIP_TROOPA_PUZZLE = "Sunken Ship troopa cannonball prize"
    SUNKEN_SHIP_3D_MAZE = "Sunken Ship 3D maze prize"
    SUNKEN_SHIP_COIN_SNAKE = "Sunken Ship coin snake puzzle prize"
    SUNKEN_SHIP_CANNONBALL_PUZZLE = "Sunken Ship cannonball puzzle prize"
    SUNKEN_SHIP_BARREL_PUZZLE = "Sunken Ship barrel switch prize"
    SUNKEN_SHIP_MIDBOSS = "Sunken Ship password boss Star Piece"
    SUNKEN_SHIP_MIDBOSS_BOSS_FIGHT = "Sunken Ship password boss fight"
    SUNKEN_SHIP_COINS_1 = "Sunken Ship outside clone room left chest"
    SUNKEN_SHIP_COINS_2 = "Sunken Ship outside clone room right chest"
    SUNKEN_SHIP_CLONE_ROOM = "Sunken Ship clone room chest"
    SUNKEN_SHIP_FROG_COIN_ROOM = "Sunken Ship hidden box room chest"
    SUNKEN_SHIP_HIDON_MUSHROOM = "Sunken Ship Hidon's room left chest"
    HIDON_CHEST = "Sunken Ship Hidon's room right chest"
    HIDON_BOSS_FIGHT = "Mimic Chest #2 boss fight"
    HIDON_BOSS = "Mimic Chest #2 Star Piece"
    HIDON_REWARD_1 = "Mimic Chest #2 drop reward"
    HIDON_REWARD_2 = "Mimic Chest #2 reload reward"
    SUNKEN_SHIP_UNDERWATER_FROG_COIN_1 = (
        "Sunken Ship underwater freestanding frog coin 1"
    )
    SUNKEN_SHIP_UNDERWATER_FROG_COIN_2 = (
        "Sunken Ship underwater freestanding frog coin 2"
    )
    SUNKEN_SHIP_UNDERWATER_FROG_COIN_3 = (
        "Sunken Ship underwater freestanding frog coin 3"
    )
    SUNKEN_SHIP_UNDERWATER_FROG_COIN_4 = (
        "Sunken Ship underwater freestanding frog coin 4"
    )
    SUNKEN_SHIP_SAFETY_RING = "Sunken Ship hidden underwater room chest"
    SUNKEN_SHIP_BLOOBER_ROOM = "Sunken Ship large pool freestanding frog coin"
    SUNKEN_SHIP_BANDANA_REDS = "Sunken Ship near final boss chest"
    SUNKEN_SHIP_BOSS_FIGHT = "Sunken Ship exit boss fight"
    SUNKEN_SHIP_BOSS = "Sunken Ship exit boss Star Piece"
    SUNKEN_SHIP_POSTGAME_BOSS_FIGHT = "Sunken Ship postgame boss fight"
    SUNKEN_SHIP_POSTGAME_BOSS = "Sunken Ship postgame boss Star Piece"
    SUNKEN_SHIP_POSTGAME_DROP = "Sunken Ship postgame prize"
    LANDS_END_CLOUD_BOSS_FIGHT = "Land's End/Belome Temple cloud boss fight"
    LANDS_END_STAR_PIECE_1 = "Land's End/Belome Temple cloud Star Piece"
    LANDS_END_RED_ESSENCE = "Land's End first chest"
    LANDS_END_CHOW_PIT_1 = "Land's End chow pit left chest"
    LANDS_END_CHOW_PIT_2 = "Land's End chow pit right chest"
    LNDS_END_BEE_ROOM = "Land's End bee room chest"
    LANDS_END_CAVE_SIDE_REMAKE = "Land's End sky bridge freestanding item"
    LANDS_END_SECRET_1 = "Land's End grotto first chest"
    LANDS_END_SECRET_2 = "Land's End grotto corner chest"
    LANDS_END_SHY_AWAY = "Land's End grotto near sewer chest"
    LANDS_END_STAR_CHEST_1 = "Land's End whirlpool 1st underground chest"
    LANDS_END_STAR_CHEST_2 = "Land's End shaman 400 coin chest"
    LANDS_END_STAR_CHEST_3 = "Land's End shaman 800 coin chest"
    TROOPA_CLIMB = "Land's End Troopa Climb sub-12 second prize"
    BELOME_TEMPLE_FORTUNE_TELLER = "Belome Temple first fortune-telling room chest"
    BELOME_TEMPLE_FORTUNE_1 = "Belome Temple left-middle-right fortune chest"
    BELOME_TEMPLE_FORTUNE_2 = "Belome Temple left-right-middle fortune chest"
    BELOME_TEMPLE_FORTUNE_3 = "Belome Temple right-left-middle fortune chest"
    BELOME_TEMPLE_FORTUNE_4 = "Belome Temple right-middle-left fortune chest"
    BELOME_TEMPLE_AFTER_FORTUNE_1 = "Belome Temple after fortune area right chest"
    BELOME_TEMPLE_AFTER_FORTUNE_2 = "Belome Temple after fortune area lower left chest"
    BELOME_TEMPLE_AFTER_FORTUNE_3 = "Belome Temple after fortune area middle chest"
    BELOME_TEMPLE_AFTER_FORTUNE_4 = "Belome Temple after fortune area upper left chest"
    BELOME_TEMPLE_TREASURE_FLOWER_1 = "Belome Temple vault flower 1"
    BELOME_TEMPLE_TREASURE_FLOWER_2 = "Belome Temple vault flower 2"
    BELOME_TEMPLE_TREASURE_FLOWER_3 = "Belome Temple vault flower 3"
    BELOME_TEMPLE_TREASURE_FLOWER_4 = "Belome Temple vault flower 4"
    BELOME_TEMPLE_TREASURE_FROG_COIN_1 = "Belome Temple vault frog coin 1"
    BELOME_TEMPLE_TREASURE_FROG_COIN_2 = "Belome Temple vault frog coin 2"
    BELOME_TEMPLE_TREASURE_FROG_COIN_3 = "Belome Temple vault frog coin 3"
    BELOME_TEMPLE_TREASURE_FROG_COIN_4 = "Belome Temple vault frog coin 4"
    BELOME_TEMPLE_TREASURE_FROG_COIN_5 = "Belome Temple vault frog coin 5"
    BELOME_TEMPLE_TREASURE_FROG_COIN_6 = "Belome Temple vault frog coin 6"
    BELOME_TEMPLE_TREASURE_FROG_COIN_7 = "Belome Temple vault frog coin 7"
    BELOME_TEMPLE_TREASURE_FROG_COIN_8 = "Belome Temple vault frog coin 8"
    BELOME_TEMPLE_TREASURE_1 = "Belome Temple vault middle item bag"
    BELOME_TEMPLE_TREASURE_2 = "Belome Temple vault left item bag"
    BELOME_TEMPLE_TREASURE_3 = "Belome Temple vault right item bag"
    BELOME_TEMPLE_BOSS_FIGHT = "Belome Temple boss fight"
    BELOME_TEMPLE_BOSS = "Belome Temple boss Star Piece"
    BELOME_TEMPLE_BOSS_POSTGAME_FIGHT = "Belome Temple postgame boss fight"
    BELOME_TEMPLE_BOSS_POSTGAME = "Belome Temple postgame boss Star Piece"
    BELOME_TEMPLE_BOSS_POSTGAME_DROP = "Belome Temple postgame prize"
    MONSTRO_TOWN_ENTRANCE = "Monstro Town entrance chest"
    MONSTRO_TOWN_THWOMP = "Monstro Town thwomp key"
    DOJO_BOSS_1 = "Monstro Town dojo first fight Star Piece"
    DOJO_BOSS_2 = "Monstro Town dojo second fight Star Piece"
    DOJO_BOSS_3 = "Monstro Town dojo third fight Star Piece"
    DOJO_BOSS_4 = "Monstro Town dojo fourth fight Star Piece"
    DOJO_BOSS_FIGHT_1 = "Monstro Town dojo first fight"
    DOJO_BOSS_FIGHT_2 = "Monstro Town dojo second fight"
    DOJO_BOSS_FIGHT_3 = "Monstro Town dojo third fight"
    DOJO_BOSS_FIGHT_4 = "Monstro Town dojo fourth fight"
    JINX_DOJO_REWARD = "Monstro Town dojo prize"
    DOJO_BOSS_FIGHT_POSTGAME = "Monstro Town dojo postgame fight"
    DOJO_BOSS_POSTGAME = "Monstro Town dojo postgame Star Piece"
    DOJO_BOSS_POSTGAME_REWARD = "Monstro Town dojo postgame prize"
    CULEX_BOSS_FIGHT = "Monstro Town sealed door boss fight"
    CULEX_BOSS = "Monstro Town sealed door Star Piece"
    CULEX_REWARD = "Monstro Town sealed door prize"
    CULEX_POSTGAME_BOSS_FIGHT = "Monstro Town postgame sealed door boss fight"
    CULEX_POSTGAME_BOSS = "Monstro Town postgame sealed door Star Piece"
    CULEX_POSTGAME_REWARD = "Monstro Town postgame sealed door prize"
    SUPER_JUMPS_30 = "Monstro Town Super Jump first prize"
    SUPER_JUMPS_100 = "Monstro Town Super Jump second prize"
    THREE_MUSTY_FEARS = "Monstro Town flag exchange prize"
    BEAN_VALLEY_1 = "Bean Valley south upper level chest"
    BEAN_VALLEY_2 = "Bean Valley north upper level chest"
    BEAN_VALLEY_LEFT_PIRANHA_PIPE = "Bean Valley left piranha pipe chest"
    BEAN_VALLEY_BOTTOM_LEFT_PIRANHA_PIPE = "Bean Valley bottom left piranha pipe chest"
    BEAN_VALLEY_BOTTOM_RIGHT_PIRANHA_PIPE_UPPER = (
        "Bean Valley bottom right piranha pipe upper chest"
    )
    BEAN_VALLEY_BOTTOM_RIGHT_PIRANHA_PIPE_LOWER = (
        "Bean Valley bottom right piranha pipe lower chest"
    )
    BEAN_VALLEY_BOX_BOY_ROOM_1 = "Bean Valley right piranha pipe left chest"
    BOX_BOY_BOSS_FIGHT = "Mimic Chest #3 boss fight"
    BOX_BOY_BOSS = "Mimic Chest #3 Star Piece"
    BEAN_VALLEY_BOX_BOY_ROOM_2 = "Bean Valley right piranha pipe right chest"
    BEAN_VALLEY_BOX_BOY_ROOM_HIDDEN = (
        "Bean Valley right piranha pipe hidden stairway item"
    )
    BEAN_VALLEY_PIRANHA_PLANTS = "Bean Valley chest above Box Boy's room"
    BEAN_VALLEY_MEGASMILAX_ROOM = "Bean Valley boss reward"
    BEAN_VALLEY_BOSS_FIGHT = "Bean Valley boss fight"
    BEAN_VALLEY_BOSS = "Bean Valley boss Star Piece"
    BEAN_VALLEY_BEANSTALK = "Bean Valley clouds solo vine chest"
    BEAN_VALLEY_BEANSTALK_FROG_COIN = (
        "Bean Valley middle vine room freestanding frog coin"
    )
    BEAN_VALLEY_BEANSTALK_COIN_1 = (
        "Bean Valley middle vine room lowest freestanding coin"
    )
    BEAN_VALLEY_BEANSTALK_COIN_2 = (
        "Bean Valley middle vine room middle freestanding coin"
    )
    BEAN_VALLEY_BEANSTALK_COIN_3 = (
        "Bean Valley middle vine room highest freestanding coin"
    )
    BEAN_VALLEY_EAST_BEANSTALK_COIN_1 = (
        "Bean Valley east vine room lowest freestanding coin"
    )
    BEAN_VALLEY_EAST_BEANSTALK_COIN_2 = (
        "Bean Valley east vine room lower freestanding coin"
    )
    BEAN_VALLEY_EAST_BEANSTALK_COIN_3 = (
        "Bean Valley east vine room middle freestanding coin"
    )
    BEAN_VALLEY_EAST_BEANSTALK_COIN_4 = (
        "Bean Valley east vine room higher freestanding coin"
    )
    BEAN_VALLEY_EAST_BEANSTALK_COIN_5 = (
        "Bean Valley east vine room highest freestanding coin"
    )
    BEAN_VALLEY_WEST_BEANSTALK_COIN_1 = (
        "Bean Valley west vine room lower freestanding coin"
    )
    BEAN_VALLEY_WEST_BEANSTALK_COIN_2 = (
        "Bean Valley west vine room middle freestanding coin"
    )
    BEAN_VALLEY_WEST_BEANSTALK_COIN_3 = (
        "Bean Valley west vine room upper freestanding coin"
    )
    BEAN_VALLEY_WEST_BEANSTALK_FROG_COIN = (
        "Bean Valley west vine room freestanding frog coin"
    )
    BEAN_VALLEY_CLOUD_1 = "Bean Valley clouds upper left chest"
    BEAN_VALLEY_CLOUD_2 = "Bean Valley clouds upper right chest"
    BEAN_VALLEY_FALL_1 = "Bean Valley clouds lower left chest"
    BEAN_VALLEY_FALL_2 = "Bean Valley clouds lower right chest"
    BEAN_VALLEY_FIRST_VINE_ROOM_FROG_COIN = (
        "Bean Valley lowest vine room freestanding frog coin"
    )
    BEAN_VALLEY_FIRST_VINE_ROOM_MIDDLE_COIN = (
        "Bean Valley lowest vine room middle freestanding coin"
    )
    BEAN_VALLEY_FIRST_VINE_ROOM_UPPER_COIN = (
        "Bean Valley lowest vine room upper freestanding coin"
    )
    BEAN_VALLEY_FIRST_VINE_ROOM_LOWER_COIN = (
        "Bean Valley lowest vine room lower freestanding coin"
    )
    CASINO_GRATE_GUY_PRIZE = "Grate Guy's Casino LOTW prize"
    NIMBUS_LAND_SHOP = "Nimbus Land shop chest"
    NIMBUS_LAND_INN = "Nimbus Land dream cushion 1st item"
    NIMBUS_LAND_INN_2 = "Nimbus Land dream cushion 2nd item"
    NIMBUS_LAND_GARRO = "Nimbus Land Garro check"
    NIMBUS_LAND_STATUE_BOSS_FIGHT = "Nimbus Castle statue keeper boss fight"
    NIMBUS_LAND_STAR_PIECE_1 = "Nimbus Castle statue keeper boss Star Piece"
    DODO_REWARD = "Nimbus Castle statue game prize"
    NIMBUS_LAND_BEFORE_BIRDETTA_2 = "Nimbus Castle west two-level room chest"
    NIMBUS_CASTLE_SINGLE_GOLD_BIRD = "Nimbus Castle single gold bird room chest"
    NIMBUS_CASTLE_OUT_OF_BOUNDS_1 = "Nimbus Castle west stairway room left chest"
    NIMBUS_CASTLE_OUT_OF_BOUNDS_2 = "Nimbus Castle west stairway room right chest"
    NIMBUS_LAND_PRISONERS = "Nimbus Castle west cellar civilian"
    NIMBUS_LAND_PRISONERS_2 = "Nimbus Castle west cellar guard"
    NIMBUS_CASTLE_EGG_BOSS_FIGHT = "Nimbus Castle giant egg boss fight"
    NIMBUS_CASTLE_STAR_PIECE_2 = "Nimbus Castle giant egg boss Star Piece"
    NIMBUS_CASTLE_BIRDETTA = "Nimbus Castle giant egg prize"
    NIMBUS_CASTLE_AFTER_EGG_1 = "Nimbus Castle east two-level room lower chest"
    NIMBUS_CASTLE_AFTER_EGG_2 = "Nimbus Castle east two-level room upper chest"
    NIMBUS_CASTLE_FINAL_BOSS_FIGHT = "Nimbus Land final boss fight"
    NIMBUS_CASTLE_STAR_PIECE_3 = "Nimbus Land final boss Star Piece"
    NIMBUS_CASTLE_STAR_CHEST = "Nimbus Castle post-throne chest (occupied)"
    NIMBUS_CASTLE_STAR_AFTER_VALENTINA = "Nimbus Castle post-throne chest (liberated)"
    NIMBUS_CASTLE_BUSINESS_CENTRE = "Nimbus Castle 5-exit room chest (occupied)"
    NIMBUS_CASTLE_CORNER_CHEST_AFTER_VALENTINA = (
        "Nimbus Castle 5-exit room chest (liberated)"
    )
    NIMBUS_LAND_RIGHT_SIDE = "Nimbus Land post-invasion off-cloud item"
    NIMBUS_LAND_SIGNAL_RING = "Nimbus Land post-invasion upper right house"
    NIMBUS_LAND_CELLAR = "Nimbus Castle post-invasion north cellar"
    BARREL_VOLCANO_SECRET_1 = "Barrel Volcano early secret room left chest"
    BARREL_VOLCANO_SECRET_2 = "Barrel Volcano early secret room right chest"
    BARREL_VOLCANO_REVERSE = "Barrel Volcano reverse lava recoil frog coin"
    BARREL_VOLCANO_DONUT_1 = (
        "Barrel Volcano first donut lift room right freestanding frog coin"
    )
    BARREL_VOLCANO_DONUT_2 = (
        "Barrel Volcano first donut lift room left freestanding frog coin"
    )
    BARREL_VOLCANO_LAVA_POOL = "Barrel Volcano lava pool freestanding frog coin"
    BARREL_VOLCANO_BEFORE_STAR_1 = "Barrel Volcano second arrow sign room left chest"
    BARREL_VOLCANO_BEFORE_STAR_2 = "Barrel Volcano second arrow sign room right chest"
    BARREL_VOLCANO_STAR_ROOM = "Barrel Volcano star chest"
    BARREL_VOLCANO_SAVE_ROOM_1 = "Barrel Volcano save room lower chest"
    BARREL_VOLCANO_SAVE_ROOM_2 = "Barrel Volcano save room upper chest"
    BARREL_VOLCANO_HINOPIO = "Barrel Volcano Hinopio shop chest"
    BARREL_VOLCANO_BOSS_FIGHT_1 = "Barrel Volcano first boss fight"
    BARREL_VOLCANO_BOSS_1 = "Barrel Volcano first boss Star Piece"
    BARREL_VOLCANO_BOSS_FIGHT_2 = "Barrel Volcano second boss fight"
    BARREL_VOLCANO_BOSS_2 = "Barrel Volcano second boss Star Piece"
    BOWSERS_KEEP_DARK_ROOM = "Bowser's Keep dark room chest"
    BOWSERS_KEEP_CROCO_SHOP_1 = "Bowser's Keep near first shop left chest"
    BOWSERS_KEEP_CROCO_SHOP_2 = "Bowser's Keep near first shop right chest"
    BOWSERS_KEEP_MAGIKOOPA = "Bowser's Keep Magikoopa's room chest"
    BOWSERS_KEEP_BOSS_FIGHT_CHESTER = "Bowser's Keep battle door final fight"
    BOWSERS_KEEP_BOSS_CHESTER = "Bowser's Keep battle door Star Piece"
    BOWSERS_KEEP_INVISIBLE_BRIDGE_1 = (
        "Bowser's Keep 6-door invisble bridge bottom chest"
    )
    BOWSERS_KEEP_INVISIBLE_BRIDGE_2 = "Bowser's Keep 6-door invisble bridge right chest"
    BOWSERS_KEEP_INVISIBLE_BRIDGE_3 = "Bowser's Keep 6-door invisble bridge left chest"
    BOWSERS_KEEP_INVISIBLE_BRIDGE_4 = "Bowser's Keep 6-door invisble bridge top chest"
    BOWSERS_KEEP_INVISIBLE_BRIDGE_COIN_1 = (
        "Bowser's Keep 6-door invisble bridge bottom left coin"
    )
    BOWSERS_KEEP_INVISIBLE_BRIDGE_COIN_2 = (
        "Bowser's Keep 6-door invisble bridge bottom right coin"
    )
    BOWSERS_KEEP_INVISIBLE_BRIDGE_COIN_3 = (
        "Bowser's Keep 6-door invisble bridge top left coin"
    )
    BOWSERS_KEEP_INVISIBLE_BRIDGE_COIN_4 = (
        "Bowser's Keep 6-door invisble bridge top right coin"
    )
    BOWSERS_KEEP_MOVING_PLATFORMS_1 = "Bowser's Keep X-Y platform room left exit chest"
    BOWSERS_KEEP_MOVING_PLATFORMS_2 = (
        "Bowser's Keep X-Y platform room left entrance chest"
    )
    BOWSERS_KEEP_MOVING_PLATFORMS_3 = (
        "Bowser's Keep X-Y platform room right entrance chest"
    )
    BOWSERS_KEEP_MOVING_PLATFORMS_4 = "Bowser's Keep X-Y platform room right exit chest"
    BOWSERS_KEEP_ELEVATOR_PLATFORMS = (
        "Bowser's Keep 6-door elevator platform room chest"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_1 = "Bowser's Keep cannonball room lower right chest"
    BOWSERS_KEEP_CANNONBALL_ROOM_2 = "Bowser's Keep cannonball room exit chest"
    BOWSERS_KEEP_CANNONBALL_ROOM_3 = "Bowser's Keep cannonball room lower left chest"
    BOWSERS_KEEP_CANNONBALL_ROOM_4 = "Bowser's Keep cannonball room upper right chest"
    BOWSERS_KEEP_CANNONBALL_ROOM_5 = "Bowser's Keep cannonball room upper left chest"
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_1 = (
        "Bowser's Keep cannonball room freestanding coin 1"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_2 = (
        "Bowser's Keep cannonball room freestanding coin 2"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_3 = (
        "Bowser's Keep cannonball room freestanding coin 3"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_4 = (
        "Bowser's Keep cannonball room freestanding coin 4"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_5 = (
        "Bowser's Keep cannonball room freestanding coin 5"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_6 = (
        "Bowser's Keep cannonball room freestanding coin 6"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_7 = (
        "Bowser's Keep cannonball room freestanding coin 7"
    )
    BOWSERS_KEEP_CANNONBALL_ROOM_COIN_8 = (
        "Bowser's Keep cannonball room freestanding coin 8"
    )
    BOWSERS_KEEP_ROTATING_PLATFORMS_1 = (
        "Bowser's Keep rotating platform room entrance chest"
    )
    BOWSERS_KEEP_ROTATING_PLATFORMS_2 = (
        "Bowser's Keep rotating platform lower left chest"
    )
    BOWSERS_KEEP_ROTATING_PLATFORMS_3 = "Bowser's Keep rotating platform right chest"
    BOWSERS_KEEP_ROTATING_PLATFORMS_4 = "Bowser's Keep rotating platform center chest"
    BOWSERS_KEEP_ROTATING_PLATFORMS_5 = (
        "Bowser's Keep rotating platform upper left chest"
    )
    BOWSERS_KEEP_ROTATING_PLATFORMS_6 = "Bowser's Keep rotating platform exit chest"
    BOWSERS_KEEP_DOOR_REWARD_1 = "Bowser's Keep door prize 1"
    BOWSERS_KEEP_DOOR_REWARD_2 = "Bowser's Keep door prize 2"
    BOWSERS_KEEP_DOOR_REWARD_3 = "Bowser's Keep door prize 3"
    BOWSERS_KEEP_DOOR_REWARD_4 = "Bowser's Keep door prize 4"
    BOWSERS_KEEP_DOOR_REWARD_5 = "Bowser's Keep door prize 5"
    BOWSERS_KEEP_DOOR_REWARD_6 = "Bowser's Keep door prize 6"
    BOWSERS_KEEP_BOSS_FIGHT_1 = "Bowser's Keep first boss after red doors fight"
    BOWSERS_KEEP_BOSS_1 = "Bowser's Keep first boss after red doors Star Piece"
    BOWSERS_KEEP_BOSS_FIGHT_2 = "Bowser's Keep second boss after red doors fight"
    BOWSERS_KEEP_BOSS_2 = "Bowser's Keep second boss after red doors Star Piece"
    BOWSERS_KEEP_BOSS_FIGHT_3 = "Bowser's Keep third boss after red doors fight"
    BOWSERS_KEEP_BOSS_3 = "Bowser's Keep third boss after red doors Star Piece"
    FACTORY_SAVE_ROOM = "Outer Factory early save room chest"
    FACTORY_BOLT_PLATFORMS = "Outer Factory bolt platform chest"
    FACTORY_BOSS_FIGHT_1 = "Outer Factory first boss fight"
    FACTORY_BOSS_1 = "Outer Factory first boss Star Piece"
    FACTORY_FALLING_AXEMS = "Outer Factory falling axem room chest"
    FACTORY_TREASURE_PIT_1 = "Outer Factory pit back chest"
    FACTORY_TREASURE_PIT_2 = "Outer Factory pit front chest"
    FACTORY_CONVEYOR_PLATFORMS_1 = "Outer Factory conveyor room right chest"
    FACTORY_CONVEYOR_PLATFORMS_2 = "Outer Factory conveyor room left chest"
    FACTORY_BEHIND_SNAKES_1 = "Outer Factory room behind machine yarid right chest"
    FACTORY_BEHIND_SNAKES_2 = "Outer Factory room behind machine yarid left chest"
    FACTORY_BOSS_FIGHT_2 = "Outer Factory second boss fight"
    FACTORY_BOSS_2 = "Outer Factory second boss Star Piece"
    FACTORY_TOAD_GIFT = "Inner Factory toad gift"
    INNER_FACTORY_BOSS_FIGHT_1 = "Inner Factory first boss fight"
    INNER_FACTORY_BOSS_1 = "Inner Factory first boss Star Piece"
    INNER_FACTORY_BOSS_FIGHT_2 = "Inner Factory second boss fight"
    INNER_FACTORY_BOSS_2 = "Inner Factory second boss Star Piece"
    INNER_FACTORY_BOSS_FIGHT_3 = "Inner Factory third boss fight"
    INNER_FACTORY_BOSS_3 = "Inner Factory third boss Star Piece"
    INNER_FACTORY_BOSS_FIGHT_4 = "Inner Factory fourth boss fight"
    INNER_FACTORY_BOSS_4 = "Inner Factory fourth boss Star Piece"
    INNER_FACTORY_BOSS_FIGHT_FINAL = "Factory final boss fight"
    INNER_FACTORY_BOSS_FINAL = "Factory final boss Star Piece"
    # Three Musty Fears proxy entries (represent the 3 randomly-selected invisible flag locations)
    THREE_MUSTY_FEARS_BONES = "Dry Bones' invisible item (Three Musty Fears)"
    THREE_MUSTY_FEARS_GREAPER = "Greaper's invisible item (Three Musty Fears)"
    THREE_MUSTY_FEARS_BOO = "Big Boo's invisible item (Three Musty Fears)"


class WorldAreaEnum(StrEnum):
    MARIOS_PAD = "Mario's Pad"
    MUSHROOM_WAY = "Mushroom Way"
    MUSHROOM_KINGDOM = "Mushroom Kingdom"
    BANDITS_WAY = "Bandit's Way"
    KERO_SEWERS = "Kero Sewers"
    MIDAS_RIVER = "Midas River"
    TADPOLE_POND = "Tadpole Pond"
    ROSE_WAY = "Rose Way"
    ROSE_TOWN = "Rose Town"
    FOREST_MAZE = "Forest Maze"
    PIPE_VAULT = "Pipe Vault"
    YOSTER_ISLE = "Yoster Isle"
    MOLEVILLE = "Moleville"
    BOOSTER_PASS = "Booster Pass"
    BOOSTER_TOWER = "Booster Tower"
    BOOSTER_HILL = "Booster Hill"
    MARRYMORE = "Marrymore"
    STAR_HILL = "Star Hill"
    SEASIDE_TOWN = "Seaside Town"
    SEA = "Sea"
    SUNKEN_SHIP = "Sunken Ship"
    LANDS_END = "Land's End"
    TEMPLE = "Belome Temple"
    MONSTRO_TOWN = "Monstro Town"
    BEAN_VALLEY = "Bean Valley"
    CASINO = "Grate Guy's Casino"
    NIMBUS_LAND = "Nimbus Land"
    BARREL_VOLCANO = "Barrel Volcano"
    BOWSERS_KEEP = "Bowser's Keep"
    FACTORY = "Factory"
    INNER_FACTORY = "Inner Factory"


SIGNAL_RING_EVENT_DICT: dict[WorldAreaEnum, int] = {
    WorldAreaEnum.MARIOS_PAD: E3887_MARIOS_PAD_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MUSHROOM_WAY: E3888_MUSHROOM_WAY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MUSHROOM_KINGDOM: E3889_MUSHROOM_KINGDOM_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BANDITS_WAY: E3890_BANDITS_WAY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.KERO_SEWERS: E3891_SEWERS_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MIDAS_RIVER: E3892_MIDAS_RIVER_STAR_PIECE_SIGNAL,
    WorldAreaEnum.TADPOLE_POND: E3893_TADPOLE_POND_STAR_PIECE_SIGNAL,
    WorldAreaEnum.ROSE_WAY: E3894_ROSE_WAY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.ROSE_TOWN: E3895_ROSE_TOWN_STAR_PIECE_SIGNAL,
    WorldAreaEnum.FOREST_MAZE: E3896_FOREST_MAZE_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MOLEVILLE: E3897_MOLEVILLE_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BOOSTER_PASS: E3898_BOOSTER_PASS_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BOOSTER_TOWER: E3899_BOOSTER_TOWER_STAR_PIECE_SIGNAL,
    WorldAreaEnum.PIPE_VAULT: E3900_PIPE_VAULT_STAR_PIECE_SIGNAL,
    WorldAreaEnum.YOSTER_ISLE: E3901_YOSTER_ISLE_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MARRYMORE: E3902_MARRYMORE_STAR_PIECE_SIGNAL,
    WorldAreaEnum.STAR_HILL: E3903_STAR_HILL_STAR_PIECE_SIGNAL,
    WorldAreaEnum.SEASIDE_TOWN: E3904_SEASIDE_TOWN_STAR_PIECE_SIGNAL,
    WorldAreaEnum.SEA: E3905_SEA_STAR_PIECE_SIGNAL,
    WorldAreaEnum.SUNKEN_SHIP: E3906_SHIP_STAR_PIECE_SIGNAL,
    WorldAreaEnum.LANDS_END: E3907_LANDS_END_STAR_PIECE_SIGNAL,
    WorldAreaEnum.TEMPLE: E3908_TEMPLE_STAR_PIECE_SIGNAL,
    WorldAreaEnum.MONSTRO_TOWN: E3909_MONSTRO_STAR_PIECE_SIGNAL,
    WorldAreaEnum.CASINO: E3910_CASINO_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BEAN_VALLEY: E3911_BEAN_VALLEY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.NIMBUS_LAND: E3912_NIMBUS_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BARREL_VOLCANO: E3913_VOLCANO_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BOWSERS_KEEP: E3914_KEEP_STAR_PIECE_SIGNAL,
    WorldAreaEnum.FACTORY: E3915_FACTORY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.INNER_FACTORY: E3916_INNER_FACTORY_STAR_PIECE_SIGNAL,
    WorldAreaEnum.BOOSTER_HILL: E3842_BOOSTER_HILL_STAR_PIECE_SIGNAL,
}


class OverworldMapRegion(StrEnum):
    WORLD_1 = "World 1"
    WORLD_2 = "World 2"
    WORLD_3 = "World 3"
    WORLD_4 = "World 4"
    WORLD_5 = "World 5"
    WORLD_6 = "World 6"
    WORLD_7 = "World 7"


_VANILLA_SPELL_OWNER_MAP: dict[type[SpellPrize], type[CharacterPrize]] | None = None


def vanilla_spell_owner(spell_prize: type[SpellPrize]) -> type[CharacterPrize] | None:
    """Return the character who learns spell_prize in the vanilla game.

    Used by SpellsAnywhere placement when learned-spell randomization
    (CharacterLearnedSpells) is disabled, so a spell found in the world is
    granted to its original owner instead of a random character. The mapping is
    derived from the spell-slot locations' _originally_held values, which are
    the canonical definition of vanilla spell ownership.
    """
    global _VANILLA_SPELL_OWNER_MAP
    if _VANILLA_SPELL_OWNER_MAP is None:
        from randomizer.logic.progression.prizes import (
            MarioRecruitmentPrize,
            ToadstoolRecruitmentPrize,
            BowserRecruitmentPrize,
            GenoRecruitmentPrize,
            MallowRecruitmentPrize,
        )
        from randomizer.logic.progression.prizelocations import (
            MarioSpell1, MarioSpell2, MarioSpell3, MarioSpell4, MarioSpell5, MarioSpell6,
            ToadstoolSpell1, ToadstoolSpell2, ToadstoolSpell3, ToadstoolSpell4, ToadstoolSpell5, ToadstoolSpell6,
            BowserSpell1, BowserSpell2, BowserSpell3, BowserSpell4, BowserSpell5, BowserSpell6,
            GenoSpell1, GenoSpell2, GenoSpell3, GenoSpell4, GenoSpell5, GenoSpell6,
            MallowSpell1, MallowSpell2, MallowSpell3, MallowSpell4, MallowSpell5, MallowSpell6,
        )

        groups: list[tuple[type[CharacterPrize], list[type[SpellSlotLocation]]]] = [
            (MarioRecruitmentPrize, [MarioSpell1, MarioSpell2, MarioSpell3, MarioSpell4, MarioSpell5, MarioSpell6]),
            (ToadstoolRecruitmentPrize, [ToadstoolSpell1, ToadstoolSpell2, ToadstoolSpell3, ToadstoolSpell4, ToadstoolSpell5, ToadstoolSpell6]),
            (BowserRecruitmentPrize, [BowserSpell1, BowserSpell2, BowserSpell3, BowserSpell4, BowserSpell5, BowserSpell6]),
            (GenoRecruitmentPrize, [GenoSpell1, GenoSpell2, GenoSpell3, GenoSpell4, GenoSpell5, GenoSpell6]),
            (MallowRecruitmentPrize, [MallowSpell1, MallowSpell2, MallowSpell3, MallowSpell4, MallowSpell5, MallowSpell6]),
        ]
        mapping: dict[type[SpellPrize], type[CharacterPrize]] = {}
        for char_prize, slot_locations in groups:
            for slot_location in slot_locations:
                held = slot_location._originally_held
                if held is not None:
                    mapping[held] = char_prize
        _VANILLA_SPELL_OWNER_MAP = mapping
    return _VANILLA_SPELL_OWNER_MAP.get(spell_prize)


class PrizeLocation(Generic[TOriginallyHeld]):
    _prize: Prize | None
    _originally_held: TOriginallyHeld
    _can_accept: list[type[Prize]]
    _rooms: list[int]
    _id: ShuffleLocationSelector
    _remake_only: bool = False
    _blacklist: list[type[Prize]] | None = None
    _model_allowlist: list[type[ItemNPC]] | None = None
    _override_id: int | None = None
    _can_be_empty: bool = False
    _bias: bool = False
    _monstro_shuffle: bool = False
    _hint: list[UsableEventScriptCommand] | None = None
    _access_conditions: str = ""

    def __repr__(self) -> str:
        prize_name = type(self._prize).__name__ if self._prize else "None"
        return f"{self.__class__.__name__}(prize={prize_name})"

    def hint(self, world: GameWorld) -> list[UsableEventScriptCommand]:
        return self._hint or []

    @property
    def access_conditions(self) -> str:
        """Optional prose describing what's needed to reach this check.

        Purely documentation: rendered in the List of Checks resource page and
        read nowhere else. Unrelated to _hint, which is in-game event script.
        Empty means nobody has written it yet.
        """
        return self._access_conditions

    @property
    def has_item(self) -> bool:
        return self._prize is not None

    @property
    def monstro_shuffle(self) -> bool:
        return self._monstro_shuffle

    _world_area: WorldAreaEnum

    def can_be_empty(self, world: GameWorld) -> bool:
        return self._can_be_empty

    @property
    def battlefields(self) -> list[Battlefield]:
        return [
            ROOM_TO_BATTLEFIELD[room]
            for room in self._rooms
            if room in ROOM_TO_BATTLEFIELD
        ]

    @property
    def world_area(self) -> WorldAreaEnum:
        return self._world_area

    @property
    def overworld_map_region(self) -> OverworldMapRegion:
        if self.world_area in [
            WorldAreaEnum.MARIOS_PAD,
            WorldAreaEnum.MUSHROOM_WAY,
            WorldAreaEnum.MUSHROOM_KINGDOM,
            WorldAreaEnum.BANDITS_WAY,
        ]:
            return OverworldMapRegion.WORLD_1
        elif self.world_area in [
            WorldAreaEnum.KERO_SEWERS,
            WorldAreaEnum.MIDAS_RIVER,
            WorldAreaEnum.TADPOLE_POND,
            WorldAreaEnum.ROSE_WAY,
            WorldAreaEnum.ROSE_TOWN,
            WorldAreaEnum.FOREST_MAZE,
            WorldAreaEnum.PIPE_VAULT,
            WorldAreaEnum.YOSTER_ISLE,
        ]:
            return OverworldMapRegion.WORLD_2
        elif self.world_area in [
            WorldAreaEnum.MOLEVILLE,
            WorldAreaEnum.BOOSTER_PASS,
            WorldAreaEnum.BOOSTER_TOWER,
            WorldAreaEnum.BOOSTER_HILL,
            WorldAreaEnum.MARRYMORE,
        ]:
            return OverworldMapRegion.WORLD_3
        elif self.world_area in [
            WorldAreaEnum.STAR_HILL,
            WorldAreaEnum.SEASIDE_TOWN,
            WorldAreaEnum.SEA,
            WorldAreaEnum.SUNKEN_SHIP,
        ]:
            return OverworldMapRegion.WORLD_4
        elif self.world_area in [
            WorldAreaEnum.LANDS_END,
            WorldAreaEnum.TEMPLE,
            WorldAreaEnum.MONSTRO_TOWN,
            WorldAreaEnum.CASINO,
            WorldAreaEnum.BEAN_VALLEY,
        ]:
            return OverworldMapRegion.WORLD_5
        elif self.world_area in [
            WorldAreaEnum.NIMBUS_LAND,
            WorldAreaEnum.BARREL_VOLCANO,
        ]:
            return OverworldMapRegion.WORLD_6
        return OverworldMapRegion.WORLD_7

    @property
    def override_id(self) -> int | None:
        return self._override_id

    @property
    def id(self) -> ShuffleLocationSelector:
        return self._id

    def set_prize(self, prize: Prize | None):
        self._prize = prize

    @property
    def prize(self) -> Prize | None:
        return self._prize

    @property
    def originally_held(self) -> type[Prize] | None:
        return self._originally_held

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        if self._blacklist and isinstance(prize, tuple(self._blacklist)):
            return False

        if isinstance(prize, StarPiecePrize) and world.settings.isflag_enabled(
            DisperseStarPieces
        ):
            # one star piece per OW region. Scan ALL locations, not just
            # world.star_piece_locations: StarPieceAvailability (stars_anywhere)
            # lets pieces land in standard chest/event locations that aren't in
            # that list, and those must still count toward the per-region limit.
            for l in world.locations.values():
                if l is not self and isinstance(l.prize, StarPiecePrize):
                    if l.overworld_map_region == self.overworld_map_region:
                        return False
        if isinstance(prize, EXPStarPrize):
            # one EXP star per locale
            for l in world.chest_locations:
                if l is not self and isinstance(l.prize, EXPStarPrize):
                    if l.world_area == self.world_area:
                        return False
        if isinstance(prize, SlotsPrize):
            if world._slot_dummy_indices is not None:
                for r in self._rooms:
                    if r not in world._slot_dummy_indices:
                        return False
            for l in world.chest_locations:
                if l is not self and isinstance(l.prize, SlotsPrize):
                    # Never have two slot machines in the same room
                    for r in l._rooms:
                        if r in self._rooms:
                            return False
        if isinstance(prize, SpellPrize):
    
            if world.settings.isflag_enabled(SpellsAnywhere):
                # Dynamic assignment mode: assign a character BEFORE placement
                # Get all recruited character types from inventory
                recruited_chars = list(
                    dict.fromkeys(
                        type(item)
                        for item in inventory
                        if isinstance(item, CharacterPrize)
                    )
                )

                # Fallback: if no characters in inventory, check character locations directly
                # This handles edge cases where inventory might not include characters yet
                if not recruited_chars:
                    for loc in world.locations.values():
                        if (
                            isinstance(loc, StartingCharacterLocation)
                            and loc.has_item
                            and isinstance(loc.prize, CharacterPrize)
                        ):
                            recruited_chars.append(type(loc.prize))
                    # Check character recruitment locations
                    for loc in world.locations.values():
                        if (
                            isinstance(loc, CharacterRecruitmentLocation)
                            and loc.has_item
                        ):
                            if isinstance(loc.prize, CharacterPrize):
                                recruited_chars.append(type(loc.prize))
                    # Deduplicate, preserving order. set() of classes iterates by
                    # id() and so varies between processes; random.choice below
                    # reads this order, which would make placement itself differ
                    # from run to run for the same seed.
                    recruited_chars = list(dict.fromkeys(recruited_chars))

                if not recruited_chars:
                    return False

                # Initialize spell assignments if needed
                if world._spell_assignments is None:
                    world._spell_assignments = {}

                # Find characters with <6 spells assigned
                available_chars = [
                    char_type
                    for char_type in recruited_chars
                    if world._spell_assignments.get(char_type, 0) < 6
                ]

                if not available_chars:
                    return False

                # Assign a character to this spell if not already assigned.
                # Note: count is NOT incremented here - it's done in _on_item_placed
                # when actually placed, because can_accept is called multiple times
                # (once per potential location).
                if prize.character is None:
            
                    if world.settings.isflag_enabled(CharacterLearnedSpells):
                        # Learned spells are randomized: distribute spells across
                        # the recruited characters that still have room.

                        selected_char = _random.choice(available_chars)
                        prize.set_character(selected_char)
                    else:
                        # Learned spells are vanilla: each spell is granted to the
                        # character who learns it in the original game.
                        owner = vanilla_spell_owner(type(prize))
                        if owner not in available_chars:
                            return False
                        prize.set_character(owner)
                return True
            else:
                return isinstance(self, SpellSlotLocation)
        if world.settings.isflag_enabled(RestrictSpecialEquips):
            if self.monstro_shuffle:
                return isinstance(prize, ItemPrize) and prize._monstro_shuffle
            else:
                return not (isinstance(prize, ItemPrize) and prize._monstro_shuffle)
        return True

    def can_access(self, inventory: Inventory, world: GameWorld) -> bool:
        return True

    def grant(self, world: GameWorld | None = None) -> EventScript:
        return EventScript([Return()])

    @property
    def remake_only(self) -> bool:
        return self._remake_only

    def __init__(self):
        self._prize = (
            self.originally_held() if self.originally_held is not None else None
        )


class StandardPrizeLocation(PrizeLocation):
    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:

        # Check if this location is disabled for progression items
        # This includes key items, star pieces, mimic launchers, and fireworks
        if isinstance(
            prize,
            (KeyPrize, StarPiecePrize, MimicFightInitiatorPrize, RegularFireworksPrize),
        ):
            enabled_check = cast(CategorizationFlag, world.settings.get_flag_by_id("chests"))
            for m in enabled_check.disabled:
                if self.__class__ == m.value:
                    return False

        if isinstance(prize, KeyPrize) and not world.settings.isflag_enabled(
            KeyItemsAnywhere
        ):
            if isinstance(self, KeyItemLocation):
                return super().can_accept(prize, inventory, world)
            return False
        elif isinstance(prize, StarPiecePrize) and not world.settings.isflag_enabled(
            StarPieceAvailability
        ):
            return False
        else:
            return super().can_accept(prize, inventory, world)


class FrogDiscipleLocation(PrizeLocation):
    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        if prize is None:
            return False
        if not isinstance(prize, ItemPrize):
            return False
        if not super().can_accept(prize, inventory, world):
            return False
        return world.get_item(prize.item).price > 0  # type: ignore


class TreasureChestLocation(StandardPrizeLocation):
    _npc_ids: list[AreaObject]
    _set_extra_bits_when_opened: list[Flag] | None = None

    @property
    def set_extra_bits_when_opened(self) -> list[Flag]:
        return self._set_extra_bits_when_opened if self._set_extra_bits_when_opened is not None else []

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "chest_grant")
            and prize.chest_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def grant(self, world: GameWorld | None = None) -> EventScript:
        from randomizer.logic.progression.prizelocations import (
            KeroSewersBeforeBelomeUpperBeforeFlipLocation,
            Mimic1ReloadRewardLocation,
            Mimic2ReloadRewardLocation,
        )

        if self.prize is None:
            return EventScript([Return()])
        itemgrant = (
            [] if self.prize.chest_grant is None else self.prize.chest_grant.contents
        )
        if (
            self._model_allowlist is not None
            and isinstance(self.prize, ItemPrize)
            and self.prize.model is not None
            and not issubclass(self.prize.model, tuple(self._model_allowlist))
        ):
            itemgrant = [
                (
                    cmd
                    if not isinstance(cmd, JmpToEvent)
                    else JmpToEvent(DefaultItem._chest_event_id)
                )
                for cmd in itemgrant
            ]
        extra_itemgrant = []
        if not isinstance(self.prize, (InfiniteCoinsPrize)):
            extra_itemgrant = extra_itemgrant + [
                *[DisableObjectTriggerInSpecificLevel(ao, room) for ao, room in zip([npc if isinstance(npc, AreaObject) else AreaObject(npc + 14) for npc in self._npc_ids], self._rooms)],
                *[SetBit(bit) for bit in (self.set_extra_bits_when_opened or [])]
            ] 
            
        # Account for mimic chests needing to be opened twice, but only when the reload
        # check actually holds a prize - if it's empty, disable the chest on the first open.
        # world is None only from structural tests: keep the two-open behaviour there.
        if isinstance(self.prize, (FirstMimicFightLauncher)):
            if not ((world is None or (world.locations[Mimic1ReloadRewardLocation].prize is None)) and not world.settings.isflag_enabled(AnnoyingChests)):
                extra_itemgrant.insert(0, JmpIfBitClear(MIMIC_1_CLEARED, [itemgrant[0].identifier.label]))
        elif isinstance(self.prize, (SecondMimicFightLauncher)):
            if not ((world is None or (world.locations[Mimic2ReloadRewardLocation].prize is None)) and not world.settings.isflag_enabled(AnnoyingChests)):
                extra_itemgrant.insert(0, JmpIfBitClear(MIMIC_2_CLEARED, [itemgrant[0].identifier.label]))

        itemgrant = extra_itemgrant + itemgrant
        return EventScript(itemgrant)

    def render(self, world: GameWorld) -> None:
        if isinstance(self.prize, SlotsPrize):
            world.event_scripts.get_script_by_id(self.prize.logic_event).set_contents(
                create_slot_machine_script(self, world)
            )
            assert world._slot_dummy_indices is not None
            for r in self._rooms:
                room = world.rooms._rooms[r]
                if room is None:
                    raise ValueError(
                        f"Room ID {r} not found in world while creating slot machine script."
                    )
                start = world._slot_dummy_indices[r]
                room._objects[start] = RegularNPC(
                    npc=FLOWER_NPC_2,
                    initiator=EventInitiator.NONE,
                    event_script=E2304_BANK_1F_RETURN_EVENT_2,
                    action_script=A0015_DO_NOTHING,
                    visible=False,
                    x=26,
                    y=108,
                    z=5,
                    z_half=False,
                    direction=SOUTHWEST,
                    face_on_trigger=False,
                    cant_enter_doors=False,
                    byte2_bit5=False,
                    set_sequence_playback=True,
                    cant_float=False,
                    cant_walk_up_stairs=False,
                    cant_walk_under=False,
                    cant_pass_walls=False,
                    cant_jump_through=False,
                    cant_pass_npcs=False,
                    byte3_bit5=False,
                    cant_walk_through=False,
                    byte3_bit7=False,
                    slidable_along_walls=True,
                    cant_move_if_in_air=True,
                    byte7_upper2=3,
                )
                room._objects[start + 1] = RegularClone(
                    npc=FLOWER_NPC_2,
                    event_script=E2304_BANK_1F_RETURN_EVENT_2,
                    action_script=A0015_DO_NOTHING,
                    visible=False,
                    x=26,
                    y=108,
                    z=5,
                    z_half=False,
                    direction=SOUTHWEST,
                )
                room._objects[start + 2] = RegularClone(
                    npc=FLOWER_NPC_2,
                    event_script=E2304_BANK_1F_RETURN_EVENT_2,
                    action_script=A0015_DO_NOTHING,
                    visible=False,
                    x=26,
                    y=108,
                    z=5,
                    z_half=False,
                    direction=SOUTHWEST,
                )
                room._objects[start + 3] = RegularNPC(
                    npc=EMPTY_NPC_3,
                    initiator=EventInitiator.NONE,
                    event_script=E2304_BANK_1F_RETURN_EVENT_2,
                    action_script=A0015_DO_NOTHING,
                    visible=False,
                    x=26,
                    y=108,
                    z=5,
                    z_half=False,
                    direction=NORTHWEST,
                    face_on_trigger=False,
                    cant_enter_doors=False,
                    byte2_bit5=False,
                    set_sequence_playback=True,
                    cant_float=False,
                    cant_walk_up_stairs=False,
                    cant_walk_under=False,
                    cant_pass_walls=False,
                    cant_jump_through=False,
                    cant_pass_npcs=False,
                    byte3_bit5=False,
                    cant_walk_through=False,
                    byte3_bit7=False,
                    slidable_along_walls=True,
                    cant_move_if_in_air=True,
                    byte7_upper2=3,
                    cannot_clone=False
                )
                room._objects[start + 4] = RegularNPC(
                    npc=EXPLOSION_NPC,
                    initiator=EventInitiator.NONE,
                    event_script=E2304_BANK_1F_RETURN_EVENT_2,
                    action_script=A0400_SEQUENCE_LOOPING_ON,
                    speed=5,
                    visible=False,
                    x=26,
                    y=108,
                    z=5,
                    z_half=False,
                    direction=NORTHWEST,
                    face_on_trigger=False,
                    cant_enter_doors=False,
                    byte2_bit5=False,
                    set_sequence_playback=True,
                    cant_float=False,
                    cant_walk_up_stairs=False,
                    cant_walk_under=False,
                    cant_pass_walls=False,
                    cant_jump_through=False,
                    cant_pass_npcs=False,
                    byte3_bit5=False,
                    cant_walk_through=False,
                    byte3_bit7=False,
                    slidable_along_walls=True,
                    cant_move_if_in_air=True,
                    byte7_upper2=3,
                )


class StandingLocation(StandardPrizeLocation):
    _npc_ids: list[AreaObject] = []

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "standing_grant")
            and prize.standing_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def grant(self, world: GameWorld | None = None) -> EventScript:
        if self.prize is None:
            return EventScript([Return()])
        if self.prize.standing_grant is None:
            return EventScript([Return()])
        return self.prize.standing_grant


class EventLocation(StandardPrizeLocation):
    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "npc_grant")
            and prize.npc_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def grant(self, world: GameWorld | None = None) -> EventScript:
        if self.prize is None:
            return EventScript([Return()])
        if self.prize.npc_grant is None:
            return EventScript([Return()])
        return self.prize.npc_grant


class RiverLocation(StandardPrizeLocation):
    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "river_grant")
            and prize.river_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def grant(self, world: GameWorld | None = None) -> EventScript:
        if self.prize is None:
            return EventScript([Return()])
        if self.prize.river_grant is None:
            return EventScript([Return()])
        return self.prize.river_grant


class RemoveIfNotFilled(StrEnum):
    """Controls whether unfilled henchman slot NPCs should be hidden."""

    NEVER = "never"  # Never hide unfilled slots (default)
    ALWAYS = "always"  # Always hide unfilled slots
    IF_ANY_FILLED = (
        "if_any_filled"  # Only hide if at least one slot of this type is filled
    )


class BossFightLocationHenchmanNPC:
    _pack_id: int | None = None
    _room_ids: list[int]
    _npc_ids: list[AreaObject]
    _skip_swap_if_flag: list[type["BooleanFlag"]] | None = None
    _remove_if_not_filled: RemoveIfNotFilled = RemoveIfNotFilled.NEVER
    _container_event: int

    @property
    def room_ids(self) -> list[int]:
        return self._room_ids

    @property
    def npc_ids(self) -> list[AreaObject]:
        return self._npc_ids

    @property
    def pack_id(self) -> int | None:
        return self._pack_id

    @property
    def skip_swap_if_flag(self) -> list[type["BooleanFlag"]] | None:
        return self._skip_swap_if_flag

    @property
    def remove_if_not_filled(self) -> RemoveIfNotFilled:
        return self._remove_if_not_filled

    @property
    def container_event(self) -> int:
        return self._container_event

    def __init__(
        self,
        room_ids: list[int],
        npc_ids: list[AreaObject],
        pack_id: int | None = None,
        skip_swap_if_flag: type["BooleanFlag"] | list[type["BooleanFlag"]] | None = None,
        remove_if_not_filled: RemoveIfNotFilled = RemoveIfNotFilled.NEVER,
        container_event: int | None = None,
    ):

        self._room_ids = room_ids
        self._npc_ids = npc_ids
        self._pack_id = pack_id
        self._remove_if_not_filled = remove_if_not_filled
        self._container_event = (
            container_event
            if container_event is not None
            else E1189_HENCHMAN_BATTLE_PACK_SELECTOR
        )
        if skip_swap_if_flag is None:
            self._skip_swap_if_flag = None
        elif isinstance(skip_swap_if_flag, list):
            self._skip_swap_if_flag = skip_swap_if_flag
        else:
            self._skip_swap_if_flag = [skip_swap_if_flag]

    def should_skip_swap(self, world: GameWorld) -> bool:
        """Check if this slot should skip NPC/pack swapping based on enabled flags."""
        if self._skip_swap_if_flag is None:
            return False
        return any(
            world.settings.isflag_enabled(flag)
            for flag in self._skip_swap_if_flag
        )


SlotCapOverride = int | Callable[["GameWorld"], int] | None
"""Per-slot cap override: a fixed int, a callable taking the world (so the
cap can vary with protagonist / recruit / etc.), or None to use the default
derived from the original room NPC."""


class BossFightLocationNPC:
    _room_id: int
    _npc_id: AreaObject
    _vram_size_override: SlotCapOverride = None
    _min_vram_size_override: SlotCapOverride = None
    _min_vram_from_seq0_override: SlotCapOverride = None
    _sequence_setter_event_id: int | None = None
    _skip_swap_if_flag: list[type["BooleanFlag"]] | None = None

    @property
    def room_id(self) -> int:
        return self._room_id

    @property
    def npc_id(self) -> AreaObject:
        return self._npc_id

    @property
    def vram_size_override(self) -> SlotCapOverride:
        """Manual VRAM size override (int or world-aware callable), if specified."""
        return self._vram_size_override

    @property
    def min_vram_size_override(self) -> SlotCapOverride:
        """Manual min_vram_size cap (int or world-aware callable)."""
        return self._min_vram_size_override

    @property
    def min_vram_from_seq0_override(self) -> SlotCapOverride:
        """Manual sequence-0 min_vram cap (int or world-aware callable)."""
        return self._min_vram_from_seq0_override

    @property
    def sequence_setter_event_id(self) -> int | None:
        return self._sequence_setter_event_id

    @property
    def skip_swap_if_flag(
        self,
    ) -> list[type["BooleanFlag"]] | None:
        return self._skip_swap_if_flag

    def should_skip_swap(self, world: "GameWorld") -> bool:
        """Keep the original room NPC (skip the boss-model swap) when any listed
        flag is enabled - mirrors BossFightLocationHenchmanNPC.should_skip_swap.

        Each entry is a flag class.
        """
        if self._skip_swap_if_flag is None:
            return False
        return any(
            world.settings.isflag_enabled(flag)
            for flag in self._skip_swap_if_flag
        )

    @staticmethod
    def _resolve(override: SlotCapOverride, world: "GameWorld") -> int | None:
        if override is None:
            return None
        if callable(override):
            return override(world)
        return override

    def get_max_vram_size(self, world: "GameWorld") -> int:
        """Compute the maximum VRAM size this slot can support.

        If vram_size_override is set (int or callable returning int), uses that.
        Otherwise, retrieves the original room NPC's sprite vram_size.
        """
        ov = self._resolve(self._vram_size_override, world)
        if ov is not None:
            return ov

        room = world.rooms._rooms[self._room_id]
        assert room is not None
        obj = room.get_npc_by_target_id(self._npc_id)
        assert obj is not None
        sprite_id = obj._npc.sprite_id
        sprite = world.get_sprite(sprite_id)
        return sprite.animation.properties.vram_size

    def get_original_min_vram_size(self, world: "GameWorld") -> int:
        """Get the min_vram_size cap for boss model selection.

        If min_vram_size_override is set (int or callable returning int), uses
        that. Otherwise returns the original NPC's min_vram_size (0-7).
        """
        ov = self._resolve(self._min_vram_size_override, world)
        if ov is not None:
            return ov
        room = world.rooms._rooms[self._room_id]
        assert room is not None
        obj = room.get_npc_by_target_id(self._npc_id)
        assert obj is not None
        return obj._npc.min_vram_size

    def get_original_min_vram_from_sequence_0(self, world: "GameWorld") -> int:
        """Get the sequence-0 min_vram cap for boss model selection.

        If min_vram_from_seq0_override is set (int or callable returning int),
        uses that. Otherwise computes the maximum VRAM needed across all frames
        in sequence 0 of the original NPC's sprite.
        """
        ov = self._resolve(self._min_vram_from_seq0_override, world)
        if ov is not None:
            return ov


        room = world.rooms._rooms[self._room_id]
        assert room is not None
        obj = room.get_npc_by_target_id(self._npc_id)
        assert obj is not None
        return min_vram_from_sequence_for_sprite(world, obj._npc.sprite_id, 0)

    def __init__(
        self,
        room_id: int,
        npc_id: AreaObject,
        vram_size_override: SlotCapOverride = None,
        sequence_setter_event_id: int | None = None,
        min_vram_size_override: SlotCapOverride = None,
        min_vram_from_seq0_override: SlotCapOverride = None,
        skip_swap_if_flag: (
            type["BooleanFlag"] | list[type["BooleanFlag"]] | None
        ) = None,
    ):
        self._room_id = room_id
        self._npc_id = npc_id
        self._vram_size_override = vram_size_override
        self._min_vram_size_override = min_vram_size_override
        self._min_vram_from_seq0_override = min_vram_from_seq0_override
        self._sequence_setter_event_id = sequence_setter_event_id
        if skip_swap_if_flag is None:
            self._skip_swap_if_flag = None
        elif isinstance(skip_swap_if_flag, list):
            self._skip_swap_if_flag = skip_swap_if_flag
        else:
            self._skip_swap_if_flag = [skip_swap_if_flag]


class BossFightLocation(PrizeLocation):
    _container_event: int = E0353_BOSS_BATTLE

    _pack_id: int
    _slots_pack_id: int | None = None
    _post_unlocks_event_id: int

    _henchman_packs: list[int] | None = None

    _dialogs_expecting_replacement: list[int] = []

    _npc_slots: list[BossFightLocationNPC] | None = None
    _character_henchman_slots: list[BossFightLocationHenchmanNPC] | None = None
    _mook_henchman_slots: list[BossFightLocationHenchmanNPC] | None = None
    _tiny_henchman_slots: list[BossFightLocationHenchmanNPC] | None = None
    _statue_slots: list[BossFightLocationNPC] | None = None

    _chosen_npc_models_by_room: dict[int, type["BossNPC"]] | None = None

    # Parallel to _chosen_npc_models_by_room but keyed by (room_id, npc_id)
    # because a single room can hold multiple henchman slots. Populated by
    # the henchman placement loop the same moment obj._npc is overwritten.
    _chosen_henchman_models_by_room_npc: dict[
        tuple[int, int], type["HenchmanNPC"]
    ] | None = None

    def get_chosen_npc_model_for_room(
        self, room_id: int
    ) -> type["BossNPC"] | None:
        """Return the NPC model selected at placement for the slot in room_id.

        Falls back to None if placement was skipped (e.g. prize matched original)
        or no slot for that room exists. Renders should re-run selection with
        slot-specific constraints in that case to stay consistent with placement.
        """
        if self._chosen_npc_models_by_room is None:
            return None
        return self._chosen_npc_models_by_room.get(room_id)

    def get_all_chosen_npc_models(self) -> list[type["BossNPC"]]:
        """Return every NPC model selected at placement across all slots."""
        if self._chosen_npc_models_by_room is None:
            return []
        return list(self._chosen_npc_models_by_room.values())

    def get_chosen_henchman_model_for_slot(
        self, room_id: int, npc_id: AreaObject
    ) -> type["HenchmanNPC"] | None:
        """Return the henchman model selected at placement for (room_id, npc_id).

        Returns None if placement didn't run for this slot (prize matched
        original, slot was skipped, or this slot isn't in any henchman list).
        """
        if self._chosen_henchman_models_by_room_npc is None:
            return None
        return self._chosen_henchman_models_by_room_npc.get((room_id, int(npc_id)))

    def get_all_chosen_henchman_models(self) -> list[type["HenchmanNPC"]]:
        """Return every henchman model selected at placement across all slots."""
        if self._chosen_henchman_models_by_room_npc is None:
            return []
        return list(self._chosen_henchman_models_by_room_npc.values())

    def resolve_npc_model_for_slot(
        self,
        world: "GameWorld",
        slot: BossFightLocationNPC,
    ) -> type["BossNPC"]:
        """Return the chosen model for slot, computing it on-demand if placement
        was skipped (prize matched original). Uses the same constraints placement
        would have used so the render and placement layers always agree.
        """
        cached = self.get_chosen_npc_model_for_room(slot.room_id)
        if cached is not None:
            return cached
        assert isinstance(self.prize, BossFightPrize)
        forced = self.prize.get_forced_npc_model_for_location(self)
        if forced is not None:
            return forced
        return self.prize.get_npc_for_slot(
            world,
            slot.get_max_vram_size(world),
            slot.get_original_min_vram_size(world),
            slot.get_original_min_vram_from_sequence_0(world),
        )

    # Whether the player can run away from battles at this location
    # Set to True for dojo fights, mimic fights with mimics anywhere, etc.
    _allow_run_away: bool = False

    # Whether the player can run away from henchmen fights at this location
    # Defaults to True (can escape). Set to False for Mushroom Kingdom, Booster Tower, etc.
    _henchman_can_run_away: bool = True

    _originally_held: type[BossFightPrize]

    _default_battlefield: Battlefield | None = None

    @property
    def default_battlefield(self) -> Battlefield | None:
        return self._default_battlefield

    @property
    def originally_held(self) -> type[BossFightPrize]:
        return self._originally_held

    @property
    def statue_slots(self) -> list[BossFightLocationNPC] | None:
        return self._statue_slots

    @property
    def npc_slots(self) -> list[BossFightLocationNPC] | None:
        return self._npc_slots

    @property
    def character_henchman_slots(self) -> list[BossFightLocationHenchmanNPC] | None:
        return self._character_henchman_slots

    @property
    def mook_henchman_slots(self) -> list[BossFightLocationHenchmanNPC] | None:
        return self._mook_henchman_slots

    @property
    def eligible_mook_henchmen(self) -> list[BossFightHenchman] | None:
        """Mook henchmen this location may put in its _mook_henchman_slots.

        Defaults to the prize's full list. Locations override to drop models
        their henchman rooms can't render.
        """
        assert isinstance(self.prize, BossFightPrize)
        return self.prize.mook_henchmen

    @property
    def tiny_henchman_slots(self) -> list[BossFightLocationHenchmanNPC] | None:
        return self._tiny_henchman_slots

    @property
    def pack_id(self) -> int:
        return self._pack_id

    @property
    def slots_pack_id(self) -> int | None:
        return self._slots_pack_id

    @property
    def henchman_packs(self) -> list[int] | None:
        return self._henchman_packs

    @property
    def allow_run_away(self) -> bool:
        """Whether the player can run away from battles at this location."""
        return self._allow_run_away

    def post_unlocks(self, world: GameWorld) -> EventScript:
        """Script commands that should run when this boss location is cleared. Depends on settings."""
        output: list[UsableEventScriptCommand] = []
        if self.prize is not None and isinstance(self.prize, BossFightPrize):
            output = self.prize.boss_hunt_unlocks(world).contents
        return EventScript([*output, Return()])

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        if not isinstance(prize, BossFightPrize) or prize.boss_fight_grant is None:
            return False

        # Mirror of the Smithy guard in StarPieceLocation.can_access. Star pieces
        # are now placed before their parent boss slot is filled, and the Smithy
        # fight is deliberately deferred to the last placement pass, so the forward
        # check can never see him at star piece placement time. Guard from this
        # side instead: a slot whose star piece child is already holding a piece
        # must not take Smithy, because beating him ends the run.
        if isinstance(prize, SmithyBossFight) and world.settings.is_flag_value(
            WinCondition, WinConditions.SMITHY
        ):
            for l in world.locations.values():
                if (
                    isinstance(l, StarPieceLocation)
                    and getattr(l, "_parent", None) is type(self)
                    and l.has_item
                ):
                    return False

        return super().can_accept(prize, inventory, world)

    def _apply_henchmen(self, world: GameWorld) -> tuple[
        list[tuple[int, int, int]],
        list[tuple[BossFightLocationHenchmanNPC, BossFightHenchman]],
    ]:
        """Assign henchmen to slots and set their NPC models and battle packs.

        Returns a tuple containing:
        - list of (container_event, room_id, pack_id) tuples for henchmen that need
          event script battle pack selectors (non-BattlePackNPC objects).
        - list of (slot, henchman) tuples for all assigned henchmen.
        """

        assert isinstance(self.prize, BossFightPrize)

        # Get lazy imports for special boss handling

        henchmen_assignments: list[
            tuple[BossFightLocationHenchmanNPC, BossFightHenchman]
        ] = []
        event_script_battle_packs: list[tuple[int, int, int]] = []

        # Set can_run_away for ALL henchman slot packs upfront
        # This ensures the setting is applied even if no henchmen are assigned
        all_henchman_slots = (
            (self.mook_henchman_slots or [])
            + (self.character_henchman_slots or [])
            + (self.tiny_henchman_slots or [])
        )

        # Assign mook henchmen
        mook_pool = self.eligible_mook_henchmen
        if self.mook_henchman_slots and mook_pool:
            # Filter out slots that should skip swapping
            active_mook_slots = [
                s for s in self.mook_henchman_slots if not s.should_skip_swap(world)
            ]
            if active_mook_slots:
                mooks = random.choices(
                    mook_pool, k=len(active_mook_slots)
                )
                henchmen_assignments.extend(zip(active_mook_slots, mooks))
                for slot, henchman in zip(active_mook_slots, mooks):
                    if slot.pack_id is None:
                        continue
                    formation_size = random.triangular(0, 5, 2)
                    if isinstance(self.prize, (KamekBossFight, CountdownBossFight)):
                        formation_size = 1
                    members: list[type[Enemy]] = [
                        h.monster
                        for h in random.choices(mook_pool, k=int(formation_size))
                        if h.monster is not None
                    ]
                    if henchman.monster is not None:
                        members.append(henchman.monster)
                    coords = generate_formation_coordinates(members, world)
                    formation_members: list[FormationMember | None] = [
                        FormationMember(
                            m,
                            c[0],
                            c[1],
                            hidden_at_start=self.prize.henchmen_hidden_at_start,
                        )
                        for m, c in zip(members, coords)
                        if c is not None
                    ]
                    # Set the formation on the henchman pack with a new Formation
                    # to avoid mutating shared Formation objects
                    henchman_pack = world.battle_packs._packs[slot.pack_id]
                    new_formation = Formation(
                        members=formation_members,
                        can_run_away=self._henchman_can_run_away,
                        unknown_bit=not self._henchman_can_run_away,
                        run_event_at_load=henchman.run_event_at_load,
                        id=world.allocate_formation_id(),
                    )
                    henchman_pack.set_formations(new_formation)

        # Assign character henchmen
        if self.character_henchman_slots:
            # Filter out slots that should skip swapping
            active_char_slots = [
                s
                for s in self.character_henchman_slots
                if not s.should_skip_swap(world)
            ]

            chars: list[BossFightHenchman] = []
            if self.prize.character_henchmen is not None and len(
                self.prize.character_henchmen
            ) >= len(active_char_slots):
                chars.extend(self.prize.character_henchmen[: len(active_char_slots)])
            elif self.prize.character_henchmen is not None:
                chars.extend(self.prize.character_henchmen)

            for slot, henchman in zip(active_char_slots[: len(chars)], chars):
                if slot.pack_id is not None and henchman.monster is not None:
                    fr: FormationMember = FormationMember(
                        henchman.monster,
                        183,
                        127,
                        hidden_at_start=self.prize.henchmen_hidden_at_start,
                    )
                    henchman_pack = world.battle_packs._packs[slot.pack_id]
                    new_formation = Formation(
                        members=[fr],
                        can_run_away=self._henchman_can_run_away,
                        unknown_bit=not self._henchman_can_run_away,
                        run_event_at_load=henchman.run_event_at_load,
                        id=world.allocate_formation_id(),
                    )
                    henchman_pack.set_formations(new_formation)
            henchmen_assignments.extend(zip(active_char_slots[: len(chars)], chars))

            # Fill remaining character slots with mooks if needed
            if (
                len(chars) < len(active_char_slots)
                and self.prize.mook_henchmen is not None
            ):
                mooks = random.choices(
                    self.prize.mook_henchmen, k=len(active_char_slots) - len(chars)
                )
                for slot, henchman in zip(active_char_slots[len(chars) :], mooks):
                    if slot.pack_id is None:
                        continue
                    formation_size = random.triangular(0, 5, 2)
                    if isinstance(self.prize, (KamekBossFight, CountdownBossFight)):
                        formation_size = 1
                    members: list[type[Enemy]] = [
                        h.monster
                        for h in random.choices(
                            self.prize.mook_henchmen, k=int(formation_size)
                        )
                        if h.monster is not None
                    ]
                    if henchman.monster is not None:
                        members.append(henchman.monster)
                    coords = generate_formation_coordinates(members, world)
                    formation_members: list[FormationMember | None] = [
                        FormationMember(
                            m,
                            c[0],
                            c[1],
                            hidden_at_start=self.prize.henchmen_hidden_at_start,
                        )
                        for m, c in zip(members, coords)
                        if c is not None
                    ]
                    # Set the formation on the henchman pack with a new Formation
                    # to avoid mutating shared Formation objects
                    henchman_pack = world.battle_packs._packs[slot.pack_id]
                    new_formation = Formation(
                        members=formation_members,
                        can_run_away=self._henchman_can_run_away,
                        unknown_bit=not self._henchman_can_run_away,
                        run_event_at_load=henchman.run_event_at_load,
                        id=world.allocate_formation_id(),
                    )
                    henchman_pack.set_formations(new_formation)
                henchmen_assignments.extend(zip(active_char_slots[len(chars) :], mooks))

        # Assign tiny henchmen
        if self.tiny_henchman_slots and self.prize.tiny_henchmen:
            # Filter out slots that should skip swapping
            active_tiny_slots = [
                s for s in self.tiny_henchman_slots if not s.should_skip_swap(world)
            ]
            if active_tiny_slots:
                blobs = random.choices(
                    self.prize.tiny_henchmen, k=len(active_tiny_slots)
                )
                henchmen_assignments.extend(zip(active_tiny_slots, blobs))

        # Set NPC models and battle packs for all assigned henchmen
        assigned_slots: set[BossFightLocationHenchmanNPC] = set()
        for slot, henchman in henchmen_assignments:
            assigned_slots.add(slot)
            for room_id, room_target in zip(slot.room_ids, slot.npc_ids):
                room = world.rooms._rooms[room_id]
                assert room is not None
                obj = room.get_npc_by_target_id(room_target)
                assert obj is not None
                new_npc = henchman.model().base
                obj._npc = new_npc
                # Record the chosen henchman model so downstream consumers
                # (e.g. the partition orchestrator's npc_expected_animations
                # sizing) can resolve animation attrs against the model that
                # actually landed here, not just the original room source.
                if self._chosen_henchman_models_by_room_npc is None:
                    self._chosen_henchman_models_by_room_npc = {}
                self._chosen_henchman_models_by_room_npc[
                    (room_id, int(room_target))
                ] = henchman.model
                if slot.pack_id is not None:
                    if isinstance(obj, (BattlePackNPC, BattlePackClone)):
                        obj.set_battle_pack(slot.pack_id)
                    else:
                        # Need event script for battle pack selection
                        event_script_battle_packs.append(
                            (slot.container_event, room_id, slot.pack_id)
                        )

        # Generate E1189 entries for unassigned slots that have non-BattlePackNPC
        # objects. This covers cases where the incoming boss has no henchmen or
        # should_skip_swap filtered the slot out - the original NPCs remain
        # visible and still call E1189 as a subroutine, so it needs an entry.
        for slot in all_henchman_slots:
            if slot in assigned_slots or slot.pack_id is None:
                continue
            for room_id, room_target in zip(slot.room_ids, slot.npc_ids):
                room = world.rooms._rooms[room_id]
                if room is None:
                    continue
                obj = room.get_npc_by_target_id(room_target)
                if obj is None:
                    continue
                if not isinstance(obj, BattlePackNPC):
                    event_script_battle_packs.append(
                        (slot.container_event, room_id, slot.pack_id)
                    )

        return event_script_battle_packs, henchmen_assignments

    def _get_henchmen_event_packs_for_original(
        self, world: GameWorld
    ) -> list[tuple[int, int, int]]:
        """Get event script battle pack entries for original (unmodified) henchmen.

        This is used when the prize matches the original - we don't modify NPCs,
        but we still need to generate event script entries for RegularNPC henchmen
        because the event scripts are being rebuilt from scratch.

        Returns a list of (container_event, room_id, pack_id) tuples for henchmen
        that need event script battle pack selectors (non-BattlePackNPC objects).
        """

        event_script_battle_packs: list[tuple[int, int, int]] = []

        # Gather all henchman slots with pack_ids
        all_slots: list[BossFightLocationHenchmanNPC] = []
        if self.mook_henchman_slots:
            all_slots.extend(self.mook_henchman_slots)
        if self.character_henchman_slots:
            all_slots.extend(self.character_henchman_slots)
        if self.tiny_henchman_slots:
            all_slots.extend(self.tiny_henchman_slots)

        # Check each slot's NPCs
        for slot in all_slots:
            if slot.pack_id is None:
                continue
            for room_id, room_target in zip(slot.room_ids, slot.npc_ids):
                room = world.rooms._rooms[room_id]
                if room is None:
                    continue
                obj = room.get_npc_by_target_id(room_target)
                if obj is None:
                    continue
                # Only RegularNPC objects need event script entries
                if not isinstance(obj, BattlePackNPC):
                    event_script_battle_packs.append(
                        (slot.container_event, room_id, slot.pack_id)
                    )

        return event_script_battle_packs

    def _on_henchmen_assigned(
        self,
        world: GameWorld,
        henchmen_assignments: list[
            tuple[BossFightLocationHenchmanNPC, BossFightHenchman]
        ],
    ) -> None:
        """Hook method called after henchmen are assigned.

        Subclasses can override this to perform additional logic based on which
        henchmen were randomly chosen.

        Args:
            world: The game world instance.
            henchmen_assignments: List of (slot, henchman) tuples for all assigned henchmen.
        """
        pass

    def _hide_unfilled_henchman_slots(
        self,
        world: GameWorld,
        henchmen_assignments: list[
            tuple[BossFightLocationHenchmanNPC, BossFightHenchman]
        ],
    ) -> None:
        """Hide NPCs for unfilled henchman slots based on their remove_if_not_filled setting.

        Args:
            world: The game world instance.
            henchmen_assignments: List of (slot, henchman) tuples for assigned henchmen.
        """
        assigned_slots = {slot for slot, _ in henchmen_assignments}

        def process_slot_list(
            slots: list[BossFightLocationHenchmanNPC] | None,
        ) -> None:
            if slots is None:
                return
            # Count how many slots of this type were filled (excluding skipped slots)
            active_slots = [s for s in slots if not s.should_skip_swap(world)]
            filled_count = sum(1 for s in active_slots if s in assigned_slots)

            for slot in slots:
                # Skip if slot was assigned or should skip swap
                if slot in assigned_slots or slot.should_skip_swap(world):
                    continue

                should_hide = False
                if slot.remove_if_not_filled == RemoveIfNotFilled.ALWAYS:
                    should_hide = True
                elif slot.remove_if_not_filled == RemoveIfNotFilled.IF_ANY_FILLED:
                    should_hide = filled_count > 0

                if should_hide:
                    for room_id, npc_id in zip(slot.room_ids, slot.npc_ids):
                        rm = world.rooms._rooms[room_id]
                        assert rm is not None
                        rm.get_npc_by_target_id(npc_id).set_visible(False)

        process_slot_list(self._character_henchman_slots)
        process_slot_list(self._mook_henchman_slots)
        process_slot_list(self._tiny_henchman_slots)

    def render(self, world: GameWorld) -> tuple[
        list[list[UsableEventScriptCommand]],
        list[UsableEventScriptCommand],
        list[tuple[int, int, int]],
    ]:

        # update the battle pack
        assert isinstance(self.prize, BossFightPrize)
        pack = world.battle_packs._packs[self._pack_id]
        run_away = self.allow_run_away

        if world.settings.isflag_enabled(MimicsAnywhere) and (
            isinstance(self.prize, MimicFightInitiatorPrize)
            or isinstance(self, MimicFightLocation)
        ):
            run_away = True

        if self.prize.formation is not None:
            # Use the prize's formation directly (preserves formation_id for AI scripts)
            formation = self.prize.formation
            pack.set_formations(formation)

            # Apply location-specific overrides to the formation
            # Always set run away based on location, not the prize's original setting
            formation.set_can_run_away(run_away)
            if self.prize.force_battlefield is not None:
                formation.set_battlefield(self.prize.force_battlefield)
            if self.prize.force_start_event is not None:
                formation.set_run_event_at_load(self.prize.force_start_event)
        else:
            # Legacy path: modify formation members in place
            # (used for prizes that haven't been migrated to use _formation)
            for f in pack.formations:
                f.set_members(
                    self.prize._members  # pyright: ignore[reportArgumentType]
                )
                # Always set run away based on location, not the prize's original setting
                f.set_can_run_away(run_away)
                if self.prize.force_battlefield is not None:
                    f.set_battlefield(self.prize.force_battlefield)
                if self.prize.force_start_event is not None:
                    f.set_run_event_at_load(self.prize.force_start_event)

        # If this location has a separate slots pack, mirror the formation to it
        if self._slots_pack_id is not None:
            slots_pack = world.battle_packs._packs[self._slots_pack_id]
    
            slots_run_away = world.settings.isflag_enabled(SlotsAnywhere)
            for f in slots_pack.formations:
                if self.prize.formation is not None:
                    f.set_members(self.prize.formation.members)
                    f.set_music(self.prize.formation.music)
                    f.set_unknown_bit(self.prize.formation.unknown_bit)
                else:
                    f.set_members(
                        self.prize._members  # pyright: ignore[reportArgumentType]
                    )
                f.set_can_run_away(slots_run_away)
                if self.prize.force_battlefield is not None:
                    f.set_battlefield(self.prize.force_battlefield)
                if self.prize.force_start_event is not None:
                    f.set_run_event_at_load(self.prize.force_start_event)

        # Skip NPC replacements if the prize matches the original (no shuffle occurred)
        prize_matches_original = isinstance(self.prize, self._originally_held)


        # Set NPC slots with boss models (using VRAM-based selection)
        if self.npc_slots is not None and not prize_matches_original:
            for slot in self.npc_slots:
                if slot.should_skip_swap(world):
                    # Leave the original room NPC in place (e.g. keep the large
                    # Dodo minigame sprite when KeepMinigameSpritesIntact is on).
                    continue
                room = world.rooms._rooms[slot.room_id]
                assert room is not None, f"Room {slot.room_id} not found"
                try:
                    obj = room.get_npc_by_target_id(slot.npc_id)
                except AssertionError:
                    raise ValueError(
                        f"{self.__class__.__name__}: Cannot access NPC {slot.npc_id} (0x{int(slot.npc_id):02x}) "
                        f"in room {slot.room_id}. Room has {len(room.objects)} objects "
                        f"(valid NPC range: 0x14-0x{0x14 + len(room.objects) - 1:02x})"
                    )
                assert obj is not None
                max_vram = slot.get_max_vram_size(world)
                max_min_vram = slot.get_original_min_vram_size(world)
                max_min_vram_seq0 = slot.get_original_min_vram_from_sequence_0(world)
                forced = self.prize.get_forced_npc_model_for_location(self)
                if forced is not None:
                    m = forced
                else:
                    m = self.prize.get_npc_for_slot(
                        world, max_vram, max_min_vram, max_min_vram_seq0
                    )
                if self._chosen_npc_models_by_room is None:
                    self._chosen_npc_models_by_room = {}
                self._chosen_npc_models_by_room[slot.room_id] = m
                obj._npc = m().base
                if isinstance(self.prize, KamekBossFight):
                    override = self.prize.get_slot_base_override(self, slot, m)
                    if override is not None:
                        obj._npc = override

        # Set statue slots with statue models
        if self.statue_slots is not None:
            for slot in self.statue_slots:
                room = world.rooms._rooms[slot.room_id]
                assert room is not None, f"Room {slot.room_id} not found"
                try:
                    obj = room.get_npc_by_target_id(slot.npc_id)
                except AssertionError:
                    raise ValueError(
                        f"{self.__class__.__name__}: Cannot access statue NPC {slot.npc_id} (0x{int(slot.npc_id):02x}) "
                        f"in room {slot.room_id}. Room has {len(room.objects)} objects "
                        f"(valid NPC range: 0x14-0x{0x14 + len(room.objects) - 1:02x})"
                    )
                assert obj is not None
                m = self.prize.statue_npc
                assert m is not None
                model = m()
                base = model.base
                obj._npc = base
                set_npc_direction_if_swse_only(world, slot.room_id, slot.npc_id, base)
                # Adjust statue sprite positioning per facing direction.
                if slot.sequence_setter_event_id is not None:
                    shift: PixelShift | None = None
                    if obj.direction == SOUTHWEST:
                        shift = model.southwest_facing_shift
                    elif obj.direction == SOUTHEAST:
                        shift = model.southeast_facing_shift
                    elif obj.direction == NORTHWEST:
                        shift = model.northwest_facing_shift
                    elif obj.direction == NORTHEAST:
                        shift = model.northeast_facing_shift
                    if shift is not None and (shift.right != 0 or shift.down != 0):
                        ev = world.event_scripts.get_script_by_id(
                            slot.sequence_setter_event_id
                        )
                        ev.set_contents(
                            [
                                ActionQueueAsync(
                                    slot.npc_id,
                                    [
                                        A_FixedFCoordOn(),
                                        A_ShiftXYPixels(shift.right, shift.down)
                                    ],
                                ),
                                *ev.contents,
                            ]
                        )

        # Assign and set henchmen
        if not prize_matches_original:
            henchmen_event_packs, henchmen_assignments = self._apply_henchmen(world)
            self._on_henchmen_assigned(world, henchmen_assignments)
            # Hide NPCs for unfilled henchman slots
            self._hide_unfilled_henchman_slots(world, henchmen_assignments)
        else:
            # Even when prize matches original, we need to generate E1189 entries
            # for RegularNPC henchmen since E1189 is rebuilt from scratch
            henchmen_event_packs = self._get_henchmen_event_packs_for_original(world)

        # any gating tied to the location or its contained boss needs to be written
        world.event_scripts.get_script_by_id(self._post_unlocks_event_id).set_contents(
            self.post_unlocks(world).contents
        )

        # return the contents for event 353
        # test this, not sure if this divide will work for mimics anywhere, esp if they end up in chests in rooms that normally dont have battles
        effective_rooms = self._rooms
        effective_battlefields: list[Battlefield] | None = None
        if isinstance(self, MimicFightLocation):
            # Lazy import to avoid circular dependency
            from randomizer.logic.progression.prizelocations import (
                Mimic1BossFight,
                Mimic2BossFight,
                Mimic3BossFight,
            )

            pairs = [
                (FirstMimicFightLauncher, Mimic1BossFight),
                (SecondMimicFightLauncher, Mimic2BossFight),
                (ThirdMimicFightLauncher, Mimic3BossFight),
            ]
            for launcher_cls, boss_cls in pairs:
                for location in world.locations.values():
                    if isinstance(location.prize, launcher_cls) and isinstance(
                        self, boss_cls
                    ):
                        effective_rooms = location._rooms
                        if self.prize.force_battlefield is not None:
                            effective_battlefields = [
                                self.prize.force_battlefield
                            ] * len(effective_rooms)
                        else:
                            effective_battlefields = [
                                ROOM_TO_BATTLEFIELD[r] for r in effective_rooms
                            ]
        elif (
            self.override_id is not None
            and self.prize.force_battlefield is None
            and self.default_battlefield is None
        ):
            identifier = str(uuid4())
            return (
                [
                    [
                        JmpIfVarEqualsConst(
                            PRIMARY_TEMP_7000, self.override_id, [identifier]
                        )
                    ]
                ],
                [
                    SetVarToConst(BATTLE_PACK_ID, self._pack_id, identifier=identifier),
                    StartBattleWithPackAt700E(),
                    Return(),
                ],
                henchmen_event_packs,
            )
        # Use prize's force_battlefield if set, otherwise use room-based battlefields
        # Only compute if not already set (e.g., by MimicFightLocation logic above)
        if effective_battlefields is None:
            if self.prize.force_battlefield is not None:
                effective_battlefields = [self.prize.force_battlefield] * len(
                    effective_rooms
                )
            elif self.default_battlefield is not None:
                effective_battlefields = [self.default_battlefield] * len(
                    effective_rooms
                )
            else:
                effective_battlefields = self.battlefields
                # Check for rooms missing from ROOM_TO_BATTLEFIELD
                missing_rooms = [
                    r for r in effective_rooms if r not in ROOM_TO_BATTLEFIELD
                ]
                if missing_rooms:
                    raise ValueError(
                        f"{self.__class__.__name__}: Rooms missing from ROOM_TO_BATTLEFIELD: {missing_rooms}. "
                        f"All rooms: {effective_rooms}"
                    )
        assert len(effective_rooms) == len(
            effective_battlefields
        ), f"Rooms and battlefields length mismatch: {len(effective_rooms)} rooms vs {len(effective_battlefields)} battlefields"
        split_ids = [str(uuid4()) for _ in effective_battlefields]
        battles = list(
            zip(
                effective_rooms,
                effective_battlefields,
                split_ids,
            )
        )
        second_array: list[UsableEventScriptCommand] = [
            cmd
            for _, battlefield, i in battles
            for cmd in (
                StartBattleAtBattlefield(self._pack_id, battlefield, identifier=i),
                Return(),
            )
        ]
        if self.override_id is not None:
            if len(battles) > 1:
                second_array = [
                    JmpIfVarEqualsConst(PRIMARY_TEMP_7000, room, [battle_id])
                    for room, _, battle_id in battles
                ] + second_array
                second_array.insert(0, Set7000ToCurrentLevel())
            return (
                [
                    [
                        JmpIfVarEqualsConst(
                            PRIMARY_TEMP_7000,
                            self.override_id,
                            [second_array[0].identifier.label],
                        )
                    ]
                ],
                second_array,
                henchmen_event_packs,
            )
        else:
            return (
                [
                    [JmpIfVarEqualsConst(PRIMARY_TEMP_7000, room, [battle_id])]
                    for room, _, battle_id in battles
                ],
                second_array,
                henchmen_event_packs,
            )


class MimicFightLocation(BossFightLocation):
    pass


class AllyNPCSub:
    _room_id: int
    _npc_id: AreaObject

    @property
    def room_id(self) -> int:
        return self._room_id

    @property
    def npc_id(self) -> AreaObject:
        return self._npc_id

    def __init__(self, room_id: int, npc_id: AreaObject):
        self._room_id = room_id
        self._npc_id = npc_id


class CharacterRecruitmentLocation(PrizeLocation):
    _show_dialog: bool
    _container_event: int
    _can_be_empty: bool = True
    _npc_fills: list[AllyNPCSub]

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "character_grant")
            and prize.character_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def render(self, world: GameWorld):
        if self.prize is None:
            return
        assert isinstance(self.prize, CharacterPrize)
        e = world.event_scripts.get_script_by_id(self._container_event)
        e.set_contents(self.prize.recruit(world, self._show_dialog).contents)
        e.contents.append(Return())

        if not isinstance(self, StartingCharacterLocation) and isinstance(
            self.prize, CharacterPrize
        ):
            for npc_sub in self._npc_fills:
                room = world.rooms._rooms[npc_sub.room_id]
                if room is None:
                    raise ValueError(
                        f"Room ID {npc_sub.room_id} not found in world while creating character recruitment script."
                    )
                obj = room.get_npc_by_target_id(npc_sub.npc_id)
                if obj is None:
                    raise ValueError(
                        f"NPC ID {npc_sub.npc_id} not found in room {npc_sub.room_id} while creating character recruitment script."
                    )
                obj._npc = self.prize.character_model.base


class StartingCharacterLocation(CharacterRecruitmentLocation):
    # Starting characters don't have NPC fills since they're assigned at game start
    _npc_fills: list[AllyNPCSub] = []


class StarPieceLocation(PrizeLocation):
    _parent: type[BossFightLocation]
    _can_be_empty: bool = True

    _excluded_win_conditions: list[WinConditions] = []

    def can_access(self, inventory: Inventory, world: GameWorld) -> bool:

        if hasattr(self, "_parent"):
            parent_location = world.get_location(self._parent)
            if parent_location is None:
                return False

            if (
                parent_location.prize is not None
                and isinstance(parent_location.prize, SmithyBossFight)
                and world.settings.is_flag_value(WinCondition, WinConditions.SMITHY)
            ):
                # Beating Smithy ends the run, so a piece granted by that fight
                # can never be collected.
                return False
        return super().can_access(inventory, world)

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:

        # Clearing this location's parent ends the run under this win condition,
        # so anything granted here is unreachable.
        for win_condition in self._excluded_win_conditions:
            if world.settings.is_flag_value(WinCondition, win_condition):
                return False

        # Check if the parent boss fight location is disabled in EnabledBossChecks
        # If so, this star piece location cannot have a star piece
        if hasattr(self, "_parent"):
            enabled_boss_check = cast(CategorizationFlag, world.settings.get_flag_by_id("bosses"))
            for m in enabled_boss_check.disabled:
                if self._parent == m.value:
                    return False

        if (
            not hasattr(prize, "postfight_star_piece_grant")
            or prize.postfight_star_piece_grant is None
        ):
            return False

        return super().can_accept(prize, inventory, world)

    _container_event: int = E0167_BOSS_GRANT_STAR_PIECE

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        identifier = str(uuid4())
        if self.prize is not None:
            postfight_grant = self.prize.postfight_star_piece_grant
            assert postfight_grant is not None
            postfight_grant.contents[0].rename(identifier)
            grant = EventScript(
                postfight_grant.contents
                + [JmpToEvent(E3092_STAR_PIECE_GRANT)]
            )
        else:
            grant = EventScript([Return(identifier=identifier)])
        if self.override_id is not None:
            return (
                [
                    [
                        JmpIfVarEqualsConst(
                            PRIMARY_TEMP_7000, self.override_id, [identifier]
                        )
                    ]
                ],
                grant.contents,
            )
        return (
            [
                [JmpIfVarEqualsConst(PRIMARY_TEMP_7000, r, [identifier])]
                for r in self._rooms
            ],
            grant.contents,
        )


class SpellSlotLocation(PrizeLocation):
    _can_be_empty: bool = True
    _level: int

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        # When SpellsAnywhere is enabled, spell slots are only sources (for pulling prizes)
        # not destinations - spells go into the general pool instead

        if world.settings.isflag_enabled(SpellsAnywhere):
            return False
        return isinstance(prize, SpellPrize) and super().can_accept(
            prize, inventory, world
        )

    def set_level(self, level: int):
        self._level = level


class PrizeRow(PrizeLocation):
    _container_event: int

    def can_be_empty(self, world: GameWorld) -> bool:

        if world.settings.is_flag_value(
            ItemQuality, ItemQualityOptions.COMPLETELY_EMPTY
        ):
            return True
        return super().can_be_empty(world)

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        identifier = str(uuid4())
        grant = self.grant(world)
        assert (
            len(grant.contents) > 0
        ), "Prize grant scripts must have at least one command"
        grant.contents[0].rename(identifier)
        if self.override_id is not None:
            return (
                [
                    [
                        JmpIfVarEqualsConst(
                            PRIMARY_TEMP_7000, self.override_id, [identifier]
                        )
                    ]
                ],
                grant.contents,
            )
        return (
            [
                [JmpIfVarEqualsConst(PRIMARY_TEMP_7000, r, [identifier])]
                for r in self._rooms
            ],
            grant.contents,
        )


class TreasureChestLocationRow(PrizeRow, TreasureChestLocation):
    def render(  # type: ignore[override]
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        TreasureChestLocation.render(self, world)
        return PrizeRow.render(self, world)


class TreasureChestLocationRow1(TreasureChestLocationRow):
    _container_event: int = E0247_CHEST_1_GRANT


class TreasureChestLocationRow2(TreasureChestLocationRow):
    _container_event: int = E0246_CHEST_2_GRANT


class TreasureChestLocationRow3(TreasureChestLocationRow):
    _container_event: int = E0245_CHEST_3_GRANT


class TreasureChestLocationRow4(TreasureChestLocationRow):
    _container_event: int = E0244_CHEST_4_GRANT


class TreasureChestLocationRow5(TreasureChestLocationRow):
    _container_event: int = E0243_CHEST_5_GRANT


class TreasureChestLocationRow6(TreasureChestLocationRow):
    _container_event: int = E0242_CHEST_6_GRANT


class NPCLocationRow(PrizeRow, EventLocation):
    _npc_ids: list[AreaObject] = []
    _check_npc_ids: list[AreaObject] = []

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        return super().render(world)


class NPCLocationRow1(NPCLocationRow):
    _container_event: int = E0253_NPC_QUEST_1_GRANT


class NPCLocationRow2(NPCLocationRow):
    _container_event: int = E0252_NPC_QUEST_2_GRANT


class NPCLocationRow3(NPCLocationRow):
    _container_event: int = E0251_NPC_QUEST_3_GRANT


class NPCLocationRow4(NPCLocationRow):
    _container_event: int = E0250_NPC_QUEST_4_GRANT


class NPCLocationRow5(NPCLocationRow):
    _container_event: int = E0249_NPC_QUEST_5_GRANT


class NPCLocationRow6(NPCLocationRow):
    _container_event: int = E0248_NPC_QUEST_6_GRANT


class NPCLocationRow7(NPCLocationRow):
    _container_event: int = E0226_NPC_QUEST_7_GRANT


class StandingLocationRow(PrizeRow, StandingLocation):
    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        return super().render(world)


class StandingLocationRow1(StandingLocationRow):
    _container_event: int = E0241_FREESTANDING_1_GRANT


class StandingLocationRow2(StandingLocationRow):
    _container_event: int = E0240_FREESTANDING_2_GRANT


class StandingLocationRow3(StandingLocationRow):
    _container_event: int = E0239_FREESTANDING_3_GRANT


class StandingLocationRow4(StandingLocationRow):
    _container_event: int = E0238_FREESTANDING_4_GRANT


class StandingLocationRow5(StandingLocationRow):
    _container_event: int = E0237_FREESTANDING_5_GRANT


class StandingLocationRow6(StandingLocationRow):
    _container_event: int = E0236_FREESTANDING_6_GRANT


class StandingLocationRow7(StandingLocationRow):
    _container_event: int = E0235_FREESTANDING_7_GRANT


class StandingLocationRow8(StandingLocationRow):
    _container_event: int = E0234_FREESTANDING_8_GRANT


class StandingLocationRow9(StandingLocationRow):
    _container_event: int = E0233_FREESTANDING_9_GRANT


class StandingLocationRow10(StandingLocationRow):
    _container_event: int = E0232_FREESTANDING_10_GRANT


class StandingLocationRow11(StandingLocationRow):
    _container_event: int = E0231_FREESTANDING_11_GRANT


class StandingLocationRow12(StandingLocationRow):
    _container_event: int = E0230_FREESTANDING_12_GRANT


class StandingLocationRow13(StandingLocationRow):
    _container_event: int = E0229_FREESTANDING_13_GRANT


class StandingLocationRow14(StandingLocationRow):
    _container_event: int = E0228_FREESTANDING_14_GRANT


class StandingLocationRow15(StandingLocationRow):
    _container_event: int = E0227_FREESTANDING_15_GRANT


class PacketLocation(StandingLocationRow):
    _replace: str
    _packet_id: int
    # Additional packets whose sprite should also be repointed to the assigned
    # prize, for items displayed by more than one packet in the room (e.g. a
    # cutscene that spawns the same item more than once). The primary
    # _packet_id is always included; subclasses opt in by listing extras here.
    _extra_packet_ids: list[int] = []

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        # Repoint the display packet's sprite to the assigned prize. This is ALL a bare
        # PacketLocation does - it is a COSMETIC mixin. The grant path comes from the
        # location's other bases (e.g. the Marrymore snifits keep their npc_grant; the
        # packet there is only a picture). A location whose prize is actually delivered by
        # the dynamically-spawned packet object must subclass PacketLocationRow1, which
        # routes grant -> packet_grant (object-local despawn) and runs the guard.
        if self.prize is None:
            self.set_prize(FPFlowerPrize())
        assert self.prize is not None and self.prize.model is not None
        for packet_id in [self._packet_id, *self._extra_packet_ids]:
            p = world.packets.packets[packet_id]
            assert p is not None, (
                f"Packet {packet_id} not found while rendering {type(self).__name__}"
            )
            p._set_sprite_id(self.prize.packet_data[0])
            prep_script = world.action_scripts.scripts[p.action_script_id]
            prep_script.insert_before_nth_command(
                0,
                A_SetSpriteSequence(
                    index=self.prize.packet_data[1], is_sequence=True, looping=True
                ),
            )
        return super().render(world)


class PacketLocationRow1(StandingLocationRow1, PacketLocation):
    # A real freestanding packet: the prize is delivered BY the dynamically-spawned packet
    # object, so its grant must be the object-local (FD-F2-free) packet_grant and the
    # presence-write guard applies. (A bare PacketLocation mixed into an NPCLocation is a
    # cosmetic sprite repoint only and keeps that location's npc_grant.)

    # When True, the grant sets SHIP_PACKET_AUTOTERM_DIALOG so the shared freestanding
    # grant variants (E4050-E4091) show the auto-terminating [end] dialog twin rather than
    # the [await] one. Correct only where the player collects the packet while running past
    # it and can't stop to press A. Default False: a standing packet must wait for input.
    _autoterminate_packet: bool = False

    def grant(self, world: GameWorld | None = None) -> EventScript:
        if self.prize is None:
            return EventScript([Return()])
        packet_grant = self.prize.packet_grant
        if packet_grant is None:
            return EventScript([Return()])
        if self._autoterminate_packet:
            # E0241 clears this at the top of every collection, so the bit is scoped to
            # exactly this grant. Prepending makes SetBit the grant's first command, which
            # PrizeRow.render renames to the room dispatch target - execution enters here.
            return EventScript(
                [SetBit(SHIP_PACKET_AUTOTERM_DIALOG), *packet_grant.contents]
            )
        return packet_grant

    def _assert_packet_grant_safe(self, world: GameWorld) -> None:
        # A packet is a dynamically-spawned object one slot past the room's last static
        # NPC, so it has no presence bit inside its own level's dynamic-width slice
        # ($7E:6D20). ANY persistent presence write on it therefore clears bit 0 of the
        # NEXT level's slice (that room's NPC_0). The real persistent writers are
        # event opcode F5 (RemoveObjectAt70A8FromCurrentLevel) and the action-level
        # "set object presence" (raw bytes FD F2) inside an ActionQueueSync - both reach
        # C0/99B0. The F9 form (RemoveObjectFromCurrentLevel on $70A8) only clears bit 7
        # of live object memory at $7E:60xx and is NOT persistent, so it is safe on a
        # packet; it is still rejected below to keep every packet grant routed through a
        # single uniform variant. Walk the whole grant + every event reachable by
        # JmpToEvent and fail the build if any such write survives.
        def writes_presence(script: EventScript) -> bool:
            for cmd in script.contents:
                if isinstance(cmd, RemoveObjectAt70A8FromCurrentLevel):
                    return True
                if isinstance(cmd, RemoveObjectFromCurrentLevel) and cmd.target == MEM_70A8:
                    return True
                if isinstance(cmd, ActionQueueSync):
                    for a in cmd.subscript.contents:
                        if isinstance(a, A_UnknownCommand) and bytes(a.render())[:2] == b"\xfd\xf2":
                            return True
            return False

        seen: set[int] = set()
        stack: list[EventScript | None] = [self.grant(world)]
        while stack:
            script = stack.pop()
            if script is None:
                continue
            if writes_presence(script):
                raise AssertionError(
                    f"{type(self).__name__}: packet grant for "
                    f"{type(self.prize).__name__} does a persistent presence write on $70A8 "
                    f"(RemoveObject or FD F2) - would despawn the next room's NPC_0. Route it "
                    f"to an FD-F2-free packet variant (see Prize._PACKET_VARIANT_EVENTS)."
                )
            for cmd in script.contents:
                if isinstance(cmd, JmpToEvent) and cmd.destination not in seen:
                    seen.add(cmd.destination)
                    stack.append(world.event_scripts.get_script_by_id(cmd.destination))

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        self._assert_packet_grant_safe(world)
        return super().render(world)


class RiverLocationRow(PrizeRow, RiverLocation):
    pass


class RiverLocationRow2(RiverLocationRow):
    _container_event: int = E0241_FREESTANDING_1_GRANT


class BoosterHillLocation(PrizeRow, StandardPrizeLocation):
    _70B1_id: int
    _npc_id: AreaObject
    _container_event: int = E0219_HILL_GRANT_LOGIC
    _designated_packet_ids: list[int]

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return (
            hasattr(prize, "hill_grant")
            and prize.hill_grant is not None
            and super().can_accept(prize, inventory, world)
        )

    def grant(self, world: GameWorld | None = None) -> EventScript:
        if self.prize is None:
            return EventScript([Return()])
        if self.prize.hill_grant is None:
            return EventScript([Return()])
        return self.prize.hill_grant

    def render(
        self, world: GameWorld
    ) -> tuple[list[list[UsableEventScriptCommand]], list[UsableEventScriptCommand]]:
        identifier = str(uuid4())
        grant = self.grant(world)
        assert (
            len(grant.contents) > 0
        ), "Prize grant scripts must have at least one command"
        for id in self._designated_packet_ids:
            packet = world.packets.packets[id]
            assert (
                packet is not None
            ), f"Packet ID {id} not found in world while creating Booster Hill location."
            assert self.prize is not None
            packet._set_sprite_id(self.prize.packet_data[0])
            prep_script = world.action_scripts.scripts[packet.action_script_id]
            prep_script.insert_before_nth_command(
                0,
                A_SetSpriteSequence(
                    index=self.prize.packet_data[1], is_sequence=True, looping=True
                ),
            )

        return (
            [[JmpIfVarEqualsConst(PRIMARY_TEMP_7000, self._70B1_id, [identifier])]],
            [
                Inc(BOOSTER_HILL_FLOWER_COUNTER, identifier=identifier),
                *grant.contents,
                EnableControlsUntilReturn([B]),
                Return(),
            ],
        )


class TreasureShopLocation(PrizeLocation):
    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        if not hasattr(prize, "_nickname"):
            return False
        return super().can_accept(prize, inventory, world)


class KeyItemLocation(PrizeLocation):
    def key(self, world: GameWorld) -> bool:
        return True

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        # No reverse restriction: non-key items can fill key locations as filler.
        # The forward restriction (key items → key locations only) is enforced by
        # StandardPrizeLocation.can_accept, which rejects KeyPrize without KeyItemsAnywhere.
        return super().can_accept(prize, inventory, world)


class InvisibleFlagLocation(NPCLocationRow1, KeyItemLocation):

    _which: int
    _x_coord: int = 0
    _y_coord: int = 0
    _z_coord: int = 0
    _x_shift: int = 0
    _y_shift: int = 0
    _clue_text: str

    def which(self) -> int:
        return self._which

    @property
    def override_id(self) -> int | None:
        if self._which == 0:
            return 530
        elif self._which == 1:
            return 531
        elif self._which == 2:
            return 532
        raise ValueError("which must be 0, 1, or 2")

    @property
    def clue_text(self) -> str:
        return self._clue_text

    @property
    def dialog_id(self) -> int:
        if self._which == 0:
            return E0084_THREE_MUSTY_FEARS_BONES_DIALOG
        elif self._which == 1:
            return E0082_THREE_MUSTY_FEARS_GREAPER_DIALOG
        elif self._which == 2:
            return E0083_THREE_MUSTY_FEARS_BOO_DIALOG
        raise ValueError("which must be 0, 1, or 2")

    @property
    def shift(self) -> ActionScript:
        cmds: list[UsableActionScriptCommand] = []
        if self._x_shift > 0:
            cmds.append(A_WalkEastPixels(self._x_shift))
        elif self._x_shift < 0:
            cmds.append(A_WalkWestPixels(-self._x_shift))
        if self._y_shift > 0:
            cmds.append(A_WalkSouthPixels(self._y_shift))
        elif self._y_shift < 0:
            cmds.append(A_WalkNorthPixels(-self._y_shift))
        cmds.append(A_ReturnQueue())
        return ActionScript(cmds)

    @property
    def bit(self) -> Flag:
        if self._which == 0:
            return INVISIBLE_FLAG_1_FOUND
        elif self._which == 1:
            return INVISIBLE_FLAG_2_FOUND
        elif self._which == 2:
            return INVISIBLE_FLAG_3_FOUND
        raise ValueError("which must be 0, 1, or 2")

    @property
    def npc(self) -> RegularNPC:
        if self._which == 0:
            ev = E1246_INVISIBLE_GRANT_1
            av = A0078_INVISIBLE_FLAG_1_POSITION
        elif self._which == 1:
            ev = E1247_INVISIBLE_GRANT_2
            av = A0079_INVISIBLE_FLAG_2_POSITION
        elif self._which == 2:
            ev = E1248_INVISIBLE_GRANT_3
            av = A0080_INVISIBLE_FLAG_3_POSITION
        else:
            raise ValueError("which must be 0, 1, or 2")
        return RegularNPC(
            npc=EMPTY_NPC_3,
            initiator=EventInitiator.PRESS_A_FROM_ANY_SIDE,
            event_script=ev,
            action_script=av,
            speed=3,
            visible=False,
            # Max out the collision box so the invisible flag is easy to bump into.
            acute_axis=15,
            obtuse_axis=15,
            height=15,
            x=self._x_coord,
            y=self._y_coord,
            z=self._z_coord,
            z_half=False,
            direction=SOUTHEAST,
            face_on_trigger=False,
            cant_enter_doors=False,
            byte2_bit5=False,
            set_sequence_playback=False,
            cant_float=False,
            cant_walk_up_stairs=False,
            cant_walk_under=False,
            cant_pass_walls=False,
            cant_jump_through=True,
            cant_pass_npcs=False,
            byte3_bit5=False,
            cant_walk_through=False,
            byte3_bit7=False,
            slidable_along_walls=True,
            cant_move_if_in_air=True,
            byte7_upper2=3,
            # The invisible flag rides the blank sprite, which is non-gridplane and never
            # lands in buffered_sprite_ids. Left at auto-decide (None) it falls through to
            # else: set_cannot_clone(True) in _recalculate_room_partition step 7 and takes
            # a dedicated VRAM allocation for a sprite that draws nothing.
            cannot_clone=False,
        )

    @property
    def originally_held(self) -> type[Prize] | None:
        # Slot order must match the found-bit order so each slot is internally
        # coherent: bit (.bit / E1246-E1248) maps i=0,1,2 -> flag1,2,3, and
        # script_2081 fixes flag1=Greaper, flag2=BigBoo, flag3=DryBones.
        if self._which == 0:
            return GreaperFlagPrize
        elif self._which == 1:
            return BigBooFlagPrize
        elif self._which == 2:
            return DryBonesFlagPrize
        raise ValueError("which must be 0, 1, or 2")

    def __init__(self, which: int):
        assert which in (0, 1, 2)
        self._which = which
        super().__init__()


ROOM_TO_BATTLEFIELD: dict[int, Battlefield] = {
    R000_DEBUG_ROOM: BF09_GRASSLANDS,
    R001_BLUE_BG_NOTHING_THERE: BF09_GRASSLANDS,
    R002_BOWSERS_KEEP_OUTSIDE_MARIO_ENTERS_AT_BEGINNING_OF_GAME: BF10_MOUNTAINS,
    R003_POSTGAME_SHIP: BF04_SUNKEN_SHIP,
    R004_POSTGAME_TOWER: BF12_BOOSTER_TOWER,
    R005_MARRYMORE_OUTSIDE_DURING_BOOSTER: BF28_MUSHROOM_KINGDOM,
    R006_MARRYMORE_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R007_MARRYMORE_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R008_BOWSERS_KEEP_AREA_09_TALL_ROOM_WO_SAVE_POINT_THIS_TIME: BF07_BOWSERS_KEEP,
    R009_MARRYMORE_INN_REGULAR_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R010_BOWSERS_KEEP_1ST_TIME_AREA_04_THRONE_ROOM: BF07_BOWSERS_KEEP,
    R011_MARRYMORE_INN_3F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R012_MARRYMORE_INN_SUITE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R013_BARREL_VOLCANO_FALLING_INTO_VOLCANO: BF20_BARREL_VOLCANO,
    R014_BOOSTER_HILL: BF10_MOUNTAINS,
    R015_VISTA_HILL: BF10_MOUNTAINS,
    R016_MARIOS_PAD: BF09_GRASSLANDS,
    R017_MUSHROOM_KINGDOM_CASTLE_MAIN_HALL: BF13_MUSHROOM_KINGDOM_CASTLE,
    R018_MUSHROOM_KINGDOM_CASTLE_THRONE_ROOM: BF15_MUSHROOM_KINGDOM_CASTLE,
    R019_MUSHROOM_KINGDOM_CASTLE_STAIR_ROOM_TO_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R020_MUSHROOM_KINGDOM_CASTLE_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R021_MUSHROOM_KINGDOM_CASTLE_BRANCH_ROOM_TO_VAULTGUEST_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R022_MUSHROOM_KINGDOM_CASTLE_GUEST_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R023_MUSHROOM_KINGDOM_BEFORE_CROCO_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R024_SUNKEN_SHIP_POSTKC_AREA_15_BANDANA_RED_ROOM_WLONG_STAIRWELL: BF04_SUNKEN_SHIP,
    R025_SUNKEN_SHIP_POSTKC_AREA_16_ENTRANCE_TO_JOHNNYS_ROOM: BF04_SUNKEN_SHIP,
    R026_SUNKEN_SHIP_POSTKC_AREA_12_UNDERWATER_ROOM_WSTAIRWELL_AND_ZEOSTARS: BF04_SUNKEN_SHIP,
    R027_SUNKEN_SHIP_POSTKC_AREA_13_LARGE_UNDERWATER_ROOM_WITH_A_BLOOBER: BF04_SUNKEN_SHIP,
    R028_SUNKEN_SHIP_POSTKC_AREA_17_JOHNNYS_ROOM: BF04_SUNKEN_SHIP,
    R029_MUSHROOM_KINGDOM_CASTLE_THRONE_ROOM_TOADSTOOL_RETURNS: BF15_MUSHROOM_KINGDOM_CASTLE,
    R030_MUSHROOM_KINGDOM_CASTLE_TOADSTOOLS_ROOM_TOADSTOOL_RETURNS: BF13_MUSHROOM_KINGDOM_CASTLE,
    R031_MUSHROOM_KINGDOM_CASTLE_VAULT: BF13_MUSHROOM_KINGDOM_CASTLE,
    R032_MUSHROOM_KINGDOM_CASTLE_ENTRANCE_TO_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R033_YOSTER_ISLE_ENTRANCE_FROM_PIPE_VAULT: BF33_PLATEAUS,
    R034_YOSTER_ISLE: BF33_PLATEAUS,
    R035_BOOSTER_TOWER_7F_3LEVEL_WPARACHUTING_SPOOKUMS: BF12_BOOSTER_TOWER,
    R036_BOOSTER_TOWER_6F_AREA_04_3LEVEL_WTHWOMP_ON_TEETERTOTTER: BF12_BOOSTER_TOWER,
    R037_BOOSTER_TOWER_4F_3LEVEL_ROOM_WJUMPING_SPOOKUMS: BF12_BOOSTER_TOWER,
    R038_BOOSTER_TOWER_9F_BOOSTERS_BOMBTHROWING_ROOM_WRAIL_TRACKS: BF12_BOOSTER_TOWER,
    R039_BOOSTER_TOWER_5F_KNIFE_GUYS_ROOM: BF12_BOOSTER_TOWER,
    R040_BOOSTER_TOWER_8F_CHOMP_STAIRWAY: BF12_BOOSTER_TOWER,
    R041_BOOSTER_TOWER_8F_AREA_01_MINESWEEPER_ROOM_WCOINS_AND_HIDDEN_FIREBALLS: BF12_BOOSTER_TOWER,
    R042_BOOSTER_TOWER_3F_AREA_02_NES_MARIO_ROOM: BF12_BOOSTER_TOWER,
    R043_BOOSTER_TOWER_1F_AREA_01_MAIN_ROOM: BF12_BOOSTER_TOWER,
    R044_MUSHROOM_KINGDOM_BEFORE_CROCO_JUMPING_KIDS_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R045_MUSHROOM_KINGDOM_BEFORE_CROCO_JUMPING_KIDS_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R046_MUSHROOM_KINGDOM_BEFORE_CROCO_RAZ_AND_RAINIS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R047_MUSHROOM_KINGDOM_BEFORE_CROCO_ITEM_SHOP_TOP_FLOOR: BF11_MUSHROOM_KINGDOM_HOUSE,
    R048_BOOSTER_TOWER_8F_AREA_02_ZOOM_SHOES_ROOM: BF12_BOOSTER_TOWER,
    R049_MUSHROOM_KINGDOM_BEFORE_CROCO_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R050_POSTGAME_CHAPEL: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R051_MUSHROOM_KINGDOM_BEFORE_CROCO_RUNNING_KIDS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R052_MUSHROOM_KINGDOM_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R053_MUSHROOM_KINGDOM_BEFORE_CROCO_ITEM_SHOP_BASEMENT: BF11_MUSHROOM_KINGDOM_HOUSE,
    R054_BOOSTER_HILL_DUMMY: BF10_MOUNTAINS,
    R055_PIPE_VAULT_ENTRANCE: BF33_PLATEAUS,
    R056_KERO_SEWERS_AREA_02_LONG_ROOM_WTHREE_PIPES: BF21_KERO_SEWERS,
    R057_KERO_SEWERS_AREA_03_LARGE_WATER_ROOM_WPIPE_IN_CENTER: BF21_KERO_SEWERS,
    R058_KERO_SEWERS_AREA_06_LONG_WATER_ROOM_WRAT_FUNKS_IN_A_LINE: BF21_KERO_SEWERS,
    R059_KERO_SEWERS_AREA_05_SUPER_STAR_ROOM_WFOUR_RAT_FUNKS: BF21_KERO_SEWERS,
    R060_KERO_SEWERS_AREA_04_LARGE_ROOM_WPANDORITE_AND_HIDING_RAT_FUNKS: BF21_KERO_SEWERS,
    R061_NIMBUS_LAND_OUTSIDE_DURING_VALENTINA_RIGHT_BEFORE_FIGHT: BF24_NIMBUS_LAND,
    R062_KERO_SEWERS_AREA_01_WATER_ROOM_WSAVE: BF21_KERO_SEWERS,
    R063_MARRYMORE_SCENE: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R064_MARRYMORE_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R065_MARRYMORE_CHAPEL_SANCTUARY: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R066_ROSE_WAY_EXIT_AREA_WHERE_BOWSERS_TROOPS_GATHERED: BF33_PLATEAUS,
    R067_MIDAS_RIVER_BUSINESS_TRANSACTION_AREA: BF33_PLATEAUS,
    R068_MIDAS_RIVER_BARREL_JUMPING_RIVER: BF34_SEA_ENCLAVE,
    R069_MIDAS_RIVER_WATERFALL: BF34_SEA_ENCLAVE,
    R070_MIDAS_RIVER_1ST_TUNNEL: BF34_SEA_ENCLAVE,
    R071_MIDAS_RIVER_2ND_TUNNEL_BOTH_LEFT_AND_RIGHT: BF34_SEA_ENCLAVE,
    R072_MIDAS_RIVER_3RD_TUNNEL_ON_LEFT: BF34_SEA_ENCLAVE,
    R073_MIDAS_RIVER_4TH_TUNNEL_ON_VERY_BOTTOM_RIGHT: BF34_SEA_ENCLAVE,
    R074_TADPOLE_POND_AREA_02: BF33_PLATEAUS,
    R075_TADPOLE_POND_AREA_01: BF33_PLATEAUS,
    R076_BANDITS_WAY_AREA_01: BF09_GRASSLANDS,
    R077_BANDITS_WAY_AREA_03: BF09_GRASSLANDS,
    R078_BANDITS_WAY_AREA_04: BF09_GRASSLANDS,
    R079_ROSE_WAY_MAIN_AREA: BF33_PLATEAUS,
    R080_ROSE_WAY_TWO_FASTFLOATING_PLATFORMS: BF33_PLATEAUS,
    R081_ROSE_WAY_TREASURE_CHESTS_WCOINS_AREA: BF33_PLATEAUS,
    R082_ROSE_WAY_WINDING_PATH_WCROOKS: BF33_PLATEAUS,
    R083_ROSE_TOWN_DURING_BOWYER_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R084_ROSE_TOWN_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R085_ROSE_TOWN_DURING_BOWYER_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R086_ROSE_TOWN_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R087_ROSE_TOWN_ITEM_SHOP: BF11_MUSHROOM_KINGDOM_HOUSE,
    R088_SMITHYS_FINAL_FORM_DEFEAT_GENOS_REDEMPTION: BF45_SMITHYS_FINAL_FORM,
    R089_ROSE_TOWN_DURING_BOWYER_THREE_GRANDKIDS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R090_ROSE_TOWN_THREE_GRANDKIDS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R091_ROSE_TOWN_COUPLES_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R092_GRATE_GUYS_CASINO_INSIDE_CASINO: BF12_BOOSTER_TOWER,
    R093_ROSE_TOWN_DURING_BOWYER_TREASURE_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R094_ROSE_TOWN_TREASURE_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R095_ROSE_TOWN_DURING_BOWYER_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R096_ROSE_TOWN_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R097_ROSE_TOWN_DURING_BOWYER_TREASURE_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R098_ROSE_TOWN_TREASURE_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R099_ROSE_TOWN_GENO_AWAKENS_IN_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R100_BOOSTER_PASS_AREA_01: BF10_MOUNTAINS,
    R101_BOOSTER_PASS_AREA_02: BF10_MOUNTAINS,
    R102_MOLEVILLE_OUTSIDE_AT_EXIT_FROM_MINES: BF10_MOUNTAINS,
    R103_SMITHY_FACTORY_AREA_17_DOMINO_AND_CLOAKERS_ROOM: BF19_SMITHY_FACTORY,
    R104_GRATE_GUYS_CASINO_FRONT_DOOR: BF12_BOOSTER_TOWER,
    R105_MOLEVILLE_DYNA_AND_MITES_HOUSE_DUMMY: BF10_MOUNTAINS,
    R106_GRATE_GUYS_CASINO_OUTSIDE: BF09_GRASSLANDS,
    R107_NIMBUS_CASTLE_AREA_09_STATUE_ROOM_AFTER_VALENTINA: BF22_NIMBUS_CASTLE,
    R108_MOLEVILLE_OUTSIDE: BF10_MOUNTAINS,
    R109_NIMBUS_CASTLE_AREA_01_ENTRANCE_HALL: BF22_NIMBUS_CASTLE,
    R110_NIMBUS_CASTLE_AREA_18_DODOS_STATUEPOLISHING_ROOM: BF22_NIMBUS_CASTLE,
    R111_NIMBUS_CASTLE_AREA_04_LEFT_OF_4WAY_PATH_RIGHTANGLE_RED_BRICK_PATH_W_TREASURE: BF22_NIMBUS_CASTLE,
    R112_NIMBUS_CASTLE_AREA_17_RIGHT_OF_4WAY_PATH_SAVE_POINT: BF22_NIMBUS_CASTLE,
    R113_NIMBUS_CASTLE_AREA_16_SMALL_TWODOOR_ROOM_WTREASURE_FROM_AREA_15: BF22_NIMBUS_CASTLE,
    R114_NIMBUS_CASTLE_AREA_10_RED_BRICK_2LEVEL_ROOM_WTREASURE_FROM_BIRDOS_ROOM: BF22_NIMBUS_CASTLE,
    R115_NIMBUS_CASTLE_AREA_03_4WAY_PATH_DURING_VALENTINA: BF22_NIMBUS_CASTLE,
    R116_NIMBUS_CASTLE_AREA_02_LEFT_OF_AREA_01: BF22_NIMBUS_CASTLE,
    R117_NIMBUS_CASTLE_AREA_15_FRONT_OF_4WAY_PATH_LARGE_RIGHTANGLE_ROOM_W_PLANT: BF22_NIMBUS_CASTLE,
    R118_NIMBUS_CASTLE_AREA_05_LONG_5EXIT_ROOM_DURING_VALENTINA: BF22_NIMBUS_CASTLE,
    R119_NIMBUS_CASTLE_AREA_06_LEFTMOST_FRONT_DOOR_FROM_AREA_05: BF22_NIMBUS_CASTLE,
    R120_NIMBUS_CASTLE_AREA_13_THRONE_ROOM_DURING_VALENTINA: BF22_NIMBUS_CASTLE,
    R121_NIMBUS_CASTLE_PATH_AFTER_THRONE_ROOM_2ND: BF22_NIMBUS_CASTLE,
    R122_NIMBUS_CASTLE_AREA_12_ENTRANCE_TO_THRONE_ROOM: BF22_NIMBUS_CASTLE,
    R123_PIPE_VAULT_AREA_01: BF21_KERO_SEWERS,
    R124_PIPE_VAULT_AREA_03_LINE_OF_PIPES: BF21_KERO_SEWERS,
    R125_PIPE_VAULT_AREA_04_LINE_OF_COINS_2_HIDDEN_TREASURES: BF21_KERO_SEWERS,
    R126_PIPE_VAULT_AREA_06_LINE_OF_RED_PIPES: BF21_KERO_SEWERS,
    R127_PIPE_VAULT_AREA_02: BF21_KERO_SEWERS,
    R128_PIPE_VAULT_AREA_07_LONG_PATH_WMOVING_PLATFORMS: BF21_KERO_SEWERS,
    R129_PIPE_VAULT_AREA_05: BF21_KERO_SEWERS,
    R130_SEA_AREA_02_LARGE_ROOM_WITH_SHOP: BF38_SEA,
    R131_SEA_AREA_04_BUNCH_OF_ZEOSTARS: BF38_SEA,
    R132_SEA_AREA_05_FROM_AREA_02_WSAVE_POINT: BF38_SEA,
    R133_SEA_AREA_06_WATER_ROOM_WWHIRLPOOLS: BF38_SEA,
    R134_SEA_AREA_03_SUPER_STAR_ROOM: BF38_SEA,
    R135_SEA_AREA_01_ENTRANCE: BF38_SEA,
    R136_SEA_AREA_07_SMALL_UNDERWATER_ROOM: BF38_SEA,
    R137_LANDS_END_AREA_01: BF10_MOUNTAINS,
    R138_LANDS_END_AREA_02: BF10_MOUNTAINS,
    R139_LANDS_END_AREA_03_GECKITS_PLAYING_CANNONBALL: BF10_MOUNTAINS,
    R140_LANDS_END_AREA_012_NOTHING_THERE_UNUSED: BF10_MOUNTAINS,
    R141_LANDS_END_AREA_04_ROTATING_FLOWERS: BF33_PLATEAUS,
    R142_LANDS_END_AREA_05_SKY_BRIDGE: BF33_PLATEAUS,
    R143_PIPE_VAULT_GOOMBATHUMPING_ROOM: BF21_KERO_SEWERS,
    R144_BOWSERS_KEEP_6DOOR_TREASURE_AFTER_EACH_ROOM: BF07_BOWSERS_KEEP,
    R145_STAR_HILL_AREA_01: BF36_STAR_HILL,
    R146_PIPE_VAULT_AREA_02_DUMMY: BF21_KERO_SEWERS,
    R147_GAME_INTRO_MIDAS_RIVER_WATER_TUNNEL: BF34_SEA_ENCLAVE,
    R148_GAME_INTRO_BANDITS_WAY_AREA_04: BF09_GRASSLANDS,
    R149_GAME_INTRO_MIDAS_RIVER_BARREL_JUMPING: BF34_SEA_ENCLAVE,
    R150_GAME_INTRO_MOLEVILLE_OUTSIDE_DURING_BOWSERS_TROOP_SCENE: BF10_MOUNTAINS,
    R151_GAME_INTRO_BOOSTER_HILL: BF10_MOUNTAINS,
    R152_MARRYMORE_CHAPEL_MAIN_HALL: BF13_MUSHROOM_KINGDOM_CASTLE,
    R153_MARRYMORE_CHAPEL_ENTRANCE_TO_SANCTUARY: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R154_MARRYMORE_CHAPEL_SANCTUARY_DURING_BOOSTER: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R155_MARRYMORE_CHAPEL_KITCHEN: BF11_MUSHROOM_KINGDOM_HOUSE,
    R156_MARRYMORE_CHAPEL_KITCHEN_NO_SPRITESEXITS_UNUSED: BF11_MUSHROOM_KINGDOM_HOUSE,
    R157_STAR_HILL_AREA_03: BF36_STAR_HILL,
    R158_STAR_HILL_AREA_02: BF36_STAR_HILL,
    R159_STAR_HILL_AREA_04: BF36_STAR_HILL,
    R160_SUNKEN_SHIP_AREA_01: BF04_SUNKEN_SHIP,
    R161_SUNKEN_SHIP_AREA_03_GREAPERS: BF04_SUNKEN_SHIP,
    R162_SUNKEN_SHIP_AREA_04_GREAPERS_DRY_BONES: BF04_SUNKEN_SHIP,
    R163_SUNKEN_SHIP_PUZZLE_ROOM_2: BF04_SUNKEN_SHIP,
    R164_SUNKEN_SHIP_AREA_02_FROM_ENTRANCE_WSAVE_POINT: BF04_SUNKEN_SHIP,
    R165_SUNKEN_SHIP_AREA_06_PUZZLE_ROOM_PASSAGEWAY: BF04_SUNKEN_SHIP,
    R166_SUNKEN_SHIP_PUZZLE_ROOM_1: BF04_SUNKEN_SHIP,
    R167_SUNKEN_SHIP_AREA_05_LONG_STAIRWELL_WITH_RUNNING_ALLEY_RATS: BF04_SUNKEN_SHIP,
    R168_SUNKEN_SHIP_PUZZLE_ROOM_3: BF04_SUNKEN_SHIP,
    R169_SUNKEN_SHIP_AREA_07_PUZZLE_ROOM_PASSAGEWAY_BRANCH_ROOM_WSHAMAN: BF04_SUNKEN_SHIP,
    R170_SUNKEN_SHIP_AREA_14_DUMMY: BF04_SUNKEN_SHIP,
    R171_SUNKEN_SHIP_PUZZLE_ROOM_4: BF04_SUNKEN_SHIP,
    R172_SUNKEN_SHIP_PUZZLE_ROOM_5: BF04_SUNKEN_SHIP,
    R173_SUNKEN_SHIP_POSTKC_AREA_01_SMALL_ROOM_WTRAMPOLINE: BF04_SUNKEN_SHIP,
    R174_SEA_AREA_08_SHORE_WITH_SUNKEN_SHIP: BF34_SEA_ENCLAVE,
    R175_SUNKEN_SHIP_POSTKC_AREA_05_WDRY_BONES_LINKED_BY_MARIO_MIRROR_ROOM: BF04_SUNKEN_SHIP,
    R176_SUNKEN_SHIP_AREA_08_WSAVE_POINT_AND_GREEN_SWITCH_FOR_BARREL: BF04_SUNKEN_SHIP,
    R177_SUNKEN_SHIP_AREA_09_PASSWORD_ROOM: BF04_SUNKEN_SHIP,
    R178_SUNKEN_SHIP_POSTKC_AREA_04_LONG_STAIRWELL_WRUNNING_ALLEY_RATS: BF04_SUNKEN_SHIP,
    R179_SUNKEN_SHIP_POSTKC_AREA_06_MARIO_MIRROR_ROOM: BF04_SUNKEN_SHIP,
    R180_SUNKEN_SHIP_POSTKC_AREA_02_SMALL_2LEVEL_ROOM: BF04_SUNKEN_SHIP,
    R181_SUNKEN_SHIP_POSTKC_AREA_03_ALLEY_RATS_ON_CANNONS: BF04_SUNKEN_SHIP,
    R182_SUNKEN_SHIP_POSTKC_AREA_07_THREE_DRY_BONES: BF04_SUNKEN_SHIP,
    R183_SUNKEN_SHIP_POSTKC_AREA_08_SECRET_ROOM_WITH_FROG_COIN: BF04_SUNKEN_SHIP,
    R184_SUNKEN_SHIP_POSTKC_AREA_09_HIDONS_ROOM_WSAVE_POINT: BF04_SUNKEN_SHIP,
    R185_SUNKEN_SHIP_POSTKC_AREA_14_SECRET_SAFETY_RING: BF04_SUNKEN_SHIP,
    R186_SUNKEN_SHIP_POSTKC_AREA_18_WARP_ROOM_FROM_JOHNNYS_ROOM: BF04_SUNKEN_SHIP,
    R187_SUNKEN_SHIP_POSTKC_AREA_10_WATER_ROOM_WITH_FROG_COINS: BF04_SUNKEN_SHIP,
    R188_SUNKEN_SHIP_POSTKC_AREA_11_WATER_ROOM_WITH_WHIRLPOOL: BF04_SUNKEN_SHIP,
    R189_MARIOS_PIPEHOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R190_MUSHROOM_KINGDOM_DURING_MACK_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R191_MUSHROOM_KINGDOM_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R192_BOOSTER_TOWER_9F_AREA_02_BOOSTERS_CURTAIN_GAME_ROOM: BF12_BOOSTER_TOWER,
    R193_BOOSTER_TOWER_2F_AREA_03_STEPS_WCIRCLING_BOBOMBS: BF12_BOOSTER_TOWER,
    R194_BOOSTER_TOWER_2F_AREA_02_BOOSTERS_RAILWAY_ROOM: BF12_BOOSTER_TOWER,
    R195_BOOSTER_TOWER_6F_AREA_02_BOOSTERS_ANCESTOR_GAME_ROOM: BF12_BOOSTER_TOWER,
    R196_BOOSTER_TOWER_2F_AREA_01_WCONSTANTLY_APPEARING_SPOOKUMS: BF12_BOOSTER_TOWER,
    R197_BOOSTER_TOWER_1F_AREA_02_HIGH_MASHER_ROOM_WTEETERTOTTER: BF12_BOOSTER_TOWER,
    R198_BOOSTER_TOWER_8F_AREA_03_3LEVEL_WONE_CHOMP: BF12_BOOSTER_TOWER,
    R199_BOOSTER_TOWER_9F_AREA_01_THREE_YELLOW_PLATFORMS_WSAVE_POINT: BF12_BOOSTER_TOWER,
    R200_BOOSTER_TOWER_6F_AREA_03_ELDERS_ROOM_WCHOMP: BF12_BOOSTER_TOWER,
    R201_BOOSTER_TOWER_6F_AREA_01_SMALL_ROOM_WSAVE_POINT: BF12_BOOSTER_TOWER,
    R202_BOOSTER_TOWER_ENTRANCE: BF09_GRASSLANDS,
    R203_MUSHROOM_WAY_AREA_01: BF09_GRASSLANDS,
    R204_MUSHROOM_WAY_AREA_02: BF09_GRASSLANDS,
    R205_MUSHROOM_WAY_AREA_03: BF09_GRASSLANDS,
    R206_BANDITS_WAY_AREA_05: BF09_GRASSLANDS,
    R207_BANDITS_WAY_AREA_02: BF09_GRASSLANDS,
    R208_SEASIDE_TOWN_DURING_YARIDOVICH_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R209_SEASIDE_TOWN_DURING_YARIDOVICH_INN_1F: BF28_MUSHROOM_KINGDOM,
    R210_SEASIDE_TOWN_DURING_YARIDOVICH_INN_2F: BF28_MUSHROOM_KINGDOM,
    R211_SEASIDE_TOWN_DURING_YARIDOVICH_ELDERS_HOUSE_1F: BF28_MUSHROOM_KINGDOM,
    R212_SEASIDE_TOWN_DURING_YARIDOVICH_ELDERS_HOUSE_2F: BF28_MUSHROOM_KINGDOM,
    R213_SEASIDE_TOWN_DURING_YARIDOVICH_BEETLES_ARE_USBOMB_SHOP: BF28_MUSHROOM_KINGDOM,
    R214_SEASIDE_TOWN_DURING_YARIDOVICH_WEAPONS_AND_ARMOR_SHOP: BF28_MUSHROOM_KINGDOM,
    R215_SEASIDE_TOWN_DURING_YARIDOVICH_HEALTH_FOOD_STORE_LEFTMOST: BF28_MUSHROOM_KINGDOM,
    R216_SEASIDE_TOWN_DURING_YARIDOVICH_MUSHROOM_BOY_SHOP_MIDDLE: BF28_MUSHROOM_KINGDOM,
    R217_SEASIDE_TOWN_DURING_YARIDOVICH_ACCESSORY_SHOP_RIGHTMOST: BF28_MUSHROOM_KINGDOM,
    R218_SEASIDE_TOWN_DURING_YARIDOVICH_SHED_UNUSED_BC_INACCESSIBLE: BF28_MUSHROOM_KINGDOM,
    R219_GAME_INTRO_SEA_SHORE_WITH_SUNKEN_SHIP: BF34_SEA_ENCLAVE,
    R220_SMITHY_FACTORY_AREA_02_WSAVE_POINT: BF19_SMITHY_FACTORY,
    R221_SMITHY_FACTORY_AREA_04_GREEN_SWITCH_WAMEBOIDS: BF19_SMITHY_FACTORY,
    R222_SMITHY_FACTORY_AREA_03_GLUM_REAPERS: BF19_SMITHY_FACTORY,
    R223_SMITHY_FACTORY_AREA_07_COUNT_DOWNS_ROOM: BF19_SMITHY_FACTORY,
    R224_FOREST_MAZE_AREA_01: BF00_FOREST_MAZE,
    R225_FOREST_MAZE_AREA_05_TREE_TRUNK_AREA: BF00_FOREST_MAZE,
    R226_FOREST_MAZE_AREA_02: BF00_FOREST_MAZE,
    R227_FOREST_MAZE_AREA_09_LEADS_TO_4PATH_MAZE: BF00_FOREST_MAZE,
    R228_FOREST_MAZE_AREA_04: BF00_FOREST_MAZE,
    R229_FOREST_MAZE_AREA_06: BF00_FOREST_MAZE,
    R230_FOREST_MAZE_4WAY_PATH_FROM_AREA_09: BF00_FOREST_MAZE,
    R231_FOREST_MAZE_SECRET_ENTRANCE: BF00_FOREST_MAZE,
    R232_FOREST_MAZE_BOWYERS_PRACTICE_PAD: BF01_FOREST_MAZE_BOWYERS_PAD,
    R233_FOREST_MAZE_AREA_03_UNDERGROUND: BF25_UNDERGROUND,
    R234_FOREST_MAZE_SECRET: BF25_UNDERGROUND,
    R235_FOREST_MAZE_AREA_08_UNDERGROUND: BF25_UNDERGROUND,
    R236_FOREST_MAZE_AREA_07_UNDERGROUND_WSLEEPING_WIGGLER: BF25_UNDERGROUND,
    R237_SMITHY_FACTORY_AREA_05_WSAVE_POINT: BF19_SMITHY_FACTORY,
    R238_SMITHY_FACTORY_FALL_FROM_LUGNUT_ROOMS_AREA_06_PRIOR: BF19_SMITHY_FACTORY,
    R239_SMITHY_FACTORY_AREA_06_ULTRA_HAMMER: BF19_SMITHY_FACTORY,
    R240_VOLCANO_AREA_21_DUMMY: BF20_BARREL_VOLCANO,
    R241_VOLCANO_AREA_02_DUMMY: BF20_BARREL_VOLCANO,
    R242_FOREST_MAZE_ALL_TREE_TRUNK_UNDERGROUND_AREAS: BF25_UNDERGROUND,
    R243_GAME_INTRO_MUSHROOM_KINGDOM_CASTLE_THRONE_ROOM: BF28_MUSHROOM_KINGDOM,
    R244_GAME_INTRO_YOSTER_ISLE_TALK_TO_YOSHI_RUN_AROUND: BF33_PLATEAUS,
    R245_GAME_INTRO_PIPE_VAULT_AREA_02_WTHWOMP: BF21_KERO_SEWERS,
    R246_GAME_INTRO_KERO_SEWERS_ENTRANCE: BF33_PLATEAUS,
    R247_GAME_INTRO_TADPOLE_POND_MARIO_SUMMONS_TADPOLES: BF33_PLATEAUS,
    R248_GAME_INTRO_MUSHROOM_WAY_AREA_01: BF09_GRASSLANDS,
    R249_GAME_INTRO_VISTA_HILL: BF10_MOUNTAINS,
    R250_GAME_INTRO_BOOSTER_TOWER_BALCONY_WITH_TOADSTOOL_CRYING: BF17_BOOSTER_TOWER_BALCONY,
    R251_BEAN_VALLEY_PIRANHA_PIPE_AREA: BF41_BEAN_VALLEY_GRASSLANDS,
    R252_BEAN_VALLEY_MAIN_AREA: BF41_BEAN_VALLEY_GRASSLANDS,
    R253_BEAN_VALLEY_MAGIC_BRICK_TO_BEANSTALK_AREA: BF41_BEAN_VALLEY_GRASSLANDS,
    R254_BEAN_VALLEY_SMILAX_AREA: BF41_BEAN_VALLEY_GRASSLANDS,
    R255_MONSTRO_TOWN_JINXS_DOJO: BF46_JINXS_DOJO,
    R256_FOREST_MAZE_SMALL_AREA_WTREE_TRUNK_UNUSED: BF00_FOREST_MAZE,
    R257_GAME_INTRO_FOREST_MAZE_FIGHTING_MAGIKOOPA_AT_BOWYERS_PAD: BF00_FOREST_MAZE,
    R258_BOOSTER_TOWER_BALCONY_AT_TOP_FLOOR: BF17_BOOSTER_TOWER_BALCONY,
    R259_BOOSTER_TOWER_3F_AREA_01_GREEN_SWITCH_FOR_BP_SECRET: BF12_BOOSTER_TOWER,
    R260_GAME_INTRO_FOREST_MAZE_JUMPING_ON_WIGGLER: BF00_FOREST_MAZE,
    R261_BOWSERS_KEEP_1ST_TIME_AREA_03_LAVA_ROOM_WBRIDGE: BF07_BOWSERS_KEEP,
    R262_LANDS_END_UNDERGROUND_AREA_04_BUY_SUPER_STARS: BF25_UNDERGROUND,
    R263_LANDS_END_UNDERGROUND_AREA_01: BF25_UNDERGROUND,
    R264_LANDS_END_UNDERGROUND_AREA_02: BF25_UNDERGROUND,
    R265_LANDS_END_UNDERGROUND_AREA_03: BF25_UNDERGROUND,
    R266_BOWSERS_KEEP_AREA_10_MAGIKOOPAS_ROOM: BF07_BOWSERS_KEEP,
    R267_MONSTRO_TOWN_ENTRANCE: BF33_PLATEAUS,
    R268_BELOME_TEMPLE_AREA_08_BELOMES_ROOM: BF42_BELOME_TEMPLE,
    R269_ENDING_CREDITS_NIMBUS_LAND_PRINCE_MALLOW: BF24_NIMBUS_LAND,
    R270_LANDS_END_SECRET_UNDERGROUND_AREA_01_LEADS_TO_KERO_SEWERS: BF25_UNDERGROUND,
    R271_MOLEVILLE_MINES_AREA_17_PUNCHINELLOS_ROOM_AFTER_BATTLE: BF05_MOLEVILLE_MINES,
    R272_MOLEVILLE_MINES_AREA_11_BOMBED_ROOM_WSINGING_MOLES: BF05_MOLEVILLE_MINES,
    R273_MOLEVILLE_MINES_AREA_04_WTRAMPOLINE: BF05_MOLEVILLE_MINES,
    R274_MOLEVILLE_MINES_AREA_02: BF05_MOLEVILLE_MINES,
    R275_MOLEVILLE_MINES_AREA_06_SMALL_ROOM_LEADING_TO_AREA_06: BF05_MOLEVILLE_MINES,
    R276_MOLEVILLE_MINES_AREA_01_ENTRANCE: BF05_MOLEVILLE_MINES,
    R277_MOLEVILLE_MINES_AREA_05_LEFT_OF_TRAMPOLINE_ROOM: BF05_MOLEVILLE_MINES,
    R278_MOLEVILLE_MINES_AREA_03_LEADS_BACK_TO_AREA_1: BF05_MOLEVILLE_MINES,
    R279_MOLEVILLE_MINES_AREA_08_CROCOS_BOMBED_ROOM: BF05_MOLEVILLE_MINES,
    R280_MOLEVILLE_MINES_AREA_15_2LEVEL_ROOM_WSPARKY_AND_10COIN_TC: BF05_MOLEVILLE_MINES,
    R281_MOLEVILLE_MINES_AREA_07_FROM_CROCOS_BOMBED_ROOM: BF05_MOLEVILLE_MINES,
    R282_MOLEVILLE_MINES_AREA_10_SMALL_ROOM_WMINECART_TRACKS: BF05_MOLEVILLE_MINES,
    R283_MOLEVILLE_MINES_AREA_09_LEADS_LEFT_TO_CROCOS_BOMBED_ROOM: BF05_MOLEVILLE_MINES,
    R284_MOLEVILLE_MINES_AREA_18_MINECART_ROOM: BF05_MOLEVILLE_MINES,
    R285_MOLEVILLE_MINES_AREA_13_LONG_MINECART_TRACKS_ROOM: BF05_MOLEVILLE_MINES,
    R286_MOLEVILLE_MINES_AREA_12_2LEVEL_ROOM_LEADS_TO_LONG_MINECART_TRACKS_ROOM: BF05_MOLEVILLE_MINES,
    R287_MOLEVILLE_MINES_AREA_14_2LEVEL_ROOM_FROM_LONG_MINECART_TRACKS_ROOM: BF05_MOLEVILLE_MINES,
    R288_MOLEVILLE_MINES_AREA_16_LARGE_SAVEPOINT_ROOM_WFOUR_BOBOMBS: BF05_MOLEVILLE_MINES,
    R289_MOLEVILLE_MINES_AREA_17_PUNCHINELLOS_ROOM_BEFORE_BATTLE: BF05_MOLEVILLE_MINES,
    R290_MOLEVILLE_MINES_AREA_19_FROM_OUTSIDE_AFTER_PAYING: BF05_MOLEVILLE_MINES,
    R291_GAME_INTRO_BOOSTER_TOWER_7F_PARACHUTING_SPOOKUMS: BF12_BOOSTER_TOWER,
    R292_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R293_BELOME_3_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R294_MARRYMORE_CHAPEL_CLONE_BOSS_LAUNCHER: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R295_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R296_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R297_UNMAPPED_OUTSIDE_TOWNPLACE_RESEMBLES_SEASIDE_TOWN: BF28_MUSHROOM_KINGDOM,
    R298_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R299_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R300_UNMAPPED_HOUSE_ROOM: BF11_MUSHROOM_KINGDOM_HOUSE,
    R301_KERO_SEWERS_AREA_07_WATER_SWITCH_ROOM_WBOOS: BF21_KERO_SEWERS,
    R302_KERO_SEWERS_AREA_08_BELOMES_ROOM: BF21_KERO_SEWERS,
    R303_KERO_SEWERS_AREA_08_BELOMES_ROOM_AFTER_DEFEAT: BF21_KERO_SEWERS,
    R304_SEASIDE_TOWN_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R305_SEASIDE_TOWN_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R306_SEASIDE_TOWN_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R307_SEASIDE_TOWN_ELDERS_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R308_SEASIDE_TOWN_ELDERS_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R309_SEASIDE_TOWN_BEETLES_ARE_US: BF11_MUSHROOM_KINGDOM_HOUSE,
    R310_SEASIDE_TOWN_WEAPON_AND_ARMOR_SHOP: BF11_MUSHROOM_KINGDOM_HOUSE,
    R311_SEASIDE_TOWN_HEALTH_FOOD_STORE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R312_SEASIDE_TOWN_MUSHROOM_BOYS_SHOP: BF11_MUSHROOM_KINGDOM_HOUSE,
    R313_SEASIDE_TOWN_ACCESSORY_SHOP: BF11_MUSHROOM_KINGDOM_HOUSE,
    R314_SEASIDE_TOWN_SHED: BF11_MUSHROOM_KINGDOM_HOUSE,
    R315_SEASIDE_TOWN_DURING_YARIDOVICH_BEACH: BF37_SEASIDE_TOWN_BEACH,
    R316_SEASIDE_TOWN_BEACH: BF37_SEASIDE_TOWN_BEACH,
    R317_LANDS_END_DESERT_AREA_01: BF43_LANDS_END_DESERT,
    R318_LANDS_END_DESERT_AREA_02: BF43_LANDS_END_DESERT,
    R319_LANDS_END_DESERT_AREA_06: BF43_LANDS_END_DESERT,
    R320_MUSHROOM_KINGDOM_CASTLE_ENTRANCE_TO_THRONE_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R321_BOWSERS_KEEP_6DOOR_ACTION_ROOM_2A_SLOW_ELEVATING_PLATFORMS: BF07_BOWSERS_KEEP,
    R322_BOWSERS_KEEP_6DOOR_ACTION_ROOM_1A_JUMPING_TERRAPIN: BF07_BOWSERS_KEEP,
    R323_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_ENTRANCE_TO_THRONE_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R324_MONSTRO_TOWN_OUTSIDE: BF33_PLATEAUS,
    R325_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_MAIN_HALL: BF13_MUSHROOM_KINGDOM_CASTLE,
    R326_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_THRONE_ROOM: BF15_MUSHROOM_KINGDOM_CASTLE,
    R327_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_STAIRWELL_TO_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R328_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R329_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_BRANCH_ROOM_TO_VAULTGUEST_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R330_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_GUEST_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R331_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_VAULT_UNUSED: BF13_MUSHROOM_KINGDOM_CASTLE,
    R332_MUSHROOM_KINGDOM_CASTLE_DURING_MACK_ENTRANCE_TO_TOADSTOOLS_ROOM: BF13_MUSHROOM_KINGDOM_CASTLE,
    R333_KERO_SEWERS_ENTRANCE: BF33_PLATEAUS,
    R334_BEAN_VALLEY_PIPE_ROOM_LEFTMOST_PIPE: BF49_BEAN_VALLEY_PIPE_ROOM,
    R335_BEAN_VALLEY_PIPE_ROOM_RIGHTMOST_PIPE_LARGE_ROOM: BF49_BEAN_VALLEY_PIPE_ROOM,
    R336_MOLEVILLE_ITEM_SHOP: BF10_MOUNTAINS,
    R337_MOLEVILLE_INN: BF10_MOUNTAINS,
    R338_MOLEVILLE_DYNA_AND_MITES_HOUSE: BF10_MOUNTAINS,
    R339_MOLEVILLE_FIREWORKS_SHOP: BF10_MOUNTAINS,
    R340_MOLEVILLE_SPECIAL_ITEMTRADING_SHOP: BF10_MOUNTAINS,
    R341_NIMBUS_LAND_GARROS_HOUSE: BF24_NIMBUS_LAND,
    R342_NIMBUS_LAND_LOWER_HOUSE: BF24_NIMBUS_LAND,
    R343_NIMBUS_LAND_INN: BF24_NIMBUS_LAND,
    R344_NIMBUS_LAND_ITEM_SHOP: BF24_NIMBUS_LAND,
    R345_NIMBUS_LAND_TOPRIGHT_HOUSE_CROCO_DROPS_SIGNAL_RING: BF24_NIMBUS_LAND,
    R346_NIMBUS_LAND_INN_BEDROOM: BF24_NIMBUS_LAND,
    R347_BEAN_VALLEY_PIPE_ROOM_TOP_PIPE_LEADS_TO_GRATE_GUYS_CASINO: BF49_BEAN_VALLEY_PIPE_ROOM,
    R348_BEAN_VALLEY_PIPE_ROOM_BOTTOM_LEFT: BF49_BEAN_VALLEY_PIPE_ROOM,
    R349_BEAN_VALLEY_PIPE_ROOM_BOTTOM_RIGHT: BF49_BEAN_VALLEY_PIPE_ROOM,
    R350_SMITHY_FACTORY_AREA_01: BF19_SMITHY_FACTORY,
    R351_CULEXS_ROOM: BF47_CULEX,
    R352_VOLCANO_AREA_21_CZAR_DRAGONS_ROOM: BF20_BARREL_VOLCANO,
    R353_VOLCANO_AREA_18_HINO_MART: BF20_BARREL_VOLCANO,
    R354_VOLCANO_AREA_01: BF20_BARREL_VOLCANO,
    R355_VOLCANO_AREA_03_SECRET_WTWO_FLOWERS: BF20_BARREL_VOLCANO,
    R356_VOLCANO_AREA_08: BF20_BARREL_VOLCANO,
    R357_VOLCANO_POSTCD_AREA_01: BF20_BARREL_VOLCANO,
    R358_VOLCANO_AREA_11: BF20_BARREL_VOLCANO,
    R359_VOLCANO_AREA_02: BF20_BARREL_VOLCANO,
    R360_VOLCANO_AREA_04_BUNCH_OF_STEPS: BF20_BARREL_VOLCANO,
    R361_VOLCANO_AREA_09: BF20_BARREL_VOLCANO,
    R362_VOLCANO_AREA_07_STOMPING_CORKPEDITE: BF20_BARREL_VOLCANO,
    R363_VOLCANO_AREA_15_STOMPING_CORKPEDITE: BF20_BARREL_VOLCANO,
    R364_VOLCANO_AREA_14: BF20_BARREL_VOLCANO,
    R365_VOLCANO_POSTCD_AREA_03: BF20_BARREL_VOLCANO,
    R366_VOLCANO_AREA_13_WSAVE_POINT: BF20_BARREL_VOLCANO,
    R367_VOLCANO_AREA_17_LEADS_TO_HINOPIOS_SHOP: BF20_BARREL_VOLCANO,
    R368_NIMBUS_LAND_ROYAL_BUS_STATION: BF24_NIMBUS_LAND,
    R369_NIMBUS_LAND_ENTRANCE_WWARP_TRAMPOLINE: BF24_NIMBUS_LAND,
    R370_NIMBUS_LAND_ENTRANCE_TO_HOT_SPRINGS: BF24_NIMBUS_LAND,
    R371_NIMBUS_LAND_FALL_FROM_PLATFORM_1ST: BF24_NIMBUS_LAND,
    R372_NIMBUS_LAND_FALL_FROM_PLATFORM_2ND: BF24_NIMBUS_LAND,
    R373_NIMBUS_LAND_FALL_FROM_PLATFORM_3RD: BF24_NIMBUS_LAND,
    R374_NIMBUS_LAND_FALL_FROM_PLATFORM_4TH: BF24_NIMBUS_LAND,
    R375_ENDING_CREDITS_STAR_PIECES_SHOOT_THROUGH_THE_SKY: BF36_STAR_HILL,
    R376_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_2B_1ST_FIGHT_CHEWY: BF07_BOWSERS_KEEP,
    R377_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_2C_1ST_FIGHT_SPARKY: BF07_BOWSERS_KEEP,
    R378_BEAN_VALLEY_BEANSTALKS_AREA_01: BF02_BEAN_VALLEY_BEANSTALKS,
    R379_BEAN_VALLEY_BEANSTALKS_AREA_02: BF02_BEAN_VALLEY_BEANSTALKS,
    R380_BEAN_VALLEY_BEANSTALKS_AREA_03_FROM_RIGHT_BEANSTALK_OF_AREA_02: BF02_BEAN_VALLEY_BEANSTALKS,
    R381_BEAN_VALLEY_BEANSTALKS_AREA_04_FROM_LEFT_BEANSTALK_OF_AREA_02: BF02_BEAN_VALLEY_BEANSTALKS,
    R382_NIMBUS_LAND_ENTRANCE_NO_TRAMPOLINESEXITS: BF24_NIMBUS_LAND,
    R383_VOLCANO_AREA_10_JUMPING_PYROSPHERES: BF20_BARREL_VOLCANO,
    R384_VOLCANO_AREA_05: BF20_BARREL_VOLCANO,
    R385_VOLCANO_AREA_06: BF20_BARREL_VOLCANO,
    R386_VOLCANO_AREA_12_ERUPTING_STUMPET: BF20_BARREL_VOLCANO,
    R387_VOLCANO_AREA_19_FROM_HINO_MART_WSAVE_POINT: BF20_BARREL_VOLCANO,
    R388_VOLCANO_POSTCD_AREA_02: BF20_BARREL_VOLCANO,
    R389_VOLCANO_AREA_20_JUMPING_PYROSPHERES: BF20_BARREL_VOLCANO,
    R390_VOLCANO_AREA_16_ERUPTING_STUMPET: BF20_BARREL_VOLCANO,
    R391_VOLCANO_POSTCD_AREA_04: BF20_BARREL_VOLCANO,
    R392_VOLCANO_POSTCD_AREA_06: BF20_BARREL_VOLCANO,
    R393_VOLCANO_POSTCD_AREA_07_WARP_TO_WORLD_MAP: BF20_BARREL_VOLCANO,
    R394_VOLCANO_POSTCD_AREA_05: BF20_BARREL_VOLCANO,
    R395_MONSTRO_TOWN_MONSTERMAMAS_HOUSE_1F: BF33_PLATEAUS,
    R396_MONSTRO_TOWN_MONSTERMAMAS_HOUSE_2F: BF33_PLATEAUS,
    R397_MONSTRO_TOWN_SUPERJUMPING_ROOM: BF33_PLATEAUS,
    R398_MONSTRO_TOWN_WEAPON_AND_ARMOR_SHOP: BF33_PLATEAUS,
    R399_MONSTRO_TOWN_3_MUSTY_FEARS_INN: BF33_PLATEAUS,
    R400_BOWSERS_KEEP_AREA_13_2ND_THRONE_ROOM_BOOMERS_ROOM: BF07_BOWSERS_KEEP,
    R401_LANDS_END_SECRET_UNDERGROUND_AREA_02_LEADS_TO_KERO_SEWERS: BF25_UNDERGROUND,
    R402_LANDS_END_DESERT_AREA_03: BF43_LANDS_END_DESERT,
    R403_LANDS_END_DESERT_AREA_05: BF43_LANDS_END_DESERT,
    R404_LANDS_END_DESERT_AREA_04: BF43_LANDS_END_DESERT,
    R405_BOOSTER_PASS_SECRET: BF10_MOUNTAINS,
    R406_FACTORY_GROUNDS_AREA_01_WITH_TOAD: BF48_FACTORY_GROUNDS,
    R407_LANDS_END_CLIFF_CLIMB_WSKY_TROOPAS: BF10_MOUNTAINS,
    R408_NIMBUS_CASTLE_AREA_14_RIGHTMOST_FRONT_DOOR_OF_LONG_5EXIT_ROOM: BF22_NIMBUS_CASTLE,
    R409_NIMBUS_CASTLE_AREA_09_BIRDOS_ROOM: BF22_NIMBUS_CASTLE,
    R410_NIMBUS_CASTLE_AREA_07_STRAIGHT_FROM_AREA_06_WLONG_STAIRCASE: BF22_NIMBUS_CASTLE,
    R411_NIMBUS_CASTLE_PATH_AFTER_THRONE_ROOM_1ST: BF22_NIMBUS_CASTLE,
    R412_NIMBUS_CASTLE_AREA_11_LONG_HALLWAY_DOOR_TO_KINGS_CELLAR: BF22_NIMBUS_CASTLE,
    R413_NIMBUS_CASTLE_KINGS_LOCKED_CELLAR: BF22_NIMBUS_CASTLE,
    R414_NIMBUS_CASTLE_AREA_08_FROM_AREA_07_GET_ROOM_KEY_1_HERE: BF22_NIMBUS_CASTLE,
    R415_NIMBUS_LAND_SMALL_PLATFORM_AFTER_NIMBUS_CASTLE_THRONE_PATHS: BF24_NIMBUS_LAND,
    R416_NIMBUS_LAND_OUTSIDE_BEFORE_VALENTINA: BF24_NIMBUS_LAND,
    R417_GARDENERS_HOUSE_OUTSIDE: BF28_MUSHROOM_KINGDOM,
    R418_GARDENERS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R419_LAZY_SHELL_CLOUD: BF02_BEAN_VALLEY_BEANSTALKS,
    R420_BELOME_TEMPLE_AREA_02_FORTUNE_ROOM: BF42_BELOME_TEMPLE,
    R421_BELOME_TEMPLE_AREA_04_ROOM_DETERMINED_BY_FORTUNE: BF42_BELOME_TEMPLE,
    R422_BELOME_TEMPLE_AREA_09_BELOMES_TREASURE_ROOM: BF42_BELOME_TEMPLE,
    R423_BELOME_TEMPLE_AREA_06_BELOMES_FORTUNE_ROOM_WELEVATING_PLATFORM: BF42_BELOME_TEMPLE,
    R424_BELOME_TEMPLE_AREA_03_PIPE_TO_ROOM_DETERMINED_BY_FORTUNE: BF42_BELOME_TEMPLE,
    R425_BELOME_TEMPLE_AREA_05_FROM_FORTUNE_ROOM: BF42_BELOME_TEMPLE,
    R426_BELOME_TEMPLE_AREA_07_PIPE_TO_BELOMES_ROOM: BF42_BELOME_TEMPLE,
    R427_BELOME_TEMPLE_AREA_10_PIPE_TO_MONSTRO_TOWN: BF42_BELOME_TEMPLE,
    R428_BELOME_TEMPLE_AREA_01_WWARP_TRAMPOLINE: BF42_BELOME_TEMPLE,
    R429_GAME_INTRO_NIMBUS_LAND_OUTSIDE_WITH_PATROLLING_BIRDIES: BF24_NIMBUS_LAND,
    R430_NIMBUS_LAND_OUTSIDE_DURING_VALENTINA: BF24_NIMBUS_LAND,
    R431_BOWSERS_KEEP_6DOOR_PUZZLE_ROOMS: BF07_BOWSERS_KEEP,
    R432_ENDING_CREDITS_JOHNNY_LOOKING_OUT_AT_SUNSET_ON_BEACH_SHORE: BF37_SEASIDE_TOWN_BEACH,
    R433_SMITHY_FACTORY_AREA_01_DUMMY: BF19_SMITHY_FACTORY,
    R434_SMITHY_FACTORY_AREA_09_FALLING_AXEM_REDS_ON_CONVEYOR_BELTS: BF19_SMITHY_FACTORY,
    R435_ENDING_CREDITS_BOWSERS_KEEP_BOWSER_TROOPS_REPAIR: BF07_BOWSERS_KEEP,
    R436_SMITHY_FACTORY_AREA_01_DUMMY: BF19_SMITHY_FACTORY,
    R437_NIMBUS_CASTLE_PATH_AFTER_THRONE_ROOM_3RD: BF22_NIMBUS_CASTLE,
    R438_NIMBUS_LAND_OUTSIDE_AFTER_VALENTINA: BF24_NIMBUS_LAND,
    R439_BOWSERS_KEEP_OUTSIDE_TALK_TO_EXOR: BF10_MOUNTAINS,
    R440_NIMBUS_CASTLE_AREA_13_THRONE_ROOM_AFTER_VALENTINA: BF22_NIMBUS_CASTLE,
    R441_ENDING_CREDITS_TOADOFSKY_CONDUCTS_CHOIR: BF33_PLATEAUS,
    R442_SMITHY_FACTORY_AREA_11_CONVEYOR_BELTS_SPAWNING_DRILL_BITS_AND_MACKS: BF19_SMITHY_FACTORY,
    R443_SMITHY_FACTORY_AREA_16_SMALL_ROOM_WTWO_TREASURES_AFTER_FALLING_YARIDOVICH_ROOM: BF19_SMITHY_FACTORY,
    R444_SMITHY_FACTORY_AREA_09_DUMMY: BF19_SMITHY_FACTORY,
    R445_SMITHY_FACTORY_AREA_10_FALL_FROM_AREA_09: BF19_SMITHY_FACTORY,
    R446_BOWSERS_KEEP_6DOOR_EXIT_ROOM_AFTER_FINISHING_4_DOORS: BF07_BOWSERS_KEEP,
    R447_NIMBUS_LAND_HOT_SPRINGS: BF24_NIMBUS_LAND,
    R448_BOWSERS_KEEP_AREA_09_TALL_ROOM_WSAVE_POINT: BF07_BOWSERS_KEEP,
    R449_BOWSERS_KEEP_AREA_11_THWOMPBULLET_ROOM_AFTER_MAGIKOOPAS_ROOM: BF07_BOWSERS_KEEP,
    R450_BOWSERS_KEEP_AREA_12_CROCOS_SHOP_2_AFTER_MAGIKOOPAS_ROOM: BF07_BOWSERS_KEEP,
    R451_BOWSERS_KEEP_AREA_07_150_COINS_AND_A_MUSHROOM: BF07_BOWSERS_KEEP,
    R452_BOWSERS_KEEP_AREA_06_SAVE_POINT_WCROCO_SHOP: BF07_BOWSERS_KEEP,
    R453_BOWSERS_KEEP_AREA_05_DARK_TUNNEL_AFTER_THRONE_ROOM: BF07_BOWSERS_KEEP,
    R454_BOWSERS_KEEP_AREA_08_ROOM_WITH_6_DOORS: BF07_BOWSERS_KEEP,
    R455_BOWSERS_KEEP_6DOOR_ACTION_ROOM_2C_VERY_SLOW_MOVING_CIRCLING_PLATFORMS: BF07_BOWSERS_KEEP,
    R456_BOWSERS_KEEP_6DOOR_ACTION_ROOM_1C_GORILLA_THROWING_BARRELS: BF07_BOWSERS_KEEP,
    R457_BOWSERS_KEEP_6DOOR_ACTION_ROOM_2B_CANNONBALL_RIDING: BF07_BOWSERS_KEEP,
    R458_BOWSERS_KEEP_6DOOR_ACTION_ROOM_1B_MOVING_PLATFORMS: BF07_BOWSERS_KEEP,
    R459_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_1A_1ST_FIGHT_TERRA_COTTA: BF07_BOWSERS_KEEP,
    R460_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_1B_1ST_FIGHT_ALLEY_RAT: BF07_BOWSERS_KEEP,
    R461_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_1C_1ST_FIGHT_BOBOMB: BF07_BOWSERS_KEEP,
    R462_BOWSERS_KEEP_6DOOR_BATTLE_ROOM_2A_1ST_FIGHT_GU_GOOMBA: BF07_BOWSERS_KEEP,
    R463_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_1B_BARRELCOUNTING: BF07_BOWSERS_KEEP,
    R464_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_1A_QUIZ: BF07_BOWSERS_KEEP,
    R465_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_2B_GREEN_SWITCHES: BF07_BOWSERS_KEEP,
    R466_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_1C_WORD_PROBLEM: BF07_BOWSERS_KEEP,
    R467_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_2A_COIN_COLLECTING: BF07_BOWSERS_KEEP,
    R468_BOWSERS_KEEP_6DOOR_PUZZLE_ROOM_2C_BALL_SOLITAIRE: BF07_BOWSERS_KEEP,
    R469_FACTORY_GROUNDS_AREA_01: BF48_FACTORY_GROUNDS,
    R470_FACTORY_GROUNDS_AREA_04_GUN_YOLKS_ROOM: BF48_FACTORY_GROUNDS,
    R471_FACTORY_GROUNDS_AREA_02: BF48_FACTORY_GROUNDS,
    R472_FACTORY_GROUNDS_AREA_03: BF48_FACTORY_GROUNDS,
    R473_SMITHY_FACTORY_AREA_13_BOWYERS_FALLING_DOWN_CONVEYOR_BELTS: BF19_SMITHY_FACTORY,
    R474_SMITHY_FACTORY_AREA_15_FALLING_YARIDOVICHS: BF19_SMITHY_FACTORY,
    R475_SMITHY_FACTORY_AREA_12_LOTS_OF_CONSECUTIVE_CONVEYOR_BELTS_AND_LILXXBOOS: BF19_SMITHY_FACTORY,
    R476_BOWSERS_KEEP_2ND_TIME_AREA_01: BF07_BOWSERS_KEEP,
    R477_BOWSERS_KEEP_2ND_TIME_AREA_02: BF07_BOWSERS_KEEP,
    R478_BOWSERS_KEEP_2ND_TIME_AREA_03_LAVA_ROOM_WBRIDGE: BF07_BOWSERS_KEEP,
    R479_BOWSERS_KEEP_2ND_TIME_AREA_04_THRONE_ROOM: BF07_BOWSERS_KEEP,
    R480_MUSHROOM_KINGDOM_DURING_MACK_JUMPING_KIDS_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R481_MUSHROOM_KINGDOM_DURING_MACK_JUMPING_KIDS_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R482_MUSHROOM_KINGDOM_DURING_MACK_RAZ_AND_RAINIS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R483_MUSHROOM_KINGDOM_DURING_MACK_ITEM_SHOP_TOP_FLOOR: BF11_MUSHROOM_KINGDOM_HOUSE,
    R484_MUSHROOM_KINGDOM_DURING_MACK_ITEM_SHOP_BASEMENT: BF11_MUSHROOM_KINGDOM_HOUSE,
    R485_MUSHROOM_KINGDOM_DURING_MACK_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R486_ENDING_CREDITS_STAR_PIECES_ROSE_TOWN_LAST_STAR_PIECE_TO_THANK_YOU: BF28_MUSHROOM_KINGDOM,
    R487_MUSHROOM_KINGDOM_DURING_MACK_RUNNING_KIDS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R488_MUSHROOM_KINGDOM_JUMPING_KIDS_HOUSE_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R489_MUSHROOM_KINGDOM_JUMPING_KIDS_HOUSE_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R490_MUSHROOM_KINGDOM_RAZ_AND_RAINIS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R491_MUSHROOM_KINGDOM_ITEM_SHOP_TOP_FLOOR: BF11_MUSHROOM_KINGDOM_HOUSE,
    R492_MUSHROOM_KINGDOM_ITEM_SHOP_BASEMENT: BF11_MUSHROOM_KINGDOM_HOUSE,
    R493_MUSHROOM_KINGDOM_INN_1F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R494_MUSHROOM_KINGDOM_INN_2F: BF11_MUSHROOM_KINGDOM_HOUSE,
    R495_MUSHROOM_KINGDOM_RUNNING_KIDS_HOUSE: BF11_MUSHROOM_KINGDOM_HOUSE,
    R496_FACTORY_GROUNDS_FIGHT_WITH_SMITHY_USES_SLEDGE: BF48_FACTORY_GROUNDS,
    R497_NIMBUS_CASTLE_AREA_06_DUMMY: BF22_NIMBUS_CASTLE,
    R498_NIMBUS_CASTLE_AREA_10_DUMMY: BF22_NIMBUS_CASTLE,
    R499_NIMBUS_CASTLE_AREA_05_LONG_5EXIT_ROOM_AFTER_VALENTINA: BF22_NIMBUS_CASTLE,
    R500_NIMBUS_CASTLE_AREA_04_DUMMY: BF22_NIMBUS_CASTLE,
    R501_NIMBUS_CASTLE_AREA_03_4WAY_PATH_AFTER_VALENTINA: BF22_NIMBUS_CASTLE,
    R502_NIMBUS_LAND_DREAM_CUSHION_DREAM_SMALL_CLOUD_PERSON_CHEERS_ON_MARIOBED_FLOATS: BF24_NIMBUS_LAND,
    R503_NIMBUS_LAND_DREAM_CUSHION_DREAM_HEAVY_TROOPA_LAYING_ON_MARIO: BF24_NIMBUS_LAND,
    R504_NIMBUS_LAND_DREAM_CUSHION_DREAM_TORTES_ARE_SEASONING_MARIO: BF24_NIMBUS_LAND,
    R505_ENDING_CREDITS_YOSTER_ISLE_CROCO_RACING_YOSHI: BF33_PLATEAUS,
    R506_ENDING_CREDITS_MARRYMORE_CHAPEL_BOOSTER_WEDDING_VALENTINA: BF35_MARRYMORE_CHAPEL_SANCTUARY,
    R507_SMITHY_FACTORY_AREA_08_TRAMPOLINE_AFTER_COUNT_DOWN: BF19_SMITHY_FACTORY,
    R508_SMITHY_FACTORY_AREA_14_WSAVE_POINT: BF19_SMITHY_FACTORY,
    R509_FACTORY_GROUNDS_SMITHYS_PAD: BF48_FACTORY_GROUNDS,
}
