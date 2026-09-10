"""Item and prize shuffling logic."""

from __future__ import annotations
from randomizer.utils.debug_output import debug_print
from randomizer.logic.offset_preview import compute_offset_assignments
from randomizer.debug import load_debug_config, get_prize_class, get_location_class
from randomizer.utils.debug_output import DEBUG_FILE_DUMPS
from randomizer.types.prize import SlotsPrize as SlotsPrizeBase
from randomizer.types.prize import MimicFightInitiatorPrize as MimicBase
import os
import random
from copy import copy
from datetime import datetime
from typing import (TYPE_CHECKING)

from smrpgpatchbuilder.datatypes.spells.enums import Status, Element

from ...data.items import (
    AbleJuiceItem,
    FroggieDrinkItem,
    HoneySyrupItem,
    MoldyMushItem,
    MushroomItem,
    MushroomItem2,
    PureWaterItem,
    RottenMushItem,
    WiltShroomItem,
    YoshiCookieItem,
)
from randomizer.types.prizelocation import StandingLocation, TreasureShopLocation
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (
    NPC_2,
    NPC_3,
    NPC_4,
    NPC_5,
    NPC_6,
    NPC_7,
)

from randomizer.logic.progression.prizes import CookiesPrize, MarioDollPrize
from ...data.rooms.npcs import EMPTY_NPC
from ...data.allies.allies import ally_collection

from ..placement import PlacementException, place, collect_accessible_items
from ...types.logic import Inventory
from ...types.prize import (CharacterPrize, ItemPrize, CoinPrize, FPFlowerPrize)
from ...logic.progression.prize_substitute import RandomPrizeSubstitute
from randomizer.logic.progression.prizes import (
    BanditsWayStarPrize,
    BowserRecruitmentPrize,
    FryingPanPrize,
    GenoRecruitmentPrize,
    MallowRecruitmentPrize,
    MarioRecruitmentPrize,
    RecoveryMushroomPrize,
    FrogCoin1Prize,
    KeroSewersStarPrize,
    MolevilleMinesStarPrize,
    SeaStarPrize,
    LandsEndVolcanoStarPrize,
    LandsEndVolcanoStarPrize,
    NimbusLandStarPrize,
    LandsEndStar2Prize,
    LandsEndStar3Prize,
    ToadstoolRecruitmentPrize,
)
from randomizer.logic.progression.prizelocations import (MushroomKingdomInnPurchaseLocation, MonstroFirstSuperJumpRewardLocation, MonstroSecondSuperJumpRewardLocation)
from ...types.flags import (
    ReplaceItems,
    SeeYa,
    ShopQualities,
    ShopQuality,
    ShuffleHillFlowers,
    ShuffleItems,
    ShuffleShops,
    RestrictSpecialEquips,
    SuperJump2Threshold,
    NoStarEgg,
    ItemQuality,
    ItemQualityOptions,
    FireworksSetting,
    FireworksOptions,
    ShuffleCharacters,
    StartingCharacters,
    AvailableCharacters,
    MaxCharacters,
    CharacterLearnedSpells,
    AvailableSpells,
    ShuffleStarPieces,
    TotalStarPieces,
    BossShuffle,
    EXPStarsAnywhere,
    MimicsAnywhere,
    SlotsAnywhere,
    ShuffleBeetlemania,
    ShuffleMagikoopaChest,
    ShuffleWeddingGear,
    SpellsAnywhere,
    BanditsWayGate,
    BanditsWayGating,
    KeroSewersGate,
    KeroSewersGating,
    ForestMazeGate,
    ForestMazeGating,
    PipeVaultGate,
    PipeVaultGating,
    Moleville1Gate,
    Moleville1Gating,
    BoosterTowerGate,
    BoosterTowerGating,
    SeaGate,
    SeaGating,
    LandsEndGate,
    LandsEndGating,
    MonstroTownGate,
    MonstroTownGating,
    NimbusGate,
    NimbusGating,
    BarrelVolcanoGate,
    BarrelVolcanoGating,
    BowsersKeepGate,
    BowsersKeepGating,
    FactoryGate,
    FactoryGating,
    BoosterHillGate,
    BoosterHillGating,
    MarrymoreGate,
    MarrymoreGating,
    YaridovichGate,
    YaridovichGating,
    StarPiecesRequired,
)
from ...types.prizelocation import (
    BoosterHillLocation,
    CharacterRecruitmentLocation,
    EventLocation,
    InvisibleFlagLocation,
    PacketLocation,
    RiverLocation,
    StarPieceLocation,
    BossFightLocation,
    SpellSlotLocation,
    FrogDiscipleLocation,
    TreasureChestLocation,
    StartingCharacterLocation,
    vanilla_spell_owner,
)
from ...types.prize import (
    CharacterPrize,
    SpellPrize,
    StarPiecePrize,
    BossFightPrize,
    damaging_spell_prizes,
)
from randomizer.logic.progression.prizelocations import (
    StartingCharacter1,
    StartingCharacter2,
    StartingCharacter3,
    StartingCharacter4,
    StartingCharacter5,
)
from randomizer.logic.progression.prizes import (
    # Key items
    RareFrogCoinPrize,
    WalletPrize,
    CricketPiePrize,
    BambinoBombPrize,
    CastleKey1Prize,
    CastleKey2Prize,
    ProgressiveCardPrize,
    GreaperFlagPrize,
    DryBonesFlagPrize,
    BigBooFlagPrize,
    ShedKeyPrize,
    ElderKeyPrize,
    CricketJamPrize,
    TempleKeyPrize,
    RoomKeyPrize,
    SeedPrize,
    FertilizerPrize,
    BrightCardPrize,
    YouMissed,
    ProgressiveEggPrize,
    LuckyJewelPrize,
    SignalRingPrize,
    GoodieBagPrize,
    CrystalShardPrize,
    ExtraShinyStonePrize,
    StayVoucherPrize,
    GoldPaintPrize,
    StarEggPrize,
    # Equipment
    FroggiestickPrize,
    ChompPrize,
    ZoomShoesPrize,
    LazyShellArmorPrize,
    LazyShellWeaponPrize,
    GhostMedalPrize,
    QuartzCharmPrize,
    JinxBeltPrize,
    AttackScarfPrize,
    WonderChompPrize,
    Stella023Prize,
    SageStickPrize,
    EnduringBroochPrize,
    TeamworkBandPrize,
    SuperSuitPrize,
    JumpShoesPrize,
    BtubRingPrize,
    # Fireworks
    RegularFireworksPrize,
    ProgressiveFireworksPrize,
    # Characters
    MarioRecruitmentPrize,
    MallowRecruitmentPrize,
    GenoRecruitmentPrize,
    BowserRecruitmentPrize,
    ToadstoolRecruitmentPrize,
    # Spells
    JumpSpellPrize,
    FireOrbSpellPrize,
    SuperJumpSpellPrize,
    SuperFlameSpellPrize,
    UltraJumpSpellPrize,
    UltraFlameSpellPrize,
    ThunderboltSpellPrize,
    HPRainSpellPrize,
    PsychopathSpellPrize,
    ShockerSpellPrize,
    SnowyPrize,
    StarRainSpellPrize,
    GenoBeamSpellPrize,
    GenoBoostSpellPrize,
    GenoWhirlSpellPrize,
    GenoBlastSpellPrize,
    GenoFlashSpellPrize,
    TerrorizeSpellPrize,
    PoisonGasSpellPrize,
    CrusherSpellPrize,
    BowserCrushSpellPrize,
    TherapySpellPrize,
    GroupHugSpellPrize,
    MuteSpellPrize,
    SleepyTimeSpellPrize,
    ComeBackSpellPrize,
    PsychBombSpellPrize,
    # Star pieces
    StarPiece1,
    StarPiece2,
    StarPiece3,
    StarPiece4,
    StarPiece5,
    StarPiece6,
    StarPiece7,
    # Special prizes
    EXPStarPrize,
    MimicFightInitiatorPrize,
    FirstMimicFightLauncher,
    SecondMimicFightLauncher,
    ThirdMimicFightLauncher,
    SlotsPrize,
    BeetlemaniaPrize,
    InfiniteCoinsPrize,
    WeddingGearPrize,
    # bosses
    SeeYaPrize,
    EarlierTimesPrize,
    CoinTrickPrize,
    ExpBoosterPrize,
    ScroogeRingPrize,
    # Boss fight prizes for gating
    HammerBrosFight,
    MackBossFight,
    BowyerBossFight,
    PunchinelloBossFight,
    BundtBossFight,
    YaridovichBossFight,
    Belome2BossFight,
    MegasmilaxBossFight,
    ValentinaBossFight,
    AxemRangersBossFight,
    KnifeGuyGrateGuyBossFight,
    JohnnyBossFight,
)
from ...data.spells.spells import (
    JumpSpell,
    FireOrbSpell,
    SuperJumpSpell,
    SuperFlameSpell,
    UltraJumpSpell,
    UltraFlameSpell,
    ThunderboltSpell,
    HPRainSpell,
    PsychopathSpell,
    ShockerSpell,
    SnowySpell,
    StarRainSpell,
    GenoBeamSpell,
    GenoBoostSpell,
    GenoWhirlSpell,
    GenoBlastSpell,
    GenoFlashSpell,
    TerrorizeSpell,
    PoisonGasSpell,
    CrusherSpell,
    BowserCrushSpell,
    TherapySpell,
    GroupHugSpell,
    MuteSpell,
    SleepyTimeSpell,
    ComeBackSpell,
    PsychBombSpell,
)
from randomizer.logic.progression.prizelocations import (
        Mimic1BossFight,
        Mimic1DropRewardLocation,
        Mimic1StarPiece,
        Mimic1ReloadRewardLocation,
        Mimic2BossFight,
        Mimic2DropRewardLocation,
        Mimic2StarPiece,
        Mimic2ReloadRewardLocation,
        Mimic3BossFight,
        Mimic3StarPiece,
    )
from randomizer.logic.progression.prizes import (
        FirstMimicFightLauncher,
        SecondMimicFightLauncher,
        ThirdMimicFightLauncher,
    )
