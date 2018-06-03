import io
from collections import defaultdict
from functools import reduce
from os import path

from .interface import get_flags, clean_and_write, set_flags, set_seed
from .tablereader import TableObject, tblpath, set_global_table_filename, set_table_specs, sort_good_order, \
    reset_everything
from .utils import classproperty, mutate_normal, shuffle_bits, utilrandom as random

VERSION = 5
ALL_OBJECTS = None
LEVEL_STATS = ["max_hp", "attack", "defense", "magic_attack", "magic_defense"]
EQUIP_STATS = ["speed", "attack", "defense", "magic_attack", "magic_defense"]


ITEM_ORDER_FILENAME = path.join(tblpath, "item_order.txt")
iof = open(ITEM_ORDER_FILENAME)
ITEM_ORDER = [int(line.strip(), 0x10) for line in iof.readlines()
              if line.strip()]
iof.close()


class CharIndexObject:
    @property
    def level(self):
        return (self.index // 5) + 2

    @property
    def character_id(self):
        return self.index % 5

    @classmethod
    def get_by_character(cls, character, index):
        candidates = [c for c in cls.every if c.character_id == character]
        return candidates[index]

    @property
    def character(self):
        return CharacterObject.get(self.character_id)


class StatObject(CharIndexObject):
    @property
    def attack(self):
        return self.physical >> 4

    @property
    def defense(self):
        return self.physical & 0xF

    @property
    def magic_attack(self):
        return self.magical >> 4

    @property
    def magic_defense(self):
        return self.magical & 0xF

    def set_stat(self, attr, value):
        assert 0 <= value <= 0xF
        if attr == "max_hp":
            self.max_hp = value
            return

        if attr in ["attack", "defense"]:
            affected = "physical"
        elif attr in ["magic_attack", "magic_defense"]:
            affected = "magical"

        oldvalue = getattr(self, affected)
        if attr in ["attack", "magic_attack"]:
            newvalue = (oldvalue & 0xF) | (value << 4)
        elif attr in ["defense", "magic_defense"]:
            newvalue = (oldvalue & 0xF0) | value

        setattr(self, affected, newvalue)


class EnemSpriteObject(TableObject): pass
class AnimSeqPTRObject(TableObject): pass


class MonsterObject(TableObject):
    flag = "m"
    flag_description = "monsters"
    mutate_attributes = {
        "hp": (1, 32000),
        "speed": None,
        "attack": None,
        "defense": None,
        "magic_attack": None,
        "magic_defense": None,
        "fp": None,
        "evade": None,
        "magic_evade": None
        }
    intershuffle_attributes = [
            "hp", "speed", "defense",
            "magic_defense", "evade", "magic_evade", "resistances",
            "immunities", "weaknesses_approach",
            #"coin_anim_entrance", (floating + random coordinates = freeze?)
        ]

    # Unused indexes and enemies that cause problems when shuffled outside their groups.
    banned_indexes = {
        0x4e, 0x61, 0x6f, 0x73, 0x74, 0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x8d, 0x8e, 0x96, 0x97, 0x98,
        0xa0, 0xa1, 0xab, 0xac, 0xad, 0xae, 0xaf, 0xb0, 0xb4, 0xb7, 0xb9, 0xba,
        0xc9, 0xcb, 0xd6, 0xe7, 0xe8, 0xf2, 0xf7, 0xf8, 0xfa, 0xfe,
    }

    # Boss enemies that shouldn't be shuffled to other groups, and also different stat shuffle algorithm.
    boss_indexes = {
        0x1b,  # HAMMER BRO
        0x21,  # MAGIKOOPA
        0x32,  # CLERK
        0x33,  # GUNYOLK
        0x34,  # BOOMER
        0x38,  # DODO
        0x39,  # JESTER
        0x4a,  # FACTORY CHIEF
        0x4c,  # MANAGER
        0x57,  # HIDON
        0x61,  # MERLIN
        0x62,  # MUCKLE
        0x72,  # DIRECTOR
        0x77,  # LUMBLER
        0x88,  # SUPER SPIKE
        0x89,  # DODO
        0x8e,  # TORTE
        0x95,  # FIRE CRYSTAL
        0x96,  # WATER CRYSTAL
        0x97,  # EARTH CRYSTAL
        0x98,  # WIND CRYSTAL
        0x9a,  # TOADSTOOL 2
        0x9f,  # KINKLINK
        0xa2,  # SMELTER
        0xb3,  # JAGGER
        0xb5,  # SMITHY
        0xb6,  # SMITHY
        0xbc,  # YARIDOVICH
        0xbd,  # HELIO
        0xbe,  # RIGHT EYE
        0xbf,  # LEFT EYE
        0xc0,  # KNIFE GUY
        0xc1,  # GRATE GUY
        0xc2,  # BUNDT
        0xc3,  # JINX
        0xc4,  # JINX
        0xc5,  # COUNT DOWN
        0xc6,  # DING}A}LING
        0xc7,  # BELOME
        0xc8,  # BELOME
        0xca,  # SMILAX
        0xcc,  # MEGASMILAX
        0xcd,  # BIRDO
        0xce,  # EGGBERT
        0xcf,  # AXEM YELLOW
        0xd0,  # PUNCHINELLO
        0xd1,  # TENTACLES
        0xd2,  # AXEM RED
        0xd3,  # AXEM GREEN
        0xd4,  # KING BOMB
        0xd5,  # MEZZO BOMB
        0xd7,  # RASPBERRY
        0xd8,  # KING CALAMARI
        0xd9,  # TENTACLES
        0xda,  # JINX
        0xdb,  # ZOMBONE
        0xdc,  # CZAR DRAGON
        0xdd,  # CLOAKER
        0xde,  # DOMINO
        0xdf,  # MAD ADDER
        0xe0,  # MACK
        0xe1,  # BODYGUARD
        0xe2,  # YARIDOVICH
        0xe3,  # DRILL BIT
        0xe4,  # AXEM PINK
        0xe5,  # AXEM BLACK
        0xe6,  # BOWYER
        0xe9,  # EXOR
        0xea,  # SMITHY
        0xeb,  # SHYPER
        0xec,  # SMITHY
        0xed,  # SMITHY
        0xee,  # SMITHY
        0xef,  # SMITHY
        0xf0,  # CROCO
        0xf1,  # CROCO
        0xf3,  # EARTH LINK
        0xf4,  # BOWSER
        0xf5,  # AXEM RANGERS
        0xf6,  # BOOSTER
        0xf9,  # JOHNNY
        0xfa,  # JOHNNY (solo vs. Mario)
        0xfb,  # VALENTINA
        0xfc,  # CLOAKER
        0xfd,  # DOMINO
        0xff,  # CULEX
    }

    def get_similar(self):
        if self.is_boss:
            return self
        candidates = [m for m in MonsterObject.ranked
                      if not m.is_boss]
        return super(MonsterObject, self).get_similar(candidates)

    @property
    def in_a_formation(self):
        if hasattr(self, "_in_a_formation"):
            return self._in_a_formation

        for e in MonsterObject.every:
            e._in_a_formation = False
        for p in PackObject.every:
            for f in p.formations:
                for e in f.enemies:
                    e._in_a_formation = True

        return self.in_a_formation

    @property
    def banned(self):
        return self.index in self.banned_indexes

    @property
    def vram_value(self):
        if hasattr(self, "_vram_value"):
            return self._vram_value
        anim_index = EnemSpriteObject.get(self.index).animation
        ptr = AnimSeqPTRObject.get(anim_index).anim_seq_ptr
        ptr &= 0x3fffff

        # Figure out which data dump file has our VRAM data.
        if ptr >= 0x360000:
            ptr -= 0x360000
            mod = '_obj_anim_data'
        else:
            ptr -= 0x259000
            mod = '_obj_seq_data'

        assert(ptr >= 0)

        mname = self.region + mod
        m = __import__(mname)

        f = io.BytesIO(m.DATA)
        f.seek(ptr + 8)
        self._vram_value = f.read(1)[0]
        f.close()
        return self.vram_value

    @property
    def name(self):
        try:
            return MonsterNameObject.get(self.index).name
        except KeyError:
            return "Unknown Monster Name ({})".format(self.index)

    @property
    def rank(self):
        hp = self.hp if self.hp >= 10 else 100
        return hp * max(self.attack, self.magic_attack, 1)

    @property
    def intershuffle_valid(self):
        return not self.is_boss

    @property
    def immune_death(self):
        return self.hit_special_defense & 0x02

    @property
    def morph_chance(self):
        return self.hit_special_defense & 0x0C

    @property
    def event_on_death(self):
        return self.misc & 1

    @property
    def is_boss(self):
        if self.index in self.boss_indexes or self.banned or self.event_on_death:
            return True
        return False

    @classmethod
    def intershuffle(cls):
        super(MonsterObject, cls).intershuffle()
        valid = [m for m in cls.every if m.intershuffle_valid]
        hitspecs = [m.hit_special_defense & 0xFC for m in valid]
        random.shuffle(hitspecs)
        for hs, m in zip(hitspecs, valid):
            m.hit_special_defense = (m.hit_special_defense & 0x03) | hs

    def mutate(self):
        oldstats = {}
        for key in self.mutate_attributes:
            oldstats[key] = getattr(self, key)
        super(MonsterObject, self).mutate()
        if self.is_boss:
            for (attr, oldval) in list(oldstats.items()):
                if getattr(self, attr) < oldval:
                    setattr(self, attr, oldval)

        if self.is_boss:
            while True:
                chance = random.randint(0, 3)
                if chance == 0:
                    break
                if chance == 1:
                    self.resistances |= (1 << random.randint(4, 7))
                elif chance == 2:
                    self.immunities |= (1 << random.randint(0, 3))
                elif chance == 3:
                    weak = (1 << random.randint(4, 7))
                    if self.weaknesses_approach & weak:
                        self.weaknesses_approach ^= weak
        else:
            resistances = shuffle_bits(self.resistances >> 4, size=4)
            self.resistances = resistances << 4
            self.immunities = shuffle_bits(self.immunities, size=4)
            weak = shuffle_bits(self.weaknesses_approach >> 4, size=4)
            self.weaknesses_approach &= 0x0F
            self.weaknesses_approach |= (weak << 4)
            if random.randint(1, 3) == 3:
                self.hit_special_defense ^= 0x2
            self.hit_special_defense ^= (random.randint(0, 3) << 2)

    @classmethod
    def full_cleanup(cls):
        smithies = [m for m in MonsterObject.every
                    if m.index in [0xb5, 0xb6, 0xed, 0xee, 0xef]]
        hp = max([m.hp for m in smithies])
        for s in smithies:
            s.hp = hp
        super(MonsterObject, cls).full_cleanup()


class MonsterNameObject(TableObject): pass


class MonsterAttackObject(TableObject):
    flag = "m"
    mutate_attributes = {"hitrate": (1, 100)}
    intershuffle_attributes = ["hitrate", "ailments"]
    restricted_indexes = [
        98,             # terrapin
        100,            # bowser
        3, 16, 124,     # goomba
        3, 96,          # hammer bro
        14, 25,         # croco 1
        13,             # shyster & mack
        1, 41, 44,      # belome 1
        ]

    @property
    def intershuffle_valid(self):
        return self.ailments and self.index not in self.restricted_indexes

    @property
    def no_damage(self):
        return self.misc_multiplier & 0x50

    @property
    def multiplier(self):
        return self.misc_multiplier & 0xF

    @property
    def hide_digits(self):
        return self.misc_multiplier & 0x20

    def mutate(self):
        if self.index in self.restricted_indexes:
            return
        if self.multiplier <= 7 and not self.buffs:
            new_multiplier = random.randint(0, random.randint(
                0, random.randint(0, random.randint(0, 8))))
            if new_multiplier > self.multiplier:
                self.misc_multiplier = new_multiplier
        if not self.buffs and random.randint(1, 5) == 5:
            i = random.randint(0, 6)
            if i != 4 or random.randint(1, 10) == 10:
                self.ailments = (0 | 1 << i)
        if self.buffs and random.choice([True, False]):
            self.buffs |= 1 << random.randint(3, 6)
        super(MonsterAttackObject, self).mutate()


class MonsterRewardObject(TableObject):
    flag = "d"
    mutate_attributes = {"xp": (1, 65535),
                         "coins": (0, 255),
                         }
    intershuffle_attributes = ["xp", "coins", "drop", "rare_drop"]

    @property
    def intershuffle_valid(self):
        return self.monster.intershuffle_valid and self.xp > 0 and (
            self.drop != self.rare_drop or self.drop == 0xFF)

    @property
    def rank(self):
        return self.monster.rank

    @classproperty
    def after_order(self):
        objs = []
        if 'p' in get_flags():
            objs.append(ShopObject)
        if 'm' in get_flags():
            objs.append(MonsterObject)
        return objs

    def __repr__(self):
        return "%s %s %s %s %s %s" % (
            self.monster.name, self.drop_item.name, self.rare_drop_item.name,
            self.yoshi_cookie_item.name, self.xp, self.coins)

    @property
    def monster(self):
        return MonsterObject.get(self.index)

    @property
    def rare_drop_item(self):
        return ItemObject.get(self.rare_drop)

    @property
    def drop_item(self):
        return ItemObject.get(self.drop)

    @property
    def yoshi_cookie_item(self):
        return ItemObject.get(self.yoshi_cookie)

    def mutate(self):
        oldxp = self.xp
        super(MonsterRewardObject, self).mutate()
        if self.monster.is_boss:
            self.xp = min(oldxp, self.xp)
        else:
            self.xp = max(oldxp, self.xp)
        consumables = [i for i in ItemObject.every
                       if i.is_consumable and not i.reuseable and not i.banned]
        if self.drop == self.rare_drop:
            linked = True
        else:
            linked = False
        self.drop = ItemObject.get(self.drop).get_similar(consumables).index
        if linked:
            self.rare_drop = self.drop
        else:
            self.rare_drop = ItemObject.get(
                self.rare_drop).get_similar(consumables).index

    def randomize(self):
        if self.monster.morph_chance and not self.monster.banned:
            self.yoshi_cookie = random.choice(
                [i for i in ItemObject.every
                 if i.is_consumable and not i.banned]).index
        else:
            self.yoshi_cookie = 0xFF


class PackObject(TableObject):
    flag = 'f'

    @classproperty
    def after_order(self):
        return [FormationObject]

    def __repr__(self):
        s = "PACK %x (%x) %s\n" % (
            self.index, self.misc,
            [e.name.strip() for e in self.common_enemies])
        if len(set(self.formation_ids)) == 1:
            formations = [self.formations[0]]
        else:
            formations = self.formations
        for f in formations:
            s += "%s\n" % f
        return s.strip()

    @property
    def rank(self):
        return sum([f.rank for f in self.formations])

    @property
    def formations(self):
        if self.misc == 7:
            mask = 0x100
        else:
            mask = 0
        return [FormationObject.get(f | mask) for f in self.formation_ids]

    @property
    def is_static(self):
        return len(set(self.formation_ids)) == 1

    @property
    def common_enemies(self):
        enemies = set(self.formations[0].enemies)
        for f in self.formations[1:]:
            enemies &= set(f.enemies)
        return sorted(enemies, key=lambda e: e.index)


class FormationObject(TableObject):
    flag = "f"
    flag_description = "enemy formations"

    def __repr__(self):
        present = bin(self.enemies_present)[2:]
        hidden = bin(self.enemies_hidden)[2:]
        present = "{0:0>8}".format(present)
        hidden = "{0:0>8}".format(hidden)
        s = "%x: " % self.index
        for i, (p, h) in enumerate(zip(present, hidden)):
            index, x, y = (getattr(self, "monster%s" % i),
                           getattr(self, "monster%s_x" % i),
                           getattr(self, "monster%s_y" % i))
            m = MonsterObject.get(index)
            if h == "1" or p == "1":
                s += "%x %s" % (index, m.name.strip())
                if m in self.leaders:
                    s += "*"
            if h != "1" and p == "1":
                s += " (%s, %s); " % (x, y)
            if h == "1":
                assert p == "1"
                s += " (hidden, %s, %s); " % (x, y)
        s = s.strip().rstrip(";").strip()
        return s

    @property
    def vram_used(self):
        if self.enemies_hidden:
            return None
        return sum([e.vram_value for e in self.enemies])

    @property
    def coordinates(self):
        coordinates = []
        for i in range(8):
            if self.enemies_present & (1 << (7-i)):
                coordinates.append((getattr(self, "monster%s_x" % i),
                                    getattr(self, "monster%s_y" % i)))
        return coordinates

    @property
    def rank(self):
        enemies = sorted(self.enemies, key=lambda m: m.rank, reverse=True)
        rank = 0
        for i, e in enumerate(enemies):
            rank += e.rank // (i+1)
        return rank

    @property
    def bosses(self):
        bosses = [e for e in self.enemies if e.is_boss]
        return bosses

    @property
    def enemies(self):
        enemies = bin(self.enemies_present | self.enemies_hidden)[2:]
        return self.get_enemy_list(enemies)

    def get_enemy_list(self, bitmask):
        bitmask = "{0:0>8}".format(bitmask)
        enemy_list = []
        for (i, c) in enumerate(bitmask):
            if c == "1":
                m = MonsterObject.get(getattr(self, "monster%s" % i))
                enemy_list.append(m)
        return enemy_list

    @property
    def leaders(self):
        if not hasattr(self, "_leaders"):
            for f in FormationObject.every:
                f._leaders = set([])
            for p in PackObject.every:
                common_enemies = set(p.common_enemies)
                for f in p.formations:
                    f._leaders |= common_enemies
            for f in FormationObject.every:
                if not f._leaders:
                    f._leaders = list(f.enemies)
                f._leaders = sorted(f._leaders, key=lambda m: m.index)
        return self._leaders

    @classproperty
    def valid_coordinates(cls):
        if hasattr(cls, "_valid_coordinates"):
            return cls._valid_coordinates

        cls._valid_coordinates = set([])
        for f in FormationObject.every:
            if not f.bosses:
                bitmask = f.enemies_present & (0xFF ^ f.enemies_hidden)
                for i in range(8):
                    if bitmask & (1 << (7-i)):
                        (x, y) = (getattr(f, "monster%s_x" % i),
                                  getattr(f, "monster%s_y" % i))
                    else:
                        continue
                    if (x, y) == (0, 0):
                        break
                    cls._valid_coordinates.add((x, y))
        cls._valid_coordinates = sorted(cls._valid_coordinates)
        xs, ys = list(zip(*cls._valid_coordinates))
        cls.lower_x, cls.upper_x = min(xs), max(xs)
        cls.lower_y, cls.upper_y = min(ys), max(ys)
        return cls.valid_coordinates

    @property
    def meta(self):
        return FormMetaObject.get(self.index)

    @property
    def has_event(self):
        if self.meta.event == 0xFF:
            return False
        else:
            return True

    @property
    def music(self):
        if self.meta.misc & 0xc0 == 0xc0:
            return None
        return (self.meta.misc >> 2) & 0x7

    @property
    def inescapable(self):
        return self.meta.misc & 3

    def set_music(self, value):
        if value is None:
            self.meta.misc &= 0xE3
            self.meta.misc |= 0xC0
        else:
            self.meta.misc &= 0xE3
            self.meta.misc |= (value << 2)

    def mutate(self):
        MAX_ENEMIES = 6
        if self.bosses or self.enemies_hidden or not self.enemies_present:
            return
        candidates = list(self.leaders)
        while len(candidates) < 3:
            base = random.choice(candidates)
            new = base.get_similar()
            if new not in candidates:
                candidates.append(new)
        assert len(set(candidates)) <= 3
        num_enemies = random.randint(1, random.randint(3, MAX_ENEMIES))
        num_enemies = max(num_enemies, len(self.leaders))
        chosen_enemies = list(self.leaders)
        while len(chosen_enemies) < num_enemies:
            vram_total = sum([e.vram_value for e in chosen_enemies])
            sub_candidates = candidates + chosen_enemies
            sub_candidates = [e for e in sub_candidates
                              if vram_total + e.vram_value <= 64]
            if not sub_candidates:
                num_enemies = len(chosen_enemies)
                break
            chosen_enemies.append(random.choice(sub_candidates))
        random.shuffle(chosen_enemies)

        def mutate_coordinate(xxx_todo_changeme):
            (x, y) = xxx_todo_changeme
            x = mutate_normal(x, minimum=self.lower_x, maximum=self.upper_x)
            y = mutate_normal(y, minimum=self.lower_y, maximum=self.upper_y)
            return (x, y)

        def get_distance(xxx_todo_changeme1, xxx_todo_changeme2):
            (x1, y1) = xxx_todo_changeme1
            (x2, y2) = xxx_todo_changeme2
            return ((x1-x2)**2 + (y1-y2)**2)**0.5

        def get_collective_distance(p, points):
            distances = [get_distance(p, p2) for p2 in points]
            return reduce(lambda a, b: a*b, distances, 1)

        def select_most_distance(candidates, done_coordinates):
            score = lambda p: get_collective_distance(p, done_coordinates)
            chosen = max(candidates, key=lambda c: score(c))
            return chosen

        self.enemies_present = 0
        done_coordinates = []
        for i in range(8):
            if i < len(chosen_enemies):
                e = chosen_enemies[i].index
                if not done_coordinates:
                    (x, y) = random.choice(self.valid_coordinates)
                    (x, y) = mutate_coordinate((x, y))
                else:
                    candidates = random.sample(self.valid_coordinates, len(chosen_enemies)*2)
                    candidates = list(map(mutate_coordinate, candidates))
                    (x, y) = select_most_distance(candidates, done_coordinates)
                done_coordinates.append((x, y))
                self.enemies_present |= (1 << (7-i))
            else:
                e = 0
            setattr(self, "monster%s" % i, e)
            setattr(self, "monster%s_x" % i, 0)
            setattr(self, "monster%s_y" % i, 0)
        done_coordinates = sorted(done_coordinates)
        for i, (x, y) in enumerate(done_coordinates):
            setattr(self, "monster%s_x" % i, x)
            setattr(self, "monster%s_y" % i, y)


class FormMetaObject(TableObject): pass


class CharacterObject(TableObject):
    flag = "c"
    flag_description = "character stats"

    mutate_attributes = {"speed": (1, 0xFF),
                         "level": (1, 30),
                         }
    intershuffle_attributes = ["speed"]

    @property
    def stats(self):
        if hasattr(self, "_stats"):
            return self._stats
        self._stats = [s for s in (StatGrowthObject.every +
                                   StatBonusObject.every)
                       if s.character_id == self.index]
        return self.stats

    @property
    def growth_stats(self):
        if hasattr(self, "_growth_stats"):
            return self._growth_stats
        self._growth_stats = [s for s in StatGrowthObject.every
                              if s.character_id == self.index]
        return self.growth_stats

    @property
    def bonus_stats(self):
        if hasattr(self, "_bonus_stats"):
            return self._bonus_stats
        self._bonus_stats = [s for s in StatBonusObject.every
                             if s.character_id == self.index]
        return self.bonus_stats

    def cleanup(self):
        self.current_hp = self.max_hp
        self.weapon = 0xFF
        self.armor = 0xFF
        self.accessory = 0xFF

        my_learned = [l for l in LearnObject.every if l.level <= self.level
                      and l.character_id == self.index]
        for l in my_learned:
            if l.spell <= 0x1A:
                self.known_spells |= (1 << l.spell)

        for g in self.growth_stats:
            if g.level > self.level:
                continue
            for attr in LEVEL_STATS:
                setattr(self, attr, getattr(self, attr) + getattr(g, attr))

        for s in self.bonus_stats:
            if s.level > self.level:
                continue
            attrs = s.best_choice
            for attr in attrs:
                setattr(self, attr, getattr(self, attr) + getattr(s, attr))

        # 255 maximum
        for attr in LEVEL_STATS:
            while self.get_max_stat_at_level(attr, 30) > 255:
                ss = [s for s in self.stats if self.level < s.level
                      and getattr(s, attr) > 0]
                s = random.choice(ss)
                value = getattr(s, attr)
                s.set_stat(attr, value-1)

        if self.level == 1:
            self.xp = 0
        else:
            self.xp = LevelUpXPObject.get(self.level-2).xp

        # If we're generating a debug seed for testing, max the starting stats.
        if self.debug_mode:
            for attr in LEVEL_STATS + ['speed']:
                if attr == 'max_hp':
                    setattr(self, attr, 999)
                else:
                    setattr(self, attr, 255)
            self.current_hp = self.max_hp

    def get_stat_at_level(self, attr, level):
        my_growths = [s for s in self.growth_stats
                      if self.level < s.level <= level]
        value = getattr(self, attr)
        for g in my_growths:
            value += getattr(g, attr)
        return value

    def get_max_stat_at_level(self, attr, level):
        value = self.get_stat_at_level(attr, level)
        my_bonuses = [s for s in self.bonus_stats
                      if self.level < s.level <= level]
        for b in my_bonuses:
            value += getattr(b, attr)
        return value


class ItemObject(TableObject):
    flag = "q"
    flag_description = "equipment stats and equippability"
    banned_indexes = set([
        0, 1, 2, 3, 4, 0x24, 0x47, 0x48, 0x49, 0x5f, 0x8b, 0x95, 0xa0, 0xa4,  # Dummy item slots
        0x85,  # Debug Bomb
        0x87,  # Bambino Bomb
        0xa5,  # S. Crow Bomb
        0xa7,  # Bane Bomb
        0xa8,  # Doom Bomb
        0xa9,  # Fear Bomb
        0xaa,  # Sleep Bomb (not SLEEPY)
        0xab,  # Mute Bomb
        0xad,  # Bomb (targets enemy)
    ] + list(range(0xb1, 0x100)))  # Unused slots

    ''' KNOWN FREEZES
    geno - 0xe super hammer (worked with mallow)
    mario - 0xf handgun
    mallow - 0xf handgun
    mario - 0x14 hurly gloves
    mario - 0x15 double punch (worked with mallow)
    geno - 0x1d super slap (worked with mario)
    geno - 0x7 noknok shell
    geno - 0x22 frying pan
    '''
    softlocks = {
        # Mario
        0: {
            0x0f,  # Handgun
            0x14,  # Hurly Gloves
            0x15,  # Double Punch
        },
        # Peach
        1: {},
        # Bowser
        2: {},
        # Geno
        3: {
            0x07,  # Noknok Shell
            0x0e,  # Super Hammer
            0x1d,  # Super Slep
            0x22,  # Frying Pan
        },
        # Mallow
        4: {
            0x0f,  # Handgun
        },
    }

    @classmethod
    def classify_rare(cls):
        for s in ShopObject.every:
            if s.uses_frog_coins:
                continue
            for i in s.items:
                item = ItemObject.get(i)
                item._rare = False
        for i in ItemObject.every:
            # if hasattr(i, "rare"):
            if hasattr(i, "_rare"):
                continue
            i._rare = True

    @property
    def rare(self):
        if hasattr(self, "_rare"):
            return self._rare
        ItemObject.classify_rare()
        return self.rare

    @property
    def rank(self):
        if hasattr(self, "_rank"):
            return self._rank
        price = PriceObject.get(self.index).price
        if self.banned:
            self._rank = -1
        elif price == 0 and not self.is_key:
            self._rank = random.randint(1, random.randint(1, 999))
        elif price == 0:
            self._rank = -1
        elif self.is_frog_coin_item:
            self._rank = price * 50
        elif price > 1000:
            self._rank = price / 2
        elif self.rare and self.is_consumable:
            rank = 2 * price
            if price <= 50:
                rank = rank * 50
            if self.reuseable:
                rank = rank * 4
            self._rank = rank
        elif self.rare and self.is_armor:
            self._rank = price * 3
        elif self.index == 0x5e:  # quartz charm
            self._rank = 999
        elif self.rare and self.is_accessory:
            self._rank = price * 2
        else:
            self._rank = price
        self._rank += (1 - (self.index / 1000.0))
        return self.rank

    @property
    def name(self):
        try:
            return ItemNameObject.get(self.index).name
        except KeyError:
            return "Item Name Unknown ({})".format(self.index)

    @property
    def price(self):
        return PriceObject.get(self.index).price

    @property
    def is_frog_coin_item(self):
        if hasattr(self, "_is_frog_coin_item"):
            return self._is_frog_coin_item
        for p in ShopObject.every:
            if self.index in p.items:
                self._is_frog_coin_item = p.uses_frog_coins
                break
        else:
            self._is_frog_coin_item = False
        return self.is_frog_coin_item

    def become_frog_coin_item(self):
        if self.is_frog_coin_item:
            return False
        factor = float(random.randint(random.randint(10, 50), 50))
        if self.rare:
            price = int(round(self.rank / factor))
        else:
            price = int(round(self.price / factor))
        PriceObject.get(self.index).price = min(max(price, 1), 50)
        self._is_frog_coin_item = True
        return True

    def unbecome_frog_coin_item(self):
        if not self.is_frog_coin_item:
            return False
        factor = float(random.randint(50, random.randint(50, 100)))
        price = int(round(self.price * factor))
        PriceObject.get(self.index).price = min(price, 1998)
        self._is_frog_coin_item = False
        return True

    @property
    def banned(self):
        return self.index in self.banned_indexes

    @property
    def is_weapon(self):
        return (self.variance and (self.useable_itemtype & 0x3) == 0
                and not self.banned)

    @property
    def is_armor(self):
        return (self.useable_itemtype & 0x3) == 1 and not self.banned

    @property
    def is_accessory(self):
        return (self.useable_itemtype & 0x3) == 2 and not self.banned

    @property
    def is_equipment(self):
        return self.is_weapon or self.is_armor or self.is_accessory

    @property
    def primary_stats(self):
        if self.is_weapon:
            return ["attack"]
        elif self.is_armor:
            return ["defense", "magic_defense"]
        return EQUIP_STATS

    @property
    def stat_point_value(self):
        score = 0
        for attr in EQUIP_STATS:
            value = getattr(self, attr)
            if value & 0x80:
                score += (value - 256)
            elif attr in self.primary_stats:
                score += value
            else:
                score += (2*value)
        return score

    @property
    def is_consumable(self):
        return self.useable_battle or self.useable_field

    @property
    def is_key(self):
        return not (self.is_equipment or self.is_consumable or self.banned)

    @property
    def useable_battle(self):
        return self.useable_itemtype & 0x08

    @property
    def useable_field(self):
        return self.useable_itemtype & 0x10

    @property
    def reuseable(self):
        return self.useable_itemtype & 0x20

    def mutate(self):
        if not self.is_equipment:
            return
        score = self.stat_point_value
        num_up = bin(random.randint(1, 31)).count('1')
        num_down = bin(random.randint(0, 31)).count('1')
        while True:
            if random.choice([True, False, False]):
                ups = [attr for attr in EQUIP_STATS
                       if 1 <= getattr(self, attr) <= 127]
                if ups:
                    break
            ups = random.sample(EQUIP_STATS, num_up)
            if set(ups) & set(self.primary_stats):
                break
        ups = dict([(u, 0) for u in ups])
        if random.choice([True, False, False]):
            downs = [attr for attr in EQUIP_STATS
                   if getattr(self, attr) >= 128]
        else:
            downs = random.sample(EQUIP_STATS, num_down)
        downs = dict([(d, 0) for d in downs if d not in ups])
        if downs:
            if score != 0:
                downpoints = random.randint(0, random.randint(0, score))
            else:
                downpoints = random.randint(0, random.randint(0, random.randint(0, 100)))
            while downpoints > 0:
                attr = random.choice(list(downs.keys()))
                downs[attr] += 1
                downpoints -= 1
                score += 1
        while score > 0:
            attr = random.choice(list(ups.keys()))
            ups[attr] += 1
            if attr in self.primary_stats:
                score -= 1
            else:
                score -= 2

        for attr in EQUIP_STATS:
            setattr(self, attr, 0)

        for attr in ups:
            setattr(self, attr, min(mutate_normal(
                ups[attr], minimum=1, maximum=127), 127))

        for attr in downs:
            value = min(mutate_normal(
                downs[attr], minimum=1, maximum=127), 127)
            if value:
                setattr(self, attr, 256 - value)

        if self.is_weapon and self.get_bit("geno"):
            assert self.equippable == 8
            return

        equippable = self.equippable & 0xE0
        num_equippable = random.randint(1,random.randint(1, 5))
        for _ in range(num_equippable):
            # If this weapon softlocks with the chosen character, re-roll until it doesn't.
            char = random.randint(0, 4)
            while self.index in self.softlocks[char]:
                char = random.randint(0, 4)
            equippable |= (1 << char)

        if self.is_weapon:
            equippable = equippable & 0xF7
            assert not equippable & 8
            if not equippable:
                return
        self.equippable = equippable

    def cleanup(self):
        if self.index == 5:
            # mario must equip tutorial hammer
            self.set_bit("mario", True)

        if self.index in [0xa5, 0xa7, 0xa9, 0xaa, 0xab]:
            self.set_bit("single_enemy", True)


class ItemNameObject(TableObject): pass
class PriceObject(TableObject): pass


class LevelUpXPObject(TableObject):
    flag = "c"

    @classmethod
    def full_randomize(cls):
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "randomized") and cls2.randomized):
                    raise Exception("Randomize order violated.")
        cls.randomized = True
        xps = sorted([mutate_normal(l.xp, minimum=1, maximum=9999)
                      for l in cls.every])
        prev = 0
        assert len(cls.every) == len(xps)
        for i, (l, xp) in enumerate(zip(cls.every, xps)):
            factor = min(i / (len(xps)/2.0), 1.0)
            xp = int(round((xp + (xp * factor))/2))
            if xp <= prev and xp < 9999:
                xp = prev + 1
            l.xp = xp
            prev = xp


