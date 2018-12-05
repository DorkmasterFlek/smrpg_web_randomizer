# enemy randomization logic.

import random
from functools import reduce

from . import utils
from .patch import Patch

# Number of enemies
NUM_ENEMIES = 256


class EnemyAttack:
    """Class representing an enemy attack."""
    BASE_ADDRESS = 0x391226

    def __init__(self, index, name, attack_level, damage_types, hit_rate, status_effects, buffs):
        """
        :type index: int
        :type name: str
        :type attack_level: int
        :type damage_types: list[int]
        :type hit_rate: int
        :type status_effects: list[int]
        :type buffs: list[int]
        """
        self.index = index
        self.name = name
        self.attack_level = attack_level
        self.damage_types = damage_types
        self.hit_rate = hit_rate
        self.status_effects = status_effects
        self.buffs = buffs

    def randomize(self):
        """Perform randomization for this attack."""
        # If the attack has no special damage types or buffs, randomize the attack priority level.
        # Allow a small chance (1 in 495) to get the instant KO flag.  Otherwise attack level is 1-7, lower more likely.
        if not self.damage_types and not self.buffs:
            new_attack_level = random.randint(0, random.randint(0, random.randint(0, random.randint(0, 8))))
            if new_attack_level > self.attack_level:
                # If we got the instant KO flag, also hide the damage numbers.
                if new_attack_level == 8:
                    new_attack_level = 7
                    self.damage_types = [3, 5]
                self.attack_level = new_attack_level

        # If there are no buffs applied to the attack, give a 1/5 chance to apply a random status effect.
        # The status effect chosen has a 1/7 chance to be the unused "berserk" status.  If we hit this status, only
        # allow it 1/10 chance, otherwise reroll it (total berserk chance 1 in 350).
        if not self.buffs and random.randint(1, 5) == 5:
            i = random.randint(0, 6)
            if i != 4 or random.randint(1, 10) == 10:
                self.status_effects = [i]

        # If there are some buffs given by this attack, give a 50% chance to have an extra random buff.
        if self.buffs and random.randint(1, 2) == 2:
            self.buffs.append(random.randint(3, 6))

        # Shuffle hit rate.  If the attack is instant death, cap hit rate at 99% so items that protect from this
        # actually work.  Protection forces the attack to miss, but 100% hit rate can't miss so it hits anyway.
        if 3 in self.damage_types:
            max_hit_rate = 99
        else:
            max_hit_rate = 100
        self.hit_rate = utils.mutate_normal(self.hit_rate, minimum=1, maximum=max_hit_rate)

    def get_patch(self):
        """Get patch for this item.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()
        base_addr = self.BASE_ADDRESS + (self.index * 4)

        data = bytearray()

        # First byte is attack level + damage type flags in a bitmap.
        attack_flags = [i for i in range(3) if self.attack_level & (1 << i)]
        attack_flags += self.damage_types
        data += utils.BitMapSet(1, attack_flags).as_bytes()

        # Other bytes are hit rate, status effects, and buffs.
        data += utils.ByteField(self.hit_rate).as_bytes()
        data += utils.BitMapSet(1, self.status_effects).as_bytes()
        data += utils.BitMapSet(1, self.buffs).as_bytes()

        patch.add_data(base_addr, data)
        return patch


class EnemyReward:
    """Class representing enemy reward parameters (exp, coins, items)."""

    def __init__(self, index, address, xp, coins, yoshi_cookie_item, normal_item, rare_item):
        """
        :type index: int
        :type address: int
        :type xp: int
        :type coins: int
        :type yoshi_cookie_item: randomizer.logic.items.Item
        :type normal_item: randomizer.logic.items.Item
        :type rare_item: randomizer.logic.items.Item
        """
        self.index = index
        self.address = address
        self.xp = xp
        self.coins = coins
        self.yoshi_cookie_item = yoshi_cookie_item
        self.normal_item = normal_item
        self.rare_item = rare_item

    def get_patch(self):
        """Get patch for this reward.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        data = bytearray()
        data += utils.ByteField(self.xp, num_bytes=2).as_bytes()
        data += utils.ByteField(self.coins).as_bytes()
        data += utils.ByteField(self.yoshi_cookie_item.index if self.yoshi_cookie_item else 0xff).as_bytes()
        data += utils.ByteField(self.normal_item.index if self.normal_item else 0xff).as_bytes()
        data += utils.ByteField(self.rare_item.index if self.rare_item else 0xff).as_bytes()
        patch.add_data(self.address, data)

        return patch


