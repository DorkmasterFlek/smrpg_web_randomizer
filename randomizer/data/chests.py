# Data module for chest data.

from randomizer.data import items
from randomizer.logic.utils import isclass_or_instance
from .locations import Area, ItemLocation


# ******* Chest location classes

class Chest(ItemLocation):
    """Subclass for treasure chest location."""
    access = 0
    ms_override = False


class NonCoinChest(Chest):
    """Subclass for chest that cannot contain coin items."""

    def item_allowed(self, item):
        """

        Args:
            item(randomizer.data.items.Item|type): Item to check.

        Returns:
            bool: True if the given item is allowed to be placed in this spot, False otherwise.

        """
        return super().item_allowed(item) and not isclass_or_instance(item, items.Coins)


class StarAllowedChest(Chest):
    """Subclass for chests that are in the same room as an invincibility star."""

    def item_allowed(self, item):
        """

        Args:
            item(randomizer.data.items.Item|type): Item to check.

        Returns:
            bool: True if the given item is allowed to be placed in this spot, False otherwise.

        """
        return super().item_allowed(item) or isclass_or_instance(item, items.InvincibilityStar)


class RoseTownGardenerChest(Chest):
    """Subclass for the Lazy Shell chests in Rose Town."""


class BowserDoorReward(Chest):
    """Subclass for Bowser door rewards because they can only be inventory items or you missed."""

    def item_allowed(self, item):
        """

        Args:
            item(randomizer.data.items.Item|type): Item to check.

        Returns:
            bool: True if the given item is allowed to be placed in this spot, False otherwise.

        """
        return super().item_allowed(item) and (not isclass_or_instance(item, items.ChestReward) or
                                               isclass_or_instance(item, items.YouMissed))


# ****************************** Actual chest classes

# *** Mushroom Way

class MushroomWay1(Chest):
    area = Area.MushroomWay
    addresses = [0x14b389]
    item = items.Coins5
    access = 1


class MushroomWay2(Chest):
    area = Area.MushroomWay
    addresses = [0x14b38d]
    item = items.Coins8
    access = 1


class MushroomWay3(Chest):
    area = Area.MushroomWay
    addresses = [0x14b3da]
    item = items.Flower
    access = 1


class MushroomWay4(Chest):
    area = Area.MushroomWay
    addresses = [0x14b3de]
    item = items.RecoveryMushroom
    access = 1


# *** Mushroom Kingdom

class MushroomKingdomVault1(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148ad3]
    item = items.Coins10
    access = 1


class MushroomKingdomVault2(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148adf]
    item = items.RecoveryMushroom
    access = 1


class MushroomKingdomVault3(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148aeb]
    item = items.Flower
    access = 1


# *** Bandit's Way

class BanditsWay1(Chest):
    area = Area.BanditsWay
    addresses = [0x14b535]
    item = items.KerokeroCola
    access = 1


class BanditsWay2(Chest):
    area = Area.BanditsWay
    addresses = [0x1495ff]
    item = items.RecoveryMushroom
    access = 1


class BanditsWayStarChest(StarAllowedChest):
    area = Area.BanditsWay
    addresses = [0x14964c]
    item = items.BanditsWayStar
    access = 1


class BanditsWayDogJump(StarAllowedChest):
    area = Area.BanditsWay
    addresses = [0x149650]
    item = items.Flower
    access = 2


class BanditsWayCroco(Chest):
    area = Area.BanditsWay
    addresses = [0x14b494]
    item = items.RecoveryMushroom
    access = 1


# *** Kero Sewers

class KeroSewersPandoriteRoom(Chest):
    area = Area.KeroSewers
    addresses = [0x149053]
    item = items.Flower
    access = 1


class KeroSewersStarChest(StarAllowedChest):
    area = Area.KeroSewers
    addresses = [0x14901e]
    item = items.KeroSewersStar
    access = 1


# *** Rose Way

class RoseWayPlatform(Chest):
    area = Area.RoseWay
    addresses = [0x14973e]
    item = items.FrogCoin
    access = 2


