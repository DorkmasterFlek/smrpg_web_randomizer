# Boss/star piece randomization data for open mode.

from enum import IntEnum

from randomizer.logic import utils
from randomizer.logic.patch import Patch


class Battlefields(IntEnum):
    """Enumeration for ID values for battlefields."""
    Bowyer = 0x01
    KingCalamari = 0x03
    SunkenShip = 0x04
    MolevilleMines = 0x05
    BowsersKeep = 0x07
    CzarDragon = 0x08
    MushroomWay = 0x09
    BoosterTower = 0x0c
    MushroomKingdomThroneRoom = 0x0f
    Exor = 0x10
    ClownBros = 0x11
    Countdown = 0x12
    Gate = 0x13
    KeroSewers = 0x15
    NimbusCastle = 0x16
    Birdo = 0x17
    Valentina = 0x18
    Boomer = 0x1d
    Bundt = 0x23
    Yaridovich = 0x25
    AxemRangers = 0x27
    CloakerDomino = 0x28
    BeanValley = 0x29
    BelomeTemple = 0x2a
    JinxDojo = 0x2e
    Culex = 0x2f
    Factory = 0x30


class BattleMusic(IntEnum):
    """Enumeration for ID values for battle music."""
    Normal = 0x01
    Boss1 = 0x04
    Boss2 = 0x08
    Smithy = 0x0c
    Culex = 0x1c


class StarLocation:
    """Class representing a star location."""

    # Star piece data
    star_address = 0x0
    has_star = False

    def __init__(self, world):
        """

        Args:
            world (randomizer.logic.main.GameWorld):

        """
        self.world = world

    def __str__(self):
        return "<{}: has_star {}>".format(self.name, self.has_star)

    def __repr__(self):
        return str(self)

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


class BossLocation:
    """Class for boss fight locations."""

    # Boss fight data
    battle_address = 0x0
    pack_number = 0
    battlefield = None
    can_run_away = False
    music = BattleMusic.Normal

    def __init__(self, world):
        """

        Args:
            world (randomizer.logic.main.GameWorld):

        """
        self.world = world

        # Get actual pack object based on the pack number.
        self.pack = self.world.get_formation_pack_by_index(self.pack_number)

    def __str__(self):
        return "<{}: members {}>".format(self.name, [m.enemy for m in self.formation.members])

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def formation(self):
        """Pack should be all the same formation for bosses, so get the object from the first item.

        Returns:
            randomizer.data.formations.EnemyFormation: Formation for this location.

        """
        return self.pack.formations[0]

    def get_patch(self):
        """

        Returns:
            randomizer.logic.patch.Patch: Patch data

        """
        patch = Patch()

        # Add boss data.
        data = bytearray()
        data += utils.ByteField(0x4a).as_bytes()
        data += utils.ByteField(self.pack.index).as_bytes()
        data += utils.ByteField(0x00).as_bytes()

        # If boss formation requires a specific battlefield, use that.  Otherwise use the location battlefield.
        if self.formation.required_battlefield is not None:
            data += utils.ByteField(self.formation.required_battlefield).as_bytes()
        else:
            data += utils.ByteField(self.battlefield).as_bytes()

        # Check for list of addresses if spot has multiple addresses that need to be set.
        if isinstance(self.battle_address, (list, tuple)):
            addrs = self.battle_address
        else:
            addrs = [self.battle_address]

        for addr in addrs:
            patch.add_data(addr, data)

        return patch


class BossAndStarLocation(StarLocation, BossLocation):
    """Subclass for star piece locations that are also boss fights."""

    def __init__(self, world):
        """

        Args:
            world (randomizer.logic.main.GameWorld):

        """
        StarLocation.__init__(self, world)
        BossLocation.__init__(self, world)

    def __str__(self):
        return "<{}: has_star {}, members {}>".format(
            self.name, self.has_star, [m.enemy for m in self.formation.members])

    def __repr__(self):
        return str(self)

    def get_patch(self):
        """

        Returns:
            randomizer.logic.patch.Patch: Patch data

        """
        patch = StarLocation.get_patch(self)
        patch += BossLocation.get_patch(self)
        return patch


class BowsersKeepLocation(BossAndStarLocation):
    """Container subclass for Bowser's Keep locations."""
    pass


# ****************************** Actual location classes
class HammerBros(BossAndStarLocation):
    star_address = 0x1e94ce
    battle_address = 0x1ffd56
    pack_number = 183
    battlefield = Battlefields.MushroomWay
    music = BattleMusic.Boss1


