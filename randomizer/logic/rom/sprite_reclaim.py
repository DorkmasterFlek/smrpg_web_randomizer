"""Cosmetic-independent free space for the sprite packer in the dialog banks.

`SpriteCollection.render` is the single most expensive step in patch assembly, so
its output is cached per seed (see `sprite_cache`). A cached blob is only safe to
replay if the packer saw the same free space when it was built, and 55 of the 58
reclaim banks handed to it already satisfy that: their bounds come from monster
scripts, action scripts and battle animations, which do not move with cosmetics.

The three dialog banks are the exception. Their reclaim range starts wherever the
compressed dialog data happens to end, and cosmetics rewrite dialog text -
RemakeNames renames every enemy, item, spell and attack; RemoveFlashes and
PlayAsStarter shift it too. Measured across 3 seeds x 4 cosmetic combinations the
end moved by up to 209 bytes, which is enough to relocate sprite writes and, on
replay of a blob built under different cosmetics, to lay graphics over live text.

So the sprite packer is given a fixed floor per dialog bank instead of the live
end. The floors sit ~1KB above the worst end seen in that sweep and cost ~1KB
each out of the 25-42KB those banks contribute, which is a rounding error against
the 2.2MB the packer places. `dialog_reclaim_ranges` enforces the invariant that
makes the floors sound: if real dialog data ever reaches one, that is a genuine
overflow and it raises rather than letting the packer overwrite text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld

# bank end -> first address the sprite packer may use in that bank.
DIALOG_SPRITE_FLOORS: dict[int, int] = {
    0x22FD18: 0x228D00,
    0x23F2D5: 0x235300,
    0x249000: 0x243300,
}


class DialogReclaimOverflow(Exception):
    """Dialog data reached the address reserved for sprite graphics."""


def dialog_reclaim_ranges(world: GameWorld) -> list[tuple[int, int]]:
    """The dialog-bank ranges the sprite packer may use, pinned per bank.

    Same result for every cosmetic combination of a given seed, which is what
    makes a cached sprite render replayable across permalink re-rolls.
    """
    ranges: list[tuple[int, int]] = []
    for start, end in world.overworld_dialogs.get_unused_ranges():
        floor = DIALOG_SPRITE_FLOORS.get(end)
        if floor is None:
            ranges.append((start, end))
            continue
        if start > floor:
            raise DialogReclaimOverflow(
                f"dialog data in the bank ending 0x{end:06X} runs to 0x{start:06X}, "
                f"past the 0x{floor:06X} floor reserved for sprite graphics. Raise "
                f"the floor in DIALOG_SPRITE_FLOORS (and invalidate cached sprite "
                f"renders, which were packed against the old one)."
            )
        ranges.append((floor, end))
    return ranges
