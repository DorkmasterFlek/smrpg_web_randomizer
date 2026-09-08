"""Settings validation for the randomizer."""

from __future__ import annotations
from typing import TYPE_CHECKING
from ..types.flags import (
        ShuffleCharacters,
        AvailableCharacters,
        MaxCharacters,
        StartingCharacters,
        BanditsWayGate, BanditsWayGating,
        KeroSewersGate, KeroSewersGating,
        PipeVaultGate, PipeVaultGating,
        Moleville1Gate, Moleville1Gating,
        BoosterTowerGate, BoosterTowerGating,
        SeaGate, SeaGating,
    )
from ..types.flags import (
        ShuffleStarPieces,
        TotalStarPieces,
        StarPiecesRequired,
        SeaGate, SeaGating,
        LandsEndGate, LandsEndGating,
        BowsersKeepGate, BowsersKeepGating,
        FactoryGate, FactoryGating,
        WinCondition, WinConditions,
        Remake
    )
from ..types.flags import (
        ExperienceNoRegular,
        ExperienceNoBosses,
        EXPChallenge,
        EXPChallengeOptions,
        BossShuffleScaleStats,
        BossScaleOptions
    )
from ..types.flags import (
        CategorizationFlag,
        CategorizationFlagWithOrdinance,
    )

if TYPE_CHECKING:
    from ..types.settings import Settings


class SettingsValidationError(Exception):
    """Raised when settings have an invalid combination."""
    pass


def validate_settings(settings: Settings) -> None:
    """Validate that settings combinations are valid."""
    _validate_character_requirements(settings)
    _validate_star_piece_requirements(settings)
    _validate_exp_sources(settings)
    _validate_multiselect_selections(settings)


def _validate_multiselect_selections(settings: Settings) -> None:
    """Reject multi-select settings that are in play with nothing selected."""

    for flag_class, flag in settings._flags.items():
        if not isinstance(flag, (CategorizationFlag, CategorizationFlagWithOrdinance)):
            continue
        if not flag._requires_selection or flag.enabled:
            continue
        if not settings.is_flag_active(flag_class):
            continue

        gates = [
            required_flag.name
            for required_flag, _ in (flag._requires_all + flag._requires_any)
            if required_flag.name
        ]
        message = f"'{flag.name}' has no options selected, so there is nothing for it to choose from."
        if gates:
            message += (
                f" Select at least one option, or turn off "
                f"{' / '.join(repr(g) for g in gates)}."
            )
        else:
            message += " Select at least one option."
        raise SettingsValidationError(message)


def _validate_character_requirements(settings: Settings) -> None:
    """Validate character-related settings are compatible."""

    if not settings.isflag_enabled(ShuffleCharacters):
        return

    starting_chars_flag = settings.get_flag(StartingCharacters)
    num_starters = len(starting_chars_flag.enabled)
    if num_starters > 5:
        raise SettingsValidationError(
            f"Too many starting characters selected ({num_starters}). "
            f"You can choose at most 5 starting characters."
        )

    if num_starters < 1:
        raise SettingsValidationError(
            "No starting characters are selected. You must choose at least one."
        )

    max_char_count = settings.get_flag(MaxCharacters).value
    if num_starters > max_char_count:
        raise SettingsValidationError(
            f"{num_starters} starting characters are selected, "
            f"but 'Total playable allies' is set to {max_char_count}. "
            f"Either reduce the number of starting characters or increase "
            f"'Total playable allies'."
        )

    gating_required_characters: set[str] = set()
    gating_checks: list[tuple[type, object, str]] = [
        (BanditsWayGate, BanditsWayGating.MALLOW, "Mallow"),
        (KeroSewersGate, KeroSewersGating.MALLOW, "Mallow"),
        (PipeVaultGate, PipeVaultGating.GENO, "Geno"),
        (Moleville1Gate, Moleville1Gating.GENO, "Geno"),
        (BoosterTowerGate, BoosterTowerGating.MARIO, "Mario"),
        (BoosterTowerGate, BoosterTowerGating.MALLOW, "Mallow"),
        (BoosterTowerGate, BoosterTowerGating.GENO, "Geno"),
        (BoosterTowerGate, BoosterTowerGating.BOWSER, "Bowser"),
        (BoosterTowerGate, BoosterTowerGating.TOADSTOOL, "Toadstool"),
        (SeaGate, SeaGating.TOADSTOOL, "Toadstool"),
    ]
    for flag_class, gating_value, char_name in gating_checks:
        if settings.is_flag_value(flag_class, gating_value):
            gating_required_characters.add(char_name)

    explicitly_set_starting_chars: set[str] = set()
    for option in starting_chars_flag.enabled:
        value = option.value
        if isinstance(value, str):
            continue
        ally_name = value.name
        if ally_name:
            explicitly_set_starting_chars.add(ally_name)

    available_chars_flag = settings.get_flag(AvailableCharacters)
    disabled_char_names = {m.value.name for m in available_chars_flag.disabled}

    all_required_characters = gating_required_characters | explicitly_set_starting_chars

    disabled_required = all_required_characters & disabled_char_names
    if disabled_required:
        raise SettingsValidationError(
            f"Settings require characters that are disabled: "
            f"{', '.join(sorted(disabled_required))}. "
            f"Either change the gating/starting settings or enable these characters."
        )

    if len(all_required_characters) > max_char_count:
        raise SettingsValidationError(
            f"Settings require {len(all_required_characters)} unique characters "
            f"({', '.join(sorted(all_required_characters))}), "
            f"but 'Total playable allies' is set to {max_char_count}. "
            f"Either reduce character requirements or increase 'Total playable allies'."
        )


