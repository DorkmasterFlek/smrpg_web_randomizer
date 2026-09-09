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
from ..types.flags import (
        AvailableSpells,
        CharacterLearnedSpells,
        SpellsAnywhere,
    )
from ..types.prize import damaging_spell_prizes
from ..types.prizelocation import vanilla_spell_owner
from ..data.allies.allies import ally_collection
from .progression import prizes as _prizes  # noqa: F401

if TYPE_CHECKING:
    from ..types.settings import Settings


class SettingsValidationError(Exception):
    """Raised when settings have an invalid combination."""
    pass


def validate_settings(settings: Settings) -> None:
    """Validate that settings combinations are valid."""
    _validate_character_requirements(settings)
    _validate_available_character_count(settings)
    _validate_damaging_spell_availability(settings)
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


def _is_vanilla_spell_mode(settings: Settings) -> bool:
    """Whether spells are learned by their vanilla owners on recruitment. Ties the spell pool to the character roster.
    """

    return not settings.isflag_enabled(
        CharacterLearnedSpells
    ) and not settings.isflag_enabled(SpellsAnywhere)


def _validate_damaging_spell_availability(settings: Settings) -> None:
    """Validate that a usable damaging spell survives the spell/ally exclusions."""

    disabled_spells = {
        member.value for member in settings.get_flag(AvailableSpells).disabled
    }
    available_damaging = [
        prize
        for prize in damaging_spell_prizes()
        if prize._spell not in disabled_spells
    ]

    if not available_damaging:
        raise SettingsValidationError(
            "No damaging spells are enabled in 'Available Ally Spells'. At least one "
            "spell that damages enemies must be available, otherwise Mokura cannot be "
            "transformed and Bowser's Keep battle doors are not completable. Any damaging spell "
            "works, regardless of its element."
        )

    # Learned spells are randomized, so any recruited ally can end up with one.
    if settings.isflag_enabled(CharacterLearnedSpells):
        return

    excluded_char_names = {
        member.value.name for member in settings.get_flag(AvailableCharacters).disabled
    }
    available_damaging_spells = {prize._spell for prize in available_damaging}

    if not _is_vanilla_spell_mode(settings):
        if any(
            owner is not None and owner._ally.name not in excluded_char_names
            for prize in available_damaging
            for owner in [vanilla_spell_owner(prize)]
        ):
            return
        raise SettingsValidationError(
            "No ally in this seed can be given a damaging spell. Enable an ally with damage spells, re-enable your selected allies' damaging spells, or turn on 'Randomize which spells "
            "each ally learns'."
        )

    qualified = sorted(
        ally.name
        for ally in ally_collection._allies
        if ally.name not in excluded_char_names
        and any(
            spell in available_damaging_spells
            for spell in (ally.starting_magic or [])
        )
    )
    if qualified:
        return

    raise SettingsValidationError(
        "At least one damage spell must be included. If spells are not randomized, "
        "then at least one ally who starts with a damage spell must be included: "
        "Mario, Mallow, Geno or Bowser. Toadstool does not learn one until level 18, "
        "so she cannot be the only ally in the seed."
    )


def _validate_available_character_count(settings: Settings) -> None:
    """Validate that enough allies are enabled to fill 'Total playable allies'."""

    available_names = sorted(
        member.value.name for member in settings.get_flag(AvailableCharacters).enabled
    )

    if not available_names:
        return

    max_char_count = settings.get_flag(MaxCharacters).value
    if max_char_count <= len(available_names):
        return

    count = len(available_names)
    raise SettingsValidationError(
        f"'Total playable allies' is set to {max_char_count}, but only {count} "
        f"{'ally is' if count == 1 else 'allies are'} enabled in 'Available Allies' "
        f"({', '.join(available_names)}). "
        f"Either lower 'Total playable allies' to {count} or enable more allies."
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
