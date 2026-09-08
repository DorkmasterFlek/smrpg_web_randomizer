"""Detection of provably-unsolvable prize placements.

Some prizes are *pinned*: the placer cannot move them, so no seed can ever
relocate them. There are two pinning sources:

* offset-driven boss fights (prize_offset / POP), which bypass place()
  and assign bosses by index, and
* every location that should_shuffle() excludes, which keeps whatever it
  originally held - including the vanilla character seats when recruit order
  is not shuffled.

An area gate whose requirement is pinned *inside the region that gate guards*
forms a closed cycle. The region is then unreachable from an empty inventory
in every seed, and nothing the placer does can open it. Placement does not
notice this directly - it surfaces much later as an unrelated-looking overflow
(e.g. key items with nowhere legal to go), after dozens of pointless retries.

This module finds those sealed regions up front.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from ..types.logic import Inventory
from ..types.flags import (
    BanditsWayGate, BanditsWayGating,
    KeroSewersGate, KeroSewersGating,
    ForestMazeGate, ForestMazeGating,
    PipeVaultGate, PipeVaultGating,
    Moleville1Gate, Moleville1Gating,
    BoosterTowerGate, BoosterTowerGating,
    BoosterHillGate, BoosterHillGating,
    MarrymoreGate, MarrymoreGating,
    YaridovichGate, YaridovichGating,
    SeaGate, SeaGating,
    LandsEndGate, LandsEndGating,
    BelomeTempleGate, BelomeTempleGating,
    MonstroTownGate, MonstroTownGating,
    NimbusGate, NimbusGating,
    BarrelVolcanoGate, BarrelVolcanoGating,
    BowsersKeepGate, BowsersKeepGating,
    FactoryGate, FactoryGating,
)
from ..types.prize import BossFightPrize, CharacterPrize
from ..types.prizelocation import KeyItemLocation

if TYPE_CHECKING:
    from ..types.gameworld import GameWorld
    from ..types.prize import Prize
    from ..types.prizelocation import PrizeLocation


class SettingsRelaxed(Exception):
    """A gate had to be forced open, so the seed must be rolled again.

    The gates are not only a placement rule - apply_shuffler_independent_settings
    turns them into ROM state (the Booster Tower door's solidity/tile mods and
    TOWER_OPENED, for one) long before the shuffler runs. Flipping a gate
    mid-shuffle therefore only convinces *placement* that the door is open; the
    game still wants the original key, and the seed is unbeatable. So the flag
    is changed on the shared Settings object and the whole world is rebuilt from
    scratch, with every settings-derived step seeing the final gate values.
    """

    def __init__(self, changes: list[str]):
        self.changes = changes
        super().__init__(
            "Gates forced open to break a placement deadlock; rebuilding world: "
            + "; ".join(changes)
        )


# Every area gate, paired with its gating enum. All 17 have an OPEN option.
AREA_GATES: list[tuple[type, type]] = [
    (BanditsWayGate, BanditsWayGating),
    (KeroSewersGate, KeroSewersGating),
    (ForestMazeGate, ForestMazeGating),
    (PipeVaultGate, PipeVaultGating),
    (Moleville1Gate, Moleville1Gating),
    (BoosterTowerGate, BoosterTowerGating),
    (BoosterHillGate, BoosterHillGating),
    (MarrymoreGate, MarrymoreGating),
    (YaridovichGate, YaridovichGating),
    (SeaGate, SeaGating),
    (LandsEndGate, LandsEndGating),
    (BelomeTempleGate, BelomeTempleGating),
    (MonstroTownGate, MonstroTownGating),
    (NimbusGate, NimbusGating),
    (BarrelVolcanoGate, BarrelVolcanoGating),
    (BowsersKeepGate, BowsersKeepGating),
    (FactoryGate, FactoryGating),
]


class OptimisticInventory(Inventory):
    """An inventory that claims to hold every prize *except* the pinned ones.

    Pinned prizes must still be earned by reaching the location they are pinned
    to; everything else is assumed already in hand. Reachability computed under
    this assumption is an upper bound on real reachability, so a location that
    is unreachable here is unreachable in every seed.
    """

    def __init__(self, pinned_classes: tuple[type[Prize], ...]):
        super().__init__()
        self._pinned_classes = pinned_classes

    def _is_pinned(self, item_type: type[Prize]) -> bool:
        return issubclass(item_type, self._pinned_classes)

    def has_item(self, item_type: type[Prize]) -> bool:
        if self._is_pinned(item_type):
            return super().has_item(item_type)
        return True

    def has_item_count(self, item_type: type[Prize], value=1) -> bool:
        if self._is_pinned(item_type):
            return super().has_item_count(item_type, value)
        return True

    def has_one_of(self, item_types: list[type[Prize]]) -> bool:
        return any(self.has_item(t) for t in item_types)


def pinned_prizes(world: GameWorld) -> dict[PrizeLocation, type[Prize]]:
    """Map every location the placer cannot fill freely to the prize it must hold.

    Offset-driven boss fights win over should_shuffle, matching the order
    shuffle_prizes applies them in.
    """
    from .shufflers.items import should_shuffle

    pinned: dict[PrizeLocation, type[Prize]] = {}

    for loc in world.locations.values():
        if should_shuffle(loc, world):
            continue
        if loc.originally_held is not None:
            pinned[loc] = loc.originally_held

    if world.settings.debug_mode and world.settings.prize_offset is not None:
        from .offset_preview import compute_offset_assignments

        boss_overrides = compute_offset_assignments(
            world.settings.prize_offset,
            mimic_offset=world.settings.mimic_offset,
            total_star_pieces=0,
            enable_slots=False,
            enable_mimics=False,
            enable_coins=False,
        )["boss_overrides"]
        by_name = {type(loc).__name__: loc for loc in world.locations.values()}
        for loc_name, prize_cls in boss_overrides.items():
            loc = by_name.get(loc_name)
            if loc is not None:
                pinned[loc] = prize_cls

    return pinned


def _collect_pinned(
    world: GameWorld,
    pinned: dict[PrizeLocation, type[Prize]],
    inventory: Inventory,
) -> Inventory:
    """Fixpoint: repeatedly bank the prize of every pinned location we can reach."""
    collected: set[PrizeLocation] = set()
    progress = True
    while progress:
        progress = False
        for loc, prize_cls in pinned.items():
            if loc in collected:
                continue
            if loc.can_access(inventory, world):
                inventory.append(prize_cls())
                collected.add(loc)
                progress = True
    return inventory


def sealed_locations(
    world: GameWorld,
    pinned: dict[PrizeLocation, type[Prize]] | None = None,
) -> list[PrizeLocation]:
    """Must-fill locations that are unreachable even under the most generous
    assumption about what the placer could hand the player.

    A non-empty result means the settings are unsolvable for *every* seed.
    """
    if pinned is None:
        pinned = pinned_prizes(world)

    # Only boss and character prizes are unique enough to reason about safely:
    # an item class pinned in one location may still have a free copy in the
    # pool, and treating it as unobtainable would give false positives.

    pinned_classes = tuple(
        cls for cls in dict.fromkeys(pinned.values())
        if issubclass(cls, (BossFightPrize, CharacterPrize))
    )
    inventory = _collect_pinned(
        world, pinned, OptimisticInventory(pinned_classes)
    )
    return [
        loc
        for loc in world.locations.values()
        if not loc.can_be_empty(world) and not loc.can_access(inventory, world)
    ]


def _gate_label(gate_cls: type, world: GameWorld) -> str:
    flag = world.settings.get_flag(gate_cls)
    return flag.name or gate_cls.__name__


def relax_deadlocked_gates(world: GameWorld) -> list[str]:
    """Open only the area gates that actually deadlock the world.

    Offsets are meant to override any other placement setting, but the gate
    flags still evaluate against the bosses the offset just pinned - so a gate
    can demand a boss that the offset locked inside the region that gate guards.
    Where that happens, the gate loses.

    Greedy, one gate at a time: try each closed gate, keep whichever unseals the
    most locations, repeat. Gates that are not part of a cycle are left alone.
    Returns a human-readable description of each gate that was forced open.
    """
    if not (world.settings.debug_mode and world.settings.prize_offset is not None):
        return []

    changes: list[str] = []
    while True:
        sealed = sealed_locations(world)
        if not sealed:
            break

        best: tuple[int, type, type, object] | None = None
        for gate_cls, gating in AREA_GATES:
            flag = world.settings.get_flag(gate_cls)
            was = flag.selected
            if was == gating.OPEN:
                continue
            flag.select(gating.OPEN)
            world.settings._is_flag_value_cache.clear()
            remaining = len(sealed_locations(world))
            flag.select(was)
            world.settings._is_flag_value_cache.clear()
            if best is None or remaining < best[0]:
                best = (remaining, gate_cls, gating, was)

        # No single gate improves things - leave the rest alone and let the
        # pre-flight check report the sealed region instead of silently
        # flattening every gate the user chose.
        if best is None or best[0] >= len(sealed):
            break

        _, gate_cls, gating, was = best
        world.settings.get_flag(gate_cls).select(gating.OPEN)
        world.settings._is_flag_value_cache.clear()
        changes.append(
            f"{_gate_label(gate_cls, world)}: "
            f"{getattr(was, 'value', was)} -> Always open "
            f"(offset pinned its requirement behind the gate itself)"
        )

    return changes


def assert_solvable(world: GameWorld) -> None:
    """Fail fast if no seed can satisfy these settings.

    Deliberately uses the same optimistic model as sealed_locations rather
    than the real prize pool. A pool-based check would have to know which
    locations *will* be filled: a star-piece slot, for instance, is only
    reachable once its parent boss slot holds a boss, so before place()
    runs it looks unreachable and a perfectly solvable world gets called sealed.
    Assuming every non-pinned prize is already in hand sidesteps that entirely,
    and still proves unsolvability - if a location is unreachable even when the
    player is handed everything the placer could ever give them, no seed can
    reach it.
    """
    from ..types.gameworld import WorldBuildingException

    sealed = sealed_locations(world)
    if not sealed:
        return

    names = sorted(type(loc).__name__ for loc in sealed)
    shown = ", ".join(names[:12]) + (" ..." if len(names) > 12 else "")
    raise WorldBuildingException(
        f"These settings are unsolvable for every seed: {len(sealed)} location(s) "
        f"that must hold a prize can never be reached, even if the player is handed "
        f"every item in the game for free. Some gate requires a boss or character "
        f"that is pinned behind that very gate, so the region can never open - this "
        f"is a closed cycle, not bad luck, and retrying cannot help. "
        f"Sealed: {shown}"
    )


# ---------------------------------------------------------------------------
# Key-item pool placeability
#
# With KeyItemsAnywhere off, a KeyPrize can only live in a KeyItemLocation, and
# the design is 1:1 - one key item per key location. sealed_locations() can't
# see a shortfall here: key slots are can-be-empty, so it never flags them, and
# its all-items-in-hand optimism hands the player the island's keys for free.
# These helpers reason about the key pool specifically.
# ---------------------------------------------------------------------------


def _reach_inventory(world: GameWorld, seed_items: list[Prize]) -> Inventory:
    """Reachability fixpoint seeded with seed_items: also collects every
    already-placed prize (offset-pinned bosses, static fills) from locations
    that become reachable. Mirrors collect_accessible_items but with a seed."""
    acc = Inventory(list(seed_items))
    checked: set[PrizeLocation] = set()
    progress = True
    while progress:
        progress = False
        for loc in world.locations.values():
            if loc in checked:
                continue
            if loc.has_item and loc.can_access(acc, world):
                acc.append(loc.prize)
                checked.add(loc)
                progress = True
    return acc


def unplaceable_key_items(
    world: GameWorld,
    key_pool: list[Prize],
    non_key_pool: list[Prize],
) -> tuple[int, list[str], list[str]]:
    """Deterministic, non-mutating assumed fill of the key-item pool only.

    Returns (count, leftover_item_names, unreachable_location_names). A slot
    is reachable for item X assuming the player holds every OTHER unplaced key
    item, all non-key pool items, and the keys already committed here - plus
    whatever pre-placed bosses those unlock. Most-constrained-first ordering
    (place the item with the fewest options next) makes this near-complete
    without backtracking; because opening a gate only ever adds reachability,
    a zero result under some gate config is monotone in that config.
    """
    from .shufflers.items import should_shuffle

    key_locs = [
        l for l in world.locations.values()
        if isinstance(l, KeyItemLocation) and should_shuffle(l, world) and not l.has_item
    ]
    remaining = list(key_pool)
    occupied: set[PrizeLocation] = set()
    committed: list[Prize] = []

    while remaining:
        best: tuple[int, int, list[PrizeLocation]] | None = None
        seen_types: set[type] = set()
        for idx, item in enumerate(remaining):
            if type(item) in seen_types:
                continue
            seen_types.add(type(item))
            others = remaining[:idx] + remaining[idx + 1:]
            inv = _reach_inventory(world, non_key_pool + others + committed)
            slots = [
                l for l in key_locs
                if l not in occupied
                and l.can_access(inv, world)
                and l.can_accept(item, inv, world)
            ]
            if slots and (best is None or len(slots) < best[0]):
                best = (len(slots), idx, slots)
        if best is None:
            leftover = sorted(type(p).__name__ for p in remaining)
            unreached = sorted(
                type(l).__name__ for l in key_locs if l not in occupied
            )
            return len(remaining), leftover, unreached
        _, idx, slots = best
        occupied.add(slots[0])
        committed.append(remaining.pop(idx))
    return 0, [], []


def assert_key_pool_balanced(
    world: GameWorld,
    key_pool: list[Prize],
) -> None:
    """Guard the 1:1 design invariant: never more key items than key slots.

    A homeless key item (more KeyPrize items than shuffle-target KeyItemLocations)
    means a flag combination removed a location without removing its item, or
    added an item without a home. Fewer items than slots is fine - the surplus
    slots hold filler - so this only fires on the genuinely-broken direction.
    """
    from .shufflers.items import should_shuffle
    from ..types.gameworld import WorldBuildingException

    key_locs = [
        l for l in world.locations.values()
        if isinstance(l, KeyItemLocation) and should_shuffle(l, world)
    ]
    if len(key_pool) <= len(key_locs):
        return

    items = sorted(type(p).__name__ for p in key_pool)
    locs = sorted(f"{type(l).__name__} (home of {l.originally_held.__name__})"
                  if l.originally_held else type(l).__name__
                  for l in key_locs)
    raise WorldBuildingException(
        f"Key-item pool is misconfigured: {len(key_pool)} key items but only "
        f"{len(key_locs)} key-item locations to hold them. A key item can only "
        f"live in a key-item location, so at least "
        f"{len(key_pool) - len(key_locs)} of them have no home. This is a data "
        f"bug (a flag removed a location without removing its item, or vice "
        f"versa), not bad luck.\n"
        f"KEY ITEMS ({len(items)}):\n  " + "\n  ".join(items) + "\n"
        f"KEY LOCATIONS ({len(locs)}):\n  " + "\n  ".join(locs)
    )


def relax_key_pool_deadlock(
    world: GameWorld,
    key_pool: list[Prize],
    non_key_pool: list[Prize],
) -> list[str]:
    """Open area gates until the key-item pool can be placed (POP only).

    The offset pins bosses so that a cluster of key slots sits behind gates that
    can only be opened by keys living in that same cluster - the key pool can't
    bootstrap. Offsets override placement settings, so the gates give way.
    Greedy: open the single gate that reduces the unplaceable count most, repeat.
    If no single gate helps but the pool still doesn't fit (AND-chained regions),
    fall back to opening every remaining gate - proven to make it placeable.
    Mutates the settings' gate flags and returns a description of each open.
    """
    if not (world.settings.debug_mode and world.settings.prize_offset is not None):
        return []

    changes: list[str] = []

    def unplaceable() -> int:
        return unplaceable_key_items(world, key_pool, non_key_pool)[0]

    while unplaceable() > 0:
        best: tuple[int, type, type, object] | None = None
        for gate_cls, gating in AREA_GATES:
            flag = world.settings.get_flag(gate_cls)
            was = flag.selected
            if was == gating.OPEN:
                continue
            flag.select(gating.OPEN)
            world.settings._is_flag_value_cache.clear()
            remaining = unplaceable()
            flag.select(was)
            world.settings._is_flag_value_cache.clear()
            if best is None or remaining < best[0]:
                best = (remaining, gate_cls, gating, was)

        if best is not None and best[0] < unplaceable():
            _, gate_cls, gating, was = best
            world.settings.get_flag(gate_cls).select(gating.OPEN)
            world.settings._is_flag_value_cache.clear()
            changes.append(
                f"{_gate_label(gate_cls, world)}: "
                f"{getattr(was, 'value', was)} -> Always open "
                f"(offset pinned key items behind this gate)"
            )
            continue

        # No single gate helps (AND-chained regions) but the pool still doesn't
        # fit. Open everything still closed - guaranteed placeable - and stop.
        opened_any = False
        for gate_cls, gating in AREA_GATES:
            flag = world.settings.get_flag(gate_cls)
            if flag.selected == gating.OPEN:
                continue
            was = flag.selected
            flag.select(gating.OPEN)
            changes.append(
                f"{_gate_label(gate_cls, world)}: "
                f"{getattr(was, 'value', was)} -> Always open "
                f"(offset pinned key items behind a chain of gates)"
            )
            opened_any = True
        world.settings._is_flag_value_cache.clear()
        if not opened_any:
            break

    return changes


def assert_key_pool_placeable(
    world: GameWorld,
    key_pool: list[Prize],
    non_key_pool: list[Prize],
) -> None:
    """Fail fast if the key-item pool still can't be placed after relaxation.

    Only reached when opening every gate did not help - so it is a genuine
    dead end, not a gate cycle. Lists both sides so the disparity is findable.
    """
    from ..types.gameworld import WorldBuildingException

    count, leftover, unreachable = unplaceable_key_items(
        world, key_pool, non_key_pool
    )
    if count == 0:
        return

    raise WorldBuildingException(
        f"{count} key item(s) cannot be placed: they may only go in key-item "
        f"locations, and that many key-item locations can never be reached in "
        f"any order, even with every area gate open. Retrying cannot help.\n"
        f"UNPLACEABLE KEY ITEMS ({len(leftover)}):\n  " + "\n  ".join(leftover) + "\n"
        f"UNREACHABLE KEY LOCATIONS ({len(unreachable)}):\n  "
        + "\n  ".join(unreachable)
    )
