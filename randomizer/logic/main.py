# Main randomizer logic module that the front end calls.

import random

from . import characters
from . import data
from . import enemies
from . import items
from . import map
from . import spells
from . import utils
from .patch import Patch

# Current version number
VERSION = '7.0'

# Possible names we can use for the hash values on the file select screen.  Needs to be 6 characters or less.
FILE_ENTRY_NAMES = (
    'MARIO',
    'MALLOW',
    'GENO',
    'BOWSER',
    'PEACH',
)
# Also use enemy names, if they're 6 characters or less.
FILE_ENTRY_NAMES += tuple(e[2].upper() for e in data.ENEMY_DATA if 1 <= len(e[2]) <= 6)
FILE_ENTRY_NAMES = tuple(sorted(set(FILE_ENTRY_NAMES)))


class Settings:
    def __init__(self, mode='full', debug_mode=False, randomize_character_stats=True, randomize_drops=True,
                 randomize_enemy_formations=True, randomize_monsters=True, randomize_shops=True,
                 randomize_equipment=True, randomize_spell_stats=True, randomize_spell_lists=True,
                 randomize_join_order=True):
        self._mode = mode
        self._debug_mode = debug_mode
        self._randomize_character_stats = randomize_character_stats
        self._randomize_drops = randomize_drops
        self._randomize_enemy_formations = randomize_enemy_formations
        self._randomize_monsters = randomize_monsters
        self._randomize_shops = randomize_shops
        self._randomize_equipment = randomize_equipment
        self._randomize_spell_stats = randomize_spell_stats
        self._randomize_spell_lists = randomize_spell_lists
        self._randomize_join_order = randomize_join_order

    def custom_flags_to_json(self):
        """Return JSON serialization of custom flags.

        :rtype: list[bool]
        """
        return [
            self.randomize_character_stats,
            self.randomize_drops,
            self.randomize_enemy_formations,
            self.randomize_monsters,
            self.randomize_shops,
            self.randomize_equipment,
            self.randomize_spell_stats,
            self.randomize_spell_lists,
            self.randomize_join_order,
        ]

    @property
    def mode(self):
        """:rtype: str"""
        return self._mode

    @property
    def debug_mode(self):
        """:rtype: bool"""
        return self._debug_mode

    @property
    def randomize_character_stats(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_character_stats

    @property
    def randomize_drops(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_drops

    @property
    def randomize_enemy_formations(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_enemy_formations

    @property
    def randomize_monsters(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_monsters

    @property
    def randomize_shops(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_shops

    @property
    def randomize_equipment(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_equipment

    @property
    def randomize_spell_stats(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_spell_stats

    @property
    def randomize_spell_lists(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_spell_lists

    @property
    def randomize_join_order(self):
        """:rtype: bool"""
        return self._mode == 'full' or self._randomize_join_order


class GameWorld:
    """Master container class representing the entire game world to be randomized.  This class doesn't do much on its
    own, but it holds all the data being randomized so the actual logic can look at and change different things across
    a single instance of the world.
    """

    def __init__(self, seed, settings):
        """
        :type seed: int
        :type settings: randomizer.logic.main.Settings
        """
        self.seed = seed
        self.settings = settings

        # *** Get vanilla data for randomizing.
        # Characters
        self.characters = [
            characters.Mario(),
            characters.Mallow(),
            characters.Geno(),
            characters.Bowser(),
            characters.Peach(),
        ]
        self.character_join_order = [self.characters[1], self.characters[2], self.characters[3], self.characters[4]]

        # Learned spells and level-up exp.
        self.learned_spells = characters.LearnedSpells()
        self.levelup_xps = characters.LevelUpExps()

        # Spells
        self.spells = []
        for args in data.VANILLA_SPELLS:
            self.spells.append(spells.Spell(*args))
        self.spells_dict = dict([(s.index, s) for s in self.spells])

        # Starting FP.
        self.starting_fp = spells.STARTING_FP

        # Items
        self.items = []
        for args in data.ITEM_DATA:
            self.items.append(items.Item(*args))
        self.items_dict = dict([(i.index, i) for i in self.items])

        # Shops
        self.shops = []
        for index, frog_coin_shop, item_indexes in data.SHOP_DATA:
            shop_items = [self.items_dict[i] for i in item_indexes if i in self.items_dict]
            self.shops.append(items.Shop(index, frog_coin_shop, shop_items))

        # Enemies
        self.enemies = []
        for args in data.ENEMY_DATA:
            self.enemies.append(enemies.Enemy(*args))
        self.enemies_dict = dict([(e.index, e) for e in self.enemies])

        # Get enemy attack data.
        self.enemy_attacks = []
        for args in data.ENEMY_ATTACK_DATA:
            self.enemy_attacks.append(enemies.EnemyAttack(*args))

        # Get enemy reward data.
        self.enemy_rewards = []
        for index, address, xp, coins, yoshi_cookie_item, normal_item, rare_item in data.ENEMY_REWARD_DATA:
            yitem = self.items_dict[yoshi_cookie_item] if yoshi_cookie_item != 0xff else None
            nitem = self.items_dict[normal_item] if normal_item != 0xff else None
            ritem = self.items_dict[rare_item] if rare_item != 0xff else None
            self.enemy_rewards.append(enemies.EnemyReward(index, address, xp, coins, yitem, nitem, ritem))

        # Get enemy formation data.
        self.enemy_formations = []
        for index, event_at_start, misc_flags, formation_enemies in data.ENEMY_FORMATION_DATA:
            members = []
            for member_index, hidden_at_start, enemy_index, x_pos, y_pos in formation_enemies:
                members.append(enemies.FormationMember(member_index, hidden_at_start, self.enemies_dict[enemy_index],
                                                       x_pos, y_pos))
            self.enemy_formations.append(enemies.EnemyFormation(index, event_at_start, misc_flags, members))
        self.enemy_formations_dict = dict((f.index, f) for f in self.enemy_formations)

        # Get enemy encounter pack data.
        self.formation_packs = []
        for index, formations in data.ENEMY_PACK_DATA:
            self.formation_packs.append(
                enemies.FormationPack(index, [self.enemy_formations_dict[i] for i in formations]))
        self.formation_packs_dict = dict((p.index, p) for p in self.formation_packs)

        # Get leaders for each formation based on common enemies in packs.
        for p in self.formation_packs:
            common_enemies = set(p.common_enemies)
            for f in p.formations:
                f.leaders |= common_enemies

        for f in self.enemy_formations:
            if not f.leaders:
                f.leaders = [m.enemy for m in f.members]
            f.leaders = sorted(f.leaders, key=lambda m: m.index)

    def get_item_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.logic.items.Item
        """
        return self.items_dict[index]

    def get_enemy_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.logic.enemies.Enemy
        """
        return self.enemies_dict[index]

    def get_enemy_formation_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.logic.enemies.EnemyFormation
        """
        return self.enemy_formations_dict[index]

    def get_formation_pack_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.logic.enemies.FormationPack
        """
        return self.formation_packs_dict[index]

    def randomize(self):
        """Randomize this entire game world instance."""
        # Seed the PRNG at the start.
        random.seed(self.seed)

        characters.randomize_characters(self)
        spells.randomize_spells(self)
        items.randomize_items(self)
        enemies.randomize_enemies(self)

    def build_patch(self):
        """Build patch data for this instance.

        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # Characters
        for character in self.characters:
            patch += character.get_patch()

        # Update party join script events for the final order.
        addresses = [0x1e2155, 0x1fc506, 0x1edf98, 0x1e8b79]
        for addr, character in zip(addresses, self.character_join_order):
            patch.add_data(addr, 0x80 + character.index)

        # Update other battle scripts so Belome eats the first one to join.
        for addr in (
                0x394b4d,
                0x394b70,
                0x394b74,
                0x394b7d,
                0x394b7f,
                0x394b83,
                0x3ab93f,
                0x3ab95a,
        ):
            patch.add_data(addr, self.character_join_order[0].index)

        # Learned spells and level-up exp.
        patch += self.learned_spells.get_patch()
        patch += self.levelup_xps.get_patch()

        # Spells
        for spell in self.spells:
            patch += spell.get_patch()

        # Starting FP (twice for starting/max FP)
        patch.add_data(0x3a00dd, utils.ByteField(self.starting_fp).as_bytes() * 2)

        # For debug mode, start with 999 coins.
        if self.settings.debug_mode:
            patch.add_data(0x3a00db, utils.ByteField(999, num_bytes=2).as_bytes())

        # Items
        for item in self.items:
            patch += item.get_patch()

        # Shops
        for shop in self.shops:
            patch += shop.get_patch()

        # Enemies
        for enemy in self.enemies:
            patch += enemy.get_patch()

        # Enemy attacks
        for attack in self.enemy_attacks:
            patch += attack.get_patch()

        # Enemy rewards
        for reward in self.enemy_rewards:
            patch += reward.get_patch()

        # Enemy formations
        for formation in self.enemy_formations:
            patch += formation.get_patch()

        # Unlock the whole map if in debug mode.
        if self.settings.debug_mode:
            patch += map.unlock_world_map()

        # Build final PRNG seed value specifically for randomizing file select character and hash.
        # Use the same version, seed, mode, and flags used for the database hash.
        final_seed = bytearray()
        final_seed += VERSION.encode('utf-8')
        final_seed += self.seed.to_bytes(4, 'big')
        final_seed += self.settings.mode.encode('utf-8')
        if self.settings.mode == 'custom':
            for flag in self.settings.custom_flags_to_json():
                final_seed += str(flag).encode('utf-8')
        random.seed(final_seed)

        # Randomize character for the file select screen.
        file_select_char = random.choice([0, 7, 13, 19, 25])

        # Change file select character graphic, if not Mario.
        if file_select_char > 0:
            addresses = [0x34757, 0x3489a, 0x34ee7, 0x340aa, 0x3501e]

            for addr, value in zip(addresses, [0, 1, 0, 0, 1]):
                patch.add_data(addr, file_select_char + value)

        # Add seed display on filename entry.
        patch.add_data(0x3ef140, str(self.seed).center(10))

        # Replace file select names with random "hash" values for seed verification.
        file_select_names = random.choices(FILE_ENTRY_NAMES, k=4)
        for i, name in enumerate(file_select_names):
            addr = 0x3ef528 + (i * 7)
            val = name.encode().ljust(7, b'\x00')
            patch.add_data(addr, val)

        # Update ROM title and version.
        title = 'SMRPG-R {}'.format(self.seed).ljust(20)
        if len(title) > 20:
            title = title[:19] + '?'

        # Add title and major version number to SNES header data.
        patch.add_data(0x7fc0, title)
        v = VERSION.split('.')
        patch.add_data(0x7fdb, int(v[0]))

        return patch