# *** Rose Town

class RoseTownStore1(Chest):
    area = Area.RoseTown
    addresses = [0x1499ad]
    item = items.Flower
    access = 1


class RoseTownStore2(Chest):
    area = Area.RoseTown
    addresses = [0x1499b9]
    item = items.FrogCoin
    access = 1


class GardenerCloud1(RoseTownGardenerChest):
    area = Area.RoseTownClouds
    addresses = [0x14de24]
    item = items.LazyShellArmor
    access = 4
    ms_override = True


class GardenerCloud2(RoseTownGardenerChest):
    area = Area.RoseTownClouds
    addresses = [0x14de28]
    item = items.LazyShellWeapon
    access = 4
    ms_override = True


# *** Forest Maze

class ForestMaze1(Chest):
    area = Area.ForestMaze
    addresses = [0x14b75e]
    item = items.KerokeroCola
    access = 1


class ForestMaze2(Chest):
    area = Area.ForestMaze
    addresses = [0x14b872]
    item = items.FrogCoin
    access = 1


class ForestMazeUnderground1(Chest):
    area = Area.ForestMaze
    addresses = [0x14bb9d]
    item = items.KerokeroCola
    access = 1


class ForestMazeUnderground2(Chest):
    area = Area.ForestMaze
    addresses = [0x14bba1]
    item = items.Flower
    access = 2


class ForestMazeUnderground3(Chest):
    area = Area.ForestMaze
    addresses = [0x14bba5]
    item = items.YouMissed
    access = 1


class ForestMazeRedEssence(Chest):
    area = Area.ForestMaze
    addresses = [0x14b841]
    item = items.RedEssence
    access = 1


# *** Pipe Vault

class PipeVaultSlide1(Chest):
    area = Area.PipeVault
    addresses = [0x14a2b7]
    item = items.Flower
    access = 1


class PipeVaultSlide2(Chest):
    area = Area.PipeVault
    addresses = [0x14a2c3]
    item = items.FrogCoin
    access = 1


class PipeVaultSlide3(Chest):
    area = Area.PipeVault
    addresses = [0x14a2cf]
    item = items.FrogCoin
    access = 1


class PipeVaultNippers1(Chest):
    area = Area.PipeVault
    addresses = [0x14a33e]
    item = items.Flower
    access = 2


class PipeVaultNippers2(Chest):
    area = Area.PipeVault
    addresses = [0x14a34a]
    item = items.CoinsDoubleBig
    access = 2


# *** Yo'ster Isle

class YosterIsleEntrance(Chest):
    area = Area.YosterIsle
    addresses = [0x148b39]
    item = items.FrogCoin
    access = 2


# *** Moleville

class MolevilleMinesStarChest(StarAllowedChest):
    area = Area.MolevilleMines
    addresses = [0x14c4af]
    item = items.MolevilleMinesStar
    access = 3


class MolevilleMinesCoins(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c3c6]
    item = items.Coins150
    access = 3


class MolevilleMinesPunchinello1(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c546]
    item = items.RecoveryMushroom
    access = 3


class MolevilleMinesPunchinello2(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c552]
    item = items.Flower
    access = 3


# *** Booster Pass

class BoosterPass1(Chest):
    area = Area.BoosterPass
    addresses = [0x149c62]
    item = items.Flower
    access = 2


class BoosterPass2(Chest):
    area = Area.BoosterPass
    addresses = [0x149c6e]
    item = items.RockCandy
    access = 1


class BoosterPassSecret1(Chest):
    area = Area.BoosterPass
    addresses = [0x14da32]
    item = items.FrogCoin
    access = 2


class BoosterPassSecret2(Chest):
    area = Area.BoosterPass
    addresses = [0x14da36]
    item = items.Flower
    access = 2


class BoosterPassSecret3(Chest):
    area = Area.BoosterPass
    addresses = [0x14da42]
    item = items.KerokeroCola
    access = 2


# *** Booster Tower

