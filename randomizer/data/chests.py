# Data module for chest data.

from randomizer.data import items
from randomizer.logic.utils import isclass_or_instance
from .locations import Area, ItemLocation


# ******* Chest location classes

class Chest(ItemLocation):
    """Subclass for treasure chest location."""


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

    @staticmethod
    def can_access(inventory):
        return inventory.has_item(items.Seed) and inventory.has_item(items.Fertilizer)


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


class MushroomWay2(Chest):
    area = Area.MushroomWay
    addresses = [0x14b38d]
    item = items.Coins8


class MushroomWay3(Chest):
    area = Area.MushroomWay
    addresses = [0x14b3da]
    item = items.Flower


class MushroomWay4(Chest):
    area = Area.MushroomWay
    addresses = [0x14b3de]
    item = items.RecoveryMushroom


# *** Mushroom Kingdom

class MushroomKingdomVault1(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148ad3]
    item = items.Coins10


class MushroomKingdomVault2(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148adf]
    item = items.RecoveryMushroom


class MushroomKingdomVault3(Chest):
    area = Area.MushroomKingdom
    addresses = [0x148aeb]
    item = items.Flower


# *** Bandit's Way

class BanditsWay1(Chest):
    area = Area.BanditsWay
    addresses = [0x14b535]
    item = items.KerokeroCola


class BanditsWay2(Chest):
    area = Area.BanditsWay
    addresses = [0x1495ff]
    item = items.RecoveryMushroom


class BanditsWayStarChest(StarAllowedChest):
    area = Area.BanditsWay
    addresses = [0x14964c]
    item = items.BanditsWayStar


class BanditsWayDogJump(StarAllowedChest):
    area = Area.BanditsWay
    addresses = [0x149650]
    item = items.Flower


class BanditsWayCroco(Chest):
    area = Area.BanditsWay
    addresses = [0x14b494]
    item = items.RecoveryMushroom


# *** Kero Sewers

class KeroSewersPandoriteRoom(Chest):
    area = Area.KeroSewers
    addresses = [0x149053]
    item = items.Flower


class KeroSewersStarChest(StarAllowedChest):
    area = Area.KeroSewers
    addresses = [0x14901e]
    item = items.KeroSewersStar


# *** Rose Way

class RoseWayPlatform(Chest):
    area = Area.RoseWay
    addresses = [0x14973e]
    item = items.FrogCoin


# *** Rose Town

class RoseTownStore1(Chest):
    area = Area.RoseTown
    addresses = [0x1499ad]
    item = items.Flower


class RoseTownStore2(Chest):
    area = Area.RoseTown
    addresses = [0x1499b9]
    item = items.FrogCoin


class GardenerCloud1(RoseTownGardenerChest):
    area = Area.RoseTownClouds
    addresses = [0x14de24]
    item = items.LazyShellArmor


class GardenerCloud2(RoseTownGardenerChest):
    area = Area.RoseTownClouds
    addresses = [0x14de28]
    item = items.LazyShellWeapon


# *** Forest Maze

class ForestMaze1(Chest):
    area = Area.ForestMaze
    addresses = [0x14b75e]
    item = items.KerokeroCola


class ForestMaze2(Chest):
    area = Area.ForestMaze
    addresses = [0x14b872]
    item = items.FrogCoin


class ForestMazeUnderground1(Chest):
    area = Area.ForestMaze
    addresses = [0x14bb9d]
    item = items.KerokeroCola


class ForestMazeUnderground2(Chest):
    area = Area.ForestMaze
    addresses = [0x14bba1]
    item = items.Flower


class ForestMazeUnderground3(Chest):
    area = Area.ForestMaze
    addresses = [0x14bba5]
    item = items.YouMissed


class ForestMazeRedEssence(Chest):
    area = Area.ForestMaze
    addresses = [0x14b841]
    item = items.RedEssence


# *** Pipe Vault

class PipeVaultSlide1(Chest):
    area = Area.PipeVault
    addresses = [0x14a2b7]
    item = items.Flower


class PipeVaultSlide2(Chest):
    area = Area.PipeVault
    addresses = [0x14a2c3]
    item = items.FrogCoin


class PipeVaultSlide3(Chest):
    area = Area.PipeVault
    addresses = [0x14a2cf]
    item = items.FrogCoin


class PipeVaultNippers1(Chest):
    area = Area.PipeVault
    addresses = [0x14a33e]
    item = items.Flower


class PipeVaultNippers2(Chest):
    area = Area.PipeVault
    addresses = [0x14a34a]
    item = items.CoinsDoubleBig


# *** Yo'ster Isle

