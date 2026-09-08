"""Enemy randomization logic."""
from __future__ import annotations
import random
from typing import TYPE_CHECKING, cast

from smrpgpatchbuilder.datatypes.spells.enums import Element, Status
from smrpgpatchbuilder.datatypes.enemies.enums import FlowerBonusType
from smrpgpatchbuilder.datatypes.battles.formations_packs.types.classes import (
    Formation,
    FormationMember,
)

from randomizer.data.packs.pack_collection import *
from randomizer.data.enemies.enemies import (
    ALLEYRATEnemy,
    AMANITAEnemy,
    AMEBOIDEnemy,
    BIRDYEnemyStatic,
    BLOOBEREnemyStatic,
    BLUEBIRDEnemyStatic,
    BOBOMBEnemyStatic,
    BUZZEREnemy,
    CHEWYEnemy,
    CHOMPEnemy,
    CHOWEnemy,
    CROOKEnemyStatic,
    DRYBONESEnemy,
    GECKITEnemy,
    GECKOEnemy,
    GLUMREAPEREnemy,
    GOOMBAEnemy,
    GREAPEREnemy,
    GUGOOMBAEnemy,
    HEAVYTROOPAEnemy,
    K9Enemy,
    LAKITUEnemy,
    LILBOOEnemy,
    MACHINEMADEAxemRedEnemy,
    MAGMITEEnemy,
    MAGMUSEnemy,
    MALAKOOPAEnemy,
    MRKIPPEREnemy,
    MUKUMUKUEnemy,
    NINJAEnemy,
    OERLIKONEnemy,
    PINWHEELEnemy,
    PYROSPHEREEnemy,
    RATFUNKEnemy,
    ROBOMBEnemy,
    SACKITEnemy,
    SHAMANEnemy,
    SHYAWAYEnemy,
    SHYGUYEnemyStatic,
    SKYTROOPAEnemy,
    SLINGSHYEnemy,
    SPARKYEnemy,
    SPIKESTEREnemy,
    SPIKEYEnemy,
    SPOOKUMEnemy,
    STARSLAPEnemy,
    STINGEREnemy,
    TERRACOTTAEnemy,
    THEBIGBOOEnemy,
    VOMEREnemy,
    ZEOSTAREnemy,
)

from ..utils import mutate_normal
from randomizer.types.spell import EnemySpell
from randomizer.data.enemies.enemies import (
        SMITHY2Enemy,
        SMITHYTankEnemy,
        SMITHYSafeEnemy2,
        SMITHYMageEnemy,
        SMITHYChestEnemy,
        STRONGBOBOMB1Enemy,
        STRONGBOBOMB2Enemy,
        STRONGBOBOMB3Enemy,
        STRONGBOBOMB4Enemy,
        BOOSTERDUMMY,
    )
from randomizer.types.flags import EnemyStats, EnemyStatsShuffleOptions
from randomizer.types.enemy import Enemy as CustomEnemy
from randomizer.logic.pre_shuffle.enemy_tweaks import _get_enemy_lists
from randomizer.logic.scanline_calculator import (
        get_scanline_footprint,
        find_valid_coordinates,
    )
from randomizer.types.prize import BossFightPrize
from randomizer.logic.scanline_calculator import clear_footprint_cache
from randomizer.logic.battle_vram_calculator import VANILLA_MAX_NONBOSS_UNIQUE_VRAM
from randomizer.types.flags import EXPMultiplier, EXPMultiplierOptions
from randomizer.data.items.items import (
    AbleJuiceItem,
    BadMushroomItem,
    BracerItem,
    CrystallineItem,
    ElixirItem,
    EnergizerItem,
    FireBombItem,
    FlowerBoxItem,
    FlowerJarItem,
    FlowerTabItem,
    FreshenUpItem,
    FrightBombItem,
    FroggieDrinkItem,
    HoneySyrupItem,
    IceBombItem,
    KerokeroColaItem,
    MapleSyrupItem,
    MaxMushroomItem,
    MegalixirItem,
    MidMushroomItem,
    MoldyMushItem,
    MukuCookieItem,
    MushroomItem,
    MushroomItem2,
    PickMeUpItem,
    PowerBlastItem,
    PureWaterItem,
    RedEssenceItem,
    RockCandyItem,
    RottenMushItem,
    RoyalSyrupItem,
    SleepyBombItem,
    WiltShroomItem,
    YoshiAdeItem,
    YoshiCandyItem,
    YoshiCookieItem,
)

if TYPE_CHECKING:
    from smrpgpatchbuilder.datatypes.items.classes import RegularItem
    from ...types.gameworld import GameWorld


def randomize_enemy_attacks_and_spells(world: GameWorld) -> None:
    """Randomize enemy spell and attack stats and effects."""

    # Status effects that can be randomly assigned (excluding berserk for safety)
    safe_statuses = [
        Status.MUTE,
        Status.SLEEP,
        Status.POISON,
        Status.FEAR,
        Status.MUSHROOM,
        Status.SCARECROW,
    ]

    for spell in world.spells.spells:
        if not isinstance(spell, EnemySpell):
            continue

        # Mutate FP cost (max 31 due to game limitation)
        new_fp = mutate_normal(int(spell.fp), minimum=1, maximum=31)
        spell.set_fp(new_fp)

        if spell.status_effects:
            num_effects = len(spell.status_effects)
            new_effects = random.sample(
                safe_statuses, min(num_effects, len(safe_statuses))
            )
            spell.set_status_effects(new_effects)

        new_power = mutate_normal(int(spell.power), minimum=0, maximum=255)
        spell.set_power(int(max(0, min(255, new_power))))

        # Mutate hit rate (cap at 99 if it's an instant KO spell)
        max_hit = 99 if spell.check_ohko else 100
        new_hit_rate = mutate_normal(int(spell.hit_rate), minimum=1, maximum=max_hit)
        spell.set_hit_rate(new_hit_rate)

    for attack in world.enemy_attacks.attacks:
        # Mutate attack level (0-7 range)
        new_level = mutate_normal(int(attack.attack_level), minimum=0, maximum=7)
        attack.set_attack_level(new_level)

        if attack.status_effects:
            num_effects = len(attack.status_effects)
            new_effects = random.sample(
                safe_statuses, min(num_effects, len(safe_statuses))
            )
            attack.set_status_effects(new_effects)

        # Mutate hit rate (cap at 99 if OHKO to allow protection to work, 100 otherwise)
        max_hit = 99 if attack.ohko else 100
        new_hit_rate = mutate_normal(int(attack.hit_rate), minimum=1, maximum=max_hit)
        attack.set_hit_rate(new_hit_rate)

        # Punchinello 2 Bob-Omb Blast (attack 78) must always hit
        if int(attack.index) == 78:
            attack.set_hit_rate(100)