class BoosterTowerSpookum(Chest):
    area = Area.BoosterTower
    addresses = [0x14b23e]
    item = items.FrogCoin
    access = 1


class BoosterTowerThwomp(Chest):
    area = Area.BoosterTower
    addresses = [0x148c60]
    item = items.RecoveryMushroom
    access = 1


class BoosterTowerParachute(Chest):
    area = Area.BoosterTower
    addresses = [0x148c2f]
    item = items.FrogCoin
    access = 1


class BoosterTowerZoomShoes(Chest):
    area = Area.BoosterTower
    addresses = [0x148eac]
    item = items.ZoomShoes
    access = 3
    ms_override = True


class BoosterTowerTop1(NonCoinChest):
    area = Area.BoosterTower
    addresses = [0x14b2d1]
    item = items.FrogCoin
    access = 2


class BoosterTowerTop2(Chest):
    area = Area.BoosterTower
    addresses = [0x14b2e1]
    item = items.GoodieBag
    access = 2


class BoosterTowerTop3(Chest):
    area = Area.BoosterTower
    addresses = [0x14b325]
    item = items.RecoveryMushroom
    access = 2


# *** Marrymore

class MarrymoreInn(Chest):
    area = Area.Marrymore
    addresses = [0x1485d7]
    item = items.FrogCoin
    access = 1


# *** Sea

class SeaStarChest(StarAllowedChest):
    area = Area.Sea
    addresses = [0x14a458]
    item = items.SeaStar
    access = 1


class SeaSaveRoom1(Chest):
    area = Area.Sea
    addresses = [0x14a40e]
    item = items.FrogCoin
    access = 1


class SeaSaveRoom2(Chest):
    area = Area.Sea
    addresses = [0x14a412]
    item = items.Flower
    access = 1


class SeaSaveRoom3(Chest):
    area = Area.Sea
    addresses = [0x14a416]
    item = items.RecoveryMushroom
    access = 1


class SeaSaveRoom4(Chest):
    area = Area.Sea
    addresses = [0x14a42f]
    item = items.MaxMushroom
    access = 1


# *** Sunken Ship

class SunkenShipRatStairs(Chest):
    area = Area.SunkenShip
    addresses = [0x14ac26]
    item = items.Coins100
    access = 1


class SunkenShipShop(Chest):
    area = Area.SunkenShip
    addresses = [0x14ac70]
    item = items.Coins100
    access = 2


class SunkenShipCoins1(Chest):
    area = Area.SunkenShip
    addresses = [0x14ad85]
    item = items.Coins100
    access = 3


class SunkenShipCoins2(Chest):
    area = Area.SunkenShip
    addresses = [0x14ad89]
    item = items.Coins100
    access = 3


class SunkenShipCloneRoom(Chest):
    area = Area.SunkenShip
    addresses = [0x14ae61]
    item = items.KerokeroCola
    access = 3


class SunkenShipFrogCoinRoom(Chest):
    area = Area.SunkenShip
    addresses = [0x14aef5]
    item = items.FrogCoin
    access = 3


class SunkenShipHidonMushroom(Chest):
    area = Area.SunkenShip
    addresses = [0x14af0e]
    item = items.RecoveryMushroom
    access = 3


class SunkenShipSafetyRing(Chest):
    area = Area.SunkenShip
    addresses = [0x14af27]
    item = items.SafetyRing
    access = 3


class SunkenShipBandanaReds(Chest):
    area = Area.SunkenShip
    addresses = [0x14895d]
    item = items.RecoveryMushroom
    access = 3


# *** Land's End

class LandsEndRedEssence(Chest):
    area = Area.LandsEnd
    addresses = [0x14a4df]
    item = items.RedEssence
    access = 1


class LandsEndChowPit1(Chest):
    area = Area.LandsEnd
    addresses = [0x14a51c]
    item = items.KerokeroCola
    access = 1


class LandsEndChowPit2(Chest):
    area = Area.LandsEnd
    addresses = [0x14a528]
    item = items.FrogCoin
    access = 1


