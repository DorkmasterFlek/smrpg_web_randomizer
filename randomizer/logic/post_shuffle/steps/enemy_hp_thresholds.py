"""Recompute enemy HP thresholds after stat randomization.

Extracted from types/gameworld.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from randomizer.data.enemies.enemies import (
    BELOME1Enemy,
    BOOSTEREnemy,
    BUNDTEnemy,
    CROCO1Enemy,
    CROCO2Enemy,
    DODOEnemy,
    JINX1Enemy,
    JINX2Enemy,
    JINX3Enemy,
    JOHNNYEnemy,
    JOHNNYEnemy2,
    LEFTEYEEnemy,
    PUNCHINELLOEnemy,
    RIGHTEYEEnemy,
    SHELLYEnemy,
    SMITHY2Enemy,
    SMITHYChestEnemy,
    SMITHYMageEnemy,
    SMITHYSafeEnemy2,
    SMITHYTankEnemy,
    VALENTINAEnemy,
)
from randomizer.logic.post_shuffle.steps.calculate_boss_stats import (sync_boomer_form_stats)
from smrpgpatchbuilder.datatypes.battle_animation_scripts.commands import (SetAMEM16BitToConst)
from smrpgpatchbuilder.datatypes.monster_scripts.commands import (IfHPBelow)
from typing import (cast)

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld


def _update_enemy_hp_thresholds(world: GameWorld) -> None:
    """Update HP-based AI script thresholds for specific enemies.

    This must be called AFTER both boss stat scaling and enemy stat mutations
    are complete, so the thresholds reflect the final HP values.
    """
    # Update Dodo's AI script HP threshold (60% of HP triggers phase 2)
    dodo = world.get_enemy(DODOEnemy)
    _, _, dodo_hp_check = world.monster_scripts.get_command_by_identifier(
        "dodo_low_hp_check"
    )
    cast(IfHPBelow, dodo_hp_check).set_threshold(round(dodo.hp * 0.6))
    # Update return condition
    valentina = world.get_enemy(VALENTINAEnemy)
    _, _, valentina_return_cmd = world.monster_scripts.get_command_by_identifier(
        "dodo_returns"
    )
    cast(IfHPBelow, valentina_return_cmd).set_threshold(
        round(valentina.hp * 1200 / 2000)
    )

    # Update Shelly's AI script HP thresholds (80%, 60%, 40%, 20% triggers phase changes)
    shelly = world.get_enemy(SHELLYEnemy)
    for identifier, percent in [
        ("shelly_low_hp_check_80_percent", 0.8),
        ("shelly_low_hp_check_60_percent", 0.6),
        ("shelly_low_hp_check_40_percent", 0.4),
        ("shelly_low_hp_check_20_percent", 0.2),
    ]:
        _, _, shelly_hp_check = world.monster_scripts.get_command_by_identifier(
            identifier
        )
        cast(IfHPBelow, shelly_hp_check).set_threshold(round(shelly.hp * percent))

    # Update Right Eye's revival HP in battle animation scripts (120% of HP)
    right_eye = world.get_enemy(RIGHTEYEEnemy)
    right_eye_revival_cmd = world.get_battle_animation_command_by_name(
        "right_eye_revival_hp"
    )
    cast(SetAMEM16BitToConst, right_eye_revival_cmd).set_value(
        round(right_eye.hp * 1.2)
    )

    left_eye = world.get_enemy(LEFTEYEEnemy)
    left_eye_revival_cmd = world.get_battle_animation_command_by_name(
        "left_eye_revival_hp"
    )
    cast(SetAMEM16BitToConst, left_eye_revival_cmd).set_value(int(left_eye.hp))

    sync_boomer_form_stats(world)

    # Update Punchinello's bomb-summoning thresholds
    punchinello = world.get_enemy(PUNCHINELLOEnemy)
    threshold_1 = round(punchinello.hp * 800 / 1200)
    _, _, bobomb_cmd_1 = world.monster_scripts.get_command_by_identifier(
        "punchinello_800_hp_1"
    )
    cast(IfHPBelow, bobomb_cmd_1).set_threshold(threshold_1)
    _, _, bobomb_cmd_2 = world.monster_scripts.get_command_by_identifier(
        "punchinello_800_hp_2"
    )
    cast(IfHPBelow, bobomb_cmd_2).set_threshold(threshold_1)
    threshold_2 = round(punchinello.hp * 400 / 1200)
    _, _, bobomb_cmd_3 = world.monster_scripts.get_command_by_identifier(
        "punchinello_400_hp_1"
    )
    cast(IfHPBelow, bobomb_cmd_3).set_threshold(threshold_2)
    _, _, bobomb_cmd_4 = world.monster_scripts.get_command_by_identifier(
        "punchinello_400_hp_2"
    )
    cast(IfHPBelow, bobomb_cmd_4).set_threshold(threshold_2)

    # Update Johnny's Get Tough threshold
    johnny = world.get_enemy(JOHNNYEnemy)
    _, _, get_tough_cmd = world.monster_scripts.get_command_by_identifier(
        "johnny_400_hp"
    )
    cast(IfHPBelow, get_tough_cmd).set_threshold(round(johnny.hp * 400 / 820))

    # Update Johnny 2's battle thresholds
    johnny_2 = world.get_enemy(JOHNNYEnemy2)
    _, _, johnny_cmd_1 = world.monster_scripts.get_command_by_identifier(
        "johnny_1000_hp"
    )
    cast(IfHPBelow, johnny_cmd_1).set_threshold(round(johnny_2.hp * 1000 / 2000))
    _, _, johnny_cmd_2 = world.monster_scripts.get_command_by_identifier(
        "johnny_500_hp"
    )
    cast(IfHPBelow, johnny_cmd_2).set_threshold(round(johnny_2.hp * 500 / 2000))

    # Update Bundt's warning phase
    bundt = world.get_enemy(BUNDTEnemy)
    _, _, bundt_warning_cmd = world.monster_scripts.get_command_by_identifier(
        "bundt_hp_threshold"
    )
    cast(IfHPBelow, bundt_warning_cmd).set_threshold(round(bundt.hp * 200 / 900))

    # Update Jinx 1's buff threshold
    jinx1 = world.get_enemy(JINX1Enemy)
    _, _, jinx1_buff_cmd = world.monster_scripts.get_command_by_identifier(
        "jinx1_phase2"
    )
    cast(IfHPBelow, jinx1_buff_cmd).set_threshold(round(jinx1.hp * 300 / 600))

    # Update Jinx 2's buff threshold
    jinx2 = world.get_enemy(JINX2Enemy)
    _, _, jinx2_buff_cmd = world.monster_scripts.get_command_by_identifier(
        "jinx2_phase2"
    )
    cast(IfHPBelow, jinx2_buff_cmd).set_threshold(round(jinx2.hp * 400 / 800))

    # Update Jinx 3's buff threshold
    jinx3 = world.get_enemy(JINX3Enemy)
    _, _, jinx3_buff_cmd = world.monster_scripts.get_command_by_identifier(
        "jinx3_phase2"
    )
    cast(IfHPBelow, jinx3_buff_cmd).set_threshold(round(jinx3.hp * 600 / 1000))
    _, _, jinx3_buff_cmd_2 = world.monster_scripts.get_command_by_identifier(
        "jinx3_phase3"
    )
    cast(IfHPBelow, jinx3_buff_cmd_2).set_threshold(round(jinx3.hp * 300 / 1000))

    # Update Croco 1's heal threshold
    croco1 = world.get_enemy(CROCO1Enemy)
    _, _, croco1_heal_cmd = world.monster_scripts.get_command_by_identifier(
        "croco1_heal"
    )
    cast(IfHPBelow, croco1_heal_cmd).set_threshold(round(croco1.hp * 100 / 320))

    # Update Croco 2's item steal threshold
    croco2 = world.get_enemy(CROCO2Enemy)
    _, _, croco2_steal_cmd = world.monster_scripts.get_command_by_identifier(
        "croco2_steal"
    )
    cast(IfHPBelow, croco2_steal_cmd).set_threshold(round(croco2.hp * 400 / 750))

    # Update Belome 1's phase change threshold
    belome1 = world.get_enemy(BELOME1Enemy)
    _, _, belome1_phase_change_cmd = world.monster_scripts.get_command_by_identifier(
        "belome1_phase2"
    )
    cast(IfHPBelow, belome1_phase_change_cmd).set_threshold(
        round(belome1.hp * 300 / 500)
    )

    # Update Booster 1's thresholds for stronger attacks
    booster1 = world.get_enemy(BOOSTEREnemy)
    _, _, booster1_strong_attack_1_cmd = (
        world.monster_scripts.get_command_by_identifier("booster_powers_up")
    )
    cast(IfHPBelow, booster1_strong_attack_1_cmd).set_threshold(
        round(booster1.hp * 500 / 800)
    )

    # Update Smithy's pattern thresholds
    smithy_2 = world.get_enemy(SMITHY2Enemy)
    _, _, smithy_phase_2 = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_2"
    )
    _, _, smithy_phase_3 = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_3"
    )
    _, _, smithy_phase_4 = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_4"
    )
    cast(IfHPBelow, smithy_phase_2).set_threshold(round(smithy_2.hp * 6000 / 8000))
    cast(IfHPBelow, smithy_phase_3).set_threshold(round(smithy_2.hp * 4000 / 8000))
    cast(IfHPBelow, smithy_phase_4).set_threshold(round(smithy_2.hp * 2000 / 8000))
    smithy_2 = world.get_enemy(SMITHYMageEnemy)
    _, _, smithy_phase_2_m = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_2_m"
    )
    _, _, smithy_phase_3_m = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_3_m"
    )
    _, _, smithy_phase_4_m = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_4_m"
    )
    cast(IfHPBelow, smithy_phase_2_m).set_threshold(
        round(smithy_2.hp * 6000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_3_m).set_threshold(
        round(smithy_2.hp * 4000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_4_m).set_threshold(
        round(smithy_2.hp * 2000 / 8000)
    )
    smithy_2 = world.get_enemy(SMITHYTankEnemy)
    _, _, smithy_phase_2_t = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_2_t"
    )
    _, _, smithy_phase_3_t = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_3_t"
    )
    _, _, smithy_phase_4_t = world.monster_scripts.get_command_by_identifier(
        "smithy2_phase_4_t"
    )
    cast(IfHPBelow, smithy_phase_2_t).set_threshold(
        round(smithy_2.hp * 6000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_3_t).set_threshold(
        round(smithy_2.hp * 4000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_4_t).set_threshold(
        round(smithy_2.hp * 2000 / 8000)
    )
    smithy_2 = world.get_enemy(SMITHYChestEnemy)
    _, _, smithy_phase_2_c = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_2_c"
    )
    _, _, smithy_phase_3_c = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_3_c"
    )
    _, _, smithy_phase_4_c = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_4_c"
    )
    cast(IfHPBelow, smithy_phase_2_c).set_threshold(
        round(smithy_2.hp * 6000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_3_c).set_threshold(
        round(smithy_2.hp * 4000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_4_c).set_threshold(
        round(smithy_2.hp * 2000 / 8000)
    )
    smithy_2 = world.get_enemy(SMITHYSafeEnemy2)
    _, _, smithy_phase_2_s = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_2_s"
    )
    _, _, smithy_phase_3_s = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_3_s"
    )
    _, _, smithy_phase_4_s = world.monster_scripts.get_command_by_identifier(
        "smithy_phase_4_s"
    )
    cast(IfHPBelow, smithy_phase_2_s).set_threshold(
        round(smithy_2.hp * 6000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_3_s).set_threshold(
        round(smithy_2.hp * 4000 / 8000)
    )
    cast(IfHPBelow, smithy_phase_4_s).set_threshold(
        round(smithy_2.hp * 2000 / 8000)
    )


__all__ = ['_update_enemy_hp_thresholds']