class YosterIsleEntrance(Chest):
    area = Area.YosterIsle
    addresses = [0x148b39]
    item = items.FrogCoin


# *** Moleville

class MolevilleMinesStarChest(StarAllowedChest):
    area = Area.MolevilleMines
    addresses = [0x14c4af]
    item = items.MolevilleMinesStar


class MolevilleMinesCoins(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c3c6]
    item = items.Coins150


class MolevilleMinesPunchinello1(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c546]
    item = items.RecoveryMushroom


class MolevilleMinesPunchinello2(Chest):
    area = Area.MolevilleMines
    addresses = [0x14c552]
    item = items.Flower


# *** Booster Pass

class BoosterPass1(Chest):
    area = Area.BoosterPass
    addresses = [0x149c62]
    item = items.Flower


class BoosterPass2(Chest):
    area = Area.BoosterPass
    addresses = [0x149c6e]
    item = items.RockCandy


class BoosterPassSecret1(Chest):
    area = Area.BoosterPass
    addresses = [0x14da32]
    item = items.FrogCoin


class BoosterPassSecret2(Chest):
    area = Area.BoosterPass
    addresses = [0x14da36]
    item = items.Flower


class BoosterPassSecret3(Chest):
    area = Area.BoosterPass
    addresses = [0x14da42]
    item = items.KerokeroCola


# *** Booster Tower

class BoosterTowerSpookum(Chest):
    area = Area.BoosterTower
    addresses = [0x14b23e]
    item = items.FrogCoin


class BoosterTowerThwomp(Chest):
    area = Area.BoosterTower
    addresses = [0x148c60]
    item = items.RecoveryMushroom


class BoosterTowerParachute(Chest):
    area = Area.BoosterTower
    addresses = [0x148c2f]
    item = items.FrogCoin


class BoosterTowerZoomShoes(Chest):
    area = Area.BoosterTower
    addresses = [0x148eac]
    item = items.ZoomShoes


class BoosterTowerTop1(NonCoinChest):
    area = Area.BoosterTower
    addresses = [0x14b2d1]
    item = items.FrogCoin


class BoosterTowerTop2(Chest):
    area = Area.BoosterTower
    addresses = [0x14b2e1]
    item = items.GoodieBag


class BoosterTowerTop3(Chest):
    area = Area.BoosterTower
    addresses = [0x14b325]
    item = items.RecoveryMushroom


# *** Marrymore

class MarrymoreInn(Chest):
    area = Area.Marrymore
    addresses = [0x1485d7]
    item = items.FrogCoin


# *** Sea

class SeaStarChest(StarAllowedChest):
    area = Area.Sea
    addresses = [0x14a458]
    item = items.SeaStar


class SeaSaveRoom1(Chest):
    area = Area.Sea
    addresses = [0x14a40e]
    item = items.FrogCoin


class SeaSaveRoom2(Chest):
    area = Area.Sea
    addresses = [0x14a412]
    item = items.Flower


class SeaSaveRoom3(Chest):
    area = Area.Sea
    addresses = [0x14a416]
    item = items.RecoveryMushroom


class SeaSaveRoom4(Chest):
    area = Area.Sea
    addresses = [0x14a42f]
    item = items.MaxMushroom


# *** Sunken Ship

class SunkenShipRatStairs(Chest):
    area = Area.SunkenShip
    addresses = [0x14ac26]
    item = items.Coins100


class SunkenShipShop(Chest):
    area = Area.SunkenShip
    addresses = [0x14ac70]
    item = items.Coins100


class SunkenShipCoins1(Chest):
    area = Area.SunkenShip
    addresses = [0x14ad85]
    item = items.Coins100


class SunkenShipCoins2(Chest):
    area = Area.SunkenShip
    addresses = [0x14ad89]
    item = items.Coins100


class SunkenShipCloneRoom(Chest):
    area = Area.SunkenShip
    addresses = [0x14ae61]
    item = items.KerokeroCola


class SunkenShipFrogCoinRoom(Chest):
    area = Area.SunkenShip
    addresses = [0x14aef5]
    item = items.FrogCoin


class SunkenShipHidonMushroom(Chest):
    area = Area.SunkenShip
    addresses = [0x14af0e]
    item = items.RecoveryMushroom


class SunkenShipSafetyRing(Chest):
    area = Area.SunkenShip
    addresses = [0x14af27]
    item = items.SafetyRing


class SunkenShipBandanaReds(Chest):
    area = Area.SunkenShip
    addresses = [0x14895d]
    item = items.RecoveryMushroom


# *** Land's End

class LandsEndRedEssence(Chest):
    area = Area.LandsEnd
    addresses = [0x14a4df]
    item = items.RedEssence


