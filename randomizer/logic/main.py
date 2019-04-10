# Main randomizer logic module that the front end calls.

import collections
import hashlib
import random
import re
import inspect

from randomizer import data
from . import bosses
from . import characters
from . import chests
from . import enemies
from . import flags
from . import games
from . import items
from . import keys
from . import map
from . import spells
from . import utils
from .patch import Patch

# Current version number
VERSION = '8.0beta17'


class Settings:
    def __init__(self, mode, debug_mode=False, flag_string=''):
        """Provide either form data fields or flag string to set flags on creation.

        Args:
            mode (str): Should be standard or open.
            debug_mode (bool): Debug flag.
            flag_string (str): Flag string if parsing flags from string.
        """
        self._mode = mode
        self._debug_mode = debug_mode
        self._enabled_flags = set()

        # If flag string provided, make fake form data based on it to parse.
        flag_data = {}
        for flag in flag_string.strip().split():
            if flag.startswith('-'):
                # Solo flag that begins with a dash.
                flag_data[flag] = True
            elif flag:
                # Flag that may have a subsection of choices and/or options.
                if flag[0] not in flag_data:
                    flag_data[flag[0]] = []
                flag_data[flag[0]] += [c for c in flag[1:]]

        # Get flags from form data.
        for category in flags.CATEGORIES:
            for flag in category.flags:
                self._check_flag_from_form_data(flag, flag_data)

        # Sanity check.
        if debug_mode:
            provided_parts = set(flag_string.strip().split())
            parsed_parts = set(self.flag_string.split())
            if provided_parts != parsed_parts:
                raise ValueError("Generated flags {!r} don't match provided {!r} - difference: {!r}".format(
                    parsed_parts, provided_parts, provided_parts - parsed_parts))

    def _check_flag_from_form_data(self, flag, flag_data):
        """

        Args:
            flag (randomizer.logic.flags.Flag): Flag to check if enabled.
            flag_data (dict): Form data dictionary.

        """
        if flag.available_in_mode(self.mode):
            if flag.value.startswith('-'):
                # Solo flag that begins with a dash.
                if flag_data.get(flag.value):
                    self._enabled_flags.add(flag)
            else:
                # Flag that may be on its own with choices and/or suboptions.
                if flag.value.startswith('@'):
                    if flag.value[1] in flag_data:
                        self._enabled_flags.add(flag)
                else:
                    char = flag.value[0]
                    rest = flag.value[1:]

                    # Single character flag, just check if it's enabled.  Otherwise, make sure the small char is there.
                    if rest:
                        if rest in flag_data.get(char, []):
                            self._enabled_flags.add(flag)
                    elif char in flag_data:
                        self._enabled_flags.add(flag)

            # If flag was enabled, check choices/options recursively.
            if self.is_flag_enabled(flag):
                for choice in flag.choices:
                    self._check_flag_from_form_data(choice, flag_data)
                for option in flag.options:
                    self._check_flag_from_form_data(option, flag_data)

    @property
    def mode(self):
        """:rtype: str"""
        return self._mode

    @property
    def debug_mode(self):
        """:rtype: bool"""
        return self._debug_mode

    def _build_flag_string_part(self, flag, flag_strings):
        """

        Args:
            flag (randomizer.logic.flags.Flag): Flag to process.
            flag_strings (dict): Dictionary for flag strings.

        Returns:
            str: Flag string piece for this flag.

        """
        if self.is_flag_enabled(flag):
            # Solo flag that begins with a dash.
            if flag.value.startswith('-'):
                flag_strings[flag.value] = True
            # Flag that may have a subsection of choices and/or options.
            else:
                rest = ''
                if flag.value.startswith('@'):
                    char = flag.value[1]
                    flag_strings['@'].append(char)
                else:
                    char = flag.value[0]
                    rest = flag.value[1:]

                # Check if this key is in the map yet.
                if char not in flag_strings:
                    flag_strings[char] = []
                if rest:
                    flag_strings[char].append(rest)

                for choice in flag.choices:
                    self._build_flag_string_part(choice, flag_strings)

                for option in flag.options:
                    self._build_flag_string_part(option, flag_strings)

    @property
    def flag_string(self):
        """
        Returns:
            str: Computed flag string for these settings.
        """
        flag_strings = collections.OrderedDict()
        flag_strings['@'] = []

        for category in flags.CATEGORIES:
            for flag in category.flags:
                self._build_flag_string_part(flag, flag_strings)

        flag_string = ''
        for key, vals in flag_strings.items():
            if key != '@':
                if key.startswith('-'):
                    flag_string += key + ' '
                elif vals or key not in flag_strings['@']:
                    flag_string += key + ''.join(vals) + ' '

        return flag_string.strip()

    def is_flag_enabled(self, flag):
        """
        Args:
            flag: Flag class to check.

        Returns:
            bool: True if flag is enabled, False otherwise.
        """
        return flag in self._enabled_flags

    def get_flag_choice(self, flag):
        """
        Args:
            flag: Flag class to get choice for.

        Returns:
            randomizer.logic.flags.Flag: Selected choice for this flag.
        """
        for choice in flag.choices:
            if self.is_flag_enabled(choice):
                return choice
        return None


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
        self.file_select_character = 'Mario'
        self.file_select_hash = 'MARIO1 / MARIO2 / MARIO3 / MARIO4'
        self._rebuild_hash()

        # *** Get vanilla data for randomizing.
        # Characters
        self.characters = data.characters.get_default_characters(self)
        self.character_join_order = self.characters[:]
        self.levelup_xps = data.characters.LevelUpExps()

        # Spells
        self.spells = data.spells.get_default_spells(self)
        self.spells_dict = dict([(s.index, s) for s in self.spells])

        # Starting FP.
        self.starting_fp = data.spells.STARTING_FP

        # Items
        self.items = data.items.get_default_items(self)
        self.items_dict = dict([(i.index, i) for i in self.items])

        # Shops
        self.shops = data.items.get_default_shops(self)

        # Enemies
        self.enemies = data.enemies.get_default_enemies(self)
        self.enemies_dict = dict([(e.index, e) for e in self.enemies])

        # Get enemy attack data.
        self.enemy_attacks = data.attacks.get_default_enemy_attacks(self)

        # Get enemy formation data.
        self.enemy_formations, self.formation_packs = data.formations.get_default_enemy_formations(self)
        self.enemy_formations_dict = dict((f.index, f) for f in self.enemy_formations)
        self.formation_packs_dict = dict((p.index, p) for p in self.formation_packs)

        # Get item location data.
        self.key_locations = data.keys.get_default_key_item_locations(self)
        self.chest_locations = data.chests.get_default_chests(self)

        # Get boss location data.
        self.boss_locations = data.bosses.get_default_boss_locations(self)

        # Minigame data.
        self.ball_solitaire = data.games.BallSolitaireGame(self)
        self.magic_buttons = data.games.MagicButtonsGame(self)

    @property
    def open_mode(self):
        """Check if this game world is Open mode.

        Returns:
            bool:

        """
        return self.settings.mode == 'open'

    @property
    def debug_mode(self):
        """Get debug mode flag.

        Returns:
            bool:

        """
        return self.settings.debug_mode

    def get_item_instance(self, cls):
        """
        Args:
            cls: Item class to get this world's instance of.

        Returns:
            randomizer.data.items.Item: Item instance for this world.
        """
        return self.items_dict[cls.index]

    def get_enemy_instance(self, cls):
        """
        Args:
            cls: Enemy class to get this world's instance of.

        Returns:
            randomizer.data.enemies.Enemy: Enemy instance for this world.
        """
        return self.enemies_dict[cls.index]

    def get_enemy_formation_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.data.formations.EnemyFormation
        """
        return self.enemy_formations_dict[index]

    def get_formation_pack_by_index(self, index):
        """
        :type index: int
        :rtype: randomizer.data.formations.FormationPack
        """
        return self.formation_packs_dict[index]

    def randomize(self):
        """Randomize this entire game world instance."""
        # Seed the PRNG at the start.
        random.seed(self.seed)

        characters.randomize_all(self)
        spells.randomize_all(self)
        items.randomize_all(self)
        enemies.randomize_all(self)
        bosses.randomize_all(self)
        keys.randomize_all(self)
        chests.randomize_all(self)
        games.randomize_all(self)

        # Rebuild hash after randomization.
        self._rebuild_hash()

    def _rebuild_hash(self):
        """Build hash value for choosing file select character and file name hash.
        Use the same version, seed, mode, and flags used for the database hash.
        """
        final_seed = bytearray()
        final_seed += VERSION.encode('utf-8')
        final_seed += self.seed.to_bytes(4, 'big')
        final_seed += self.settings.mode.encode('utf-8')
        final_seed += self.settings.flag_string.encode('utf-8')
        self.hash = hashlib.md5(final_seed).hexdigest()

    def build_patch(self):
        """Build patch data for this instance.

        :rtype: randomizer.logic.patch.Patch
        """
        patch = Patch()

        # Characters
        for character in self.characters:
            patch += character.get_patch()

        # Update party join script events for the final order.  These are different for standard vs open mode.
        if self.open_mode:
            addresses = [0x1ef86d, 0x1ef86f, 0x1ef871, 0x1fc4f2, 0x1e8b72]
            for addr, character in zip(addresses, self.character_join_order):
                patch.add_data(addr, 0x80 + character.index)
        else:
            # For standard mode, Mario is the first character.  Update the other four only.
            addresses = [0x1e2155, 0x1fc506, 0x1edf98, 0x1e8b79]
            for addr, character in zip(addresses, self.character_join_order[1:]):
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
                patch.add_data(addr, self.character_join_order[1].index)

        # Learned spells and level-up exp.
        patch += self.levelup_xps.get_patch()

        # Spells
        for spell in self.spells:
            patch += spell.get_patch()

        # Starting FP (twice for starting/max FP)
        patch.add_data(0x3a00dd, utils.ByteField(self.starting_fp).as_bytes() * 2)

        # For debug mode, start with 9999 coins and 99 frog coins.
        if self.debug_mode or self.settings.is_flag_enabled(flags.FreeShops):
            patch.add_data(0x3a00db, utils.ByteField(9999, num_bytes=2).as_bytes())
            patch.add_data(0x3a00df, utils.ByteField(99, num_bytes=2).as_bytes())

        # No Mack Skip flag
        if self.settings.is_flag_enabled(flags.NoMackSkip):
            patch.add_data(0x14ca6c, bytes([0xA5]))

        # Items
        for item in self.items:
            patch += item.get_patch()
        patch += data.items.Item.build_descriptions_patch(self)

        # Shops
        for shop in self.shops:
            patch += shop.get_patch()

        # Enemies
        for enemy in self.enemies:
            patch += enemy.get_patch()
        patch += data.enemies.Enemy.build_psychopath_patch(self)

        # Enemy attacks
        for attack in self.enemy_attacks:
            patch += attack.get_patch()

        # Enemy formations
        for formation in self.enemy_formations:
            patch += formation.get_patch()

        # Open mode specific data.
        if self.open_mode:
            # Item locations.
            # FIXME
            # for location in self.key_locations + self.chest_locations:
            #     print(">>>>>>>> {}".format(location))

            for location in self.key_locations:
                patch += location.get_patch()

            for location in self.chest_locations:
                patch += location.get_patch()

            # Boss locations.
            for boss in self.boss_locations:
                # FIXME
                # print(">>>>>>>>>>>>>>>> {}".format(boss))
                patch += boss.get_patch()

            # Set flags for seven star mode and Bowser's Keep.
            if self.settings.is_flag_enabled(flags.SevenStarHunt):
                patch.add_data(0x1fd341, utils.ByteField(0xa2).as_bytes())

            if self.settings.is_flag_enabled(flags.BowsersKeepOpen):
                patch.add_data(0x1fd343, utils.ByteField(0xa2).as_bytes())

            # If star piece exp progression is on, set exp values for each star piece number and enable flag.
            choice = self.settings.get_flag_choice(flags.StarExpChallenge)
            if choice:
                if choice is flags.StarExp1:
                    exps = (2, 4, 5, 6, 8, 9, 11)
                elif choice is flags.StarExp2:
                    exps = (1, 2, 3, 5, 6, 7, 11)
                else:
                    raise ValueError("Got unrecognized value for star exp challenge: {!r}".format(choice))

                patch.add_data(0x39bc44, utils.ByteField(exps[0]).as_bytes())  # 0 stars
                patch.add_data(0x39bc46, utils.ByteField(exps[1]).as_bytes())  # 1 star
                patch.add_data(0x39bc48, utils.ByteField(exps[2]).as_bytes())  # 2 stars
                patch.add_data(0x39bc4a, utils.ByteField(exps[3]).as_bytes())  # 3 stars
                patch.add_data(0x39bc4c, utils.ByteField(exps[4]).as_bytes())  # 4 stars
                patch.add_data(0x39bc4e, utils.ByteField(exps[5]).as_bytes())  # 5 stars
                patch.add_data(0x39bc52, utils.ByteField(exps[6]).as_bytes())  # 6/7 stars
                patch.add_data(0x1fd32d, utils.ByteField(0xa0).as_bytes())  # Enable flag

            # Minigames
            patch += self.ball_solitaire.get_patch()
            patch += self.magic_buttons.get_patch()

        # Unlock the whole map if in debug mode in standard.
        if self.debug_mode and not self.open_mode:
            patch += map.unlock_world_map()

        # bowsers keep doors
        if self.settings.is_flag_enabled(flags.ShuffleBowsersKeep):

            # def find_subclasses(module, clazz):
            #     return [
            #         cls
            #         for name, cls in inspect.getmembers(module)
            #         if inspect.isclass(cls) and issubclass(cls, clazz) and cls != clazz
            #     ]
            # all_rooms = find_subclasses(data.locations, data.locations.BowserRoom)
            # shuffleable_rooms = [i for i in all_rooms if not i.is_final]
            # last_rooms = [i for i in all_rooms if i.is_final]
            #
            # rooms = random.sample(shuffleable_rooms, 3)
            # rooms.append(random.choice(last_rooms))
            # #print(rooms)
            #
            # #set croco's room to lead to the first randomized room
            # patch.add_data(0x1D46AE, [rooms[0].relative_room_id])
            # patch.add_data(0x1D46B3, [rooms[0].start_x, rooms[0].start_y, rooms[0].start_z + 0xE0])
            #
            # #next rooms
            # for index, room in enumerate(rooms):
            #     if index+1 < len(rooms):
            #         patch.add_data(rooms[index].next_room_address, [rooms[index+1].relative_room_id])
            #         patch.add_data(rooms[index].next_coord_address, [rooms[index+1].start_x, rooms[index+1].start_y, rooms[index+1].start_z + 0xE0])
            # #make final room always go to final chest
            # #todo: really need a way to make any room avaiable in any slot
            # patch.add_data(0x204CB1, [0xBE, 0x81, 0x10])
            #
            # #remove backward exits
            # for i in rooms:
            #     if i.backward_exit_byte > 0:
            #         patch.add_data(i.backward_exit_byte, 15)
            #     if i.backward_event_byte > 0:
            #         patch.add_data(i.backward_event_byte, 15)
            #
            # #death spawn in croco room
            # patch.add_data(0x2050D8, [0xC4])
            # patch.add_data(0x2050DA, [0x09, 0x5D])
            #
            # #exclude any chests in unused bowser door rooms from world.chest_locations
            # for i in all_rooms:
            #     if i not in rooms:
            #         if i == data.locations.BowserDoorInvisible:
            #             for c in self.chest_locations:
            #                 if (i == data.locations.BowserDoorInvisible and (isinstance(c, data.chests.BowsersKeepInvisibleBridge1) or isinstance(c, data.chests.BowsersKeepInvisibleBridge2) or isinstance(c, data.chests.BowsersKeepInvisibleBridge3) or isinstance(c, data.chests.BowsersKeepInvisibleBridge4))) or (i == data.locations.BowserDoorXY and (isinstance(c, data.chests.BowsersKeepMovingPlatforms1) or isinstance(c, data.chests.BowsersKeepMovingPlatforms2) or isinstance(c, data.chests.BowsersKeepMovingPlatforms3) or isinstance(c, data.chests.BowsersKeepMovingPlatforms4))) or (i == data.locations.BowserDoorZ and isinstance(c, data.chests.BowsersKeepElevatorPlatforms)) or (i == data.locations.BowserDoorCannonball and (isinstance(c, data.chests.BowsersKeepCannonballRoom1) or isinstance(c, data.chests.BowsersKeepCannonballRoom2) or isinstance(c, data.chests.BowsersKeepCannonballRoom3) or isinstance(c, data.chests.BowsersKeepCannonballRoom4) or isinstance(c, data.chests.BowsersKeepCannonballRoom5))) or (i == data.locations.BowserDoorRotating and (isinstance(c, data.chests.BowsersKeepRotatingPlatforms1) or isinstance(c, data.chests.BowsersKeepRotatingPlatforms2) or isinstance(c, data.chests.BowsersKeepRotatingPlatforms3) or isinstance(c, data.chests.BowsersKeepRotatingPlatforms4) or isinstance(c, data.chests.BowsersKeepRotatingPlatforms5) or isinstance(c, data.chests.BowsersKeepRotatingPlatforms6))):
            #                     self.chest_locations.remove(c)
            # #need to update this to include prize chests once we figure that out
            #


            def find_subclasses(module, clazz):
                return [
                    cls
                    for name, cls in inspect.getmembers(module)
                    if inspect.isclass(cls) and issubclass(cls, clazz) and cls != clazz
                ]

            all_rooms = find_subclasses(data.locations, data.locations.BowserRoom)
            doors = [[], [], [], [], [], []]
            assigned_rooms = []

            #remove backward exits
            for i in all_rooms:
                if i.backward_exit_byte > 0:
                    patch.add_data(i.backward_exit_byte, 15)
                if i.backward_event_byte > 0:
                    patch.add_data(i.backward_event_byte, 15)
                if i.is_final:
                    patch.add_data(i.change_event_byte, [0x4C, 0x81])

            for i in range(0, len(doors)):
                for j in range(0,3):
                    room = random.choice([r for r in all_rooms if r not in assigned_rooms])
                    doors[i].append(room)
                    assigned_rooms.append(room)

            #exits and event exits need to go to room 240, patch room 240 to run event 332 on load and bowsers keep music
            patch.add_data(0x1D40D5, [0xF0, 0xA0, 0x93, 0x1C, 0x05, 0x02, 0x39, 0xE0, 0x81, 0xF0, 0xA0])
            patch.add_data(0x1D4307, [0xF0, 0xA0])
            patch.add_data(0x1D46E4, [0xF0, 0xA0, 0x92, 0x1B, 0x03, 0x06, 0x2F, 0xE1, 0x81, 0x42, 0xA1, 0x87, 0x76, 0x02, 0x1A, 0x58, 0x62, 0x81, 0xF0, 0xA0, 0x95, 0x56, 0x02, 0x16, 0x7B, 0xE0, 0x81, 0xF0, 0xA0, 0x96, 0x19, 0x00, 0x02, 0x3F, 0xE0, 0x81, 0xF0, 0xA0, 0x96, 0x19, 0x00, 0x02, 0x3F, 0xE0, 0x81, 0xF0, 0xA0])
            patch.add_data(0x204E8D, [0xF0, 0x80, 0x02, 0x37, 0xE0, 0xFE, 0x68, 0xF0, 0x80])
            patch.add_data(0x20502A, [0xF0, 0x80])
            patch.add_data(0x205285, [0xF0, 0x80])
            patch.add_data(0x20F217, [0x42, 0x4C, 0x01])
            #battle rooms should load BK2 music
            patch.add_data(0x20F6CD, [0x42])
            patch.add_data(0x20F6E8, [0x42])
            patch.add_data(0x20FB8D, [0x42])
            patch.add_data(0x20FBA8, [0x42])
            patch.add_data(0x20FBC3, [0x42])
            patch.add_data(0x20FBE4, [0x42])
            #patch final rooms so that they always run event 332 on exit
            patch.add_data(0x20F703, [0x4C, 0x81])
            patch.add_data(0x20FB6C, [0x4C, 0x81])
            patch.add_data(0x20FB75, [0x4C, 0x81])
            patch.add_data(0x20FBDE, [0x4C, 0x81])
            patch.add_data(0x20FC11, [0x4C, 0x81])
            patch.add_data(0x20FC1D, [0x4C, 0x81])

            # create a patch that modifies event 322 to be usable for keep reward chest rooms and rooms with hard exits
            # modify event 332 for room logic
            # patch 3350 to 332
            # event_patch_data = [0xE4, 0x2D, 0x00, 0x00, 0x00, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x11, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x1F, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x30, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x41, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x56, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x67, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x78, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x89, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x9A, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0xAB, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0xBC, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0xCD, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0xDE, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0xEF, 0x23, 0xE4, 0x2D, 0x00, 0x00, 0x00, 0x24, 0xE4, 0x2D, 0x00, 0x00, 0x11, 0x24, 0xE4, 0x2D, 0x00, 0x00, 0x22, 0x24, 0xD2, 0x33, 0x24, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xD0, 0x01, 0x03, 0x6A, 0xE0, 0x71, 0xD0, 0x0F, 0x00, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCF, 0x81, 0x02, 0x37, 0xE0, 0x71, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xD2, 0x01, 0x0C, 0x61, 0xE0, 0x71, 0xD0, 0x24, 0x0D, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xD3, 0x01, 0x16, 0x53, 0xE0, 0x71, 0xD0, 0x0F, 0x00, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xB0, 0x1F, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xD1, 0x01, 0x16, 0x21, 0xE0, 0x71, 0xD0, 0x1E, 0x0D, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xD4, 0x01, 0x16, 0x7B, 0xE0, 0x71, 0xD0, 0xC2, 0x0E, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0x42, 0x01, 0x08, 0x73, 0xE2, 0x71, 0xD0, 0x22, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCA, 0x01, 0x07, 0x75, 0xE2, 0x71, 0xD0, 0x23, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xC8, 0x01, 0x16, 0x7B, 0xE0, 0x71, 0xD0, 0x2C, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0x41, 0x01, 0x04, 0x3A, 0xE5, 0x71, 0xD0, 0x20, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xC9, 0x01, 0x02, 0x39, 0xE0, 0x71, 0xD0, 0x2B, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xC7, 0x01, 0x06, 0x2F, 0xE1, 0x71, 0xD0, 0x21, 0x07, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCB, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x70, 0x08, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCC, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x75, 0x08, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCD, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x7A, 0x08, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0xCE, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x7F, 0x08, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0x78, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x84, 0x08, 0xFE, 0xB0, 0x2D, 0x00, 0x00, 0xF0, 0x00, 0x68, 0x79, 0x01, 0x02, 0x3F, 0xE0, 0x71, 0xD0, 0x89, 0x08, 0xFE, 0x9B, 0xF0, 0x00, 0xF3, 0x90, 0xA8, 0xF3, 0xBE, 0xA9, 0xB4, 0x17, 0xFD, 0xB0, 0x70, 0x00, 0xE2, 0x20, 0x00, 0x66, 0x24, 0xE2, 0x30, 0x00, 0x71, 0x24, 0xE2, 0x40, 0x00, 0x7C, 0x24, 0xE2, 0x50, 0x00, 0x87, 0x24, 0xE2, 0x60, 0x00, 0x92, 0x24, 0xB4, 0x47, 0xFD, 0xB1, 0x80, 0x00, 0xB5, 0x47, 0xD2, 0x9A, 0x24, 0xB4, 0x47, 0xFD, 0xB1, 0x08, 0x00, 0xB5, 0x47, 0xD2, 0x9A, 0x24, 0xB4, 0x48, 0xFD, 0xB1, 0x80, 0x00, 0xB5, 0x48, 0xD2, 0x9A, 0x24, 0xB4, 0x48, 0xFD, 0xB1, 0x08, 0x00, 0xB5, 0x48, 0xD2, 0x9A, 0x24, 0xB4, 0x49, 0xFD, 0xB1, 0x80, 0x00, 0xB5, 0x49, 0xD2, 0x9A, 0x24, 0xB4, 0x49, 0xFD, 0xB1, 0x08, 0x00, 0xB5, 0x49, 0xB4, 0x17, 0xFD, 0xB0, 0x07, 0x00, 0xAD, 0x00, 0x02, 0xAF, 0xDF, 0xAD, 0x24, 0xF3, 0x90, 0x28, 0xF3, 0xBE, 0x29, 0xAA, 0x16, 0xE0, 0x16, 0x02, 0xBE, 0x24, 0xF0, 0x00, 0x68, 0x90, 0x80, 0x04, 0x4F, 0xE0, 0x71, 0xFE, 0xF0, 0x00, 0x68, 0xBE, 0x81, 0x10, 0x4F, 0xE0, 0x71]
            # patch.add_data(0x1E2291, event_patch_data)
            # i = 0x1E2291 + len(event_patch_data)

            # modify event 2121 to set tries counter to 10 at the start of each of the 6 starter rooms and then load their original entrance event, and initiate counter
            #start of event checks to see if it's a retry on a platforming room - this is specifically for Z-platform room
            event_patch_data = [0xE0, 0x2B, 0x00, 0xBA, 0x7A, 0xE4, 0x2D, 0x01, 0x00, 0xBD, 0x7A, 0xE4, 0x2D, 0x05, 0x00, 0xBD, 0x7A, 0xE4, 0x2D, 0x09, 0x00, 0xBD, 0x7A, 0xE4, 0x2D, 0x0D, 0x00, 0xBD, 0x7A, 0xE4, 0x2D, 0x11, 0x00, 0xBD, 0x7A, 0xE4, 0x2D, 0x15, 0x00, 0xBD, 0x7A, 0xA8, 0x2B, 0x0A, 0xC3, 0xE2, 0xCF, 0x01, 0xDC, 0x7A, 0xE2, 0xD3, 0x01, 0xE4, 0x7A, 0xE2, 0xC8, 0x01, 0xEC, 0x7A, 0xE2, 0xD1, 0x01, 0xF4, 0x7A, 0xE2, 0xD2, 0x01, 0xFC, 0x7A, 0xE2, 0xC9, 0x01, 0x04, 0x7B, 0xB0, 0x2D, 0x01, 0x00, 0xD0, 0x1A, 0x0D, 0xFE, 0xB0, 0x2D, 0x05, 0x00, 0xD0, 0x0F, 0x00, 0xFE, 0xB0, 0x2D, 0x09, 0x00, 0xD0, 0x2C, 0x07, 0xFE, 0xB0, 0x2D, 0x0D, 0x00, 0xD0, 0x1E, 0x0D, 0xFE, 0xB0, 0x2D, 0x11, 0x00, 0xD0, 0x24, 0x0D, 0xFE, 0xB0, 0x2D, 0x15, 0x00, 0xD0, 0x2B, 0x07, 0xFE]
            patch.add_data(0x1F7A91, event_patch_data)
            i = 0x1F7A91 + len(event_patch_data)
            while i <= 0x1F7B0C:
                patch.add_data(i, 0x9B)
                i += 1

            # fix Z-platform room failing to reload on failure - force it to run entrance event on reload at original coords
            # this only affects this one room for some reason
            # this means that if you fail at any point in this room, you will go back to the beginning of it
            # oh well. git gud
            patch.add_data(0x1F5666, [0x81, 0x04, 0x3A, 0xE5])

            # 6 entrance doors
            initial_door_room_addresses = [0x205CCD, 0x205CD4, 0x205CDB, 0x205CE2, 0x205CE9, 0x205CF0]
            initial_door_coord_addresses = [0x205CCF, 0x205CD6, 0x205CDD, 0x205CE4, 0x205CEB, 0x205CF2]

            # remove any 10-try set events from rooms so that they dont reset if in the middle of a chain
            patch.add_data(0x1F5462, [0xA6, 0xAC, 0xD0, 0x25, 0x07, 0xFE, 0x9B, 0xFE])
            patch.add_data(0x1F5531, [0xA6, 0xAC, 0x9C, 0x0B, 0x15, 0xF2, 0x36, 0x03, 0x16, 0xF2, 0x36, 0x03, 0x17, 0xF2, 0x36, 0x03, 0xD0, 0x25, 0x07, 0xFE, 0x9B, 0xFE])

            # loop thru rooms to determine which exits should be loading 3350 or 332
            # if index in door is < 2, twin rooms should be using event 332 as entrance event, and finisher rooms should be using event 332 as exit event
            # if index in door is 3, twin rooms should be using event 3350 as entrance event, and finisher rooms should be using event 3350 as exit event

            # DYNAMIC WRITING OF EVENT 332 #
            # man, this is some shit #
            # dont ask me what the hell i did here but it apparently works #
            # this code completely replaces event 332 and calculates where jump pointers need to go, as some rooms have special conditions on how the entrance event should run, meaning varying byte size #

            original_address = 0x1E2291
            ram_jump_data = []
            room_counters = [1, 2, 5, 6, 9, 10, 13, 14, 17, 18, 21, 22]
            for counter in room_counters:
                ram_jump_data.append([0xE4, 0x2D, counter, 0x00, 0, 0])
            treasure_room_ram_jump = [0xD2, 0x00, 0x00]
            room_increments = [2, 3, 6, 7, 10, 11, 14, 15, 18, 19, 22, 23]
            ram_load_event_data = []

            for index, door in enumerate(doors):
                # set bowser door # to this room
                patch.add_data(initial_door_room_addresses[index], [door[0].relative_room_id])
                patch.add_data(initial_door_coord_addresses[index],
                               [door[0].start_x, door[0].start_y, door[0].start_z + 0xE0])
                # set tries to 10 and load original room event
                patch.add_data(0x1f7ABF + (index * 5), door[0].relative_room_id)
                patch.add_data(0x1f7AE1 + (index * 8), door[0].original_event)
                patch.add_data(door[0].original_event_location, [0x49, 0x08])
                for j in range(0, len(door)):
                    if j + 1 < len(door):
                        current_condition_address = original_address + 6 * len(ram_jump_data) + len(
                            treasure_room_ram_jump)
                        for l in range(0, index * 2 + j):
                            current_condition_address += len(ram_load_event_data[l])
                        addr = format(current_condition_address, 'x').zfill(6)
                        ram_jump_data[index * 2 + j][4] = int(addr[4:6], 16)
                        ram_jump_data[index * 2 + j][5] = int(addr[2:4], 16)
                        patchdata = []
                        patchdata.extend((0xB0, 0x2D, room_increments[index * 2 + j], 0x00))
                        if door[j + 1].relative_room_id == 0xD1:
                            patchdata.extend((0xB0, 0x1F, 0x00, 0x00))
                        patchdata.extend((0xF0, 0x00))
                        if not door[j].needs_manual_run_on_exit:
                            patchdata.extend((0x68, door[j + 1].relative_room_id, 0x81, door[j + 1].start_x,
                                              door[j + 1].start_y, door[j + 1].start_z + 0xE0))
                            patchdata.append(0x71)
                        else:
                            patchdata.extend((0x68, door[j + 1].relative_room_id, 0x01, door[j + 1].start_x,
                                              door[j + 1].start_y, door[j + 1].start_z + 0xE0))
                            patchdata.append(0x71)
                            patchdata.extend((0xD0, door[j + 1].original_event[0], door[j + 1].original_event[1]))
                        patchdata.append(0xFE)
                        ram_load_event_data.append(patchdata)

            treasure_room_jump_address = original_address
            for l in ram_jump_data:
                treasure_room_jump_address += len(l)
            treasure_room_jump_address += len(treasure_room_ram_jump)
            for l in ram_load_event_data:
                treasure_room_jump_address += len(l)
            addr = format(treasure_room_jump_address, 'x').zfill(6)
            treasure_room_ram_jump[1] = int(addr[4:6], 16)
            treasure_room_ram_jump[2] = int(addr[2:4], 16)

            combined_data = []
            for i in ram_jump_data:
                for j in i:
                    combined_data.append(j)
            for j in treasure_room_ram_jump:
                combined_data.append(j)
            for i in ram_load_event_data:
                for j in i:
                    combined_data.append(j)

            combined_data.extend((0xF0, 0x00))
            combined_data.extend((0xF3, 0x90, 0xA8))
            combined_data.extend((0xF3, 0xBE, 0xA9))
            combined_data.extend((0xB4, 0x17))
            combined_data.extend((0xFD, 0xB0, 0x70, 0x00))
            addr = treasure_room_jump_address
            jumpaddr = format(addr + 0x32, 'x').zfill(6)
            combined_data.extend((0xE2, 0x20, 0x00, int(jumpaddr[4:6], 16), int(jumpaddr[2:4], 16)))
            jumpaddr = format(addr + 0x32 + 0x0B, 'x').zfill(6)
            combined_data.extend((0xE2, 0x30, 0x00, int(jumpaddr[4:6], 16), int(jumpaddr[2:4], 16)))
            jumpaddr = format(addr + 0x32 + 0x0B + 0x0B, 'x').zfill(6)
            combined_data.extend((0xE2, 0x40, 0x00, int(jumpaddr[4:6], 16), int(jumpaddr[2:4], 16)))
            jumpaddr = format(addr + 0x32 + 0x0B + 0x0B + 0x0B, 'x').zfill(6)
            combined_data.extend((0xE2, 0x50, 0x00, int(jumpaddr[4:6], 16), int(jumpaddr[2:4], 16)))
            jumpaddr = format(addr + 0x32 + 0x0B + 0x0B + 0x0B + 0x0B, 'x').zfill(6)
            combined_data.extend((0xE2, 0x60, 0x00, int(jumpaddr[4:6], 16), int(jumpaddr[2:4], 16)))
            combined_data.extend((0xB4, 0x47))
            combined_data.extend((0xFD, 0xB1, 0x80, 0x00))
            combined_data.extend((0xB5, 0x47))
            jump1 = int(format(addr + 0x66, 'x').zfill(6)[4:6], 16)
            jump2 = int(format(addr + 0x66, 'x').zfill(6)[2:4], 16)
            combined_data.extend((0xD2, jump1, jump2))
            combined_data.extend((0xB4, 0x47))
            combined_data.extend((0xFD, 0xB1, 0x08, 0x00))
            combined_data.extend((0xB5, 0x47))
            combined_data.extend((0xD2, jump1, jump2))
            combined_data.extend((0xB4, 0x48))
            combined_data.extend((0xFD, 0xB1, 0x80, 0x00))
            combined_data.extend((0xB5, 0x48))
            combined_data.extend((0xD2, jump1, jump2))
            combined_data.extend((0xB4, 0x48))
            combined_data.extend((0xFD, 0xB1, 0x08, 0x00))
            combined_data.extend((0xB5, 0x48))
            combined_data.extend((0xD2, jump1, jump2))
            combined_data.extend((0xB4, 0x49))
            combined_data.extend((0xFD, 0xB1, 0x80, 0x00))
            combined_data.extend((0xB5, 0x49))
            combined_data.extend((0xD2, jump1, jump2))
            combined_data.extend((0xB4, 0x49))
            combined_data.extend((0xFD, 0xB1, 0x08, 0x00))
            combined_data.extend((0xB5, 0x49))
            combined_data.extend((0xB4, 0x17))
            combined_data.extend((0xFD, 0xB0, 0x07, 0x00))
            combined_data.extend((0xAD, 0x00, 0x02))
            combined_data.append(0xAF)
            clearaddr1 = int(format(addr + 0x66 + 0x13, 'x').zfill(6)[4:6], 16)
            clearaddr2 = int(format(addr + 0x66 + 0x13, 'x').zfill(6)[2:4], 16)
            combined_data.extend((0xDF, clearaddr1, clearaddr2))
            combined_data.extend((0xF3, 0x90, 0x28))
            combined_data.extend((0xF3, 0xBE, 0x29))
            finaladdr1 = int(format(addr + 0x8A, 'x').zfill(6)[4:6], 16)
            finaladdr2 = int(format(addr + 0x8A, 'x').zfill(6)[2:4], 16)
            combined_data.extend((0xAA, 0x16))
            if self.settings.is_flag_enabled(flags.BowsersKeep1):
                combined_data.extend((0xE0, 0x16, 0x01, finaladdr1, finaladdr2))
            elif self.settings.is_flag_enabled(flags.BowsersKeep2):
                combined_data.extend((0xE0, 0x16, 0x02, finaladdr1, finaladdr2))
            elif self.settings.is_flag_enabled(flags.BowsersKeep3):
                combined_data.extend((0xE0, 0x16, 0x03, finaladdr1, finaladdr2))
            elif self.settings.is_flag_enabled(flags.BowsersKeep5):
                combined_data.extend((0xE0, 0x16, 0x05, finaladdr1, finaladdr2))
            elif self.settings.is_flag_enabled(flags.BowsersKeep6):
                combined_data.extend((0xE0, 0x16, 0x06, finaladdr1, finaladdr2))
            else:
                combined_data.extend((0xE0, 0x16, 0x04, finaladdr1, finaladdr2))
            combined_data.extend((0xF0, 0x00))
            combined_data.extend((0x68, 0x90, 0x80, 0x04, 0x4F, 0xE0))
            combined_data.append(0x71)
            combined_data.append(0xFE)
            combined_data.extend((0xF0, 0x00))
            combined_data.extend((0x68, 0xBE, 0x81, 0x10, 0x4F, 0xE0))
            combined_data.append(0x71)

            c2 = []
            for i in combined_data:
                c2.append(format(i, 'x').zfill(2))

            patch.add_data(original_address, combined_data)
            i = original_address + len(combined_data)
            while i <= 0x1E24C6:
                patch.add_data(i, 0x9B)
                i += 1



        #Also need to patch the original event!!! In case Ds flag isnt enabled
        if self.settings.is_flag_enabled(flags.BowsersKeep1):
            patch.add_data(0x204CAD, 1)
        elif self.settings.is_flag_enabled(flags.BowsersKeep2):
            patch.add_data(0x204CAD, 2)
        elif self.settings.is_flag_enabled(flags.BowsersKeep3):
            patch.add_data(0x204CAD, 3)
        elif self.settings.is_flag_enabled(flags.BowsersKeep4):
            patch.add_data(0x204CAD, 4)
        elif self.settings.is_flag_enabled(flags.BowsersKeep5):
            patch.add_data(0x204CAD, 5)
        elif self.settings.is_flag_enabled(flags.BowsersKeep6):
            patch.add_data(0x204CAD, 6)

        # Choose character for the file select screen.
        i = int(self.hash, 16) % 5
        file_select_char_bytes = [0, 7, 13, 25, 19]
        self.file_select_character = [c for c in self.characters if c.index == i][0].__class__.__name__

        # Change file select character graphic, if not Mario.
        if i != 0:
            addresses = [0x34757, 0x3489a, 0x34ee7, 0x340aa, 0x3501e]
            for addr, value in zip(addresses, [0, 1, 0, 0, 1]):
                patch.add_data(addr, file_select_char_bytes[i] + value)

        # Possible names we can use for the hash values on the file select screen.  Needs to be 6 characters or less.
        file_entry_names = {
            'MARIO',
            'MALLOW',
            'GENO',
            'BOWSER',
            'PEACH',
        }
        # Also use enemy names, if they're 6 characters or less.
        for e in self.enemies:
            if isinstance(e, data.enemies.K9):
                name = e.name
            else:
                name = re.sub(r'[^A-Za-z]', '', e.name.upper())
            if len(name) <= 6:
                file_entry_names.add(name)
        file_entry_names = sorted(file_entry_names)

        # Replace file select names with "hash" values for seed verification.
        file_select_names = [
            file_entry_names[int(self.hash[0:8], 16) % len(file_entry_names)],
            file_entry_names[int(self.hash[8:16], 16) % len(file_entry_names)],
            file_entry_names[int(self.hash[16:24], 16) % len(file_entry_names)],
            file_entry_names[int(self.hash[24:32], 16) % len(file_entry_names)],
        ]
        for i, name in enumerate(file_select_names):
            addr = 0x3ef528 + (i * 7)
            val = name.encode().ljust(7, b'\x00')
            patch.add_data(addr, val)

        # Save file select hash text to show the user on the website, but the game uses '}' instead of dash.
        self.file_select_hash = ' / '.join(file_select_names).replace('}', '-')

        # Update ROM title and version.
        title = 'SMRPG-R {}'.format(self.seed).ljust(20)
        if len(title) > 20:
            title = title[:19] + '?'

        # Add version number on name entry screen.
        version_text = ('v' + VERSION).ljust(10)
        if len(version_text) > 10:
            raise ValueError("Version text is too long: {!r}".format(version_text))
        patch.add_data(0x3ef140, version_text)

        # Add title and major version number to SNES header data.
        patch.add_data(0x7fc0, title)
        v = VERSION.split('.')
        patch.add_data(0x7fdb, int(v[0]))

        return patch