class Croco1(BossAndStarLocation):
    star_address = 0x1e94fa
    battle_address = 0x1f3a54
    pack_number = 163
    battlefield = Battlefields.MushroomWay
    music = BattleMusic.Boss1


class Mack(BossAndStarLocation):
    star_address = 0x1e9951
    has_star = True
    battle_address = 0x1e2d35
    pack_number = 179
    battlefield = Battlefields.MushroomKingdomThroneRoom
    music = BattleMusic.Boss2


class Pandorite(BossAndStarLocation):
    star_address = 0x1e9517
    battle_address = 0x200a30
    pack_number = 156
    battlefield = Battlefields.KeroSewers


class Belome1(BossAndStarLocation):
    star_address = 0x1e952a
    battle_address = 0x200d80
    pack_number = 168
    battlefield = Battlefields.KeroSewers
    music = BattleMusic.Boss1


class Bowyer(BossAndStarLocation):
    star_address = 0x1e953d
    has_star = True
    battle_address = 0x1fc4f3
    pack_number = 181
    battlefield = Battlefields.Bowyer
    music = BattleMusic.Boss2


class Croco2(BossAndStarLocation):
    star_address = 0x1e95bd
    battle_address = 0x1e9554
    pack_number = 164
    battlefield = Battlefields.MolevilleMines
    music = BattleMusic.Boss1


class Punchinello(BossAndStarLocation):
    star_address = 0x1e96d9
    has_star = True
    battle_address = 0x1e693c
    pack_number = 140
    battlefield = Battlefields.MolevilleMines
    music = BattleMusic.Boss1


class Booster(BossAndStarLocation):
    star_address = 0x1e96ec
    battle_address = [0x1ef4e8, 0x20d7f5]
    pack_number = 161
    battlefield = Battlefields.BoosterTower
    music = BattleMusic.Boss1


class ClownBros(BossAndStarLocation):
    star_address = 0x1e9714
    battle_address = 0x1ee82c
    pack_number = 177
    battlefield = Battlefields.ClownBros
    music = BattleMusic.Boss1


class Bundt(BossAndStarLocation):
    star_address = 0x1e9727
    battle_address = 0x1e8a62
    pack_number = 176
    battlefield = Battlefields.Bundt
    music = BattleMusic.Boss1


class StarHill(StarLocation):
    star_address = 0x1e973a
    has_star = True


class KingCalamari(BossAndStarLocation):
    star_address = 0x1e9773
    battle_address = 0x1e974f
    pack_number = 167
    battlefield = Battlefields.SunkenShip
    music = BattleMusic.Boss1


class Hidon(BossAndStarLocation):
    star_address = 0x1e97a6
    battle_address = 0x200a37
    pack_number = 157
    battlefield = Battlefields.SunkenShip


class Johnny(BossAndStarLocation):
    star_address = 0x1e97b9
    battle_address = 0x20363d
    pack_number = 166
    battlefield = Battlefields.SunkenShip
    music = BattleMusic.Boss1


class Yaridovich(BossAndStarLocation):
    star_address = 0x1e97cc
    has_star = True
    battle_address = 0x1ed255
    pack_number = 180
    battlefield = Battlefields.Yaridovich
    music = BattleMusic.Boss2


class Belome2(BossAndStarLocation):
    star_address = 0x1e9813
    battle_address = 0x1e97dd
    pack_number = 169
    battlefield = Battlefields.BelomeTemple
    music = BattleMusic.Boss1


class Jagger(BossAndStarLocation):
    star_address = 0x1e99e2
    battle_address = 0x1f6ca4
    pack_number = 189
    battlefield = Battlefields.JinxDojo
    can_run_away = True


class Jinx1(BossLocation):
    battle_address = 0x1f6e8f
    pack_number = 178
    battlefield = Battlefields.JinxDojo
    can_run_away = True
    music = BattleMusic.Boss1


class Jinx2(BossLocation):
    battle_address = 0x1f6e96
    pack_number = 187
    battlefield = Battlefields.JinxDojo
    can_run_away = True
    music = BattleMusic.Boss1


class Jinx3(BossAndStarLocation):
    star_address = 0x1e9834
    battle_address = 0x1f6e9d
    pack_number = 188
    battlefield = Battlefields.JinxDojo
    can_run_away = True
    music = BattleMusic.Boss1


