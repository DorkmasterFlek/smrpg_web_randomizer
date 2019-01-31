# Boss randomization data for open mode.

from randomizer.logic import utils
from randomizer.logic.patch import Patch


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
    star_address = 0x1e97cc
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
    star_address = 0x1e9a1b


class Boomer(BowsersKeepLocation):
    star_address = 0x1e9a2e


class Exor(BowsersKeepLocation):
    star_address = 0x1e9a41


# ********************* Default lists for the world.

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