from ...types.flags import SpellsAnywhere
from ...types.flags import KeyItemsAnywhere
from ...types.prize import SpellPrize
from ..placement import collect_accessible_items
from ...types.prize import KeyPrize
from ..solvability import (
        SettingsRelaxed,
        assert_key_pool_balanced,
        assert_key_pool_placeable,
        relax_key_pool_deadlock,
    )
from ...types.flags import WinCondition, WinConditions
from randomizer.logic.progression.prizes import SmithyBossFight
from ...data.physical_objects.items import (
        YellowSpellObject,
        FireSpellObject,
        BlueSpellObject,
        GreenSpellObject,
        GraySpellObject,
    )
from ...data.variables.sprite_names import (
        SPR0214_RED_BALL,
        SPR0215_BLUE_BALL,
        SPR0217_GREEN_BALL,
        SPR0218_YELLOW_BALL,
        SPR0224_GRAY_BALL,
    )
from smrpgpatchbuilder.datatypes.spells.enums import Element
from ..placement import diagnose_empty_locations
from randomizer.debug import load_debug_config, get_location_class
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
        DisableObjectTriggerInSpecificLevel,
        JmpIfBitClear,
    )
from ...types.flags import (
        AnnoyingChests,
        EquipmentProperties,
        EquipmentPropertiesOptions,
        StarPieceHints,
    )
from ...types.prizelocation import (
        TreasureChestLocation,
        StandardPrizeLocation,
        RiverLocation,
        StandingLocation,
        SIGNAL_RING_EVENT_DICT,
    )
from ...types.prize import ItemPrize, CoinPrize, StarPiecePrize
from randomizer.logic.progression.prizes import YouMissed, Coins10Prize
from ...data.items.items import (
        MushroomItem,
        HoneySyrupItem,
        AbleJuiceItem,
        YoshiCookieItem,
        PureWaterItem,
        FroggieDrinkItem,
        WiltShroomItem,
        RottenMushItem,
        MoldyMushItem,
        MushroomItem2,
    )


if TYPE_CHECKING:
    from ...types.gameworld import GameWorld
    from ...types.prizelocation import PrizeLocation
    from ...types.prize import Prize


def _on_item_placed(
    world: GameWorld, item: Prize, placed_location: PrizeLocation
) -> None:
    """Callback to handle placement events like Mimic world area updates and spell count tracking."""

    # the character was assigned back in can_accept; only the count lands here
    if isinstance(item, SpellPrize) and world.settings.isflag_enabled(SpellsAnywhere):
        if item.character is not None:
            if world._spell_assignments is None:
                world._spell_assignments = {}
            char_type = item.character
            world._spell_assignments[char_type] = (
                world._spell_assignments.get(char_type, 0) + 1
            )

    if isinstance(item, FirstMimicFightLauncher):
        world_area = placed_location._world_area
        world.locations[Mimic1BossFight]._world_area = world_area
        world.locations[Mimic1DropRewardLocation]._world_area = world_area
        world.locations[Mimic1StarPiece]._world_area = world_area
        world.locations[Mimic1ReloadRewardLocation]._world_area = world_area
    elif isinstance(item, SecondMimicFightLauncher):
        world_area = placed_location._world_area
        world.locations[Mimic2BossFight]._world_area = world_area
        world.locations[Mimic2DropRewardLocation]._world_area = world_area
        world.locations[Mimic2StarPiece]._world_area = world_area
        world.locations[Mimic2ReloadRewardLocation]._world_area = world_area
    elif isinstance(item, ThirdMimicFightLauncher):
        world_area = placed_location._world_area
        world.locations[Mimic3BossFight]._world_area = world_area
        world.locations[Mimic3StarPiece]._world_area = world_area


ally_name_to_prize: dict[str, type[CharacterPrize]] = {
    "Mario": MarioRecruitmentPrize,
    "Mallow": MallowRecruitmentPrize,
    "Geno": GenoRecruitmentPrize,
    "Bowser": BowserRecruitmentPrize,
    "Toadstool": ToadstoolRecruitmentPrize,
}

PROGRESSION_PRIZES = 0
RESTRICTED_PRIZES = 1
MANDATORY_INCLUSIONS = 2
LOW_PRIORITY = 3

TIERS_CAN_OVERFLOW = [LOW_PRIORITY]

TIER_NAMES = {
    PROGRESSION_PRIZES: "PROGRESSION",
    RESTRICTED_PRIZES: "RESTRICTED",
    MANDATORY_INCLUSIONS: "MANDATORY_INCLUSIONS",
    LOW_PRIORITY: "LOW_PRIORITY",
}