class LandsEndBeeRoom(Chest):
    area = Area.LandsEnd
    addresses = [0x14a5a2]
    item = items.FrogCoin
    access = 1


class LandsEndSecret1(Chest):
    area = Area.LandsEnd
    addresses = [0x14c1f4]
    item = items.FrogCoin
    access = 1


class LandsEndSecret2(Chest):
    area = Area.LandsEnd
    addresses = [0x14c200]
    item = items.FrogCoin
    access = 1


class LandsEndShyAway(Chest):
    area = Area.LandsEnd
    addresses = [0x14d932]
    item = items.RecoveryMushroom
    access = 1


class LandsEndStarChest1(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c069]
    item = items.LandsEndVolcanoStar
    access = 2


class LandsEndStarChest2(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c02c]
    item = items.LandsEndStar2
    access = 2


class LandsEndStarChest3(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c030]
    item = items.LandsEndStar3
    access = 3


# *** Belome Temple

class BelomeTempleFortuneTeller(Chest):
    area = Area.BelomeTemple
    addresses = [0x14de81]
    item = items.Coins50
    access = 2


class BelomeTempleAfterFortune1(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df69]
    item = items.FrogCoin
    access = 2


class BelomeTempleAfterFortune2(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df6d]
    item = items.Coins150
    access = 2


class BelomeTempleAfterFortune3(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df79]
    item = items.FrogCoin
    access = 2


class BelomeTempleAfterFortune4(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df7d]
    item = items.FrogCoin
    access = 2


# *** Monstro Town

class MonstroTownEntrance(Chest):
    area = Area.MonstroTown
    addresses = [0x14c10d]
    item = items.FrogCoin
    access = 1


# *** Bean Valley

class BeanValley1(Chest):
    area = Area.BeanValley
    addresses = [0x14bde3]
    item = items.Flower
    access = 1


class BeanValley2(Chest):
    area = Area.BeanValley
    addresses = [0x14bdef]
    item = items.FrogCoin
    access = 1


class BeanValleyBoxBoyRoom1(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cc58]
    item = items.RedEssence
    access = 2


class BeanValleyBoxBoyRoom2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cc64]
    item = items.FrogCoin
    access = 2


class BeanValleySlotRoom(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cf7e]
    item = items.KerokeroCola
    access = 2


class BeanValleyPiranhaPlants(Chest):
    area = Area.BeanValley
    addresses = [0x14bdb6]
    item = items.FrogCoin
    access = 2


class BeanValleyBeanstalk(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d444]
    item = items.Flower
    access = 3


class BeanValleyCloud1(Chest):
    area = Area.BeanValley
    addresses = [0x14d2f1]
    item = items.FrogCoin
    access = 3


class BeanValleyCloud2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d2fd]
    item = items.RareScarf
    access = 3


class BeanValleyFall1(Chest):
    area = Area.BeanValley
    addresses = [0x14d316]
    item = items.Flower
    access = 3


class BeanValleyFall2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d322]
    item = items.Flower
    access = 3


# *** Nimbus Land

class NimbusLandShop(NonCoinChest):
    area = Area.NimbusLand
    addresses = [0x14ce25]
    item = items.FrogCoin
    access = 1


class NimbusCastleBeforeBirdo1(StarAllowedChest):
    area = Area.NimbusLand
    addresses = [0x14a088]
    item = items.Flower
    missable = True
    access = 1


class NimbusCastleBeforeBirdo2(Chest):
    area = Area.NimbusLand
    addresses = [0x14eda7]
    item = items.FrogCoin
    access = 4


class NimbusCastleOutOfBounds1(NonCoinChest):
    area = Area.NimbusLand
    addresses = [0x14db97]
    item = items.FrogCoin
    access = 2


class NimbusCastleOutOfBounds2(Chest):
    area = Area.NimbusLand
    addresses = [0x14dba3]
    item = items.FrogCoin
    access = 2


class NimbusCastleSingleGoldBird(Chest):
    area = Area.NimbusLand
    addresses = [0x149f47]
    item = items.RecoveryMushroom
    access = 1


