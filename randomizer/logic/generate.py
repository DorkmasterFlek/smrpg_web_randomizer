"""One entry point for producing a seed and persisting it.

Generation itself (`randomizer.main.create`) is already a pure function of seed,
settings and an optional cached placement. What was not shared was everything
around it: looking up a stored placement, and writing the Seed row. That lived in
two near-identical copies inside the view handlers, so anything calling
generation from outside the request cycle - a queue worker, a management command,
a test - had to become a third copy.

This module is that shared path. Views, workers and tooling should all call
`generate_seed`; nothing outside it should need to know how the placement cache
is keyed or what a Seed row looks like.

No Django view, form or HTTP import belongs here, so a worker process can import
it without pulling in the request layer.
"""

from __future__ import annotations

import base64
import logging
import re
from typing import Callable

from django.db import transaction

from randomizer.logic.build_world import compute_seed_hash
from randomizer.logic.rom.shuffler_cache import ShufflerCacheError
from randomizer.logic.rom.sprite_cache import (serialize as serialize_sprites)
from randomizer.logic.progression.prizelocations.marios_house.starting_character1 import (
    StartingCharacter1,
)
from randomizer.main import VERSION, create
from randomizer.models import Seed, SpriteRender
from randomizer.types.flags import FlagError, PlayAsStarter
from randomizer.types.prize import CharacterPrize
from randomizer.types.gameworld import GameWorld
from randomizer.types.settings import Settings

logger = logging.getLogger(__name__)

# One "X(flag|flag:value)" group of the flag string.
_FLAG_BLOCK = r"([A-Z])\(([^)]*)\)"


def load_placement_cache(
    seed: int | str, settings: Settings, debug_mode: bool
) -> bytes | None:
    """A previous run's placement for this exact seed and hashed flag string.

    The seed hash deliberately excludes cosmetics, so changing a palette or a
    name flag reuses the placement and skips the search entirely - which is the
    whole point of storing it. Callers that key their own work (a queue keying
    jobs, say) must key on `settings.flag_string`, not on the full flag string
    including the cosmetic `R(...)` group, or they will miss every cache hit.

    Offset overrides mutate flags during generation and are a debug-only path, so
    they never reuse a cache.
    """
    if debug_mode or settings.prize_offset is not None or settings.mimic_offset is not None:
        return None
    row = (
        Seed.objects.filter(hash=compute_seed_hash(VERSION, seed, settings.flag_string))
        .only("placement")
        .first()
    )
    if row is None or not row.placement:
        return None
    return base64.b64decode(row.placement)


def encode_placement(world: GameWorld) -> str:
    """The world's placement blob, ready for `Seed.placement`."""
    return base64.b64encode(world.placement_result).decode() if world.placement_result else ""


def load_sprite_render(
    seed: int | str, settings: Settings, debug_mode: bool
) -> bytes | None:
    """A previous run's packed sprites for this seed and PlayAsStarter value"""
    if debug_mode or settings.prize_offset is not None or settings.mimic_offset is not None:
        return None
    row = (
        SpriteRender.objects.filter(
            seed__hash=compute_seed_hash(VERSION, seed, settings.flag_string),
            play_as_starter=settings.isflag_enabled(PlayAsStarter),
        )
        .only("blob")
        .first()
    )
    if row is None or not row.blob:
        return None
    return base64.b64decode(row.blob)


def save_sprite_render(row: Seed, world: GameWorld) -> None:
    """Store the render this world produced, replacing any row it supersedes."""
    if world.sprite_writes is None or world.sprite_reclaim_banks is None:
        return
    blob = serialize_sprites(world.sprite_writes, world.sprite_reclaim_banks, VERSION)
    SpriteRender.objects.update_or_create(
        seed=row,
        play_as_starter=world.settings.isflag_enabled(PlayAsStarter),
        defaults={"blob": base64.b64encode(blob).decode()},
    )


def ensure_sprite_render_variants(
    row: Seed,
    seed: int | str,
    world: GameWorld,
    *,
    debug_mode: bool = False,
) -> str:
    """Make sure both PlayAsStarter variants are stored for this seed so that anyone coming from the permalink doesnt have to regen SpriteCollection"""
    settings = world.settings
    if debug_mode or settings.prize_offset is not None or settings.mimic_offset is not None:
        return "skipped"

    other = not settings.isflag_enabled(PlayAsStarter)
    if row.sprite_renders.filter(play_as_starter=other).exists():
        return "present"

    mine = row.sprite_renders.filter(
        play_as_starter=settings.isflag_enabled(PlayAsStarter)
    ).first()
    if mine is None:
        return "skipped"

    starter = world.get_location(StartingCharacter1)
    if (
        starter is not None
        and isinstance(starter.prize, CharacterPrize)
        and starter.prize.ally.index == 0
    ):
        SpriteRender.objects.update_or_create(
            seed=row, play_as_starter=other, defaults={"blob": mine.blob}
        )
        return "copied"

    flipped = Settings()
    flipped.set_from_flag_string(settings.get_flag_string())
    flipped.set_boolean_flag(PlayAsStarter, other)
    # PlayAsStarter is gated on ShuffleCharacters, so on a seed that cannot turn it
    # on there is no second variant anyone can ask for.
    if flipped.isflag_enabled(PlayAsStarter) != other:
        return "skipped"

    other_world = build_world_for(seed, flipped, debug_mode=debug_mode)
    other_world.get_patch()  # discarded; run for the sprite render it leaves behind
    save_sprite_render(row, other_world)
    return "packed"


