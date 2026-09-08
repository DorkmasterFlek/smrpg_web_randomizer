import pickle
from typing import Callable

from .types.gameworld import GameWorld, Settings
from .data.allies.allies import ally_collection
from .data.battle_animation._02.export import bank as bank02
from .data.battle_animation._35.export import bank as bank35
from .data.battle_animation._3A.export import bank as bank3A
from .data.battle_dialogs.battle_dialogs import collection as battle_dialog_collection
from .data.dialogs.dialogs import data as dialog_collection
from .data.enemies.enemies import ENEMIES
from .data.enemy_attacks.attacks import collection as enemy_attack_collection
from .data.items.items import ITEMS
from .data.monster_ai.monster_scripts import monster_scripts
from .data.overworld_scripts.event.events import events
from .data.overworld_scripts.animation.actionqueues import actions
from .data.packets.packets import ALL_PACKETS
from .data.packs.pack_collection import pack_collection
from .data.rooms.rooms import room_collection
from .data.shops.shops import shop_collection
from .data.spells.spells import ALL_SPELLS
from .data.sprites.sprites import sprites
from .data.world_map_locations.world_map_locations import world_map_location_collection
from .data.palettes.event_palettes import ALL_EVENT_PALETTES
from .data.palettes.sprite_palettes import ALL_SPRITE_PALETTES
from .logic.solvability import SettingsRelaxed


# Each seed needs its own copy of every collection, because randomizing mutates
# them in place. deepcopy costs ~5.1s per generation across these twenty-odd
# object graphs; a pickle round-trip produces the same independent copies in
# ~0.9s, because it walks the graph in C instead of dispatching per object in
# Python. The blobs are built once at import so only the load is paid per seed.
#
# Anything added here must be picklable, which for these plain data classes it
# already is. If that ever stops being true the failure is immediate and loud at
# import, not a subtly-shared object at runtime.
def _snapshot(obj: object) -> bytes:
    return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)


_PRISTINE: dict[str, bytes] = {}


def _fresh(name: str, obj: object):
    """An independent copy of a module-level collection."""
    blob = _PRISTINE.get(name)
    if blob is None:
        blob = _PRISTINE[name] = _snapshot(obj)
    return pickle.loads(blob)


# Current version number
VERSION = '9.0.0'

def create(
    seed: int | str,
    settings: Settings,
    progress_callback: Callable[[str, int], None] | None = None,
    debug_bps_patches: bool = False,
    placement_cache: bytes | None = None,
) -> GameWorld:
    """Create a patch for the given seed.

    Deep copies all mutable collections so modifications during randomization
    don't affect subsequent seed generations.

    Args:
        seed: The randomizer seed value.
        settings: The randomizer settings/flags.
        progress_callback: Optional callback for progress updates. Called with
            (message: str, percent: int) during generation.
        debug_bps_patches: If True, generate separate BPS patches for each render
            stage (only works in debug/development environment).
        placement_cache: A blob from a previous run of this exact seed and
            hashed flag string. When given, the placement search is skipped and
            replayed from the blob instead. The finished world always carries a
            freshly captured blob on placement_result
    """

    def build() -> GameWorld:
        return GameWorld(
            seed,
            VERSION,
            settings,
            _fresh("ally_collection", ally_collection),
            {
                0x02: _fresh("bank02", bank02),
                0x35: _fresh("bank35", bank35),
                0x3A: _fresh("bank3A", bank3A),
            },
            _fresh("battle_dialog_collection", battle_dialog_collection),
            _fresh("dialog_collection", dialog_collection),
            _fresh("ENEMIES", ENEMIES),
            _fresh("enemy_attack_collection", enemy_attack_collection),
            _fresh("ITEMS", ITEMS),
            _fresh("monster_scripts", monster_scripts),
            _fresh("events", events),
            _fresh("actions", actions),
            _fresh("ALL_PACKETS", ALL_PACKETS),
            _fresh("pack_collection", pack_collection),
            _fresh("room_collection", room_collection),
            _fresh("shop_collection", shop_collection),
            _fresh("ALL_SPELLS", ALL_SPELLS),
            _fresh("sprites", sprites),
            _fresh("world_map_location_collection", world_map_location_collection),
            _fresh("ALL_EVENT_PALETTES", ALL_EVENT_PALETTES),
            _fresh("ALL_SPRITE_PALETTES", ALL_SPRITE_PALETTES),
            progress_callback=progress_callback,
            debug_bps_patches=debug_bps_patches,
            placement_cache=placement_cache,
        )

    # A gate may be forced open to break an offset-induced deadlock. The flag
    # then lives on the shared settings object, so building again from scratch
    # makes every settings-derived step - including the pre-shuffler pass that
    # writes the door's ROM state - see the corrected value. Relaxation happens
    # in two stages (region seals in _shuffle_items, then key-pool islands in
    # shuffle_prizes), so more than one rebuild can be needed; loop until it
    # builds clean. Each round opens at least one gate, and there are only 17,
    # so the bound is generous and purely a runaway guard.
    for _ in range(20):
        try:
            return build()
        except SettingsRelaxed:
            continue
    return build()