class Enemy:
    """Class representing an enemy in the game."""
    FLOWER_BONUS_BASE_ADDRESS = 0x39bb44
    BASE_PSYCHOPATH_POINTER_ADDRESS = 0x399fd1
    PSYCHOPATH_DATA_POINTER_OFFSET = 0x390000
    BASE_PSYCHOPATH_DATA_ADDRESS = 0x39a1d1

    def __init__(self, index, address, name, boss, hp, speed, attack, defense, magic_attack, magic_defense, fp, evade,
                 magic_evade, invincible, death_immune, morph_chance, sound_on_hit, sound_on_approach, resistances,
                 weaknesses, status_immunities, palette, flower_bonus_type, flower_bonus_chance):
        """
        :type index: int
        :type address: int
        :type name: str
        :type boss: bool
        :type hp: int
        :type speed: int
        :type attack: int
        :type defense: int
        :type magic_attack: int
        :type magic_defense: int
        :type fp: int
        :type evade: int
        :type magic_evade: int
        :type invincible: bool
        :type death_immune: bool
        :type morph_chance: int
        :type sound_on_hit: int
        :type sound_on_approach: int
        :type resistances: list[int]
        :type weaknesses: list[int]
        :type status_immunities: list[int]
        :type palette: int
        :type flower_bonus_type: int
        :type flower_bonus_chance: int
        """
        self.index = index
        self.address = address
        self.name = name
        self.boss = boss
        self.hp = hp
        self.speed = speed
        self.attack = attack
        self.defense = defense
        self.magic_attack = magic_attack
        self.magic_defense = magic_defense
        self.fp = fp
        self.evade = evade
        self.magic_evade = magic_evade
        self.invincible = invincible
        self.death_immune = death_immune
        self.morph_chance = morph_chance
        self.sound_on_hit = sound_on_hit
        self.sound_on_approach = sound_on_approach
        self.resistances = resistances
        self.weaknesses = weaknesses
        self.status_immunities = status_immunities
        self.palette = palette
        self.flower_bonus_type = flower_bonus_type
        self.flower_bonus_chance = flower_bonus_chance

        # Flying enemies
        self.flying = self.index in (2, 9, 10, 12, 13, 28, 44, 66, 73, 77, 92, 108)

        # "High flying" enemies are Goby and Mr. Kipper
        self.high_flying = self.index in (9, 73)

    @property
    def rank(self):
        """Calculate rough difficulty ranking of enemy based on HP and attack stats.

        :rtype: int
        """
        hp = self.hp if self.hp >= 10 else 100
        return hp * max(self.attack, self.magic_attack, 1)

    @property
    def psychopath_text(self):
        """Make Psychopath text to show elemental weaknesses and immunities.

        :rtype: str
        """
        desc = ''

        # Elemental immunities.
        if self.resistances:
            desc += '\x7C'
            desc += utils.add_desc_fields((
                ('\x7E', 6, self.resistances),
                ('\x7D', 4, self.resistances),
                ('\x7F', 5, self.resistances),
                ('\x85', 7, self.resistances),
            ))
        else:
            desc += '\x20' * 5

        desc += '\x20'

        # Elemental weaknesses.
        if self.weaknesses:
            desc += '\x7B'
            desc += utils.add_desc_fields((
                ('\x7E', 6, self.weaknesses),
                ('\x7D', 4, self.weaknesses),
                ('\x7F', 5, self.weaknesses),
                ('\x85', 7, self.weaknesses),
            ))
        else:
            desc += '\x20' * 5

        desc += '\x20\x20'

        # Status vulnerabilities.
        vulnerabilities = [i for i in range(4) if i not in self.status_immunities]
        if vulnerabilities:
            desc += utils.add_desc_fields((
                ('\x82', 0, vulnerabilities),
                ('\x80', 1, vulnerabilities),
                ('\x83', 2, vulnerabilities),
                ('\x81', 3, vulnerabilities),
                ('\x84\x84', True, not self.death_immune),
            ))
        else:
            desc += '\x20' * 6

        desc += '\x02'

        return desc

    def get_similar(self, world):
        """Get a similar enemy to this one for formation shuffling based on rank.

        :type world: randomizer.logic.main.GameWorld
        :rtype: Enemy
        """
        # If we're a boss enemy, treat as unique.
        if self.boss:
            return self

        # Get all non-boss candidates sorted by rank.
        candidates = [e for e in world.enemies if not e.boss]
        candidates = sorted(candidates, key=lambda e: (e.rank, e.index))

        # If this is a special enemy, don't replace it.
        if self.rank < 0:
            return self
        elif self not in candidates:
            return self

        # Sort by rank and mutate our position within the list to get a replacement item.
        index = candidates.index(self)
        index = utils.mutate_normal(index, maximum=len(candidates) - 1)
        return candidates[index]

    def randomize(self):
        """Randomize stats for this enemy."""
        # Randomize main stats.  For bosses, don't let the stats go below their vanilla values.
        mutate_attributes = (
            "hp",
            "speed",
            "attack",
            "defense",
            "magic_attack",
            "magic_defense",
            "fp",
            "evade",
            "magic_evade",
        )
        old_stats = {}
        for key in mutate_attributes:
            old_stats[key] = getattr(self, key)

        self.hp = utils.mutate_normal(self.hp, minimum=1, maximum=32000)
        self.speed = utils.mutate_normal(self.speed)
        self.attack = utils.mutate_normal(self.attack)
        self.defense = utils.mutate_normal(self.defense)
        self.magic_attack = utils.mutate_normal(self.magic_attack)
        self.magic_defense = utils.mutate_normal(self.magic_defense)
        self.fp = utils.mutate_normal(self.fp)
        self.evade = utils.mutate_normal(self.evade, minimum=0, maximum=100)
        self.magic_evade = utils.mutate_normal(self.magic_evade, minimum=0, maximum=100)

        if self.boss:
            for attr, old_val in old_stats.items():
                if getattr(self, attr) < old_val:
                    setattr(self, attr, old_val)

        if self.boss:
            # For bosses, allow a small 1/255 chance to be vulnerable to Geno Whirl.
            if utils.coin_flip(1 / 255):
                self.death_immune = False

        else:
            # Have a 1/3 chance of reversing instant death immunity for normal enemies.
            if random.randint(1, 3) == 3:
                self.death_immune = not self.death_immune

            # Randomize morph item chance of success.
            self.morph_chance = random.randint(0, 3)

        # Shuffle elemental resistances and status immunities.  Keep the same number but randomize them for now.
        self.status_immunities = random.sample(range(0, 4), len(self.status_immunities))

        # Make a 50/50 chance to prioritize elemental immunities over weaknesses or vice versa.
        # Allow earth (jump) to be in both however, because they can be weak to jump while immune to it.
        # Jump Shoes bypass the immunity and they'll take double damage.
        if utils.coin_flip():
            self.resistances = random.sample(range(4, 8), len(self.resistances))
            potential_weaknesses = set(range(4, 8)) - set(self.resistances)
            potential_weaknesses.add(7)
            self.weaknesses = random.sample(potential_weaknesses, min(len(self.weaknesses), len(potential_weaknesses)))
        else:
            self.weaknesses = random.sample(range(4, 8), len(self.weaknesses))
            potential_resistances = set(range(4, 8)) - set(self.weaknesses)
            potential_resistances.add(7)
            self.resistances = random.sample(potential_resistances, min(len(self.resistances), len(potential_resistances)))

        # Randomize flower bonus type and chance for this enemy.
        self.flower_bonus_type = random.randint(1, 5)
        self.flower_bonus_chance = random.randint(0, 5) + random.randint(0, 5)

    def get_patch(self):
        """Get patch for this enemy.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # Main stats.
        data = bytearray()
        data += utils.ByteField(self.hp, num_bytes=2).as_bytes()
        data += utils.ByteField(self.speed).as_bytes()
        data += utils.ByteField(self.attack).as_bytes()
        data += utils.ByteField(self.defense).as_bytes()
        data += utils.ByteField(self.magic_attack).as_bytes()
        data += utils.ByteField(self.magic_defense).as_bytes()
        data += utils.ByteField(self.fp).as_bytes()
        data += utils.ByteField(self.evade).as_bytes()
        data += utils.ByteField(self.magic_evade).as_bytes()
        patch.add_data(self.address, data)

        # Special defense bits, sound on approach is top half.
        data = bytearray()
        hit_special_defense = 1 if self.invincible else 0
        hit_special_defense |= (1 if self.death_immune else 0) << 1
        hit_special_defense |= self.morph_chance << 2
        hit_special_defense |= self.sound_on_approach << 4
        data.append(hit_special_defense)

        # Elemental resistances.
        data += utils.BitMapSet(1, self.resistances).as_bytes()

        # Elemental weaknesses byte (top half), sound on hit is bottom half.
        weaknesses_approach = self.sound_on_hit
        for weakness in self.weaknesses:
            weaknesses_approach |= 1 << weakness
        data.append(weaknesses_approach)

        # Status immunities.
        data += utils.BitMapSet(1, self.status_immunities).as_bytes()

        patch.add_data(self.address + 11, data)

        # Flower bonus.
        bonus_addr = self.FLOWER_BONUS_BASE_ADDRESS + self.index
        bonus = self.flower_bonus_chance << 4
        bonus |= self.flower_bonus_type
        patch.add_data(bonus_addr, utils.ByteField(bonus).as_bytes())

        # For Dodo boss enemy, update the battle event trigger so he runs away from the solo fight at 60% of his
        # shuffled HP, not always 600 HP like the vanilla game.
        if self.index == 56:
            run_away = int(round(self.hp * 0.6))
            patch.add_data(0x393818, utils.ByteField(run_away, num_bytes=2).as_bytes())

        return patch

    @classmethod
    def build_psychopath_patch(cls, world):
        """Build patch data for Psychopath text.  These use pointers, so we need to do them all together.

        :type world: randomizer.logic.main.GameWorld
        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # Begin text data with a single null byte to use for all empty text to save space.
        pointer_data = bytearray()
        text_data = bytearray()
        text_data.append(0x00)

        for i in range(NUM_ENEMIES):
            try:
                enemy = world.get_enemy_by_index(i)
            except KeyError:
                desc = ''
            else:
                desc = enemy.psychopath_text

            # If the description is empty, just use the null byte at the very beginning.
            if not desc:
                pointer = cls.BASE_PSYCHOPATH_DATA_ADDRESS - cls.PSYCHOPATH_DATA_POINTER_OFFSET
                pointer_data += utils.ByteField(pointer, num_bytes=2).as_bytes()
                continue

            # Compute pointer from base address and current data length.
            pointer = cls.BASE_PSYCHOPATH_DATA_ADDRESS + len(text_data) - cls.PSYCHOPATH_DATA_POINTER_OFFSET
            pointer_data += utils.ByteField(pointer, num_bytes=2).as_bytes()

            # Add null byte to terminate the text string.
            desc = desc.encode('latin1')
            desc += bytes([0x00])
            text_data += desc

        # Sanity check that pointer data has the correct number of items.
        if len(pointer_data) != NUM_ENEMIES * 2:
            raise ValueError("Wrong length for pointer data, something went wrong...")

        # Add pointer data, then add text data.
        patch.add_data(cls.BASE_PSYCHOPATH_POINTER_ADDRESS, pointer_data)
        patch.add_data(cls.BASE_PSYCHOPATH_DATA_ADDRESS, text_data)

        return patch