def _validate_star_piece_requirements(settings: Settings) -> None:
    """Validate star piece-related settings are compatible."""

    total_stars = settings.get_flag(TotalStarPieces).value
    required_stars = settings.get_flag(StarPiecesRequired).value

    if required_stars > total_stars:
        raise SettingsValidationError(
            f"'Star Pieces required to access the final Factory boss' ({required_stars}) "
            f"cannot be higher than 'Total Star Pieces available' ({total_stars})."
        )

    if required_stars == 0 and settings.is_flag_value(WinCondition, WinConditions.STARS):
        raise SettingsValidationError(
            f"'Condition required to beat the game' is set to "
            f"'{WinConditions.STARS.value}', but 'Star Pieces required to access "
            f"the final Factory boss' is 0. Either raise the required Star Piece "
            f"count or choose a different win condition."
        )

    if settings.isflag_enabled(Remake) and settings.is_flag_value(WinCondition, WinConditions.SEALED):
        raise SettingsValidationError(
            f"The Monstro Town sealed door gates too much remake content to make placements solvable. Disable the remake content flag or choose a different win condition."
        )

    if not settings.isflag_enabled(ShuffleStarPieces):
        return

    min_required = 0
    min_reason = ""

    if settings.is_flag_value(SeaGate, SeaGating.STAR_4):
        if min_required < 4:
            min_required = 4
            min_reason = "'Sea & Sunken Ship access' is set to 'Collect 4 Star Pieces'"

    if settings.is_flag_value(LandsEndGate, LandsEndGating.STAR_5):
        if min_required < 5:
            min_required = 5
            min_reason = "'Land's End access' is set to 'Collect 5 Star Pieces'"

    if settings.is_flag_value(BowsersKeepGate, BowsersKeepGating.STAR_6):
        if min_required < 6:
            min_required = 6
            min_reason = "'Bowser's Keep access' is set to 'Collect 6 Star Pieces'"

    if settings.is_flag_value(FactoryGate, FactoryGating.STAR_6):
        if min_required < 6:
            min_required = 6
            min_reason = "'Factory access' is set to 'Collect 6 Star Pieces'"

    if total_stars < min_required:
        raise SettingsValidationError(
            f"'Total Star Pieces available' ({total_stars}) must be at least {min_required} "
            f"because {min_reason}."
        )


def _validate_exp_sources(settings: Settings) -> None:
    """Validate that at least one EXP source is available."""

    no_regular_exp = settings.isflag_enabled(ExperienceNoRegular)
    no_boss_exp = settings.isflag_enabled(ExperienceNoBosses)
    no_star_exp = settings.is_flag_value(EXPChallenge, EXPChallengeOptions.NONE)
    is_godmode = settings.is_flag_value(BossShuffleScaleStats, BossScaleOptions.GODMODE)


    if no_regular_exp and no_boss_exp and no_star_exp and not is_godmode and not settings.debug_mode:
        raise SettingsValidationError(
            "Invalid settings combination: all EXP sources are disabled. "
            "You cannot have 'Remove EXP from regular enemy encounters', "
            "'Remove EXP from boss encounters', and 'EXP Star Behaviour' set to 'None' "
            "all at the same time. The player needs at least one source of EXP."
        )
