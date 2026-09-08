from __future__ import annotations
from typing import TYPE_CHECKING
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import *
from randomizer.data.variables.room_names import *
from randomizer.data.variables.event_script_names import *
from randomizer.data.variables.action_script_names import *
from randomizer.data.variables.pack_names import *
from randomizer.logic.progression.prizes import *
from randomizer.types.flags import *
from randomizer.data.physical_objects.items import (BigCoinObject, DefaultItem, FlowerObject, FrogCoinObject, KeyObject, RecoveryMushroomObject, SmallCoinObject, SmallFrogCoinObject)
from randomizer.types.logic import (Inventory)
from randomizer.types.prize import (CharacterPrize, damaging_spell_prizes)
from randomizer.types.prizelocation import (CharacterRecruitmentLocation, StartingCharacterLocation, vanilla_spell_owner)
if TYPE_CHECKING:
    from randomizer.types.gameworld import (GameWorld)


def boss_slot_min_vram_cap_for_room(
    world: GameWorld,
    room_id: int,
    *,
    base_budget: int = 1,
    recruit_location: type[CharacterRecruitmentLocation] | None = None,
) -> int:
    """Compute an adaptive min_vram cap for a boss model slot in room_id.

    Starts from base_budget (the cap to use when nothing else is competing
    for VRAM in the room) and subtracts 1 row per known competing factor:

    * **Protagonist-driven ally buffer growth.** Calls
      Room.project_ally_sprite_buffer_size to see what
      ally_sprite_buffer_size will become for the current
      world.overworld_character. Bowser always pushes the ally buffer up;
      Peach/Geno can also push it up depending on the room's
      extra_sprite_actions. Each unit of growth above the room's stored
      value subtracts 1 from the cap.

    * **Bowser at the recruit slot.** If recruit_location is given and
      that location's prize is the Bowser ally, the recruit's room NPC
      becomes a non-gridplane cannot_clone, eating an extra row.

    Result is clamped to [0, base_budget]. Callers pass this as a
    min_vram_size_override / min_vram_from_seq0_override callable on
    a BossFightLocationNPC so boss model selection downgrades to a
    smaller variant when the room is tight.
    """
    cap = base_budget
    room = world.rooms._rooms[room_id]
    if room is not None and room.partition is not None and room.partition.ally_sprite_buffer_size > 0:
        projection = room.project_ally_sprite_buffer_size(world)
        if projection is not None:
            new_buf, _ = projection
            cap -= max(0, new_buf - room.partition.ally_sprite_buffer_size)
    if recruit_location is not None and recruit_location in world.locations:
        recruit_prize = world.get_location(recruit_location).prize
        if isinstance(recruit_prize, CharacterPrize) and recruit_prize.ally.index == 2:
            cap -= 1
    return max(0, cap)


def can_defeat_bosses(world: GameWorld, inventory: Inventory, count: int) -> bool:
    if world.settings.is_flag_value(
        ProgressionLogicDifficulty, ProgressionLogicDifficultyOptions.HARD
    ):
        return True
    return inventory.has_item_count(BossFightPrize, count)


def almost_earlygame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 3)


def is_midgame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 6)

def not_earlygame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 10)

def lategame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 15)

def expect_halfway_decent_movement(world: GameWorld, inventory: Inventory) -> bool:
    if world.settings.is_flag_value(
        ProgressionLogicDifficulty, ProgressionLogicDifficultyOptions.NORMAL
    ):
        return almost_earlygame(world, inventory)
    return True

def expect_ok_movement(world: GameWorld, inventory: Inventory) -> bool:
    if world.settings.is_flag_value(
        ProgressionLogicDifficulty, ProgressionLogicDifficultyOptions.NORMAL
    ):
        return is_midgame(world, inventory)
    return True

def expect_good_movement(world: GameWorld, inventory: Inventory) -> bool:
    if world.settings.is_flag_value(
        ProgressionLogicDifficulty, ProgressionLogicDifficultyOptions.NORMAL
    ):
        return not_earlygame(world, inventory)
    return True


def is_early_midgame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 10)


def is_late_midgame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 20)