def randomize_enemy_stats(world: GameWorld) -> None:
    """Randomize enemy stats based on EnemyStats flag setting."""
    strong_bobomb_types = (
        STRONGBOBOMB1Enemy, STRONGBOBOMB2Enemy,
        STRONGBOBOMB3Enemy, STRONGBOBOMB4Enemy,
    )

    all_enemies = list(world.enemies.enemies)

    sidekick_types, boss_types = _get_enemy_lists()
    boss_related_types = set(sidekick_types) | set(boss_types)

    # Capture original vanilla stats BEFORE any shuffling for ±50% clamping
    # Also capture disable_auto_death to ensure it's never changed
    original_stats: dict[int, dict[str, int]] = {}
    original_disable_auto_death: dict[int, bool] = {}
    for enemy in all_enemies:
        original_stats[id(enemy)] = {
            "hp": int(enemy.hp),
            "speed": int(enemy.speed),
            "attack": int(enemy.attack),
            "defense": int(enemy.defense),
            "magic_attack": int(enemy.magic_attack),
            "magic_defense": int(enemy.magic_defense),
            "fp": int(enemy.fp),
        }
        original_disable_auto_death[id(enemy)] = enemy.disable_auto_death

    if (
        world.settings.get_flag(EnemyStats).selected
        != EnemyStatsShuffleOptions.DISABLED
    ):

        full_random = (
            world.settings.get_flag(EnemyStats).selected
            == EnemyStatsShuffleOptions.FULL_RANDOM
        )

        # Exclude both ohko_immune enemies AND sidekick enemies (boss henchmen)
        non_boss_enemies = [
            e for e in world.enemies.enemies
            if not e.ohko_immune and type(e) not in boss_related_types
        ]

        # Note: We intentionally do NOT inter-shuffle STATS (HP, attack, defense, etc.)
        # between enemies. Inter-shuffling could cause early-game enemies to inherit
        # late-game stats, making the game unfairly difficult. The ±50% mutation
        # provides enough variety. Boss stat scaling is handled separately.

        # In FULL_RANDOM mode, we DO shuffle non-stat properties (elemental, morph)
        if full_random:
            for attr in ["resistances", "weaknesses", "status_immunities"]:
                shuffled = list(non_boss_enemies)
                max_index = len(non_boss_enemies) - 1
                done: set = set()

                for i in range(len(non_boss_enemies)):
                    if shuffled[i] in done:
                        continue
                    new_index = i
                    while random.randint(0, 1) == 1:
                        new_index += 1
                    new_index = min(new_index, max_index)
                    a, b = shuffled[i], shuffled[new_index]
                    done.add(a)
                    shuffled[i] = b
                    shuffled[new_index] = a

                swaps = [getattr(s, attr) for s in shuffled]
                for enemy, swapped_val in zip(non_boss_enemies, swaps):
                    setter_name = f"set_{attr}"
                    if hasattr(enemy, setter_name):
                        setter = getattr(enemy, setter_name)
                        setter(list(swapped_val))

            morph_chances = [e.morph_chance for e in non_boss_enemies]
            random.shuffle(morph_chances)
            for chance, enemy in zip(morph_chances, non_boss_enemies):
                enemy.set_morph_chance(chance)

        # Cap changes at ±50% to prevent wild swings, especially for scaled boss stats
        for enemy in all_enemies:
            # BOOSTERDUMMY is an internal mechanic actor, not a real combatant -
            # never mutate its stats.
            if isinstance(enemy, BOOSTERDUMMY):
                continue
            orig = original_stats[id(enemy)]

            enemy.set_hp(mutate_normal(int(enemy.hp), minimum=1, maximum=32000, max_change_ratio=0.5))
            enemy.set_speed(mutate_normal(int(enemy.speed), minimum=0, maximum=255, max_change_ratio=0.5))
            enemy.set_attack(mutate_normal(int(enemy.attack), minimum=1, maximum=255, max_change_ratio=0.5))
            enemy.set_defense(mutate_normal(int(enemy.defense), minimum=1, maximum=255, max_change_ratio=0.5))
            enemy.set_magic_attack(mutate_normal(int(enemy.magic_attack), minimum=1, maximum=255, max_change_ratio=0.5))
            enemy.set_magic_defense(mutate_normal(int(enemy.magic_defense), minimum=1, maximum=255, max_change_ratio=0.5))
            enemy.set_fp(mutate_normal(int(enemy.fp), minimum=1, maximum=31, max_change_ratio=0.5))

            # Clamp all stats to ±50% of ORIGINAL vanilla values
            stat_bounds = {
                "hp": (1, 32000),
                "speed": (0, 255),
                "attack": (1, 255),
                "defense": (1, 255),
                "magic_attack": (1, 255),
                "magic_defense": (1, 255),
                "fp": (1, 31),
            }
            for attr, (stat_min, stat_max) in stat_bounds.items():
                original_val = orig[attr]
                current_val = int(getattr(enemy, attr))
                min_allowed = max(stat_min, int(original_val * 0.5))
                max_allowed = min(stat_max, int(original_val * 1.5))
                clamped_val = max(min_allowed, min(max_allowed, current_val))
                setter = getattr(enemy, f"set_{attr}")
                setter(clamped_val)

            # Strong Bob-Ombs in Punchinello 2: hp/attack/defense can rise but never drop
            if isinstance(enemy, strong_bobomb_types):
                for attr in ("hp", "attack", "defense"):
                    original_val = orig[attr]
                    current_val = int(getattr(enemy, attr))
                    if current_val < original_val:
                        setter = getattr(enemy, f"set_{attr}")
                        setter(original_val)

            # For bosses, don't let stats go below vanilla values
            if enemy.ohko_immune:
                for attr in stat_bounds.keys():
                    original_val = orig[attr]
                    current_val = int(getattr(enemy, attr))
                    if current_val < original_val:
                        setter = getattr(enemy, f"set_{attr}")
                        setter(original_val)

                # Small 1/255 chance for boss to be vulnerable to Geno Whirl
                if random.randint(1, 255) == 1:
                    enemy.set_ohko_immune(False)
            else:
                # For non-bosses: 1/3 chance to reverse OHKO immunity
                if random.randint(1, 3) == 3:
                    enemy.set_ohko_immune(not enemy.ohko_immune)

                if full_random:
                    morph_options = [0, 25, 75, 100]
                    enemy.set_morph_chance(random.choice(morph_options))

            # FULL_RANDOM: also shuffle elemental resistances/weaknesses
            if full_random:
                _randomize_enemy_elements_and_statuses(enemy)

        # Special logic for Smithy 2: All heads must have the same HP
        try:
            main_head = world.enemies.get_by_type(SMITHY2Enemy)
            for head_type in [SMITHYTankEnemy, SMITHYSafeEnemy2, SMITHYMageEnemy, SMITHYChestEnemy]:
                head = world.enemies.get_by_type(head_type)
                head.set_hp(int(main_head.hp))
        except (KeyError, StopIteration):
            pass

    # Restore disable_auto_death to original values (must never change)
    for enemy in all_enemies:
        enemy.set_disable_auto_death(original_disable_auto_death[id(enemy)])

    # Enemies with 0 HP (undead like Dry Bones, Vomer) must stay at 0 HP
    for enemy in all_enemies:
        if original_stats[id(enemy)]["hp"] == 0:
            enemy.set_hp(0)

    for enemy in all_enemies:
        custom_enemy = cast(CustomEnemy, enemy)
        custom_enemy.set_psychopath_message(custom_enemy.build_psychopath_text())