class StatGrowthObject(StatObject, TableObject):
    flag = "c"

    @classmethod
    def full_randomize(cls):
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "randomized") and cls2.randomized):
                    raise Exception("Randomize order violated.")
        cls.randomized = True
        curves = defaultdict(list)
        for character_index in range(5):
            c = CharacterObject.get(character_index)
            for attr in LEVEL_STATS:
                value = getattr(c, attr)
                for l in cls.every:
                    if l.character_id == c.index and l.level <= 20:
                        value += getattr(l, attr)
                value = mutate_normal(value, maximum=255)
                fixed_points = [(1, 0), (20, value)]
                for _ in range(3):
                    dex = random.randint(1, len(fixed_points)-1)
                    lower_level, lower_value = fixed_points[dex-1]
                    upper_level, upper_value = fixed_points[dex]
                    if upper_level - lower_level < 4:
                        continue
                    level_interval = (upper_level - lower_level) // 2
                    value_interval = (upper_value - lower_value) // 2
                    level = (lower_level + random.randint(0, level_interval)
                             + random.randint(0, level_interval))
                    if level <= lower_level or level >= upper_level:
                        continue
                    value = (lower_value + random.randint(0, value_interval)
                             + random.randint(0, value_interval))
                    fixed_points.append((level, value))
                    fixed_points = sorted(fixed_points)

                for ((l1, v1), (l2, v2)) in zip(fixed_points, fixed_points[1:]):
                    ldist = l2 - l1
                    vdist = v2 - v1
                    for l in range(l1+1, l2):
                        factor = (l - l1) / float(ldist)
                        v = v1 + (factor * vdist)
                        fixed_points.append((l, int(round(v))))
                fixed_points = sorted(fixed_points)
                levels, values = list(zip(*fixed_points))
                assert len(fixed_points) == 20
                assert levels == tuple(sorted(levels))
                assert values == tuple(sorted(values))
                increases = []
                for v1, v2 in zip(values, values[1:]):
                    increases.append(v2-v1)

                frontload_factor = random.random() * random.random()
                if attr in ["defense", "magic_defense"]:
                    frontload_factor *= random.random()
                frontloaded = 0
                for n, inc in enumerate(increases):
                    max_index = len(increases) - 1
                    factor = (((max_index-n) / float(max_index))
                              * frontload_factor)
                    amount = int(round(inc * factor))
                    frontloaded += amount
                    increases[n] = (inc - amount)
                frontloaded = max(frontloaded, 1)

                while max(increases) > 15:
                    i = increases.index(max(increases))
                    increases[i] = increases[i] - 1
                    choices = [n for (n, v) in enumerate(increases) if v < 15]
                    if random.randint(0, len(choices)) == 0:
                        frontloaded += 1
                    elif choices:
                        i = random.choice(choices)
                        increases[i] = increases[i] + 1

                curves[attr].append((frontloaded, increases))

        for attr in LEVEL_STATS:
            attr_curves = curves[attr]
            random.shuffle(attr_curves)
            for character_index in range(5):
                (base, increases) = attr_curves.pop()
                c = CharacterObject.get(character_index)
                if c.index == 0 and attr in ["max_hp", "attack"]:
                    # ensure basic starting stats for Mario
                    while base < 20:
                        base += 1
                        for i in range(len(increases)):
                            if increases[i] > 0:
                                increases[i] = increases[i] - 1
                                break
                getattr(c, attr)
                setattr(c, attr, base)
                assert len(increases) == 19
                for s in StatGrowthObject.every:
                    if s.character_id == c.index:
                        if increases:
                            s.set_stat(attr, increases.pop(0))
                        else:
                            s.set_stat(attr, mutate_normal(2))