def is_lategame(world: GameWorld, inventory: Inventory) -> bool:
    return can_defeat_bosses(world, inventory, 30)

def can_access_bandits_way(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Bandit's Way."""
    if world.settings.is_flag_value(BanditsWayGate, BanditsWayGating.MALLOW):
        return inventory.has_item(MallowRecruitmentPrize)
    if world.settings.is_flag_value(BanditsWayGate, BanditsWayGating.HAMMER_BRO):
        return inventory.has_item(HammerBrosFight)
    # Mushroom Way: true
    return True


def can_access_sewer(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Kero Sewers."""
    if can_dodge_lands_end_enemies(world, inventory):
        return True
    if world.settings.is_flag_value(KeroSewersGate, KeroSewersGating.MALLOW):
        return inventory.has_item(MallowRecruitmentPrize)
    if world.settings.is_flag_value(KeroSewersGate, KeroSewersGating.MACK):
        return inventory.has_item(MackBossFight)
    if world.settings.is_flag_value(KeroSewersGate, KeroSewersGating.KINGDOM):
        return can_access_bandits_way(world, inventory)
    if world.settings.is_flag_value(KeroSewersGate, KeroSewersGating.RFC):
        return can_access_bandits_way(world, inventory) and inventory.has_item(
            RareFrogCoinPrize
        )
    return True


def can_access_forest(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Forest Maze."""
    if world.settings.is_flag_value(ForestMazeGate, ForestMazeGating.PIE):
        return inventory.has_item(CricketPiePrize)
    return True


def can_clear_forest(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Forest Maze."""
    return can_access_forest(world, inventory) and almost_earlygame(world, inventory)


def can_access_pipe_vault(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Pipe Vault."""
    if world.settings.is_flag_value(PipeVaultGate, PipeVaultGating.GENO):
        return inventory.has_item(GenoRecruitmentPrize)
    if world.settings.is_flag_value(PipeVaultGate, PipeVaultGating.FOREST):
        return can_clear_forest(world, inventory)
    if world.settings.is_flag_value(PipeVaultGate, PipeVaultGating.BOWYER):
        return inventory.has_item(BowyerBossFight)
    return True


def can_do_mushroom_derby(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to do the curtain game in Booster Tower."""
    if world.settings.isflag_enabled(ShuffleCookies) and not inventory.has_item(
        CookiesPrize
    ):
        return False
    return can_access_pipe_vault(world, inventory)


def can_access_moleville_entrance(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the uper entrance to the mines."""
    if not expect_halfway_decent_movement(world, inventory):
        return False
    if world.settings.is_flag_value(Moleville1Gate, Moleville1Gating.GENO):
        return inventory.has_item(GenoRecruitmentPrize) 
    if world.settings.is_flag_value(Moleville1Gate, Moleville1Gating.FOREST):
        return can_access_forest(world, inventory) 
    if world.settings.is_flag_value(Moleville1Gate, Moleville1Gating.BOWYER):
        return inventory.has_item(BowyerBossFight)
    if world.settings.is_flag_value(Moleville1Gate, Moleville1Gating.BOSHI):
        return can_do_mushroom_derby(world, inventory) 
    return True


def can_access_inner_mines(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the inner half
    of Moleville Mines (beyond the exploding wall)."""
    return can_access_moleville_entrance(world, inventory) and inventory.has_item(
        BambinoBombPrize
    )


def can_clear_mines(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Moleville Mines."""
    return can_access_inner_mines(world, inventory) and almost_earlygame(world, inventory)


def can_access_moleville_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the postgame boss at Moleville."""
    return (
        can_access_inner_mines(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )


def can_access_tower(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to enter Booster Tower."""
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MARIO):
        return inventory.has_item(MarioRecruitmentPrize) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MALLOW):
        return inventory.has_item(MallowRecruitmentPrize) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.GENO):
        return inventory.has_item(GenoRecruitmentPrize) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.BOWSER):
        return inventory.has_item(BowserRecruitmentPrize) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.TOADSTOOL):
        return inventory.has_item(ToadstoolRecruitmentPrize) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.MINES):
        return can_access_inner_mines(world, inventory) and expect_halfway_decent_movement(world, inventory)
    if world.settings.is_flag_value(BoosterTowerGate, BoosterTowerGating.PUNCHINELLO):
        return inventory.has_item(PunchinelloBossFight) and expect_halfway_decent_movement(world, inventory)
    return expect_halfway_decent_movement(world, inventory)


