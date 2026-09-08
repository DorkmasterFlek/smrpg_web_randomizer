from __future__ import annotations
from randomizer.logic.offset_preview import compute_offset_assignments
from randomizer.debug import load_debug_config, get_location_class

from randomizer.logic.progression.prizelocations import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (
    NPC_10, NPC_11, NPC_19,
)
from randomizer.types.flags import (WinCondition, WinConditions, AvailableCharacters, FixKnifeGuy, FireworksSetting, FireworksOptions, StartingCharacters, NimbusGate, NimbusGating, Remake, InvisibleFlagsSetting, KeyItemsAnywhere, StarPieceAvailability, SeeYa, ShuffleShops, ShuffleItems)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (SummonObjectToSpecificLevel)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types.area_object import (
    AreaObject,
)
from smrpgpatchbuilder.datatypes.levels.classes import RegularClone, RegularNPC
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import SOUTHEAST
from smrpgpatchbuilder.datatypes.scripts_common.classes import UInt4, UInt8
from typing import cast, TYPE_CHECKING
from copy import copy, deepcopy

from ...types.prizelocation import (TreasureChestLocation, EventLocation, StandingLocation, RiverLocation, BoosterHillLocation, SpellSlotLocation, BossFightLocation, StarPieceLocation, CharacterRecruitmentLocation, KeyItemLocation, InvisibleFlagLocation)
from ...types.prize import SlotsPrize
from ...data.rooms.npcs import EMPTY_NPC_4
from ...data.variables.event_script_names import E0091_INVISIBLE_ITEM_SUMMONER, E2304_BANK_1F_RETURN_EVENT_2
from ...data.variables.action_script_names import A0015_DO_NOTHING

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld


def _make_dummy_npc() -> RegularNPC:
    """Create a minimal, inert dummy NPC (non-clone) for pre-allocating object presence table slots.

    Uses RegularNPC to break clone chain grouping - the serializer groups all consecutive
    Clone objects after a non-Clone parent, so the first dummy in each batch must be a
    non-Clone to prevent grouping with incompatible preceding NPCs.

    cannot_clone=False is explicit, not incidental: the EMPTY sprite is non-gridplane, so
    it never lands in buffered_sprite_ids, and an auto-decide (None) dummy falls through to
    else: set_cannot_clone(True) in _recalculate_room_partition step 7 - handing a
    dedicated VRAM allocation to a sprite that draws nothing. Step 7 honors an explicit
    False (elif original_cannot_clone is False: pass), so pinning it here keeps these
    placeholders free in any room that gets recalculated for another reason.
    """
    return RegularNPC(
        npc=EMPTY_NPC_4,
        event_script=E2304_BANK_1F_RETURN_EVENT_2,
        action_script=A0015_DO_NOTHING,
        visible=False,
        x=0, y=0, z=0, z_half=False,
        direction=SOUTHEAST,
        acute_axis=UInt4(11),
        obtuse_axis=UInt4(11),
        height=UInt8(11),
        slidable_along_walls=True,
        cant_move_if_in_air=True,
        byte7_upper2=3,
        cannot_clone=False,
    )


def _make_dummy_clone() -> RegularClone:
    """Create a minimal, inert dummy clone NPC for pre-allocating object presence table slots."""
    return RegularClone(
        npc=EMPTY_NPC_4,
        event_script=E2304_BANK_1F_RETURN_EVENT_2,
        action_script=A0015_DO_NOTHING,
        visible=False,
        x=0, y=0, z=0, z_half=False,
        direction=SOUTHEAST,
        acute_axis=UInt4(11),
        obtuse_axis=UInt4(11),
        height=UInt8(11),
    )


def _pre_allocate_dummy_npcs(world: GameWorld, invisible_item_pool: list[type]) -> None:
    """Pre-allocate dummy NPCs in all rooms that could receive slot machines or invisible flags.

    This ensures the NPC count per room is constant regardless of which prizes are assigned,
    making the WRAM object presence table layout ($6D20-$6F1F) deterministic across seeds.

    Rooms that already have vanilla slot machine NPCs (the 3 Bean Valley pipe rooms) are handled
    specially: their existing 5 slot NPCs are adopted as the dummy positions and replaced with
    inert dummies, so no extra NPCs are added.
    """
    if world._slot_dummy_indices is not None:
        return  # Already allocated (shuffle retry)

    world._slot_dummy_indices = {}
    world._flag_dummy_index = {}

    # Identify rooms that already contain vanilla slot machine NPCs.
    # These are rooms belonging to locations whose _originally_held is a SlotsPrize subclass.
    # Their last 5 objects are the vanilla slot NPCs - adopt those positions instead of adding new ones.
    vanilla_slot_rooms: set[int] = set()
    for loc in world.locations.values():
        if isinstance(loc, TreasureChestLocation):
            originally_held = loc._originally_held
            if isinstance(originally_held, type) and issubclass(originally_held, SlotsPrize):
                for r in loc._rooms:
                    vanilla_slot_rooms.add(r)

    # Compute slot-eligible rooms: rooms of TreasureChestLocations that don't blacklist SlotsPrize.
    # Mirror the can_accept() blacklist check: isinstance(prize, tuple(blacklist)) catches subclasses,
    # so we use issubclass here to match.
    slot_eligible_rooms: set[int] = set()
    for loc in world.locations.values():
        if isinstance(loc, TreasureChestLocation):
            if not loc._blacklist or not issubclass(SlotsPrize, tuple(loc._blacklist)):
                for r in loc._rooms:
                    slot_eligible_rooms.add(r)

    # Compute flag-candidate rooms: rooms of all InvisibleFlagLocation subclasses
    flag_candidate_rooms: set[int] = set()
    for loc_cls in invisible_item_pool:
        temp_loc = loc_cls(0)
        for r in temp_loc._rooms:
            flag_candidate_rooms.add(r)

    for room_id in sorted(slot_eligible_rooms):
        room = world.rooms._rooms[room_id]
        if room is None:
            continue

        if room_id in vanilla_slot_rooms:
            # Room already has 5 vanilla slot NPCs as its last 5 objects.
            # Adopt their positions and replace them with inert dummies so they're
            # harmless when slots get shuffled elsewhere.
            start_idx = len(room.objects) - 5
            world._slot_dummy_indices[room_id] = start_idx
            # First dummy must be RegularNPC to break clone chain from preceding objects
            room._objects[start_idx] = _make_dummy_npc()
            for i in range(1, 5):
                room._objects[start_idx + i] = _make_dummy_clone()
        else:
            # Room needs new dummy NPCs added (skip if would overflow 28-object limit)
            if len(room.objects) + 5 > 28:
                continue
            world._slot_dummy_indices[room_id] = len(room.objects)
            # First dummy must be RegularNPC to break clone chain from preceding objects
            room.add_objects([_make_dummy_npc()] + [_make_dummy_clone() for _ in range(4)])

    # Add 1 flag dummy to each flag-candidate room (skip rooms that would overflow 28-object limit)
    for room_id in sorted(flag_candidate_rooms):
        room = world.rooms._rooms[room_id]
        if room is None:
            continue
        if len(room.objects) + 1 > 28:
            continue
        world._flag_dummy_index[room_id] = len(room.objects)
        # Use RegularNPC to break clone chain from preceding objects
        room.add_object(_make_dummy_npc())


