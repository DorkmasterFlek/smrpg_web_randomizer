# Data module for chest data.

from randomizer.data import items
from randomizer.logic.utils import isclass_or_instance
from . import locations


# ******* Chest location classes

class Chest(locations.ItemLocation):
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


# ******* NPC reward data classes

class Reward(locations.ItemLocation):
    """Subclass for NPC reward location."""


# ****************************** Actual chest classes

# *** Mushroom Way

class MushroomWay1(Chest):
    area = locations.Area.MushroomWay
    addresses = [0x14b389]
    item = items.Coins5


class MushroomWay2(Chest):
    area = locations.Area.MushroomWay
    addresses = [0x14b38d]
    item = items.Coins8


class MushroomWay3(Chest):
    area = locations.Area.MushroomWay
    addresses = [0x14b3da]
    item = items.Flower


class MushroomWay4(Chest):
    area = locations.Area.MushroomWay
    addresses = [0x14b3de]
    item = items.RecoveryMushroom


class ToadRescue1(Reward):
    area = locations.Area.MushroomWay
    addresses = [0x1efedc]
    item = items.HoneySyrup


class ToadRescue2(Reward):
    area = locations.Area.MushroomWay
    addresses = [0x1efe1e]
    item = items.FlowerTab


class HammerBrosReward(Reward):
    area = locations.Area.MushroomWay
    addresses = [0x1e94c4]
    item = items.Hammer


# *** Mushroom Kingdom

class MushroomKingdomVault1(Chest):
    area = locations.Area.MushroomKingdom
    addresses = [0x148ad3]
    item = items.Coins10


class MushroomKingdomVault2(Chest):
    area = locations.Area.MushroomKingdom
    addresses = [0x148adf]
    item = items.RecoveryMushroom


class MushroomKingdomVault3(Chest):
    area = locations.Area.MushroomKingdom
    addresses = [0x148aeb]
    item = items.Flower


class WalletGuy1(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e3765]
    item = items.FlowerTab
    missable = True


class WalletGuy2(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e17de]
    item = items.FrogCoin
    missable = True


class MushroomKingdomStore(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e65f8]
    item = items.PickMeUp


class PeachSurprise(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e26b2]
    item = items.Mushroom


class InvasionFamily(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e3a74]
    item = items.FlowerTab
    missable = True


class InvasionGuestRoom(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e3373]
    item = items.WakeUpPin
    missable = True


class InvasionGuard(Reward):
    area = locations.Area.MushroomKingdom
    addresses = [0x1e3514]
    item = items.FlowerTab
    missable = True


# *** Bandit's Way

class BanditsWay1(Chest):
    area = locations.Area.BanditsWay
    addresses = [0x14b535]
    item = items.KerokeroCola


class BanditsWay2(Chest):
    area = locations.Area.BanditsWay
    addresses = [0x1495ff]
    item = items.RecoveryMushroom


class BanditsWayStarChest(StarAllowedChest):
    area = locations.Area.BanditsWay
    addresses = [0x14964c]
    item = items.BanditsWayStar


class BanditsWayDogJump(StarAllowedChest):
    area = locations.Area.BanditsWay
    addresses = [0x149650]
    item = items.Flower


class BanditsWayCroco(Chest):
    area = locations.Area.BanditsWay
    addresses = [0x14b494]
    item = items.RecoveryMushroom


class Croco1Reward(Reward):
    area = locations.Area.BanditsWay
    addresses = [0x1e94f0]
    item = items.Wallet


# *** Kero Sewers

class KeroSewersPandoriteRoom(Chest):
    area = locations.Area.KeroSewers
    addresses = [0x149053]
    item = items.Flower


class KeroSewersStarChest(StarAllowedChest):
    area = locations.Area.KeroSewers
    addresses = [0x14901e]
    item = items.KeroSewersStar


class PandoriteReward(Reward):
    area = locations.Area.KeroSewers
    addresses = [0x1e950d]
    item = items.TrueformPin


# *** Midas River