class FormationMember:
    """Class representing a single enemy in a formation with meta data."""

    def __init__(self, index, hidden_at_start, enemy, x_pos, y_pos):
        """
        :type index: int
        :type hidden_at_start: bool
        :type enemy: Enemy
        :type x_pos: int
        :type y_pos: int
        """
        self.index = index
        self.hidden_at_start = hidden_at_start
        self.enemy = enemy
        self.x_pos = x_pos
        self.y_pos = y_pos


class EnemyFormation:
    """Class representing an enemy formation for a battle."""
    BASE_ADDRESS = 0x39C000
    BASE_META_ADDRESS = 0x392AAA

    # Valid x,y coordinates for enemies in formations based on vanilla data.
    valid_coordinates = (
        (119, 111),
        (119, 119),
        (119, 127),
        (135, 103),
        (135, 111),
        (135, 119),
        (135, 127),
        (151, 103),
        (151, 111),
        (151, 119),
        (151, 127),
        (151, 135),
        (151, 143),
        (167, 103),
        (167, 111),
        (167, 119),
        (167, 127),
        (167, 135),
        (167, 143),
        (167, 151),
        (183, 103),
        (183, 111),
        (183, 119),
        (183, 127),
        (183, 135),
        (183, 143),
        (183, 151),
        (183, 159),
        (199, 119),
        (199, 135),
        (199, 143),
        (199, 151),
        (199, 159),
        (215, 111),
        (215, 119),
        (215, 127),
        (215, 135),
        (215, 143),
        (215, 151),
        (215, 159),
        (231, 127),
        (231, 135),
        (231, 143),
        (231, 151),
        (231, 159),
    )

    lower_x = min(c[0] for c in valid_coordinates)
    upper_x = max(c[0] for c in valid_coordinates)
    lower_y = min(c[1] for c in valid_coordinates)
    upper_y = max(c[1] for c in valid_coordinates)

    def __init__(self, index, event_at_start, misc_flags, members):
        """
        :type index: int
        :type event_at_start: int
        :type misc_flags: int
        :type members: list[FormationMember]
        """
        self.index = index
        self.event_at_start = event_at_start
        self.misc_flags = misc_flags
        self.members = members
        self.leaders = set()

    @property
    def bosses(self):
        return [m.enemy for m in self.members if m.enemy.boss]

    @property
    def hidden_enemies(self):
        return [m.enemy for m in self.members if m.hidden_at_start]

    def mutate_coordinate(self, x, y):
        x = utils.mutate_normal(x, minimum=self.lower_x, maximum=self.upper_x)
        y = utils.mutate_normal(y, minimum=self.lower_y, maximum=self.upper_y)
        return x, y

    def get_distance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def get_collective_distance(self, x, y, points):
        distances = [self.get_distance(x, y, x2, y2) for x2, y2 in points]
        return reduce(lambda a, b: a * b, distances, 1)

    def select_most_distance(self, candidates, done_coordinates):
        score = lambda x, y: self.get_collective_distance(x, y, done_coordinates)
        chosen = max(candidates, key=lambda c: score(c[0], c[1]))
        return chosen

    def randomize(self, world):
        """Randomize this enemy formation.

        :type world: randomizer.logic.main.GameWorld
        """
        # Max enemies for a given group.
        MAX_ENEMIES = 6

        # Don't shuffle any formations with bosses or hidden enemies (special battle events), or empty groups.
        if self.bosses or self.hidden_enemies or not self.members:
            return

        # If we have less than three leader enemies, get a randomized similar ranked one.
        candidates = list(self.leaders)
        while len(candidates) < 3:
            base = random.choice(candidates)
            new = base.get_similar(world)
            if new not in candidates:
                candidates.append(new)

        # Make sure we have at most three unique candidates.
        num_candidates = len(set(candidates))
        if num_candidates > 3:
            raise ValueError("Got more than three unique candidates, {} instead".format(num_candidates))

        # Pick random number of enemies for the group, weighted slightly lower.
        num_enemies = random.randint(1, random.randint(3, MAX_ENEMIES))
        num_enemies = max(num_enemies, len(self.leaders))
        chosen_enemies = list(self.leaders)

        # Fill out the number of enemies with randomly chosen candidates, but make sure VRAM palette totals less than
        # 64 because the VRAM can only hold so much palette data at once.
        while len(chosen_enemies) < num_enemies:
            vram_total = sum([e.palette for e in chosen_enemies])
            sub_candidates = candidates + chosen_enemies
            sub_candidates = [e for e in sub_candidates if vram_total + e.palette <= 64]
            if not sub_candidates:
                break
            chosen_enemies.append(random.choice(sub_candidates))

        random.shuffle(chosen_enemies)

        # Randomize coordinates for the chosen enemies.
        self.members = []
        done_coordinates = []
        for i in range(8):
            if i < len(chosen_enemies):
                enemy = chosen_enemies[i]
                while True:
                    if not done_coordinates:
                        x, y = random.choice(self.valid_coordinates)
                        x, y = self.mutate_coordinate(x, y)
                    else:
                        candidates = random.sample(self.valid_coordinates, len(chosen_enemies) * 2)
                        candidates = [self.mutate_coordinate(c[0], c[1]) for c in candidates]
                        x, y = self.select_most_distance(candidates, done_coordinates)

                    # High flying units with an x coord of 119-124 cannot have a y coordinate of 138 or higher, or the
                    # game will softlock after they finish attacking.  Reroll if we hit this scenario.
                    if enemy.high_flying and 119 <= x <= 124 and y >= 138:
                        continue
                    # Regular flying enemies will softlock in the range x 116-153, y 150-168
                    elif enemy.flying and 116 <= x <= 153 and 150 <= y <= 168:
                        continue

                    done_coordinates.append((x, y))
                    self.members.append(FormationMember(i, False, enemy, x, y))
                    break

        self.members.sort(key=lambda m: m.index)

        done_coordinates = sorted(done_coordinates)
        for i, (x, y) in enumerate(done_coordinates):
            self.members[i].x_pos = x
            self.members[i].y_pos = y

    def get_patch(self):
        """Get patch for this formation.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        data = bytearray()

        # Monsters present bitmap.
        monsters_present = [7 - m.index for m in self.members]
        data += utils.BitMapSet(1, monsters_present).as_bytes()

        # Monsters hidden bitmap.
        monsters_hidden = [7 - m.index for m in self.members if m.hidden_at_start]
        data += utils.BitMapSet(1, monsters_hidden).as_bytes()

        # Monster data.
        for member in self.members:
            data += utils.ByteField(member.enemy.index).as_bytes()
            data += utils.ByteField(member.x_pos).as_bytes()
            data += utils.ByteField(member.y_pos).as_bytes()

        base_addr = self.BASE_ADDRESS + (self.index * 26)
        patch.add_data(base_addr, data)

        return patch


class FormationPack:
    """Class representing a pack of enemy formations.  For each encounter, the game chooses a random formation of
    enemies from the pack being encountered.  For bosses, all the formations are just the same.
    """
    BASE_ADDRESS = 0x39222A

    def __init__(self, index, formations):
        """
        :type index: int
        :type formations: list[EnemyFormation]
        """
        self.index = index
        self.formations = formations

    @property
    def common_enemies(self):
        """Common enemies between all formations in this pack.

        :rtype: list[Enemy]
        """
        enemies = set(m.enemy for m in self.formations[0].members)
        for f in self.formations[1:]:
            enemies &= set(m.enemy for m in f.members)
        return sorted(enemies, key=lambda e: e.index)

    def get_patch(self):
        """Get patch for this formation pack.

        :return: Patch data.
        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        data = bytearray()

        hi_num = False
        for formation in self.formations:
            val = formation.index

            # For formations > 255, set the high bank indicator since each formation is a single byte only.
            if val > 255:
                hi_num = True
                val -= 255

            data += utils.ByteField(val).as_bytes()

        # High bank indicator.
        val = 7 if hi_num else 0
        data += utils.ByteField(val).as_bytes()

        base_addr = self.BASE_ADDRESS + (self.index * 4)
        patch.add_data(base_addr, data)

        return patch


