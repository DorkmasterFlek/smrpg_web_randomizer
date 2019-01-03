# Character randomization logic.

import collections
import random

from . import utils
from .patch import Patch

# Stats used during levelups.
LEVEL_STATS = ["max_hp", "attack", "defense", "magic_attack", "magic_defense"]


class StatGrowth:
    """Container class for a stat growth/bonus for a certain level + character."""

    def __init__(self, max_hp, attack, defense, magic_attack, magic_defense):
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense

    @property
    def best_choices(self):
        """Best choice of attributes for a levelup bonus based on the numbers.  For HP, it must be twice the total of
        the attack + defense options to be considered "better".  This is arbitrary, but HP is less useful.

        :return: Tuple of attributes to select for best choice.
        :rtype: tuple[str]
        """
        options = [(self.max_hp / 2, ("max_hp",)),
                   (self.attack + self.defense, ("attack", "defense")),
                   (self.magic_attack + self.magic_defense,
                    ("magic_attack", "magic_defense"))]
        a, b = max(options)
        options = [(c, d) for (c, d) in options if c == a]
        a, b = options[0]
        return b

    def as_bytes(self):
        """Return byte representation of this stat growth object for the patch.

        :rtype: bytearray
        """
        data = bytearray()

        # HP is one byte on its own.  Attack/defense stats are 4 bits each combined into a single byte together.
        data += utils.ByteField(self.max_hp).as_bytes()

        physical = self.attack << 4
        physical |= self.defense
        data += utils.ByteField(physical).as_bytes()

        magical = self.magic_attack << 4
        magical |= self.magic_defense
        data += utils.ByteField(magical).as_bytes()

        return data