class MidasRiverFirstTime(Reward):
    area = locations.Area.MidasRiver
    addresses = [0x205fd3]
    item = items.NokNokShell


# *** Tadpole Pond

class CricketPieReward(Reward):
    area = locations.Area.TadpolePond
    addresses = [0x1e6636]
    item = items.FroggieStick

    @staticmethod
    def can_access(inventory):
        return inventory.has_item(items.CricketPie)


class CricketJamReward(Reward):
    area = locations.Area.TadpolePond
    addresses = [0x1e6642]
    item = items.FrogCoin

    @staticmethod
    def can_access(inventory):
        return inventory.has_item(items.CricketJam)

    def get_patch(self):
        patch = super().get_patch()

        # Extra bytes needed to enable this spot to use the regular item granting subroutine.
        patch.add_data(0x1e6631, bytes([0x40, 0x66]))

        return patch


# *** Rose Way

class RoseWayPlatform(Chest):
    area = locations.Area.RoseWay
    addresses = [0x14973e]
    item = items.FrogCoin


# *** Rose Town

class RoseTownStore1(Chest):
    area = locations.Area.RoseTown
    addresses = [0x1499ad]
    item = items.Flower


class RoseTownStore2(Chest):
    area = locations.Area.RoseTown
    addresses = [0x1499b9]
    item = items.FrogCoin


class GardenerCloud1(RoseTownGardenerChest):
    area = locations.Area.RoseTownClouds
    addresses = [0x14de24]
    item = items.LazyShellArmor


class GardenerCloud2(RoseTownGardenerChest):
    area = locations.Area.RoseTownClouds
    addresses = [0x14de28]
    item = items.LazyShellWeapon


class RoseTownToad(Reward):
    area = locations.Area.RoseTown
    addresses = [0x1e6030]
    item = items.FlowerTab
    missable = True


class Gaz(Reward):
    area = locations.Area.RoseTown
    addresses = [0x1e61ff]
    item = items.FingerShot


# *** Forest Maze

class ForestMaze1(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14b75e]
    item = items.KerokeroCola


class ForestMaze2(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14b872]
    item = items.FrogCoin


class ForestMazeUnderground1(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14bb9d]
    item = items.KerokeroCola


class ForestMazeUnderground2(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14bba1]
    item = items.Flower


class ForestMazeUnderground3(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14bba5]
    item = items.YouMissed


class ForestMazeRedEssence(Chest):
    area = locations.Area.ForestMaze
    addresses = [0x14b841]
    item = items.RedEssence


# *** Pipe Vault

class PipeVaultSlide1(Chest):
    area = locations.Area.PipeVault
    addresses = [0x14a2b7]
    item = items.Flower


class PipeVaultSlide2(Chest):
    area = locations.Area.PipeVault
    addresses = [0x14a2c3]
    item = items.FrogCoin


class PipeVaultSlide3(Chest):
    area = locations.Area.PipeVault
    addresses = [0x14a2cf]
    item = items.FrogCoin


class PipeVaultNippers1(Chest):
    area = locations.Area.PipeVault
    addresses = [0x14a33e]
    item = items.Flower


class PipeVaultNippers2(Chest):
    area = locations.Area.PipeVault
    addresses = [0x14a34a]
    item = items.CoinsDoubleBig


class GoombaThumping1(Reward):
    area = locations.Area.PipeVault
    addresses = [0x1e2f9c]
    item = items.FlowerTab


class GoombaThumping2(Reward):
    area = locations.Area.PipeVault
    addresses = [0x1e3fae]
    item = items.FlowerJar


# *** Yo'ster Isle

class YosterIsleEntrance(Chest):
    area = locations.Area.YosterIsle
    addresses = [0x148b39]
    item = items.FrogCoin


# *** Moleville


class TreasureSeller1(Reward):
    area = locations.Area.Moleville
    addresses = [0x1f8ca5]
    item = items.LuckyJewel


class TreasureSeller2(Reward):
    area = locations.Area.Moleville
    addresses = [0x1f8cd1]
    item = items.MysteryEgg


