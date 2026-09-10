from __future__ import annotations
from typing import TYPE_CHECKING
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import *
from randomizer.data.variables.room_names import *
from randomizer.data.variables.event_script_names import *
from randomizer.data.variables.action_script_names import *
from randomizer.data.variables.pack_names import *
from randomizer.logic.progression.prizes import *
from randomizer.types.flags import *
from randomizer.logic.renders import (render_dojo_fight)
from randomizer.logic.progression.prizelocations.access import (can_access_fifth_dojo_boss, can_damage_enemies_with_spells, expect_good_movement, not_earlygame, expect_halfway_decent_movement, almost_earlygame, is_midgame, expect_ok_movement, lategame)
from randomizer.types.logic import (Inventory)
from randomizer.types.prize import (Prize)
from randomizer.types.prizelocation import (BossFightLocation, BossFightLocationNPC, ShuffleLocationSelector, WorldAreaEnum)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (NPC_4)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (UsableEventScriptCommand)
if TYPE_CHECKING:
    from randomizer.types.gameworld import (GameWorld)


class DojoFifthFight(BossFightLocation):
    _bias = True
    _originally_held = Jinx4BossFight
    _rooms = [R255_MONSTRO_TOWN_JINXS_DOJO]
    _id = ShuffleLocationSelector.DOJO_BOSS_FIGHT_POSTGAME
    _world_area = WorldAreaEnum.MONSTRO_TOWN
    _override_id = 525
    _default_battlefield = BF46_JINXS_DOJO
    _remake_only = True
    _pack_id = PACK119_DOJO_POSTGAME
    _post_unlocks_event_id = E1217_DOJO_5_BOSS_UNLOCKS
    _allow_run_away = True
    _resets_on_game_over = False
    _npc_slots = [
        BossFightLocationNPC(
            R255_MONSTRO_TOWN_JINXS_DOJO,
            NPC_4,
            sequence_setter_event_id=E0815_DOJO_SHUFFLED_NPC_ANIMATION_LOADER,
        ),
    ]
    _access_conditions = "Must fully clear the Dojo and use the Stay Voucher. Not a check if \"Enable Remake content\" is turned off."

    def can_accept(self, prize: Prize, inventory: Inventory, world: GameWorld) -> bool:
        return super().can_accept(prize, inventory, world) and (
            can_damage_enemies_with_spells(world, inventory)
            or not isinstance(prize, MokuraBossFight)
        )

    def can_access(self, inventory: Inventory, world: GameWorld) -> bool:
        return can_access_fifth_dojo_boss(world, inventory)

    def render(self, world: GameWorld) -> tuple[
        list[list[UsableEventScriptCommand]],
        list[UsableEventScriptCommand],
        list[tuple[int, int, int]],
    ]:
        op = super().render(world)
        assert isinstance(self.prize, BossFightPrize)
        if not isinstance(
            self.prize, (Jinx1BossFight, Jinx2BossFight, Jinx3BossFight, Jinx4BossFight)
        ):
            render_dojo_fight(
                world,
                self.prize,
                "dojo_boss_5_initiate_aq",
                "dojo_boss_5_initiate",
                "dojo_boss_5_pause",
                "EVENT_2247_player_challenge_aq"
            )
        return op


__all__ = ["DojoFifthFight"]
