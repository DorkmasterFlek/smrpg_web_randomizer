"""Allow running away from certain shuffled fights.

Extracted from the apply_shuffler_results orchestrator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from randomizer.data.variables.pack_names import (
    PACK156_SEWER_CHEST_FIGHT,
    PACK157_SHIP_CHEST_FIGHT,
    PACK158_VALLEY_CHEST_FIGHT,
    PACK160_SLOTS_CHEST_FIGHT,
)
from randomizer.types.flags import (MimicsAnywhere, SlotsAnywhere)
from randomizer.types.prizelocation import (BossFightLocation)

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld



def set_fight_run_away_flags(world: GameWorld) -> None:
    # NOTE: update_changed_room_partitions(world) used to be here but was moved
    # to after the protagonist sprite remap below - the orchestrator reads
    # sprite data from world.sprites for VRAM calculations, and the per-character
    # protagonist sprites aren't written to slots 31-37 until after this point.

    # (Freestanding frog-coin animation is now handled per-placement in the
    # StandingLocation render above: a non-vanilla frog coin uses the animated
    # FROG_COIN_BASE model when its room has a Coins buffer in slot C, else the
    # static FrogCoinObject. Vanilla frog coins keep their room-data NPC.)

    # Set can_run_away for each boss fight location's formation
    # This must happen after all renders to ensure the correct formation is used
    # Each boss fight is unique, so each formation should only be used by one location
    for location in world.locations.values():
        if isinstance(location, BossFightLocation) and location.prize is not None:
            pack = world.battle_packs._packs[location._pack_id]
            for formation in pack.formations:
                formation.set_can_run_away(location.allow_run_away)
                if not location.allow_run_away:
                    formation.set_unknown_bit(True)

    # Allow running away from the three mimic-reserved packs when MimicsAnywhere
    # is enabled, and from the slots-specific mimic 3 pack when SlotsAnywhere is
    # enabled. Clearing both bits 0 and 1 of formation meta byte 3 ($7EFA1E) puts
    # the formation in the 80% flee-success bucket (vs 50% with only can_run_away
    # cleared). Must run after the loop above, which otherwise resets
    # can_run_away to location.allow_run_away (False for mimic locations).
    if world.settings.isflag_enabled(MimicsAnywhere):
        for pack_id in (PACK156_SEWER_CHEST_FIGHT, PACK157_SHIP_CHEST_FIGHT, PACK158_VALLEY_CHEST_FIGHT):
            for formation in world.battle_packs._packs[pack_id].formations:
                formation.set_can_run_away(True)
                formation.set_unknown_bit(False)
    if world.settings.isflag_enabled(SlotsAnywhere):
        for formation in world.battle_packs._packs[PACK160_SLOTS_CHEST_FIGHT].formations:
            formation.set_can_run_away(True)
            formation.set_unknown_bit(False)


__all__ = ['set_fight_run_away_flags']