class TreasureSeller3(Reward):
    area = locations.Area.Moleville
    addresses = [0x1f8cfd]
    item = items.FryingPan


# *** Moleville Mines

class MolevilleMinesStarChest(StarAllowedChest):
    area = locations.Area.MolevilleMines
    addresses = [0x14c4af]
    item = items.MolevilleMinesStar


class MolevilleMinesCoins(Chest):
    area = locations.Area.MolevilleMines
    addresses = [0x14c3c6]
    item = items.Coins150


class MolevilleMinesPunchinello1(Chest):
    area = locations.Area.MolevilleMines
    addresses = [0x14c546]
    item = items.RecoveryMushroom


class MolevilleMinesPunchinello2(Chest):
    area = locations.Area.MolevilleMines
    addresses = [0x14c552]
    item = items.Flower


class CrocoFlunkie1(Reward):
    area = locations.Area.MolevilleMines
    addresses = [0x202073]
    item = items.FlowerTab
    missable = True


class CrocoFlunkie2(Reward):
    area = locations.Area.MolevilleMines
    addresses = [0x2020cc]
    item = items.FlowerTab
    missable = True


class CrocoFlunkie3(Reward):
    area = locations.Area.MolevilleMines
    addresses = [0x202123]
    item = items.FlowerTab
    missable = True


# *** Booster Pass

class BoosterPass1(Chest):
    area = locations.Area.BoosterPass
    addresses = [0x149c62]
    item = items.Flower


class BoosterPass2(Chest):
    area = locations.Area.BoosterPass
    addresses = [0x149c6e]
    item = items.RockCandy


class BoosterPassSecret1(Chest):
    area = locations.Area.BoosterPass
    addresses = [0x14da32]
    item = items.FrogCoin


class BoosterPassSecret2(Chest):
    area = locations.Area.BoosterPass
    addresses = [0x14da36]
    item = items.Flower


class BoosterPassSecret3(Chest):
    area = locations.Area.BoosterPass
    addresses = [0x14da42]
    item = items.KerokeroCola


# *** Booster Tower

class BoosterTowerSpookum(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x14b23e]
    item = items.FrogCoin


class BoosterTowerThwomp(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x148c60]
    item = items.RecoveryMushroom


class BoosterTowerMasher(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x1f9ce9]
    item = items.Masher


class BoosterTowerParachute(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x148c2f]
    item = items.FrogCoin


class BoosterTowerZoomShoes(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x148eac]
    item = items.ZoomShoes


class BoosterTowerTop1(NonCoinChest):
    area = locations.Area.BoosterTower
    addresses = [0x14b2d1]
    item = items.FrogCoin


class BoosterTowerTop2(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x14b2e1]
    item = items.GoodieBag


class BoosterTowerTop3(Chest):
    area = locations.Area.BoosterTower
    addresses = [0x14b325]
    item = items.RecoveryMushroom


class BoosterTowerRailway(Reward):
    area = locations.Area.BoosterTower
    addresses = [0x1ee468]
    item = items.FlowerTab


class BoosterTowerChomp(Reward):
    area = locations.Area.BoosterTower
    addresses = [0x1ee27b]
    item = items.Chomp


class BoosterTowerCurtainGame(Reward):
    area = locations.Area.BoosterTower
    addresses = [0x1ef49b]
    item = items.Amulet


# *** Marrymore

class MarrymoreInn(Chest):
    area = locations.Area.Marrymore
    addresses = [0x1485d7]
    item = items.FrogCoin


# *** Seaside Town

class SeasideTownRescue(Reward):
    area = locations.Area.SeasideTown
    addresses = [0x1ed6c7]
    item = items.FlowerBox

    @staticmethod
    def can_access(inventory):
        return inventory.has_item(items.ShedKey)


# *** Sea

class SeaStarChest(StarAllowedChest):
    area = locations.Area.Sea
    addresses = [0x14a458]
    item = items.SeaStar


class SeaSaveRoom1(Chest):
    area = locations.Area.Sea
    addresses = [0x14a40e]
    item = items.FrogCoin