def build_world_for(
    seed: int | str,
    settings: Settings,
    *,
    debug_mode: bool = False,
    debug_bps_patches: bool = False,
    progress_callback: Callable[[str, int], None] | None = None,
) -> GameWorld:
    """Generate a world, replaying a stored placement when one is available.

    A stored blob that no longer applies - written against different flags, or by
    a build with different location/prize classes - is not fatal. It is reported
    and the seed is generated from scratch, which is what would have happened
    before any of it was cached.
    """
    world: GameWorld | None = None
    cache = load_placement_cache(seed, settings, debug_mode)
    if cache is not None:
        try:
            world = create(
                seed,
                settings,
                progress_callback=progress_callback,
                debug_bps_patches=debug_bps_patches,
                placement_cache=cache,
            )
        except ShufflerCacheError as exc:
            logger.warning(
                "stored placement rejected for seed %r (%s), regenerating", seed, exc
            )
    if world is None:
        world = create(
            seed,
            settings,
            progress_callback=progress_callback,
            debug_bps_patches=debug_bps_patches,
        )
    world.offer_sprite_blob(load_sprite_render(seed, settings, debug_mode))
    return world


def save_seed(world: GameWorld, seed: int | str, *, debug_mode: bool, race_mode: bool) -> Seed:
    """Persist the world as a Seed row, updating any row with the same hash"""
    with transaction.atomic():
        row, _ = Seed.objects.update_or_create(
            hash=world.hash,
            defaults={
                "seed": seed,
                "version": VERSION,
                "mode": "open",  # Deprecated but required by model
                "debug_mode": debug_mode,
                "flags": world.settings.flag_string,
                "file_select_char": world.file_select_character,
                "file_select_hash": world.file_select_hash,
                "race_mode": race_mode,
                "spoiler": world.spoiler,
                "placement": encode_placement(world),
            },
        )
        save_sprite_render(row, world)
    return row


def settings_from_flag_string(flag_string: str) -> Settings:
    """Build Settings from one flag string covering gameplay and cosmetics both.

    `Settings.set_from_flag_string` ignores anything it does not recognise, so a
    typo'd or truncated string parses cleanly into settings that are quietly not
    the ones asked for - a different flag string, a different seed hash, and a
    generated seed nobody wanted, with no error raised anywhere. Callers handed a
    string from somewhere else want to hear about that, so it is checked here.

    Raises:
        FlagError: the string names a flag that does not exist, or holds text
            outside any `X(...)` block.
    """
    settings = Settings()
    settings.set_from_flag_string(flag_string)

    known = settings._build_flag_id_map()
    ids = [
        entry.split(":", 1)[0].strip()
        for _, body in re.findall(_FLAG_BLOCK, flag_string)
        for entry in body.split("|")
        if entry.strip()
    ]
    unknown = [i for i in ids if i not in known]
    leftover = re.sub(_FLAG_BLOCK, "", flag_string).strip()
    if unknown or leftover:
        raise FlagError(
            f"unusable flag string {flag_string!r}: "
            + ", ".join(
                part
                for part in (
                    f"unknown flags {unknown}" if unknown else "",
                    f"unparsed text {leftover!r}" if leftover else "",
                )
                if part
            )
        )
    return settings


def generate_seed(
    seed: int | str,
    settings: Settings | str,
    *,
    debug_mode: bool = False,
    race_mode: bool = False,
    debug_bps_patches: bool = False,
    progress_callback: Callable[[str, int], None] | None = None,
) -> tuple[GameWorld, Seed]:
    """Generate a seed, assemble its patch and store it, reusing what already exists.

    `settings` may be a flag string, so a caller holding nothing but a seed and a
    string - a queue worker, say - has one call to make and no conversion of its
    own to get right. Returns the world and its stored row.
    """
    if isinstance(settings, str):
        settings = settings_from_flag_string(settings)
    world = build_world_for(
        seed,
        settings,
        debug_mode=debug_mode,
        debug_bps_patches=debug_bps_patches,
        progress_callback=progress_callback,
    )
    world.get_patch()
    row = save_seed(world, seed, debug_mode=debug_mode, race_mode=race_mode)
    ensure_sprite_render_variants(row, seed, world, debug_mode=debug_mode)
    return world, row


__all__ = [
    "build_world_for",
    "encode_placement",
    "ensure_sprite_render_variants",
    "generate_seed",
    "load_placement_cache",
    "save_seed",
    "settings_from_flag_string",
    "save_sprite_render",
    "load_sprite_render",
]
