from __future__ import annotations
from typing import TYPE_CHECKING
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import *
from randomizer.data.variables.room_names import *
from randomizer.data.variables.event_script_names import *
from randomizer.data.variables.action_script_names import *
from randomizer.data.variables.pack_names import *
from randomizer.logic.progression.prizes import *
from randomizer.types.flags import *
from randomizer.utils.event_script_snippets.es_mimic_rise import (get_mimic_rise_dojo)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands.commands import (A_FaceNorthwest, A_Pause, A_SetSpriteSequence)
from typing import (cast)
from randomizer.logic.renders import (update_ally_challenge)
from randomizer.logic.progression.prizelocations.access import (can_access_monstro_town, can_damage_enemies_with_spells, expect_good_movement, not_earlygame, expect_halfway_decent_movement, almost_earlygame, is_midgame, expect_ok_movement, lategame)
from randomizer.types.logic import (Inventory)
from randomizer.types.prize import (Prize)
from randomizer.types.prizelocation import (BossFightLocation, BossFightLocationNPC, ShuffleLocationSelector, WorldAreaEnum)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (NPC_1)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (UsableEventScriptCommand)
if TYPE_CHECKING:
    from randomizer.types.gameworld import (GameWorld)


def render_dojo_first_fight(world: GameWorld, prize: BossFightPrize) -> None:
    """Apply animation changes for Dojo first fight."""
    m = prize.smallest_npc()
    # Check if prize is a mimic-type boss
    duration = 45
    

    if isinstance(
        prize, (PandoriteBossFight, HidonBossFight, BoxBoyBossFight, ChesterBossFight)
    ):
        cast(
            ActionQueueAsync,
            world.event_scripts.get_command_by_identifier("dojo_boss_1_initiate_aq"),
        ).set_subscript(get_mimic_rise_dojo())
    else:
        if m.animations.dojo_challenge is not None:
            duration = max(45, m.animations.dojo_challenge.total_duration + 12)
            world.event_scripts.get_subscript_command_by_identifier(
                "dojo_boss_1_initiate_aq",
                "dojo_boss_1_initiate",
                A_SetSpriteSequence,
            ).set_index(m.animations.dojo_challenge.sequence_id)
            world.event_scripts.get_subscript_command_by_identifier(
                "dojo_boss_1_initiate_aq", "dojo_boss_1_pause", A_Pause
            ).set_length(duration)
        else:
            world.event_scripts.get_subscript_command_by_identifier(
                "dojo_boss_1_initiate_aq",
                "dojo_boss_1_initiate",
                A_SetSpriteSequence,
            ).set_index(0)
    if m.animations.recoil is not None:
        world.event_scripts.get_subscript_command_by_identifier(
            "dojo_boss_1_recoil_aq", "dojo_boss_1_recoil", A_SetSpriteSequence
        ).set_index(m.animations.recoil.sequence_id)
        world.event_scripts.get_subscript_command_by_identifier(
            "dojo_boss_1_recoil_aq", "dojo_boss_1_recoil_pause", A_Pause
        ).set_length(m.animations.recoil.total_duration)
    else:
        world.event_scripts.delete_subscript_command_by_identifier(
            "dojo_boss_1_recoil_aq", "dojo_boss_1_recoil"
        )
    world.event_scripts.replace_subscript_command_by_identifier(
        "EVENT_2067_action_queue_0", "jagger_looks_around", A_FaceNorthwest()
    )
    update_ally_challenge(world, duration, "EVENT_2066_player_challenge_aq")


class DojoFirstFight(BossFightLocation):
    _bias = True
    _originally_held = JaggerBossFight
    _rooms = [R255_MONSTRO_TOWN_JINXS_DOJO]
    _id = ShuffleLocationSelector.DOJO_BOSS_FIGHT_1
    _world_area = WorldAreaEnum.MONSTRO_TOWN
    _pack_id = PACK189_DOJO_PREFIGHT
    _post_unlocks_event_id = E1213_DOJO_1_BOSS_UNLOCKS
    _allow_run_away = True
    _resets_on_game_over = False

    _npc_slots = [
        BossFightLocationNPC(
            R255_MONSTRO_TOWN_JINXS_DOJO,
            NPC_1,
            sequence_setter_event_id=E0815_DOJO_SHUFFLED_NPC_ANIMATION_LOADER,
        ),
    ]
    _dialogs_expecting_replacement = [
        DI3044_DOJO_BOSS_1_AFTER_DEFEAT,
        DI3352_DOJO_BOSS_1_FULLY_DEFEATED,
    ]
    _hint = [
        # SetVarToConst(PRIMARY_TEMP_7000, 289),
        # RunDialog(
        #     dialog_id=DI2010_DEBUG_7000,
        #     above_object=BOWSER,
        #     closable=True,
        #     sync=False,
        #     multiline=True,
        #     use_background=True,
        # ),
        JmpIfBitSet(DOJO_BOSS_1_DEFEATED, ["next"]),
        JmpIfBitSet(MAP_MONSTRO_TOWN, ["monstro_town_hint_text"]),
    ]

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return super().can_accept(prize, inventory, world) and (
            can_damage_enemies_with_spells(world, inventory)
            or not isinstance(prize, MokuraBossFight)
        )

    def can_access(self, inventory: Inventory, world: GameWorld) -> bool:
        return can_access_monstro_town(world, inventory) and is_midgame(world, inventory)

    def render(self, world: GameWorld) -> tuple[
        list[list[UsableEventScriptCommand]],
        list[UsableEventScriptCommand],
        list[tuple[int, int, int]],
    ]:
        op = super().render(world)
        assert isinstance(self.prize, BossFightPrize)
        render_dojo_first_fight(world, self.prize)
        return op


__all__ = ["DojoFirstFight"]