class Culex(BossAndStarLocation):
    star_address = 0x1e98c9
    battle_address = 0x1f6fd7
    pack_number = 216
    battlefield = Battlefields.Culex
    music = BattleMusic.Culex


class BoxBoy(BossAndStarLocation):
    star_address = 0x1e99cd
    battle_address = 0x1e999a
    pack_number = 158
    battlefield = Battlefields.KeroSewers


class MegaSmilax(BossAndStarLocation):
    star_address = 0x1e98dc
    battle_address = 0x1fdb4f
    pack_number = 173
    battlefield = Battlefields.BeanValley
    music = BattleMusic.Boss1


class Dodo(BossAndStarLocation):
    star_address = 0x1e98ef
    battle_address = [0x1f7a1b, 0x209405]
    pack_number = 208
    battlefield = Battlefields.NimbusCastle
    music = BattleMusic.Boss1


class Birdo(BossAndStarLocation):
    star_address = 0x1e9902
    battle_address = 0x20a397
    pack_number = 175
    battlefield = Battlefields.Birdo
    music = BattleMusic.Boss1


class Valentina(BossAndStarLocation):
    star_address = 0x1e9915
    battle_address = 0x1ea5dd
    pack_number = 171
    battlefield = Battlefields.Valentina
    music = BattleMusic.Boss1


class CzarDragon(BossAndStarLocation):
    star_address = 0x1e9928
    battle_address = 0x204100
    pack_number = 172
    battlefield = Battlefields.CzarDragon
    music = BattleMusic.Boss1


class AxemRangers(BossAndStarLocation):
    star_address = 0x1e993b
    has_star = True
    battle_address = 0x2046fc
    pack_number = 182
    battlefield = Battlefields.AxemRangers
    music = BattleMusic.Boss2


class Magikoopa(BowsersKeepLocation):
    star_address = 0x1e9a1b
    battle_address = 0x1f8847
    pack_number = 209
    battlefield = Battlefields.BowsersKeep
    music = BattleMusic.Boss1


class Boomer(BowsersKeepLocation):
    star_address = 0x1e9a2e
    battle_address = 0x1f8a3a
    pack_number = 210
    battlefield = Battlefields.Boomer
    music = BattleMusic.Boss1


class Exor(BowsersKeepLocation):
    star_address = 0x1e9a41
    battle_address = 0x1f8a58
    pack_number = 186
    battlefield = Battlefields.BowsersKeep
    music = BattleMusic.Boss2


class Countdown(BossLocation):
    battle_address = 0x1fe11d
    pack_number = 174
    battlefield = Battlefields.Gate
    music = BattleMusic.Boss1


class CloakerDomino(BossLocation):
    battle_address = 0x1f61d9
    pack_number = 184
    battlefield = Battlefields.Gate
    music = BattleMusic.Boss1


class Clerk(BossLocation):
    battle_address = 0x1fe3ec
    pack_number = 146
    battlefield = Battlefields.Factory


class Manager(BossLocation):
    battle_address = 0x1fe819
    pack_number = 147
    battlefield = Battlefields.Factory


class Director(BossLocation):
    battle_address = 0x1fea21
    pack_number = 148
    battlefield = Battlefields.Factory


class Gunyolk(BossLocation):
    battle_address = 0x1fe247
    pack_number = 149
    battlefield = Battlefields.Factory
    music = BattleMusic.Boss1


# ********************* Default lists for the world.

def get_default_boss_locations(world):
    """Get default boss locations.

    Args:
        world (randomizer.logic.main.GameWorld):

    Returns:
        list[BossAndStarLocation]: List of default boss locations.

    """
    return [
        HammerBros(world),
        Croco1(world),
        Mack(world),
        Pandorite(world),
        Belome1(world),
        Bowyer(world),
        Croco2(world),
        Punchinello(world),
        Booster(world),
        ClownBros(world),
        Bundt(world),
        StarHill(world),
        KingCalamari(world),
        Hidon(world),
        Johnny(world),
        Yaridovich(world),
        Belome2(world),
        Jagger(world),
        Jinx1(world),
        Jinx2(world),
        Jinx3(world),
        Culex(world),
        BoxBoy(world),
        MegaSmilax(world),
        Dodo(world),
        Birdo(world),
        Valentina(world),
        CzarDragon(world),
        AxemRangers(world),
        Magikoopa(world),
        Boomer(world),
        Exor(world),
        Countdown(world),
        CloakerDomino(world),
        Clerk(world),
        Manager(world),
        Director(world),
        Gunyolk(world),
    ]