class LandsEndChowPit1(Chest):
    area = Area.LandsEnd
    addresses = [0x14a51c]
    item = items.KerokeroCola


class LandsEndChowPit2(Chest):
    area = Area.LandsEnd
    addresses = [0x14a528]
    item = items.FrogCoin


class LandsEndBeeRoom(Chest):
    area = Area.LandsEnd
    addresses = [0x14a5a2]
    item = items.FrogCoin


class LandsEndSecret1(Chest):
    area = Area.LandsEnd
    addresses = [0x14c1f4]
    item = items.FrogCoin


class LandsEndSecret2(Chest):
    area = Area.LandsEnd
    addresses = [0x14c200]
    item = items.FrogCoin


class LandsEndShyAway(Chest):
    area = Area.LandsEnd
    addresses = [0x14d932]
    item = items.RecoveryMushroom


class LandsEndStarChest1(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c069]
    item = items.LandsEndVolcanoStar


class LandsEndStarChest2(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c02c]
    item = items.LandsEndStar2


class LandsEndStarChest3(StarAllowedChest):
    area = Area.LandsEnd
    addresses = [0x14c030]
    item = items.LandsEndStar3


# *** Belome Temple

class BelomeTempleFortuneTeller(Chest):
    area = Area.BelomeTemple
    addresses = [0x14de81]
    item = items.Coins50


class BelomeTempleAfterFortune1(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df69]
    item = items.FrogCoin


class BelomeTempleAfterFortune2(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df6d]
    item = items.Coins150


class BelomeTempleAfterFortune3(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df79]
    item = items.FrogCoin


class BelomeTempleAfterFortune4(Chest):
    area = Area.BelomeTemple
    addresses = [0x14df7d]
    item = items.FrogCoin


# *** Monstro Town

class MonstroTownEntrance(Chest):
    area = Area.MonstroTown
    addresses = [0x14c10d]
    item = items.FrogCoin


# *** Bean Valley

class BeanValley1(Chest):
    area = Area.BeanValley
    addresses = [0x14bde3]
    item = items.Flower


class BeanValley2(Chest):
    area = Area.BeanValley
    addresses = [0x14bdef]
    item = items.FrogCoin


class BeanValleyBoxBoyRoom1(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cc58]
    item = items.RedEssence


class BeanValleyBoxBoyRoom2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cc64]
    item = items.FrogCoin


class BeanValleySlotRoom(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14cf7e]
    item = items.KerokeroCola


class BeanValleyPiranhaPlants(Chest):
    area = Area.BeanValley
    addresses = [0x14bdb6]
    item = items.FrogCoin


class BeanValleyBeanstalk(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d444]
    item = items.Flower


class BeanValleyCloud1(Chest):
    area = Area.BeanValley
    addresses = [0x14d2f1]
    item = items.FrogCoin


class BeanValleyCloud2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d2fd]
    item = items.RareScarf


class BeanValleyFall1(Chest):
    area = Area.BeanValley
    addresses = [0x14d316]
    item = items.Flower


class BeanValleyFall2(NonCoinChest):
    area = Area.BeanValley
    addresses = [0x14d322]
    item = items.Flower


# *** Nimbus Land

class NimbusLandShop(NonCoinChest):
    area = Area.NimbusLand
    addresses = [0x14ce25]
    item = items.FrogCoin


class NimbusCastleBeforeBirdo1(StarAllowedChest):
    area = Area.NimbusLand
    addresses = [0x14a088]
    item = items.Flower
    missable = True


class NimbusCastleBeforeBirdo2(Chest):
    area = Area.NimbusLand
    addresses = [0x14eda7]
    item = items.FrogCoin


class NimbusCastleOutOfBounds1(NonCoinChest):
    area = Area.NimbusLand
    addresses = [0x14db97]
    item = items.FrogCoin


class NimbusCastleOutOfBounds2(Chest):
    area = Area.NimbusLand
    addresses = [0x14dba3]
    item = items.FrogCoin


class NimbusCastleSingleGoldBird(Chest):
    area = Area.NimbusLand
    addresses = [0x149f47]
    item = items.RecoveryMushroom


class NimbusCastleStarChest(StarAllowedChest):
    area = Area.NimbusLand
    addresses = [0x14a1a3]
    item = items.NimbusLandStar


class NimbusCastleStarAfterValentina(Chest):
    area = Area.NimbusLand
    addresses = [0x14a1af]
    item = items.Flower


# *** Barrel Volcano

class BarrelVolcanoSecret1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d048]
    item = items.Flower


class BarrelVolcanoSecret2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d04c]
    item = items.Flower


class BarrelVolcanoBeforeStar1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d595]
    item = items.Flower