def _randomize_enemy_elements_and_statuses(enemy) -> None:
    """Randomize elemental resistances/weaknesses and status immunities for an enemy."""
    total_immunities = len(enemy.status_immunities) + len(enemy.resistances)
    new_status_immunities = random.randint(
        max(0, total_immunities - 4), min(total_immunities, 4)
    )
    new_resistances = total_immunities - new_status_immunities
    new_status_immunities = max(0, min(4, new_status_immunities))
    new_resistances = max(0, min(4, new_resistances))

    available_statuses = [Status.MUTE, Status.SLEEP, Status.POISON, Status.FEAR]
    enemy.set_status_immunities(
        random.sample(available_statuses, min(new_status_immunities, len(available_statuses)))
    )

    available_elements = [Element.ICE, Element.THUNDER, Element.FIRE, Element.JUMP]

    if random.randint(0, 1) == 0:
        # Prioritize resistances
        new_res = random.sample(available_elements, min(new_resistances, len(available_elements)))
        enemy.set_resistances(new_res)
        # Only allow weaknesses from elements NOT in resistances
        potential_weak = [e for e in available_elements if e not in new_res]
        current_weak_count = len(enemy.weaknesses)
        enemy.set_weaknesses(
            random.sample(potential_weak, min(current_weak_count, len(potential_weak)))
        )
    else:
        # Prioritize weaknesses
        current_weak_count = len(enemy.weaknesses)
        new_weak = random.sample(available_elements, min(current_weak_count, len(available_elements)))
        enemy.set_weaknesses(new_weak)
        # Only allow resistances from elements NOT in weaknesses
        potential_res = [e for e in available_elements if e not in new_weak]
        enemy.set_resistances(
            random.sample(potential_res, min(new_resistances, len(potential_res)))
        )

    flower_types = [
        FlowerBonusType.ATTACK_UP, FlowerBonusType.DEFENSE_UP, FlowerBonusType.HP_MAX,
        FlowerBonusType.ONCE_AGAIN, FlowerBonusType.LUCKY,
    ]
    enemy.set_flower_bonus_type(random.choice(flower_types))
    chance = (random.randint(0, 5) + random.randint(0, 5)) * 10
    enemy.set_flower_bonus_chance(chance)


def randomize_enemy_drops(world: GameWorld) -> None:
    """Randomize enemy drops (coins, XP, items)."""
    consumables_group_1 = [
        MushroomItem,
        HoneySyrupItem,
        PickMeUpItem,
        AbleJuiceItem,
        BracerItem,
        EnergizerItem,
        YoshiCookieItem,
        PureWaterItem,
        SleepyBombItem,
        BadMushroomItem,
        FlowerTabItem,
        FroggieDrinkItem,
        MukuCookieItem,
        FreshenUpItem,
        FrightBombItem,
        WiltShroomItem,
        RottenMushItem,
        MoldyMushItem,
        MushroomItem2,
    ]

    consumables_group_2 = [
        MidMushroomItem,
        MaxMushroomItem,
        MapleSyrupItem,
        RoyalSyrupItem,
        YoshiAdeItem,
        RedEssenceItem,
        KerokeroColaItem,
        FireBombItem,
        IceBombItem,
        FlowerJarItem,
        FlowerBoxItem,
        YoshiCandyItem,
        ElixirItem,
        MegalixirItem,
        RockCandyItem,
        CrystallineItem,
        PowerBlastItem,
    ]

    for enemy in world.enemies.enemies:
        old_coins = int(enemy.coins)
        if old_coins > 0:
            enemy.set_coins(mutate_normal(old_coins, minimum=1, maximum=255))

        old_xp = int(enemy.xp)
        new_xp = mutate_normal(old_xp, minimum=1, maximum=0xFFFF)

        # For bosses, don't let XP go above vanilla; for normal enemies, don't go below
        # Minimum of 1 XP (0 XP is only allowed via ExperienceNoBosses/ExperienceNoRegular flags)
        if enemy.ohko_immune:
            enemy.set_xp(max(1, min(old_xp, new_xp)))
        else:
            enemy.set_xp(max(1, max(old_xp, new_xp)))

        linked = enemy.common_item_drop == enemy.rare_item_drop

        if enemy.common_item_drop is not None:
            enemy.set_common_item_drop(random.choice(consumables_group_1))

        if linked:
            enemy.set_rare_item_drop(enemy.common_item_drop)
        elif enemy.rare_item_drop is not None:
            enemy.set_rare_item_drop(random.choice(consumables_group_2))

        if enemy.morph_chance > 0:
            enemy.set_yoshi_cookie_item(random.choice(consumables_group_2))


VALID_FORMATION_COORDINATES = [
    # Coords on the "ally side" of the diagonal axis through the problem
    # (135, 143) Sparky have been shifted +5 right, -5 up to avoid producing
    # a near-vertical bullet trajectory from caster to target. The SA-1
    # motion-normalization routine produces a ~1 sub-pixel/frame minor-axis
    # step for very lopsided delta ratios, stalling Finger Shot (and other
    # projectile-bullet weapons) in PauseScriptUntil(UNKNOWN_PAUSE_7) for
    # several real-world minutes.
    #
    # Allies sit at roughly (54,184), (88,205), (120,220). Slope between
    # the front and back ally ≈ (220-184)/(120-54) = 36/66 ≈ 0.545. The
    # boundary line is that slope drawn through the original problem coord
    # (135, 143): y = 0.545·(x − 135) + 143. Any coord with y >= line_y
    # (i.e. closer to the ally line on screen) has been shifted (+5, -5):
    #   (103, 127) → (108, 122)
    #   (119, 135) → (124, 130)
    #   (135, 143) → (140, 138)
    (135, 111), (151, 119), (167, 127),
    (119, 119), (135, 127), (151, 135),
    (108, 122), (124, 130), (140, 138),
]