class NimbusCastleStarChest(StarAllowedChest):
    area = Area.NimbusLand
    addresses = [0x14a1a3]
    item = items.NimbusLandStar
    missable = True
    access = 4


class NimbusCastleStarAfterValentina(Chest):
    area = Area.NimbusLand
    addresses = [0x14a1af]
    item = items.Flower
    access = 4


# *** Barrel Volcano

class BarrelVolcanoSecret1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d048]
    item = items.Flower
    access = 1


class BarrelVolcanoSecret2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d04c]
    item = items.Flower
    access = 1


class BarrelVolcanoBeforeStar1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d595]
    item = items.Flower
    access = 1


class BarrelVolcanoBeforeStar2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d5a1]
    item = items.Coins100
    access = 1


class BarrelVolcanoStarRoom(StarAllowedChest):
    area = Area.BarrelVolcano
    addresses = [0x14d5ce]
    item = items.LandsEndVolcanoStar
    access = 1


class BarrelVolcanoSaveRoom1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d203]
    item = items.Flower
    access = 2


class BarrelVolcanoSaveRoom2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d207]
    item = items.FrogCoin
    access = 2


class BarrelVolcanoHinnopio(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d220]
    item = items.Coins100
    access = 2


# *** Bowser's Keep

class BowsersKeepDarkRoom(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e3b1]
    item = items.RecoveryMushroom
    access = 1


class BowsersKeepCrocoShop1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e37f]
    item = items.Coins150
    access = 1


class BowsersKeepCrocoShop2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e38b]
    item = items.RecoveryMushroom
    access = 1


class BowsersKeepInvisibleBridge1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9b3]
    item = items.FrightBomb
    access = 2


class BowsersKeepInvisibleBridge2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9b7]
    item = items.RoyalSyrup
    access = 2


class BowsersKeepInvisibleBridge3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9bb]
    item = items.IceBomb
    access = 2


class BowsersKeepInvisibleBridge4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9bf]
    item = items.RockCandy
    access = 2


class BowsersKeepMovingPlatforms1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e536]
    item = items.Flower
    access = 3


class BowsersKeepMovingPlatforms2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e542]
    item = items.RedEssence
    access = 3


class BowsersKeepMovingPlatforms3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e546]
    item = items.MaxMushroom
    access = 3


class BowsersKeepMovingPlatforms4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e54a]
    item = items.FireBomb
    access = 3


class BowsersKeepElevatorPlatforms(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c97a]
    item = items.KerokeroCola
    access = 2


class BowsersKeepCannonballRoom1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4b1]
    item = items.Flower
    access = 2


class BowsersKeepCannonballRoom2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4b5]
    item = items.Flower
    access = 2


class BowsersKeepCannonballRoom3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c1]
    item = items.PickMeUp
    access = 2


class BowsersKeepCannonballRoom4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c5]
    item = items.RockCandy
    access = 2


class BowsersKeepCannonballRoom5(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c9]
    item = items.MaxMushroom
    access = 2


class BowsersKeepRotatingPlatforms1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e3ff]
    item = items.Flower
    access = 3


class BowsersKeepRotatingPlatforms2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e403]
    item = items.Flower
    access = 3


class BowsersKeepRotatingPlatforms3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e40f]
    item = items.FireBomb
    access = 3


class BowsersKeepRotatingPlatforms4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e413]
    item = items.RoyalSyrup
    access = 3


class BowsersKeepRotatingPlatforms5(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e417]
    item = items.PickMeUp
    access = 3


class BowsersKeepRotatingPlatforms6(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e41b]
    item = items.KerokeroCola
    access = 3


class BowsersKeepDoorReward1(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204bfc]
    item = items.SonicCymbal
    access = 2


class BowsersKeepDoorReward2(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c02]
    item = items.SuperSlap
    access = 2


class BowsersKeepDoorReward3(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c08]
    item = items.DrillClaw
    access = 4