def can_do_tower_curtain_game(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to do the curtain game in Booster Tower."""
    if world.settings.isflag_enabled(ShuffleMarioDoll) and not inventory.has_item(
        MarioDollPrize
    ):
        return False
    return can_access_tower(world, inventory)


def can_clear_tower(world: GameWorld, inventory: Inventory) -> bool:
    return can_do_tower_curtain_game(world, inventory) and almost_earlygame(world, inventory)


def can_access_tower_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the postgame boss at Booster Tower."""
    return (
        can_clear_tower(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )


def can_access_hill(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Booster Hill."""
    if world.settings.is_flag_value(BoosterHillGate, BoosterHillGating.TOWER):
        return can_clear_tower(world, inventory)
    if world.settings.is_flag_value(BoosterHillGate, BoosterHillGating.KGGG):
        return inventory.has_item(KnifeGuyGrateGuyBossFight)
    return True


def can_access_chapel(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to enter the Marrymore chapel."""
    if world.settings.is_flag_value(MarrymoreGate, MarrymoreGating.TOWER):
        return can_clear_tower(world, inventory)
    if world.settings.is_flag_value(MarrymoreGate, MarrymoreGating.KGGG):
        return inventory.has_item(KnifeGuyGrateGuyBossFight)
    if world.settings.is_flag_value(MarrymoreGate, MarrymoreGating.HILL):
        return can_access_hill(world, inventory)
    return True


def can_clear_chapel(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the boss of Marrymore."""
    has_gear = inventory.has_item(ShoesPrize) and inventory.has_item(RingPrize) and inventory.has_item(BroochPrize) and inventory.has_item(CrownPrize)
    if not world.settings.isflag_enabled(ShuffleWeddingGear):
        has_gear = True
    return (
        has_gear and can_access_chapel(world, inventory) and is_midgame(world, inventory)
    )


def can_access_chapel_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the postgame boss at Marrymore."""
    return (
        can_clear_chapel(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )


def can_access_sea(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the Sea."""
    if world.settings.is_flag_value(SeaGate, SeaGating.TOADSTOOL):
        return inventory.has_item(ToadstoolRecruitmentPrize)
    if world.settings.is_flag_value(SeaGate, SeaGating.STAR_4):
        return inventory.has_item_count(StarPiecePrize, 4)
    if world.settings.is_flag_value(SeaGate, SeaGating.BUNDT):
        return inventory.has_item(BundtBossFight)
    if world.settings.is_flag_value(SeaGate, SeaGating.MARRYMORE):
        return can_clear_chapel(world, inventory)
    return True


def can_access_early_ship(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Sunken Ship."""
    return can_access_sea(world, inventory) and expect_ok_movement(world, inventory)


def can_clear_ship(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Sunken Ship."""
    return can_access_early_ship(world, inventory) and is_midgame(world, inventory)


def can_access_ship_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the postgame boss at Sunken Ship."""
    return (
        can_clear_ship(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )


def can_access_seaside_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the Seaside Town boss."""
    if world.settings.is_flag_value(YaridovichGate, YaridovichGating.SHIP):
        return can_clear_ship(world, inventory)
    if world.settings.is_flag_value(YaridovichGate, YaridovichGating.JOHNNY):
        return inventory.has_item(JohnnyBossFight)
    return True


def can_clear_seaside_boss(world: GameWorld, inventory: Inventory) -> bool:
    return can_access_seaside_boss(world, inventory) and is_midgame(world, inventory)


def can_access_lands_end(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Land's End."""
    if world.settings.is_flag_value(LandsEndGate, LandsEndGating.STAR_5):
        return inventory.has_item_count(StarPiecePrize, 5)
    if world.settings.is_flag_value(LandsEndGate, LandsEndGating.ELDER):
        return can_access_seaside_boss(world, inventory) and inventory.has_item(
            ShedKeyPrize
        )
    if world.settings.is_flag_value(LandsEndGate, LandsEndGating.YARIDOVICH):
        return inventory.has_item(YaridovichBossFight)
    if world.settings.is_flag_value(LandsEndGate, LandsEndGating.SEASIDE):
        return can_clear_seaside_boss(world, inventory)
    return True


def can_dodge_lands_end_enemies(world: GameWorld, inventory: Inventory) -> bool:
    return can_access_lands_end(world, inventory) and expect_ok_movement(world, inventory)


def can_pass_whirlpools(world: GameWorld, inventory: Inventory) -> bool:
    if world.settings.isflag_enabled(SkipAnts):
        return can_dodge_lands_end_enemies(world, inventory)
    return can_dodge_lands_end_enemies(world, inventory) and is_midgame(world, inventory)

def can_access_temple(world: GameWorld, inventory: Inventory) -> bool:
    if not world.settings.isflag_enabled(EXPStarsAnywhere):
        return can_pass_whirlpools(world, inventory)
    return can_pass_whirlpools(world, inventory) and is_midgame(world, inventory)


def can_access_temple_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Belome Temple."""
    if world.settings.is_flag_value(BelomeTempleGate, BelomeTempleGating.KEY):
        return inventory.has_item(TempleKeyPrize) and can_dodge_lands_end_enemies(
            world, inventory
        ) and is_midgame(world, inventory)
    return can_dodge_lands_end_enemies(world, inventory) and is_midgame(world, inventory)


def can_clear_temple_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Belome Temple."""
    return can_access_temple_boss(world, inventory)


def can_access_temple_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the postgame boss at Belome Temple."""
    return (
        can_clear_temple_boss(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )


def can_access_monstro_town(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Monstro Town."""
    if world.settings.is_flag_value(MonstroTownGate, MonstroTownGating.LANDS_END):
        return can_access_temple_boss(world, inventory) and not_earlygame(
            world, inventory
        )
    if world.settings.is_flag_value(MonstroTownGate, MonstroTownGating.BELOME_2):
        return inventory.has_item(Belome2BossFight)
    return True 


def can_access_fifth_dojo_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the 5th Monstro dojo boss."""
    return (
        can_access_monstro_town(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and lategame(world, inventory)
    )

def can_access_valley(world: GameWorld, inventory: Inventory) -> bool:
    return expect_good_movement(world, inventory)


def can_do_valley_pipes(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear the pipes."""
    # You're expected to have the lamb's lure and be able to despawn the chewies.
    # The chewies are also the only fight in the game that rolls a formation at random on contact without needing to room-reload. 

    if (inventory.has_item_count(ProgressiveEggPrize, 2) and not world.settings.isflag_enabled(EnemyFormations) and not world.settings.is_flag_value(EnemyStats, EnemyStatsShuffleOptions.FULL_RANDOM)) and (world.settings.isflag_enabled(SeeYa) or inventory.has_item(SeeYaPrize)):
        return can_access_valley(world, inventory)
    return not_earlygame(world, inventory)

def can_clear_valley(world, inventory):
    return can_access_valley(world, inventory) and not_earlygame(world, inventory)


def can_access_outer_nimbus(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to get to Nimbus Land."""
    if world.settings.is_flag_value(NimbusGate, NimbusGating.VALLEY):
        return can_clear_valley(world, inventory)
    if world.settings.is_flag_value(NimbusGate, NimbusGating.MEGASMILAX):
        return inventory.has_item(MegasmilaxBossFight)
    return True


def can_access_juice_bar_alto(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to shop at the Alto Card juice bar."""
    return inventory.has_item_count(ProgressiveCardPrize, 1)


def can_access_juice_bar_tenor(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to shop at the Tenor Card juice bar."""
    return inventory.has_item_count(ProgressiveCardPrize, 2)


def can_access_juice_bar_soprano(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to shop at the Soprano Card juice bar."""
    return inventory.has_item_count(ProgressiveCardPrize, 3)


def can_enter_statue_game(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Nimbus Castle."""
    outer_access = can_access_outer_nimbus(world, inventory)
    if world.settings.is_flag_value(NimbusGate, NimbusGating.PAINT):
        return outer_access and inventory.has_item(GoldPaintPrize)
    return outer_access


def can_access_nimbus_castle(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Nimbus Castle."""
    return can_enter_statue_game(world, inventory) and expect_good_movement(world, inventory)


def can_access_inner_nimbus(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to get past the Castle Key 1 door."""
    return can_access_nimbus_castle(world, inventory) and inventory.has_item(
        CastleKey1Prize
    )


def can_access_late_nimbus(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to get past the Castle Key 2 door."""
    return can_access_inner_nimbus(world, inventory) and inventory.has_item(
        CastleKey2Prize
    )


def can_clear_nimbus_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear the Nimbus Land boss."""
    return can_access_late_nimbus(world, inventory) and not_earlygame(world, inventory)


def can_access_volcano(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Barrel Volcano."""
    if world.settings.is_flag_value(BarrelVolcanoGate, BarrelVolcanoGating.NIMBUS):
        return can_clear_nimbus_boss(world, inventory)
    if world.settings.is_flag_value(BarrelVolcanoGate, BarrelVolcanoGating.VALENTINA):
        return inventory.has_item(ValentinaBossFight) and expect_good_movement(world, inventory)
    return expect_good_movement(world, inventory)


def can_clear_volcano(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to clear Barrel Volcano."""
    return can_access_volcano(world, inventory) and not_earlygame(world, inventory)


def can_access_keep(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access Bowser's Keep."""
    if world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.VOLCANO):
        return can_clear_volcano(world, inventory)
    if world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.STAR_6):
        return inventory.has_item_count(StarPiecePrize, 6) and expect_good_movement(world, inventory)
    if world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.AXEM):
        return inventory.has_item(AxemRangersBossFight) and expect_good_movement(world, inventory)
    return expect_good_movement(world, inventory)


def can_pass_obstacle_courses(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to pass the obstacle courses in Bowser's Keep."""
    return can_access_keep(world, inventory) and can_damage_enemies_with_spells(
        world, inventory
    ) and not_earlygame(world, inventory)


def can_exit_keep(world: GameWorld, inventory: Inventory) -> bool:
    if world.settings.is_flag_value(BowserDoorRequirements, 6) or world.settings.isflag_enabled(BowserDoorShuffle):
        return can_pass_obstacle_courses(world, inventory)
    if world.settings.is_flag_value(BowserDoorRequirements, 5):
        return is_midgame(world, inventory)
    return expect_good_movement(world, inventory)


def can_clear_keep(world: GameWorld, inventory: Inventory) -> bool:
    return can_exit_keep(world, inventory) and not_earlygame(world, inventory)
        
    

def can_access_factory(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the Outer Factory."""
    if world.settings.is_flag_value(FactoryGate, FactoryGating.STAR_6):
        return (
            inventory.has_item_count(StarPiecePrize, 6)
            and can_access_keep(world, inventory)
            and expect_good_movement(world, inventory)
        )
    if world.settings.is_flag_value(FactoryGate, FactoryGating.EXOR):
        return (
            inventory.has_item(ExorBossFight)
            and can_access_keep(world, inventory)
            and expect_good_movement(world, inventory)
        )
    if world.settings.is_flag_value(FactoryGate, FactoryGating.OPEN):
        return can_access_keep(world, inventory) and expect_good_movement(world, inventory)
    if world.settings.is_flag_value(FactoryGate, FactoryGating.KEEP):
        return can_clear_keep(world, inventory) and expect_good_movement(world, inventory)
    return expect_good_movement(world, inventory)


def can_defeat_factory_bosses(world: GameWorld, inventory: Inventory) -> bool:
    return can_access_factory(world, inventory) and lategame(world, inventory)


def can_access_inner_factory_final_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the final Factory boss."""
    value = world.settings.get_flag(StarPiecesRequired).value
    has_stars = inventory.has_item_count(StarPiecePrize, value)
    if world.settings.is_flag_value(FireworksSetting, FireworksOptions.SHUFFLE_ONE):
        fireworks_access = inventory.has_item(RegularFireworksPrize)
    elif world.settings.is_flag_value(FireworksSetting, FireworksOptions.PROGRESSIVE):
        fireworks_access = inventory.has_item_count(ProgressiveFireworksPrize, 3)
    else:
        fireworks_access = True
    can_access_bucket = (
        fireworks_access
        and can_clear_mines(world, inventory)
        and world.settings.isflag_enabled(BucketWarp)
    )
    can_access_casino = world.settings.isflag_enabled(
        CasinoWarp
    ) and inventory.has_item(BrightCardPrize)
    return (
        has_stars
        and (
            can_access_bucket
            or can_access_casino
            or can_defeat_factory_bosses(world, inventory)
        )
        and lategame(world, inventory)
    )


def can_access_sealed_door_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the sealed door boss."""
    boss_reqs = can_access_monstro_town(world, inventory) and lategame(
        world, inventory
    )
    item_reqs: bool = False
    if world.settings.is_flag_value(FireworksSetting, FireworksOptions.SHUFFLE_ONE):
        item_reqs = inventory.has_item(RegularFireworksPrize) and can_clear_mines(
            world, inventory
        )
    elif world.settings.is_flag_value(FireworksSetting, FireworksOptions.PROGRESSIVE):
        item_reqs = inventory.has_item_count(ProgressiveFireworksPrize, 2)
    else:
        item_reqs = can_clear_mines(world, inventory)
    return item_reqs and boss_reqs


def can_access_sealed_postgame_boss(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to access the second sealed door boss."""
    return (
        can_access_sealed_door_boss(world, inventory)
        and inventory.has_item(StayVoucherPrize)
        and inventory.has_item(ExtraShinyStonePrize)
        and lategame(world, inventory)
    )


def can_damage_enemies_with_spells(world: GameWorld, inventory: Inventory) -> bool:
    """If true, the player is expected to be able to damage enemies with a spell.

    Any damaging spell counts, whatever its element. FORMLESS transforms into
    Mokura off a counter on IfTargetedByCommand([COMMAND_SPECIAL]) (monster
    script 147), which no element can dodge, and Mokura merely resists (not
    nullifies) Thunder and Jump.
    """
    pool = damaging_spell_prizes()
    if not world.settings.isflag_enabled(
        CharacterLearnedSpells
    ) and not world.settings.isflag_enabled(SpellsAnywhere):
        # Spells aren't shuffled, so check if the player has recruited a character
        # whose vanilla spells include a damage spell that isn't disabled.
        disabled_spells: set[type] = {
            m.value for m in world.settings.get_flag(AvailableSpells).disabled
        }
        for spell_prize in pool:
            if spell_prize._spell in disabled_spells:
                continue
            owner = vanilla_spell_owner(spell_prize)
            if owner is not None and inventory.has_item(owner):
                return True
        return False
    return inventory.has_one_of(list(pool))


def is_all_starting_chars_set(world: GameWorld, inventory: Inventory | None = None):
    """Check if all starting character slots are filled.

    If inventory is provided, also counts character prizes in the inventory
    as "effectively set" for assumed-reachability placement.
    """
    strchars = world.settings.get_flag(StartingCharacters)
    startmax = len(strchars.enabled)

    # Count how many character prizes are in the assumed inventory
    chars_in_inventory = 0
    if inventory is not None:
        chars_in_inventory = sum(
            1 for item in inventory if isinstance(item, CharacterPrize)
        )

    # Starting-character locations in slot order (STARTER_CHARACTER_1..5), found
    # by base class so access.py needs no import of the concrete location files.
    starter_slots = sorted(
        (
            (cls, loc)
            for cls, loc in world.locations.items()
            if issubclass(cls, StartingCharacterLocation)
            and cls is not StartingCharacterLocation
        ),
        key=lambda pair: pair[0].__name__,
    )
    unfilled_slots = sum(
        1 for _, loc in starter_slots[:startmax] if loc.prize is None
    )

    # All starting chars are "effectively set" if the inventory has enough
    # character prizes to fill the unfilled slots
    return chars_in_inventory >= unfilled_slots