class SeaSaveRoom2(Chest):
    area = locations.Area.Sea
    addresses = [0x14a412]
    item = items.Flower


class SeaSaveRoom3(Chest):
    area = locations.Area.Sea
    addresses = [0x14a416]
    item = items.RecoveryMushroom


class SeaSaveRoom4(Chest):
    area = locations.Area.Sea
    addresses = [0x14a42f]
    item = items.MaxMushroom


# *** Sunken Ship

class SunkenShipRatStairs(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14ac26]
    item = items.Coins100


class SunkenShipShop(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14ac70]
    item = items.Coins100


class SunkenShipCoins1(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14ad85]
    item = items.Coins100


class SunkenShipCoins2(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14ad89]
    item = items.Coins100


class SunkenShipCloneRoom(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14ae61]
    item = items.KerokeroCola


class SunkenShipFrogCoinRoom(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14aef5]
    item = items.FrogCoin


class SunkenShipHidonMushroom(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14af0e]
    item = items.RecoveryMushroom


class SunkenShipSafetyRing(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14af27]
    item = items.SafetyRing


class SunkenShipBandanaReds(Chest):
    area = locations.Area.SunkenShip
    addresses = [0x14895d]
    item = items.RecoveryMushroom


class SunkenShip3DMaze(Reward):
    area = locations.Area.SunkenShip
    addresses = [0x203b30]
    item = items.RoyalSyrup


class SunkenShipCannonballPuzzle(Reward):
    area = locations.Area.SunkenShip
    addresses = [0x203b57]
    item = items.Mushroom


class SunkenShipHidonReward(Reward):
    area = locations.Area.SunkenShip
    addresses = [0x1e979c]
    item = items.SafetyBadge


# *** Land's End

class LandsEndRedEssence(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14a4df]
    item = items.RedEssence


class LandsEndChowPit1(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14a51c]
    item = items.KerokeroCola


class LandsEndChowPit2(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14a528]
    item = items.FrogCoin


class LandsEndBeeRoom(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14a5a2]
    item = items.FrogCoin


class LandsEndSecret1(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14c1f4]
    item = items.FrogCoin


class LandsEndSecret2(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14c200]
    item = items.FrogCoin


class LandsEndShyAway(Chest):
    area = locations.Area.LandsEnd
    addresses = [0x14d932]
    item = items.RecoveryMushroom


class LandsEndStarChest1(StarAllowedChest):
    area = locations.Area.LandsEnd
    addresses = [0x14c069]
    item = items.LandsEndVolcanoStar


class LandsEndStarChest2(StarAllowedChest):
    area = locations.Area.LandsEnd
    addresses = [0x14c02c]
    item = items.LandsEndStar2


class LandsEndStarChest3(StarAllowedChest):
    area = locations.Area.LandsEnd
    addresses = [0x14c030]
    item = items.LandsEndStar3


class TroopaClimb(Reward):
    area = locations.Area.LandsEnd
    addresses = [0x1f5282]
    item = items.TroopaPin


# *** Belome Temple

class BelomeTempleFortuneTeller(Chest):
    area = locations.Area.BelomeTemple
    addresses = [0x14de81]
    item = items.Coins50


class BelomeTempleAfterFortune1(Chest):
    area = locations.Area.BelomeTemple
    addresses = [0x14df69]
    item = items.FrogCoin


class BelomeTempleAfterFortune2(Chest):
    area = locations.Area.BelomeTemple
    addresses = [0x14df6d]
    item = items.Coins150


class BelomeTempleAfterFortune3(Chest):
    area = locations.Area.BelomeTemple
    addresses = [0x14df79]
    item = items.FrogCoin


class BelomeTempleAfterFortune4(Chest):
    area = locations.Area.BelomeTemple
    addresses = [0x14df7d]
    item = items.FrogCoin


class BelomeTempleTreasure1(Reward):
    area = locations.Area.BelomeTemple
    addresses = [0x1f4fba]
    item = items.RoyalSyrup