class StatBonusObject(StatObject, TableObject):
    flag = "c"
    intershuffle_attributes = ["max_hp", "physical", "magical"]

    @property
    def intershuffle_valid(self):
        return self.level <= 20

    @property
    def best_choice(self):
        options = [(self.max_hp/2, ("max_hp",)),
                   (self.attack + self.defense, ("attack", "defense")),
                   (self.magic_attack + self.magic_defense,
                    ("magic_attack", "magic_defense"))]
        a, b = max(options)
        options = [(c, d) for (c, d) in options if c == a]
        if len(options) > 1:
            options = [random.choice(options)]
        a, b = options[0]
        return b

    def mutate(self):
        valids = [s for s in StatBonusObject.every if s.intershuffle_valid and
                  all([getattr(s, attr)
                       for attr in self.intershuffle_attributes])]
        for attr in self.intershuffle_attributes:
            while getattr(self, attr) == 0:
                setattr(self, attr, getattr(random.choice(valids), attr))
        for attr in LEVEL_STATS:
            self.set_stat(attr, mutate_normal(
                getattr(self, attr), minimum=0, maximum=0xf))


class SpellObject(TableObject):
    flag = "s"
    flag_description = "character spell stats"
    mutate_attributes = {
            "fp": (1, 99),
            "power": None,
            "hitrate": (1, 100),
            }

    @property
    def name(self):
        try:
            return SpellNameObject.get(self.index).name
        except KeyError:
            return "Spell Name Unknown ({})".format(self.index)

    def set_name(self, name):
        SpellNameObject.get(self.index).name = name

    def mutate(self):
        # Geno Boost - shuffle only FP cost because of special effects of the spell
        if self.index == 0x11:
            self.mutate_attributes = {
                "fp": (1, 99),
            }

        super().mutate()


