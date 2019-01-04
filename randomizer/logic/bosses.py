# Boss randomization logic for open mode.

import random

from . import utils
from .patch import Patch


class BossLocation:
    """Class representing a boss location."""
    star_address = 0x0
    has_star = False

    @property
    def name(self):
        return self.__class__.__name__

    def get_patch(self):
        """

        Returns:
            randomizer.logic.patch.Patch: Patch data

        """
        patch = Patch()

        # Zero for no star, or 255 if this boss has a star.
        val = 0xff if self.has_star else 0x00
        patch.add_data(self.star_address, utils.ByteField(val).as_bytes())

        return patch


class BowsersKeepLocation(BossLocation):
    """Container subclass for Bowser's Keep locations."""
    pass


# ****************************** Actual location classes
class HammerBros(BossLocation):
    star_address = 0x1e94ce


class Croco1(BossLocation):
    star_address = 0x1e94fa


class Mack(BossLocation):
    star_address = 0x1e9951
    has_star = True


class Pandorite(BossLocation):
    star_address = 0x1e9517


class Belome1(BossLocation):
    star_address = 0x1e952a


class Bowyer(BossLocation):
    star_address = 0x1e953d
    has_star = True


class Croco2(BossLocation):
    star_address = 0x1e95bd


class Punchinello(BossLocation):
    star_address = 0x1e96d9
    has_star = True


class Booster(BossLocation):
    star_address = 0x1e96ec


class ClownBros(BossLocation):
    star_address = 0x1e9714


class Bundt(BossLocation):
    star_address = 0x1e9727


class StarHill(BossLocation):
    star_address = 0x1e973a
    has_star = True


class KingCalamari(BossLocation):
    star_address = 0x1e9773


class Hidon(BossLocation):
    star_address = 0x1e97a6


class Johnny(BossLocation):
    star_address = 0x1e97b9


class Yaridovich(BossLocation):
    star_address = 0x1e97c8
    has_star = True


class Belome2(BossLocation):
    star_address = 0x1e9813


class Jagger(BossLocation):
    star_address = 0x1e99e2


class Jinx(BossLocation):
    star_address = 0x1e9834


class Culex(BossLocation):
    star_address = 0x1e98c9


class BoxBoy(BossLocation):
    star_address = 0x1e99cd


class MegaSmilax(BossLocation):
    star_address = 0x1e98dc


class Birdo(BossLocation):
    star_address = 0x1e9902


class Valentina(BossLocation):
    star_address = 0x1e9915


class CzarDragon(BossLocation):
    star_address = 0x1e9928


class AxemRangers(BossLocation):
    star_address = 0x1e993b
    has_star = True


class Magikoopa(BowsersKeepLocation):
    star_address = 0x1e9cea


class Boomer(BowsersKeepLocation):
    star_address = 0x1e9cfd


class Exor(BowsersKeepLocation):
    star_address = 0x1e9d010


def get_default_boss_locations():
    """Get default boss locations.

    Returns:
        list[BossLocation]: List of default boss locations.

    """
    return [
        HammerBros(),
        Croco1(),
        Mack(),
        Pandorite(),
        Belome1(),
        Bowyer(),
        Croco2(),
        Punchinello(),
        Booster(),
        ClownBros(),
        Bundt(),
        StarHill(),
        KingCalamari(),
        Hidon(),
        Johnny(),
        Yaridovich(),
        Belome2(),
        Jagger(),
        Jinx(),
        Culex(),
        BoxBoy(),
        MegaSmilax(),
        Birdo(),
        Valentina(),
        CzarDragon(),
        AxemRangers(),
        Magikoopa(),
        Boomer(),
        Exor(),
    ]


def _boss_location_filter(world, location):
    """Filter function for boss locations based on whether Culex and/or Bowser's Keep is included.

    Args:
        world (randomizer.logic.main.GameWorld):
        location (BossLocation):

    Returns:
        bool:
    """
    if isinstance(location, Culex) and world.settings.randomize_stars < 2:
        return False
    if isinstance(location, BowsersKeepLocation) and not world.settings.randomize_stars_bk:
        return False
    return True


def randomize_bosses(world):
    """

    Args:
        world (randomizer.logic.main.GameWorld): Game world to randomize.

    """
    # Open mode-specific shuffles.
    if world.open_mode:
        # Shuffle boss star locations.
        if world.settings.randomize_stars:
            for boss in world.boss_locations:
                boss.has_star = False

            possible_stars = [b for b in world.boss_locations if _boss_location_filter(world, b)]

            # Check if we're doing 6 or 7 stars.
            num_stars = 7 if world.settings.randomize_stars_seven else 6
            star_bosses = random.sample(possible_stars, num_stars)
            for boss in star_bosses:
                boss.has_star = True