class BowsersKeepDoorReward4(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c0e]
    item = items.StarGun
    access = 2


class BowsersKeepDoorReward5(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c14]
    item = items.RockCandy
    access = 2


class BowsersKeepDoorReward6(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c1a]
    item = items.RockCandy
    access = 4


# *** Factory

class FactorySaveRoom(Chest):
    area = Area.Factory
    addresses = [0x14bafa]
    item = items.RecoveryMushroom
    access = 4


class FactoryBoltPlatforms(Chest):
    area = Area.Factory
    addresses = [0x14bb6c]
    item = items.UltraHammer
    access = 4


class FactoryFallingAxems(Chest):
    area = Area.Factory
    addresses = [0x14e0c8]
    item = items.RecoveryMushroom
    access = 4


class FactoryTreasurePit1(Chest):
    area = Area.Factory
    addresses = [0x14e2c4]
    item = items.RecoveryMushroom
    access = 4


class FactoryTreasurePit2(NonCoinChest):
    area = Area.Factory
    addresses = [0x14e2cc]
    item = items.Flower
    access = 4


class FactoryConveyorPlatforms1(Chest):
    area = Area.Factory
    addresses = [0x14e9cb]
    item = items.RoyalSyrup
    access = 4


class FactoryConveyorPlatforms2(Chest):
    area = Area.Factory
    addresses = [0x14e9cf]
    item = items.MaxMushroom
    access = 4


class FactoryBehindSnakes1(Chest):
    area = Area.Factory
    addresses = [0x14e2c8]
    item = items.RecoveryMushroom
    access = 4


class FactoryBehindSnakes2(Chest):
    area = Area.Factory
    addresses = [0x14e2d0]
    item = items.Flower
    access = 4


# ********************* Default objects for world

