from __future__ import annotations

import hashlib
import random
import time

from django.core.management.base import BaseCommand, CommandError

from randomizer.main import VERSION, create
from randomizer.types.flag_categories import PRESETS
from randomizer.types.settings import Settings


def _patch_map(world) -> dict[int, bytes]:
    return {int(a): bytes(b) for a, b in world.get_patch()._data.items()}


class Command(BaseCommand):
    help = "Check that a cached placement replays to a byte-identical ROM patch."

    def add_arguments(self, parser):
        parser.add_argument("--flags", default="", help="Flag string to generate with.")
        parser.add_argument(
            "--preset", default=None, help="Use a named preset's flags instead."
        )
        parser.add_argument(
            "--seed", type=int, default=None, help="Seed (default: random)."
        )
        parser.add_argument(
            "--runs", type=int, default=1, help="How many seeds to check."
        )

    def handle(self, *args, **options):
        flags = options["flags"]
        if options["preset"]:
            match = next(
                (p for p in PRESETS if p.__name__ == options["preset"]), None
            )
            if match is None:
                raise CommandError(
                    f"unknown preset {options['preset']!r}; "
                    f"available: {', '.join(p.__name__ for p in PRESETS)}"
                )
            flags = match().flags

        failures = 0
        for run in range(options["runs"]):
            seed = options["seed"]
            if seed is None:
                seed = random.SystemRandom().getrandbits(32)
            elif run:
                seed += run
            failures += self._check_one(seed, flags)

        if failures:
            raise CommandError(f"{failures} seed(s) did not replay identically")
        self.stdout.write(self.style.SUCCESS("placement cache replays identically"))

    def _check_one(self, seed: int, flags: str) -> int:
        settings = Settings()
        settings.set_from_flag_string(flags.strip())

        t0 = time.perf_counter()
        cold = create(seed, settings)
        cold_patch = _patch_map(cold)
        cold_time = time.perf_counter() - t0

        # apply_cosmetic_settings reseeds from os.urandom on purpose, so some of
        # the ROM is meant to differ between any two generations - Star Hill
        # wishes, the Marrymore boss names, and the sprite repacking that follows
        # them. Generate a second time to learn which addresses those are rather
        # than carrying a hand-maintained list that would rot as cosmetics change.
        baseline_settings = Settings()
        baseline_settings.set_from_flag_string(flags.strip())
        baseline_patch = _patch_map(create(seed, baseline_settings))
        # Assert only on addresses the two cold runs agree on. Anything else -
        # a differing value, or a chunk boundary that moved because the dialog
        # above it changed length - is downstream of that deliberate randomness
        # and carries no information about the cache.
        stable = {
            a for a in set(cold_patch) & set(baseline_patch)
            if cold_patch[a] == baseline_patch[a]
        }

        blob = cold.placement_result
        if not blob:
            raise CommandError(f"seed {seed} produced no placement blob")

        # A second Settings built from the same string, so the replay cannot
        # accidentally inherit state the first generation left on the object.
        replay_settings = Settings()
        replay_settings.set_from_flag_string(flags.strip())
        t0 = time.perf_counter()
        warm = create(seed, replay_settings, placement_cache=blob)
        warm_patch = _patch_map(warm)
        warm_time = time.perf_counter() - t0

        self.stdout.write(
            f"seed {seed}  cold {cold_time:5.1f}s  replay {warm_time:5.1f}s  "
            f"blob {len(blob)} B  ({len(stable)} stable addrs compared)"
        )

        if cold.hash != warm.hash:
            self.stdout.write(
                self.style.ERROR(
                    f"  seed hash differs: {cold.hash} vs {warm.hash}"
                )
            )
            return 1

        missing = sorted(a for a in stable if a not in warm_patch)
        differing = sorted(
            a for a in stable if a in warm_patch and warm_patch[a] != cold_patch[a]
        )
        if not (missing or differing):
            return 0

        self.stdout.write(
            self.style.ERROR(
                f"  MISMATCH: {len(differing)} stable addresses differ, "
                f"{len(missing)} absent from the replay"
            )
        )
        for addr in (differing + missing)[:8]:
            self.stdout.write(f"    0x{addr:06X}")
        self.stdout.write(
            "  Something the placement search decided is neither stored in the "
            "blob nor re-derived after it. See logic/rom/shuffler_cache.py."
        )
        return 1
