# Main randomizer logic module that the front end calls.

import collections
import hashlib
import random
import re
import binascii
import math

from randomizer import data
from . import bosses
from . import characters
from . import chests
from . import dialogs
from . import doors
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
VERSION = '8.1.2'


def calcpointer(dec, origBytes=[]):
    origBytes.reverse()
    str = format(dec, 'x')
    hexcode = str.zfill(4)
    hexbytes = [int(hexcode[i:i + 2], 16) for i in range(0, len(hexcode), 2)]
    iterator = 0
    for by in origBytes:
        hexbytes[iterator] += by
        iterator += 1
    hexbytes.reverse()
    return hexbytes

def approximate_dimension(num):
  base = max(num - 32, 0)
  return 32 + math.ceil(base / 16) * 16

class SpritePhaseEvent:
    npc = 0
    sprite = 0
    mold = 0
    is_sequence_and_not_mold = True
    sequence = 0
    reverse = False
    original_event = 0
    original_event_location = 0
    level = 0
    invert_se_sw = False

    def __init__(self, npc, sprite, mold, is_sequence_and_not_mold, sequence, reverse, level, original_event, original_event_location):
        self.npc = npc
        self.sprite = sprite
        self.mold = mold
        self.is_sequence_and_not_mold = is_sequence_and_not_mold
        self.sequence = sequence
        self.reverse = reverse
        self.level = level
        self.original_event = original_event
        self.original_event_location = original_event_location

    # convert a sprite value to a pointer that can be patched in

    def generate_code(self):
        returnBytes = [];
        if not isinstance(self.npc, list):
            npcs = [];
            npcs.append(self.npc)
        else:
            npcs = self.npc
        for npc in npcs:
            returnBytes.extend([(0x14 + npc), 0x83])
            if self.is_sequence_and_not_mold and not self.reverse:
                returnBytes.extend([0x08, 0x40 + self.sprite, self.sequence])
            elif self.is_sequence_and_not_mold and self.reverse:
                returnBytes.extend([0x08, 0x40 + self.sprite, 0x80 + self.sequence])
            elif not self.is_sequence_and_not_mold and not self.reverse:
                returnBytes.extend([0x08, 0x08 + self.sprite, self.mold])
            elif not self.is_sequence_and_not_mold and self.reverse:
                returnBytes.extend([0x08, 0x08 + self.sprite, 0x80 + self.mold])
        returnBytes.append(0xD0)
        eventpointer = calcpointer(self.original_event)
        returnBytes.extend(eventpointer)
        returnBytes.append(0xFE)
        return returnBytes



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

        # Bundt palette swap flag.
        self.chocolate_cake = False

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

        # String data.
        self.wishes = data.dialogs.Wishes(self)
        self.quiz = data.dialogs.Quiz(self)

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
        dialogs.randomize_all(self)

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
            #Fail if starter is excluded, or if everyone excluded
            if (self.settings.is_flag_enabled(flags.ExcludeMario) and self.settings.is_flag_enabled(
                    flags.StartMario)) or (
                    self.settings.is_flag_enabled(flags.ExcludeMallow) and self.settings.is_flag_enabled(
                    flags.StartMallow)) or (
                    self.settings.is_flag_enabled(flags.ExcludeGeno) and self.settings.is_flag_enabled(
                    flags.StartGeno)) or (
                    self.settings.is_flag_enabled(flags.ExcludeBowser) and self.settings.is_flag_enabled(
                    flags.StartBowser)) or (
                    self.settings.is_flag_enabled(flags.ExcludeToadstool) and self.settings.is_flag_enabled(
                    flags.StartToadstool)):
                raise Exception("Cannot exclude your starter")
            elif self.settings.is_flag_enabled(flags.ExcludeMario) and self.settings.is_flag_enabled(
                    flags.ExcludeMallow) and self.settings.is_flag_enabled(
                    flags.ExcludeGeno) and self.settings.is_flag_enabled(
                    flags.ExcludeBowser) and self.settings.is_flag_enabled(flags.ExcludeToadstool):
                raise Exception("Cannot exclude all 5 characters")
            #Move chosen starting character to front of join order
            else:
                for char in self.character_join_order:
                    if (self.settings.is_flag_enabled(flags.StartMario) and char.index == 0) or (self.settings.is_flag_enabled(flags.StartMallow) and char.index == 4) or (self.settings.is_flag_enabled(flags.StartGeno) and char.index == 3) or (self.settings.is_flag_enabled(flags.StartBowser) and char.index == 2) or (self.settings.is_flag_enabled(flags.StartToadstool) and char.index == 1):
                        self.character_join_order.insert(0, self.character_join_order.pop(self.character_join_order.index(char)))
            #Count number of excluded characters, and empty their slots
            position_iterator = 0
            empties = 0
            for char in self.character_join_order:
                if (self.settings.is_flag_enabled(flags.ExcludeMario) and char.index == 0) or (
                        self.settings.is_flag_enabled(flags.ExcludeMallow) and char.index == 4) or (
                        self.settings.is_flag_enabled(flags.ExcludeGeno) and char.index == 3) or (
                        self.settings.is_flag_enabled(flags.ExcludeBowser) and char.index == 2) or (
                        self.settings.is_flag_enabled(flags.ExcludeToadstool) and char.index == 1):
                    self.character_join_order[position_iterator] = None
                    empties += 1
                position_iterator += 1
            #Make sure first three slots are filled when NFC is turned off, when possible
            if not self.settings.is_flag_enabled(flags.NoFreeCharacters):
                for i in range(empties):
                    position_iterator = 0
                    for char in self.character_join_order:
                        if char is None and position_iterator < 3:
                            self.character_join_order.append(self.character_join_order.pop(self.character_join_order.index(char)))
                        position_iterator += 1
            #Add characters to Mushroom Way and Moleville when NFC is turned on
            if self.settings.is_flag_enabled(flags.NoFreeCharacters):
                addresses = [0x1ef86c, 0x1ffd82, 0x1fc4f1, 0x1e6d58, 0x1e8b71]
            else:
                addresses = [0x1ef86c, 0x1ef86e, 0x1ef870, 0x1fc4f1, 0x1e8b71]
            dialogue_iterator = 0
            for addr, character in zip(addresses, self.character_join_order):
                dialogue_iterator += 1
                #Character joins and dialogues are 0x9B by default, replaced with this code when populated
                if character is not None:
                    #Write message stating who joined
                    if character.palette is not None and character.palette.rename_character:
                        message = '"' + character.palette.name + '" (' + character.name + ') joins!'
                    else:
                        message = character.name + " joins!"
                    messagestring = binascii.hexlify(bytes(message, encoding='ascii'))
                    messagebytes = [int(messagestring[i:i+2],16) for i in range(0,len(messagestring),2)]
                    messagebytes.append(0x00)
                    #Append character join event and corresponding message to code
                    if self.settings.is_flag_enabled(flags.NoFreeCharacters):
                        if dialogue_iterator == 2:
                            patch.add_data(0x242c52, messagebytes)
                            patch.add_data(0x1ffd84, [0x60, 0xac, 0xac, 0x00])
                        if dialogue_iterator == 3:
                            patch.add_data(0x221475, messagebytes)
                            patch.add_data(0x1fc8dd, [0x60, 0x48, 0xa2, 0x00])
                            #show character walking around forest maze
                        if dialogue_iterator == 4:
                            patch.add_data(0x242238, messagebytes)
                            patch.add_data(0x1e6d5a, [0x60, 0x89, 0xac, 0x00])
                        if dialogue_iterator == 5:
                            patch.add_data(0x23abf2, messagebytes)
                            patch.add_data(0x1e8b49, [0x60, 0xff, 0xaa, 0x00])
                    else:
                        if dialogue_iterator == 4:
                            patch.add_data(0x242c52, messagebytes)
                            patch.add_data(0x1fc8dd, [0x60, 0xac, 0xac, 0x00])
                        if dialogue_iterator == 5:
                            patch.add_data(0x221475, messagebytes)
                            patch.add_data(0x1e8b49, [0x60, 0x48, 0xa2, 0x00])
                    patch.add_data(addr, [0x36, 0x80 + character.index])
                #replace overworld characters in recruitment spots
                if self.settings.is_flag_enabled(flags.NoFreeCharacters) and dialogue_iterator == 2:
                    #mushroom way
                    patch.add_data(0x14b3BC, character.mway_1_npc_id)
                    patch.add_data(0x14b411, character.mway_2_npc_id)
                    patch.add_data(0x14b452, character.mway_3_npc_id)
                if (dialogue_iterator == 4 and not self.settings.is_flag_enabled(flags.NoFreeCharacters)) or (self.settings.is_flag_enabled(flags.NoFreeCharacters) and dialogue_iterator == 3):
                    #forest maze
                    patch.add_data(0x14b8eb, character.forest_maze_sprite_id)
                    if character.name is "Mario":
                        patch.add_data(0x215e4f, 0x42)
                        patch.add_data(0x215e56, 0x12)
                if self.settings.is_flag_enabled(flags.NoFreeCharacters) and dialogue_iterator == 4:
                    #moleville
                    patch.add_data(0x14c491, character.moleville_sprite_id)
                if dialogue_iterator == 5:
                    #show character in marrymore
                    patch.add_data(0x14a94d, character.forest_maze_sprite_id)
                    if character.name is not "Toadstool":
                        if character.name is "Mario":
                            #surprised
                            patch.add_data(0x20d338, [0x08, 0x43, 0x00])
                            #on ground
                            patch.add_data(0x20d34e, [0x08, 0x4B, 0x01])
                            #sitting
                            patch.add_data(0x20d43b, [0x08, 0x4a, 0x1f])
                            #looking down
                            patch.add_data(0x20d445, [0x08, 0x48, 0x06])
                            patch.add_data(0x20d459, [0x08, 0x48, 0x06])
                            #crying
                            patch.add_data(0x20d464, [0x10, 0x80])
                            patch.add_data(0x20d466, [0x08, 0x43, 0x03])
                            #surprised
                            patch.add_data(0x20d48c, [0x08, 0x43, 0x00])
                            #looking down
                            patch.add_data(0x20d4d4, [0x08, 0x48, 0x06])
                            #crying
                            patch.add_data(0x20d4d9, [0x10, 0x80])
                            patch.add_data(0x20d4db, [0x08, 0x43, 0x03])
                            #surprised reversed
                            patch.add_data(0x20d5d8, [0x08, 0x43, 0x80])
                            #crying in other direction
                            patch.add_data(0x20d5e3, [0x08, 0x43, 0x84])
                        else:
                            #surprised
                            patch.add_data(0x20d338, [0x08, 0x42, 0x00])
                            patch.add_data(0x20d48c, [0x08, 0x42, 0x00])
                            #surprised reversed
                            patch.add_data(0x20d5d8, [0x08, 0x42, 0x80])
                            #sitting
                            patch.add_data(0x20d43b, [0x08, 0x49, 0x1f])
                            if character.name is "Geno":
                                #crying
                                patch.add_data(0x20d466, [0x08, 0x40, 0x0B])
                                patch.add_data(0x20d4db, [0x08, 0x40, 0x0B])
                                #crying in other direction
                                patch.add_data(0x20d5e3, [0x08, 0x40, 0x8C])

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
        cursor_id = self.character_join_order[0].index

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

            # Dialogs
            patch += self.wishes.get_patch()
            patch += self.quiz.get_patch()

            # FIXME
            # print(">>>>>>>> WISHES")
            # for wish in self.wishes.wishes:
            #     print(">>>>>>>>>>>>>>>> {}".format(wish))

            # print(">>>>>>>> QUIZ")
            # for question in self.quiz.questions:
            #     print(">>>>>>>>>>>>>>>> {}".format(question))

        # Unlock the whole map if in debug mode in standard.
        if self.debug_mode and not self.open_mode:
            patch += map.unlock_world_map()

        # Bowser's Keep doors
        patch += doors.patch_bowser_doors(self)

        # factory warp
        if self.settings.is_flag_enabled(flags.CasinoWarp):
            # patch the event jump
            # event 2637

            # star piece event check
            # sometimes lazy shell can cause some weirdness with addresses, but we know this event began at 0x1FF451
            # and our custom code should start +3 after that

            # if R7 is turned on, we want this to be a check for 7 star pieces, not 6

            if self.settings.is_flag_enabled(flags.SevenStarHunt):
                patch.add_data(0x1FF454, [0xE0, 0x35, 0x07, 0x5C, 0xF4])
            else:
                patch.add_data(0x1FF454, [0xE0, 0x35, 0x06, 0x5C, 0xF4])

            patch.add_data(0x1FF459, [0xD2, 0x67, 0xF4, 0xD0, 0x48, 0x08])

            original_event_address = 0x1FF467
            start9_b_address = 0x1FF45F
            i = start9_b_address
            while i < original_event_address:
                patch.add_data(i, 0x9B)
                i += 1

            # event 2120
            patch.add_data(0x1F7A4D,
                           [0x60, 0x80, 0xAB, 0xC0, 0x66, 0x58, 0x7A, 0xD2, 0x67, 0xF4, 0xFE, 0x74, 0xD0, 0xCF, 0x0E,
                            0xFE])
            original_end_address = 0x1F7A90
            start9_b_address = 0x1F7A5D
            i = start9_b_address
            while i <= original_end_address:
                patch.add_data(i, 0x9B)
                i += 1

            # Dialog
            patch.add_data(0x23D3CE, [0x44, 0x6F, 0x0F, 0x20, 0x77, 0x61, 0x6E, 0x74, 0x11, 0x67, 0x6F, 0x11, 0x53,
                                      0x6D, 0x69, 0x74, 0x68, 0x79, 0x3F, 0x02, 0x08, 0x07, 0x20, 0x28, 0x4E, 0x6F,
                                      0x29, 0x01, 0x08, 0x07, 0x20, 0x28, 0x59, 0x65, 0x73, 0x29, 0x00])





        #### Logic for rewriting overworld sprites ####

        #Some sprites are not default, and need an event to set the proper mold.
        #This array will contain a set of building blocks for those sprites and where they should appear, and rewrite 3727 to control it.
        spritePhaseEvents = []


        for location in self.boss_locations:
            if (location.name in ["HammerBros", "Croco1", "Mack", "Belome1", "Bowyer", "Croco2", "Punchinello", "KingCalamari",
                                  "Booster", "Johnny", "Belome2", "Jagger", "Jinx3",
                                  "Megasmilax", "Dodo", "Valentina", "Magikoopa", "Boomer", "CzarDragon", "AxemRangers",
                                  "Countdown", "Clerk", "Manager", "Director", "Gunyolk"]):
                for enemy in location.pack.common_enemies:
                    if enemy.overworld_sprite is not None:
                        shuffled_boss = enemy
                if (approximate_dimension(shuffled_boss.sprite_height) <= approximate_dimension(location.sprite_height) and approximate_dimension(shuffled_boss.sprite_width) <= approximate_dimension(location.sprite_width)) or location.name in ["Belome1", "Belome2", "Johnny", "Jagger", "Jinx3", "Dodo", "Magikoopa", "Boomer", "Countdown"]:
                    sprite = shuffled_boss.battle_sprite
                    mold = shuffled_boss.battle_mold
                    sequence = shuffled_boss.battle_sequence
                    plus = shuffled_boss.battle_sprite_plus
                    freeze = shuffled_boss.battle_freeze
                    sesw_only = shuffled_boss.battle_sesw_only
                    invert_se_sw = shuffled_boss.battle_invert_se_sw
                    extra_sequence = False
                    push_sequence = shuffled_boss.battle_push_sequence
                    push_length = shuffled_boss.battle_push_length
                    northeast_mold = shuffled_boss.battle_northeast_mold
                    dont_reverse_northeast = False
                else:
                    sprite = shuffled_boss.overworld_sprite
                    mold = shuffled_boss.overworld_mold
                    sequence = shuffled_boss.overworld_sequence
                    plus = shuffled_boss.overworld_sprite_plus
                    freeze = shuffled_boss.overworld_freeze
                    sesw_only = shuffled_boss.overworld_sesw_only
                    invert_se_sw = shuffled_boss.overworld_invert_se_sw
                    extra_sequence = shuffled_boss.overworld_extra_sequence
                    push_sequence = shuffled_boss.overworld_push_sequence
                    push_length = shuffled_boss.overworld_push_length
                    northeast_mold = shuffled_boss.overworld_northeast_mold
                    dont_reverse_northeast = shuffled_boss.overworld_dont_reverse_northeast
                    

                # Mushroom Way
                if location.name == "HammerBros":
                    print(location, shuffled_boss)
                    # reassign NPC 283's sprite
                    # try big sprite
                    patch.add_data(0x1DBfbd, calcpointer(sprite, [0x00, 0x68]));
                    #for sprites that require a specific mold or sequence, change the room load events to set the proper sequence or mold first
                    if sequence > 0 or mold > 0:
                        if sequence > 0:
                            sub_sequence = True
                        elif mold > 0:
                            sub_sequence = False
                        spritePhaseEvents.append(SpritePhaseEvent(7, plus, mold, sub_sequence, sequence, False, 205, 2814, 0x20f045))
                # Bandit's Way
                if location.name == "Croco1":
                    print(location, shuffled_boss)
                    # use npc 110, set properties to match croco's
                    for addr in [0x1495e1, 0x14963a, 0x14969f, 0x14b4c7, 0x14b524]:
                        patch.add_data(addr, [0xBB, 0x01])
                    # replace its sprite
                    if freeze or sesw_only:
                        patch.add_data(0x1DBB02, calcpointer(sprite, [0x00, 0x08]));
                    else:
                        patch.add_data(0x1DBB02, calcpointer(sprite, [0x00, 0x00]));
                    patch.add_data(0x1DBB04, [0x80, 0x02, 0x55, 0x0a]);
                    #need to change a lot of things in bandit's way to get every boss to work
                    sub_sequence = False
                    if sequence > 0:
                        sub_sequence = True
                    #bandits way 1
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(5, plus, mold, sub_sequence, sequence, False, 76, 1714, 0x20e8e0))
                    if not freeze:
                        if extra_sequence is not False:
                            patch.add_data(0x1f3bac, [0x08, 0x40, 0x80 + extra_sequence])
                        else:
                            patch.add_data(0x1f3bac, [0x08, 0x40 + plus, 0x80 + sequence])
                    else:
                        patch.add_data(0x1f3bac, [0x9b, 0x9b, 0x9b])
                    if invert_se_sw: #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x1f3be4, [0x75]) #face northwest
                        patch.add_data(0x1f3be7, [0x73]) #face southwest
                    if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                        patch.add_data(0x1f3bb1, [0x9b])
                    if sesw_only: #dont face another direction
                        patch.add_data(0x1f3be7, [0x73]) #face southwest
                    if freeze: #dont face southwest
                        patch.add_data(0x1f3be4, [0x9b])
                        patch.add_data(0x1f3be7, [0x9b])
                    if freeze or (not sub_sequence and mold > 0): #dont loop
                        patch.add_data(0x1f3be8, [0x9b])
                    #bandits way 2
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(8, plus, mold, sub_sequence, sequence, False, 207, 1702, 0x20F07b))
                    if not freeze:
                        if extra_sequence is not False:
                            patch.add_data(0x1f3541, [0x08, 0x40, 0x80 + extra_sequence])
                        else:
                            patch.add_data(0x1f3541, [0x08, 0x40 + plus, 0x80 + sequence])
                    else:
                        patch.add_data(0x1f3541, [0x9b, 0x9b, 0x9b])
                    if invert_se_sw:  #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x1f3553, [0x75])  #face northwest
                        patch.add_data(0x1f3556, [0x73])  #face southwest
                        patch.add_data(0x1f356e, [0x71])  #face southeast
                        patch.add_data(0x1f357d, [0x77])  #face northeast
                    if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                        patch.add_data(0x1f3552, [0x9b])
                    if sesw_only: #dont face north
                        patch.add_data(0x1f3556, [0x73])  #face southwest
                        patch.add_data(0x1f356e, [0x71])  #face southeast
                    if freeze: #dont face southwest
                        patch.add_data(0x1f3553, [0x9b])
                        patch.add_data(0x1f357d, [0x9b])
                        patch.add_data(0x1f3556, [0x9b])
                        patch.add_data(0x1f356e, [0x9b])
                    if freeze or (not sub_sequence and mold > 0): #dont loop
                        patch.add_data(0x1f3563, [0x9b])
                    #bandits way 3
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(8, plus, mold, sub_sequence, sequence, False, 77, 1713, 0x20e8e3))
                    if not freeze:
                        if extra_sequence is not False:
                            patch.add_data(0x1f3b81, [0x08, 0x40, 0x80 + extra_sequence])
                        else:
                            patch.add_data(0x1f3b81, [0x08, 0x40 + plus, 0x80 + sequence])
                    else:
                        patch.add_data(0x1f3b81, [0x9b, 0x9b, 0x9b])
                    if invert_se_sw: #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x1f3b91, [0x75]) #face northwest
                        patch.add_data(0x211ffa, [0x75]) #face northwest
                        patch.add_data(0x21202b, [0x75]) #face northwest
                        patch.add_data(0x212059, [0x77]) #face northeast
                    if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                        patch.add_data(0x1f3b90, [0x9b])
                    if freeze: #dont face another direction
                        patch.add_data(0x1f3b91, [0x9b])
                    if freeze or (not sub_sequence and mold > 0): #dont loop
                        patch.add_data(0x211fd8, [0x9b])
                        patch.add_data(0x211ff0, [0x9b])
                    if freeze: #dont face southwest
                        patch.add_data(0x211ffa, [0x9b])
                        patch.add_data(0x21202b, [0x9b])
                        patch.add_data(0x212059, [0x9b])
                    #bandits way 4
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(12, plus, mold, sub_sequence, sequence, False, 78, 1698, 0x20e8e6))
                    if invert_se_sw: #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x1f33d0, [0x71])  #face southeast
                        patch.add_data(0x1f3406, [0x77])  #face northeast
                        patch.add_data(0x1f3409, [0x75])  #face northwest
                        patch.add_data(0x1f3414, [0x77])  #face northeast
                    if freeze or (not sub_sequence and mold > 0): #dont loop
                        patch.add_data(0x1f33c9, [0x9b])
                        #patch.add_data(0x1f340e, [0x9b])
                    if sesw_only: #dont face another direction
                        patch.add_data(0x1f33d0, [0x71])  #face southeast
                    if freeze: #dont face southwest
                        patch.add_data(0x1f3406, [0x9b])
                        patch.add_data(0x1f3409, [0x9b])
                        patch.add_data(0x1f3414, [0x9b])
                        patch.add_data(0x1f33d0, [0x9b])
                    #bandits way 5
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(8, plus, mold, sub_sequence, sequence, False, 206, 1708, 0x20f078))
                    if not freeze:
                        if extra_sequence is not False:
                            patch.add_data(0x1f3863, [0x08, 0x40, 0x80 + extra_sequence])
                        else:
                            patch.add_data(0x1f3863, [0x08, 0x40 + plus, 0x80 + sequence])
                    else:
                        patch.add_data(0x1f3863, [0x9b, 0x9b, 0x9b])
                    if invert_se_sw:  #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x1f3873, [0x75])  #face northwest
                        patch.add_data(0x1f3995, [0x73])  #face southwest
                        patch.add_data(0x1f39ac, [0x73])  #face southwest
                        patch.add_data(0x1f3876, [0x73])  #face southwest
                        patch.add_data(0x1f38e4, [0x71])  #face southeast
                        patch.add_data(0x1f39da, [0x77])  #face northeast
                    if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                        patch.add_data(0x1f3872, [0x9b])
                    if sesw_only: #dont face north
                        patch.add_data(0x1f3876, [0x73])
                        patch.add_data(0x1f38e4, [0x71])  #face southeast
                    if freeze: #dont face southwest
                        patch.add_data(0x1f3873, [0x9b])
                        patch.add_data(0x1f3876, [0x9b])
                        patch.add_data(0x1f38e4, [0x9b])
                        patch.add_data(0x1f39da, [0x9b])
                        patch.add_data(0x1f3995, [0x9b])  #face southwest
                        patch.add_data(0x1f39ac, [0x9b])  #face southwest
                    #if freeze or (not sub_sequence and mold > 0): #dont loop
                    #    patch.add_data(0x211fc5, [0x9b])
                if location.name == "Mack":
                    print(location, shuffled_boss)
                    # reassign NPC 480's sprite
                    patch.add_data(0x1Dc520, calcpointer(sprite, [0x00, 0x68]));
                    #face southwest
                    patch.add_data(0x14ca86, 0x63);
                    #delete sequence init if character shouldnt move
                    if not freeze:
                        patch.add_data(0x1e2921, [0x08, 0x40 + plus, sequence])
                    else:
                        patch.add_data(0x1e2921, [0x9b, 0x9b, 0x9b])
                    #for sprites that require a specific mold or sequence, change the room load events to set the proper sequence or mold first
                    if sequence > 0 or mold > 0:
                        if sequence > 0:
                            sub_sequence = True
                        elif mold > 0:
                            sub_sequence = False
                        spritePhaseEvents.append(SpritePhaseEvent(3, plus, mold, sub_sequence, sequence, False, 326, 368, 0x20f47d))
                if location.name == "Belome1":
                    # use npc 371, set properties to match belome's
                    patch.add_data(0x14c67a, [0xcd, 0x05]);
                    # replace its sprite
                    patch.add_data(0x1Dc225, calcpointer(sprite, [0x00, 0xA8]));
                    patch.add_data(0x1Dc227, [0x60, 0x02, 0xaa, 0x12, 0x00]);
                    print(location, shuffled_boss)
                    if sequence > 0 or mold > 0:
                        if sequence > 0:
                            sub_sequence = True
                        elif mold > 0:
                            sub_sequence = False
                        spritePhaseEvents.append(SpritePhaseEvent(3, plus, mold, sub_sequence, sequence, False, 302, 3135, 0x20f3be))
                if location.name == "Bowyer":
                    print(location, shuffled_boss)
                    # reassign NPC 455's sprite
                    # try big sprite
                    patch.add_data(0x1dc54a, calcpointer(sprite, [0x00, 0x68]));
                    if sequence > 0 or mold > 0:
                        if sequence > 0:
                            sub_sequence = True
                        elif mold > 0:
                            sub_sequence = False
                        spritePhaseEvents.append(SpritePhaseEvent(16, plus, mold, sub_sequence, sequence, False, 232, 15, 0x20F1C6))
                if location.name == "Croco2":
                    print(location, shuffled_boss)
                    # use npc 367, set properties to match croco's
                    patch.add_data(0x14c2a2, [0xBE, 0xA5]);
                    patch.add_data(0x14c300, [0xBE, 0xE5]);
                    patch.add_data(0x14c33e, [0xBE, 0xF5]);
                    patch.add_data(0x14c398, [0xBE, 0xC5]);
                    patch.add_data(0x14c3e6, [0xBE, 0xD5]);
                    patch.add_data(0x14c448, [0xBE, 0xB5]);
                    # replace its sprite
                    if freeze or sesw_only:
                        patch.add_data(0x1Dc209, calcpointer(sprite, [0x00, 0x08]));
                    else:
                        patch.add_data(0x1Dc209, calcpointer(sprite, [0x00, 0x00]));
                    patch.add_data(0x1Dc20b, [0x80, 0xa2, 0x55, 0x2a]);
                    #need to change a lot of things in moleville to get this to work
                    sub_sequence = True
                    if sequence == 0 and mold > 0:
                        sub_sequence = False
                    if freeze or (not sub_sequence and mold > 0): #dont loop
                        patch.add_data(0x202615, [0x9b])
                        patch.add_data(0x21887f, [0x9b])
                        patch.add_data(0x218885, [0x9b])
                        patch.add_data(0x218b4e, [0x9b])
                        patch.add_data(0x218b56, [0x9b])
                        patch.add_data(0x218ac4, [0x9b])
                        patch.add_data(0x218acb, [0x9b])
                        patch.add_data(0x218a34, [0x9b])
                        patch.add_data(0x218a3d, [0x9b])
                        patch.add_data(0x2189aa, [0x9b])
                        patch.add_data(0x2189ad, [0x9b])
                        patch.add_data(0x218915, [0x9b])
                        patch.add_data(0x21891B, [0x9b])
                    if freeze: #dont do directional commands
                        patch.add_data(0x21886f, [0x9b])
                        patch.add_data(0x218b41, [0x9b])
                        patch.add_data(0x218ab7, [0x9b])
                        patch.add_data(0x218a27, [0x9b])
                        patch.add_data(0x218a37, [0x9b])
                        patch.add_data(0x218a3a, [0x9b])
                        patch.add_data(0x21899D, [0x9b])
                        patch.add_data(0x218905, [0x9b])
                        patch.add_data(0x218914, [0x9b])
                    if sesw_only: #dont face north
                        patch.add_data(0x218a37, [0x73])
                        patch.add_data(0x21899D, [0x73])
                        patch.add_data(0x218905, [0x71])
                    if invert_se_sw: #scarecrow sprite sequence 0 and 1 are inverted
                        patch.add_data(0x21886f, [0x77])
                        patch.add_data(0x218b41, [0x77])
                        patch.add_data(0x218ab7, [0x77])
                        patch.add_data(0x218a27, [0x75])
                        patch.add_data(0x218a37, [0x73])
                        patch.add_data(0x218a3a, [0x77])
                        patch.add_data(0x21899D, [0x73])
                        patch.add_data(0x218905, [0x71])
                        patch.add_data(0x218914, [0x77])
                    if sequence > 0 or mold > 0:
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 273, 15, 0x20f301))
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 277, 15, 0x20f313))
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 275, 15, 0x20f30d))
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 281, 15, 0x20f325))
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 279, 15, 0x20f319))
                        spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 283, 3204, 0x20f32b))
                if location.name == "Punchinello":
                    print(location, shuffled_boss)
                    patch.add_data(0x1dc4b0, calcpointer(sprite, [0x00, 0x48]));
                    #push animations
                    if not freeze and push_sequence is not False:
                        if shuffled_boss.name is "Booster":
                            patch.add_data(0x1dc4b0, calcpointer(502, [0x00, 0x48]));
                            patch.add_data(0x1e6d8b, [0x08, 0x50, 3])
                        else:
                            patch.add_data(0x1e6d8b, [0x08, 0x50, push_sequence])
                    else:
                        patch.add_data(0x1e6d8b, [0x9b, 0x9b, 0x9b])
                    patch.add_data(0x1e6d99, [0xf0, (max(1, push_length - 1))]);
                    patch.add_data(0x1e6da4, [0xf0, (max(1, push_length - 1))]);
                    patch.add_data(0x1e6d90, [0x9b, 0x9b, 0x9b])
                    patch.add_data(0x1e6e04, [0x9b, 0x9b, 0x9b, 0x9b])
                    patch.add_data(0x1e6e1b, [0x9b, 0x9b, 0x9b, 0x9b])
                    patch.add_data(0x1e6e32, [0x9b, 0x9b, 0x9b, 0x9b])
                    sub_sequence = True
                    if sequence == 0 and mold > 0:
                        sub_sequence = False
                    spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 289, 592, 0x20F36b))
                if location.name == "KingCalamari":
                    print(location, shuffled_boss)
                    if (shuffled_boss.name is not "KingCalamari"):
                        patch.add_data(0x1dbc98, calcpointer(sprite, [0x00, 0x28]))
                        patch.add_data(0x214068, 0x9b)
                        patch.add_data(0x214098, 0x9b)
                        patch.add_data(0x21409D, 0x9b)
                        patch.add_data(0x214076, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x21407b, [0x9b, 0x9b, 0x9b])
                        if sequence > 0:
                            sub_sequence = True
                            patch.add_data(0x21406c, [0x08, 0x50 + plus, sequence])
                        elif mold > 0:
                            sub_sequence = False
                            patch.add_data(0x21406c, [0x08, 0x58 + plus, mold])
                        spritePhaseEvents.append(SpritePhaseEvent(7, plus, mold, sub_sequence, sequence, False, 177, 3224, 0x20eef1))
                if location.name == "Booster":
                    print(location, shuffled_boss)
                    if (shuffled_boss.name is not "Booster"):
                        #replace sprite for npc 50
                        if freeze or sesw_only:
                            patch.add_data(0x1db95e, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1db95e, calcpointer(sprite, [0x00, 0x00]))
                        #was gonna replace snifits too for axems + culex's sidekicks, but they are cloned + it wouldnt work
                        #only do it for clerk, manager, director, croco, mack, bowyer, punchinello, johnny, megasmilax, czar dragon
                        if shuffled_boss.name in ["Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon"]:
                            patch.add_data(0x1dc5c8, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x20]))
                            #tower
                            patch.add_data(0x1ee8b4, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b3d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b42, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b47, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b4d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b52, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b57, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x216b5c, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ee8ff, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ee98e, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ee9d7, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eea69, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eea7a, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeae0, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeaef, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeb5b, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeb6b, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eebe3, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eec02, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eec16, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeca5, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eecad, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eed16, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eed28, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eed91, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eeda3, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eee78, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eee7f, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eee86, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eef0d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eef1d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eef2d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eefc0, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eefc5, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1eefca, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef05d, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef062, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef067, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef0fa, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef109, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef10e, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef11a, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef11f, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef12b, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef1e0, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef1fe, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef217, [0x9b, 0x9b, 0x9b])
                        if freeze: #never change directions
                            #portrait room
                            patch.add_data(0x1ee055, 0x9b)
                            patch.add_data(0x1ee073, 0x9b)
                            #tower
                            patch.add_data(0x1ed899, 0x9b)
                            patch.add_data(0x1ee4ce, 0x9b)
                            patch.add_data(0x1ee4d4, 0x9b)
                            patch.add_data(0x1ee541, 0x9b)
                            patch.add_data(0x1ee6c9, 0x9b)
                            patch.add_data(0x1eea36, 0x9b)
                            patch.add_data(0x1ef2bc, 0x9b)
                            patch.add_data(0x1ef2f2, 0x9b)
                            patch.add_data(0x1ef35c, 0x9b)
                            patch.add_data(0x1ef360, 0x9b)
                            patch.add_data(0x1ef3f7, 0x9b)
                            patch.add_data(0x1ef431, 0x9b)
                            patch.add_data(0x1ef4dd, 0x9b)
                            patch.add_data(0x1ef5be, 0x9b)
                            patch.add_data(0x1ef509, 0x9b)
                            #marrymore
                            patch.add_data(0x20d5d3, 0x9b)
                            patch.add_data(0x20d5fe, 0x9b)
                            patch.add_data(0x20d6fe, 0x9b)
                        sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            #tower
                            patch.add_data(0x1ed89a, 0x9b)
                            patch.add_data(0x1ef2fa, 0x9b)
                            patch.add_data(0x1ef35a, 0x9b)
                        if freeze or (not sub_sequence and mold > 0): #dont reset properties
                            #portrait room
                            patch.add_data(0x1ee090, 0x9b)
                            #tower
                            patch.add_data(0x1ee550, 0x9b)
                            patch.add_data(0x1ef2bb, 0x9b)
                            patch.add_data(0x1ef2f1, 0x9b)
                            patch.add_data(0x1ef35b, 0x9b)
                            patch.add_data(0x1ef37e, 0x9b)
                            patch.add_data(0x1ef3f6, 0x9b)
                            patch.add_data(0x1ef5b7, 0x9b)
                            patch.add_data(0x1ef4f5, 0x9b)
                            #marrymore
                            patch.add_data(0x20d6fc, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            #portrait room
                            patch.add_data(0x1ee055, 0x77)
                            patch.add_data(0x1ee073, 0x75)
                            #tower
                            patch.add_data(0x1ed899, 0x75)
                            patch.add_data(0x1ee4d4, 0x71)
                            patch.add_data(0x1ee541, 0x75)
                            patch.add_data(0x1ee6c9, 0x73)
                            patch.add_data(0x1ef2bc, 0x73)
                            patch.add_data(0x1ef2f2, 0x73)
                            patch.add_data(0x1ef35c, 0x73)
                            patch.add_data(0x1ef360, 0x77)
                            patch.add_data(0x1ef3f7, 0x73)
                            patch.add_data(0x1ef431, 0x77)
                            patch.add_data(0x1ef4dd, 0x73)
                            patch.add_data(0x1ef5be, 0x75)
                            patch.add_data(0x1ef509, 0x75)
                            #marrymore
                            patch.add_data(0x20d5d3, 0x71)
                            patch.add_data(0x20d5fe, 0x75)
                            patch.add_data(0x20d6fe, 0x71)
                        #portrait room
                        patch.add_data(0x1ee078, [0x9b, 0x9b, 0x9b])
                        #tower
                        patch.add_data(0x1ef2c9, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1ef2ce, [0x9b, 0x9b, 0x9b])
                        #special animations
                        if not freeze:
                            if extra_sequence is not False:
                                #tower
                                patch.add_data(0x1ee54b, [0x08, 0x40, 0x80 + extra_sequence])
                                patch.add_data(0x1ef379, [0x08, 0x40, 0x80 + extra_sequence])
                                patch.add_data(0x1ef38e, [0x08, 0x40, 0x80 + extra_sequence])
                                #marrymore
                                patch.add_data(0x20d625, [0x08, 0x40, 0x80 + extra_sequence])
                            else:
                                #tower
                                patch.add_data(0x1ee54b, [0x08, 0x40 + plus, 0x80 + sequence])
                                patch.add_data(0x1ef379, [0x08, 0x40 + plus, 0x80 + sequence])
                                patch.add_data(0x1ef38e, [0x08, 0x40 + plus, 0x80 + sequence])
                                #marrymore
                                patch.add_data(0x20d625, [0x77, 0x9b, 0x9b])
                        else:
                            #tower
                            patch.add_data(0x1ee54b, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef379, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1ef38e, [0x9b, 0x9b, 0x9b])
                            #marrymore
                            patch.add_data(0x20d625, [0x9b, 0x9b, 0x9b])
                        #exception for marrymore sprite
                        if freeze or sesw_only or not northeast_mold:
                            patch.add_data(0x20d31b, [0x9b, 0x9b, 0x9b])
                        else:
                            if dont_reverse_northeast:
                                patch.add_data(0x20d31b, [0x08, 0x48, northeast_mold])
                            else:
                                patch.add_data(0x20d31b, [0x08, 0x48, 0x80 + northeast_mold])
                        #preload sprite form if needed
                        if sequence > 0 or mold > 0:
                            #tower
                            spritePhaseEvents.append(SpritePhaseEvent([0, 7], plus, mold, sub_sequence, sequence, False, 192, 1359, 0x20efad))
                            # marrymore
                            spritePhaseEvents.append(SpritePhaseEvent(15, plus, mold, sub_sequence, sequence, False, 154, 600, 0x20edc7))
                            # portrait room
                            spritePhaseEvents.append(SpritePhaseEvent(6, plus, mold, sub_sequence, sequence, False, 195, 1339, 0x20efe4))
                            # stair room
                            spritePhaseEvents.append(SpritePhaseEvent(6, plus, mold, sub_sequence, sequence, False, 193, 15, 0x20efce))
        #set sprite molds and sequences where necessary
        if len(spritePhaseEvents) > 0:
            patch.add_data(0x20ab6f, 0xC3)
            start_instructions = 0x20ab70
            shortened_start_instructions = 0xab70
            append_jumps = []
            total_jump_length = len(spritePhaseEvents) * 5
            current_length_of_npc_code = 0
            for event in spritePhaseEvents:
                patch.add_data(event.original_event_location, calcpointer(3727))
                append_jumps.append(0xe2)
                append_jumps.extend(calcpointer(event.level))
                append_jumps.extend(calcpointer(shortened_start_instructions + total_jump_length + current_length_of_npc_code))
                current_length_of_npc_code += len(event.generate_code())
            for event in spritePhaseEvents:
                append_jumps.extend(event.generate_code())
            patch.add_data(start_instructions, append_jumps)




        # Choose character for the file select screen.
        i = cursor_id
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

    @property
    def spoiler(self):
        """

        Returns:
            dict: Spoiler for current game world state in JSON object form (Python dictionary).

        """
        # TODO: Build spoilers that are in all modes first.
        spoiler = {}

        # TODO: Open mode only spoilers.
        if self.open_mode:
            spoiler['Boss Locations'] = bosses.get_spoiler(self)

        return spoiler