def set_locations(world: GameWorld) -> None:
    # establish all functional prize locations
    # regardless if they will have their contents shuffled or not

    world.locations = {
        StartingItem1Location: StartingItem1Location(),
        StartingItem2Location: StartingItem2Location(),
        StartingItem3Location: StartingItem3Location(),
        StartingItem4Location: StartingItem4Location(),
        StartingCharacter1: StartingCharacter1(),
        MushroomWay1LowerChest: MushroomWay1LowerChest(),
        MushroomWay1UpperChest: MushroomWay1UpperChest(),
        MushroomWay1ToadRescue: MushroomWay1ToadRescue(),
        MushroomWay2LedgeChest: MushroomWay2LedgeChest(),
        MushroomWay2ToadRescue: MushroomWay2ToadRescue(),
        MushroomWayRightGoomba: MushroomWayRightGoomba(),
        MushrooomWayBossFight: MushrooomWayBossFight(),
        MushroomWayStarPiece: MushroomWayStarPiece(),
        MushroomWayBossFightRewardItem: MushroomWayBossFightRewardItem(),
        MushroomWayCharacter: MushroomWayCharacter(),
        MushroomKingdomMainHall: MushroomKingdomMainHall(),
        MushroomKingdomLiberatedVaultLeft: MushroomKingdomLiberatedVaultLeft(),
        MushroomKingdomLiberatedVaultRight: MushroomKingdomLiberatedVaultRight(),
        MushroomKingdomLiberatedVaultMiddle: MushroomKingdomLiberatedVaultMiddle(),
        MushroomKingdomOccupiedVaultLeft: MushroomKingdomOccupiedVaultLeft(),
        MushroomKingdomOccupiedVaultRight: MushroomKingdomOccupiedVaultRight(),
        MushroomKingdomOccupiedVaultMiddle: MushroomKingdomOccupiedVaultMiddle(),
        MushroomKingdomChair: MushroomKingdomChair(),
        MushroomKingdomFreeShopItem: MushroomKingdomFreeShopItem(),
        MushroomKingdomShopBasementLeft: MushroomKingdomShopBasementLeft(),
        MushroomKingdomShopBasementRight: MushroomKingdomShopBasementRight(),
        MushroomKingdomWalletGuyFirstRewardLocation: MushroomKingdomWalletGuyFirstRewardLocation(),
        MushroomKingdomWalletGuySecondRewardLocation: MushroomKingdomWalletGuySecondRewardLocation(),
        MushroomKingdomOccupiedOutdoorGuardLocation: MushroomKingdomOccupiedOutdoorGuardLocation(),
        MushroomKingdomOccupiedCastleToadRescueLocation: MushroomKingdomOccupiedCastleToadRescueLocation(),
        MushroomKingdomOccupiedFamilyRescueLocation: MushroomKingdomOccupiedFamilyRescueLocation(),
        MushroomKingdomOccupiedGuestRoomLocation: MushroomKingdomOccupiedGuestRoomLocation(),
        MushroomKingdomBossFight: MushroomKingdomBossFight(),
        MushroomKingdomStarPiece: MushroomKingdomStarPiece(),
        MushroomKingdomStoreExchangeLocation: MushroomKingdomStoreExchangeLocation(),
        MushroomKingdomInnPurchaseLocation: MushroomKingdomInnPurchaseLocation(),
        BanditsWayFlowerJumpLocation: BanditsWayFlowerJumpLocation(),
        BanditsWayCoin1Location: BanditsWayCoin1Location(),
        BanditsWayCoin2Location: BanditsWayCoin2Location(),
        BanditsWayCoin3Location: BanditsWayCoin3Location(),
        BanditsWayDogChestLocation: BanditsWayDogChestLocation(),
        BanditsWayPlatformsLeftChestLocation: BanditsWayPlatformsLeftChestLocation(),
        BanditsWayPlatformsRightChestLocation: BanditsWayPlatformsRightChestLocation(),
        BanditsWayDeadEndChestLocation: BanditsWayDeadEndChestLocation(),
        BanditsWayBossFight: BanditsWayBossFight(),
        BanditsWayStarPiece: BanditsWayStarPiece(),
        BanditsWayBossFirstItemDropLocation: BanditsWayBossFirstItemDropLocation(),
        BanditsWayBossSecondItemDropLocation: BanditsWayBossSecondItemDropLocation(),
        KeroSewersStairRoomLeftChestLocation: KeroSewersStairRoomLeftChestLocation(),
        KeroSewersStairRoomRightChestLocation: KeroSewersStairRoomRightChestLocation(),
        Mimic1BossFight: Mimic1BossFight(),
        Mimic1DropRewardLocation: Mimic1DropRewardLocation(),
        Mimic1StarPiece: Mimic1StarPiece(),
        Mimic1ReloadRewardLocation: Mimic1ReloadRewardLocation(),
        KeroSewersFourRatRoomChestLocation: KeroSewersFourRatRoomChestLocation(),
        KeroSewersBeforeBelomeLowerLocation: KeroSewersBeforeBelomeLowerLocation(),
        KeroSewersBeforeBelomeUpperBeforeFlipLocation: KeroSewersBeforeBelomeUpperBeforeFlipLocation(),
        KeroSewersBossFight: KeroSewersBossFight(),
        KeroSewersStarPiece: KeroSewersStarPiece(),
        MidasRiverFirstCompletionRewardLocation: MidasRiverFirstCompletionRewardLocation(),
        MidasRiverBottomLeftCaveLocation: MidasRiverBottomLeftCaveLocation(),
        MidasRiverBottomRightCaveLocation: MidasRiverBottomRightCaveLocation(),
        MidasRiverLeftCaveLocation: MidasRiverLeftCaveLocation(),
        TadpolePondCricketPieExchangeLocation: TadpolePondCricketPieExchangeLocation(),
        TadpolePondCricketJamExchangeLocation: TadpolePondCricketJamExchangeLocation(),
        MelodyBayFirstRewardLocation: MelodyBayFirstRewardLocation(),
        MelodyBaySecondRewardLocation: MelodyBaySecondRewardLocation(),
        MelodyBayThirdRewardLocation: MelodyBayThirdRewardLocation(),
        RoseWaySwingingPlatformRoomLocation: RoseWaySwingingPlatformRoomLocation(),
        RoseWayLeftIslandLocation: RoseWayLeftIslandLocation(),
        RoseWayMiddleIslandLocation: RoseWayMiddleIslandLocation(),
        RoseWayCoin1Location: RoseWayCoin1Location(),
        RoseWayCoin2Location: RoseWayCoin2Location(),
        RoseWayCoin3Location: RoseWayCoin3Location(),
        RoseWayCoin4Location: RoseWayCoin4Location(),
        RoseWayCoin5Location: RoseWayCoin5Location(),
        RoseWayFiveChestRoomTopLocation: RoseWayFiveChestRoomTopLocation(),
        RoseWayFiveChestRoomBottomLeftLocation: RoseWayFiveChestRoomBottomLeftLocation(),
        RoseWayFiveChestRoomRightLocation: RoseWayFiveChestRoomRightLocation(),
        RoseWayFiveChestRoomLeftLocation: RoseWayFiveChestRoomLeftLocation(),
        RoseWayFiveChestRoomBottomRightLocation: RoseWayFiveChestRoomBottomRightLocation(),
        RoseTownShopLeftChestLocation: RoseTownShopLeftChestLocation(),
        RoseTownShopRightChestLocation: RoseTownShopRightChestLocation(),
        RoseTownCloudRightChestLocation: RoseTownCloudRightChestLocation(),
        RoseTownCloudLeftChestLocation: RoseTownCloudLeftChestLocation(),
        RoseTownInnToadPrizeLocation: RoseTownInnToadPrizeLocation(),
        RoseTownInnGazPrizeLocation: RoseTownInnGazPrizeLocation(),
        RoseTownTreasureHouseLeftChestLocation: RoseTownTreasureHouseLeftChestLocation(),
        RoseTownTreasureHouseRightChestLocation: RoseTownTreasureHouseRightChestLocation(),
        RoseTownTreasureHouseMazeRewardLocation: RoseTownTreasureHouseMazeRewardLocation(),
        RoseTownTreasureHouseUpperChestLocation: RoseTownTreasureHouseUpperChestLocation(),
        ForestMazeFirstRoomLocation: ForestMazeFirstRoomLocation(),
        ForestMazeFirstUndergroundExitLocation: ForestMazeFirstUndergroundExitLocation(),
        ForestMazeUndergroundWigglerChestLocation: ForestMazeUndergroundWigglerChestLocation(),
        ForestMazeUndergroundBottomRightTrunkChestLocation: ForestMazeUndergroundBottomRightTrunkChestLocation(),
        ForestMazeUndergroundMiddleLeftChestLocation: ForestMazeUndergroundMiddleLeftChestLocation(),
        ForestMazeInnerMazeEntranceLocation: ForestMazeInnerMazeEntranceLocation(),
        ForestMazeSecretTopRightChestLocation: ForestMazeSecretTopRightChestLocation(),
        ForestMazeSecretBottomRightChestLocation: ForestMazeSecretBottomRightChestLocation(),
        ForestMazeSecretTopMiddleChestLocation: ForestMazeSecretTopMiddleChestLocation(),
        ForestMazeSecretBottomMiddleChestLocation: ForestMazeSecretBottomMiddleChestLocation(),
        ForestMazeSecretLeftChestLocation: ForestMazeSecretLeftChestLocation(),
        ForestMazeBossFight: ForestMazeBossFight(),
        ForestMazeStarPiece: ForestMazeStarPiece(),
        ForestMazeCharacter: ForestMazeCharacter(),
        PipeVaultSlidingCoinRoomBackChestLocation: PipeVaultSlidingCoinRoomBackChestLocation(),
        PipeVaultSlidingCoinRoomMiddleChestLocation: PipeVaultSlidingCoinRoomMiddleChestLocation(),
        PipeVaultSlidingCoinRoomFrontChestLocation: PipeVaultSlidingCoinRoomFrontChestLocation(),
        PipeVaultSlidingCoinRoomCoin1Location: PipeVaultSlidingCoinRoomCoin1Location(),
        PipeVaultSlidingCoinRoomCoin2Location: PipeVaultSlidingCoinRoomCoin2Location(),
        PipeVaultSlidingCoinRoomCoin3Location: PipeVaultSlidingCoinRoomCoin3Location(),
        PipeVaultSlidingCoinRoomCoin4Location: PipeVaultSlidingCoinRoomCoin4Location(),
        PipeVaultSlidingCoinRoomCoin5Location: PipeVaultSlidingCoinRoomCoin5Location(),
        PipeVaultSlidingCoinRoomCrouchItemLocation: PipeVaultSlidingCoinRoomCrouchItemLocation(),
        PipeVaultGoombaThumpinFirstPrizeLocation: PipeVaultGoombaThumpinFirstPrizeLocation(),
        PipeVaultGoombaThumpinSecondPrizeLocation: PipeVaultGoombaThumpinSecondPrizeLocation(),
        PipeVaultRisingPlatformChestLocation: PipeVaultRisingPlatformChestLocation(),
        PipeVaultChompweedChestLocation: PipeVaultChompweedChestLocation(),
        YosterEntranceChestLocation: YosterEntranceChestLocation(),
        YosterRacePrize1Location: YosterRacePrize1Location(),
        YosterRacePrize2Location: YosterRacePrize2Location(),
        YosterRacePrize3Location: YosterRacePrize3Location(),
        BucketGirlRewardLocation: BucketGirlRewardLocation(),
        TreasureShopItem1: TreasureShopItem1(),
        TreasureShopItem2: TreasureShopItem2(),
        TreasureShopItem3: TreasureShopItem3(),
        OuterMinesTrampolineHenchmanLocation: OuterMinesTrampolineHenchmanLocation(),
        OuterMinesLeftHenchmanLocation: OuterMinesLeftHenchmanLocation(),
        OuterMinesRightHenchmanLocation: OuterMinesRightHenchmanLocation(),
        OuterMinesBossPrizeLocation: OuterMinesBossPrizeLocation(),
        OuterMinesBossFight: OuterMinesBossFight(),
        OuterMinesStarPiece: OuterMinesStarPiece(),
        InnerMinesTracksChestLocation: InnerMinesTracksChestLocation(),
        InnerMinesShyguyCartLocation: InnerMinesShyguyCartLocation(),
        InnerMinesBoxesChestLocation: InnerMinesBoxesChestLocation(),
        InnerMinesSaveBlockChestLocation: InnerMinesSaveBlockChestLocation(),
        InnerMinesHighUpChestLocation: InnerMinesHighUpChestLocation(),
        InnerMinesBossFight: InnerMinesBossFight(),
        InnerMinesStarPiece: InnerMinesStarPiece(),
        InnerMinesCharacter: InnerMinesCharacter(),
        BoosterPassBushLocation: BoosterPassBushLocation(),
        BoosterPassFirstRoomLeftChestLocation: BoosterPassFirstRoomLeftChestLocation(),
        BoosterPassFirstRoomRightChestLocation: BoosterPassFirstRoomRightChestLocation(),
        BoosterPassSecondRoomFlowerLocation: BoosterPassSecondRoomFlowerLocation(),
        BoosterPassSecretMiddleChestLocation: BoosterPassSecretMiddleChestLocation(),
        BoosterPassSecretRightChestLocation: BoosterPassSecretRightChestLocation(),
        BoosterPassSecretLeftChestLocation: BoosterPassSecretLeftChestLocation(),
        BoosterTowerSpookumStairsLocation: BoosterTowerSpookumStairsLocation(),
        BoosterTowerTrainRoomCreviceLocation: BoosterTowerTrainRoomCreviceLocation(),
        BoosterTowerChestNearThwompLocation: BoosterTowerChestNearThwompLocation(),
        BoosterTowerFallingChestLocation: BoosterTowerFallingChestLocation(),
        BoosterTowerKnifeGuyPrizeLocation: BoosterTowerKnifeGuyPrizeLocation(),
        BoosterTowerPortraitPrizeLocation: BoosterTowerPortraitPrizeLocation(),
        BoosterTowerElderKeyItemLocation: BoosterTowerElderKeyItemLocation(),
        BoosterTowerParachuteRoomChestLocation: BoosterTowerParachuteRoomChestLocation(),
        BoosterTowerParachuteRoomCreviceLocation: BoosterTowerParachuteRoomCreviceLocation(),
        BoosterTowerCheckerboardRightmostItemLocation: BoosterTowerCheckerboardRightmostItemLocation(),
        BoosterTowerCheckerboardTopItemLocation: BoosterTowerCheckerboardTopItemLocation(),
        BoosterTowerCheckerboardLeftmostItemLocation: BoosterTowerCheckerboardLeftmostItemLocation(),
        BoosterTowerCheckerboardUpperRightItemLocation: BoosterTowerCheckerboardUpperRightItemLocation(),
        BoosterTowerCheckerboardBottomItemLocation: BoosterTowerCheckerboardBottomItemLocation(),
        BoosterTowerCheckerboardCoin1Location: BoosterTowerCheckerboardCoin1Location(),
        BoosterTowerCheckerboardCoin2Location: BoosterTowerCheckerboardCoin2Location(),
        BoosterTowerCheckerboardCoin3Location: BoosterTowerCheckerboardCoin3Location(),
        BoosterTowerCheckerboardCoin4Location: BoosterTowerCheckerboardCoin4Location(),
        BoosterTowerCheckerboardCoin5Location: BoosterTowerCheckerboardCoin5Location(),
        BoosterTowerCheckerboardCoin6Location: BoosterTowerCheckerboardCoin6Location(),
        BoosterTowerCheckerboardCoin7Location: BoosterTowerCheckerboardCoin7Location(),
        BoosterTowerCheckerboardCoin8Location: BoosterTowerCheckerboardCoin8Location(),
        BoosterTowerCheckerboardCoin9Location: BoosterTowerCheckerboardCoin9Location(),
        BoosterTowerRoomKeyChestLocation: BoosterTowerRoomKeyChestLocation(),
        BoosterTowerTopFloorLowerChestLocation: BoosterTowerTopFloorLowerChestLocation(),
        BoosterTowerTopFloorUpperChestLocation: BoosterTowerTopFloorUpperChestLocation(),
        BoosterTowerTopFloorCornerChestLocation: BoosterTowerTopFloorCornerChestLocation(),
        BoosterTowerCurtainGamePrizeLocation: BoosterTowerCurtainGamePrizeLocation(),
        BoosterTowerIndoorBossFight: BoosterTowerIndoorBossFight(),
        BoosterTowerIndoorStarPiece: BoosterTowerIndoorStarPiece(),
        BoosterTowerBalconyBossFight: BoosterTowerBalconyBossFight(),
        BoosterTowerBalconyStarPiece: BoosterTowerBalconyStarPiece(),
        BoosterHillGuaranteedItem1: BoosterHillGuaranteedItem1(),
        BoosterHillGuaranteedItem2: BoosterHillGuaranteedItem2(),
        BoosterHillGuaranteedItem3: BoosterHillGuaranteedItem3(),
        BoosterHillGuaranteedItem4: BoosterHillGuaranteedItem4(),
        BoosterHillGuaranteedItem5: BoosterHillGuaranteedItem5(),
        BoosterHillGuaranteedItem6: BoosterHillGuaranteedItem6(),
        BoosterHillGuaranteedItem7: BoosterHillGuaranteedItem7(),
        BoosterHillGuaranteedItem8: BoosterHillGuaranteedItem8(),
        BoosterHillGuaranteedItem9: BoosterHillGuaranteedItem9(),
        BoosterHillGuaranteedItem10: BoosterHillGuaranteedItem10(),
        BoosterHillGuaranteedItem11: BoosterHillGuaranteedItem11(),
        BoosterHillGuaranteedItem12: BoosterHillGuaranteedItem12(),
        BoosterHillGuaranteedItem13: BoosterHillGuaranteedItem13(),
        BoosterHillGuaranteedItem14: BoosterHillGuaranteedItem14(),
        BoosterHillGuaranteedItem15: BoosterHillGuaranteedItem15(),
        BoosterHillGuaranteedItem16: BoosterHillGuaranteedItem16(),
        MarrymoreFirstSuitePrizeLocation: MarrymoreFirstSuitePrizeLocation(),
        MarrymoreSecondSuitePrizeLocation: MarrymoreSecondSuitePrizeLocation(),
        MarrymoreThirdSuitePrizeLocation: MarrymoreThirdSuitePrizeLocation(),
        MarrymoreFourthSuitePrizeLocation: MarrymoreFourthSuitePrizeLocation(),
        MarrymoreFifthSuitePrizeLocation: MarrymoreFifthSuitePrizeLocation(),
        MarrymoreSixthSuitePrizeLocation: MarrymoreSixthSuitePrizeLocation(),
        MarrymoreBigTipLocation: MarrymoreBigTipLocation(),
        MarrymoreHotelChestLocation: MarrymoreHotelChestLocation(),
        MarrymoreSnifit1Location: MarrymoreSnifit1Location(),
        MarrymoreSnifit2Location: MarrymoreSnifit2Location(),
        MarrymoreSnifit3Location: MarrymoreSnifit3Location(),
        MarrymoreAltarHeadLocation: MarrymoreAltarHeadLocation(),
        MarrymoreBossFight: MarrymoreBossFight(),
        MarrymoreBossFightStarPiece: MarrymoreBossFightStarPiece(),
        MarrymoreCharacter: MarrymoreCharacter(),
        StarHillStarPiece: StarHillStarPiece(),
        FrogDiscipleLocation2: FrogDiscipleLocation2(),
        FrogDiscipleLocation3: FrogDiscipleLocation3(),
        FrogDiscipleLocation4: FrogDiscipleLocation4(),
        FrogDiscipleLocation5: FrogDiscipleLocation5(),
        SeasideBeachBossFight: SeasideBeachBossFight(),
        SeasideBeachStarPiece: SeasideBeachStarPiece(),
        SeasideTownBossPrizeLocation: SeasideTownBossPrizeLocation(),
        SeasideTownShedRescueLocation: SeasideTownShedRescueLocation(),
        SeaStarslapRoomChestLocation: SeaStarslapRoomChestLocation(),
        SeaSaveRoomBackChestLocation: SeaSaveRoomBackChestLocation(),
        SeaSaveRoomMiddleChestLocation: SeaSaveRoomMiddleChestLocation(),
        SeaSaveRoomFrontChestLocation: SeaSaveRoomFrontChestLocation(),
        SeaWhirlpoolChestLocation: SeaWhirlpoolChestLocation(),
        ShipRatStairsChestLocation: ShipRatStairsChestLocation(),
        ShipRatStairsBoxesLocation: ShipRatStairsBoxesLocation(),
        ShipTroopaPuzzleLocation: ShipTroopaPuzzleLocation(),
        ShipTrampolinePuzzle: ShipTrampolinePuzzle(),
        Ship3DMazePuzzle: Ship3DMazePuzzle(),
        ShipShopChestLocation: ShipShopChestLocation(),
        ShipCoinSnakePuzzleLocation: ShipCoinSnakePuzzleLocation(),
        ShipCannonballPuzzle: ShipCannonballPuzzle(),
        ShipBarrelPuzzle: ShipBarrelPuzzle(),
        ShipPasswordBossFight: ShipPasswordBossFight(),
        ShipPasswordStarPiece: ShipPasswordStarPiece(),
        EarlyInnerShipLeftChestLocation: EarlyInnerShipLeftChestLocation(),
        EarlyInnerShipRightChestLocation: EarlyInnerShipRightChestLocation(),
        InnerShipCloneRoomChestLocation: InnerShipCloneRoomChestLocation(),
        InnerShipBehindBoxesChestLocation: InnerShipBehindBoxesChestLocation(),
        InnerShipSaveRoomLeftChestLocation: InnerShipSaveRoomLeftChestLocation(),
        InnerShipSaveRoomRightChestLocation: InnerShipSaveRoomRightChestLocation(),
        Mimic2DropRewardLocation: Mimic2DropRewardLocation(),
        Mimic2BossFight: Mimic2BossFight(),
        Mimic2StarPiece: Mimic2StarPiece(),
        Mimic2ReloadRewardLocation: Mimic2ReloadRewardLocation(),
        InnerShipFirstUnderwaterRoomBottomItemLocation: InnerShipFirstUnderwaterRoomBottomItemLocation(),
        InnerShipFirstUnderwaterRoomTopItemLocation: InnerShipFirstUnderwaterRoomTopItemLocation(),
        InnerShipFirstUnderwaterRoomLeftItemLocation: InnerShipFirstUnderwaterRoomLeftItemLocation(),
        InnerShipFirstUnderwaterRoomMiddleItemLocation: InnerShipFirstUnderwaterRoomMiddleItemLocation(),
        InnerShipSecretRoomChestLocation: InnerShipSecretRoomChestLocation(),
        InnerShipPoolRoomLocation: InnerShipPoolRoomLocation(),
        InnerShipBeforeBossChestLocation: InnerShipBeforeBossChestLocation(),
        ShipFinalBossFight: ShipFinalBossFight(),
        ShipFinalStarPiece: ShipFinalStarPiece(),
        LandsEndRisingPlatformChestLocation: LandsEndRisingPlatformChestLocation(),
        LandsEndChowPitStaticChestLocation: LandsEndChowPitStaticChestLocation(),
        LandsEndChowPitMovingChestLocation: LandsEndChowPitMovingChestLocation(),
        LandsEndBeeTowerChestLocation: LandsEndBeeTowerChestLocation(),
        LandsEndGrottoEntranceChestLocation: LandsEndGrottoEntranceChestLocation(),
        LandsEndGrottoCornerChestLocation: LandsEndGrottoCornerChestLocation(),
        LandsEndGrottoEndChestLocation: LandsEndGrottoEndChestLocation(),
        KeroSewersBeforeBelomeUpperAfterFlipLocation: KeroSewersBeforeBelomeUpperAfterFlipLocation(),
        LandsEndUndergroundSaveBoxChestLocation: LandsEndUndergroundSaveBoxChestLocation(),
        LandsEndFirstPurchasableChestLocation: LandsEndFirstPurchasableChestLocation(),
        LandsEndSecondPurchasableChestLocation: LandsEndSecondPurchasableChestLocation(),
        TroopaClimbSub12PrizeLocation: TroopaClimbSub12PrizeLocation(),
        LandsEndCloudBoss: LandsEndCloudBoss(),
        LandsEndCloudStarPiece: LandsEndCloudStarPiece(),
        BelomeTempleFortuneTellerLocation: BelomeTempleFortuneTellerLocation(),
        BelomeTempleLMRChestLocation: BelomeTempleLMRChestLocation(),
        BelomeTempleLRMChestLocation: BelomeTempleLRMChestLocation(),
        BelomeTempleRLMChestLocation: BelomeTempleRLMChestLocation(),
        BelomeTempleRMLChestLocation: BelomeTempleRMLChestLocation(),
        BelomeBeforeBossRightChestLocation: BelomeBeforeBossRightChestLocation(),
        BelomeBeforeBossLowerLeftChestLocation: BelomeBeforeBossLowerLeftChestLocation(),
        BelomeBeforeBossMiddleChestLocation: BelomeBeforeBossMiddleChestLocation(),
        BelomeBeforeBossUpperLeftChestLocation: BelomeBeforeBossUpperLeftChestLocation(),
        BelomeTempleTreasuryUpperCornerLeftItemLocation: BelomeTempleTreasuryUpperCornerLeftItemLocation(),
        BelomeTempleTreasuryUpperCornerLowerLeftItemLocation: BelomeTempleTreasuryUpperCornerLowerLeftItemLocation(),
        BelomeTempleTreasuryUpperCornerTopItemLocation: BelomeTempleTreasuryUpperCornerTopItemLocation(),
        BelomeTempleTreasuryTopmostItemLocation: BelomeTempleTreasuryTopmostItemLocation(),
        BelomeTempleTreasuryMidLeftItemLocation: BelomeTempleTreasuryMidLeftItemLocation(),
        BelomeTempleTreasuryAlmostTopItemLocation: BelomeTempleTreasuryAlmostTopItemLocation(),
        BelomeTempleTreasuryAlmostLeftmostItemLocation: BelomeTempleTreasuryAlmostLeftmostItemLocation(),
        BelomeTempleTreasuryOuterUpperRightItemLocation: BelomeTempleTreasuryOuterUpperRightItemLocation(),
        BelomeTempleTreasuryInnerUpperRightItemLocation: BelomeTempleTreasuryInnerUpperRightItemLocation(),
        BelomeTempleTreasuryLowestItemsRightLocation: BelomeTempleTreasuryLowestItemsRightLocation(),
        BelomeTempleTreasuryLowerOuterBottomRightItemLocation: BelomeTempleTreasuryLowerOuterBottomRightItemLocation(),
        BelomeTempleTreasuryRightmostItemLocation: BelomeTempleTreasuryRightmostItemLocation(),
        BelomeTempleTreasuryBottomLeftCornerItemLocation: BelomeTempleTreasuryBottomLeftCornerItemLocation(),
        BelomeTempleTreasuryLowestItemsLeftLocation: BelomeTempleTreasuryLowestItemsLeftLocation(),
        BelomeTempleTreasuryUpperOuterBottomRightItemLocation: BelomeTempleTreasuryUpperOuterBottomRightItemLocation(),
        TempleBossFight: TempleBossFight(),
        TempleBossFightStarPiece: TempleBossFightStarPiece(),
        MonstroEntranceLocation: MonstroEntranceLocation(),
        MonstroThwompItemLocation: MonstroThwompItemLocation(),
        DojoFirstFight: DojoFirstFight(),
        DojoFirstFightStarPiece: DojoFirstFightStarPiece(),
        DojoSecondFight: DojoSecondFight(),
        DojoSecondFightStarPiece: DojoSecondFightStarPiece(),
        DojoThirdFight: DojoThirdFight(),
        DojoThirdFightStarPiece: DojoThirdFightStarPiece(),
        DojoFourthFight: DojoFourthFight(),
        DojoFourthFightStarPiece: DojoFourthFightStarPiece(),
        MonstroDojoClearRewardLocation: MonstroDojoClearRewardLocation(),
        MonstroSealedDoorBossFight: MonstroSealedDoorBossFight(),
        MonstroFlagExchangeLocation: MonstroFlagExchangeLocation(),
        BeanValleyFirstDeadEndLocation: BeanValleyFirstDeadEndLocation(),
        BeanValleyFirstProgressChestLocation: BeanValleyFirstProgressChestLocation(),
        BeanValleyLeftPiranhaPipeLocation: BeanValleyLeftPiranhaPipeLocation(),
        BeanValleyBottomLeftPiranhaPipeLocation: BeanValleyBottomLeftPiranhaPipeLocation(),
        BeanValleyBottomRightPiranhaPipeUpperLocation: BeanValleyBottomRightPiranhaPipeUpperLocation(),
        BeanValleyBottomRightPiranhaPipeLowerLocation: BeanValleyBottomRightPiranhaPipeLowerLocation(),
        BeanValleyRightPipeLeftChestLocation: BeanValleyRightPipeLeftChestLocation(),
        Mimic3BossFight: Mimic3BossFight(),
        Mimic3StarPiece: Mimic3StarPiece(),
        BeanValleyRightPipeRightChestLocation: BeanValleyRightPipeRightChestLocation(),
        BeanValleyRightPipeUnderStairsLocation: BeanValleyRightPipeUnderStairsLocation(),
        BeanValleyRightPipeAboveGroundLocation: BeanValleyRightPipeAboveGroundLocation(),
        BeanValleyPlanterBossFight: BeanValleyPlanterBossFight(),
        BeanValleyPlanterStarPiece: BeanValleyPlanterStarPiece(),
        BeanValleyBossNoteLocation: BeanValleyBossNoteLocation(),
        BeanstalkLowestChestLocation: BeanstalkLowestChestLocation(),
        BeanValley1stRoomFloatingItemLocation: BeanValley1stRoomFloatingItemLocation(),
        BeanValley1stRoomMiddleCoinLocation: BeanValley1stRoomMiddleCoinLocation(),
        BeanValley1stRoomUpperCoinLocation: BeanValley1stRoomUpperCoinLocation(),
        BeanValley1stRoomLowerCoinLocation: BeanValley1stRoomLowerCoinLocation(),
        Beanstalk2ndRoomFloatingItemLocation: Beanstalk2ndRoomFloatingItemLocation(),
        Beanstalk2ndRoomCoin1Location: Beanstalk2ndRoomCoin1Location(),
        Beanstalk2ndRoomCoin2Location: Beanstalk2ndRoomCoin2Location(),
        Beanstalk2ndRoomCoin3Location: Beanstalk2ndRoomCoin3Location(),
        BeanValleyEastBeanstalkCoin1Location: BeanValleyEastBeanstalkCoin1Location(),
        BeanValleyEastBeanstalkCoin2Location: BeanValleyEastBeanstalkCoin2Location(),
        BeanValleyEastBeanstalkCoin3Location: BeanValleyEastBeanstalkCoin3Location(),
        BeanValleyEastBeanstalkCoin4Location: BeanValleyEastBeanstalkCoin4Location(),
        BeanValleyEastBeanstalkCoin5Location: BeanValleyEastBeanstalkCoin5Location(),
        BeanValleyWestBeanstalkCoin1Location: BeanValleyWestBeanstalkCoin1Location(),
        BeanValleyWestBeanstalkCoin2Location: BeanValleyWestBeanstalkCoin2Location(),
        BeanValleyWestBeanstalkCoin3Location: BeanValleyWestBeanstalkCoin3Location(),
        BeanValleyWestBeanstalkFloatingItemLocation: BeanValleyWestBeanstalkFloatingItemLocation(),
        BeanstalkUpperCloudLeftChestLocation: BeanstalkUpperCloudLeftChestLocation(),
        BeanstalkUpperCloudRightChestLocation: BeanstalkUpperCloudRightChestLocation(),
        BeanstalkLowerCloudLeftChestLocation: BeanstalkLowerCloudLeftChestLocation(),
        BeanstalkLowerCloudRightChestLocation: BeanstalkLowerCloudRightChestLocation(),
        CasinoGrateGuyPrizeLocation: CasinoGrateGuyPrizeLocation(),
        NimbusShopChestLocation: NimbusShopChestLocation(),
        NimbusInnDreamPrize1Location: NimbusInnDreamPrize1Location(),
        NimbusInnDreamPrize2Location: NimbusInnDreamPrize2Location(),
        NimbusCastleStatueGamePrizeLocation: NimbusCastleStatueGamePrizeLocation(),
        StatueRoomBossFight: StatueRoomBossFight(),
        StatueRoomStarPiece: StatueRoomStarPiece(),
        NimbusCastleOuterPrisonCellarRightNPCLocation: NimbusCastleOuterPrisonCellarRightNPCLocation(),
        NimbusCastleOuterPrisonCellarLeftNPCLocation: NimbusCastleOuterPrisonCellarLeftNPCLocation(),
        NimbusCastleBusinessCentreOccupiedChestLocation: NimbusCastleBusinessCentreOccupiedChestLocation(),
        NimbusCastleCornerBridgeChestLocation: NimbusCastleCornerBridgeChestLocation(),
        NimbusCastleOutOfBoundsChestLocation: NimbusCastleOutOfBoundsChestLocation(),
        NimbusCastleAboveJawfulChestLocation: NimbusCastleAboveJawfulChestLocation(),
        NimbusCastleSingleGoldBirdChestLocation: NimbusCastleSingleGoldBirdChestLocation(),
        NimbusCastleTwoLevelLowerChestLocation: NimbusCastleTwoLevelLowerChestLocation(),
        GiantEggBossFight: GiantEggBossFight(),
        GiantEggStarPiece: GiantEggStarPiece(),
        NimbusCastleGiantEggRewardLocation: NimbusCastleGiantEggRewardLocation(),
        NimbusCastleTwoLevelUpperChestLocation: NimbusCastleTwoLevelUpperChestLocation(),
        NimbusCastleBackHallwayOccupiedChestLocation: NimbusCastleBackHallwayOccupiedChestLocation(),
        NimbusFinalBossFight: NimbusFinalBossFight(),
        NimbusFinalStarPiece: NimbusFinalStarPiece(),
        NimbusCastleBackHallwayLiberatedChestLocation: NimbusCastleBackHallwayLiberatedChestLocation(),
        NimbusCastleBusinessCentreLiberatedChestLocation: NimbusCastleBusinessCentreLiberatedChestLocation(),
        NimbusLandRightSideLocation: NimbusLandRightSideLocation(),
        NimbusLandCrocoItemLocation: NimbusLandCrocoItemLocation(),
        NimbusLandInnerCellarLocation: NimbusLandInnerCellarLocation(),
        VolcanoLavaCoveLeftChestLocation: VolcanoLavaCoveLeftChestLocation(),
        VolcanoLavaCoveRightChestLocation: VolcanoLavaCoveRightChestLocation(),
        VolcanoEarlyProgressChestLeftLocation: VolcanoEarlyProgressChestLeftLocation(),
        VolcanoEarlyProgressChestRightLocation: VolcanoEarlyProgressChestRightLocation(),
        VolcanoEarlyProgressThirdChestLocation: VolcanoEarlyProgressThirdChestLocation(),
        VolcanoLavaPoolLocation: VolcanoLavaPoolLocation(),
        VolcanoReverseRecoilItemLocation: VolcanoReverseRecoilItemLocation(),
        VolcanoRightDonutItemLocation: VolcanoRightDonutItemLocation(),
        VolcanoLeftDonutItemLocation: VolcanoLeftDonutItemLocation(),
        VolcanoSaveRoomLowerChestLocation: VolcanoSaveRoomLowerChestLocation(),
        VolcanoSaveRoomUpperChestLocation: VolcanoSaveRoomUpperChestLocation(),
        VolcanoShopEntranceChestLocation: VolcanoShopEntranceChestLocation(),
        VolcanoBridgeBossFight: VolcanoBridgeBossFight(),
        VolcanoBridgeStarPiece: VolcanoBridgeStarPiece(),
        VolcanoExitBossFight: VolcanoExitBossFight(),
        VolcanoExitStarPiece: VolcanoExitStarPiece(),
        KeepDarkRoomChestLocation: KeepDarkRoomChestLocation(),
        KeepFirstCrocoShopLeftChestLocation: KeepFirstCrocoShopLeftChestLocation(),
        KeepFirstCrocoShopRightChestLocation: KeepFirstCrocoShopRightChestLocation(),
        KeepInvisibleBridgeFrontChestLocation: KeepInvisibleBridgeFrontChestLocation(),
        KeepInvisibleBridgeRightChestLocation: KeepInvisibleBridgeRightChestLocation(),
        KeepInvisibleBridgeLeftChestLocation: KeepInvisibleBridgeLeftChestLocation(),
        KeepInvisibleBridgeBackChestLocation: KeepInvisibleBridgeBackChestLocation(),
        KeepInvisibleBridgeCoin1Location: KeepInvisibleBridgeCoin1Location(),
        KeepInvisibleBridgeCoin2Location: KeepInvisibleBridgeCoin2Location(),
        KeepInvisibleBridgeCoin3Location: KeepInvisibleBridgeCoin3Location(),
        KeepInvisibleBridgeCoin4Location: KeepInvisibleBridgeCoin4Location(),
        KeepXYPlatformsBackLeftChestLocation: KeepXYPlatformsBackLeftChestLocation(),
        KeepXYPlatformsFrontLeftChestLocation: KeepXYPlatformsFrontLeftChestLocation(),
        KeepXYPlatformsFrontRightChestLocation: KeepXYPlatformsFrontRightChestLocation(),
        KeepXYPlatformsBackRightChestLocation: KeepXYPlatformsBackRightChestLocation(),
        KeepElevatorRoomChestLocation: KeepElevatorRoomChestLocation(),
        KeepCannonballRoomFrontRightChestLocation: KeepCannonballRoomFrontRightChestLocation(),
        KeepCannonballRoomBackChestLocation: KeepCannonballRoomBackChestLocation(),
        KeepCannonballFrontLeftChestLocation: KeepCannonballFrontLeftChestLocation(),
        KeepCannonballMidRightChestLocation: KeepCannonballMidRightChestLocation(),
        KeepCannonballMidLeftChestLocation: KeepCannonballMidLeftChestLocation(),
        KeepCannonballCoin1Location: KeepCannonballCoin1Location(),
        KeepCannonballCoin2Location: KeepCannonballCoin2Location(),
        KeepCannonballCoin3Location: KeepCannonballCoin3Location(),
        KeepCannonballCoin4Location: KeepCannonballCoin4Location(),
        KeepCannonballCoin5Location: KeepCannonballCoin5Location(),
        KeepCannonballCoin6Location: KeepCannonballCoin6Location(),
        KeepCannonballCoin7Location: KeepCannonballCoin7Location(),
        KeepCannonballCoin8Location: KeepCannonballCoin8Location(),
        KeepRotatingPlatformsFrontChestLocation: KeepRotatingPlatformsFrontChestLocation(),
        KeepRotatingPlatformsFrontMidLeftChestLocation: KeepRotatingPlatformsFrontMidLeftChestLocation(),
        KeepRotatingPlatformsBackMidRightChestLocation: KeepRotatingPlatformsBackMidRightChestLocation(),
        KeepRotatingPlatformsFrontMidRightChestLocation: KeepRotatingPlatformsFrontMidRightChestLocation(),
        KeepRotatingPlatformsBackMidLeftChestLocation: KeepRotatingPlatformsBackMidLeftChestLocation(),
        KeepRotatingPlatformsBackChestLocation: KeepRotatingPlatformsBackChestLocation(),
        ObstacleCourseFinalFight: ObstacleCourseFinalFight(),
        ObstacleCourseFinalFightStarPiece: ObstacleCourseFinalFightStarPiece(),
        KeepDoorRewardChest1Location: KeepDoorRewardChest1Location(),
        KeepDoorRewardChest2Location: KeepDoorRewardChest2Location(),
        KeepDoorRewardChest3Location: KeepDoorRewardChest3Location(),
        KeepDoorRewardChest4Location: KeepDoorRewardChest4Location(),
        KeepDoorRewardChest5Location: KeepDoorRewardChest5Location(),
        KeepDoorRewardChest6Location: KeepDoorRewardChest6Location(),
        KeepAfterObstaclesBossFight: KeepAfterObstaclesBossFight(),
        KeepAfterObstaclesStarPiece: KeepAfterObstaclesStarPiece(),
        KeepAfterObstaclesBossChestLocation: KeepAfterObstaclesBossChestLocation(),
        KeepChandelierBossFight: KeepChandelierBossFight(),
        KeepChandelierStarPiece: KeepChandelierStarPiece(),
        KeepFinalBossFight: KeepFinalBossFight(),
        KeepFinalStarPiece: KeepFinalStarPiece(),
        OuterFactorySaveRoomChestLocation: OuterFactorySaveRoomChestLocation(),
        FactoryBoltPlatformsChestLocation: FactoryBoltPlatformsChestLocation(),
        FactoryEntranceBossFight: FactoryEntranceBossFight(),
        FactoryEntranceStarPiece: FactoryEntranceStarPiece(),
        FactoryAxemConveyorsChestLocation: FactoryAxemConveyorsChestLocation(),
        FactoryTreasurePitBackChestLocation: FactoryTreasurePitBackChestLocation(),
        FactoryTreasurePitFrontChestLocation: FactoryTreasurePitFrontChestLocation(),
        FactoryBigConveyorRoomFirstChestLocation: FactoryBigConveyorRoomFirstChestLocation(),
        FactoryBigConveyorRoomSecondChestLocation: FactoryBigConveyorRoomSecondChestLocation(),
        FactoryBehindNinjasRightChestLocation: FactoryBehindNinjasRightChestLocation(),
        FactoryBehindNinjasLeftChestLocation: FactoryBehindNinjasLeftChestLocation(),
        FactoryTransitionBossFight: FactoryTransitionBossFight(),
        FactoryTransitionStarPiece: FactoryTransitionStarPiece(),
        InnerFactoryFirstFight: InnerFactoryFirstFight(),
        InnerFactoryFirstFightStarPiece: InnerFactoryFirstFightStarPiece(),
        InnerFactoryToadGiftLocation: InnerFactoryToadGiftLocation(),
        InnerFactorySecondFight: InnerFactorySecondFight(),
        InnerFactorySecondFightStarPiece: InnerFactorySecondFightStarPiece(),
        InnerFactoryThirdFight: InnerFactoryThirdFight(),
        InnerFactoryThirdFightStarPiece: InnerFactoryThirdFightStarPiece(),
        InnerFactoryFourthFight: InnerFactoryFourthFight(),
        InnerFactoryFourthFightStarPiece: InnerFactoryFourthFightStarPiece(),
        FinalBossFight: FinalBossFight(),
    }
    if not world.settings.is_flag_value(WinCondition, WinConditions.SEALED):
        world.locations[MonstroSealedDoorStarPiece] = MonstroSealedDoorStarPiece()
        world.locations[MonstroSealedDoorClearRewardLocation] = MonstroSealedDoorClearRewardLocation()

    

    # SeeYa removes SeeYaPrize (Frog Disciple 1's item). The shop only shrinks to
    # 4 items when it is NOT fully shuffled: if BOTH shops and items are shuffled
    # the pool has a surplus, so the 5th slot fills normally and all 5 locations
    # must stay. Only drop FrogDiscipleLocation1 when SeeYa is on and the shop is
    # effectively unshuffled (shops off OR items off). This predicate MUST match
    # the FROG_DISCIPLE_ITEM_5_PURCHASED sale-bit condition in gameworld.py - a
    # 4-item shop with the bit unset opens a glitched empty menu.
    frog_shop_reduced = world.settings.isflag_enabled(SeeYa) and not (
        world.settings.isflag_enabled(ShuffleShops)
        and world.settings.isflag_enabled(ShuffleItems)
    )
    if not frog_shop_reduced:
        world.locations[FrogDiscipleLocation1] = FrogDiscipleLocation1()


    # Always register FinalBossFightStarPiece so its vanilla StarPiece7 seeds the pool
    # in every win condition. Under FACTORY the location is source-only: its can_accept
    # rejects all prizes (defeating the final boss ends the game, so a star piece placed
    # here could never be collected), and StarPiece7 gets shuffled to a collectible spot.
    world.locations[FinalBossFightStarPiece] = FinalBossFightStarPiece()

    # Add spell slot locations for all included characters
    # (needed for vanilla placement, CharacterLearnedSpells shuffling, or SpellsAnywhere pooling)
    included_charaters = [m.value for m in world.settings.get_flag(AvailableCharacters).enabled]
    if MARIO_Ally in included_charaters:
        world.locations = {
            **world.locations,
            MarioSpell1: MarioSpell1(),
            MarioSpell2: MarioSpell2(),
            MarioSpell3: MarioSpell3(),
            MarioSpell4: MarioSpell4(),
            MarioSpell5: MarioSpell5(),
            MarioSpell6: MarioSpell6(),
        }
    if MALLOW_Ally in included_charaters:
        world.locations = {
            **world.locations,
            MallowSpell1: MallowSpell1(),
            MallowSpell2: MallowSpell2(),
            MallowSpell3: MallowSpell3(),
            MallowSpell4: MallowSpell4(),
            MallowSpell5: MallowSpell5(),
            MallowSpell6: MallowSpell6(),
        }
    if GENO_Ally in included_charaters:
        world.locations = {
            **world.locations,
            GenoSpell1: GenoSpell1(),
            GenoSpell2: GenoSpell2(),
            GenoSpell3: GenoSpell3(),
            GenoSpell4: GenoSpell4(),
            GenoSpell5: GenoSpell5(),
            GenoSpell6: GenoSpell6(),
        }
    if BOWSER_Ally in included_charaters:
        world.locations = {
            **world.locations,
            BowserSpell1: BowserSpell1(),
            BowserSpell2: BowserSpell2(),
            BowserSpell3: BowserSpell3(),
            BowserSpell4: BowserSpell4(),
            BowserSpell5: BowserSpell5(),
            BowserSpell6: BowserSpell6(),
        }
    if TOADSTOOL_Ally in included_charaters:
        world.locations = {
            **world.locations,
            ToadstoolSpell1: ToadstoolSpell1(),
            ToadstoolSpell2: ToadstoolSpell2(),
            ToadstoolSpell3: ToadstoolSpell3(),
            ToadstoolSpell4: ToadstoolSpell4(),
            ToadstoolSpell5: ToadstoolSpell5(),
            ToadstoolSpell6: ToadstoolSpell6(),
        }

    # NOTE: The two Monstro Super Jump reward locations are added later, in
    # shuffle_rules(), once the final character roster is known. In vanilla
    # learned-spell mode the feature only exists if Super Jump's learner (Mario)
    # is actually in the seed, which isn't decided until character selection.

    if world.settings.isflag_enabled(FixKnifeGuy):
        world.locations = {
            **world.locations,
            BoosterTowerKnifeGuy2PrizeLocation: BoosterTowerKnifeGuy2PrizeLocation(),
        }

    if world.settings.isflag_enabled(ShuffleCookies):
        world.locations = {
            **world.locations,
            YosterRaceCookieYoshiLocation: YosterRaceCookieYoshiLocation(),
        }

    if world.settings.isflag_enabled(ShuffleMarioDoll):
        world.locations = {
            **world.locations,
            BoosterTowerMarioDollLocation: BoosterTowerMarioDollLocation(),
        }


    if world.settings.is_flag_value(FireworksSetting, FireworksOptions.PROGRESSIVE):
        fwshop = FireworksShopItemLocation()
        fwshop._originally_held = ProgressiveFireworksPrize
        fwshop.set_prize(ProgressiveFireworksPrize())
        world.locations = {
            **world.locations,
            FireworksShopItemLocation: fwshop,
            PurtendStoreLocation: PurtendStoreLocation(),
            CookieTraderLocation: CookieTraderLocation(),
        }
        world.get_item(FireworksItem).set_price(0)
        world.get_item(ShinyStoneItem).set_price(0)
        world.get_item(CarboCookieItem).set_price(0)
    elif world.settings.is_flag_value(FireworksSetting, FireworksOptions.SHUFFLE_ONE):
        world.locations = {
            **world.locations,
            FireworksShopItemLocation: FireworksShopItemLocation(),
        }
        world.get_item(FireworksItem).set_price(0)
        world.get_item(ShinyStoneItem).set_price(0)
        world.get_item(CarboCookieItem).set_price(0)

    strchars = world.settings.get_flag(StartingCharacters)
    startmax = len(strchars.enabled)
    if startmax >= 2:
        world.locations = {
            **world.locations,
            StartingCharacter2: StartingCharacter2(),
        }
    if startmax >= 3:
        world.locations = {
            **world.locations,
            StartingCharacter3: StartingCharacter3(),
        }
    if startmax >= 4:
        world.locations = {
            **world.locations,
            StartingCharacter4: StartingCharacter4(),
        }
    if startmax >= 5:
        world.locations = {
            **world.locations,
            StartingCharacter5: StartingCharacter5(),
        }
    # The starter locations are deliberately left empty here. shuffle_prizes
    # clears every shuffled location's prize before it fills anything, so a prize
    # set at this point is discarded - and resolving the flag's Random_X slots
    # here would only burn RNG draws on a party the seed then throws away.

    if world.settings.is_flag_value(NimbusGate, NimbusGating.PAINT):
        world.locations = {
            **world.locations,
            GarroFreeItem: GarroFreeItem(),
        }

    # Optionally include remake content.
    if world.settings.get_flag(Remake).enabled:
        world.locations = {
            **world.locations,
            PostgameVoucherLocation: PostgameVoucherLocation(),
            MushroomWayLeftItemRemake: MushroomWayLeftItemRemake(),
            MushroomWayRightItemRemake: MushroomWayRightItemRemake(),
            InnerMinesPostgameBossFight: InnerMinesPostgameBossFight(),
            InnerMinesPostgameStarPiece: InnerMinesPostgameStarPiece(),
            InnerMinesPostgameDrop: InnerMinesPostgameDrop(),
            BoosterTowerIndoorBossFightRemake: BoosterTowerIndoorBossFightRemake(),
            BoosterTowerIndoorStarPieceRemake: BoosterTowerIndoorStarPieceRemake(),
            BoosterTowerRemakeBossFightPrizeLocation: BoosterTowerRemakeBossFightPrizeLocation(),
            MarrymoreBossFightRemake: MarrymoreBossFightRemake(),
            MarrymoreBossFightStarPieceRemake: MarrymoreBossFightStarPieceRemake(),
            MarrymoreBossFightRemakeItemDrop: MarrymoreBossFightRemakeItemDrop(),
            ShipPostgameBossFight: ShipPostgameBossFight(),
            ShipPostgameFightItemDrop: ShipPostgameFightItemDrop(),
            ShipPostgameStarPiece: ShipPostgameStarPiece(),
            TempleBossFightPostgame: TempleBossFightPostgame(),
            TempleBossFightStarPiecePostgame: TempleBossFightStarPiecePostgame(),
            TemplePostgameFightItemDrop: TemplePostgameFightItemDrop(),
            DojoFifthFight: DojoFifthFight(),
            DojoFifthFightStarPiece: DojoFifthFightStarPiece(),
            MonstroDojoPostgameClearRewardLocation: MonstroDojoPostgameClearRewardLocation(),
            LandsEndCaveSideRemake: LandsEndCaveSideRemake(),
        }
        # Only include Monstro sealed door postgame locations if win condition is not SEALED
        # (when SEALED is the win condition, defeating the sealed door boss ends the game
        # so there's no opportunity to collect postgame rewards)
        if not world.settings.is_flag_value(WinCondition, WinConditions.SEALED):
            world.locations[MonstroSealedDoorBossFightPostgame] = (
                MonstroSealedDoorBossFightPostgame()
            )
            world.locations[MonstroSealedDoorStarPiecePostgame] = (
                MonstroSealedDoorStarPiecePostgame()
            )
            world.locations[MonstroSealedDoorClearRewardLocationPostgame] = (
                MonstroSealedDoorClearRewardLocationPostgame()
            )
        room = world.rooms._rooms[R204_MUSHROOM_WAY_AREA_02]
        assert room is not None, f"Room {R204_MUSHROOM_WAY_AREA_02} not found"
        npc_10 = room.get_npc_by_target_id(NPC_10)
        assert npc_10 is not None, f"NPC_10 not found in room {R204_MUSHROOM_WAY_AREA_02}"
        npc_10.set_visible(True)
        npc_11 = room.get_npc_by_target_id(NPC_11)
        assert npc_11 is not None, f"NPC_11 not found in room {R204_MUSHROOM_WAY_AREA_02}"
        npc_11.set_visible(True)
        room = world.rooms._rooms[R142_LANDS_END_AREA_05_SKY_BRIDGE]
        assert room is not None, f"Room {R142_LANDS_END_AREA_05_SKY_BRIDGE} not found"
        npc_19 = room.get_npc_by_target_id(NPC_19)
        assert npc_19 is not None, f"NPC_19 not found in room {R142_LANDS_END_AREA_05_SKY_BRIDGE}"
        npc_19.set_visible(True)
    else:
        world.event_scripts.get_script_by_id(E0225_CHECK_VOUCHER_UNLOCK).set_contents([
            Return()
        ])


    invisible_item_pool = [
        MariosPadBedFlag,
        RoseTownSignFlag,
        YosterIsleGoalFlag,
        MariosPadSteamwhistleFlag,
        MariosPadLanternFlag,
        MariosPadHatFlag,
        MushroomWayTreeFlag,
        MushroomKingdomSignFlag,
        MushroomKingdomEmptyHouseFlag,
        ChancellorThroneFlag,
        BanditsWayFlowerFlag,
        KeroStairsFlag,
        KeroGateFlag,
        MidasTreesFlag,
        TadpoleCabinetFlag,
        RoseWayDirtPatchFlag,
        RoseTownHydrantFlag,
        RoseTownSinkFlag,
        RoseTownBowserFlag,
        RoseTownGardenerHydrantFlag,
        RoseTownGardenerBucketFlag,
        RoseTownGardenerLeafFlag,
        ForestMazeSecretStumpFlag,
        ForestMazeSecretMushroomsFlag,
        ForestMazeSecretWigglerFlag,
        PipeVaultExteriorFlag,
        PipeVaultRedPipeFlag,
        YosterIsleHutFlag,
        MolevilleHydrantFlag,
        MolevilleMountainBushFlag,
        MolevilleMountainGoFlag,
        MolevilleBedFlag,
        MolevilleMinesArrowsFlag,
        MolevilleMinesCeilingFlag,
        MolevilleMinesEntryFlag,
        BoosterPassCornerBushFlag,
        BoosterTowerExteriorSignFlag,
        BoosterTowerDeskFlag,
        BoosterTowerMasherRoomFlag,
        BoosterTowerCurtainFlag,
        BoosterTowerThwompInvisibleFlag,
        BoosterTowerBrokenFrameFlag,
        BoosterTowerBeetleCageFlag,
        BoosterTowerToyBoxFlag,
        MarrymoreOutsideCrateFlag,
        MarrymoreHallwayFlag,
        MarrymoreSuiteBedFlag,
        MarrymoreCurtains,
        MarrymoreKitchenFlag,
        MarrymoreFireplaceFlag,
        MarrymoreWindowFlag,
        MarrymoreOrganFlag,
        MarrymoreAltarFlag,
        StarHillNorthStarFlag,
        SeasideTownAnchorFlag,
        SeasideTownHydrantFlag,
        SeasideTownBucketFlag,
        SeasideTownFlowersFlag,
        SeasideTownShedBoxFlag,
        SeaArrowFlag,
        SeaBoxesFlag,
        SeaStalagnateFlag,
        SeaUnderwaterSailFlag,
        ShipBarrelPileFlag,
        ShipDoorMarkerFlag,
        ShipButtonFlag,
        ShipSwitchFlag,
        LandsEndPlatformFlag,
        LandsEndCannonFlag,
        LandsEndArrowFlag,
        LandsEndHillFlag,
        LandsEndTwoHillFlag,
        LandsEndStalagmiteFlag,
        LandsEndCliffBushFlag,
        LandsEndSignFlag,
        TempleShaftFlag,
        TempleShaftSwitchFlag,
        DojoBonsaiFlag,
        MonstroEntranceSignFlag,
        MonstroBatFlag,
        MonstroFanFlag,
        MonstroShellFlag,
        BeanValleyPipeFlag,
        BeanValleyBeanstalkBlockFlag,
        BeanValleyCloudsFlag,
        CasinoBellFlag,
        NimbusGoldGoombaFlag,
        NimbusInnLobbyFlag,
        NimbusPlantFlag,
        NimbusBirdFlag,
        NimbusHotSpringsFlag,
        NimbusOutdoorFlag,
        BarrelVolcanoStumpetFlag,
        BarrelVolcanoInnSignFlag,
        VolcanoShipsFlag,
        VolcanoBedFlag,
        VolcanoLampFlag,
        KeepPostObstacleBossRoomFlag,
        KeepThwompFlag,
        FactoryLugnutFlag,
        FactoryTrampolineFlag,
        FactoryButtonFlag,
    ]

    # Pre-allocate dummy NPCs for deterministic object presence table layout.
    # Must be called after world.locations is populated but before invisible flag placement.
    _pre_allocate_dummy_npcs(world, invisible_item_pool)

    # reuse across retries: set_locations runs once per attempt and would otherwise duplicate these
    # reset the invisible flag summoner if a reroll needs to happen
    summoner = world.event_scripts.get_script_by_id(E0091_INVISIBLE_ITEM_SUMMONER)
    if world._invisible_summoner_base is None:
        world._invisible_summoner_base = deepcopy(summoner.contents)
    else:
        summoner.set_contents(deepcopy(world._invisible_summoner_base))

    if world._invisible_item_locations is not None:
        invisible_flag_locations = world._invisible_item_locations
    else:
        invisible_flag_locations = {}

        debug_invisible_flags: list[type] | None = None
        if world.settings.debug_mode:
            # Prize offset takes precedence over config.yml for invisible flags -
            # unless the invisible flag category is switched off in the offset UI,
            # in which case config.yml is back in charge and, failing that, the
            # flags shuffle normally.
            if (
                world.settings.prize_offset is not None
                and world.settings.offset_invisible_flags
            ):
                offset_result = compute_offset_assignments(world.settings.prize_offset)
                debug_invisible_flags = offset_result["flag_classes"]
            else:
                config = load_debug_config()
                flag_names = config.get("invisible_flags", [])
                if len(flag_names) == 3:
                    debug_invisible_flags = []
                    for name in flag_names:
                        cls = get_location_class(name)
                        if cls is not None:
                            debug_invisible_flags.append(cls)
                        else:
                            debug_invisible_flags = None
                            break

        used_flag_rooms: set[int] = set()
        chosen_flag_classes: list[type] = []
        for i in range(0, 3):
            if world._invisible_flag_choice is not None:
                location_cls = world._invisible_flag_choice[i]
            elif debug_invisible_flags is not None:
                location_cls = debug_invisible_flags[i]
            elif not world.settings.isflag_enabled(InvisibleFlagsSetting):
                location_cls = invisible_item_pool[i]
            else:
                # Filter out locations whose rooms overlap with already-chosen flags
                # or whose rooms don't have a pre-allocated flag dummy
                assert world._flag_dummy_index is not None
                valid_pool = [
                    loc_cls for loc_cls in invisible_item_pool
                    if not any(r in used_flag_rooms for r in loc_cls(0)._rooms)
                    and all(r in world._flag_dummy_index for r in loc_cls(0)._rooms)
                ]

                if not valid_pool:
                    raise Exception(f"No valid rooms available for invisible flag {i+1}! All candidate rooms are taken.")

                location_cls = random.choice(valid_pool)

            chosen_flag_classes.append(location_cls)
            location = cast(InvisibleFlagLocation, location_cls(i))
            used_flag_rooms.update(location._rooms)
            for r in location._rooms:
                # Replace the pre-allocated dummy NPC with the actual invisible flag NPC
                room = world.rooms._rooms[r]
                assert room is not None
                assert world._flag_dummy_index is not None

                idx = world._flag_dummy_index[r]
                n_id = AreaObject(0x14 + idx)
                npc = location.npc
                npc.set_visible(False)
                room._objects[idx] = npc
                world.action_scripts.replace_script(
                    npc.action_script, location.shift
                )
                world.event_scripts.get_script_by_id(
                    E0091_INVISIBLE_ITEM_SUMMONER
                ).insert_before_nth_command(0, SummonObjectToSpecificLevel(n_id, r))
            # Hint dialog must match the found-bit each slot sets (i=0,1,2 ->
            # flag1,2,3), and in script_2081 flag1's NPC (Greaper) shows DI1109,
            # flag2's (Big Boo) shows DI1107, flag3's (Dry Bones) shows DI1108.
            if i == 0:
                world.update_dialog(
                    DI1109_RESERVED_FOR_GREAPERFLAG_HINT,
                    "GREAPER:\n" + location.clue_text,
                )
            elif i == 1:
                world.update_dialog(
                    DI1107_RESERVED_FOR_BIGBOOFLAG_HINT,
                    "THE BIG BOO:\n" + location.clue_text,
                )
            elif i == 2:
                world.update_dialog(
                    DI1108_RESERVED_FOR_DRYBONESFLAG_HINT,
                    "DRY BONES:\n" + location.clue_text,
                )
            invisible_flag_locations[location_cls] = location

        # Store the invisible item locations for reuse on retry
        world._invisible_item_locations = invisible_flag_locations
        world._invisible_flag_choice = chosen_flag_classes

    world.locations = {**world.locations, **invisible_flag_locations}
    
    world.chest_locations = [
        loc for loc in world.locations.values() if isinstance(loc, TreasureChestLocation)
    ]
    world.standard_locations = [
        loc for loc in world.locations.values() if isinstance(loc, (TreasureChestLocation, EventLocation, StandingLocation, RiverLocation, BoosterHillLocation, FrogDiscipleLocation))
    ]
    world.coin_locations = [
        loc for loc in world.locations.values() if isinstance(loc, (TreasureChestLocation, EventLocation, StandingLocation))
    ]
    world.spell_locations = [
        loc for loc in world.locations.values() if isinstance(loc, SpellSlotLocation)
    ]
    world.boss_fight_locations = [
        loc for loc in world.locations.values() if isinstance(loc, BossFightLocation)
    ]
    world.star_piece_locations = [
        loc for loc in world.locations.values() if isinstance(loc, StarPieceLocation)
    ]
    world.extra_star_piece_locations = copy(world.star_piece_locations)
    if world.settings.isflag_enabled(StarPieceAvailability):
        world.extra_star_piece_locations.extend(world.standard_locations)
    world.key_item_locations = [
        loc for loc in world.locations.values() if isinstance(loc, KeyItemLocation)
    ]
    world.extra_key_item_locations = copy(world.key_item_locations)
    if world.settings.isflag_enabled(KeyItemsAnywhere):
        world.extra_key_item_locations.extend(world.standard_locations)
    world.character_recruitment_locations = [
        loc for loc in world.locations.values() if isinstance(loc, CharacterRecruitmentLocation)
    ]