class BelomeTempleTreasure2(Reward):
    area = locations.Area.BelomeTemple
    addresses = [0x1f4fc0]
    item = items.MaxMushroom


class BelomeTempleTreasure3(Reward):
    area = locations.Area.BelomeTemple
    addresses = [0x1f4fc6]
    item = items.FireBomb


# *** Monstro Town

class MonstroTownEntrance(Chest):
    area = locations.Area.MonstroTown
    addresses = [0x14c10d]
    item = items.FrogCoin


class JinxDojoReward(Reward):
    area = locations.Area.MonstroTown
    addresses = [0x1e982a]
    item = items.JinxBelt


class CulexReward(Reward):
    area = locations.Area.MonstroTown
    addresses = [0x1e98bf]
    item = items.QuartzCharm


class SuperJumps30(Reward):
    area = locations.Area.MonstroTown
    addresses = [0x1f6b41, 0x1f6b6a]
    item = items.AttackScarf


class SuperJumps100(Reward):
    area = locations.Area.MonstroTown
    addresses = [0x1f6b8f]
    item = items.SuperSuit


class ThreeMustyFears(Reward):
    area = locations.Area.MonstroTown
    addresses = [0x1f7160]
    item = items.GhostMedal

    @staticmethod
    def can_access(inventory):
        return (inventory.has_item(items.BigBooFlag) and inventory.has_item(items.GreaperFlag) and
                inventory.has_item(items.DryBonesFlag))


# *** Bean Valley

class BeanValley1(Chest):
    area = locations.Area.BeanValley
    addresses = [0x14bde3]
    item = items.Flower


class BeanValley2(Chest):
    area = locations.Area.BeanValley
    addresses = [0x14bdef]
    item = items.FrogCoin


class BeanValleyBoxBoyRoom1(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14cc58]
    item = items.RedEssence


class BeanValleyBoxBoyRoom2(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14cc64]
    item = items.FrogCoin


class BeanValleySlotRoom(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14cf7e]
    item = items.KerokeroCola


class BeanValleyPiranhaPlants(Chest):
    area = locations.Area.BeanValley
    addresses = [0x14bdb6]
    item = items.FrogCoin


class BeanValleyBeanstalk(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14d444]
    item = items.Flower


class BeanValleyCloud1(Chest):
    area = locations.Area.BeanValley
    addresses = [0x14d2f1]
    item = items.FrogCoin


class BeanValleyCloud2(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14d2fd]
    item = items.RareScarf


class BeanValleyFall1(Chest):
    area = locations.Area.BeanValley
    addresses = [0x14d316]
    item = items.Flower


class BeanValleyFall2(NonCoinChest):
    area = locations.Area.BeanValley
    addresses = [0x14d322]
    item = items.Flower


# *** Nimbus Land

class NimbusLandShop(NonCoinChest):
    area = locations.Area.NimbusLand
    addresses = [0x14ce25]
    item = items.FrogCoin


class NimbusCastleBeforeBirdo1(StarAllowedChest):
    area = locations.Area.NimbusLand
    addresses = [0x14a088]
    item = items.Flower
    missable = True


class NimbusCastleBeforeBirdo2(Chest):
    area = locations.Area.NimbusLand
    addresses = [0x14eda7]
    item = items.FrogCoin


class NimbusCastleOutOfBounds1(NonCoinChest):
    area = locations.Area.NimbusLand
    addresses = [0x14db97]
    item = items.FrogCoin


class NimbusCastleOutOfBounds2(Chest):
    area = locations.Area.NimbusLand
    addresses = [0x14dba3]
    item = items.FrogCoin


class NimbusCastleSingleGoldBird(Chest):
    area = locations.Area.NimbusLand
    addresses = [0x149f47]
    item = items.RecoveryMushroom


class NimbusCastleStarChest(StarAllowedChest):
    area = locations.Area.NimbusLand
    addresses = [0x14a1a3]
    item = items.NimbusLandStar

    @staticmethod
    def can_access(inventory):
        return locations.can_access_nimbus_castle_back(inventory)