class BarrelVolcanoBeforeStar2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d5a1]
    item = items.Coins100


class BarrelVolcanoStarRoom(StarAllowedChest):
    area = Area.BarrelVolcano
    addresses = [0x14d5ce]
    item = items.LandsEndVolcanoStar


class BarrelVolcanoSaveRoom1(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d203]
    item = items.Flower


class BarrelVolcanoSaveRoom2(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d207]
    item = items.FrogCoin


class BarrelVolcanoHinnopio(Chest):
    area = Area.BarrelVolcano
    addresses = [0x14d220]
    item = items.Coins100


# *** Bowser's Keep

class BowsersKeepDarkRoom(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e3b1]
    item = items.RecoveryMushroom


class BowsersKeepCrocoShop1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e37f]
    item = items.Coins150


class BowsersKeepCrocoShop2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e38b]
    item = items.RecoveryMushroom


class BowsersKeepInvisibleBridge1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9b3]
    item = items.FrightBomb


class BowsersKeepInvisibleBridge2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9b7]
    item = items.RoyalSyrup


class BowsersKeepInvisibleBridge3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9bb]
    item = items.IceBomb


class BowsersKeepInvisibleBridge4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c9bf]
    item = items.RockCandy


class BowsersKeepMovingPlatforms1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e536]
    item = items.Flower


class BowsersKeepMovingPlatforms2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e542]
    item = items.RedEssence


class BowsersKeepMovingPlatforms3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e546]
    item = items.MaxMushroom


class BowsersKeepMovingPlatforms4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e54a]
    item = items.FireBomb


class BowsersKeepElevatorPlatforms(Chest):
    area = Area.BowsersKeep
    addresses = [0x14c97a]
    item = items.KerokeroCola


class BowsersKeepCannonballRoom1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4b1]
    item = items.Flower


class BowsersKeepCannonballRoom2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4b5]
    item = items.Flower


class BowsersKeepCannonballRoom3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c1]
    item = items.PickMeUp


class BowsersKeepCannonballRoom4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c5]
    item = items.RockCandy


class BowsersKeepCannonballRoom5(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e4c9]
    item = items.MaxMushroom


class BowsersKeepRotatingPlatforms1(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e3ff]
    item = items.Flower


class BowsersKeepRotatingPlatforms2(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e403]
    item = items.Flower


class BowsersKeepRotatingPlatforms3(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e40f]
    item = items.FireBomb


class BowsersKeepRotatingPlatforms4(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e413]
    item = items.RoyalSyrup


class BowsersKeepRotatingPlatforms5(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e417]
    item = items.PickMeUp


class BowsersKeepRotatingPlatforms6(Chest):
    area = Area.BowsersKeep
    addresses = [0x14e41b]
    item = items.KerokeroCola


class BowsersKeepDoorReward1(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204bfc]
    item = items.SonicCymbal


class BowsersKeepDoorReward2(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c02]
    item = items.SuperSlap


class BowsersKeepDoorReward3(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c08]
    item = items.DrillClaw


class BowsersKeepDoorReward4(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c0e]
    item = items.StarGun


class BowsersKeepDoorReward5(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c14]
    item = items.RockCandy


class BowsersKeepDoorReward6(BowserDoorReward):
    area = Area.BowsersKeep
    addresses = [0x204c1a]
    item = items.RockCandy


# *** Factory

class FactorySaveRoom(Chest):
    area = Area.Factory
    addresses = [0x14bafa]
    item = items.RecoveryMushroom


class FactoryBoltPlatforms(Chest):
    area = Area.Factory
    addresses = [0x14bb6c]
    item = items.UltraHammer


class FactoryFallingAxems(Chest):
    area = Area.Factory
    addresses = [0x14e0c8]
    item = items.RecoveryMushroom


class FactoryTreasurePit1(Chest):
    area = Area.Factory
    addresses = [0x14e2c4]
    item = items.RecoveryMushroom


class FactoryTreasurePit2(NonCoinChest):
    area = Area.Factory
    addresses = [0x14e2cc]
    item = items.Flower


class FactoryConveyorPlatforms1(Chest):
    area = Area.Factory
    addresses = [0x14e9cb]
    item = items.RoyalSyrup


class FactoryConveyorPlatforms2(Chest):
    area = Area.Factory
    addresses = [0x14e9cf]
    item = items.MaxMushroom


class FactoryBehindSnakes1(Chest):
    area = Area.Factory
    addresses = [0x14e2c8]
    item = items.RecoveryMushroom


class FactoryBehindSnakes2(Chest):
    area = Area.Factory
    addresses = [0x14e2d0]
    item = items.Flower


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