class SpellNameObject(TableObject): pass


class LearnObject(CharIndexObject, TableObject):
    flag = "z"
    flag_description = "character spell lists"

    @property
    def rank(self):
        return self.level

    @classmethod
    def full_randomize(cls):
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "randomized") and cls2.randomized):
                    raise Exception("Randomize order violated.")
        for c in CharacterObject.every:
            c.known_spells = 0
        spells = list(range(0x1b))
        spells.remove(7)  # group hug
        random.shuffle(spells)
        supplemental = [0xFF] * 3
        spells = spells + supplemental
        charspells = defaultdict(list)
        while spells:
            valid = [i for i in range(5) if len(charspells[i]) < 5 or (len(charspells[i]) < 6 and i != 1)]
            chosen = random.choice(valid)
            spell = spells.pop(0)
            if spell == 0xFF:
                valid = [s for s in range(0x1b) if s not in charspells[4] and s != 7]  # group hug
                spell = random.choice(valid)
            charspells[chosen].append(spell)
        charspells[1].insert(random.randint(0, 5), 7)
        for l in LearnObject.every:
            l.spell = 0xFF
        for i in range(5):
            charlevels = sorted(random.sample(list(range(2, 20)), 5))
            spells = charspells[i]
            c = CharacterObject.get(i)
            c.known_spells |= (1 << spells[0])
            for l, s in zip(charlevels, spells[1:]):
                l = LearnObject.get_by_character(i, l-2)
                l.spell = s
        cls.randomized = True