class NimbusCastleStarAfterValentina(Chest):
    area = locations.Area.NimbusLand
    addresses = [0x14a1af]
    item = items.Flower

    @staticmethod
    def can_access(inventory):
        return locations.can_access_nimbus_castle_back(inventory)


class DodoReward(Reward):
    area = locations.Area.NimbusLand
    addresses = [0x20936a]
    item = items.Feather


class NimbusLandPrisoners(Reward):
    area = locations.Area.NimbusLand
    addresses = [0x20a9c5]
    item = items.FlowerJar
    missable = True


class NimbusLandSignalRing(Reward):
    area = locations.Area.NimbusLand
    addresses = [0x20a456]
    item = items.SignalRing

    @staticmethod
    def can_access(inventory):
        return locations.can_access_nimbus_castle_back(inventory)


class NimbusLandCellar(Reward):
    area = locations.Area.NimbusLand
    addresses = [0x1ea732]
    item = items.FlowerJar

    @staticmethod
    def can_access(inventory):
        return locations.can_access_nimbus_castle_back(inventory)


# *** Barrel Volcano

class BarrelVolcanoSecret1(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d048]
    item = items.Flower


class BarrelVolcanoSecret2(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d04c]
    item = items.Flower


class BarrelVolcanoBeforeStar1(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d595]
    item = items.Flower


class BarrelVolcanoBeforeStar2(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d5a1]
    item = items.Coins100


class BarrelVolcanoStarRoom(StarAllowedChest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d5ce]
    item = items.LandsEndVolcanoStar


class BarrelVolcanoSaveRoom1(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d203]
    item = items.Flower


class BarrelVolcanoSaveRoom2(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d207]
    item = items.FrogCoin


class BarrelVolcanoHinnopio(Chest):
    area = locations.Area.BarrelVolcano
    addresses = [0x14d220]
    item = items.Coins100


# *** Bowser's Keep

class BowsersKeepDarkRoom(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e3b1]
    item = items.RecoveryMushroom


class BowsersKeepCrocoShop1(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e37f]
    item = items.Coins150


class BowsersKeepCrocoShop2(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e38b]
    item = items.RecoveryMushroom


class BowsersKeepInvisibleBridge1(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14c9b3]
    item = items.FrightBomb


class BowsersKeepInvisibleBridge2(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14c9b7]
    item = items.RoyalSyrup


class BowsersKeepInvisibleBridge3(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14c9bb]
    item = items.IceBomb


class BowsersKeepInvisibleBridge4(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14c9bf]
    item = items.RockCandy


class BowsersKeepMovingPlatforms1(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e536]
    item = items.Flower


class BowsersKeepMovingPlatforms2(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e542]
    item = items.RedEssence


class BowsersKeepMovingPlatforms3(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e546]
    item = items.MaxMushroom


class BowsersKeepMovingPlatforms4(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e54a]
    item = items.FireBomb


class BowsersKeepElevatorPlatforms(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14c97a]
    item = items.KerokeroCola


class BowsersKeepCannonballRoom1(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e4b1]
    item = items.Flower


class BowsersKeepCannonballRoom2(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e4b5]
    item = items.Flower


class BowsersKeepCannonballRoom3(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e4c1]
    item = items.PickMeUp


class BowsersKeepCannonballRoom4(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e4c5]
    item = items.RockCandy


class BowsersKeepCannonballRoom5(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e4c9]
    item = items.MaxMushroom


class BowsersKeepRotatingPlatforms1(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e3ff]
    item = items.Flower


class BowsersKeepRotatingPlatforms2(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e403]
    item = items.Flower


class BowsersKeepRotatingPlatforms3(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e40f]
    item = items.FireBomb


class BowsersKeepRotatingPlatforms4(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e413]
    item = items.RoyalSyrup


class BowsersKeepRotatingPlatforms5(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e417]
    item = items.PickMeUp


class BowsersKeepRotatingPlatforms6(Chest):
    area = locations.Area.BowsersKeep
    addresses = [0x14e41b]
    item = items.KerokeroCola


