from __future__ import annotations
from typing import Any, cast, TypeVar
from .flags import *
from .check_flags import *
from .flag_categories import *
import re


class RandomizerSettingsException(Exception):
    """Exception raised for settings-related errors."""
    pass

B64_TABLE: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


FlagT = TypeVar("FlagT", bound=Flag)

class Settings:
    _debug_mode: bool = False
    _prize_offset: int | None = None
    _mimic_offset: int | None = None
    offset_slots: bool = True
    offset_mimics: bool = True
    offset_coins: bool = True
    offset_star_pieces: bool = True
    offset_invisible_flags: bool = True
    _flags: dict[type[Flag], Flag]
    _override: dict = {}
    _is_flag_value_cache: dict[tuple[type[Flag], Any], bool]
    forced_overrides: list[str]

    @property
    def debug_mode(self) -> bool:
        """Whether debug mode is enabled."""
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        self._debug_mode = value

    @property
    def prize_offset(self) -> int | None:
        """Prize offset for deterministic placement (dev-only). None means disabled."""
        return self._prize_offset

    @prize_offset.setter
    def prize_offset(self, value: int | None) -> None:
        self._prize_offset = value

    @property
    def mimic_offset(self) -> int | None:
        """Independent offset for mimic fight placement (dev-only). None means fall back to prize_offset for mimics."""
        return self._mimic_offset

    @mimic_offset.setter
    def mimic_offset(self, value: int | None) -> None:
        self._mimic_offset = value

    @property
    def override(self) -> dict:
        """Override certain settings (developer mode)"""
        return self._override

    @property
    def flag_string(self) -> str:
        """Computed flag string for these settings."""
        return self.get_flag_string_without_cosmetics()

    def __init__(self) -> None:
        self._is_flag_value_cache = {}
        self.forced_overrides = []
        self._flags = {
            ShuffleCharacters: ShuffleCharacters(),
            MaxCharacters: MaxCharacters(),
            AllowAllySwitching: AllowAllySwitching(),
            StartingCharacters: StartingCharacters(),
            PlayAsStarter: PlayAsStarter(),
            EquipmentCharacters: EquipmentCharacters(),
            EquipmentProperties: EquipmentProperties(),
            IgnoreNamesakeProperties: IgnoreNamesakeProperties(),
            StarPieceHints: StarPieceHints(),
            EXPMultiplier: EXPMultiplier(),
            CharacterStats: CharacterStats(),
            CharacterLearnedSpells: CharacterLearnedSpells(),
            CharacterSpellStats: CharacterSpellStats(),
            InfuseSpellElements: InfuseSpellElements(),
            CharacterSpellElements: CharacterSpellElements(),
            UncapSuperJumps: UncapSuperJumps(),
            UncapMaxFP: UncapMaxFP(),
            AvailableSpells: AvailableSpells(),
            AvailableCharacters: AvailableCharacters(),
            ShuffleStarPieces: ShuffleStarPieces(),
            TotalStarPieces: TotalStarPieces(),
            EnabledBossChecks: EnabledBossChecks(),
            ProgressionLogicDifficulty: ProgressionLogicDifficulty(),
            DisperseStarPieces: DisperseStarPieces(),
            ShuffleItems: ShuffleItems(),
            ItemQuality: ItemQuality(),
            BiasItemShuffle: BiasItemShuffle(),
            NoStarEgg: NoStarEgg(),
            RestrictSpecialEquips: RestrictSpecialEquips(),
            EXPStarsAnywhere: EXPStarsAnywhere(),
            ShuffleHillFlowers: ShuffleHillFlowers(),
            ShuffleCoins: ShuffleCoins(),
            MimicsAnywhere: MimicsAnywhere(),
            SlotsAnywhere: SlotsAnywhere(),
            ShuffleBeetlemania: ShuffleBeetlemania(),
            ShuffleMagikoopaChest: ShuffleMagikoopaChest(),
            ShuffleWeddingGear: ShuffleWeddingGear(),
            ShuffleMarioDoll: ShuffleMarioDoll(),
            ShuffleCookies: ShuffleCookies(),
            AnnoyingChests: AnnoyingChests(),
            FireworksSetting: FireworksSetting(),
            KeyItemsAnywhere: KeyItemsAnywhere(),
            StarPieceAvailability: StarPieceAvailability(),
            SpellsAnywhere: SpellsAnywhere(),
            InvisibleFlagsSetting: InvisibleFlagsSetting(),
            Remake: Remake(),
            EnabledRegularChecks: EnabledRegularChecks(),
            ReplaceItems: ReplaceItems(),
            PoisonMushroom: PoisonMushroom(),
            EXPChallenge: EXPChallenge(),
            GrateGuyPrizeThreshold: GrateGuyPrizeThreshold(),
            KnifeGuyPrizeThreshold: KnifeGuyPrizeThreshold(),
            FixKnifeGuy: FixKnifeGuy(),
            KnifeGuyFixedPrizeThreshold: KnifeGuyFixedPrizeThreshold(),
            SuitePrize1Threshold: SuitePrize1Threshold(),
            SuitePrize2Threshold: SuitePrize2Threshold(),
            SuitePrize3Threshold: SuitePrize3Threshold(),
            SuitePrize4Threshold: SuitePrize4Threshold(),
            SuitePrize5Threshold: SuitePrize5Threshold(),
            SuitePrize6Threshold: SuitePrize6Threshold(),
            SuperJump1Threshold: SuperJump1Threshold(),
            SuperJump2Threshold: SuperJump2Threshold(),
            BanditsWayGate: BanditsWayGate(),
            KeroSewersGate: KeroSewersGate(),
            ForestMazeGate: ForestMazeGate(),
            PipeVaultGate: PipeVaultGate(),
            Moleville1Gate: Moleville1Gate(),
            BoosterTowerGate: BoosterTowerGate(),
            BoosterHillGate: BoosterHillGate(),
            MarrymoreGate: MarrymoreGate(),
            YaridovichGate: YaridovichGate(),
            SeaGate: SeaGate(),
            LandsEndGate: LandsEndGate(),
            BelomeTempleGate: BelomeTempleGate(),
            MonstroTownGate: MonstroTownGate(),
            SkipMustyFearsSequence: SkipMustyFearsSequence(),
            NimbusGate: NimbusGate(),
            BarrelVolcanoGate: BarrelVolcanoGate(),
            BowsersKeepGate: BowsersKeepGate(),
            FactoryGate: FactoryGate(),
            BowserDoorRequirements: BowserDoorRequirements(),
            StarPiecesRequired: StarPiecesRequired(),
            CasinoWarp: CasinoWarp(),
            BucketWarp: BucketWarp(),
            FastTravel: FastTravel(),
            WinCondition: WinCondition(),
            BallSolitaireShuffle: BallSolitaireShuffle(),
            MagicButtonShuffle: MagicButtonShuffle(),
            QuizShuffle: QuizShuffle(),
            QuizIncludeNonSmrpg: QuizIncludeNonSmrpg(),
            RandomTadpolePondSong: RandomTadpolePondSong(),
            RandomSunkenShipPassword: RandomSunkenShipPassword(),
            BowserDoorShuffle: BowserDoorShuffle(),
            SkipMinecart: SkipMinecart(),
            RandomMinecartTrack: RandomMinecartTrack(),
            RedBarrels: RedBarrels(),
            SkipAnts: SkipAnts(),
            BetterTips: BetterTips(),
            ShuffleShops: ShuffleShops(),
            ShopQuality: ShopQuality(),
            BiasShopShuffle: BiasShopShuffle(),
            PickMeUpAvailability: PickMeUpAvailability(),
            ShowEquips: ShowEquips(),
            FreeShops: FreeShops(),
            ProtectSpecialItems: ProtectSpecialItems(),
            BossShuffle: BossShuffle(),
            BossShuffleScaleStats: BossShuffleScaleStats(),
            DontAutoheal: DontAutoheal(),
            KeepMinigameSpritesIntact: KeepMinigameSpritesIntact(),
            DifferentiateRepeatedBosses: DifferentiateRepeatedBosses(),
            ShuffledBosses: ShuffledBosses(),
            EnemyStats: EnemyStats(),
            EnemyDrops: EnemyDrops(),
            EnemyFormations: EnemyFormations(),
            EnemyAttacks: EnemyAttacks(),
            EnemySpells: EnemySpells(),
            ExperienceNoRegular: ExperienceNoRegular(),
            ExperienceNoBosses: ExperienceNoBosses(),
            Punchinello2BobombDifficulty: Punchinello2BobombDifficulty(),
            SkipBossFights: SkipBossFights(),
            NoGenoWhirlExor: NoGenoWhirlExor(),
            FixMagikoopa: FixMagikoopa(),
            NoOHKO: NoOHKO(),
            SeeYa: SeeYa(),
            FixInvincibility: FixInvincibility(),
            MarioPaletteChoice: MarioPaletteChoice(),
            MallowPaletteChoice: MallowPaletteChoice(),
            GenoPaletteChoice: GenoPaletteChoice(),
            BowserPaletteChoice: BowserPaletteChoice(),
            ToadstoolPaletteChoice: ToadstoolPaletteChoice(),
            ChangeNames: ChangeNames(),
            RemakeNames: RemakeNames(),
            CanonNames: CanonNames(),
            Peach: Peach(),
            JapaneseABXY: JapaneseABXY(),
            BossShuffleMusic: BossShuffleMusic(),
            ShuffledMusic: ShuffledMusic(),
            RemoveFlashes: RemoveFlashes(),
            HoldB: HoldB(),
        }
        self._flags_by_id: dict[str, Flag] = {f.id: f for f in self._flags.values()}

    @property
    def flags(self) -> dict[type[Flag], Flag]:
        """All settings flags."""
        return self._flags

    def force_override(self, message: str) -> None:
        """Record a setting that generation changed behind the user's back."""
        if message not in self.forced_overrides:
            self.forced_overrides.append(message)

    def get_flag(self, flag_type: type[FlagT]) -> FlagT:
        """Get a flag instance with proper typing."""
        return cast(FlagT, self._flags[flag_type])

    def get_flag_by_id(self, flag_id: str) -> Flag:
        """Get a flag instance by its string id (e.g. "chests", "bosses")."""
        return self._flags_by_id[flag_id]
    
    def is_flag_value(self, flag_class: type[FlagT], value: Any) -> bool:
        """Check if a setting is set to the given value. Results are cached."""
        cache_key = (flag_class, value)
        if cache_key in self._is_flag_value_cache:
            return self._is_flag_value_cache[cache_key]

        flag = self.get_flag(flag_class)
        if isinstance(flag, BooleanFlag):
            result = flag.enabled == value
        elif isinstance(flag, SelectOneFlag):
            result = flag.selected == value
        elif isinstance(flag, RangeFlag):
            result = flag.value == value
        elif isinstance(flag, CategorizationFlag):
            result = value in flag.enabled
        else:
            raise RandomizerSettingsException(
                f"is_flag_value unknown flag type {type(flag)}"
            )

        self._is_flag_value_cache[cache_key] = result
        return result
    
    def isflag_enabled(self, flag_class: type[BooleanFlag]) -> bool:
        """Check if a boolean flag is on or not."""
        return self.is_flag_value(flag_class, True)

    def _requirement_met(self, requirement: tuple[Flag, Any]) -> bool:
        """Evaluate one (flag, expected value) entry from a flag's requirements."""
        required_flag, expected = requirement
        flag_class = type(required_flag)
        if isinstance(required_flag, BooleanFlag):
            return self.isflag_enabled(flag_class) == expected
        if isinstance(required_flag, SelectOneFlag):
            choices = expected if isinstance(expected, list) else [expected]
            return any(self.is_flag_value(flag_class, choice) for choice in choices)
        raise RandomizerSettingsException(
            f"unsupported requirement flag type {flag_class.__name__}"
        )

    def is_flag_active(self, flag_class: type[Flag]) -> bool:
        """Whether a flag's dependencies are satisfied, i.e. whether it does anything."""
        flag = self.get_flag(flag_class)
        if any(not self._requirement_met(r) for r in flag._requires_all):
            return False
        if flag._requires_any and not any(
            self._requirement_met(r) for r in flag._requires_any
        ):
            return False
        if flag._disabled_if_all and all(
            self._requirement_met(r) for r in flag._disabled_if_all
        ):
            return False
        return True

    def set_boolean_flag(self, flag_class: type[BooleanFlag], enabled: bool) -> None:
        """Turn a boolean flag on or off after the settings have been built."""
        flag = self.get_flag(flag_class)
        if not isinstance(flag, BooleanFlag):
            raise RandomizerSettingsException(
                f"set_boolean_flag on non-boolean flag {flag_class.__name__}"
            )
        flag.enabled = enabled
        self._is_flag_value_cache.clear()


    @staticmethod
    def _get_sorted_options_list(flag: CategorizationFlag | CategorizationFlagWithOrdinance) -> list:
        """Get options sorted alphabetically by display text; must match _get_option_text() in flags.py."""
        def get_text(opt) -> str:
            if hasattr(opt, 'value'):
                val = opt.value
            else:
                val = opt

            if isinstance(val, str):
                return val
            if isinstance(val, tuple):
                if len(val) >= 2 and isinstance(val[1], str):
                    return val[1]
                return str(val)
            if hasattr(val, '_text'):
                return val._text
            if hasattr(val, '_name') and isinstance(val._name, str):
                return val._name
            if hasattr(val, '_title'):
                return val._title
            if hasattr(val, '_id'):
                id_val = val._id
                if hasattr(id_val, 'value') and isinstance(id_val.value, str):
                    return id_val.value
            if hasattr(val, 'value') and isinstance(val.value, str):
                return val.value
            if hasattr(val, 'name') and isinstance(val.name, str):
                return val.name
            if hasattr(val, '__name__'):
                return val.__name__
            return str(val)
        return sorted(flag.options.keys(), key=lambda x: get_text(x).lower())

    @staticmethod
    def _encode_categorization_hash(flag: CategorizationFlag) -> str:
        """Encode a CategorizationFlag's enabled options as a compact hash."""
        options_list = Settings._get_sorted_options_list(flag)
        bitmask = 0
        for i, opt in enumerate(options_list):
            if flag.options[opt]:
                bitmask |= (1 << i)

        if bitmask == 0:
            return "A"

        result = ""
        while bitmask > 0:
            result += B64_TABLE[bitmask & 0x3F]
            bitmask >>= 6
        return result

    @staticmethod
    def _decode_categorization_hash(hash_str: str, flag: CategorizationFlag) -> dict:
        """Decode a hash string back to option enabled states."""
        options_list = Settings._get_sorted_options_list(flag)
        bitmask = 0
        for i, char in enumerate(hash_str):
            idx = B64_TABLE.index(char)
            bitmask |= (idx << (i * 6))

        result = {}
        for i, opt in enumerate(options_list):
            result[opt] = bool(bitmask & (1 << i))
        return result

    @staticmethod
    def _encode_ordinance_hash(flag: CategorizationFlagWithOrdinance) -> str:
        """Encode a CategorizationFlagWithOrdinance's enabled options and order."""
        options_list = Settings._get_sorted_options_list(flag)

        enabled_with_order = [
            (opt, flag.options[opt])
            for opt in options_list
            if flag.options[opt] is not None
        ]
        enabled_with_order.sort(key=lambda x: x[1])  # type: ignore

        indices = [str(options_list.index(opt)) for opt, _ in enabled_with_order]
        return ":".join(indices) if indices else ""

    @staticmethod
    def _decode_ordinance_hash(
        hash_str: str, flag: CategorizationFlagWithOrdinance
    ) -> dict:
        """Decode a hash string back to option enabled states with ordinance."""
        options_list = Settings._get_sorted_options_list(flag)
        result: dict = {opt: None for opt in options_list}

        if not hash_str:
            return result

        parts = hash_str.split(":")
        for ordinance, part in enumerate(parts):
            try:
                opt_idx = int(part)
                if 0 <= opt_idx < len(options_list):
                    result[options_list[opt_idx]] = ordinance
            except ValueError:
                continue

        return result

    def _is_flag_at_default(self, flag: Flag) -> bool:
        """Check if a flag is at its default value."""
        if isinstance(flag, BooleanFlag):
            return flag.enabled == flag.default
        if isinstance(flag, RangeFlag):
            return flag.value == flag.default
        if isinstance(flag, SelectOneFlag):
            return flag.selected == flag.default
        if isinstance(flag, CategorizationFlagWithOrdinance):
            return flag.options == flag.default
        if isinstance(flag, CategorizationFlag):
            return flag.options == flag.default
        return True

    def _encode_single_flag(self, flag: Flag) -> str | None:
        """Encode a single flag to string format. Returns None if at default."""
        if self._is_flag_at_default(flag):
            return None

        if isinstance(flag, BooleanFlag):
            if flag.enabled:
                return flag.id
            return None

        if isinstance(flag, RangeFlag):
            return f"{flag.id}:{flag.value}"

        if isinstance(flag, SelectOneFlag):
            selected = flag.selected
            if hasattr(selected, "name"):
                key_name = selected.name.lower()
            else:
                key_name = str(selected).split(".")[-1].lower()
            return f"{flag.id}:{key_name}"

        if isinstance(flag, CategorizationFlagWithOrdinance):
            hash_val = self._encode_ordinance_hash(flag)
            return f"{flag.id}:{hash_val}"

        if isinstance(flag, CategorizationFlag):
            hash_val = self._encode_categorization_hash(flag)
            return f"{flag.id}:{hash_val}"

        return None

    @staticmethod
    def default_value_string(flag: Flag) -> str:
        """Render a flag's DEFAULT value the way it appears in the flag string."""
        if isinstance(flag, BooleanFlag):
            return "true" if flag.default else "false"
        if isinstance(flag, RangeFlag):
            return str(flag.default)
        if isinstance(flag, SelectOneFlag):
            return flag.default.name.lower()
        if isinstance(flag, CategorizationFlagWithOrdinance):
            return Settings._encode_ordinance_hash(type(flag)())
        if isinstance(flag, CategorizationFlag):
            return Settings._encode_categorization_hash(type(flag)())
        return ""

    def _get_all_subcategories(
        self, exclude_cosmetic: bool = False
    ) -> list[type[FlagCategory]]:
        """Get all subcategories (leaf categories with flags)."""
        subcategories: list[type[FlagCategory]] = []
        for category in CATEGORIES:
            cat_instance = category()
            if exclude_cosmetic and isinstance(cat_instance, CosmeticCategory):
                continue
            if cat_instance.subcategories:
                for subcat in cat_instance.subcategories:
                    if exclude_cosmetic and subcat()._id == "R":
                        continue
                    subcategories.append(subcat)
            elif cat_instance.flags:
                if exclude_cosmetic and cat_instance._id == "R":
                    continue
                subcategories.append(category)
        return subcategories

    def get_flag_string(self) -> str:
        """Generate a compact string representation of all non-default flags."""
        id_to_flags: dict[str, list[str]] = {}

        for subcat_cls in self._get_all_subcategories():
            subcat = subcat_cls()
            cat_id = subcat.id

            for flag_cls in subcat.flags:
                if flag_cls not in self._flags:
                    continue
                flag = self._flags[flag_cls]
                encoded = self._encode_single_flag(flag)
                if encoded:
                    if cat_id not in id_to_flags:
                        id_to_flags[cat_id] = []
                    id_to_flags[cat_id].append(encoded)

        parts: list[str] = []
        for cat_id in sorted(id_to_flags.keys()):
            flag_parts = id_to_flags[cat_id]
            if flag_parts:
                parts.append(f"{cat_id}({"|".join(flag_parts)})")

        return " ".join(parts)

    def get_flag_string_without_cosmetics(self) -> str:
        """Generate flag string excluding all flags under 'R' category ID."""
        id_to_flags: dict[str, list[str]] = {}

        for subcat_cls in self._get_all_subcategories(exclude_cosmetic=True):
            subcat = subcat_cls()
            cat_id = subcat.id

            if cat_id == "R":
                continue

            for flag_cls in subcat.flags:
                if flag_cls not in self._flags:
                    continue
                flag = self._flags[flag_cls]
                encoded = self._encode_single_flag(flag)
                if encoded:
                    if cat_id not in id_to_flags:
                        id_to_flags[cat_id] = []
                    id_to_flags[cat_id].append(encoded)

        parts: list[str] = []
        for cat_id in sorted(id_to_flags.keys()):
            flag_parts = id_to_flags[cat_id]
            if flag_parts:
                parts.append(f"{cat_id}({"|".join(flag_parts)})")

        return " ".join(parts)


    def _build_flag_id_map(self) -> dict[str, type[Flag]]:
        """Build a mapping from flag ID to flag class."""
        flag_map: dict[str, type[Flag]] = {}
        for subcat_cls in self._get_all_subcategories():
            subcat = subcat_cls()
            for flag_cls in subcat.flags:
                flag_instance = flag_cls()
                flag_map[flag_instance.id] = flag_cls
        return flag_map

    def _decode_and_set_flag(self, flag_cls: type[Flag], value_str: str | None) -> None:
        """Decode a flag value string and set the flag accordingly."""
        if flag_cls not in self._flags:
            return

        flag = self._flags[flag_cls]

        if isinstance(flag, BooleanFlag):
            flag.enabled = True
            return

        if value_str is None:
            return

        if isinstance(flag, RangeFlag):
            try:
                flag.set_value(int(value_str))
            except (ValueError, FlagError):
                pass
            return

        if isinstance(flag, SelectOneFlag):
            for choice in flag.choices:
                if hasattr(choice, "name"):
                    if choice.name.lower() == value_str.lower():
                        flag.select(choice)
                        return
                else:
                    choice_name = str(choice).split(".")[-1]
                    if choice_name.lower() == value_str.lower():
                        flag.select(choice)
                        return
            return

        if isinstance(flag, CategorizationFlagWithOrdinance):
            decoded = self._decode_ordinance_hash(value_str, flag)
            flag._options = decoded
            return

        if isinstance(flag, CategorizationFlag):
            decoded = self._decode_categorization_hash(value_str, flag)
            for opt, enabled in decoded.items():
                if enabled:
                    flag.enable(opt)
                else:
                    flag.disable(opt)
            return

    def set_from_flag_string(self, flag_string: str) -> None:
        """Parse a flag string and set flags accordingly."""

        for flag in self._flags.values():
            if hasattr(flag, "reset"):
                flag.reset()  # type: ignore[union-attr]

        flag_id_map = self._build_flag_id_map()

        pattern = r"([A-Z])\(([^)]*)\)"
        matches = re.findall(pattern, flag_string)

        for cat_id, flags_content in matches:
            if not flags_content:
                continue

            flag_entries = flags_content.split("|")

            for entry in flag_entries:
                entry = entry.strip()
                if not entry:
                    continue

                if ":" in entry:
                    flag_id, value_str = entry.split(":", 1)
                else:
                    flag_id = entry
                    value_str = None

                if flag_id in flag_id_map:
                    flag_cls = flag_id_map[flag_id]
                    self._decode_and_set_flag(flag_cls, value_str)

    def print_settings(self, max_width: int = 120) -> str:
        """Print all settings values in a readable format."""
        lines = []
        lines.append("=" * max_width)
        lines.append("SETTINGS SUMMARY")
        lines.append("=" * max_width)
        lines.append("")

        for flag in self._flags.values():
            flag_name = flag.name or flag.__class__.__name__

            if isinstance(flag, BooleanFlag):
                value_str = "ON" if flag.enabled else "OFF"
                default_str = "ON" if flag.default else "OFF"
                marker = "  " if flag.enabled == flag.default else "* "
                lines.append(f"{marker}{flag_name}: {value_str} (default: {default_str})")

            elif isinstance(flag, SelectOneFlag):
                selected = flag.selected
                default = flag.default
                value_str = selected.name if hasattr(selected, 'name') else str(selected)
                default_str = default.name if hasattr(default, 'name') else str(default)
                marker = "  " if selected == default else "* "
                lines.append(f"{marker}{flag_name}: {value_str} (default: {default_str})")

            elif isinstance(flag, RangeFlag):
                marker = "  " if flag.value == flag.default else "* "
                lines.append(f"{marker}{flag_name}: {flag.value} (default: {flag.default})")

            elif isinstance(flag, CategorizationFlagWithOrdinance):
                enabled_items = [
                    (opt, order) for opt, order in flag.options.items()
                    if order is not None
                ]
                enabled_items.sort(key=lambda x: x[1])
                enabled_with_order = [
                    f"{order}: {self._get_option_display_name(opt)}"
                    for opt, order in enabled_items
                ]

                disabled_items = [
                    opt for opt, order in flag.options.items()
                    if order is None
                ]
                disabled_names = sorted([self._get_option_display_name(opt) for opt in disabled_items])

                default_items = [
                    (opt, order) for opt, order in flag.default.items()
                    if order is not None
                ]
                default_items.sort(key=lambda x: x[1])
                default_with_order = [
                    f"{order}: {self._get_option_display_name(opt)}"
                    for opt, order in default_items
                ]

                enabled_names = [self._get_option_display_name(opt) for opt, _ in enabled_items]
                default_names = [self._get_option_display_name(opt) for opt, _ in default_items]
                marker = "  " if enabled_names == default_names else "* "

                lines.append(f"{marker}{flag_name}:")
                lines.append(f"    Enabled ({len(enabled_with_order)}): {', '.join(enabled_with_order)}")
                if disabled_names:
                    lines.append(f"    Disabled ({len(disabled_names)}): {', '.join(disabled_names)}")
                if marker == "* ":
                    lines.append(f"    Default ({len(default_with_order)}): {', '.join(default_with_order)}")

            elif isinstance(flag, CategorizationFlag):
                enabled = flag.enabled
                disabled = flag.disabled
                default_enabled = [opt for opt, val in flag.default.items() if val]

                enabled_names = sorted([self._get_option_display_name(opt) for opt in enabled])
                disabled_names = sorted([self._get_option_display_name(opt) for opt in disabled])
                default_names = sorted([self._get_option_display_name(opt) for opt in default_enabled])

                is_default = set(enabled_names) == set(default_names)
                marker = "  " if is_default else "* "

                lines.append(f"{marker}{flag_name}:")

                lines.append(f"    Enabled ({len(enabled_names)}):")
                if enabled_names:
                    lines.append(self._format_options_table(enabled_names, max_width - 6, "      "))
                else:
                    lines.append("      (none)")

                lines.append(f"    Disabled ({len(disabled_names)}):")
                if disabled_names:
                    lines.append(self._format_options_table(disabled_names, max_width - 6, "      "))
                else:
                    lines.append("      (none)")

                if not is_default:
                    lines.append(f"    Default enabled ({len(default_names)}):")
                    if default_names:
                        lines.append(self._format_options_table(default_names, max_width - 6, "      "))

            lines.append("")

        lines.append("=" * max_width)
        lines.append("* = differs from default")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _get_option_display_name(opt) -> str:
        """Get a display name for a categorization option."""
        if hasattr(opt, '_text'):
            return opt._text
        if hasattr(opt, '_name') and isinstance(opt._name, str):
            return opt._name
        if hasattr(opt, '_title'):
            return opt._title
        if hasattr(opt, '_id'):
            id_val = opt._id
            if hasattr(id_val, 'value') and isinstance(id_val.value, str):
                return id_val.value
        if hasattr(opt, 'value') and isinstance(opt.value, str):
            return opt.value
        if hasattr(opt, 'name') and isinstance(opt.name, str):
            return opt.name
        if hasattr(opt, '__name__'):
            return opt.__name__
        return str(opt)

    @staticmethod
    def _format_options_table(items: list[str], max_width: int, indent: str) -> str:
        """Format a list of items into a compact table with multiple items per line."""
        if not items:
            return ""

        max_item_len = max(len(item) for item in items)
        col_width = max_item_len + 2

        available_width = max_width - len(indent)
        num_cols = max(1, available_width // col_width)

        lines = []
        for i in range(0, len(items), num_cols):
            row_items = items[i:i + num_cols]
            row = indent + "  ".join(item.ljust(max_item_len) for item in row_items)
            lines.append(row.rstrip())

        return "\n".join(lines)
