# Flag definitions and logic.


class Flag:
    """Class representing a flag with its description, and possible values."""

    def __init__(self, name, field, letter, levels=1, default=0, modes=None, hard_level=99):
        """

        Args:
            name (str): Name
            field (str): Form field key
            letter (str): Single letter used to represent this flag in the flagset when building filenames
            levels (int): Number of levels this flag has.  Default is 1, i.e. on or off.
            default (bool|str): Default level, should be 0 for off for all flags.
            modes (list[str]): List of available modes for this flag.  If not set, will default to standard and open.
            hard_level (int): Level at which this flag becomes a "hard" flag, highlighted in red on the front end.
                              99 is used as a placeholder for flags that don't have a hard level.

        """
        self.name = name
        self.field = field
        self.letter = letter
        self.value = default
        self.levels = levels
        self.hard_level = hard_level
        self.modes = set()

        if not modes:
            self.set_available_mode('standard')
            self.set_available_mode('open')
        else:
            for mode in modes:
                self.set_available_mode(mode)

    def set_available_mode(self, mode, allowed=True):
        """

        Args:
            mode (str): Which mode is available or not.
            allowed (bool): Whether this mode is available.

        """
        if allowed:
            self.modes.add(mode)
        elif mode in self.modes:
            self.modes.remove(mode)

    def available_in_mode(self, mode):
        """

        Args:
            mode (str): Mode to check availability.

        Returns:
            bool: True if this flag is available in the given mode, False otherwise.

        """
        return mode in self.modes

    @classmethod
    def get_default_flags(cls):
        """

        Returns:
            list[Flag]: List of Flag objects with default values.

        """
        flags = [
            Flag('Key Items', 'randomize_key_items', 'K', 2, modes=['open']),
            Flag('Star Pieces', 'randomize_stars', 'R', 2, modes=['open'], hard_level=2),
            Flag('Seven Star Hunt', 'randomize_stars_seven', 'V', modes=['open']),
            Flag("Bowser's Keep Open", 'randomize_stars_bk', 'W', modes=['open']),
            Flag('Character Stats', 'randomize_character_stats', 'C'),
            Flag('Character Join Order', 'randomize_join_order', 'J'),
            Flag('Enemy Stats', 'randomize_enemies', 'E'), Flag('Enemy Drops', 'randomize_drops', 'D'),
            Flag('Enemy Formations', 'randomize_enemy_formations', 'F'), Flag('Shops', 'randomize_shops', 'P'),
            Flag('Equipment Stats', 'randomize_equipment', 'Q'), Flag('Equipment Buffs', 'randomize_buffs', 'U'),
            Flag('Equipment Allowed Characters', 'randomize_allowed_equips', 'A'),
            Flag('Character Spell Stats', 'randomize_spell_stats', 'S'),
            Flag('Character Spell Lists', 'randomize_spell_lists', 'L'),
        ]

        return flags


class Preset:
    def __init__(self, name, flags, description):
        """Holder for preset info.

        Args:
            name (str): Name
            flags (str): Flag string, ex. ABC2DEF
            description (str): Text description to show on the UI.
        """
        self.name = name
        self.flags = flags
        self.description = description

    @classmethod
    def get_default_presets(cls):
        """

        Returns:
            list[Preset]: List of presets for the UI.

        """
        presets = []

        # Format: (name, flags, description)
        for name, flags, description in (
                ('Vanilla', '',
                 'No randomization, just a vanilla experience with the base game changes for cutscenes and '
                 'non-linearity.'),
                ('Full Shuffle', 'K2R2VWCJEDFPQUASL',
                 'High degree of randomization shuffling all available elements of the game.'),
        ):
            presets.append(Preset(name, flags, description))

        return presets