class BowsersKeepDoorReward1(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204bfc]
    item = items.SonicCymbal


class BowsersKeepDoorReward2(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204c02]
    item = items.SuperSlap


class BowsersKeepDoorReward3(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204c08]
    item = items.DrillClaw


class BowsersKeepDoorReward4(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204c0e]
    item = items.StarGun


class BowsersKeepDoorReward5(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204c14]
    item = items.RockCandy


class BowsersKeepDoorReward6(BowserDoorReward):
    area = locations.Area.BowsersKeep
    addresses = [0x204c1a]
    item = items.RockCandy


# *** Factory

class FactorySaveRoom(Chest):
    area = locations.Area.Factory
    addresses = [0x14bafa]
    item = items.RecoveryMushroom


class FactoryBoltPlatforms(Chest):
    area = locations.Area.Factory
    addresses = [0x14bb6c]
    item = items.UltraHammer


class FactoryFallingAxems(Chest):
    area = locations.Area.Factory
    addresses = [0x14e0c8]
    item = items.RecoveryMushroom


class FactoryTreasurePit1(Chest):
    area = locations.Area.Factory
    addresses = [0x14e2c4]
    item = items.RecoveryMushroom


class FactoryTreasurePit2(NonCoinChest):
    area = locations.Area.Factory
    addresses = [0x14e2cc]
    item = items.Flower


class FactoryConveyorPlatforms1(Chest):
    area = locations.Area.Factory
    addresses = [0x14e9cb]
    item = items.RoyalSyrup


class FactoryConveyorPlatforms2(Chest):
    area = locations.Area.Factory
    addresses = [0x14e9cf]
    item = items.MaxMushroom


class FactoryBehindSnakes1(Chest):
    area = locations.Area.Factory
    addresses = [0x14e2c8]
    item = items.RecoveryMushroom


class FactoryBehindSnakes2(Chest):
    area = locations.Area.Factory
    addresses = [0x14e2d0]
    item = items.Flower


class FactoryToadGift(Reward):
    area = locations.Area.Factory
    addresses = [0x1ff7ed]
    item = items.RockCandy


# ********************* Default objects for world

def get_default_chests(world):
    """Get default vanilla chest and reward list for the world.

    Args:
        world (randomizer.logic.main.GameWorld):

    Returns:
        list[ItemLocation]: List of default chest objects.
    """
    return [
        # Chests
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
        BoosterTowerMasher(world),
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

        # NPC rewards
        ToadRescue1(world),
        ToadRescue2(world),
        HammerBrosReward(world),
        WalletGuy1(world),
        WalletGuy2(world),
        MushroomKingdomStore(world),
        PeachSurprise(world),
        InvasionFamily(world),
        InvasionGuestRoom(world),
        InvasionGuard(world),
        Croco1Reward(world),
        PandoriteReward(world),
        MidasRiverFirstTime(world),
        RoseTownToad(world),
        Gaz(world),
        TreasureSeller1(world),
        TreasureSeller2(world),
        TreasureSeller3(world),
        CrocoFlunkie1(world),
        CrocoFlunkie2(world),
        CrocoFlunkie3(world),
        BoosterTowerRailway(world),
        BoosterTowerChomp(world),
        BoosterTowerCurtainGame(world),
        SeasideTownRescue(world),
        SunkenShip3DMaze(world),
        SunkenShipCannonballPuzzle(world),
        SunkenShipHidonReward(world),
        BelomeTempleTreasure1(world),
        BelomeTempleTreasure2(world),
        BelomeTempleTreasure3(world),
        JinxDojoReward(world),
        CulexReward(world),
        SuperJumps30(world),
        SuperJumps100(world),
        ThreeMustyFears(world),
        TroopaClimb(world),
        DodoReward(world),
        NimbusLandPrisoners(world),
        NimbusLandSignalRing(world),
        NimbusLandCellar(world),
        FactoryToadGift(world),
        GoombaThumping1(world),
        GoombaThumping2(world),
        CricketPieReward(world),
        CricketJamReward(world),
    ]
