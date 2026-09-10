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
from randomizer.logic.progression.prizelocations.access import (can_access_monstro_town, can_damage_enemies_with_spells, not_earlygame, is_early_midgame, is_late_midgame, is_lategame, expect_good_movement, expect_halfway_decent_movement, almost_earlygame, is_midgame, expect_ok_movement, lategame)
from randomizer.types.logic import (Inventory)
from randomizer.types.prize import (Prize)
from randomizer.types.prizelocation import (BossFightLocation, BossFightLocationNPC, ShuffleLocationSelector, WorldAreaEnum)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (NPC_0)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (UsableEventScriptCommand)
if TYPE_CHECKING:
    from randomizer.types.gameworld import (GameWorld)


class DojoSecondFight(BossFightLocation):
    _bias = True
    _originally_held = Jinx1BossFight
    _rooms = [R255_MONSTRO_TOWN_JINXS_DOJO]
    _id = ShuffleLocationSelector.DOJO_BOSS_FIGHT_2
    _world_area = WorldAreaEnum.MONSTRO_TOWN
    _override_id = 515
    _default_battlefield = BF46_JINXS_DOJO
    _pack_id = PACK178_DOJO_FIGHT_1
    _post_unlocks_event_id = E1214_DOJO_2_BOSS_UNLOCKS
    _allow_run_away = True
    _resets_on_game_over = False
    _npc_slots = [
        BossFightLocationNPC(
            R255_MONSTRO_TOWN_JINXS_DOJO,
            NPC_0,
            sequence_setter_event_id=E0815_DOJO_SHUFFLED_NPC_ANIMATION_LOADER,
        ),
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
        render_dojo_fight(
            world,
            self.prize,
            "dojo_boss_2_initiate_aq",
            "dojo_boss_2_initiate",
            "dojo_boss_2_pause",
            "EVENT_2068_player_challenge_aq"
        )
        # If the swapped-in NPC's sprite has a non-gridplane mold 0,
        # set cannot_clone on the room object to prevent VRAM conflicts.
        room = world.rooms._rooms[R255_MONSTRO_TOWN_JINXS_DOJO]
        assert room is not None
        npc_obj = room.get_npc_by_target_id(NPC_0)
        sprite = world.get_sprite(npc_obj._npc.sprite_id)
        if not sprite.animation.properties.molds[0].gridplane:
            npc_obj.set_cannot_clone(True)
        return op


__all__ = ["DojoSecondFight"]