class LearnedSpells:
    """Class for spells learned at each level for all characters."""
    BASE_ADDRESS = 0x3a42f5

    def __init__(self):
        # Vanilla spells learned
        self._spells = [
            # Mario
            [0x00, 0xff, 0x01, 0xff, 0xff, 0x02, 0xff, 0xff, 0xff, 0x03, 0xff, 0xff, 0xff, 0x04, 0xff, 0xff, 0xff, 0x05,
             0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            # Peach
            [0xff, 0xff, 0x06, 0xff, 0xff, 0xff, 0x07, 0xff, 0xff, 0xff, 0x08, 0xff, 0x09, 0xff, 0x0a, 0xff, 0xff, 0x0b,
             0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            # Bowser
            [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x0c, 0xff, 0xff, 0xff, 0x0d, 0xff, 0xff, 0x0e, 0xff, 0xff, 0x0f,
             0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            # Geno
            [0xff, 0xff, 0xff, 0xff, 0xff, 0x10, 0xff, 0x11, 0xff, 0xff, 0x12, 0xff, 0xff, 0x13, 0xff, 0xff, 0x14, 0xff,
             0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
            # Mallow
            [0xff, 0x15, 0x16, 0xff, 0xff, 0x17, 0xff, 0xff, 0xff, 0x18, 0xff, 0xff, 0xff, 0x19, 0xff, 0xff, 0xff, 0x1a,
             0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff],
        ]

    def randomize(self):
        """Perform randomization for learned spells."""
        # Reset all learned spells.
        for level in range(30):
            for index in range(5):
                self._spells[index][level] = 0xff

        # Shuffle all spells.  There are 27 spells, so add an extra 3 random ones to ensure everybody has 6 spells.
        # Group Hug only works with Peach however, so remove it from the shuffle and give Peach only 5 spells.
        spells = list(range(0x1b))
        spells.remove(7)
        spells += random.sample(spells, 3)
        random.shuffle(spells)
        charspells = collections.defaultdict(list)
        while spells:
            valid = [i for i in range(5) if len(charspells[i]) < 5 or (len(charspells[i]) < 6 and i != 1)]
            chosen = random.choice(valid)
            charspells[chosen].append(spells.pop(0))

        # Insert Group Hug for Peach, but make sure it's not the final spell learned for balance.
        charspells[1].insert(random.randint(0, 4), 7)

        # Assign chosen spells for each character.  Make the first spell always learned from the start (level 1), and
        # assign the other spells to random levels from 2-20.
        for index in range(5):
            charlevels = [1] + sorted(random.sample(list(range(2, 20)), 5))
            spells = charspells[index]
            for level, spell in zip(charlevels, spells):
                self._spells[index][level - 1] = spell

    def get_patch(self):
        """Get patch for learned spells.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        # Data is 29 blocks (starting at level 2), 5 bytes each block (1 byte per character in order)
        data = bytearray()
        for level in range(2, 31):
            for index in range(5):
                data += utils.ByteField(self.get_spell(index, level)).as_bytes()

        patch = Patch()
        patch.add_data(self.BASE_ADDRESS, data)
        return patch

    def get_spells_for_character(self, index):
        """
        :type index: int
        :return: List of spells learned for this character.
        :rtype: list[int]
        """
        if index not in range(5):
            raise ValueError("Character index must be 0-4")
        return self._spells[index]

    def get_spell(self, index, level):
        """
        :type index: int
        :type level: int
        :return: Spell for this character and level
        :rtype: int
        """
        if index not in range(5):
            raise ValueError("Character index must be 0-4")
        if level < 1 or level > 30:
            raise ValueError("Level must be between 1 and 30")
        return self._spells[index][level - 1]


class LevelUpExps:
    """Class for amounts of exp required for each levelup."""
    BASE_ADDRESS = 0x3a1aff

    def __init__(self):
        self._levels = [
            0,
            16,
            48,
            84,
            130,
            200,
            290,
            402,
            538,
            700,
            890,
            1110,
            1360,
            1640,
            1950,
            2290,
            2660,
            3060,
            3490,
            3950,
            4440,
            4960,
            5510,
            6088,
            6692,
            7320,
            7968,
            8634,
            9315,
            9999,
        ]

    def get_xp_for_level(self, level):
        """
        :type level: int
        :return: XP required to reach this level.
        :rtype: int
        """
        if level < 1 or level > 30:
            raise ValueError("Level must be between 1 and 30")
        return self._levels[level - 1]

    def get_patch(self):
        """Get patch for exp required for each level up.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        # Data is 29 blocks (starting at level 2), 2 bytes each block.
        data = bytearray()
        for level in range(2, 31):
            data += utils.ByteField(self.get_xp_for_level(level), num_bytes=2).as_bytes()

        patch = Patch()
        patch.add_data(self.BASE_ADDRESS, data)
        return patch

    def randomize(self):
        """Perform randomization of exp needed to reach each level by shuffling the difference between each level."""
        gaps = []
        for i in range(1, len(self._levels)):
            xp_to_levelup = self.get_xp_for_level(i + 1) - self.get_xp_for_level(i)
            gaps.append(utils.mutate_normal(xp_to_levelup, minimum=1, maximum=9999))
        gaps.sort()

        # Make sure we total 9999 at lvl 30.  If not, divide the difference into 435 "pieces" and add 1 piece to the
        # first levelup, 2 pieces to the second, etc. to curve it out nicely.
        total = sum(gaps)
        if total != 9999:
            diff = 9999 - total
            piece = diff / sum(range(1, 30))
            for i in range(len(gaps)):
                gaps[i] += round(piece * (i + 1))

        # Check total again for any rounding.  Just alter the final level for that, as it should only be a couple exp.
        total = sum(gaps)
        if total != 9999:
            diff = 9999 - total
            gaps[-1] += diff
            gaps.sort()

        # Now set the amount to level up for each level based on the gaps.
        prev = 0
        self._levels[0] = 0
        for i, amt in enumerate(gaps, start=1):
            new_val = prev + amt
            self._levels[i] = new_val
            prev = new_val


class Character:
    """Class for handling a character."""
    BASE_ADDRESS = 0x3a002c
    BASE_STAT_GROWTH_ADDRESS = 0x3a1b39
    BASE_STAT_BONUS_ADDRESS = 0x3a1cec
    index = 0

    starting_level = 1
    starting_hp = 1
    starting_speed = 1
    starting_attack = 1
    starting_defense = 1
    starting_magic_attack = 1
    starting_magic_defense = 1
    starting_xp = 0

    # Placeholders for vanilla starting levelup growth and bonus numbers.
    starting_growths = ()
    starting_bonuses = ()

    def __init__(self):
        self.level = self.starting_level
        self.max_hp = self.starting_hp
        self.speed = self.starting_speed
        self.attack = self.starting_attack
        self.defense = self.starting_defense
        self.magic_attack = self.starting_magic_attack
        self.magic_defense = self.starting_magic_defense
        self.xp = self.starting_xp
        self.starting_spells = set()

        # Level-up stat growth and bonuses.
        self.levelup_growths = []
        for max_hp, attack, defense, magic_attack, magic_defense in self.starting_growths:
            self.levelup_growths.append(StatGrowth(max_hp, attack, defense, magic_attack, magic_defense))

        self.levelup_bonuses = []
        for max_hp, attack, defense, magic_attack, magic_defense in self.starting_bonuses:
            self.levelup_bonuses.append(StatGrowth(max_hp, attack, defense, magic_attack, magic_defense))

    def get_stat_at_level(self, attr, level):
        """Get natural value of the given stat at the given level using just the levelup growths.

        :type attr: str
        :type level: int
        :rtype: int
        """
        if level < 1 or level > 30:
            raise ValueError("Level must be between 1 and 30")

        value = getattr(self, attr)
        for g in self.levelup_growths[:level - 1]:
            value += getattr(g, attr)
        return value

    def get_optimal_stat_at_level(self, attr, level):
        """Get optimal value of the given stat at the given level using the levelup growths and best choice bonuses.

        :type attr: str
        :type level: int
        :rtype: int
        """
        if level < 1 or level > 30:
            raise ValueError("Level must be between 1 and 30")

        value = self.get_stat_at_level(attr, level)
        for b in self.levelup_bonuses[:level - 1]:
            if attr in b.best_choices:
                value += getattr(b, attr)
        return value

    def get_max_stat_at_level(self, attr, level):
        """Get max value of the given stat at the given level using the levelup growths and bonuses.

        :type attr: str
        :type level: int
        :rtype: int
        """
        if level < 1 or level > 30:
            raise ValueError("Level must be between 1 and 30")

        value = self.get_stat_at_level(attr, level)
        for b in self.levelup_bonuses[:level - 1]:
            value += getattr(b, attr)
        return value

    def randomize(self):
        """Perform randomization for this character."""
        self.level = utils.mutate_normal(self.level, minimum=1, maximum=30)
        self.speed = utils.mutate_normal(self.speed, minimum=1, maximum=255)

        # Shuffle level up stat bonuses.
        for i, bonus in enumerate(self.levelup_bonuses):
            for attr in LEVEL_STATS:
                value = getattr(bonus, attr)
                # Make each bonus at least 1.
                setattr(bonus, attr, max(utils.mutate_normal(value, maximum=15), 1))

        # Shuffle level up stat growths up to level 20.  Past level 20, make them tiny similar to vanilla.
        for attr in LEVEL_STATS:
            # Shuffle expected value at level 20 and rework the stat curve based on the final value.
            # Make sure the stat at level 20 is at least 20, i.e. one point for each level at minimum.
            value = self.get_stat_at_level(attr, 20)
            value = utils.mutate_normal(value, minimum=20, maximum=255)

            # Generate random fixed value points between level 1 and 20 to interpolate between.
            fixed_points = [(1, 0), (20, value)]

            for _ in range(3):
                # Pick a random level range in the fixed points list that is >= 4 levels apart to spread them out a bit.
                range_index = [i for i in range(1, len(fixed_points) - 1) if
                               fixed_points[i][0] - fixed_points[i - 1][0] >= 4]
                if not range_index:
                    break

                dex = random.choice(range_index)
                lower_level, lower_value = fixed_points[dex - 1]
                upper_level, upper_value = fixed_points[dex]

                level_interval = (upper_level - lower_level) // 2
                value_interval = (upper_value - lower_value) // 2

                # Increase by at least 1 level, but not all the way to the upper level.
                level_increase = max(random.randint(0, level_interval) + random.randint(0, level_interval), 1)
                level = min(lower_level + level_increase, upper_level - 1)

                # Increase value by at least 1 for each level.
                value_increase = random.randint(0, value_interval) + random.randint(0, value_interval)
                value_increase = max(value_increase, level_increase)
                value = lower_value + value_increase

                fixed_points.append((level, value))
                fixed_points = sorted(fixed_points)

            # Linear interpolate between fixed value points to fill in the other levels.
            for ((level1, value1), (level2, value2)) in zip(fixed_points, fixed_points[1:]):
                level_difference = level2 - level1
                value_difference = value2 - value1
                for l in range(level1 + 1, level2):
                    steps_away_from_level1 = l - level1
                    factor = steps_away_from_level1 / float(level_difference)
                    # Min increase value number of steps away from level1, so we increase by at least 1 for each level.
                    v = value1 + max(int(round(factor * value_difference)), steps_away_from_level1)
                    fixed_points.append((l, v))

            fixed_points = sorted(fixed_points)
            levels, values = list(zip(*fixed_points))

            # Sanity checks
            num_points = len(fixed_points)
            if num_points != 20:
                raise ValueError("Generated fixed points is not 20 levels: {} instead".format(num_points))

            if levels != tuple(sorted(levels)):
                raise ValueError("Generate levels aren't in order: {!r}".format(levels))

            if values != tuple(sorted(values)):
                raise ValueError("Stat values aren't in order character {}, stat {}: {!r}, fixed_points {!r}".format(
                    self.__class__.__name__, attr, values, fixed_points))

            # Get increases for each levelup.
            increases = []
            for value1, value2 in zip(values, values[1:]):
                increases.append(value2 - value1)

            # Frontload bigger stat increases earlier.  For defense, make the frontload factor a bit smaller.
            frontload_factor = random.random() * random.random()
            if attr in ["defense", "magic_defense"]:
                frontload_factor *= random.random()

            base = 0
            for n, inc in enumerate(increases):
                max_index = len(increases) - 1
                factor = (((max_index - n) / float(max_index)) * frontload_factor)
                amount = int(round(inc * factor))
                base += amount
                increases[n] = (inc - amount)
            base = max(base, 1)

            # Make sure no single level has an increase greater than 15.  Shuffle increases to avoid this.
            while max(increases) > 15:
                i = increases.index(max(increases))
                increases[i] = increases[i] - 1
                choices = [n for (n, v) in enumerate(increases) if v < 15]
                if random.randint(0, len(choices)) == 0:
                    base += 1
                elif choices:
                    i = random.choice(choices)
                    increases[i] = increases[i] + 1

            # Special logic for Mario.
            if self.index == 0:
                # Make sure Mario has minimum basic starting HP and attack.  Shuffle increases to account for this.
                # TODO: Should this be applied to the other two starting characters in open mode?
                if attr in ["max_hp", "attack"]:
                    while base < 20:
                        candidates = [i for i in range(len(increases)) if increases[i] > 0]
                        if not candidates:
                            break
                        base += 1
                        weights = [(len(increases) - i) for i in candidates]
                        chosen = random.choices(candidates, weights=weights)[0]
                        increases[chosen] -= 1

                # Make sure physical attack increase for level 2 is at least 3 because of a weird oversight in the game.
                # The level up stat growths are right after the exp for level up amounts in the data.  The game doesn't
                # actually stop levelling up at 30 however, so if Mario's level 2 stat growths make a two byte "exp"
                # value less than 9999 (the max exp at lvl 30) then the game will continue to level up.  This makes
                # things get messy as dummy spells get learnt and bad data is used for level up stats.  If the physical
                # attack growth is at least 3, this will make two bytes 0x3000 at minimum which is > 12000 no matter
                # what the other values are.  This prevents this bug from happening.
                if attr == 'attack':
                    while increases[0] < 3:
                        candidates = [i for i in range(1, len(increases)) if increases[i] > 0]
                        if not candidates:
                            break
                        increases[0] += 1
                        weights = [(len(increases) - i) for i in candidates]
                        chosen = random.choices(candidates, weights=weights)[0]
                        increases[chosen] -= 1

            # Set base value and set levelup growth increases to generated values.  Past level 20, just random shuffle
            # between 1-2 to keep increases lower similar to the vanilla game.
            setattr(self, attr, base)
            for s in self.levelup_growths:
                if increases:
                    setattr(s, attr, increases.pop(0))
                else:
                    # Beyond level 20, give a 1/3 chance of 2 increase, 2/3 chance of 1 increase.
                    setattr(s, attr, random.choices([1, 2], weights=[2, 1])[0])

    def finalize(self, world):
        """Finalize character data after other shuffling has happened outside of this instance.

        :param world: World instance for this seed.
        :type world: randomizer.logic.main.GameWorld
        """
        # Determine starting stats based on starting level and best stat choices up to that point.
        for attr in LEVEL_STATS:
            # Make sure stat can't grow beyond max value.  This should be rare, but if it happens then subtract from
            # the levelup growths beyond the starting level to fix it.
            if attr == 'max_hp':
                max_allowed = 999
            else:
                max_allowed = 255

            while self.get_max_stat_at_level(attr, 30) > max_allowed:
                # Subtract 1 from a random growth that has > 1 currently so we have at least 1 per level.
                ss = [s for s in self.levelup_growths[self.level - 1:] if getattr(s, attr) > 1]
                if not ss:
                    break
                s = random.choice(ss)
                value = getattr(s, attr)
                setattr(s, attr, value - 1)

            # Set final starting stat value based on optimal bonuses.
            setattr(self, attr, self.get_optimal_stat_at_level(attr, self.level))

        # If we're in debug mode, max all starting stats.
        if world.debug_mode:
            self.level = 30
            self.max_hp = 999
            self.speed = 255
            self.attack = 255
            self.defense = 255
            self.magic_attack = 255
            self.magic_defense = 255

        # Set starting spells based on starting level and learned spells.
        self.starting_spells.clear()
        for level in range(1, self.level + 1):
            spell = world.learned_spells.get_spell(self.index, level)
            if spell != 0xff:
                self.starting_spells.add(spell)

        # Set starting exp based on starting level.
        self.xp = world.levelup_xps.get_xp_for_level(self.level)

    def get_patch(self):
        """Build patch data for this character.

        :return: Patch data for this character.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # Build character patch data.
        char_data = bytearray()
        char_data += utils.ByteField(self.level).as_bytes()
        char_data += utils.ByteField(self.max_hp, num_bytes=2).as_bytes()  # Current HP
        char_data += utils.ByteField(self.max_hp, num_bytes=2).as_bytes()  # Max HP
        char_data += utils.ByteField(self.speed).as_bytes()
        char_data += utils.ByteField(self.attack).as_bytes()
        char_data += utils.ByteField(self.defense).as_bytes()
        char_data += utils.ByteField(self.magic_attack).as_bytes()
        char_data += utils.ByteField(self.magic_defense).as_bytes()
        char_data += utils.ByteField(self.xp, num_bytes=2).as_bytes()
        # Set starting weapon/armor/accessory as blank for all characters.
        char_data += utils.ByteField(0xff).as_bytes()
        char_data += utils.ByteField(0xff).as_bytes()
        char_data += utils.ByteField(0xff).as_bytes()
        char_data.append(0x00)  # Unused byte
        char_data += utils.BitMapSet(4, self.starting_spells).as_bytes()

        # Base address plus offset based on character index.
        addr = self.BASE_ADDRESS + (self.index * 20)
        patch.add_data(addr, char_data)

        # Add levelup stat growth and bonuses to the patch data for this character.  Offset is 15 bytes for each stat
        # object, 3 bytes per character.
        for i, stat in enumerate(self.levelup_growths):
            addr = self.BASE_STAT_GROWTH_ADDRESS + (i * 15) + (self.index * 3)
            patch.add_data(addr, stat.as_bytes())

        for i, stat in enumerate(self.levelup_bonuses):
            addr = self.BASE_STAT_BONUS_ADDRESS + (i * 15) + (self.index * 3)
            patch.add_data(addr, stat.as_bytes())

        return patch

    def __str__(self):
        s = "Character({}):\n".format(self.__class__.__name__)
        s += "\tLevel: {}\n".format(self.level)
        s += "\tHP: {}\n".format(self.max_hp)
        s += "\tSpeed: {}\n".format(self.speed)
        s += "\tAttack: {}\n".format(self.attack)
        s += "\tDefense: {}\n".format(self.defense)
        s += "\tMagic Attack: {}\n".format(self.magic_attack)
        s += "\tMagic Defense: {}\n".format(self.magic_defense)
        s += "\tStarting XP: {}\n".format(self.xp)
        s += "\tStarting Spells: {}\n".format(self.starting_spells)
        return s


# Character definitions.
class Mario(Character):
    index = 0
    starting_level = 1
    starting_hp = 20
    starting_speed = 20
    starting_attack = 20
    starting_defense = 0
    starting_magic_attack = 10
    starting_magic_defense = 2
    starting_xp = 0

    # Vanilla levelup stat growths
    # (hp, attack, defense, m.attack, m.defense)
    starting_growths = (
        (5, 3, 2, 2, 2),
        (5, 3, 2, 2, 2),
        (5, 3, 3, 2, 2),
        (5, 3, 3, 2, 2),
        (5, 4, 3, 3, 2),
        (6, 4, 3, 3, 2),
        (6, 4, 3, 3, 2),
        (7, 4, 3, 3, 2),
        (7, 4, 3, 3, 2),
        (7, 5, 4, 3, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (9, 5, 4, 4, 3),
        (9, 6, 4, 4, 3),
        (9, 6, 4, 4, 3),
        (10, 6, 4, 4, 3),
        (10, 6, 4, 5, 3),
        (10, 6, 4, 5, 3),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
    )

    # Vanilla levelup stat bonus options
    # (hp, attack, defense, m.attack, m.defense)
    starting_bonuses = (
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (3, 2, 1, 1, 1),
        (4, 1, 1, 1, 1),
        (3, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
    )


class Peach(Character):
    index = 1
    starting_level = 9
    starting_hp = 50
    starting_speed = 24
    starting_attack = 40
    starting_defense = 24
    starting_magic_attack = 40
    starting_magic_defense = 28
    starting_xp = 600

    # Vanilla levelup stat growths
    # (hp, attack, defense, m.attack, m.defense)
    starting_growths = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (4, 1, 3, 4, 2),
        (5, 2, 3, 4, 3),
        (6, 3, 3, 4, 3),
        (7, 4, 3, 4, 3),
        (8, 5, 3, 4, 3),
        (9, 6, 3, 4, 3),
        (10, 7, 3, 4, 4),
        (11, 8, 4, 4, 4),
        (12, 9, 4, 4, 4),
        (13, 10, 4, 4, 4),
        (14, 10, 4, 4, 4),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
    )

    # Vanilla levelup stat bonus options
    # (hp, attack, defense, m.attack, m.defense)
    starting_bonuses = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (9, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (9, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (9, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (9, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (3, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
    )


class Bowser(Character):
    index = 2
    starting_level = 8
    starting_hp = 80
    starting_speed = 15
    starting_attack = 85
    starting_defense = 52
    starting_magic_attack = 20
    starting_magic_defense = 30
    starting_xp = 470

    # Vanilla levelup stat growths
    # (hp, attack, defense, m.attack, m.defense)
    starting_growths = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (8, 3, 3, 4, 2),
        (8, 3, 3, 4, 2),
        (8, 4, 3, 4, 2),
        (8, 4, 3, 4, 2),
        (8, 4, 3, 4, 2),
        (8, 4, 3, 4, 2),
        (8, 4, 3, 4, 2),
        (8, 5, 4, 4, 2),
        (8, 5, 4, 4, 2),
        (9, 5, 4, 4, 2),
        (9, 6, 4, 4, 2),
        (9, 6, 4, 4, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
        (4, 2, 2, 2, 2),
    )

    # Vanilla levelup stat bonus options
    # (hp, attack, defense, m.attack, m.defense)
    starting_bonuses = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
        (3, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 2, 1, 1, 1),
    )


class Geno(Character):
    index = 3
    starting_level = 6
    starting_hp = 45
    starting_speed = 30
    starting_attack = 60
    starting_defense = 23
    starting_magic_attack = 25
    starting_magic_defense = 17
    starting_xp = 234

    # Vanilla levelup stat growths
    # (hp, attack, defense, m.attack, m.defense)
    starting_growths = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (8, 5, 3, 4, 2),
        (8, 5, 3, 4, 2),
        (8, 5, 3, 4, 2),
        (8, 5, 3, 4, 2),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 4, 3),
        (8, 5, 4, 5, 3),
        (8, 5, 4, 5, 3),
        (8, 6, 4, 5, 3),
        (8, 6, 4, 5, 3),
        (8, 6, 4, 5, 3),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
        (1, 2, 3, 2, 2),
    )

    # Vanilla levelup stat bonus options
    # (hp, attack, defense, m.attack, m.defense)
    starting_bonuses = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (6, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (5, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (5, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 3, 1),
        (1, 3, 1, 1, 1),
    )


class Mallow(Character):
    index = 4
    starting_level = 2
    starting_hp = 20
    starting_speed = 18
    starting_attack = 22
    starting_defense = 3
    starting_magic_attack = 15
    starting_magic_defense = 10
    starting_xp = 30

    # Vanilla levelup stat growths
    # (hp, attack, defense, m.attack, m.defense)
    starting_growths = (
        (0, 0, 0, 0, 0),
        (4, 2, 3, 2, 2),
        (4, 2, 3, 2, 2),
        (4, 2, 3, 3, 2),
        (5, 2, 3, 3, 2),
        (5, 3, 3, 3, 2),
        (5, 3, 3, 4, 2),
        (6, 3, 3, 4, 3),
        (6, 3, 3, 4, 3),
        (6, 4, 3, 4, 3),
        (7, 4, 3, 5, 3),
        (7, 4, 3, 5, 3),
        (7, 4, 3, 5, 3),
        (8, 5, 3, 5, 3),
        (8, 5, 3, 5, 3),
        (8, 5, 3, 5, 3),
        (9, 5, 3, 5, 4),
        (9, 6, 3, 5, 4),
        (9, 6, 3, 5, 4),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
        (2, 2, 2, 2, 2),
    )

    # Vanilla levelup stat bonus options
    # (hp, attack, defense, m.attack, m.defense)
    starting_bonuses = (
        (0, 0, 0, 0, 0),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (4, 3, 1, 1, 1),
        (6, 1, 1, 1, 1),
        (4, 1, 1, 2, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 2, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 2, 1),
        (1, 3, 1, 1, 1),
        (2, 1, 1, 1, 1),
        (1, 1, 1, 2, 1),
        (1, 3, 1, 1, 1),
    )


def randomize_characters(world):
    """Randomize everything for characters for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    # Shuffle learned spells for all characters.
    if world.settings.randomize_spell_lists:
        world.learned_spells.randomize()

    # Shuffle exp required for level ups.
    if world.settings.randomize_character_stats:
        world.levelup_xps.randomize()

    # Shuffle each character if needed, and finalize starting attributes based on learned spells.
    if world.settings.randomize_character_stats:
        # Intershuffle levelup stat bonuses up to level 20 between all characters for variance.
        all_bonuses = []
        for c in world.characters:
            all_bonuses += c.levelup_bonuses[:19]

        # Shuffle physical and magical bonuses together.
        for attrs in (
                ('max_hp',),
                ('attack', 'defense'),
                ('magic_attack', 'magic_defense'),
        ):
            # Shuffle between all characters.
            shuffled = all_bonuses[:]
            random.shuffle(shuffled)

            for attr in attrs:
                swaps = []
                for s in shuffled:
                    swaps.append(getattr(s, attr))
                for bonus, bval in zip(all_bonuses, swaps):
                    setattr(bonus, attr, bval)

            # For any bonuses that are zero, pick a random non-zero one.
            non_zeros = [b for b in all_bonuses if all([getattr(b, attr) for attr in attrs])]
            for bonus in all_bonuses:
                for attr in attrs:
                    while getattr(bonus, attr) == 0:
                        setattr(bonus, attr, getattr(random.choice(non_zeros), attr))

        # Now randomize everything else including the intershuffled bonus values and other levelup growths.
        for c in world.characters:
            c.randomize()

    # If we're shuffling join order, do that now before we finalize the characters.  For standard mode, keep Mario as
    # the first character and shuffle the others.  For open mode, shuffle the whole list.
    if world.settings.randomize_join_order:
        if world.open_mode:
            random.shuffle(world.character_join_order)
        else:
            extra_characters = world.character_join_order[1:]
            random.shuffle(extra_characters)
            world.character_join_order = world.character_join_order[:1] + extra_characters

    # Adjust starting levels according to join order.  Get original levels, then update starting levels based on
    # join order with Mallow = 4, Geno = 3, Bowser = 2, Peach = 1.
    orig_levels = {}
    for c in world.characters:
        orig_levels[c.index] = c.level

    # For open mode, make the first three characters level 1 to start.  The final two join at Bowyer and Bundt,
    # so make their levels the same as Geno and Peach respectively.
    if world.open_mode:
        world.character_join_order[0].level = 1
        world.character_join_order[1].level = 1
        world.character_join_order[2].level = 1
        world.character_join_order[3].level = orig_levels[3]
        world.character_join_order[4].level = orig_levels[1]
    # For standard mode, just make their levels the same as the vanilla join order.
    else:
        for i, c in enumerate(world.character_join_order):
            c.level = orig_levels[4 - i]

    # Now finalize the characters and get patch data.
    for c in world.characters:
        c.finalize(world)