def get_default_chests(world):
    """Get default vanilla chest list for the world.

    Args:
        world (randomizer.logic.main.GameWorld):

    Returns:
        list[ItemLocation]: List of default chest objects.
    """
    return [
        MushroomWay1(world),
        MushroomWay2(world),
        MushroomWay3(world),
        MushroomWay4(world),
        MushroomKingdomVault1(world),
        MushroomKingdomVault2(world),
        MushroomKingdomVault3(world),
        BanditsWay1(world),
        BanditsWay2(world),
        BanditsWayStarChest(world),
        BanditsWayDogJump(world),
        BanditsWayCroco(world),
        KeroSewersPandoriteRoom(world),
        KeroSewersStarChest(world),
        RoseWayPlatform(world),
        RoseTownStore1(world),
        RoseTownStore2(world),
        GardenerCloud1(world),
        GardenerCloud2(world),
        ForestMaze1(world),
        ForestMaze2(world),
        ForestMazeUnderground1(world),
        ForestMazeUnderground2(world),
        ForestMazeUnderground3(world),
        ForestMazeRedEssence(world),
        PipeVaultSlide1(world),
        PipeVaultSlide2(world),
        PipeVaultSlide3(world),
        PipeVaultNippers1(world),
        PipeVaultNippers2(world),
        YosterIsleEntrance(world),
        MolevilleMinesStarChest(world),
        MolevilleMinesCoins(world),
        MolevilleMinesPunchinello1(world),
        MolevilleMinesPunchinello2(world),
        BoosterPass1(world),
        BoosterPass2(world),
        BoosterPassSecret1(world),
        BoosterPassSecret2(world),
        BoosterPassSecret3(world),
        BoosterTowerSpookum(world),
        BoosterTowerThwomp(world),
        BoosterTowerParachute(world),
        BoosterTowerZoomShoes(world),
        BoosterTowerTop1(world),
        BoosterTowerTop2(world),
        BoosterTowerTop3(world),
        MarrymoreInn(world),
        SeaStarChest(world),
        SeaSaveRoom1(world),
        SeaSaveRoom2(world),
        SeaSaveRoom3(world),
        SeaSaveRoom4(world),
        SunkenShipRatStairs(world),
        SunkenShipShop(world),
        SunkenShipCoins1(world),
        SunkenShipCoins2(world),
        SunkenShipCloneRoom(world),
        SunkenShipFrogCoinRoom(world),
        SunkenShipHidonMushroom(world),
        SunkenShipSafetyRing(world),
        SunkenShipBandanaReds(world),
        LandsEndRedEssence(world),
        LandsEndChowPit1(world),
        LandsEndChowPit2(world),
        LandsEndBeeRoom(world),
        LandsEndSecret1(world),
        LandsEndSecret2(world),
        LandsEndShyAway(world),
        LandsEndStarChest1(world),
        LandsEndStarChest2(world),
        LandsEndStarChest3(world),
        BelomeTempleFortuneTeller(world),
        BelomeTempleAfterFortune1(world),
        BelomeTempleAfterFortune2(world),
        BelomeTempleAfterFortune3(world),
        BelomeTempleAfterFortune4(world),
        MonstroTownEntrance(world),
        BeanValley1(world),
        BeanValley2(world),
        BeanValleyBoxBoyRoom1(world),
        BeanValleyBoxBoyRoom2(world),
        BeanValleySlotRoom(world),
        BeanValleyPiranhaPlants(world),
        BeanValleyBeanstalk(world),
        BeanValleyCloud1(world),
        BeanValleyCloud2(world),
        BeanValleyFall1(world),
        BeanValleyFall2(world),
        NimbusLandShop(world),
        NimbusCastleBeforeBirdo1(world),
        NimbusCastleBeforeBirdo2(world),
        NimbusCastleOutOfBounds1(world),
        NimbusCastleOutOfBounds2(world),
        NimbusCastleSingleGoldBird(world),
        NimbusCastleStarChest(world),
        NimbusCastleStarAfterValentina(world),
        BarrelVolcanoSecret1(world),
        BarrelVolcanoSecret2(world),
        BarrelVolcanoBeforeStar1(world),
        BarrelVolcanoBeforeStar2(world),
        BarrelVolcanoStarRoom(world),
        BarrelVolcanoSaveRoom1(world),
        BarrelVolcanoSaveRoom2(world),
        BarrelVolcanoHinnopio(world),
        BowsersKeepDarkRoom(world),
        BowsersKeepCrocoShop1(world),
        BowsersKeepCrocoShop2(world),
        BowsersKeepInvisibleBridge1(world),
        BowsersKeepInvisibleBridge2(world),
        BowsersKeepInvisibleBridge3(world),
        BowsersKeepInvisibleBridge4(world),
        BowsersKeepMovingPlatforms1(world),
        BowsersKeepMovingPlatforms2(world),
        BowsersKeepMovingPlatforms3(world),
        BowsersKeepMovingPlatforms4(world),
        BowsersKeepElevatorPlatforms(world),
        BowsersKeepCannonballRoom1(world),
        BowsersKeepCannonballRoom2(world),
        BowsersKeepCannonballRoom3(world),
        BowsersKeepCannonballRoom4(world),
        BowsersKeepCannonballRoom5(world),
        BowsersKeepRotatingPlatforms1(world),
        BowsersKeepRotatingPlatforms2(world),
        BowsersKeepRotatingPlatforms3(world),
        BowsersKeepRotatingPlatforms4(world),
        BowsersKeepRotatingPlatforms5(world),
        BowsersKeepRotatingPlatforms6(world),
        BowsersKeepDoorReward1(world),
        BowsersKeepDoorReward2(world),
        BowsersKeepDoorReward3(world),
        BowsersKeepDoorReward4(world),
        BowsersKeepDoorReward5(world),
        BowsersKeepDoorReward6(world),
        FactorySaveRoom(world),
        FactoryBoltPlatforms(world),
        FactoryFallingAxems(world),
        FactoryTreasurePit1(world),
        FactoryTreasurePit2(world),
        FactoryConveyorPlatforms1(world),
        FactoryConveyorPlatforms2(world),
        FactoryBehindSnakes1(world),
        FactoryBehindSnakes2(world),
    ]
