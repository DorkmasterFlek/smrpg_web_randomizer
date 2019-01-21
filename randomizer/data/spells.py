# Data module for spell data.

from randomizer.logic import utils
from randomizer.logic.patch import Patch

STARTING_FP = 10


class Spell:
    """Class representing a magic spell to be randomized."""
    BASE_ADDRESS = 0x3a20f1

    # Default per-spell attributes.
    index = 0
    fp = 0
    power = 0
    hit_rate = 0
    instant_ko = False

    def __init__(self, world):
        """

        Args:
            world (randomizer.logic.main.GameWorld):

        """
        self.world = world

    def __str__(self):
        return "<{}>".format(self.name)

    def __repr__(self):
        return str(self)

    @property
    def name(self):
        return self.__class__.__name__

    def get_patch(self):
        """Get patch for this spell.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # FP is byte 3, power is byte 6, hit rate is byte 7.  Each spell is 12 bytes.
        base_addr = self.BASE_ADDRESS + (self.index * 12)
        patch.add_data(base_addr + 2, utils.ByteField(self.fp).as_bytes())
        data = utils.ByteField(self.power).as_bytes()
        data += utils.ByteField(self.hit_rate).as_bytes()
        patch.add_data(base_addr + 5, data)

        return patch


# ********************* Actual data classes

class Jump(Spell):
    index = 0
    fp = 3
    power = 25
    hit_rate = 100


class FireOrb(Spell):
    index = 1
    fp = 5
    power = 20
    hit_rate = 100


class SuperJump(Spell):
    index = 2
    fp = 7
    power = 45
    hit_rate = 100


class SuperFlame(Spell):
    index = 3
    fp = 9
    power = 40
    hit_rate = 100


class UltraJump(Spell):
    index = 4
    fp = 11
    power = 65
    hit_rate = 100


class UltraFlame(Spell):
    index = 5
    fp = 14
    power = 60
    hit_rate = 100


class Therapy(Spell):
    index = 6
    fp = 2
    power = 40
    hit_rate = 100


class GroupHug(Spell):
    index = 7
    fp = 4
    power = 30
    hit_rate = 100


class SleepyTime(Spell):
    index = 8
    fp = 4
    hit_rate = 99


class ComeBack(Spell):
    index = 9
    fp = 2
    hit_rate = 100


class Mute(Spell):
    index = 10
    fp = 3
    hit_rate = 99


class PsychBomb(Spell):
    index = 11
    fp = 15
    power = 60
    hit_rate = 100


class Terrorize(Spell):
    index = 12
    fp = 6
    power = 10
    hit_rate = 90


class PoisonGas(Spell):
    index = 13
    fp = 10
    power = 20
    hit_rate = 90


class Crusher(Spell):
    index = 14
    fp = 12
    power = 60
    hit_rate = 100


class BowserCrush(Spell):
    index = 15
    fp = 16
    power = 58
    hit_rate = 100


class GenoBeam(Spell):
    index = 16
    fp = 3
    power = 40
    hit_rate = 100


class GenoBoost(Spell):
    index = 17
    fp = 4
    hit_rate = 100


class GenoWhirl(Spell):
    index = 18
    fp = 8
    power = 45
    hit_rate = 100


class GenoBlast(Spell):
    index = 19
    fp = 12
    power = 50
    hit_rate = 100


class GenoFlash(Spell):
    index = 20
    fp = 16
    power = 60
    hit_rate = 100


class Thunderbolt(Spell):
    index = 21
    fp = 2
    power = 15
    hit_rate = 100


class HPRain(Spell):
    index = 22
    fp = 2
    power = 10
    hit_rate = 100


class Psychopath(Spell):
    index = 23
    fp = 1
    hit_rate = 100


class Shocker(Spell):
    index = 24
    fp = 8
    power = 60
    hit_rate = 100


class Snowy(Spell):
    index = 25
    fp = 12
    power = 40
    hit_rate = 100


class StarRain(Spell):
    index = 26
    fp = 14
    power = 55
    hit_rate = 100


class Drain(Spell):
    index = 64
    fp = 1
    power = 4
    hit_rate = 90


class LightningOrb(Spell):
    index = 65
    fp = 2
    power = 8
    hit_rate = 90


class Flame(Spell):
    index = 66
    fp = 3
    power = 12
    hit_rate = 90


class Bolt(Spell):
    index = 67
    fp = 4
    power = 20
    hit_rate = 90


class Crystal(Spell):
    index = 68
    fp = 5
    power = 25
    hit_rate = 90


class FlameStone(Spell):
    index = 69
    fp = 6
    power = 32
    hit_rate = 90


class MegaDrain(Spell):
    index = 70
    fp = 7
    power = 40
    hit_rate = 90


class WillyWisp(Spell):
    index = 71
    fp = 8
    power = 48
    hit_rate = 90


class DiamondSaw(Spell):
    index = 72
    fp = 9
    power = 60
    hit_rate = 90


class Electroshock(Spell):
    index = 73
    fp = 10
    power = 72
    hit_rate = 90


class Blast(Spell):
    index = 74
    fp = 11
    power = 89
    hit_rate = 90


class Storm(Spell):
    index = 75
    fp = 12
    power = 108
    hit_rate = 90


class IceRock(Spell):
    index = 76
    fp = 13
    power = 130
    hit_rate = 90


class Escape(Spell):
    index = 77
    hit_rate = 100


class DarkStar(Spell):
    index = 78
    fp = 20
    power = 160
    hit_rate = 90


class Recover(Spell):
    index = 79
    fp = 3
    power = 50
    hit_rate = 100


class MegaRecover(Spell):
    index = 80
    fp = 9
    power = 200
    hit_rate = 100


class FlameWall(Spell):
    index = 81
    fp = 2
    power = 8
    hit_rate = 90


class StaticE(Spell):
    index = 82
    fp = 4
    power = 12
    hit_rate = 90


class SandStorm(Spell):
    index = 83
    fp = 6
    power = 16
    hit_rate = 90


class Blizzard(Spell):
    index = 84
    fp = 8
    power = 22
    hit_rate = 90


class DrainBeam(Spell):
    index = 85
    fp = 10
    power = 26
    hit_rate = 90


class MeteorBlast(Spell):
    index = 86
    fp = 12
    power = 30
    hit_rate = 90


class LightBeam(Spell):
    index = 87
    fp = 13
    power = 34
    hit_rate = 90


class WaterBlast(Spell):
    index = 88
    fp = 14
    power = 39
    hit_rate = 90


class Solidify(Spell):
    index = 89
    fp = 15
    power = 47
    hit_rate = 90


class PetalBlast(Spell):
    index = 90
    fp = 16
    power = 40
    hit_rate = 85


class AuroraFlash(Spell):
    index = 91
    fp = 17
    power = 50
    hit_rate = 85


class Boulder(Spell):
    index = 92
    fp = 18
    power = 72
    hit_rate = 90


class Corona(Spell):
    index = 93
    fp = 19
    power = 88
    hit_rate = 90


class MeteorSwarm(Spell):
    index = 94
    fp = 20
    power = 100
    hit_rate = 90


class KnockOut(Spell):
    index = 95
    fp = 15
    power = 1
    hit_rate = 60
    instant_ko = True


class WeirdMushroom(Spell):
    index = 96
    power = 30
    hit_rate = 100


class BreakerBeam(Spell):
    index = 97
    fp = 15
    power = 80
    hit_rate = 90


class Shredder(Spell):
    index = 98
    fp = 8
    hit_rate = 100


class Sledge(Spell):
    index = 99
    fp = 6
    power = 50
    hit_rate = 99


class SwordRain(Spell):
    index = 100
    fp = 8
    power = 80
    hit_rate = 99


class SpearRain(Spell):
    index = 101
    fp = 5
    power = 60
    hit_rate = 99


class ArrowRain(Spell):
    index = 102
    fp = 2
    power = 40
    hit_rate = 99


class BigBang(Spell):
    index = 103
    power = 100
    hit_rate = 100


class ChainSaw(Spell):
    index = 108
    power = 50
    hit_rate = 90


# ********************* Default lists for the world.

def get_default_spells(world):
    """Get default vanilla item list for the world.

    Args:
        world (randomizer.logic.main.GameWorld):

    Returns:
        list[Spell]: List of default spell objects.

    """
    return [
        Jump(world),
        FireOrb(world),
        SuperJump(world),
        SuperFlame(world),
        UltraJump(world),
        UltraFlame(world),
        Therapy(world),
        GroupHug(world),
        SleepyTime(world),
        ComeBack(world),
        Mute(world),
        PsychBomb(world),
        Terrorize(world),
        PoisonGas(world),
        Crusher(world),
        BowserCrush(world),
        GenoBeam(world),
        GenoBoost(world),
        GenoWhirl(world),
        GenoBlast(world),
        GenoFlash(world),
        Thunderbolt(world),
        HPRain(world),
        Psychopath(world),
        Shocker(world),
        Snowy(world),
        StarRain(world),
        Drain(world),
        LightningOrb(world),
        Flame(world),
        Bolt(world),
        Crystal(world),
        FlameStone(world),
        MegaDrain(world),
        WillyWisp(world),
        DiamondSaw(world),
        Electroshock(world),
        Blast(world),
        Storm(world),
        IceRock(world),
        Escape(world),
        DarkStar(world),
        Recover(world),
        MegaRecover(world),
        FlameWall(world),
        StaticE(world),
        SandStorm(world),
        Blizzard(world),
        DrainBeam(world),
        MeteorBlast(world),
        LightBeam(world),
        WaterBlast(world),
        Solidify(world),
        PetalBlast(world),
        AuroraFlash(world),
        Boulder(world),
        Corona(world),
        MeteorSwarm(world),
        KnockOut(world),
        WeirdMushroom(world),
        BreakerBeam(world),
        Shredder(world),
        Sledge(world),
        SwordRain(world),
        SpearRain(world),
        ArrowRain(world),
        BigBang(world),
        ChainSaw(world),
    ]
