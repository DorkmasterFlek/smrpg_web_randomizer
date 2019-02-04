# Boss randomization logic for open mode.

import random

from randomizer.data import bosses
from . import flags


def _boss_star_piece_filter(world, location):
    """Filter function for boss location star piece shuffle based on whether Culex and/or Bowser's Keep is included.

    Args:
        world (randomizer.logic.main.GameWorld):
        location (randomizer.data.bosses.StarLocation):

    Returns:
        bool: True is location is okay to be included, False otherwise.

    """
    if not isinstance(location, bosses.StarLocation):
        return False
    if isinstance(location, bosses.Culex) and not world.settings.is_flag_enabled(flags.CulexStarShuffle):
        return False
    if isinstance(location, bosses.BowsersKeepLocation) and not world.settings.is_flag_enabled(flags.BowsersKeepOpen):
        return False
    return True


def _boss_fight_filter(world, location):
    """

    Args:
        world (randomizer.logic.main.GameWorld):
        location (randomizer.data.bosses.BossLocation):

    Returns:
        bool: True is location is okay to be included, False otherwise.

    """
    if not isinstance(location, bosses.BossLocation):
        return False
    if isinstance(location, bosses.Culex) and not world.settings.is_flag_enabled(flags.BossShuffleCulex):
        return False
    return True


def randomize_all(world):
    """Randomize all the boss settings for the world.

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Shuffle boss star locations.
        if world.settings.is_flag_enabled(flags.StarPieceShuffle):
            for boss in world.boss_locations:
                boss.has_star = False

            possible_stars = [b for b in world.boss_locations if _boss_star_piece_filter(world, b)]

            # Check if we're doing 6 or 7 stars.
            num_stars = 7 if world.settings.is_flag_enabled(flags.SevenStarHunt) else 6
            star_bosses = random.sample(possible_stars, num_stars)
            for boss in star_bosses:
                boss.has_star = True

        # Shuffle boss encounters.
        if world.settings.is_flag_enabled(flags.BossShuffle):
            locations_to_shuffle = [b for b in world.boss_locations if _boss_fight_filter(world, b)]
            shuffled_packs = [b.pack for b in locations_to_shuffle]
            random.shuffle(shuffled_packs)

            # TODO: Scale boss stats accordingly if keep stats not enabled.
            if not world.settings.is_flag_enabled(flags.BossShuffleKeepStats):
                pass

            # Assign packs to their new locations and update music and can't run flags.
            for location, pack in zip(locations_to_shuffle, shuffled_packs):
                location.pack = pack
                location.formation.music = location.music
                location.formation.can_run_away = location.can_run_away