class WeaponTimingObject(TableObject): pass


class ShopObject(TableObject):
    flag = "p"
    flag_description = "shops"

    @classproperty
    def after_order(self):
        if 'q' in get_flags():
            return [ItemObject]
        return []

    @property
    def uses_frog_coins(self):
        return self.get_bit("frog_coins") or self.get_bit("frog_coins_limited")

    @property
    def rank(self):
        maxprice = max([PriceObject.get(i).price for i in self.items])
        if self.uses_frog_coins:
            maxprice += 2000
        return maxprice

    @property
    def is_juice_bar(self):
        return 0x9 <= self.index <= 0xC

    def __repr__(self):
        s = "%x " % self.index
        s += "FROG COINS\n" if self.uses_frog_coins else "COINS\n"
        for i in self.items:
            if i == 0xFF:
                continue
            i = ItemObject.get(i)
            s += "%s %s\n" % (i.name, i.price)
        return s.strip()

    @classmethod
    def full_randomize(cls):
        # fix debug bombs before this
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "randomized") and cls2.randomized):
                    raise Exception("Randomize order violated.")
        cls.randomized = True

        assignments = {}

        # phase 1: frog coin shops
        frog_candidates = [i for i in ItemObject.every if i.price and
            (i.rare or i.is_consumable or i.is_accessory) and not i.banned]
        frog_not_rare = [i for i in frog_candidates if not i.rare]
        unfrog = random.randint(
            random.randint(0, len(frog_not_rare)), len(frog_not_rare))
        unfrog = random.sample(frog_not_rare, unfrog)
        for i in sorted(unfrog, key=lambda i2: i2.index):
            frog_candidates.remove(i)
        frog_chosen = random.sample(frog_candidates, 25)
        disciple_shop = 3
        frog_coin_emporium = 6
        one_only = [i for i in frog_chosen if
            (i.is_equipment and bin(i.equippable).count("1") == 1) or
            (i.is_consumable and i.reuseable)]
        num_choose = min(10, len(one_only))
        num_choose = random.randint(random.randint(0, num_choose), num_choose)
        num_choose = min(num_choose, len(one_only))
        chosen = random.sample(one_only, num_choose)
        choose_again = [i for i in frog_chosen if i not in chosen and (
            i in one_only or i.is_equipment)]
        num_choose = 10 - len(chosen)
        num_choose = random.randint(random.randint(0, num_choose), num_choose)
        num_choose = min(num_choose, len(choose_again))
        if num_choose and choose_again:
            chosen += random.sample(choose_again, num_choose)
        num_choose = 10 - len(chosen)
        if num_choose:
            choose_again = [i for i in frog_chosen if i not in chosen]
            random.shuffle(choose_again)
            chosen += choose_again[:num_choose]
        assert len(chosen) == 10
        assignments[disciple_shop] = chosen
        assignments[frog_coin_emporium] = [
            i for i in frog_chosen if i not in chosen]

        # phase 2: non-frog coin shops
        carryover = [i for i in frog_candidates if
                     i not in assignments[disciple_shop] and
                     i not in assignments[frog_coin_emporium]]
        random.shuffle(carryover)
        num_choose = random.randint(0, random.randint(0, len(carryover)))
        carryover = carryover[:num_choose]
        shop_items = carryover + [i for i in ItemObject.every if
                i not in assignments[disciple_shop] and
                i not in assignments[frog_coin_emporium] and
                not i.banned and not i.rare]
        shop_items = sorted(set(shop_items), key=lambda i: i.rank)
        juice_bar_partial = [9, 10, 11]  # full: 12
        special_conditions = {
            0: lambda i: i.is_consumable or (
                i.is_equipment and i.equippable & 0b10001),
            1: lambda i: i.is_consumable,
            2: lambda i: i.is_equipment and i.equippable & 0b11001,
            4: lambda i: i.is_consumable or (
                i.is_equipment and i.equippable & 0b11001),
            8: lambda i: i.is_consumable and (
                (i.misc_attack not in [1, 2, 4, 5] and not
                    i.get_bit("status_nullification")) or i.get_bit("all")),
            12: lambda i: special_conditions[8](i) and not i.reuseable,
            13: lambda i: i.is_weapon,
            14: lambda i: i.is_armor,
            15: lambda i: i.is_accessory,
            16: lambda i: i.is_consumable,
            18: lambda i: i.is_consumable,
            19: lambda i: i.is_equipment,
            20: lambda i: special_conditions[8](i),
            24: lambda i: i.is_consumable,
            }
        done_already = set([])
        for p in range(25):
            if p in juice_bar_partial + [disciple_shop, frog_coin_emporium]:
                continue
            shop = ShopObject.get(p)
            if p == 12:
                num_items = 15
            else:
                num_items = len([i for i in shop.items if i != 0xFF])
                num_items = mutate_normal(num_items, minimum=1, maximum=15)
            valid_items = list(shop_items)
            if p in special_conditions:
                valid_items = [i for i in valid_items
                               if special_conditions[p](i)]
            temp = [i for i in valid_items if i not in done_already or
                    (i.is_consumable and not i.reuseable and not i.rare
                        and not i.get_bit("all")
                        and (i.misc_attack in [1, 2, 4] or
                             i.get_bit("status_nullification")))]
            if temp and p not in [12, 13, 14, 20]:
                valid_items = temp
                extras = [i for i in valid_items if i not in temp]
                extras = random.sample(extras,
                    random.randint(0, len(extras)))
                valid_items = sorted(set(valid_items + extras),
                                     key=lambda i: i.rank)
            assert valid_items
            num_items = min(num_items, len(valid_items))
            if p != 20 and len(valid_items) > num_items:
                valid_items = valid_items[:random.randint(
                    num_items, random.randint(num_items, len(valid_items)))]
                consumables = [i for i in valid_items if i.is_consumable]
                others = [i for i in valid_items if i not in consumables]
                if consumables and others and num_items >= 4:
                    num_con = (random.randint(0, num_items) +
                               random.randint(0, num_items)) // 2
                    num_con = max(num_con, num_items-num_con)
                    num_con = min(num_con, num_items-2)
                    num_oth = num_items-num_con
                    num_con = min(num_con, len(consumables))
                    num_oth = min(num_oth, len(others))
                    valid_items = (random.sample(consumables, num_con) +
                                   random.sample(others, num_oth))
                    num_items = num_con + num_oth
            chosen_items = random.sample(valid_items, num_items)
            assignments[p] = chosen_items
            for i in chosen_items:
                done_already.add(i)

        # phase 2.5: juice bar
        for n, p in enumerate(sorted(juice_bar_partial, reverse=True)):
            n = len(juice_bar_partial) - n
            previous_items = assignments[p+1]
            minimum = n
            maximum = len(previous_items)-1
            average = (minimum + maximum) // 2
            num_items = random.randint(
                random.randint(minimum, average), maximum)
            chosen_items = random.sample(previous_items, num_items)
            assignments[p] = chosen_items

        # phase 3: repricing
        repriced = set([])
        for p, items in list(assignments.items()):
            for item in items:
                if item in repriced:
                    continue
                if p in [disciple_shop, frog_coin_emporium]:
                    item.become_frog_coin_item()
                else:
                    if not item.unbecome_frog_coin_item() and item.rare:
                        PriceObject.get(item.index).price = max(
                            item.price, int(item.rank))
                price = min(999, max(2, item.price))
                price = mutate_normal(price, minimum=2, maximum=999)
                PriceObject.get(item.index).price = price
                repriced.add(item)
        for p, items in list(assignments.items()):
            final = [0xFF] * 15
            items = sorted(items, key=lambda i: ITEM_ORDER.index(i.index))
            final[:len(items)] = [i.index for i in items]
            ShopObject.get(p).items = final

        ShopObject.get(20).set_bit("discount50", True)


    def cleanup(self):
        frog_items = set([i.index for i in ItemObject.every
                          if i.is_frog_coin_item])
        for p in ShopObject.every:
            for i in p.items:
                if i == 0xFF:
                    continue
                i = ItemObject.get(i)
                assert 1 <= i.price <= 999
            if p.index in [3, 6]:
                continue
            assert not set(p.items) & frog_items