def _get_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points."""
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def generate_formation_coordinates(
    enemy_types: list[type],
    world: GameWorld,
) -> list[tuple[int, int] | None]:
    """
    Generate scanline-aware formation coordinates that are well-spaced from each other.

    For each enemy type, computes the scanline footprint and filters candidate
    coordinates by (a) not matching an already-placed coord, (b) respecting the
    per-scanline OAM budget, and (c) not significantly visually overlapping any
    already-placed enemy. Prefers <= 50% sprite overlap; falls back to <= 85%
    if no spot qualifies; otherwise returns None for this enemy.

    For each subsequent enemy, picks the coord that maximizes the minimum
    Euclidean distance to already-placed enemies (greedy farthest-point). Ties
    are broken randomly.

    Args:
        enemy_types: The enemy class types to place.
        world: The game world instance for sprite lookups.

    Returns:
        A list of (x, y) coordinate tuples or None for enemies that can't fit.
    """
    # Lazy import to avoid circular dependency

    if not enemy_types:
        return []

    result: list[tuple[int, int] | None] = []
    placed: list[tuple[tuple[int, int], dict[int, int]]] = []

    for enemy_type in enemy_types:
        footprint = get_scanline_footprint(enemy_type, world)

        # Require that the candidate coord does not visually overlap any
        # already-placed enemy by more than 50% of the shorter sprite's body.
        # If no such coord exists (e.g., two tall sprites can't fit in the
        # tight coord grid at <= 50% overlap), drop this enemy - caller will
        # handle the None and exclude it from the formation. Producing a
        # "mostly overlapping" placement just looks like a bug to the player.
        valid = find_valid_coordinates(
            placed,
            footprint,
            VALID_FORMATION_COORDINATES,
            overlap_fraction=0.5,
        )

        if not valid:
            result.append(None)
            continue

        if not placed:
            # First enemy: uniform random from valid coords
            coord = random.choice(valid)
        else:
            # Subsequent: greedy farthest-point. Pick the coord whose minimum
            # distance to any already-placed enemy is largest. This spreads
            # more aggressively than product-of-distances weighting, which
            # could pick a candidate close to one enemy but far from another.
            used_points = [p[0] for p in placed]
            best_min_distance = -1.0
            best_candidates: list[tuple[int, int]] = []
            for c in valid:
                min_d = min(_get_distance(c[0], c[1], px, py) for px, py in used_points)
                if min_d > best_min_distance:
                    best_min_distance = min_d
                    best_candidates = [c]
                elif min_d == best_min_distance:
                    best_candidates.append(c)
            coord = random.choice(best_candidates)

        result.append(coord)
        placed.append((coord, footprint))

    return result


FORMATION_FORCED_ENEMIES: dict[Formation, list[type]] = {
    # Map Formation -> list of Enemy classes that MUST appear in
    # that formation when "randomize formations" is enabled. The randomizer
    # will guarantee each listed class is present at least once, even if the
    # class falls outside the normal stat-similarity pool. Forced enemies
    # still respect the per-formation VRAM budget (they are added first and
    # subsequent random additions get pruned to fit).
    #
    # Entries below were auto-generated by cross-referencing every
    # BattlePackNPC / BattlePackClone in randomizer/data/rooms against the
    # formations in each battle pack. Each overworld NPC's sprite implies a
    # specific enemy (sprite_id 256-511 map directly to monster_id 0-255),
    # so the corresponding enemy is forced into every formation the
    # battle_pack can roll into.
    FORM0001_TWO_SPIKEY: [SPIKEYEnemy],
    FORM0002_ONE_SPIKEY_ONE_SKYTROOPA: [SPIKEYEnemy],
    FORM0003_THREE_SPIKEY: [SPIKEYEnemy],
    FORM0004_TWO_SPIKEY_ONE_FROGOG: [SPIKEYEnemy],
    FORM0005_ONE_SKYTROOPA: [SKYTROOPAEnemy],
    FORM0006_TWO_SKYTROOPA: [SKYTROOPAEnemy],
    FORM0007_TWO_SKYTROOPA_ONE_GOOMBA: [SKYTROOPAEnemy],
    FORM0008_TWO_SKYTROOPA_ONE_FROGOG: [SKYTROOPAEnemy],
    FORM0009_TWO_GOOMBA: [GOOMBAEnemy],
    FORM0010_THREE_GOOMBA: [GOOMBAEnemy],
    FORM0011_ONE_GOOMBA_ONE_FROGOG_ONE_SPIKEY: [GOOMBAEnemy],
    FORM0012_TWO_GOOMBA_ONE_SPIKEY: [GOOMBAEnemy],
    FORM0014_TWO_K9: [K9Enemy],
    FORM0015_TWO_K9_ONE_SPIKEY: [K9Enemy],
    FORM0016_ONE_K9_TWO_FROGOG: [K9Enemy],
    FORM0019_TWO_RATFUNK: [RATFUNKEnemy],
    FORM0020_TWO_RATFUNK_ONE_SHADOW: [RATFUNKEnemy],
    FORM0021_TWO_RATFUNK_ONE_HOBGOBLIN: [RATFUNKEnemy],
    FORM0022_ONE_RATFUNK_TWO_HOBGOBLIN: [RATFUNKEnemy],
    FORM0023_ONE_THEBIGBOO_ONE_SHADOW: [THEBIGBOOEnemy],
    FORM0024_ONE_THEBIGBOO_ONE_SHADOW_ONE_HOBGOBLIN: [THEBIGBOOEnemy],
    FORM0025_THREE_THEBIGBOO_ONE_SHADOW: [THEBIGBOOEnemy],
    FORM0026_TWO_GOBY: [GOBYEnemy],
    FORM0027_THREE_GOBY: [GOBYEnemy],
    FORM0028_TWO_CROOK: [CROOKEnemyStatic],
    FORM0029_TWO_CROOK_ONE_SHYGUY: [CROOKEnemyStatic],
    FORM0030_ONE_CROOK_TWO_SNAPDRAGON: [CROOKEnemyStatic],
    FORM0031_ONE_CROOK_ONE_STARSLAP_ONE_ARACHNE: [CROOKEnemyStatic],
    FORM0032_ONE_SHYGUY_ONE_STARSLAP: [SHYGUYEnemyStatic],
    FORM0033_TWO_SHYGUY_ONE_SNAPDRAGON: [SHYGUYEnemyStatic],
    FORM0034_ONE_SHYGUY_ONE_CROOK_ONE_ARACHNE: [SHYGUYEnemyStatic],
    FORM0035_ONE_STARSLAP_ONE_SHYGUY: [STARSLAPEnemy],
    FORM0036_ONE_STARSLAP_ONE_ARACHNE: [STARSLAPEnemy],
    FORM0037_ONE_STARSLAP_TWO_SNAPDRAGON: [STARSLAPEnemy],
    FORM0038_FOUR_STARSLAP: [STARSLAPEnemy],
    FORM0043_TWO_AMANITA: [AMANITAEnemy],
    FORM0044_TWO_AMANITA_ONE_BUZZER: [AMANITAEnemy],
    FORM0045_TWO_AMANITA_ONE_OCTOLOT: [AMANITAEnemy],
    FORM0046_ONE_AMANITA_ONE_GUERRILLA_ONE_BUZZER: [AMANITAEnemy],
    FORM0047_ONE_BUZZER_ONE_OCTOLOT: [BUZZEREnemy],
    FORM0048_TWO_BUZZER_ONE_AMANITA: [BUZZEREnemy],
    FORM0049_ONE_BUZZER_ONE_GUERRILLA: [BUZZEREnemy],
    FORM0050_ONE_BUZZER_ONE_GUERRILLA: [BUZZEREnemy],
    FORM0056_ONE_PIRANHAPLANT: [PIRANHAPLANTEnemyStatic],
    FORM0057_TWO_PIRANHAPLANT_ONE_SHYRANGER: [PIRANHAPLANTEnemyStatic],
    FORM0058_THREE_PIRANHAPLANT: [PIRANHAPLANTEnemyStatic],
    FORM0059_FIVE_PIRANHAPLANT: [PIRANHAPLANTEnemyStatic],
    FORM0060_ONE_BOBOMB: [BOBOMBEnemyStatic],
    FORM0061_TWO_BOBOMB_ONE_CLUSTER: [BOBOMBEnemyStatic],
    FORM0062_FOUR_BOBOMB: [BOBOMBEnemyStatic],
    FORM0063_TWO_BOBOMB_ONE_ENIGMA_ONE_CLUSTER: [BOBOMBEnemyStatic],
    FORM0064_ONE_SPARKY_ONE_ENIGMA: [SPARKYEnemy],
    FORM0065_TWO_SPARKY_ONE_BOBOMB: [SPARKYEnemy],
    FORM0066_ONE_SPARKY_TWO_CLUSTER: [SPARKYEnemy],
    FORM0067_TWO_SPARKY_TWO_ENIGMA: [SPARKYEnemy],
    FORM0068_TWO_MAGMITE: [MAGMITEEnemy],
    FORM0069_ONE_MAGMITE_ONE_BOBOMB_ONE_SPARKY: [MAGMITEEnemy],
    FORM0070_TWO_MAGMITE_TWO_CLUSTER: [MAGMITEEnemy],
    FORM0071_TWO_MAGMITE_ONE_BOBOMB_ONE_CLUSTER: [MAGMITEEnemy],
    FORM0073_ONE_LAKITU_ONE_SPIKESTER_ONE_ARTICHOKER: [LAKITUEnemy],
    FORM0074_THREE_LAKITU: [LAKITUEnemy],
    FORM0075_TWO_LAKITU_ONE_ARTICHOKER: [LAKITUEnemy],
    FORM0076_ONE_SPIKESTER_ONE_CARROBOSCIS: [SPIKESTEREnemy],
    FORM0077_TWO_SPIKESTER_ONE_ARTICHOKER: [SPIKESTEREnemy],
    FORM0078_ONE_SPIKESTER_TWO_CARROBOSCIS: [SPIKESTEREnemy],
    FORM0079_FOUR_SPIKESTER_ONE_CARROBOSCIS: [SPIKESTEREnemy],
    FORM0080_ONE_SPOOKUM_ONE_ORBUSER: [SPOOKUMEnemy],
    FORM0081_TWO_SPOOKUM_ONE_JESTER: [SPOOKUMEnemy],
    FORM0082_ONE_SPOOKUM_ONE_REMOCON_ONE_ORBUSER: [SPOOKUMEnemy],
    FORM0083_TWO_SPOOKUM_ONE_REMOCON: [SPOOKUMEnemy],
    FORM0084_ONE_ROBOMB: [ROBOMBEnemy],
    FORM0085_THREE_ROBOMB: [ROBOMBEnemy],
    FORM0086_TWO_ROBOMB_ONE_REMOCON: [ROBOMBEnemy],
    FORM0087_FOUR_ROBOMB_ONE_ORBUSER: [ROBOMBEnemy],
    FORM0088_ONE_CHOMP_ONE_JESTER: [CHOMPEnemy],
    FORM0089_ONE_CHOMP_ONE_ROBOMB_ONE_REMOCON: [CHOMPEnemy],
    FORM0090_TWO_CHOMP_ONE_ORBUSER: [CHOMPEnemy],
    FORM0091_ONE_CHOMP_TWO_JESTER: [CHOMPEnemy],
    FORM0092_ONE_BLASTER_ONE_SPOOKUM: [BLASTEREnemy],
    FORM0093_ONE_BLASTER_ONE_SPOOKUM_ONE_REMOCON: [BLASTEREnemy],
    FORM0094_TWO_BLASTER_ONE_SPOOKUM: [BLASTEREnemy],
    FORM0097_ONE_MUKUMUKU: [MUKUMUKUEnemy],
    FORM0098_TWO_MUKUMUKU: [MUKUMUKUEnemy],
    FORM0099_TWO_MUKUMUKU_ONE_PULSAR: [MUKUMUKUEnemy],
    FORM0100_ONE_MUKUMUKU_ONE_PULSAR_ONE_GECKO: [MUKUMUKUEnemy],
    FORM0101_TWO_SACKIT: [SACKITEnemy],
    FORM0102_TWO_SACKIT_ONE_MUKUMUKU_ONE_GECKO: [SACKITEnemy],
    FORM0103_ONE_SACKIT_TWO_PULSAR: [SACKITEnemy],
    FORM0104_ONE_SACKIT_ONE_MASTADOOM: [SACKITEnemy],
    FORM0105_ONE_GECKO_ONE_SACKIT: [GECKOEnemy],
    FORM0106_ONE_GECKO_ONE_MASTADOOM: [GECKOEnemy],
    FORM0107_TWO_GECKO_TWO_MUKUMUKU_TWO_SACKIT: [GECKOEnemy],
    FORM0108_TWO_GECKO_ONE_MASTADOOM: [GECKOEnemy],
    FORM0109_TWO_ZEOSTAR: [ZEOSTAREnemy],
    FORM0110_TWO_ZEOSTAR_ONE_BLOOBER: [ZEOSTAREnemy],
    FORM0111_TWO_ZEOSTAR_TWO_LEUKO: [ZEOSTAREnemy],
    FORM0112_ONE_ZEOSTAR_ONE_LEUKO_ONE_CRUSTY: [ZEOSTAREnemy],
    FORM0113_ONE_BLOOBER_ONE_MRKIPPER: [BLOOBEREnemyStatic],
    FORM0114_THREE_BLOOBER: [BLOOBEREnemyStatic],
    FORM0115_TWO_BLOOBER_ONE_MRKIPPER_ONE_CRUSTY: [BLOOBEREnemyStatic],
    FORM0116_TWO_BLOOBER_TWO_ZEOSTAR_ONE_LEUKO: [BLOOBEREnemyStatic],
    FORM0117_THREE_MRKIPPER: [MRKIPPEREnemy],
    FORM0118_TWO_MRKIPPER_ONE_CRUSTY: [MRKIPPEREnemy],
    FORM0119_TWO_MRKIPPER_ONE_CRUSTY: [MRKIPPEREnemy],
    FORM0120_FOUR_MRKIPPER: [MRKIPPEREnemy],
    FORM0129_ONE_ALLEYRAT_ONE_GORGON: [ALLEYRATEnemy],
    FORM0130_TWO_ALLEYRAT_TWO_GREAPER: [ALLEYRATEnemy],
    FORM0131_TWO_ALLEYRAT_TWO_GORGON: [ALLEYRATEnemy],
    FORM0132_ONE_ALLEYRAT_ONE_REACHER_ONE_GORGON: [ALLEYRATEnemy],
    FORM0133_ONE_GREAPER: [GREAPEREnemy],
    FORM0134_TWO_GREAPER_ONE_REACHER: [GREAPEREnemy],
    FORM0135_ONE_GREAPER_ONE_STRAWHEAD_ONE_REACHER: [GREAPEREnemy],
    FORM0140_ONE_STINGER_ONE_FINKFLOWER: [STINGEREnemy],
    FORM0141_TWO_STINGER_ONE_OCTOVADER: [STINGEREnemy],
    FORM0142_ONE_STINGER_TWO_FINKFLOWER: [STINGEREnemy],
    FORM0143_FOUR_STINGER: [STINGEREnemy],
    FORM0144_ONE_CHOW_ONE_OCTOVADER: [CHOWEnemy],
    FORM0145_ONE_CHOW_ONE_SHOGUN: [CHOWEnemy],
    FORM0146_ONE_CHOW_ONE_SHOGUN_ONE_OCTOVADER: [CHOWEnemy],
    FORM0147_ONE_CHOW_ONE_FINKFLOWER_TWO_SHOGUN: [CHOWEnemy],
    FORM0149_TWO_CHOMPCHOMP: [CHOMPCHOMPEnemy],
    FORM0150_THREE_CHOMPCHOMP: [CHOMPCHOMPEnemy],
    FORM0151_FOUR_CHOMPCHOMP: [CHOMPCHOMPEnemy],
    FORM0152_ONE_SHYAWAY: [SHYAWAYEnemy],
    FORM0153_TWO_SHYAWAY_ONE_KRIFFID: [SHYAWAYEnemy],
    FORM0154_TWO_SHYAWAY_ONE_RIBBITE: [SHYAWAYEnemy],
    FORM0155_ONE_SHYAWAY_ONE_GECKIT_ONE_RIBBITE: [SHYAWAYEnemy],
    FORM0159_TWO_CHEWY_TWO_GECKIT_ONE_KRIFFID: [CHEWYEnemy],
    FORM0156_TWO_CHEWY: [CHEWYEnemy],
    FORM0160_ONE_GECKIT_ONE_SPINTHRA: [GECKITEnemy],
    FORM0161_TWO_GECKIT_ONE_SPINTHRA: [GECKITEnemy],
    FORM0162_TWO_GECKIT_TWO_CHEWY_ONE_SHYAWAY: [GECKITEnemy],
    FORM0163_TWO_GECKIT_ONE_SPINTHRA_ONE_KRIFFID: [GECKITEnemy],
    FORM0164_ONE_BIRDY_ONE_HEAVYTROOPA: [BIRDYEnemyStatic],
    FORM0165_THREE_BIRDY: [BIRDYEnemyStatic],
    FORM0166_TWO_BIRDY_ONE_HEAVYTROOPA: [BIRDYEnemyStatic],
    FORM0167_FIVE_BIRDY: [BIRDYEnemyStatic],
    FORM0169_TWO_BLUEBIRD_ONE_HEAVYTROOPA: [BLUEBIRDEnemyStatic],
    FORM0170_FOUR_BLUEBIRD: [BLUEBIRDEnemyStatic],
    FORM0171_TWO_BLUEBIRD_ONE_HEAVYTROOPA: [BLUEBIRDEnemyStatic],
    FORM0172_ONE_PINWHEEL: [PINWHEELEnemy],
    FORM0173_ONE_PINWHEEL_ONE_MUCKLE: [PINWHEELEnemy],
    FORM0174_TWO_PINWHEEL_TWO_MUCKLE: [PINWHEELEnemy],
    FORM0176_TWO_SHAMAN: [SHAMANEnemy],
    FORM0177_ONE_SHAMAN_ONE_ORBISON_ONE_JAWFUL: [SHAMANEnemy],
    FORM0178_TWO_SHAMAN_ONE_JAWFUL: [SHAMANEnemy],
    FORM0179_TWO_SHAMAN_TWO_SLINGSHY_ONE_JAWFUL: [SHAMANEnemy],
    FORM0180_ONE_SLINGSHY_ONE_ORBISON: [SLINGSHYEnemy],
    FORM0181_ONE_SLINGSHY_TWO_ORBISON: [SLINGSHYEnemy],
    FORM0182_ONE_SLINGSHY_TWO_ORBISON_ONE_JAWFUL: [SLINGSHYEnemy],
    FORM0183_TWO_SLINGSHY_TWO_PINWHEEL_ONE_MUCKLE: [SLINGSHYEnemy],
    FORM0184_ONE_MAGMUS: [MAGMUSEnemy],
    FORM0185_TWO_MAGMUS_ONE_ARMOREDANT: [MAGMUSEnemy],
    FORM0186_THREE_MAGMUS_TWO_OERLIKON: [MAGMUSEnemy],
    FORM0187_TWO_MAGMUS_TWO_ARMOREDANT: [MAGMUSEnemy],
    FORM0188_ONE_OERLIKON_ONE_VOMER: [OERLIKONEnemy],
    FORM0189_THREE_OERLIKON: [OERLIKONEnemy],
    FORM0190_ONE_OERLIKON_ONE_CHAINEDKONG_ONE_ARMOREDANT: [OERLIKONEnemy],
    FORM0191_TWO_OERLIKON_ONE_CHAINEDKONG: [OERLIKONEnemy],
    FORM0192_THREE_PYROSPHERE: [SPARKYEnemy],
    FORM0193_TWO_PYROSPHERE_ONE_CHAINEDKONG: [SPARKYEnemy],
    FORM0194_ONE_CORKPEDITE_ONE_BODY_ONE_PYROSPHERE: [CORKPEDITEEnemy, BODYEnemy, SPARKYEnemy],
    FORM0196_ONE_VOMER_ONE_CHAINEDKONG: [VOMEREnemy],
    FORM0197_THREE_VOMER: [VOMEREnemy],
    FORM0198_ONE_CORKPEDITE_ONE_BODY_ONE_VOMER: [CORKPEDITEEnemy, BODYEnemy, VOMEREnemy],
    FORM0200_ONE_TERRACOTTA: [TERRACOTTAEnemy],
    FORM0201_THREE_TERRACOTTA: [TERRACOTTAEnemy],
    FORM0202_ONE_TERRACOTTA_TWO_FORKIES: [TERRACOTTAEnemy],
    FORM0204_ONE_MALAKOOPA_ONE_TUBOTROOPA: [MALAKOOPAEnemy],
    FORM0205_TWO_MALAKOOPA_ONE_TUBOTROOPA: [MALAKOOPAEnemy],
    FORM0206_TWO_MALAKOOPA_ONE_TERRACOTTA_ONE_TUBOTROOPA: [MALAKOOPAEnemy],
    FORM0207_ONE_MALAKOOPA_TWO_TUBOTROOPA: [MALAKOOPAEnemy],
    FORM0208_TWO_GUGOOMBA: [GUGOOMBAEnemy],
    FORM0209_TWO_GUGOOMBA_ONE_STARCRUSTER: [GUGOOMBAEnemy],
    FORM0210_ONE_GUGOOMBA_ONE_FORKIES_ONE_STARCRUSTER: [GUGOOMBAEnemy],
    FORM0211_TWO_GUGOOMBA_TWO_MALAKOOPA_TWO_TERRACOTTA: [GUGOOMBAEnemy],
    FORM0212_ONE_BIGBERTHA: [BIGBERTHAEnemy],
    FORM0213_TWO_BIGBERTHA: [BIGBERTHAEnemy],
    FORM0214_ONE_BIGBERTHA_ONE_FORKIES: [BIGBERTHAEnemy],
    FORM0215_TWO_BIGBERTHA_ONE_TERRACOTTA: [BIGBERTHAEnemy],
    FORM0218_ONE_NINJA: [NINJAEnemy],
    FORM0219_ONE_NINJA_ONE_DOPPEL: [NINJAEnemy],
    FORM0220_TWO_NINJA_ONE_HIPPOPO: [NINJAEnemy],
    FORM0221_FIVE_NINJA: [NINJAEnemy],
    FORM0235_THREE_GLUMREAPER: [GLUMREAPEREnemy],
    FORM0236_ONE_GLUMREAPER_ONE_HIPPOPO: [GLUMREAPEREnemy],
    FORM0237_TWO_GLUMREAPER_TWO_DOPPEL: [GLUMREAPEREnemy],
    FORM0238_TWO_GLUMREAPER_TWO_LILBOO: [GLUMREAPEREnemy],
    FORM0239_ONE_LILBOO: [LILBOOEnemy],
    FORM0240_TWO_LILBOO_ONE_HIPPOPO: [LILBOOEnemy],
    FORM0241_TWO_LILBOO_ONE_PUPPOX_ONE_DOPPEL: [LILBOOEnemy],
    FORM0242_FOUR_LILBOO: [LILBOOEnemy],
    FORM0247_THREE_RATFUNK: [RATFUNKEnemy],
    FORM0248_FIVE_RATFUNK: [RATFUNKEnemy],
    FORM0252_TWO_FIREBALL: [FIREBALLEnemy],
    FORM0253_THREE_FIREBALL: [FIREBALLEnemy],
    FORM0254_ONE_STUMPET_TWO_MAGMUS: [STUMPETEnemy],
    FORM0255_ONE_STUMPET_THREE_MAGMUS: [STUMPETEnemy],
    FORM0256_ONE_CORKPEDITE_ONE_BODY_ONE_OERLIKON: [CORKPEDITEEnemy, BODYEnemy], 
    FORM0257_ONE_CORKPEDITE_ONE_BODY_TWO_OERLIKON: [CORKPEDITEEnemy, BODYEnemy],
    FORM0300_THREE_HEAVYTROOPA: [HEAVYTROOPAEnemy],
    FORM0310_ONE_MACHINEMADEAXEMPINK_ONE_MACHINEMADEAXEMRED_ONE_MACHINEMADEAXEMGREEN: [MACHINEMADEAxemRedEnemy],
    FORM0311_TWO_MACHINEMADEAXEMBLACK_TWO_MACHINEMADEAXEMYELLOW: [MACHINEMADEAxemRedEnemy],
    FORM0331_FOUR_TERRACOTTA: [TERRACOTTAEnemy],
    FORM0332_TWO_OERLIKON_ONE_STARCRUSTER: [OERLIKONEnemy],
    FORM0333_ONE_SACKIT_TWO_BIGBERTHA: [SACKITEnemy],
    FORM0334_TWO_CHOW_ONE_FORKIES: [CHOWEnemy],
    FORM0335_ONE_ALLEYRAT_TWO_ARMOREDANT: [ALLEYRATEnemy],
    FORM0336_THREE_BLOOBER_ONE_STARCRUSTER: [BLOOBEREnemyStatic],
    FORM0337_FOUR_STINGER: [STINGEREnemy],
    FORM0338_TWO_GECKIT_ONE_CHAINEDKONG: [GECKITEnemy],
    FORM0339_ONE_ROBOMB_TWO_BIGBERTHA: [ROBOMBEnemy],
    FORM0340_FOUR_VOMER: [VOMEREnemy],
    FORM0341_TWO_MAGMUS_TWO_PULSAR: [MAGMUSEnemy],
    FORM0343_FIVE_GUGOOMBA: [GUGOOMBAEnemy],
    FORM0344_TWO_MALAKOOPA_ONE_TUBOTROOPA: [MALAKOOPAEnemy],
    FORM0345_TWO_THEBIGBOO_TWO_ORBISON: [THEBIGBOOEnemy],
    FORM0346_FIVE_SLINGSHY: [SLINGSHYEnemy],
    FORM0347_TWO_CHEWY_TWO_SHYAWAY: [CHEWYEnemy],
    FORM0348_ONE_MRKIPPER_TWO_MUCKLE: [MRKIPPEREnemy],
    FORM0349_TWO_AMANITA_ONE_ORBISON: [AMANITAEnemy],
    FORM0350_TWO_GREAPER_ONE_GLUMREAPER: [GREAPEREnemy, GLUMREAPEREnemy],
    FORM0351_THREE_PYROSPHERE: [PYROSPHEREEnemy],
    FORM0352_THREE_LAKITU: [LAKITUEnemy],
    FORM0353_TWO_ZEOSTAR_TWO_SHAMAN: [ZEOSTAREnemy],
    FORM0354_SIX_SHAMAN: [SHAMANEnemy],
    FORM0362_TWO_BOBOMB_ONE_CLUSTER: [BOBOMBEnemyStatic],
    FORM0363_FOUR_BOBOMB: [BOBOMBEnemyStatic],
}

# Formations the EnemyFormations shuffler must never modify.
PROTECTED_FORMATIONS: list[Formation] = [FORM0234_FIVE_AMEBOID]

# Enemies the EnemyFormations shuffler must never add to any formation.
# AMEBOID is locked to its vanilla formation (FORM0234).
SHUFFLE_EXCLUDED_ENEMY_TYPES: set[type] = {AMEBOIDEnemy}


def randomize_enemy_formations(world: GameWorld) -> None:
    """Randomize enemy formations.

    - Boss fight packs (used by BossFightLocation subclasses) are excluded entirely
    - Monsters that appear in boss fight formations are excluded from the candidate pool
    - Monsters are matched by stat similarity: sum of (attack + defense + magic_attack + magic_defense)
      must be within ±20% of the formation's average
    - Per-formation forced enemies declared in FORMATION_FORCED_ENEMIES are
      always included in the resulting formation, even when they fall outside
      the stat-similarity candidate pool.
    """
    from randomizer.types.prizelocation import BossFightLocation

    clear_footprint_cache()

    max_enemies = 6

    # Collect all pack IDs used by boss fight locations - these packs are never modified
    boss_pack_ids: set[int] = set()
    for location_cls in BossFightLocation.__subclasses__():
        if hasattr(location_cls, '_pack_id') and location_cls._pack_id is not None:
            boss_pack_ids.add(location_cls._pack_id)

    boss_enemy_types: set[type] = set()
    for prize_cls in BossFightPrize.__subclasses__():
        if hasattr(prize_cls, '_members') and prize_cls._members:
            for member in prize_cls._members:
                if member is not None:
                    boss_enemy_types.add(member.enemy)
        if hasattr(prize_cls, '_additional_enemies_to_scale'):
            boss_enemy_types.update(prize_cls._additional_enemies_to_scale)
        if hasattr(prize_cls, '_extra_hp_enemies'):
            boss_enemy_types.update(prize_cls._extra_hp_enemies)
        if hasattr(prize_cls, '_hp_slice_excluded_enemies'):
            boss_enemy_types.update(prize_cls._hp_slice_excluded_enemies)
        if hasattr(prize_cls, '_scaling_excluded_enemies'):
            boss_enemy_types.update(prize_cls._scaling_excluded_enemies)
        if hasattr(prize_cls, '_anchor_enemy') and prize_cls._anchor_enemy:
            anchor = prize_cls._anchor_enemy
            if isinstance(anchor, list):
                boss_enemy_types.update(anchor)
            else:
                boss_enemy_types.add(anchor)

    eligible_enemy_types = [
        type(e) for e in world.enemies.enemies
        if not e.ohko_immune
        and type(e) not in boss_enemy_types
        and type(e) not in SHUFFLE_EXCLUDED_ENEMY_TYPES
    ]

    protected_formation_ids: set[int] = {
        f.formation_id for f in PROTECTED_FORMATIONS if f.formation_id is not None
    }

    # Undead enemies (Dry Bones, Vomer) have 0 HP and self-revive; dropping
    # them into certain early-game / scripted encounters softlocks or unfairly
    # stalls the fight. Collect the formation IDs reachable through the packs
    # they must be kept out of. Formation instances are shared across packs,
    # so a formation belonging to a restricted pack can still be mutated while
    # shuffling a *different* pack - hence we restrict by formation_id rather
    # than pack_id.
    from randomizer.logic.progression.prizelocations import (
        MushroomKingdomBossFight,
        BoosterTowerIndoorBossFight,
        InnerFactoryFirstFight,
        ShipFinalBossFight,
    )
    undead_restricted_pack_ids: set[int] = {
        PACK139_ARTICHOKERS_ONLY,
        PACK046_SPOOKUM_WITH_OTHER_MONSTERS,
        PACK047_MULTIPLE_SPOOKUM_WITH_OTHER_MONSTERS,
        PACK067_KIPPER_PACK_2,
        PACK144_STUMPET_ENCOUNTER,
        PACK143_TOWER_FIREBALLS,
    }
    # For the boss fights, the boss pack itself is never shuffled - it is the
    # henchman packs (swapped in around the boss by the henchman shuffler)
    # that can roll undead enemies, so restrict those instead.
    for boss_fight_cls in (
        MushroomKingdomBossFight,
        BoosterTowerIndoorBossFight,
        InnerFactoryFirstFight,
        ShipFinalBossFight,
    ):
        for henchman_slots in (
            boss_fight_cls._character_henchman_slots,
            boss_fight_cls._mook_henchman_slots,
            boss_fight_cls._tiny_henchman_slots,
        ):
            if henchman_slots is None:
                continue
            for henchman_slot in henchman_slots:
                if henchman_slot.pack_id is not None:
                    undead_restricted_pack_ids.add(henchman_slot.pack_id)
    undead_restricted_formation_ids: set[int] = set()
    for restricted_pack_id in undead_restricted_pack_ids:
        if 0 <= restricted_pack_id < len(world.battle_packs.packs):
            for restricted_formation in world.battle_packs.packs[restricted_pack_id].formations:
                if restricted_formation.formation_id is not None:
                    undead_restricted_formation_ids.add(restricted_formation.formation_id)

    undead_enemy_types = (DRYBONESEnemy, VOMEREnemy)

    def get_stat_sum(enemy) -> int:
        return enemy.attack + enemy.defense + enemy.magic_attack + enemy.magic_defense

    # Sprite ID = monster_id + 256
    def get_vram_size(enemy_type: type) -> int:
        enemy = world.enemies.get_by_type(enemy_type)
        sprite_id = enemy.monster_id + 256
        try:
            sprite = world.get_sprite(sprite_id)
            return sprite.animation.properties.vram_size
        except (IndexError, AttributeError):
            # Default to a reasonable size if sprite lookup fails
            return 2048

    # Maximum unique VRAM size for a formation.
    # Duplicate enemies share sprite VRAM, so only unique sprites count.
    # 14336 = vanilla ceiling for non-boss formations (old value 8192 was too low).
    MAX_VRAM_SIZE = VANILLA_MAX_NONBOSS_UNIQUE_VRAM

    for pack_id, pack in enumerate(world.battle_packs.packs):
        # Skip boss fight packs entirely - never modify boss formations
        if pack_id in boss_pack_ids:
            continue

        for formation in pack.formations:
            if formation.formation_id in protected_formation_ids:
                continue

            current_members = [m for m in formation.members if m is not None]
            if not current_members:
                continue
            if any(m.hidden_at_start for m in current_members):
                continue

            current_enemy_types = list(dict.fromkeys(m.enemy for m in current_members))

            # Skip if any current enemy is a boss enemy (shouldn't shuffle boss-adjacent formations)
            if any(e in boss_enemy_types for e in current_enemy_types):
                continue

            # Forced enemies for this specific formation_id (user-configured).
            # These must appear in the final formation regardless of stat similarity.
            forced_enemies: list[type] = []
            if formation.formation_id is not None:
                for key, enemies in FORMATION_FORCED_ENEMIES.items():
                    if key.formation_id == formation.formation_id:
                        forced_enemies = list(enemies)
                        break

            # Keep undead enemies (Dry Bones, Vomer) out of formations
            # reachable through restricted packs. Vanilla members are left
            # untouched; this only blocks undead from being forced in or
            # added as random fill.
            restrict_undead = (
                formation.formation_id is not None
                and formation.formation_id in undead_restricted_formation_ids
            )
            if restrict_undead:
                forced_enemies = [
                    e for e in forced_enemies if e not in undead_enemy_types
                ]

            candidates = list(current_enemy_types)
            for fe in forced_enemies:
                if fe not in candidates:
                    candidates.append(fe)

            current_enemies_objs = [world.enemies.get_by_type(e) for e in current_enemy_types]
            avg_stat_sum = sum(get_stat_sum(e) for e in current_enemies_objs) / len(current_enemies_objs)

            similar_enemies = []
            for enemy_type in eligible_enemy_types:
                enemy = world.enemies.get_by_type(enemy_type)
                enemy_stat_sum = get_stat_sum(enemy)

                lower_bound = avg_stat_sum * 0.8
                upper_bound = avg_stat_sum * 1.2

                if lower_bound <= enemy_stat_sum <= upper_bound:
                    similar_enemies.append(enemy_type)

            # Only use similar enemies for candidate pool - don't fall back to all eligible enemies
            # If no similar enemies exist, we only use the original formation enemies
            candidate_pool = similar_enemies if similar_enemies else []

            if restrict_undead:
                candidate_pool = [
                    e for e in candidate_pool if e not in undead_enemy_types
                ]

            while len(candidates) < 3 and candidate_pool:
                remaining_unique = [e for e in candidate_pool if e not in candidates]
                if not remaining_unique:
                    break  # No more unique enemies available
                candidates.append(random.choice(remaining_unique))

            # Bias toward multi-enemy formations: floor at 2 so single-enemy
            # rolls are only possible when vanilla itself had a single member.
            num_enemies = random.randint(2, random.randint(3, max_enemies))
            num_enemies = max(num_enemies, len(current_members), len(forced_enemies))

            # Build formation while respecting VRAM constraint.
            # Duplicate enemies share sprite VRAM, so track unique sprites only.
            # Seed with original members plus any user-forced enemies so they are
            # guaranteed to appear in the final formation.
            chosen_enemies: list[type] = list(current_enemy_types)
            for fe in forced_enemies:
                if fe not in chosen_enemies:
                    chosen_enemies.append(fe)
            unique_vram: dict[type, int] = {
                e: get_vram_size(e) for e in dict.fromkeys(chosen_enemies)
            }
            current_vram = sum(unique_vram.values())

            while len(chosen_enemies) < num_enemies:
                sub_candidates = candidates + chosen_enemies
                if not sub_candidates:
                    break

                # Filter candidates by VRAM constraint.
                # If the enemy type is already in the formation, it adds 0 VRAM (shared).
                vram_valid_candidates = [
                    e for e in sub_candidates
                    if e in unique_vram  # already loaded, free
                    or current_vram + get_vram_size(e) <= MAX_VRAM_SIZE
                ]

                if not vram_valid_candidates:
                    break  # Can't add any more enemies without exceeding VRAM

                new_enemy = random.choice(vram_valid_candidates)
                chosen_enemies.append(new_enemy)
                if new_enemy not in unique_vram:
                    vram_cost = get_vram_size(new_enemy)
                    unique_vram[new_enemy] = vram_cost
                    current_vram += vram_cost

            # Shuffle for visual variety, then re-prioritize: forced enemies
            # first, then vanilla originals, then random additions. Coord
            # placement is greedy.
            random.shuffle(chosen_enemies)
            forced_set = set(forced_enemies)
            originals_set = set(current_enemy_types)
            chosen_enemies.sort(
                key=lambda e: (
                    0 if e in forced_set
                    else 1 if e in originals_set
                    else 2
                )
            )

            coordinates = generate_formation_coordinates(chosen_enemies, world)

            new_members: list[FormationMember | None] = []
            for enemy_type, coord in zip(chosen_enemies, coordinates):
                if coord is None:
                    continue
                x, y = coord
                new_members.append(
                    FormationMember(enemy=enemy_type, x_pos=x, y_pos=y, hidden_at_start=False)
                )

            if not new_members:
                x, y = random.choice(VALID_FORMATION_COORDINATES)
                new_members.append(
                    FormationMember(enemy=chosen_enemies[0], x_pos=x, y_pos=y, hidden_at_start=False)
                )

            formation.set_members(new_members)


def apply_exp_multiplier(world: GameWorld) -> None:
    """Apply EXP multiplier to all enemies based on settings."""

    exp_setting = world.settings.get_flag(EXPMultiplier).selected

    if exp_setting == EXPMultiplierOptions.VANILLA:
        return

    multiplier = 1
    if exp_setting == EXPMultiplierOptions.DOUBLE:
        multiplier = 2
    elif exp_setting == EXPMultiplierOptions.TRIPLE:
        multiplier = 3

    for enemy in world.enemies.enemies:
        current_xp = enemy.xp
        # Minimum of 1 XP (0 XP is only allowed via ExperienceNoBosses/ExperienceNoRegular flags)
        new_xp = max(1, min(9999, current_xp * multiplier))
        enemy.set_xp(new_xp)
