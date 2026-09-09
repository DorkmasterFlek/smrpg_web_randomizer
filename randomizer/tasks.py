import logging

from django.core.cache import cache
from django.db import transaction
from django.tasks import task, TaskContext

from randomizer.models import Patch

logger = logging.getLogger(__name__)


@task(takes_context=True, queue_name='seeds')
def generate_seed_task(
        context: TaskContext,
        seed: int | str,
        flags: str,
        debug_flags: dict,
):
    """Generate a seed and/or patch using the background process.

    A stored blob that no longer applies - written against different flags, or by
    a build with different location/prize classes - is not fatal. It is reported
    and the seed is generated from scratch, which is what would have happened
    before any of it was cached.
    """
    import hashlib
    import json
    import pickle
    from randomizer.logic.generate import generate_seed
    from randomizer.types.patch import PatchJSONEncoder
    from randomizer.types.settings import Settings

    logger.info(f"Seed {seed} starting generation")

    def progress_callback(
            message: str,
            percent: int,
    ) -> None:
        """Callback function to update message and percent as progress is done."""
        logger.info(f"Seed {seed}: Progress {percent}% - {message}")
        cache_key = f'task-status-{context.task_result.id}'
        payload = {
            'message': message,
            'percent': percent,
        }
        cache.set(cache_key, payload)

    settings = Settings()
    settings.set_from_flag_string(flags)
    settings.debug_mode = bool(debug_flags)
    settings.prize_offset = debug_flags.get('prize_offset')
    settings.mimic_offset = debug_flags.get('mimic_offset')
    settings.offset_slots = debug_flags.get('offset_slots', False)
    settings.offset_mimics = debug_flags.get('offset_mimics', False)
    settings.offset_coins = debug_flags.get('offset_coins', False)
    settings.offset_star_pieces = debug_flags.get('offset_star_pieces', False)
    settings.offset_invisible_flags = debug_flags.get('offset_invisible_flags', False)

    # Generate game world.
    world, seed_obj = generate_seed(seed, settings, debug_mode=settings.debug_mode,
                                    debug_bps_patches=debug_flags.get('debug_bps_patches', False),
                                    progress_callback=progress_callback)

    # Get patch (should be cached now).
    rom_patch = world.get_patch()

    with transaction.atomic():
        patch_dump = pickle.dumps(json.loads(json.dumps(rom_patch, cls=PatchJSONEncoder)),
                                  protocol=pickle.HIGHEST_PROTOCOL)
        h = hashlib.sha256()
        h.update(patch_dump)

        patch = Patch.objects.create(
            seed=seed_obj,
            hash=h.hexdigest(),
            patch=patch_dump,
        )
        logger.info(f"Patch {patch.id} for seed {seed} finished generation")

    return str(patch.id)