class FlowerBonusObject(TableObject):
    flag = "d"
    flag_description = "drops"

    def randomize(self):
        probability = random.randint(0, 5) + random.randint(0, 5)
        bonustype = random.randint(1, 5)
        self.bonus = (probability << 4) | bonustype


class WorldMapObject(TableObject):
    def unlock_everything(self):
        self.node_unlock &= 0xFC00
        self.node_unlock |= 0x100
        for direction in ["north", "east", "south", "west"]:
            attr = "%s_unlock" % direction
            value = getattr(self, attr)
            if value == 0xFF:
                continue
            value &= 0xC0
            value |= 1
            setattr(self, attr, value)


def randomize_for_web(seed, mode, debug_mode=False, randomize_character_stats=True, randomize_drops=True,
                      randomize_enemy_formations=True, randomize_monsters=True, randomize_shops=True,
                      randomize_equipment=True, randomize_spell_stats=True, randomize_spell_lists=True):
    """Randomizer for the web and return patch data.

    :return: Patch data for each region.
    :rtype: dict[list]
    """
    flags = []
    full = mode == 'full'
    if randomize_character_stats or full:
        flags.append('c')
    if randomize_drops or full:
        flags.append('d')
    if randomize_enemy_formations or full:
        flags.append('f')
    if randomize_monsters or full:
        flags.append('m')
    if randomize_shops or full:
        flags.append('p')
    if randomize_equipment or full:
        flags.append('q')
    if randomize_spell_stats or full:
        flags.append('s')
    if randomize_spell_lists or full:
        flags.append('z')

    flags = ''.join(flags)
    set_flags(flags)
    set_seed(seed)

    patches = {}

    for region, table_fname in (
            ('US', 'tables_list.txt'),
            ('JP', 'tables_list_jp.txt'),
    ):
        objects = [g for g in list(globals().values()) if
                   isinstance(g, type) and issubclass(g, TableObject) and g not in [TableObject]]

        # Set region for all classes and load master table.
        reset_everything()
        TableObject.region = region
        set_global_table_filename(table_fname)
        set_table_specs()

        objects = sort_good_order(objects)
        for o in objects:
            o.debug_mode = debug_mode
            e = o.every

        for o in objects:
            if not hasattr(o, "flag") or o.flag in flags:
                random.seed(seed)
                o.full_randomize()

        patches[region] = clean_and_write(objects, seed, verbose=False)

    # Randomize file select the same for both regions.
    file_select_char = random.choice([7, 13, 19, 25])

    for region, char_addrs, text_addr in (
            ('US', [0x34757, 0x3489a, 0x34ee7, 0x340aa, 0x3501e], 0x3ef140),
            ('JP', [0x347d7, 0x3490d, 0x34f59, 0x340fa, 0x35099], 0x3ef109),
    ):
        for addr, value in zip(char_addrs, [0, 1, 0, 0, 1]):
            patches[region].append({addr: file_select_char + value})

        # Add seed display on filename entry.
        patches[region].append({text_addr: list(str(seed).center(10).encode())})

        # Update ROM title.
        title = 'SMRPG-R {}'.format(seed).ljust(20)
        if len(title) > 20:
            title = title[:19] + '?'

        patches[region].append({0x7FC0: list(title.encode())})
        patches[region].append({0X7FDB: list(bytes([VERSION]))})

    return patches