def _dump_placement_failure(
    world: GameWorld,
    pool_before: dict[int, list[str]],
    unplaced_items: list[str],
    priority_classes: set[type[Prize]] | None = None,
) -> str:
    """Write a debug dump to a timestamped file when placement fails.

    Returns the path to the written file.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(
        os.path.dirname(__file__), "..", "..", "debug", "placement_logs"
    )
    os.makedirs(log_dir, exist_ok=True)
    filepath = os.path.join(log_dir, f"placement_fail_{timestamp}.txt")

    player_has = collect_accessible_items(world)

    lines: list[str] = []
    lines.append(f"PLACEMENT FAILURE - {datetime.now().isoformat()}")
    lines.append("=" * 80)

    lines.append("")
    lines.append("POOL BEFORE PLACEMENT (by tier)")
    lines.append("-" * 40)
    for tier_id in sorted(pool_before.keys()):
        tier_name = TIER_NAMES.get(tier_id, f"TIER_{tier_id}")
        items = pool_before[tier_id]
        lines.append(f"  {tier_name} ({len(items)} items):")
        for item_name in sorted(items):
            lines.append(f"    - {item_name}")

    lines.append("")
    lines.append("PRIORITY CLASSES (high-volume items)")
    lines.append("-" * 40)
    if priority_classes:
        for cls_name in sorted(cls.__name__ for cls in priority_classes):
            lines.append(f"  - {cls_name}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append(f"UNPLACEABLE ITEMS ({len(unplaced_items)})")
    lines.append("-" * 40)
    for name in sorted(unplaced_items):
        lines.append(f"  - {name}")

    placed: list[tuple[str, str]] = []
    for loc in world.locations.values():
        if loc.has_item:
            placed.append((type(loc).__name__, type(loc.prize).__name__))
    placed.sort()

    lines.append("")
    lines.append(f"PLACED ITEMS ({len(placed)})")
    lines.append("-" * 40)
    for loc_name, prize_name in placed:
        lines.append(f"  {loc_name}: {prize_name}")

    accessible_empty: list[str] = []
    for loc in world.locations.values():
        if loc.can_access(player_has, world) and not loc.has_item:
            accessible_empty.append(type(loc).__name__)
    accessible_empty.sort()

    lines.append("")
    lines.append(f"ACCESSIBLE EMPTY LOCATIONS ({len(accessible_empty)})")
    lines.append("-" * 40)
    for name in accessible_empty:
        lines.append(f"  - {name}")

    inaccessible: list[str] = []
    for loc in world.locations.values():
        if not loc.can_access(player_has, world):
            prize_info = type(loc.prize).__name__ if loc.has_item else "(empty)"
            inaccessible.append(f"{type(loc).__name__}: {prize_info}")
    inaccessible.sort()

    lines.append("")
    lines.append(f"INACCESSIBLE LOCATIONS ({len(inaccessible)})")
    lines.append("-" * 40)
    for entry in inaccessible:
        lines.append(f"  - {entry}")

    text = "\n".join(lines) + "\n"
    with open(filepath, "w") as f:
        f.write(text)

    if world.settings.debug_mode:
        debug_print(f"[DEBUG] Placement failure dump written to: {filepath}")
    return filepath


def select_spells(
    world: GameWorld, selected_roster: set[type[CharacterPrize]]
) -> list[type[Prize]]:
    # All 27 spell prize classes
    all_spell_prizes: list[type[Prize]] = [
        JumpSpellPrize,
        FireOrbSpellPrize,
        SuperJumpSpellPrize,
        SuperFlameSpellPrize,
        UltraJumpSpellPrize,
        UltraFlameSpellPrize,
        ThunderboltSpellPrize,
        HPRainSpellPrize,
        PsychopathSpellPrize,
        ShockerSpellPrize,
        SnowyPrize,
        StarRainSpellPrize,
        GenoBeamSpellPrize,
        GenoBoostSpellPrize,
        GenoWhirlSpellPrize,
        GenoBlastSpellPrize,
        GenoFlashSpellPrize,
        TerrorizeSpellPrize,
        PoisonGasSpellPrize,
        CrusherSpellPrize,
        BowserCrushSpellPrize,
        TherapySpellPrize,
        GroupHugSpellPrize,
        MuteSpellPrize,
        SleepyTimeSpellPrize,
        ComeBackSpellPrize,
        PsychBombSpellPrize,
    ]

    available_spells_flag = world.settings.get_flag(AvailableSpells)
    excluded_spell_classes: set[type] = {
        m.value for m in available_spells_flag.disabled
    }

    spell_to_prize: dict[type, type[Prize]] = {
        JumpSpell: JumpSpellPrize,
        FireOrbSpell: FireOrbSpellPrize,
        SuperJumpSpell: SuperJumpSpellPrize,
        SuperFlameSpell: SuperFlameSpellPrize,
        UltraJumpSpell: UltraJumpSpellPrize,
        UltraFlameSpell: UltraFlameSpellPrize,
        ThunderboltSpell: ThunderboltSpellPrize,
        HPRainSpell: HPRainSpellPrize,
        PsychopathSpell: PsychopathSpellPrize,
        ShockerSpell: ShockerSpellPrize,
        SnowySpell: SnowyPrize,
        StarRainSpell: StarRainSpellPrize,
        GenoBeamSpell: GenoBeamSpellPrize,
        GenoBoostSpell: GenoBoostSpellPrize,
        GenoWhirlSpell: GenoWhirlSpellPrize,
        GenoBlastSpell: GenoBlastSpellPrize,
        GenoFlashSpell: GenoFlashSpellPrize,
        TerrorizeSpell: TerrorizeSpellPrize,
        PoisonGasSpell: PoisonGasSpellPrize,
        CrusherSpell: CrusherSpellPrize,
        BowserCrushSpell: BowserCrushSpellPrize,
        TherapySpell: TherapySpellPrize,
        GroupHugSpell: GroupHugSpellPrize,
        MuteSpell: MuteSpellPrize,
        SleepyTimeSpell: SleepyTimeSpellPrize,
        ComeBackSpell: ComeBackSpellPrize,
        PsychBombSpell: PsychBombSpellPrize,
    }

    excluded_spell_prizes: set[type[Prize]] = {
        spell_to_prize[spell_cls]
        for spell_cls in excluded_spell_classes
        if spell_cls in spell_to_prize
    }

    available_spells: list[type[Prize]] = [
        sp for sp in all_spell_prizes if sp not in excluded_spell_prizes
    ]

    if not world.settings.isflag_enabled(CharacterLearnedSpells):
        # Characters learn their vanilla spells. Only include spells whose
        # vanilla owner is actually in the seed's character roster: a spell
        # learned by an available-but-unselected character can never be placed
        # (its owner is never recruited) and would deadlock placement.
        return [
            loc.originally_held
            for loc in world.locations.values()
            if isinstance(loc, SpellSlotLocation)
            and loc.originally_held is not None
            and loc.originally_held not in excluded_spell_prizes
            and vanilla_spell_owner(loc.originally_held) in selected_roster
        ]

    # Cached for the duration of this shuffle attempt: shuffle_rules() calls this
    # once per location, and re-rolling the pick on every call would hand each
    # call a different spell pool (and so a different tier assignment).
    if world._cached_spells is not None:
        return world._cached_spells

    forced_spells: list[type[Prize]] = []
    if SuperJumpSpellPrize in available_spells:
        forced_spells.append(SuperJumpSpellPrize)
    max_characters = world.settings.get_flag(MaxCharacters).value
    target_spell_count = min(27, 6 * max_characters) - len(forced_spells)
    remaining_spells = [a for a in available_spells if a not in forced_spells]

    # Mokura's transform needs one damaging spell somewhere in the seed. When the
    # settings leave any damaging spell available, re-roll until the random pick
    # actually lands one -- otherwise a roster small enough to only take a few
    # spells (MaxCharacters 1 takes six) can draw all-utility by chance. If the
    # settings exclude every damaging spell there is nothing to re-roll toward;
    # shuffle_rules() raises on that below.
    damaging_is_available = any(
        issubclass(sp, SpellPrize) and sp.deals_damage() for sp in available_spells
    )
    while True:
        random.shuffle(remaining_spells)
        selected_spells = forced_spells + remaining_spells[:target_spell_count]
        if not damaging_is_available or any(
            issubclass(sp, SpellPrize) and sp.deals_damage() for sp in selected_spells
        ):
            break

    world._cached_spells = selected_spells
    return selected_spells


def shuffle_rules(world: GameWorld) -> dict[int, list[type[Prize]]]:
    # Prize placement guidelines are divided into tiers.
    # The highest tier is prizes that gate other checks.
    progress_rules: list[type[Prize]] = [
        CastleKey1Prize,
        CastleKey2Prize,
        BambinoBombPrize,
        BrightCardPrize,
        ElderKeyPrize,
        RoomKeyPrize,
        WalletPrize,
        GreaperFlagPrize,
        DryBonesFlagPrize,
        BigBooFlagPrize,
        CricketJamPrize,
        SeedPrize,
        FertilizerPrize,
        RegularFireworksPrize,
        ProgressiveFireworksPrize,
        WeddingGearPrize,
        ExtraShinyStonePrize,
        StayVoucherPrize,
        CookiesPrize,
        MarioDollPrize,
        FirstMimicFightLauncher,
        SecondMimicFightLauncher,
        ThirdMimicFightLauncher,
        CricketPiePrize,
        TempleKeyPrize,
        RareFrogCoinPrize,
        ShedKeyPrize,
        GoldPaintPrize,
    ]

    # Tier 4: Other prizes that don't unlock anything but are still mandatory to include
    # These can include unpurchase-able items, for example
    should_otherwise_include_rules: list[type[Prize]] = [
        ProgressiveEggPrize,
        CrystalShardPrize,
        ProgressiveCardPrize,
        EarlierTimesPrize,
        CoinTrickPrize,
        ExpBoosterPrize,
        ScroogeRingPrize,
        LuckyJewelPrize,
    ]
    if not world.settings.isflag_enabled(SeeYa):
        should_otherwise_include_rules.append(SeeYaPrize)

    # All boss fights are progress because they each unlock one star piece check at minimum.
    for prize_cls in BossFightPrize.__subclasses__():
        progress_rules.append(prize_cls)
    all_character_prizes: dict[str, type[CharacterPrize]] = {
        "Mario": MarioRecruitmentPrize,
        "Mallow": MallowRecruitmentPrize,
        "Geno": GenoRecruitmentPrize,
        "Bowser": BowserRecruitmentPrize,
        "Toadstool": ToadstoolRecruitmentPrize,
    }

    available_chars_flag = world.settings.get_flag(AvailableCharacters)
    excluded_char_names: set[str] = {
        m.value.name for m in available_chars_flag.disabled
    }
    # Decide which characters are actually in the seed BEFORE selecting spells,
    # so the spell pool can be derived from the final roster. In vanilla
    # learned-spell mode a spell is only learnable by its owning character, so a
    # spell whose owner isn't in the seed must never enter the pool (it could
    # never be placed and would deadlock the fill).

    max_characters = world.settings.get_flag(MaxCharacters).value

    # Characters explicitly chosen as starters. They must be present in the
    # pool, otherwise StartingCharacter1's placement falls back to a filler
    # character and the user's chosen starter silently disappears. Also used to
    # bias non-elemental progression-spell selection toward owners already in
    # the seed.
    starting_chars_flag = world.settings.get_flag(StartingCharacters)
    explicit_starter_prizes: set[type[CharacterPrize]] = set()
    for option in starting_chars_flag.enabled:
        value = option.value
        # Skip Random_X placeholders - those are meant to be resolved randomly
        if isinstance(value, str):
            continue
        prize_cls = all_character_prizes.get(value.name)
        if prize_cls is not None:
            explicit_starter_prizes.add(prize_cls)

    conditional_progress: dict[type[Prize], list[tuple[type, object]]] = {
        MallowRecruitmentPrize: [
            (BanditsWayGate, BanditsWayGating.MALLOW),
            (KeroSewersGate, KeroSewersGating.MALLOW),
            (BoosterTowerGate, BoosterTowerGating.MALLOW),
        ],
        GenoRecruitmentPrize: [
            (PipeVaultGate, PipeVaultGating.GENO),
            (Moleville1Gate, Moleville1Gating.GENO),
            (BoosterTowerGate, BoosterTowerGating.GENO),
        ],
        MarioRecruitmentPrize: [
            (BoosterTowerGate, BoosterTowerGating.MARIO),
        ],
        ToadstoolRecruitmentPrize: [
            (BoosterTowerGate, BoosterTowerGating.TOADSTOOL),
            (SeaGate, SeaGating.TOADSTOOL),
        ],
        BowserRecruitmentPrize: [
            (BoosterTowerGate, BoosterTowerGating.BOWSER),
        ],
    }

    progression_required_chars: set[type[CharacterPrize]] = set()
    for prize_cls, gating_info in conditional_progress.items():
        if not issubclass(prize_cls, CharacterPrize):
            continue  # Just a sanity check, all keys here should be CharacterPrize subclasses
        for gate, gating_flag in gating_info:
            if world.settings.is_flag_value(gate, gating_flag):
                progression_required_chars.add(prize_cls)
                break

    progression_required_chars |= explicit_starter_prizes

    prize_to_name: dict[type[CharacterPrize], str] = {
        v: k for k, v in all_character_prizes.items()
    }

    # Every Bowser's Keep location gates on can_pass_obstacle_courses(), which in
    # vanilla learned-spell mode is satisfied only by recruiting a character who
    # learns a damage spell. No area gate is obliged to require one --
    # set them all to "always open" and none of these characters is gate-critical, so
    # they all land in MANDATORY_INCLUSIONS, which is filled by a *later* place()
    # call. The Keep is then unreachable for the entire progression pass, its four
    # boss locations can never be filled, and since boss prizes are 1:1 with boss
    # locations exactly four boss fights are stranded on every retry. So treat the
    # spell gate like any other gate: one of its characters is progression-required.
    if not world.settings.isflag_enabled(
        CharacterLearnedSpells
    ) and not world.settings.isflag_enabled(SpellsAnywhere):
        disabled_spells: set[type] = {
            m.value for m in world.settings.get_flag(AvailableSpells).disabled
        }
        damaging_spells = {prize._spell for prize in damaging_spell_prizes()}
        # Restricted to allies holding an available damage spell from recruitment
        # (starting_magic), since can_pass_obstacle_courses() does not model levels.
        # Mario/Mallow/Geno/Bowser start with one; Toadstool's is Psych Bomb at 18.
        # Sorted so the random pick below is reproducible for a given seed.
        qualified: list[type[CharacterPrize]] = sorted(
            (
                prize_cls
                for name, prize_cls in all_character_prizes.items()
                if name not in excluded_char_names
                and any(
                    spell in damaging_spells and spell not in disabled_spells
                    for spell in (prize_cls._ally.starting_magic or [])
                )
            ),
            key=lambda cls: cls.__name__,
        )
        if not qualified:
            raise ValueError(
                "No available ally starts with a damaging spell, so Bowser's Keep "
                "would be unreachable. Include Mario, Mallow, Geno or Bowser and "
                "leave the damaging spell they start with available."
            )
        if not progression_required_chars & set(qualified):
            # Cached for the duration of this shuffle attempt for the same reason as
            # _cached_char_fill below: shuffle_rules() runs once per location in the
            # pull loop and the roster must not change between those calls.
            if world._cached_spell_damage_char is None:
                world._cached_spell_damage_char = random.choice(qualified)
            progression_required_chars.add(world._cached_spell_damage_char)

    for prize_cls in progression_required_chars:
        char_name = prize_to_name.get(prize_cls)
        if char_name and char_name in excluded_char_names:
            raise ValueError(
                f"Character '{char_name}' is required for progression but has been excluded in settings."
            )

    if max_characters < len(progression_required_chars):
        raise ValueError(
            f"MaxCharacters ({max_characters}) is less than the number of characters "
            f"required for progression ({len(progression_required_chars)}). "
            f"Required characters: {[prize_to_name[c] for c in progression_required_chars]}"
        )

    available_char_prizes: set[type[CharacterPrize]] = {
        prize_cls
        for name, prize_cls in all_character_prizes.items()
        if name not in excluded_char_names
    }

    if max_characters > len(available_char_prizes):
        raise ValueError(
            f"MaxCharacters ({max_characters}) cannot be fulfilled. "
            f"Only {len(available_char_prizes)} characters are available after exclusions."
        )

    for prize_cls in progression_required_chars:
        progress_rules.append(prize_cls)

    remaining_slots = max_characters - len(progression_required_chars)

    non_progression_available: list[type[CharacterPrize]] = [
        prize_cls
        for prize_cls in available_char_prizes
        if prize_cls not in progression_required_chars
    ]

    # Randomly select characters to fill remaining slots. Cached for the duration
    # of this shuffle attempt: shuffle_rules() runs many times per attempt (once
    # per location in the pull loop), and the roster must stay identical across
    # those calls so the spell pool and Super Jump reward locations agree.
    if world._cached_char_fill is not None:
        chars_to_include = world._cached_char_fill
    elif remaining_slots > 0 and non_progression_available:
        chars_to_include = random.sample(
            non_progression_available,
            min(remaining_slots, len(non_progression_available)),
        )
        world._cached_char_fill = chars_to_include
    else:
        chars_to_include = []
        world._cached_char_fill = chars_to_include

    # The final character roster present in the seed (required + randomly
    # selected fill). Source of truth for deriving the spell pool and the
    # Super Jump reward locations below.
    selected_roster: set[type[CharacterPrize]] = (
        progression_required_chars | set(chars_to_include)
    )

    # Resolve the StartingCharacters flag's Random_X slots against that roster,
    # once per attempt. Drawing from the roster is what keeps a random starter
    # in the prize pool: picking from all five allies could name a character
    # MaxCharacters or AvailableCharacters left out of the seed, and the starter
    # location would then be handed nothing at all.
    if world._cached_starting_chars is None:
        roster_allies = [
            ally
            for ally in ally_collection._allies
            if all_character_prizes.get(ally.name) in selected_roster
        ]
        world._cached_starting_chars = starting_chars_flag.resolve_random_selections(
            available=roster_allies
        )

    selected_spells = select_spells(world, selected_roster)

    selected_damaging_spells: list[type[SpellPrize]] = [
        prize for prize in damaging_spell_prizes() if prize in selected_spells
    ]
    if len(selected_damaging_spells) == 0:
        raise ValueError(
            "No damaging spells are available to assign to progress rules. At least "
            "one spell that damages enemies must be included in the seed for "
            "progression purposes."
        )

    # Place up to 2 damaging spells in the progression tier so MokuraBossFight
    # (and similar) can be placed (they require a damaging spell to be
    # accessible). These come from selected_spells, which is already
    # roster-derived, so their owners are guaranteed to be in the seed. Prefer
    # explicit-starter-owned spells.
    preferred_spells = [
        s
        for s in selected_damaging_spells
        if vanilla_spell_owner(s) in explicit_starter_prizes
    ]
    other_spells = [s for s in selected_damaging_spells if s not in preferred_spells]
    random.shuffle(preferred_spells)
    random.shuffle(other_spells)
    ordered_damaging = preferred_spells + other_spells
    # With SpellsAnywhere on and learned spells vanilla, can_accept() only takes a
    # spell once its vanilla owner is recruited, and the progression pass recruits
    # exactly two groups: the starters, which are pre-filled into their locations
    # (and pulled from the pool) before any place() call, and the
    # progression-required characters, which place() seats first. Everyone else is a
    # MANDATORY_INCLUSIONS fill handled by a *later* place(), so a progression-tier
    # spell owned by one of them has zero legal locations anywhere in the world and
    # strands the pass on every retry. Toadstool owns exactly one damaging spell
    # (Psych Bomb), so a lone-Toadstool roster always stranded the second pick.
    # Filtering before the slice keeps 2 wherever 2 are placeable and drops to 1
    # where only one is. Applied after both shuffles, so the random stream is
    # untouched and seeds that already worked are unaffected.
    if world.settings.isflag_enabled(
        SpellsAnywhere
    ) and not world.settings.isflag_enabled(CharacterLearnedSpells):
        recruited_during_progression: set[type[CharacterPrize]] = set(
            progression_required_chars
        )
        # Explicit starters are already progression-required; a Random_X starter is
        # not, but is still pre-filled and so recruited from the first sphere.
        for ally in world._cached_starting_chars or []:
            starter_prize = all_character_prizes.get(ally.name)
            if starter_prize is not None:
                recruited_during_progression.add(starter_prize)
        ordered_damaging = [
            s
            for s in ordered_damaging
            if vanilla_spell_owner(s) in recruited_during_progression
        ]
    progression_damaging_spells = ordered_damaging[: min(2, len(ordered_damaging))]

    # Assign selected spells to tiers. Super Jump is intentionally NOT forced
    # into the progression tier: it gates only its own two Monstro reward
    # locations, and forcing it early deadlocks the fill when its owner (Mario)
    # is a later, non-progression recruit. As a mandatory inclusion, place()'s
    # character-first ordering guarantees Mario is recruited before it is placed.
    for spell in selected_spells:
        if spell in progression_damaging_spells:
            progress_rules.append(spell)
        else:
            should_otherwise_include_rules.append(spell)

    # Super Jump reward locations are included only when the Super Jump spell
    # actually exists in the seed: it is enabled in AvailableSpells, and in
    # vanilla learned-spell mode its learner (Mario) is in the roster. The
    # locations gate on has_item(SuperJumpSpellPrize), which already implies
    # Mario is recruited, so no extra access check is required here.
    super_jump_in_available_spells = any(
        opt.value == SuperJumpSpell
        for opt in world.settings.get_flag(AvailableSpells).enabled
    )
    super_jump_enabled = super_jump_in_available_spells and (
        world.settings.isflag_enabled(CharacterLearnedSpells)
        or MarioRecruitmentPrize in selected_roster
    )
    # Reconcile reward-location presence with the decision. world.locations is
    # not rebuilt between shuffle retries, so a prior attempt may have left these
    # behind; keep this symmetric (add when enabled, remove when not) so the
    # reward locations never outlive the Super Jump spell that gates them.
    monstro_locations = (
        MonstroFirstSuperJumpRewardLocation,
        MonstroSecondSuperJumpRewardLocation,
    )
    if super_jump_enabled:
        if MonstroFirstSuperJumpRewardLocation not in world.locations:
            world.locations = {
                **world.locations,
                MonstroFirstSuperJumpRewardLocation: MonstroFirstSuperJumpRewardLocation(),
                MonstroSecondSuperJumpRewardLocation: MonstroSecondSuperJumpRewardLocation(),
            }
    elif any(loc in world.locations for loc in monstro_locations):
        world.locations = {
            k: v for k, v in world.locations.items() if k not in monstro_locations
        }

    # Tier 3: Prizes that don't unlock anything but that are extremely limited in terms of where they can be placed, so they need to be placed next
    post_progression_rules: list[type[Prize]] = [
        SlotsPrize,
        BanditsWayStarPrize,
        KeroSewersStarPrize,
        MolevilleMinesStarPrize,
        SeaStarPrize,
        LandsEndVolcanoStarPrize,
        NimbusLandStarPrize,
        LandsEndStar2Prize,
        LandsEndStar3Prize,
    ]
    if not world.settings.isflag_enabled(ShuffleShops):
        should_otherwise_include_rules.extend(
            [
                FryingPanPrize,
            ]
        )
    # Guarantee transformative equips
    if not world.settings.is_flag_value(ShopQuality, ShopQualities.ORIGINAL):
        should_otherwise_include_rules.extend(
            [
                JumpShoesPrize,
                BtubRingPrize,
            ]
        )
    # Add all spells except Super Jump and the chosen non-elemental
    if not world.settings.isflag_enabled(NoStarEgg):
        should_otherwise_include_rules.extend([StarEggPrize])

    should_otherwise_include_rules.extend(chars_to_include)
    if world.settings.isflag_enabled(ShuffleBeetlemania):
        should_otherwise_include_rules.append(BeetlemaniaPrize)
    should_otherwise_include_rules.extend(
        [SignalRingPrize, GoodieBagPrize, YouMissed]
    )

    if world.settings.isflag_enabled(RestrictSpecialEquips):
        should_otherwise_include_rules.extend(
            [
                FroggiestickPrize,
                ChompPrize,
                ZoomShoesPrize,
                LazyShellArmorPrize,
                LazyShellWeaponPrize,
                GhostMedalPrize,
                QuartzCharmPrize,
                JinxBeltPrize,
                AttackScarfPrize,
                SuperSuitPrize,
                WonderChompPrize,
                Stella023Prize,
                SageStickPrize,
                EnduringBroochPrize,
                TeamworkBandPrize,
            ]
        )

    progress_stars = 0
    if world.settings.is_flag_value(SeaGate, SeaGating.STAR_4):
        progress_stars = 4
    elif world.settings.is_flag_value(LandsEndGate, LandsEndGating.STAR_5):
        progress_stars = 4
    elif world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.STAR_6):
        progress_stars = 6
    elif world.settings.is_flag_value(FactoryGate, FactoryGating.STAR_6):
        progress_stars = 6
    mxstars = world.settings.get_flag(StarPiecesRequired).value
    if mxstars > progress_stars:
        progress_stars = mxstars
    maxstars = world.settings.get_flag(TotalStarPieces).value

    stars = [
        StarPiece1,
        StarPiece2,
        StarPiece3,
        StarPiece4,
        StarPiece5,
        StarPiece6,
        StarPiece7,
    ]
    # Iterate over the FULL total (maxstars), not just progress_stars: the first
    # progress_stars are progression-tier, the rest (up to TotalStarPieces) are
    # mandatory inclusions. Bounding the loop by progress_stars made the elif dead
    # code, so extra star pieces above StarPiecesRequired were never placed.
    # validation.py guarantees maxstars >= progress_stars.
    for i in range(maxstars):
        if i < progress_stars:
            progress_rules.append(stars[i])
        elif i < maxstars:
            should_otherwise_include_rules.append(stars[i])

    return {
        PROGRESSION_PRIZES: copy(progress_rules),
        RESTRICTED_PRIZES: copy(post_progression_rules),
        MANDATORY_INCLUSIONS: should_otherwise_include_rules,
        LOW_PRIORITY: [FrogCoin1Prize, RecoveryMushroomPrize, FPFlowerPrize, CoinPrize],
    }


def should_shuffle(location: PrizeLocation, world: GameWorld) -> bool:
    if isinstance(
        location,
        (
            TreasureChestLocation,
            StandingLocation,
            EventLocation,
            RiverLocation,
            BoosterHillLocation,
            PacketLocation,
            InvisibleFlagLocation,
        ),
    ) and not world.settings.isflag_enabled(ShuffleItems):
        return False
    if isinstance(
        location, (TreasureShopLocation, FrogDiscipleLocation)
    ) and not world.settings.isflag_enabled(ShuffleShops):
        return False
    if isinstance(location, BoosterHillLocation) and not world.settings.isflag_enabled(
        ShuffleHillFlowers
    ):
        return False
    if isinstance(
        location, CharacterRecruitmentLocation
    ) and not world.settings.isflag_enabled(ShuffleCharacters):
        return False
    if isinstance(location, StarPieceLocation) and not world.settings.isflag_enabled(
        ShuffleStarPieces
    ):
        return False
    if isinstance(location, BossFightLocation) and not world.settings.isflag_enabled(
        BossShuffle
    ):
        return False
    if isinstance(
        location, MushroomKingdomInnPurchaseLocation
    ) and not world.settings.isflag_enabled(ShuffleBeetlemania):
        return False
    if location.originally_held is not None:
        if issubclass(location.originally_held, CoinPrize) and isinstance(
            location, StandingLocation
        ):
            return False
        if issubclass(
            location.originally_held, SlotsPrize
        ) and not world.settings.isflag_enabled(SlotsAnywhere):
            return False
        if issubclass(
            location.originally_held, EXPStarPrize
        ) and not world.settings.isflag_enabled(EXPStarsAnywhere):
            return False
        if issubclass(
            location.originally_held, MimicFightInitiatorPrize
        ) and not world.settings.isflag_enabled(MimicsAnywhere):
            return False
        if issubclass(
            location.originally_held, InfiniteCoinsPrize
        ) and not world.settings.isflag_enabled(ShuffleMagikoopaChest):
            return False
        if issubclass(
            location.originally_held, WeddingGearPrize
        ) and not world.settings.isflag_enabled(ShuffleWeddingGear):
            return False
        if (
            issubclass(location.originally_held, SpellPrize)
            and not world.settings.isflag_enabled(CharacterLearnedSpells)
            and not world.settings.isflag_enabled(SpellsAnywhere)
        ):
            return False
        if issubclass(
            location.originally_held, RegularFireworksPrize
        ) and world.settings.is_flag_value(FireworksSetting, FireworksOptions.VANILLA):
            return False
    if not world.is_location_enabled(type(location)):
        return False
    if location.originally_held == SuperSuitPrize and world.settings.is_flag_value(
        SuperJump2Threshold, 100
    ):
        roll = random.randint(0, 1)
        if roll == 1:
            return False
    return True


def _maybe_replace_bad_item_with_coin(prize: "Prize", world: GameWorld) -> "Prize":
    """Swap the worst consumables for coins worth their price when ReplaceItems
    is on. Independent of ShuffleItems: a vanilla-placed chest item is eligible
    too. Non-item prizes (bosses, characters, key items, good items) pass through.
    """
    if not (
        world.settings.isflag_enabled(ReplaceItems) and isinstance(prize, ItemPrize)
    ):
        return prize
    item = prize.item
    if issubclass(
        item,
        (
            MushroomItem,
            HoneySyrupItem,
            AbleJuiceItem,
            YoshiCookieItem,
            PureWaterItem,
            FroggieDrinkItem,
            WiltShroomItem,
            RottenMushItem,
            MoldyMushItem,
        ),
    ) or (
        issubclass(item, MushroomItem2)
        and Status.INVINCIBLE
        not in world.get_item(MushroomItem2).status_immunities
    ):
        return CoinPrize(world.get_item(item).price)
    return prize


def pull_prize(location: PrizeLocation, world: GameWorld) -> Prize | None:
    # empty locations don't return anything
    if location.originally_held is None:
        return None
    if issubclass(location.originally_held, SpellPrize):
        return None
    if issubclass(
        location.originally_held, SeeYaPrize
    ) and world.settings.isflag_enabled(SeeYa):
        return None
    # always return the original prize if shuffling disabled so that it can receive its original prize during placement
    # this should happen regardless of item shuffler pool settings
    if not should_shuffle(location, world):
        return location.originally_held()
    inclusions = shuffle_rules(world)
    if issubclass(location.originally_held, (StarPiecePrize, CharacterPrize)):
        for _, classes in inclusions.items():
            for cls in classes:
                if issubclass(location.originally_held, cls):
                    return cls()
        return None
    if issubclass(
        location.originally_held, RegularFireworksPrize
    ) and world.settings.is_flag_value(FireworksSetting, FireworksOptions.PROGRESSIVE):
        return ProgressiveFireworksPrize()
    if issubclass(
        location.originally_held, StarEggPrize
    ) and world.settings.isflag_enabled(NoStarEgg):
        return None
    if issubclass(location.originally_held, (CharacterPrize, StarPiecePrize)):
        for tier in inclusions.values():
            for prize_cls in tier:
                if issubclass(location.originally_held, prize_cls):
                    return location.originally_held()
        return None
    if isinstance(
        location,
        (
            TreasureChestLocation,
            StandingLocation,
            EventLocation,
            RiverLocation,
            BoosterHillLocation,
        ),
    ):
        for tier, prizes in inclusions.items():
            for prize_cls in prizes:
                if tier == LOW_PRIORITY and world.settings.is_flag_value(
                    ItemQuality, ItemQualityOptions.COMPLETELY_EMPTY
                ):
                    return None
                if issubclass(location.originally_held, prize_cls):
                    return location.originally_held()
        if world.settings.is_flag_value(
            ItemQuality, ItemQualityOptions.COMPLETELY_EMPTY
        ):
            return None

        if world.settings.is_flag_value(ItemQuality, ItemQualityOptions.ORIGINAL_POOL):
            prize = location.originally_held()
        else:
            prize = RandomPrizeSubstitute().generate(world, location)

        prize = _maybe_replace_bad_item_with_coin(prize, world)
        return prize

    return location.originally_held()


def remove_prize_from_pool(
    pool: dict[int, list[Prize]], prize_class: type[Prize], world: GameWorld
) -> None:
    """Remove the first instance of a prize class from the pool dict.

    Traverses all tiers in the pool dict and removes the first prize that is an
    instance of the specified class.

    Args:
        pool: The pool dict mapping tier IDs to lists of Prize instances.
        prize_class: The prize class to remove an instance of.

    Returns:
        True if an instance was found and removed, False otherwise.
    """
    for tier in pool:
        for i, prize in enumerate(pool[tier]):
            if isinstance(prize, prize_class):
                pool[tier].pop(i)
                return
    # certain force-included debug items that aren't normally found in a prize location are fine
    pr = prize_class()
    if isinstance(pr, ItemPrize) and world.get_item(pr.item).price > 0:
        return
    raise ValueError(
        f"Prize of class {prize_class} not found in pool when attempting to remove. Was it already set to a debug location?"
    )


def _build_priority_classes(world: GameWorld) -> set[type[Prize]]:
    """Build the set of high-unlock-volume prize types for priority placement.

    These items unlock many downstream checks, so they should be placed
    earlier and spread throughout the placement order rather than clumping
    at the end.
    """
    priority: set[type[Prize]] = {
        BambinoBombPrize,
        CastleKey1Prize,
        CastleKey2Prize,
        GoldPaintPrize,
        StayVoucherPrize,
        TempleKeyPrize,
    }

    # MarioDollPrize if Booster Tower completion gates downstream areas
    if world.settings.is_flag_value(
        BoosterHillGate, BoosterHillGating.TOWER
    ) or world.settings.is_flag_value(MarrymoreGate, MarrymoreGating.TOWER):
        priority.add(MarioDollPrize)

    # Star pieces if any area is star-gated
    if (
        world.settings.is_flag_value(SeaGate, SeaGating.STAR_4)
        or world.settings.is_flag_value(LandsEndGate, LandsEndGating.STAR_5)
        or world.settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.STAR_6)
        or world.settings.is_flag_value(FactoryGate, FactoryGating.STAR_6)
    ):
        priority.add(StarPiecePrize)

    # Boss fights that are required for gating in AreaAccessSubcategory flags
    boss_gating: list[tuple[type, object, type[Prize]]] = [
        (BanditsWayGate, BanditsWayGating.HAMMER_BRO, HammerBrosFight),
        (KeroSewersGate, KeroSewersGating.MACK, MackBossFight),
        (PipeVaultGate, PipeVaultGating.BOWYER, BowyerBossFight),
        (Moleville1Gate, Moleville1Gating.BOWYER, BowyerBossFight),
        (BoosterTowerGate, BoosterTowerGating.PUNCHINELLO, PunchinelloBossFight),
        (BoosterHillGate, BoosterHillGating.KGGG, KnifeGuyGrateGuyBossFight),
        (MarrymoreGate, MarrymoreGating.KGGG, KnifeGuyGrateGuyBossFight),
        (SeaGate, SeaGating.BUNDT, BundtBossFight),
        (YaridovichGate, YaridovichGating.JOHNNY, JohnnyBossFight),
        (LandsEndGate, LandsEndGating.YARIDOVICH, YaridovichBossFight),
        (MonstroTownGate, MonstroTownGating.BELOME_2, Belome2BossFight),
        (NimbusGate, NimbusGating.MEGASMILAX, MegasmilaxBossFight),
        (BarrelVolcanoGate, BarrelVolcanoGating.VALENTINA, ValentinaBossFight),
        (BowsersKeepGate, BowsersKeepGating.AXEM, AxemRangersBossFight),
    ]
    for gate, gating_value, boss_prize in boss_gating:
        if world.settings.is_flag_value(gate, gating_value):
            priority.add(boss_prize)

    if world.settings.is_flag_value(LandsEndGate, LandsEndGating.ELDER):
        priority.add(ShedKeyPrize)

    if world.settings.is_flag_value(KeroSewersGate, KeroSewersGating.RFC):
        priority.add(RareFrogCoinPrize)

    if world.settings.is_flag_value(ForestMazeGate, ForestMazeGating.PIE):
        priority.add(CricketPiePrize)

    # Characters that are required by active gating settings (gate-critical)
    character_gating: list[tuple[type, object, type[Prize]]] = [
        (BanditsWayGate, BanditsWayGating.MALLOW, MallowRecruitmentPrize),
        (KeroSewersGate, KeroSewersGating.MALLOW, MallowRecruitmentPrize),
        (BoosterTowerGate, BoosterTowerGating.MALLOW, MallowRecruitmentPrize),
        (PipeVaultGate, PipeVaultGating.GENO, GenoRecruitmentPrize),
        (Moleville1Gate, Moleville1Gating.GENO, GenoRecruitmentPrize),
        (BoosterTowerGate, BoosterTowerGating.GENO, GenoRecruitmentPrize),
        (BoosterTowerGate, BoosterTowerGating.MARIO, MarioRecruitmentPrize),
        (BoosterTowerGate, BoosterTowerGating.TOADSTOOL, ToadstoolRecruitmentPrize),
        (SeaGate, SeaGating.TOADSTOOL, ToadstoolRecruitmentPrize),
        (BoosterTowerGate, BoosterTowerGating.BOWSER, BowserRecruitmentPrize),
    ]
    for gate, gating_value, char_prize in character_gating:
        if world.settings.is_flag_value(gate, gating_value):
            priority.add(char_prize)

    return priority


def shuffle_prizes(world: GameWorld) -> None:
    # Force-enable location-freeing flags for prize offset mode BEFORE the pool
    # is built, so non-shuffled vanilla mimic/slot/etc. chests become shuffled
    # and the pool builder doesn't pre-bind their originally-held prizes to them.
    if world.settings.debug_mode and world.settings.prize_offset is not None:
        # Any chest-targeting override (slots, mimics or coins) can land on a
        # vanilla mimic/slot/exp-star/magikoopa chest, so all four chest-freeing
        # flags are needed as soon as *one* of those categories is on. With all
        # three off, leave the player's own flags alone so those chests shuffle
        # exactly as their settings say.
        if (
            world.settings.offset_slots
            or world.settings.offset_mimics
            or world.settings.offset_coins
        ):
            # MimicsAnywhere must be enabled BEFORE the pool builder runs so the
            # vanilla mimic chests (e.g., KeroSewersStairRoomRightChestLocation)
            # are treated as shuffleable. Otherwise the pool builder binds
            # FirstMimicFightLauncher to the vanilla chest, and after our mimic
            # override steals it, the vanilla chest is left empty.
            world.settings._flags[MimicsAnywhere] = MimicsAnywhere(True)
            # SlotsAnywhere/EXPStarsAnywhere/ShuffleMagikoopaChest were added in
            # 3bbe42a6 and silently dropped by 0bda84c3 ("config fix") when the
            # MimicsAnywhere force-enable was hoisted above the pool builder.
            # Without them, vanilla slot/exp-star/magikoopa chests stay
            # not-shuffleable, the pool builder pre-binds their originally_held
            # prizes, and any duplicate of those classes ends up in LOW_PRIORITY
            # - which is how slot/exp-star prizes silently leak into chests the
            # offset preview never showed.
            world.settings._flags[SlotsAnywhere] = SlotsAnywhere(True)
            world.settings._flags[EXPStarsAnywhere] = EXPStarsAnywhere(True)
            world.settings._flags[ShuffleMagikoopaChest] = ShuffleMagikoopaChest(True)
            for _msg in (
                "Mimics can appear anywhere: forced ON",
                "Slots can appear anywhere: forced ON",
                "EXP stars can appear anywhere: forced ON",
                "Magikoopa chest shuffled: forced ON",
            ):
                world.settings.force_override(_msg)
        # ShuffleStarPieces gates whether the offset's star piece overrides
        # actually flow through to placement and signal-ring patching. Without
        # it, TotalStarPieces is treated as default (6) and the UI offset
        # preview diverges from the seed's real star piece placements.
        if world.settings.offset_star_pieces:
            world.settings._flags[ShuffleStarPieces] = ShuffleStarPieces(True)
            world.settings.force_override("Shuffle star pieces: forced ON")
        world.settings._is_flag_value_cache.clear()

    # NOTE: gate relaxation deliberately does NOT happen here. Gates are baked
    # into ROM state by apply_shuffler_independent_settings long before the
    # shuffler runs, so they must be settled before that - see
    # GameWorld._shuffle_items, which calls relax_deadlocked_gates() and rebuilds
    # the world if anything changed.

    pool: dict[int, list[Prize]] = {
        PROGRESSION_PRIZES: [],
        RESTRICTED_PRIZES: [],
        MANDATORY_INCLUSIONS: [],
        LOW_PRIORITY: [],
    }
    # Always have 3 progressive eggs if item shuffle is enabled
    if world.settings.isflag_enabled(ShuffleItems):
        pool[MANDATORY_INCLUSIONS].extend(
            [ProgressiveEggPrize(), ProgressiveEggPrize()]
        )
        if not world.settings.is_flag_value(ShopQuality, ShopQualities.ORIGINAL):
            pool[MANDATORY_INCLUSIONS].extend(
                [
                    JumpShoesPrize(),
                    BtubRingPrize(),
                ]
            )

    world._spell_assignments = None
    # Reset the cached character roster so this attempt re-rolls the random fill
    # (retries should get a fresh roster), but stays stable across the many
    # shuffle_rules() calls within this attempt.
    world._cached_char_fill = None
    world._cached_spell_damage_char = None
    world._cached_spells = None
    world._cached_starting_chars = None
    # Fresh least-used ledger per attempt, so a retry re-deals the substitute
    # fill instead of inheriting the previous attempt's usage counts.
    world.substitute_draw_counts = {}

    rules = shuffle_rules(world)

    all_locations = list(world.locations.values())

    pre_seeded = sum(len(p) for p in pool.values())

    # Spells are a special case - added from rules, not pulled from locations
    spell_count = 0
    for tier, classes in rules.items():
        for cls in classes:
            if issubclass(cls, SpellPrize):
                pool[tier].append(cls())
                spell_count += 1

    pulled_count = 0
    for loc in all_locations:
        loc.set_prize(None)
        pool_item = pull_prize(loc, world)

        if pool_item is None:
            continue
        pulled_count += 1

        included = False
        for tier, classes in rules.items():
            if any(isinstance(pool_item, cls) for cls in classes):
                pool[tier].append(pool_item)
                included = True
                break
        if not included:
            if world.settings.is_flag_value(
                ItemQuality, ItemQualityOptions.ORIGINAL_POOL
            ):
                pool[MANDATORY_INCLUSIONS].append(pool_item)
            else:
                pool[LOW_PRIORITY].append(pool_item)

    # Track chest location classes that got offset-placed slot/mimic prizes, so
    # config.yml overrides later can skip these locations (otherwise config.yml
    # would overwrite the offset placements).
    offset_reserved_chest_classes: set[type] = set()

    # Apply offset-based overrides: when prize_offset is set, compute boss and slot
    # assignments from the offset and pre-place them. This runs before config.yml
    # overrides so offset takes precedence for boss fights and slots.
    # (Flag overrides for this mode were already applied at the top of shuffle_prizes
    # so the pool builder treats mimic/slot/etc. vanilla chests as shuffleable.)
    if world.settings.debug_mode and world.settings.prize_offset is not None:
        total_sp = (
            world.settings.get_flag(TotalStarPieces).value
            if world.settings.offset_star_pieces
            else 0
        )
        offset_result = compute_offset_assignments(
            world.settings.prize_offset,
            mimic_offset=world.settings.mimic_offset,
            total_star_pieces=total_sp,
            enable_slots=world.settings.offset_slots,
            enable_mimics=world.settings.offset_mimics,
            enable_coins=world.settings.offset_coins,
            win_condition=world.settings.get_flag(WinCondition).selected.name,
        )

        # Boss overrides: {location_class_name: prize_class}
        for loc_name, prize_cls in offset_result["boss_overrides"].items():
            for loc in world.locations.values():
                if type(loc).__name__ == loc_name:
                    loc.set_prize(prize_cls())
                    break
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

        # Slot overrides: [(chest_class, slots_prize_class), ...]
        for chest_cls, slots_prize_cls in offset_result["slot_overrides"]:
            offset_reserved_chest_classes.add(chest_cls)
            for loc in world.locations.values():
                if isinstance(loc, chest_cls):
                    loc.set_prize(slots_prize_cls())
                    break
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == slots_prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

        # Mimic overrides: [(chest_class, mimic_prize_class), ...]
        # Mimic launcher placement requires _on_item_placed() to update the
        # _world_area on Mimic1BossFight / DropReward / StarPiece / ReloadReward
        # locations, which affects accessibility.
        for chest_cls, mimic_prize_cls in offset_result["mimic_overrides"]:
            offset_reserved_chest_classes.add(chest_cls)
            placed_prize = mimic_prize_cls()
            placed_at = None
            for loc in world.locations.values():
                if isinstance(loc, chest_cls):
                    loc.set_prize(placed_prize)
                    placed_at = loc
                    break
            if placed_at is not None:
                _on_item_placed(world, placed_prize, placed_at)
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == mimic_prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

        # Coin override: [(chest_class, InfiniteCoinsPrize)] - one chest per offset.
        for chest_cls, coin_prize_cls in offset_result["coin_overrides"]:
            offset_reserved_chest_classes.add(chest_cls)
            for loc in world.locations.values():
                if isinstance(loc, chest_cls):
                    loc.set_prize(coin_prize_cls())
                    break
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == coin_prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

        # Star piece overrides: [(star_piece_location_class, star_piece_prize_class), ...]
        # Lock TotalStarPieces star pieces to specific boss-fight star piece locations
        # so the offset slider also rotates star piece placements deterministically.
        for sp_loc_cls, sp_prize_cls in offset_result["star_piece_overrides"]:
            placed_at_location = False
            for loc in world.locations.values():
                if isinstance(loc, sp_loc_cls):
                    loc.set_prize(sp_prize_cls())
                    placed_at_location = True
                    break
            if not placed_at_location:
                # The target location isn't in this world (win-condition-dependent
                # locations are dropped by the pre-shuffler). Leaving the pool pop
                # below unguarded deleted the star piece without ever placing it;
                # instead leave it in the pool so it shuffles normally.
                continue
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == sp_prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

    # Apply debug overrides: place the specified prize at each override location
    # and remove one instance of that prize class from the pool.
    # This happens after pool building so all prizes are in the pool normally.
    # The shuffler will see these locations as already occupied and skip them.
    if world.settings.debug_mode:
        config = load_debug_config()
        overrides = config.get("items", {}).get("override", {})
        for location_name, prize_name in overrides.items():
            location_cls = get_location_class(location_name)
            prize_cls = get_prize_class(prize_name)
            if location_cls is None:
                raise ValueError(f"Invalid location name in debug config: '{location_name}'")
            if prize_cls is None:
                raise ValueError(f"Invalid prize name in debug config: '{prize_name}'")
            # Skip boss/slot/mimic overrides if prize_offset is active (offset takes
            # precedence). A category switched off in the offset UI is not offset-driven,
            # so config.yml is back in charge of it.
            if world.settings.prize_offset is not None:
                if (issubclass(location_cls, BossFightLocation)
                        or (world.settings.offset_slots and issubclass(prize_cls, SlotsPrizeBase))
                        or (world.settings.offset_mimics and issubclass(prize_cls, MimicBase))):
                    continue
                # Also skip locations where the offset code already placed a
                # slot or mimic prize - otherwise config.yml would overwrite
                # that placement with a different prize.
                if location_cls in offset_reserved_chest_classes:
                    continue
            for loc in world.locations.values():
                if isinstance(loc, location_cls):
                    loc.set_prize(prize_cls())
                    break
            removed = False
            for tier_list in pool.values():
                for i, item in enumerate(tier_list):
                    if type(item) == prize_cls:
                        tier_list.pop(i)
                        pulled_count -= 1
                        removed = True
                        break
                if removed:
                    break

    pool_total = sum(len(p) for p in pool.values())
    if pool_total != pre_seeded + spell_count + pulled_count:
        pool_contents: dict[str, int] = {}
        for tier_prizes in pool.values():
            for p in tier_prizes:
                name = type(p).__name__
                pool_contents[name] = pool_contents.get(name, 0) + 1
        if world.settings.debug_mode:
            debug_print(f"[DEBUG] Full pool contents: {dict(sorted(pool_contents.items()))}")
    # remove slot machine npcs from their original rooms
    room_334 = world.rooms._rooms[334]
    assert room_334 is not None, "Room 334 not found"
    for npc_target in [NPC_2, NPC_3, NPC_4, NPC_5, NPC_6]:
        npc = room_334.get_npc_by_target_id(npc_target)
        assert npc is not None, f"NPC {npc_target} not found in room 334"
        npc._npc = EMPTY_NPC
    room_348 = world.rooms._rooms[348]
    assert room_348 is not None, "Room 348 not found"
    for npc_target in [NPC_2, NPC_3, NPC_4, NPC_5, NPC_6]:
        npc = room_348.get_npc_by_target_id(npc_target)
        assert npc is not None, f"NPC {npc_target} not found in room 348"
        npc._npc = EMPTY_NPC
    room_349 = world.rooms._rooms[349]
    assert room_349 is not None, "Room 349 not found"
    for npc_target in [NPC_3, NPC_4, NPC_5, NPC_6, NPC_7]:
        npc = room_349.get_npc_by_target_id(npc_target)
        assert npc is not None, f"NPC {npc_target} not found in room 349"
        npc._npc = EMPTY_NPC

    starting_char_locations: dict[type, int] = {
        StartingCharacter1: 0,
        StartingCharacter2: 1,
        StartingCharacter3: 2,
        StartingCharacter4: 3,
        StartingCharacter5: 4,
    }

    ally_name_to_prize: dict[str, type[CharacterPrize]] = {
        "Mario": MarioRecruitmentPrize,
        "Mallow": MallowRecruitmentPrize,
        "Geno": GenoRecruitmentPrize,
        "Bowser": BowserRecruitmentPrize,
        "Toadstool": ToadstoolRecruitmentPrize,
    }

    # Resolved once per attempt in shuffle_rules, against the roster, so every
    # starter here is a character this seed actually contains. Re-resolving would
    # roll a different party than the roster and spell pool were built for.
    resolved_starting_chars = world._cached_starting_chars
    assert (
        resolved_starting_chars is not None
    ), "shuffle_rules must resolve starting characters before placement"

    for loc in world.locations.values():
        if isinstance(loc, StartingCharacterLocation):
            loc_idx = starting_char_locations.get(type(loc))
            if loc_idx is not None and loc_idx < len(resolved_starting_chars):
                ally = resolved_starting_chars[loc_idx]
                prize_cls = ally_name_to_prize[ally.name]
                char_in_pool = any(
                    isinstance(p, prize_cls) for tier in pool.values() for p in tier
                )
                if not char_in_pool:
                    raise ValueError(
                        f"Starting character '{ally.name}' is not in the prize pool. "
                        f"The starter roster and the character roster have diverged."
                    )
                loc.set_prize(prize_cls())
                remove_prize_from_pool(pool, prize_cls, world)
            # Slots past the end of the enabled starter list hold nothing.
            continue

        elif not should_shuffle(loc, world):
            if loc.originally_held is not None:
                # Excluded characters/star pieces/spells won't be in the pool
                prize_exists_in_pool = any(
                    isinstance(p, loc.originally_held)
                    for tier in pool.values()
                    for p in tier
                )
                if prize_exists_in_pool:
                    prize = loc.originally_held()
                    # ReplaceItems runs even without item shuffle: swap the worst
                    # consumables for coins wherever a coin can actually be held
                    # (chests, most NPC/event spots). A location that can't grant
                    # a coin - e.g. StartingItem - keeps its item.
                    swapped = _maybe_replace_bad_item_with_coin(prize, world)
                    if swapped is not prize and not loc.can_accept(
                        swapped, Inventory(), world
                    ):
                        swapped = prize
                    loc.set_prize(swapped)
                    remove_prize_from_pool(pool, loc.originally_held, world)

    # shuffled twice on purpose. A dropped experiment used to sit between these
    # two passes, and the second one is now redundant, but dropping it shifts
    # every subsequent random() draw and so changes every existing seed.
    for prizes in pool.values():
        random.shuffle(prizes)

    for prizes in pool.values():
        random.shuffle(prizes)

    # Snapshot pool before placement (item names per tier, for debug dump)
    pool_before: dict[int, list[str]] = {
        tier: [type(p).__name__ for p in prizes] for tier, prizes in pool.items()
    }

    # Snapshot pool before placement for post-placement diff
    pool_snapshot: dict[str, int] = {}
    for tier_prizes in pool.values():
        for p in tier_prizes:
            name = type(p).__name__
            pool_snapshot[name] = pool_snapshot.get(name, 0) + 1
    # Also count items placed during static fills (debug/unshuffled)
    static_placed: dict[str, int] = {}
    for loc in world.locations.values():
        if loc.has_item:
            name = type(loc.prize).__name__
            static_placed[name] = static_placed.get(name, 0) + 1
    pool_plus_static: dict[str, int] = dict(pool_snapshot)
    for name, count in static_placed.items():
        pool_plus_static[name] = pool_plus_static.get(name, 0) + count

    shuffle_filter = lambda loc: should_shuffle(loc, world)
    priority_classes = _build_priority_classes(world)

    # Key-item pool health. With KeyItemsAnywhere off, key items may only go in
    # key-item locations, 1:1, so guard the count invariant, then - under POP -
    # open gates if boss pinning islanded some key slots (see solvability.py).
    # With KeyItemsAnywhere on, key items are ordinary items placed by the
    # general fill into any location, so the key-slot accounting is meaningless
    # and would false-positive whenever a key location gets filled by non-key
    # filler (e.g. a debug override) - skip the whole guard.
    if not world.settings.isflag_enabled(KeyItemsAnywhere):
        all_pool = [p for prizes in pool.values() for p in prizes]
        key_pool = [p for p in all_pool if isinstance(p, KeyPrize)]
        non_key_pool = [p for p in all_pool if not isinstance(p, KeyPrize)]
        assert_key_pool_balanced(world, key_pool)
        key_gate_changes = relax_key_pool_deadlock(world, key_pool, non_key_pool)
        if key_gate_changes:
            for message in key_gate_changes:
                world.settings.force_override(message)
            # Gates are baked into ROM by the pre-shuffler, so rebuild the world
            # for the change to reach the game and not just placement (see
            # _shuffle_items).
            raise SettingsRelaxed(key_gate_changes)
        assert_key_pool_placeable(world, key_pool, non_key_pool)

    # Win condition "Beat Smithy": defeating Smithy ends the game the instant it
    # happens, so nothing is ever gated behind him. Pull his fight out of the pool
    # and place it in its own pass AFTER every accessibility-relevant prize (below,
    # just before the LOW_PRIORITY filler pass that unlocks nothing). Every other
    # location is therefore filled and proven reachable without beating Smithy, so
    # his slot can block nothing. Placement is 1:1 boss-prize -> boss-location and
    # BossFightLocation rejects non-boss prizes, so the leftover boss slot stays
    # reserved until the dedicated pass. If an attempt leaves only a stranding slot
    # for him, that pass raises PlacementException and _shuffle_items re-rolls.
    # (Only fires when Smithy is actually in the boss pool, i.e. BossShuffle is on;
    # otherwise he keeps his vanilla location and this is a no-op.)

    deferred_smithy: Prize | None = None
    if world.settings.is_flag_value(WinCondition, WinConditions.SMITHY):
        for tier_list in pool.values():
            for i, item in enumerate(tier_list):
                if isinstance(item, SmithyBossFight):
                    deferred_smithy = tier_list.pop(i)
                    break
            if deferred_smithy is not None:
                break

    try:
        place(
            world,
            pool[PROGRESSION_PRIZES],
            on_placed=lambda i, l: _on_item_placed(world, i, l),
            location_filter=shuffle_filter,
            priority_classes=priority_classes,
        )

        # Debug: check which locations are still inaccessible after progression placement
        player_has = collect_accessible_items(world)
        inaccessible = [
            loc
            for loc in world.locations.values()
            if should_shuffle(loc, world) and not loc.can_access(player_has, world)
        ]
        non_spell_inaccessible = [
            l for l in inaccessible if not isinstance(l, SpellSlotLocation)
        ]
        if world.settings.debug_mode:
            if non_spell_inaccessible:
                debug_print(
                    f"[DEBUG] After progression placement: {len(non_spell_inaccessible)} non-SpellSlot locations still inaccessible:"
                )
                for loc in non_spell_inaccessible:
                    debug_print(f"[DEBUG]   {type(loc).__name__}")
            else:
                debug_print(
                    f"[DEBUG] After progression placement: {len(inaccessible)} inaccessible locations, all SpellSlotLocations"
                )

        place(
            world,
            pool[RESTRICTED_PRIZES],
            on_placed=lambda i, l: _on_item_placed(world, i, l),
            location_filter=shuffle_filter,
        )
        place(
            world,
            pool[MANDATORY_INCLUSIONS],
            on_placed=lambda i, l: _on_item_placed(world, i, l),
            force_frog_disciple=True,
            location_filter=shuffle_filter,
        )
        # Dead last among everything that affects accessibility: the Smithy fight
        # (WinCondition == SMITHY). Runs before LOW_PRIORITY so the reserved boss
        # slot is filled before that pass's overflow check, and because LOW_PRIORITY
        # is pure filler that unlocks nothing.
        if deferred_smithy is not None:
            place(
                world,
                [deferred_smithy],
                on_placed=lambda i, l: _on_item_placed(world, i, l),
                location_filter=shuffle_filter,
            )
        place(
            world,
            pool[LOW_PRIORITY],
            can_overflow=True,
            on_placed=lambda i, l: _on_item_placed(world, i, l),
            location_filter=shuffle_filter,
        )
    except PlacementException as e:
        if DEBUG_FILE_DUMPS:
            _dump_placement_failure(world, pool_before, e.unplaced_items, priority_classes)
        raise

    # Post-placement diff: collect all items from every location and compare to pool snapshot
    placed_items: dict[str, int] = {}
    for loc in world.locations.values():
        if loc.has_item:
            name = type(loc.prize).__name__
            placed_items[name] = placed_items.get(name, 0) + 1
    total_after = sum(placed_items.values())
    if world.settings.debug_mode:
        debug_print(f"[DEBUG] Items in locations after placement: {total_after}")

        all_keys = sorted(set(pool_plus_static.keys()) | set(placed_items.keys()))
        diffs: list[str] = []
        for key in all_keys:
            before = pool_plus_static.get(key, 0)
            after = placed_items.get(key, 0)
            if before != after:
                diffs.append(
                    f"  {key}: pool+static={before}, placed={after} (diff={after - before:+d})"
                )
        if diffs:
            debug_print(f"[DEBUG] POOL vs PLACED DIFF ({len(diffs)} mismatches):")
            for d in diffs:
                debug_print(f"[DEBUG] {d}")
        else:
            debug_print(f"[DEBUG] Pool and placed items match perfectly.")


def assign_spell_prize_models(world: GameWorld) -> None:
    """Assign spell prize models and packet data based on their element.

    This sets the visual appearance (colored orb) for spell prizes when they
    appear as freestanding items in the overworld:
    - Thunder spells → Yellow orb (SPR0218_YELLOW_BALL)
    - Fire spells → Red orb (SPR0214_RED_BALL)
    - Ice spells → Blue orb (SPR0215_BLUE_BALL)
    - Jump/Earth spells → Green orb (SPR0217_GREEN_BALL)
    - No element spells → Gray orb (SPR0224_GRAY_BALL)

    Also sets packet_data to (sprite_id, 0) for each spell prize based on element.

    Must run after spell elements are finalized and after prizes are shuffled into locations.
    """

    # Iterate through all locations to find spell prizes
    for location in world.locations.values():
        if not location.has_item:
            continue

        prize = location.prize
        if not isinstance(prize, SpellPrize):
            continue

        # Get the actual spell instance from world with its finalized element
        spell_instance = world.get_spell(prize.spell)  # type: ignore

        # Map element to orb model and packet sprite
        if spell_instance.element == Element.THUNDER:
            prize.set_model(YellowSpellObject)
            prize._packet_data = (SPR0218_YELLOW_BALL, 0)
        elif spell_instance.element == Element.FIRE:
            prize.set_model(FireSpellObject)
            prize._packet_data = (SPR0214_RED_BALL, 0)
        elif spell_instance.element == Element.ICE:
            prize.set_model(BlueSpellObject)
            prize._packet_data = (SPR0215_BLUE_BALL, 0)
        elif spell_instance.element == Element.JUMP:
            prize.set_model(GreenSpellObject)
            prize._packet_data = (SPR0217_GREEN_BALL, 0)
        else:  # Element.NONE
            prize.set_model(GraySpellObject)
            prize._packet_data = (SPR0224_GRAY_BALL, 0)


def apply_debug_overrides(world: GameWorld) -> None:
    """Apply debug item diagnostics after shuffling.

    Overrides are now applied BEFORE shuffling in shuffle_prizes() so that
    overridden locations are excluded from the pool and don't cause duplicates.
    This function only handles diagnostics.
    """

    if not world.settings.debug_mode:
        return

    # Overrides are now applied pre-shuffle in shuffle_prizes().
    # Just track which locations were overridden for diagnostics.
    config = load_debug_config()
    overrides = config.get("items", {}).get("override", {})
    debug_locations: set[type[PrizeLocation]] = set()
    for location_name in overrides.keys():
        location_cls = get_location_class(location_name)
        if location_cls is not None:
            debug_locations.add(location_cls)
    world._debug_locations = debug_locations
    diagnose_empty_locations(world)


def post_shuffle_cleanup(world: GameWorld) -> None:
    """Handle empty chests and replace low-value items with coins.

    This function:
    1. Applies debug overrides (if debug mode enabled)
    2. Assigns spell prize models based on finalized elements
    3. Fills or disables empty treasure chests based on settings
    4. Replaces low-impact items with coin prizes at half their price
    """

    # Apply debug overrides (replaces shuffled prizes at configured locations)
    apply_debug_overrides(world)

    # Assign spell prize models based on their finalized elements
    assign_spell_prize_models(world)

    # Replace as necessary
    for loc in [
        s for s in world.locations.values() if isinstance(s, TreasureChestLocation)
    ]:
        if not loc.has_item:
            if world.settings.isflag_enabled(AnnoyingChests):
                loc.set_prize(YouMissed())
            else:
                disable = zip(loc._rooms, loc._npc_ids)
                for room, npc in disable:
                    world.event_2496_startup.append(
                        DisableObjectTriggerInSpecificLevel(npc, room)
                    )

    # Verify that all locations that need prizes are filled
    for loc in world.locations.values():
        if loc.has_item:
            continue
        if loc.can_be_empty(world):
            continue  # Location is allowed to be empty
        debug_print(f"Error: Location {loc} is empty but cannot be empty based on settings")
        raise PlacementException(0, [])

    for loc in [
        s
        for s in world.locations.values()
        if s.has_item
        and isinstance(s, StandardPrizeLocation)
        and not isinstance(s, RiverLocation)
    ]:
        if isinstance(loc.prize, ItemPrize) and (
            isinstance(
                loc.prize,
                (
                    MushroomItem,
                    HoneySyrupItem,
                    AbleJuiceItem,
                    YoshiCookieItem,
                    PureWaterItem,
                    FroggieDrinkItem,
                    WiltShroomItem,
                    RottenMushItem,
                    MoldyMushItem,
                    MushroomItem2,
                ),
            )
            or (
                not world.settings.is_flag_value(
                    EquipmentProperties, EquipmentPropertiesOptions.SOME
                )
                and type(loc.prize) in world.low_impact_equip
            )
        ):
            if isinstance(loc, StandingLocation):
                loc.set_prize(Coins10Prize())
            else:
                loc.set_prize(CoinPrize(world.get_item(loc.prize.item).price // 2))

    if world.settings.isflag_enabled(StarPieceHints):
        for l in world.locations.values():
            if not isinstance(l.prize, StarPiecePrize):
                continue
            event = SIGNAL_RING_EVENT_DICT[l.world_area]
            script = world.event_scripts.get_script_by_id(event)
            assert (
                script is not None
            ), f"Event script {event} not found for StarPieceHints"
            script.insert_before_nth_command(
                0, JmpIfBitClear(l.prize._hint, [f"EVENT_{event}_play_sound"])
            )
    else:
        world.event_scripts.delete_command_by_identifier("star_hill_set_checked_with_sr")