def randomize_enemies(world):
    """Randomize everything for enemies for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    if world.settings.randomize_monsters:
        # *** Shuffle enemy attacks ***
        # Intershuffle attacks with status effects.
        with_status_effects = [a for a in world.enemy_attacks if a.status_effects]
        for attr in ('hit_rate', 'status_effects'):
            shuffled = with_status_effects[:]
            random.shuffle(shuffled)
            swaps = []
            for attack in shuffled:
                swaps.append(getattr(attack, attr))
            for attack, swapped_val in zip(with_status_effects, swaps):
                setattr(attack, attr, swapped_val)

        # Now perform normal shuffle for the rest, and get patch data.
        for attack in world.enemy_attacks:
            attack.randomize()

        # *** Shuffle enemy stats ***
        # Start with inter-shuffling some stats between non-boss enemies around the same rank as each other.
        candidates = [m for m in world.enemies if not m.boss]
        candidates.sort(key=lambda c: c.rank)

        for attribute in ("hp", "speed", "defense", "magic_defense", "evade", "magic_evade", "resistances",
                          "weaknesses", "status_immunities"):
            shuffled = candidates[:]
            max_index = len(candidates) - 1
            done = set()

            # For each enemy, have a 50/50 chance of swapping stat with the next enemy up sorted by rank.
            for i in range(len(candidates)):
                new_index = i
                if shuffled[i] in done:
                    continue
                while random.randint(0, 1) == 1:
                    new_index += 1
                new_index = int(round(new_index))
                new_index = min(new_index, max_index)
                a, b = shuffled[i], shuffled[new_index]
                done.add(a)
                shuffled[i] = b
                shuffled[new_index] = a

            # Now swap attribute values with shuffled list.
            swaps = []
            for a, b in zip(candidates, shuffled):
                aval, bval = getattr(a, attribute), getattr(b, attribute)
                swaps.append(bval)
            for a, bval in zip(candidates, swaps):
                setattr(a, attribute, bval)

        # Now inter-shuffle morph chances randomly.
        valid = [m for m in world.enemies if not m.boss]
        morph_chances = [m.morph_chance for m in valid]
        random.shuffle(morph_chances)
        for chance, m in zip(morph_chances, valid):
            m.morph_chance = chance

        # Finally shuffle enemy attribute values as normal.
        for m in world.enemies:
            m.randomize()

        # *** Shuffle enemy rewards ***
        # Intershuffle xp, coins, and items like old logic.
        candidates = [r for r in world.enemy_rewards if not world.get_enemy_by_index(r.index).boss and r.xp > 0 and (
                r.normal_item != r.rare_item or r.normal_item == 0xFF)]
        candidates.sort(key=lambda r: world.get_enemy_by_index(r.index).rank)

        for attribute in ("xp", "coins", "normal_item", "rare_item"):
            shuffled = candidates[:]
            max_index = len(candidates) - 1
            done = set()

            # For each reward, have a 50/50 chance of swapping stat with the next one up sorted by rank.
            for i in range(len(candidates)):
                new_index = i
                if shuffled[i] in done:
                    continue
                while random.randint(0, 1) == 1:
                    new_index += 1
                new_index = int(round(new_index))
                new_index = min(new_index, max_index)
                a, b = shuffled[i], shuffled[new_index]
                done.add(a)
                shuffled[i] = b
                shuffled[new_index] = a

            # Now swap attribute values with shuffled list.
            swaps = []
            for a, b in zip(candidates, shuffled):
                aval, bval = getattr(a, attribute), getattr(b, attribute)
                swaps.append(bval)
            for a, bval in zip(candidates, swaps):
                setattr(a, attribute, bval)

    # Randomize individual rewards on their own.
    if world.settings.randomize_drops:
        for r in world.enemy_rewards:
            enemy = world.get_enemy_by_index(r.index)
            r.coins = utils.mutate_normal(r.coins, maximum=255)

            # For bosses, don't let exp go above vanilla.  For normal enemies, don't let it go below.
            oldxp = r.xp
            r.xp = utils.mutate_normal(r.xp, minimum=1, maximum=65535)
            if enemy.boss:
                r.xp = min(oldxp, r.xp)
            else:
                r.xp = max(oldxp, r.xp)

            # Shuffle reward items with other consumable items.
            linked = r.normal_item == r.rare_item
            consumables = [i for i in world.items if i.consumable and not i.reuseable]

            # Shuffle normal item, if this reward has one.
            if r.normal_item:
                r.normal_item = r.normal_item.get_similar(consumables)

            # If we're linked, set the rare item to the normal one.  Otherwise shuffle the rare one as well.
            if linked:
                r.rare_item = r.normal_item
            elif r.rare_item:
                r.rare_item = r.rare_item.get_similar(consumables)

            # If we have a morph chance, randomize the Yoshi Cookie item.
            if enemy.morph_chance:
                r.yoshi_cookie_item = random.choice(consumables)
            else:
                r.yoshi_cookie_item = None

    # Shuffle enemy formations.
    if world.settings.randomize_enemy_formations:
        for formation in world.enemy_formations:
            formation.randomize(world)
