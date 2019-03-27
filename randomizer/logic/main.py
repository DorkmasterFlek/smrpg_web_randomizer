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
VERSION = '8.0beta16'


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

            #patch hard exits so they always go to twin rooms
            patch.add_data(0x1D40D5, [0x41, 0xA1, 0x93, 0x1C, 0x05, 0x00, 0x00, 0xE0, 0x81, 0x24, 0xA1, 0x9B, 0x56, 0x02, 0x00, 0x00, 0xE0])
            patch.add_data(0x1D4307, [0x2B, 0xA1, 0x96, 0x19, 0x00, 0x00, 0x00])
            patch.add_data(0x1D46E4, [0x27, 0xA1, 0x92, 0x1B, 0x03, 0x00, 0x00, 0xE0, 0x81, 0x42, 0xA1, 0x87, 0x76, 0x02, 0x1A, 0x58, 0x62, 0x81, 0x25, 0xA1, 0x95, 0x56, 0x02, 0x00, 0x00, 0xE0, 0x81, 0x28, 0xA1, 0x96, 0x19, 0x00, 0x00, 0x00, 0xE0, 0x81, 0x29, 0xA1, 0x96, 0x19, 0x00, 0x00, 0x00, 0xE0, 0x81, 0x2A, 0xA1, 0x96, 0x19, 0x00, 0x00, 0x00])
            #patch event exits so they always go to twin rooms
            patch.add_data(0x204E8D, [0x8C, 0x80, 0x00, 0x00, 0xE0, 0xFE, 0x68, 0x00, 0x81, 0x00, 0x00])
            patch.add_data(0x20502A, [0x9C, 0x80, 0x00, 0x00])
            patch.add_data(0x205285, [0xDA, 0x80, 0x00, 0x00])

            #patch twin rooms and final rooms so that they always run event 332 on load
            patch.add_data(0x20ED2E, [0x4C, 0x01])
            patch.add_data(0x20EDD3, [0x4C, 0x01])
            patch.add_data(0x20F0EE, [0x4C, 0x01])
            patch.add_data(0x20F2A4, [0x4C, 0x01])
            patch.add_data(0x20F38C, [0x4C, 0x01])
            patch.add_data(0x20F38F, [0x4C, 0x01])
            patch.add_data(0x20F392, [0x4C, 0x01])
            patch.add_data(0x20F395, [0x4C, 0x01])
            patch.add_data(0x20F398, [0x4C, 0x01])
            patch.add_data(0x20F39B, [0x4C, 0x01])
            patch.add_data(0x20F39E, [0x4C, 0x01])
            patch.add_data(0x20F3A1, [0x4C, 0x01])
            patch.add_data(0x20F703, [0x4C, 0x81])
            patch.add_data(0x20FB6C, [0x4C, 0x81])
            patch.add_data(0x20FB75, [0x4C, 0x81])
            patch.add_data(0x20FBDE, [0x4C, 0x81])
            patch.add_data(0x20FC11, [0x4C, 0x81])
            patch.add_data(0x20FC1D, [0x4C, 0x81])

            #remove music from twin rooms
            patch.add_data(0x20ED2D, [0x42])
            patch.add_data(0x20EDD2, [0x42])
            patch.add_data(0x20F0ED, [0x42])
            patch.add_data(0x20F2A3, [0x42])
            patch.add_data(0x20F38B, [0x42])
            patch.add_data(0x20F38E, [0x42])
            patch.add_data(0x20F391, [0x42])
            patch.add_data(0x20F394, [0x42])
            patch.add_data(0x20F397, [0x42])
            patch.add_data(0x20F39A, [0x42])
            patch.add_data(0x20F39D, [0x42])
            patch.add_data(0x20F3A0, [0x42])

            #create a patch that modifies event 322 to be usable for keep reward chest rooms and rooms with hard exits
            #create conditions that allow you to run an event for rooms that by default are a finishing room or a hard exit room
            event_patch_data = [0xC3, 0xE2, 0xD2, 0x01, 0xEC, 0x22, 0xE2, 0xD4, 0x01, 0xF3, 0x22, 0xE2, 0xC8, 0x01, 0xFA, 0x22, 0xE2, 0xC7, 0x01, 0x01, 0x23, 0xE2, 0xCD, 0x01, 0x08, 0x23, 0xE2, 0x79, 0x01, 0x0F, 0x23, 0xE2, 0x24, 0x01, 0x16, 0x23, 0xE2, 0x25, 0x01, 0x1D, 0x23, 0xE2, 0x26, 0x01, 0x24, 0x23, 0xE2, 0x27, 0x01, 0x2B, 0x23, 0xE2, 0x28, 0x01, 0x32, 0x23, 0xE2, 0x29, 0x01, 0x39, 0x23, 0xE2, 0x2A, 0x01, 0x40, 0x23, 0xE2, 0x2B, 0x01, 0x47, 0x23, 0xE2, 0x8C, 0x00, 0x4E, 0x23, 0xE2, 0x9C, 0x00, 0x55, 0x23, 0xE2, 0xDA, 0x00, 0x5C, 0x23, 0xE2, 0x00, 0x01, 0x63, 0x23, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE, 0x68, 0xBE, 0x81, 0x0F, 0x0F, 0xE0, 0xFE]
            patch.add_data(0x1E2291, event_patch_data)
            i = 0x1E2291 + len(event_patch_data)
            while i < 0x1E24C6:
                patch.add_data(i, 0x9B)
                i += 1
            patch.add_data(0x1E24C6, 0xFE)

            #loop thru rooms to determine which exits should be loading 3350 or 332
            #if index in door is < 2, twin rooms should be using event 332 as entrance event, and finisher rooms should be using event 332 as exit event
            #if index in door is 3, twin rooms should be using event 3350 as entrance event, and finisher rooms should be using event 3350 as exit event

            initial_door_room_addresses = [0x205CCD, 0x205CD4, 0x205CDB, 0x205CE2, 0x205CE9, 0x205CF0]
            initial_door_coord_addresses = [0x205CCF, 0x205CD6, 0x205CDD, 0x205CE4, 0x205CEB, 0x205CF2]
            for index, door in enumerate(doors):
                #set bowser door # to this room
                patch.add_data(initial_door_room_addresses[index], [door[0].relative_room_id])
                patch.add_data(initial_door_coord_addresses[index], [door[0].start_x, door[0].start_y, door[0].start_z + 0xE0])
                for j in range(0,len(door)):
                    #patch room to switch twin room entrance event, or current room's exit event, to 3350 (load reward chest)
                    if j+1 == len(door):
                        if door[j].is_final:
                            patch.add_data(door[j].change_event_byte, [0x16, 0x8D])
                        else:
                            patch.add_data(door[j].change_event_byte, [0x16, 0x0D])
                    #patch room to change event 322 to make this room's twin room or exit condition load the next room in the array
                    else:
                        patch.add_data(door[j].next_room_address, [door[j+1].relative_room_id])
                        print(door[j+1], hex(door[j].next_coord_address), [door[j+1].start_x, door[j+1].start_y, door[j+1].start_z + 0xE0])
                        patch.add_data(door[j].next_coord_address, [door[j+1].start_x, door[j+1].start_y, door[j+1].start_z + 0xE0])

            print(doors)

        # required doors to reach magikoopa
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
