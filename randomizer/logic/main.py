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

    def generate_code_culex(self):

        for i in range(len(self.npc)):
            returnBytes = [];
            returnBytes.extend([(0x14 + self.npc[i]), 0x83])
            if not self.reverse[i]:
                returnBytes.extend([0x08, 0x40 + self.sprite, self.sequence[i]])
            else:
                returnBytes.extend([0x08, 0x40 + self.sprite, 0x80 + self.sequence[i]])
        returnBytes.append(0xD0)
        eventpointer = calcpointer(self.original_event)
        returnBytes.extend(eventpointer)
        returnBytes.append(0xFE)
        return returnBytes

    def generate_code(self):
        returnBytes = [];
        if not isinstance(self.npc, list):
            npcs = [];
            npcs.append(self.npc)
        else:
            npcs = self.npc
        for npc in npcs:
            rb = [];
            if self.is_sequence_and_not_mold and not self.reverse:
                rb.extend([0x08, 0x40 + self.sprite, self.sequence])
            elif self.is_sequence_and_not_mold and self.reverse:
                rb.extend([0x08, 0x40 + self.sprite, 0x80 + self.sequence])
            elif not self.is_sequence_and_not_mold and not self.reverse:
                rb.extend([0x08, 0x08 + self.sprite, self.mold])
            elif not self.is_sequence_and_not_mold and self.reverse:
                rb.extend([0x08, 0x08 + self.sprite, 0x80 + self.mold])
            initial_bytes = [(0x14 + npc), 0x80 + len(rb)]
            initial_bytes.extend(rb)
            returnBytes.extend(initial_bytes)
        returnBytes.append(0xD0)
        eventpointer = calcpointer(self.original_event)
        returnBytes.extend(eventpointer)
        returnBytes.append(0xFE)
        return returnBytes

    def export_sprite_load(self):
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
        return returnBytes

    def export_sprite_sequence(self):
        returnBytes = [];
        if not isinstance(self.npc, list):
            npcs = [];
            npcs.append(self.npc)
        else:
            npcs = self.npc
        for npc in npcs:
            if self.is_sequence_and_not_mold and not self.reverse:
                returnBytes.extend([0x08, 0x40 + self.sprite, self.sequence])
            elif self.is_sequence_and_not_mold and self.reverse:
                returnBytes.extend([0x08, 0x40 + self.sprite, 0x80 + self.sequence])
            elif not self.is_sequence_and_not_mold and not self.reverse:
                returnBytes.extend([0x08, 0x08 + self.sprite, self.mold])
            elif not self.is_sequence_and_not_mold and self.reverse:
                returnBytes.extend([0x08, 0x08 + self.sprite, 0x80 + self.mold])
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
                #replace overworld characters in recruitment spots - there are no partitions identical to 89 that have CBC set to 3 instead of 4, so modify 89 since it's only used by this room
                if self.settings.is_flag_enabled(flags.NoFreeCharacters) and dialogue_iterator == 2:
                    #mushroom way
                    patch.add_data(0x14b3BC, character.mway_1_npc_id)
                    patch.add_data(0x14b411, character.mway_2_npc_id)
                    patch.add_data(0x14b452, character.mway_3_npc_id)
                    #change partition to accommodate mallow's sprite in mway
                    if character.name is "Mallow":
                        patch.add_data(0x1ddf67, 0x80)
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
                    patch.add_data(0x148f91, character.forest_maze_sprite_id)
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
                            #booster hill
                            patch.add_data(0x207147, [0x08, 0x43, 0x89])
                            patch.add_data(0x20714E, [0x08, 0x43, 0x09])
                            patch.add_data(0x207160, [0x08, 0x43, 0x89])
                            patch.add_data(0x207165, [0x08, 0x43, 0x88])
                            patch.add_data(0x206b1a, [0x08, 0x43, 0x88])
                            patch.add_data(0x206d19, [0x08, 0x43, 0x89])
                            patch.add_data(0x206d20, [0x08, 0x43, 0x09])
                            patch.add_data(0x206d34, [0x08, 0x43, 0x89])
                            patch.add_data(0x206d39, [0x08, 0x43, 0x88])
                        else:
                            #surprised
                            patch.add_data(0x20d338, [0x08, 0x42, 0x00])
                            patch.add_data(0x20d48c, [0x08, 0x42, 0x00])
                            #surprised reversed
                            patch.add_data(0x20d5d8, [0x08, 0x42, 0x80])
                            #sitting
                            patch.add_data(0x20d43b, [0x08, 0x49, 0x1f])
                            #booster hill
                            patch.add_data(0x207147, [0x08, 0x42, 0x09])
                            patch.add_data(0x20714E, [0x08, 0x42, 0x89])
                            patch.add_data(0x207160, [0x08, 0x42, 0x09])
                            patch.add_data(0x207165, [0x08, 0x42, 0x88])
                            patch.add_data(0x206b1a, [0x08, 0x42, 0x88])
                            patch.add_data(0x206d19, [0x08, 0x42, 0x09])
                            patch.add_data(0x206d20, [0x08, 0x42, 0x89])
                            patch.add_data(0x206d34, [0x08, 0x42, 0x09])
                            patch.add_data(0x206d39, [0x08, 0x42, 0x88])
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
                                  "MegaSmilax", "Dodo", "Valentina", "Magikoopa", "Boomer", "CzarDragon", "AxemRangers",
                                  "Countdown", "Clerk", "Manager", "Director", "Gunyolk"]):
                for enemy in location.pack.common_enemies:
                    if enemy.overworld_sprite is not None:
                        shuffled_boss = enemy
                if (location.name is not "Gunyolk" and (approximate_dimension(shuffled_boss.sprite_height) <= approximate_dimension(location.sprite_height) and approximate_dimension(shuffled_boss.sprite_width) <= approximate_dimension(location.sprite_width)) or location.name in ["Belome1", "Belome2", "Dodo"]):
                    sprite = shuffled_boss.battle_sprite
                    mold = shuffled_boss.battle_mold
                    sequence = shuffled_boss.battle_sequence
                    plus = shuffled_boss.battle_sprite_plus
                    freeze = shuffled_boss.battle_freeze
                    sesw_only = shuffled_boss.battle_sesw_only
                    invert_se_sw = shuffled_boss.battle_invert_se_sw
                    extra_sequence = shuffled_boss.battle_extra_sequence
                    push_sequence = shuffled_boss.battle_push_sequence
                    push_length = shuffled_boss.battle_push_length
                    northeast_mold = shuffled_boss.battle_northeast_mold
                    dont_reverse_northeast = False
                    if shuffled_boss.battle_sprite == shuffled_boss.overworld_sprite:
                        overworld_is_skinny = shuffled_boss.overworld_is_skinny
                    else:
                        overworld_is_skinny = False
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
                    overworld_is_skinny = shuffled_boss.overworld_is_skinny

                bank_1e_scarecrow_queues = []
                bank_1e_scarecrow_addresses = []
                bank_1f_scarecrow_queues = []
                bank_1f_scarecrow_addresses = []
                bank_20_scarecrow_queues = []
                bank_20_scarecrow_addresses = []
                bank_21_scarecrow_queues = []
                bank_21_scarecrow_addresses = []
                scarecrow_face_northwest = [0x08, 0x40, 0x80]
                scarecrow_face_northeast = [0x08, 0x40, 0x00]
                scarecrow_face_southwest = [0x08, 0x40, 0x01]
                scarecrow_face_southeast = [0x08, 0x40, 0x81]

                def add_scarecrow_script(npc, instructions, referencing_address, is_sync):
                    if referencing_address > 0x210000:
                        bank_21_scarecrow_addresses.add(referencing_address)
                        bank_21_scarecrow_queues.add(instructions)
                        #add jump to surrogate action in main action, do important actions, jump back to next address in main action
                    else:
                        if is_sync:
                            script_to_add = [0x14 + npc, len(instructions)]
                        else:
                            script_to_add = [0x14 + npc, 0x80 + len(instructions)]
                        script_to_add.extend(instructions)
                        script_to_add.append(0xFE)
                        if referencing_address > 0x200000:
                            bank_20_scarecrow_queues.add(script_to_add)
                            bank_20_scarecrow_addresses.add(referencing_address)
                        if referencing_address > 0x1f0000:
                            bank_1f_scarecrow_queues.add(script_to_add)
                            bank_1f_scarecrow_addresses.add(referencing_address)
                        if referencing_address > 0x1e0000:
                            bank_1e_scarecrow_queues.add(script_to_add)
                            bank_1e_scarecrow_addresses.add(referencing_address)

                if location.name == "HammerBros":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "HammerBros":
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
                if location.name == "Croco1":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name not in ["Croco1", "Croco2"]:
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
                        if invert_se_sw: #scarecrow needs a special script
                            scarecrow_script = []
                            #play sound, jump, pause
                            scarecrow_script.extend([0xFD, 0x9E, 0x21, 0x7F, 0x60, 0x00, 0xF0, 0x07])
                            #face southwest
                            scarecrow_script.extend(scarecrow_face_southwest)
                            #pause for 8 frames
                            scarecrow_script.extend([0xF0, 0x07])
                            #face northwest
                            scarecrow_script.extend(scarecrow_face_northwest)
                            #sequence looping on
                            scarecrow_script.extend([0x04])
                            add_scarecrow_script(5, scarecrow_script, 0x1f3bda, False)
                        if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                            patch.add_data(0x1f3bb1, [0x9b])
                        # if sesw_only: #dont face another direction
                        #     patch.add_data(0x1f3be7, [0x73]) #face southwest
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
                        if invert_se_sw: #scarecrow needs a special script
                            #####
                            #####first script
                            scarecrow_script = []
                            #clear solidity, play sound jump, pause
                            scarecrow_script.extend([0x0C, 0x04, 0xFD, 0x9E, 0x21, 0x7F, 0x60, 0x00, 0xF0, 0x07])
                            #dont reset
                            scarecrow_script.extend([0x9B])
                            #face southwest
                            scarecrow_script.extend(scarecrow_face_southwest)
                            #pause for 8 frames
                            scarecrow_script.extend([0xF0, 0x07])
                            #face northwest
                            scarecrow_script.extend(scarecrow_face_northwest)
                            add_scarecrow_script(8, scarecrow_script, 0x1f3546, False)
                            #####
                            #####second script
                            scarecrow_script = []
                            #everything before 0x1f356e
                            scarecrow_script.extend([0x04, 0x10, 0xC1, 0x57, 0x02, 0x41, 0x13, 0x03, 0xFD, 0x0F, 0x03])
                            #face northeast
                            scarecrow_script.extend(scarecrow_face_northeast)
                            #everything before 0x1f357d
                            scarecrow_script.extend([0x0B, 0x04, 0xF0, 0x0C, 0xFD, 0x9E, 0x21, 0x7F, 0x90, 0x00, 0x57, 0x04, 0x67, 0x10])
                            #everything else
                            scarecrow_script.extend([0x06, 0xF0, 0x09, 0x60, 0x32, 0xFD, 0x9E, 0x21, 0x7F, 0x50, 0x00, 0x60, 0x28, 0xF0, 0x00, 0xFD, 0x3D, 0x1C, 0x8B, 0x35, 0x10, 0xC1, 0xFD, 0x9E, 0x21, 0x7F, 0x80, 0x00, 0x50, 0x04, 0x01])
                            add_scarecrow_script(8, scarecrow_script, 0x1f3561, True)
                        if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                            patch.add_data(0x1f3552, [0x9b])
                        # if sesw_only: #dont face north
                        #     patch.add_data(0x1f3556, [0x73])  #face southwest
                        #     patch.add_data(0x1f356e, [0x71])  #face southeast
                        # if freeze: #dont face southwest
                        #     patch.add_data(0x1f3553, [0x9b])
                        #     patch.add_data(0x1f357d, [0x9b])
                        #     patch.add_data(0x1f3556, [0x9b])
                        #     patch.add_data(0x1f356e, [0x9b])
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
                        if invert_se_sw: #scarecrow needs a special script
                            scarecrow_script = []
                            #standard script
                            scarecrow_script.extend([0xFD, 0x9E, 0x21, 0x7F, 0x60, 0x00, 0xF0, 0x1D])
                            #dont reset
                            scarecrow_script.extend([0x9B])
                            #face southwest
                            scarecrow_script.extend(scarecrow_face_southwest)
                            add_scarecrow_script(8, scarecrow_script, 0x1f3b86, False)
                            #action script replacements
                            scarecrow_script = []
                            scarecrow_script.extend(scarecrow_face_southwest)
                            scarecrow_script.extend([0xF0, 0x00])
                            add_scarecrow_script(None, scarecrow_script, 0x211ffa, False)
                            scarecrow_script = []
                            scarecrow_script.extend(scarecrow_face_southwest)
                            scarecrow_script.extend([0xF0, 0x00])
                            add_scarecrow_script(None, scarecrow_script, 0x21202b, False)
                            scarecrow_script = []
                            scarecrow_script.extend(scarecrow_face_southeast)
                            scarecrow_script.extend([0xF0, 0x00])
                            add_scarecrow_script(None, scarecrow_script, 0x212059, False)
                        if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                            patch.add_data(0x1f3b90, [0x9b])
                        # if freeze: #dont face another direction
                        #     patch.add_data(0x1f3b91, [0x9b])
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            patch.add_data(0x211fd8, [0x9b])
                            patch.add_data(0x211ff0, [0x9b])
                        # if freeze: #dont face southwest
                        #     patch.add_data(0x211ffa, [0x9b])
                        #     patch.add_data(0x21202b, [0x9b])
                        #     patch.add_data(0x212059, [0x9b])
                        #bandits way 4
                        if sequence > 0 or mold > 0:
                            spritePhaseEvents.append(SpritePhaseEvent(12, plus, mold, sub_sequence, sequence, False, 78, 1698, 0x20e8e6))
                        if invert_se_sw: #scarecrow needs a special script
                            #####script 1
                            scarecrow_script = []
                            scarecrow_script.extend([0xFD, 0x01, 0x00, 0x04, 0x67, 0x01, 0x06, 0x62, 0x08, 0x07])
                            scarecrow_script.extend(scarecrow_face_northeast)
                            add_scarecrow_script(12, scarecrow_script, 0x1f33c4, True)
                            #####script 2
                            scarecrow_script = []
                            scarecrow_script.extend([0xF0, 0x13])
                            scarecrow_script.extend(scarecrow_face_southeast)
                            scarecrow_script.extend([0xF0, 0x07])
                            scarecrow_script.extend(scarecrow_face_southwest)
                            scarecrow_script.extend([0xF0, 0x13, 0x53, 0x03, 0x10, 0x80])
                            add_scarecrow_script(12, scarecrow_script, 0x1f3402, False)
                            #####script 3
                            scarecrow_script = []
                            scarecrow_script.extend([0x10, 0xC1])
                            scarecrow_script.extend(scarecrow_face_southeast)
                            scarecrow_script.extend([0xF0, 0x1D, 0xFD, 0x9E, 0x21, 0x7F, 0x70, 0x00, 0x06, 0x50, 0x04, 0x01])
                            add_scarecrow_script(12, scarecrow_script, 0x1f3410, False)
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            patch.add_data(0x1f33c9, [0x9b])
                            #patch.add_data(0x1f340e, [0x9b])
                        # if sesw_only: #dont face another direction
                        #     patch.add_data(0x1f33d0, [0x71])  #face southeast
                        # if freeze: #dont face southwest
                        #     patch.add_data(0x1f3406, [0x9b])
                        #     patch.add_data(0x1f3409, [0x9b])
                        #     patch.add_data(0x1f3414, [0x9b])
                        #     patch.add_data(0x1f33d0, [0x9b])
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
                            patch.add_data(0x1f39da, [0x77])  #face northeast
                            #####script 1
                            scarecrow_script = []
                            scarecrow_script.extend([0xFD, 0x9E, 0x21, 0x7F, 0x60, 0x00, 0xF0, 0x07])
                            scarecrow_script.extend([0x9b])
                            scarecrow_script.extend(scarecrow_face_southwest)
                            scarecrow_script.extend([0xF0, 0x13])
                            scarecrow_script.extend(scarecrow_face_northwest)
                            add_scarecrow_script(8, scarecrow_script, 0x1f3868, False)
                            #replace "Face Mario" since dont know what direction that will be
                            patch.add_data(0x1f3995, [0x9b])
                            patch.add_data(0x1f39ac, [0x9b])
                            #####script 2
                            scarecrow_script = []
                            scarecrow_script.extend([0x92, 0x0B, 0x73, 0x00])
                            scarecrow_script.extend(scarecrow_face_northeast)
                            scarecrow_script.extend([0x00])
                            add_scarecrow_script(8, scarecrow_script, 0x1f38DE, False)
                            #####script 3
                            scarecrow_script = []
                            scarecrow_script.extend([0x07])
                            scarecrow_script.extend(scarecrow_face_southeast)
                            add_scarecrow_script(8, scarecrow_script, 0x1f39d7, False)
                        if freeze or sequence > 0 or (not sub_sequence and mold > 0): #dont reset properties
                            patch.add_data(0x1f3872, [0x9b])
                        # if sesw_only: #dont face north
                        #     patch.add_data(0x1f3876, [0x73])
                        #     patch.add_data(0x1f38e4, [0x71])  #face southeast
                        # if freeze: #dont face southwest
                        #     patch.add_data(0x1f3873, [0x9b])
                        #     patch.add_data(0x1f3876, [0x9b])
                        #     patch.add_data(0x1f38e4, [0x9b])
                        #     patch.add_data(0x1f39da, [0x9b])
                        #     patch.add_data(0x1f3995, [0x9b])  #face southwest
                        #     patch.add_data(0x1f39ac, [0x9b])  #face southwest
                        #if freeze or (not sub_sequence and mold > 0): #dont loop
                        #    patch.add_data(0x211fc5, [0x9b])
                if location.name == "Mack":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Mack":
                        # reassign NPC 480's sprite
                        patch.add_data(0x1Dc520, calcpointer(sprite, [0x00, 0x68]));
                        #face southwest
                        patch.add_data(0x14ca86, 0x63);
                        #delete sequence init, this can be delegated to spritePhaseEvents if special sequence needs to be loaded
                        patch.add_data(0x1e2921, [0x9b, 0x9b, 0x9b])
                        #for sprites that require a specific mold or sequence, change the room load events to set the proper sequence or mold first
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(3, plus, mold, sub_sequence, sequence, False, 326, 368, 0x20f47d))
                if location.name == "Belome1":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name not in ["Belome1", "Belome2"]:
                        # use npc 371, set properties to match belome's
                        patch.add_data(0x14c67a, [0xcd, 0x05]);
                        # replace its sprite
                        patch.add_data(0x1Dc225, calcpointer(sprite, [0x00, 0xA8]));
                        patch.add_data(0x1Dc227, [0x60, 0x02, 0xaa, 0x12, 0x00]);
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(3, plus, mold, sub_sequence, sequence, False, 302, 3135, 0x20f3be))
                if location.name == "Bowyer":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Bowyer":
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
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name not in ["Croco1", "Croco2"]:
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
                        patch.add_data(0x1Dc20b, [0x80, 0x22, 0x55, 0x2a]);
                        #change partitions for small sprites
                        if overworld_is_skinny:
                            #area 4 - modify partition 53
                            patch.add_data(0x1DDED5, 0x81)
                            #area 5 and 7 - reconfigure and use partition 2
                            patch.add_data(0x14c33a, 0x02)
                            patch.add_data(0x14c3e2, 0x02)
                            patch.add_data(0x1dde08, [0xB1, 0x81, 0x80, 0x80]);
                            #area 6 and 8 can use partition 60, it meets its needs when a small sprite is on croco
                            patch.add_data(0x14c2fc, 0x3c)
                            patch.add_data(0x14c394, 0x3c)
                            #area 9 - reconfigure and use partition 1
                            patch.add_data(0x14c444, 0x01)
                            patch.add_data(0x1dde04, [0xB2, 0x81, 0x80, 0x80]);
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
                        # if freeze: #dont do directional commands
                        #     patch.add_data(0x21886f, [0x9b])
                        #     patch.add_data(0x218b41, [0x9b])
                        #     patch.add_data(0x218ab7, [0x9b])
                        #     patch.add_data(0x218a27, [0x9b])
                        #     patch.add_data(0x218a37, [0x9b])
                        #     patch.add_data(0x218a3a, [0x9b])
                        #     patch.add_data(0x21899D, [0x9b])
                        #     patch.add_data(0x218905, [0x9b])
                        #     patch.add_data(0x218914, [0x9b])
                        # if sesw_only: #dont face north
                        #     patch.add_data(0x218a37, [0x73])
                        #     patch.add_data(0x21899D, [0x73])
                        #     patch.add_data(0x218905, [0x71])
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
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Punchinello":
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
                    print(location.name + ": " + shuffled_boss.name)
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
                    print(location.name + ": " + shuffled_boss.name)
                    if (shuffled_boss.name is not "Booster"):
                        #fix marrymore if fat sprite is used
                        if not overworld_is_skinny:
                            #chapel
                            patch.add_data(0x14a8c9, 0x29)
                        #replace sprite for npc 50
                        if freeze or sesw_only:
                            patch.add_data(0x1db95e, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1db95e, calcpointer(sprite, [0x00, 0x00]))
                        #was gonna replace snifits too for axems + culex's sidekicks, but they are cloned + it wouldnt work
                        #only do it for clerk, manager, director, croco, mack, bowyer, punchinello, johnny, megasmilax, czar dragon
                        if shuffled_boss.name in ["Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x1dc5c8, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x20]))
                            patch.add_data(0x1db8fc, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x00]))
                            #tower
                            patch.add_data(0x1ee8b4, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b3d, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b42, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b47, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b4d, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b52, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b57, [0x75, 0x75, 0x75])
                            patch.add_data(0x216b5c, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ee8ff, [0x75, 0x75, 0x75])
                            patch.add_data(0x1EE947, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ee98e, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ee9d7, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eea69, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eea7a, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeae0, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeaef, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeb5b, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeb6b, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eebe3, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eec02, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eec16, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeca5, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eecad, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eed16, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eed28, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eed91, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eeda3, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eee78, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eee7f, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eee86, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eef0d, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eef1d, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eef2d, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eefc0, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eefc5, [0x75, 0x75, 0x75])
                            patch.add_data(0x1eefca, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef05d, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef062, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef067, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef0fa, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef109, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef10e, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef11a, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef11f, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef12b, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef1e0, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef1fe, [0x75, 0x75, 0x75])
                            patch.add_data(0x1ef217, [0x75, 0x75, 0x75])
                        # if freeze or sequence > 0 or mold > 0: #never change directions
                        #     patch.add_data(0x14a93f, 0x40)
                        #     #portrait room
                        #     patch.add_data(0x1ee055, 0x9b)
                        #     patch.add_data(0x1ee073, 0x9b)
                        #     #tower
                        #     patch.add_data(0x1ed899, 0x9b)
                        #     patch.add_data(0x1ee4d4, 0x9b)
                        #     patch.add_data(0x1ee541, 0x9b)
                        #     patch.add_data(0x1ee6c9, 0x9b)
                        #     patch.add_data(0x1eea39, 0x9b)
                        #     patch.add_data(0x1ef2bc, 0x9b)
                        #     patch.add_data(0x1ef2f2, 0x9b)
                        #     patch.add_data(0x1ef35c, 0x9b)
                        #     patch.add_data(0x1ef360, 0x9b)
                        #     patch.add_data(0x1ef3f7, 0x9b)
                        #     patch.add_data(0x1ef431, 0x9b)
                        #     patch.add_data(0x1ef4dd, 0x9b)
                        #     patch.add_data(0x1ef5be, 0x9b)
                        #     patch.add_data(0x1ef509, 0x9b)
                        #     #marrymore
                        #     patch.add_data(0x20d5d3, 0x9b)
                        #     patch.add_data(0x20d5fe, 0x9b)
                        #     patch.add_data(0x20d6fe, 0x9b)
                        #     #booster hill
                        #     patch.add_data(0x207158, 0x9b)
                        #     patch.add_data(0x20715B, 0x9b)
                        #     patch.add_data(0x20716E, 0x9b)
                        #     patch.add_data(0x207171, 0x9b)
                        #     patch.add_data(0x206d2b, 0x9b)
                        #     patch.add_data(0x206d2e, 0x9b)
                        #     patch.add_data(0x206d44, 0x9b)
                        #     patch.add_data(0x206d47, 0x9b)
                        sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            #tower
                            patch.add_data(0x1ed89a, 0x9b)
                            patch.add_data(0x1ef2fa, 0x9b)
                            patch.add_data(0x1ef35a, 0x9b)
                            #booster hill
                            patch.add_data(0x206b58, 0x9b)
                            patch.add_data(0x206b64, 0x9b)
                        if freeze or sequence > 0 or mold > 0: #dont reset properties
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
                            #booster hill
                            patch.add_data(0x211fc5, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            #portrait room
                            patch.add_data(0x1ee055, 0x77)
                            patch.add_data(0x1ee073, 0x75)
                            #tower
                            patch.add_data(0x1ed899, 0x75)
                            patch.add_data(0x1ee4d4, 0x71)
                            patch.add_data(0x1ee541, 0x75)
                            patch.add_data(0x1ee6c9, 0x73)
                            patch.add_data(0x1eea39, 0x73)
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
                            #booster hill
                            patch.add_data(0x207158, 0x75)
                            patch.add_data(0x20715B, 0x77)
                            patch.add_data(0x20716E, 0x75)
                            patch.add_data(0x207171, 0x73)
                            patch.add_data(0x206d2b, 0x75)
                            patch.add_data(0x206d2e, 0x77)
                            patch.add_data(0x206d44, 0x75)
                            patch.add_data(0x206d47, 0x73)
                        #portrait room
                        patch.add_data(0x1ee078, [0x9b, 0x9b, 0x9b])
                        #tower
                        patch.add_data(0x1ef2c9, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1ef2ce, [0x9b, 0x9b, 0x9b])
                        #shovel knight enemies have weird sprite layouts
                        #unsure if this is still necessary - im commenting it out since i made their sequences match everyone elses
                        # if dont_reverse_northeast:
                        #     patch.add_data(0x14a93f, 0x40)
                        #     patch.add_data(0x20d6fc, 0x9b)
                        #     patch.add_data(0x20d6fe, 0x9b)
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
                        if sequence > 0:
                            patch.add_data(0x1ee4cc, [0x08, 0x40 + plus, sequence])
                            patch.add_data(0x1ef4d5, [(0x14 + 7), 0x83, 0x08, 0x40 + plus, sequence])
                        elif mold > 0:
                            patch.add_data(0x1ee4cc, [0x08, 0x08 + plus, mold])
                            patch.add_data(0x1ef4d5, [(0x14 + 7), 0x83, 0x08, 0x08 + plus, mold])
                        elif freeze:
                            patch.add_data(0x1ee4ce, 0x9b)
                        if sequence > 0 or mold > 0:
                            #tower
                            spritePhaseEvents.append(SpritePhaseEvent([0, 7], plus, mold, sub_sequence, sequence, False, 192, 1359, 0x20efad))
                            # marrymore
                            spritePhaseEvents.append(SpritePhaseEvent(15, plus, mold, sub_sequence, sequence, False, 154, 600, 0x20edc7))
                            # portrait room
                            spritePhaseEvents.append(SpritePhaseEvent(6, plus, mold, sub_sequence, sequence, False, 195, 1339, 0x20efe4))
                            # stair room
                            spritePhaseEvents.append(SpritePhaseEvent(6, plus, mold, sub_sequence, sequence, False, 193, 15, 0x20efce))
                            # booster hill
                            spritePhaseEvents.append(SpritePhaseEvent(7, plus, mold, sub_sequence, sequence, False, 54, 3499, 0x20e74f))
                if location.name == "Johnny":
                    print(location.name + ": " + shuffled_boss.name)
                    if (shuffled_boss.name is not "Johnny"):
                        #replace sprite for npc 52
                        if freeze or sesw_only:
                            patch.add_data(0x1db96c, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1db96c, calcpointer(sprite, [0x00, 0x00]))
                        # these bosses will have someone replace bandana blues
                        if shuffled_boss.name in ["Booster", "Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Booster", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x1dc10d, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x20]))
                        # if freeze: #never change directions
                        #     patch.add_data(0x203873, 0x9b)
                        sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            patch.add_data(0x213faa, 0x9b)
                            patch.add_data(0x213fb2, 0x9b)
                        if freeze or sequence > 0 or mold > 0: #dont reset properties
                            patch.add_data(0x213fb1, 0x9b)
                            patch.add_data(0x203871, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            patch.add_data(0x203873, 0x73)
                        #preload sprite form if needed
                        patch.add_data(0x213FA7, [0x9b, 0x9b, 0x9b])
                        if sequence > 0 or mold > 0:
                            spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, False, 28, 3282, 0x20E586))
                if location.name == "Belome2":
                    # replace belome's sprite
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name not in ["Belome1", "Belome2"]:
                        patch.add_data(0x1Dc471, calcpointer(sprite, [0x00, 0xA8]))
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(4, plus, mold, sub_sequence, sequence, False, 268, 1771, 0x20f2e6))
                if location.name == "Jagger":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Jagger":
                        # replace jagger's sprite
                        if freeze or sesw_only:
                            patch.add_data(0x1Dbc44, calcpointer(sprite, [0x00, 0x28]))
                        else:
                            patch.add_data(0x1Dbc44, calcpointer(sprite, [0x00, 0x20]))
                        # if freeze or sequence > 0 or mold > 0: #never change directions
                        #     patch.add_data(0x14be67, 0x40)
                        #     sub_sequence = True
                        #     patch.add_data(0x1f6bb9, 0x9b)
                        #     patch.add_data(0x1f6bc6, 0x9b)
                        #     patch.add_data(0x1f6bcf, 0x9b)
                        #     patch.add_data(0x1f6be0, 0x9b)
                        #     patch.add_data(0x1f6c00, 0x9b)
                        #     patch.add_data(0x1f6c7b, 0x9b)
                        #     patch.add_data(0x1f6cc2, 0x9b)
                        #     patch.add_data(0x1f6d18, 0x9b)
                        #     patch.add_data(0x1f6d29, 0x9b)
                        #     patch.add_data(0x1f6f4c, 0x9b)
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        #if freeze or (not sub_sequence and mold > 0): #dont loop
                        if freeze or sequence > 0 or mold > 0: #dont reset properties
                            patch.add_data(0x1f6c0a, 0x9b)
                            patch.add_data(0x1f6c2f, 0x9b)
                            patch.add_data(0x1f6cc1, 0x9b)
                            patch.add_data(0x1f6d17, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            patch.add_data(0x1f6bb9, 0x71)
                            patch.add_data(0x1f6bc6, 0x75)
                            patch.add_data(0x1f6bcf, 0x77)
                            patch.add_data(0x1f6be0, 0x75)
                            patch.add_data(0x1f6c00, 0x75)
                            patch.add_data(0x1f6c7b, 0x75)
                            patch.add_data(0x1f6cc2, 0x75)
                            patch.add_data(0x1f6d20, 0x71)
                            patch.add_data(0x1f6d29, 0x77)
                            patch.add_data(0x1f6f4c, 0x75)
                        #if dont_reverse_northeast: #factory clerks
                        #special animations
                        if not freeze:
                            if push_sequence is not False:
                                patch.add_data(0x1f6c8c, [0x08, 0x50, push_sequence])
                            else:
                                patch.add_data(0x1f6c8c, [0x08, 0x50, sequence])
                            if extra_sequence is not False:
                                patch.add_data(0x1f6d12, [0x08, 0x40, extra_sequence])
                            else:
                                patch.add_data(0x1f6d12, [0x9b,0x9b, 0x9b])
                        else:
                            patch.add_data(0x1f6c8c, [0x9b,0x9b, 0x9b])
                            patch.add_data(0x1f6d12, [0x9b,0x9b, 0x9b])
                        #remove sfx
                        patch.add_data(0x1f6c8a, [0x9b, 0x9b])
                        patch.add_data(0x1f6c05, [0x9b, 0x9b, 0x9b])
                        #If Jinx needs preloading, do it now
                        for l in self.boss_locations:
                            if (l.name in ["HammerBros", "Croco1", "Mack", "Belome1", "Bowyer", "Croco2",
                                                  "Punchinello", "KingCalamari",
                                                  "Booster", "Johnny", "Belome2", "Jagger", "Jinx3",
                                                  "Megasmilax", "Dodo", "Valentina", "Magikoopa", "Boomer",
                                                  "CzarDragon", "AxemRangers",
                                                  "Countdown", "Clerk", "Manager", "Director", "Gunyolk"]):
                                for e in l.pack.common_enemies:
                                    if e.overworld_sprite is not None:
                                        if l.name is "Jinx3" and e.name is not "Jinx3":
                                            if e.overworld_sequence > 0 or e.overworld_mold > 0:
                                                if e.overworld_sequence > 0:
                                                    patch.add_data(0x1f6c5e, [0x14, 0x86, 0x08, 0x40 + e.overworld_sprite_plus, e.overworld_sequence, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                                                elif e.overworld_mold > 0:
                                                    patch.add_data(0x1f6c5e, [0x14, 0x86, 0x08, 0x08 + e.overworld_sprite_plus, e.overworld_mold, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(1, plus, mold, sub_sequence, sequence, False, 255, 2064, 0x20f2a1))
                if location.name == "Jinx3":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name not in ["Jinx1", "Jinx2", "Jinx3"]:
                        if freeze or sesw_only:
                            patch.add_data(0x1Dbda9, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1Dbda9, calcpointer(sprite, [0x00, 0x00]))
                        # if freeze or sequence > 0 or mold > 0: #never change directions
                        #     patch.add_data(0x14be5b, 0x40)
                        #     sub_sequence = True
                        #     patch.add_data(0x1f6bd7, 0x9b)
                        #     patch.add_data(0x1f6bea, 0x9b)
                        #     patch.add_data(0x1f6cba, 0x9b)
                        #     patch.add_data(0x1f6d30, 0x9b)
                        #     patch.add_data(0x1f6d82, 0x9b)
                        #     patch.add_data(0x1f6d9b, 0x9b)
                        #     patch.add_data(0x1f6dc2, 0x9b)
                        #     patch.add_data(0x1f6dd8, 0x9b)
                        #     patch.add_data(0x1f6deb, 0x9b)
                        #     patch.add_data(0x1f6e19, 0x9b)
                        #     patch.add_data(0x1f6eb9, 0x9b)
                        #     patch.add_data(0x1f6f37, 0x9b)
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        #if freeze or (not sub_sequence and mold > 0): #dont loop
                        if freeze or sequence > 0 or mold > 0: #dont reset properties
                            patch.add_data(0x1f6d50, 0x9b)
                            patch.add_data(0x1f6eb8, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            patch.add_data(0x1f6bd7, 0x75)
                            patch.add_data(0x1f6bea, 0x75)
                            patch.add_data(0x1f6cba, 0x75)
                            patch.add_data(0x1f6d30, 0x77)
                            patch.add_data(0x1f6d82, 0x71)
                            patch.add_data(0x1f6d9b, 0x71)
                            patch.add_data(0x1f6dc2, 0x77)
                            patch.add_data(0x1f6dd8, 0x75)
                            patch.add_data(0x1f6deb, 0x75)
                            patch.add_data(0x1f6e19, 0x75)
                            patch.add_data(0x1f6eb9, 0x75)
                            patch.add_data(0x1f6f37, 0x75)
                        #if dont_reverse_northeast: #factory clerks
                        #special animations
                        if not freeze:
                            if push_sequence is not False:
                                patch.add_data(0x1f6e69, [0x08, 0x50, push_sequence])
                            else:
                                patch.add_data(0x1f6e69, [0x08, 0x50, sequence])
                        else:
                            patch.add_data(0x1f6e69, [0x9b, 0x9b, 0x9b])
                if location.name == "MegaSmilax":
                    #maybe bring shy away back for added comedy
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "MegaSmilax":
                        # use npc 154, set properties to match smilax's
                        #fix scripts
                        patch.add_data(0x14be2c, [0x6B, 0xF2, 0xC0, 0xFC, 0x69, 0x00, 0x9B, 0x46, 0x61, 0x00, 0x40, 0x50, 0x2B, 0xF7, 0xC0, 0xFC, 0x09, 0x00, 0x1B])
                        patch.add_data(0x1dbc36, calcpointer(sprite, [0x00, 0x08]))
                        patch.add_data(0x1dbc38, [0x80, 0x81, 0x44, 0x07])
                        patch.add_data(0x1fdb24, [0x15, 0xF9])
                        patch.add_data(0x1fdb26, [0x16, 0xF9])
                        patch.add_data(0x1fdb3b, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fdb2d, [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 254, 2555, 0x20f299))
                            patch.add_data(0x1fdb28, SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 254, 2555, 0x20f299).export_sprite_load())
                        else:
                            patch.add_data(0x1fdb28, [0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                if location.name == "Dodo":
                    #always replace npc sprite here, it's normally just the feather
                    print(location.name + ": " + shuffled_boss.name)
                    #load dodo in save room if you won statue game
                    patch.add_data(0x1f759f, SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, True, 112, 2108, 0x20eb0f).export_sprite_sequence())
                    patch.add_data(0x1dbb95, calcpointer(sprite, [0x00, 0x88]))
                if location.name == "Valentina":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Valentina":
                        if freeze or sesw_only:
                            patch.add_data(0x1db988, calcpointer(sprite, [0x00, 0x08]))
                            #patch.add_data(0x1db9b9, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1db988, calcpointer(sprite, [0x00, 0x00]))
                            #patch.add_data(0x1db9b9, calcpointer(sprite, [0x00, 0x00]))
                        # if freeze or sequence > 0 or mold > 0: #never change directions
                        #     sub_sequence = True
                        #     patch.add_data(0x1ea3e2, 0x9b)
                        #     patch.add_data(0x1ea515, 0x9b)
                        #     patch.add_data(0x1ea405, 0x9b)
                        #     patch.add_data(0x1ea428, 0x9b)
                        #     patch.add_data(0x1ea434, 0x9b)
                        #     patch.add_data(0x1ea443, 0x9b)
                        #     patch.add_data(0x1ea44c, 0x9b)
                        #     patch.add_data(0x1ea42b, 0x9b)
                        #     patch.add_data(0x1ea43a, 0x9b)
                        #     patch.add_data(0x1ea449, 0x9b)
                        #     patch.add_data(0x1ea452, 0x9b)
                        #     patch.add_data(0x1ea512, 0x9b)
                        #     patch.add_data(0x1ea524, 0x9b)
                        #     patch.add_data(0x1ea595, 0x9b)
                        #     patch.add_data(0x1ea5a7, 0x9b)
                        #     patch.add_data(0x1ea42e, 0x9b)
                        #     patch.add_data(0x1ea437, 0x9b)
                        #     patch.add_data(0x1ea43d, 0x9b)
                        #     patch.add_data(0x1ea437, 0x9b)
                        #     patch.add_data(0x1ea446, 0x9b)
                        #     patch.add_data(0x1ea44f, 0x9b)
                        #     patch.add_data(0x1ea458, 0x9b)
                        #     patch.add_data(0x1ea518, 0x9b)
                        #     patch.add_data(0x1ea573, 0x9b)
                        #     patch.add_data(0x1ea59d, 0x9b)
                        #     patch.add_data(0x1ea431, 0x9b)
                        #     patch.add_data(0x1ea440, 0x9b)
                        #     patch.add_data(0x1ea455, 0x9b)
                        #     patch.add_data(0x1ea50f, 0x9b)
                        #     patch.add_data(0x1ea521, 0x9b)
                        #     patch.add_data(0x1ea570, 0x9b)
                        #     patch.add_data(0x1ea592, 0x9b)
                        #     patch.add_data(0x1ea59a, 0x9b)
                        #     patch.add_data(0x1ea5a4, 0x9b)
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            patch.add_data(0x1ea528, 0x9b)
                            patch.add_data(0x1ea52b, 0x9b)
                        #if freeze or sequence > 0 or mold > 0: #dont reset properties
                        if invert_se_sw: #change north-south cardinality on everything
                            patch.add_data(0x1ea3e2, 0x75)
                            patch.add_data(0x1ea515, 0x75)
                            patch.add_data(0x1ea405, 0x77)
                            patch.add_data(0x1ea428, 0x73)
                            patch.add_data(0x1ea434, 0x73)
                            patch.add_data(0x1ea443, 0x73)
                            patch.add_data(0x1ea44c, 0x73)
                            patch.add_data(0x1ea42b, 0x75)
                            patch.add_data(0x1ea43a, 0x75)
                            patch.add_data(0x1ea449, 0x75)
                            patch.add_data(0x1ea452, 0x75)
                            patch.add_data(0x1ea512, 0x75)
                            patch.add_data(0x1ea524, 0x75)
                            patch.add_data(0x1ea595, 0x75)
                            patch.add_data(0x1ea5a7, 0x75)
                            patch.add_data(0x1ea42e, 0x71)
                            patch.add_data(0x1ea437, 0x71)
                            patch.add_data(0x1ea43d, 0x71)
                            patch.add_data(0x1ea437, 0x71)
                            patch.add_data(0x1ea446, 0x71)
                            patch.add_data(0x1ea44f, 0x71)
                            patch.add_data(0x1ea458, 0x71)
                            patch.add_data(0x1ea518, 0x71)
                            patch.add_data(0x1ea573, 0x71)
                            patch.add_data(0x1ea59d, 0x71)
                            patch.add_data(0x1ea431, 0x77)
                            patch.add_data(0x1ea440, 0x77)
                            patch.add_data(0x1ea455, 0x77)
                            patch.add_data(0x1ea50f, 0x77)
                            patch.add_data(0x1ea521, 0x77)
                            patch.add_data(0x1ea570, 0x77)
                            patch.add_data(0x1ea592, 0x77)
                            patch.add_data(0x1ea59a, 0x77)
                            patch.add_data(0x1ea5a4, 0x77)
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(9, plus, mold, sub_sequence, sequence, True, 430, 738, 0x20fa1a))
                        ###statues
                        ##room 109
                        #change partition to 12
                        patch.add_data(0x149e3e, 0x0c)
                        #change statue sprite
                        patch.add_data(0x1db9b9, 0x0c)
                        #set SESW only if necessary
                        if sesw_only:
                            patch.add_data(0x1db9b9, calcpointer(sprite, [0x00, 0x08]))
                        else:
                            patch.add_data(0x1db9b9, calcpointer(sprite, [0x00, 0x00]))
                    #dont change statues back to king nimbus after castle finished, since doesnt exist in changed mold
                    #always doing this, bc using those action scripts for scarecrow
                    #entrance hall
                    for addr in [0x209f9b, 0x209f9f, 0x209fa3, 0x209fa7, 0x209fab, 0x209faf]:
                        patch.add_data(addr, [0x9b, 0x9b, 0x9b, 0x9b])
                if location.name == "CzarDragon":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "CzarDragon":
                        #for added hilarity, use npc 155 to summon other sprites instead of sparky
                        if shuffled_boss.name in ["Booster", "Bundt", "Clerk", "Manager", "Director", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x14cfd4, [0x6f, 0x82])
                            if len(shuffled_boss.czar_sprite) > 0:
                                patch.add_data(0x1dbc3d, calcpointer(shuffled_boss.czar_sprite[0], [0x00, 0x08]))
                            else:
                                patch.add_data(0x1dbc3d, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x08]))
                            patch.add_data(0x1dbc3f, [0x80, 0x23, 0x55, 0x2b])
                        patch.add_data(0x1dbde8, calcpointer(sprite, [0x00, 0x68]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(1, plus, mold, sub_sequence, sequence, True, 352, 3330, 0x20f608))
                if location.name == "AxemRangers":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "AxemRangers":
                        #change partitions for small sprites
                        if overworld_is_skinny:
                            #trampoline room
                            #use and modify partition 3
                            patch.add_data(0x14d761, 0x03)
                            #may need to make partition data different depending on underling sprites
                            #ie bowyer arrows may also need slot C modified
                            patch.add_data(0x1dde0c, [0xA0, 0x87, 0x81]);
                        #just skip a hard cutscene, i dont wanna deal with it
                        #nevermind, this hardlocks, dumb game
                        #patch.add_data(0x204b30, [0xD2, 0x3A, 0x4B, 0x9b, 0x9b, 0x9b, 0x9b])
                        #patch.add_data(0x204b5f, [0xD2, 0x69, 0x4B, 0x9b, 0x9b, 0x9b, 0x9b])
                        #patch.add_data(0x204b75, [0xD2, 0x74, 0x4B, 0x9b, 0x9b, 0x9b, 0x9b])
                        #patch.add_data(0x204b92, [0xD2, 0x9c, 0x4B, 0x9b, 0x9b, 0x9b, 0x9b])
                        #axem red
                        patch.add_data(0x1dbdb0, calcpointer(sprite, [0x00, 0x08]))
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if shuffled_boss.name is not "Culex":
                            if len(shuffled_boss.other_sprites) < 1:
                                #dont show axem green
                                #room 4
                                patch.add_data(0x20496d, [0xD9, 0xF4, 0x87, 0x49, 0xA1, 0xF4, 0x15, 0x05, 0x01, 0xFD, 0xF2, 0x57, 0x02, 0x14, 0x07, 0x01, 0xFD, 0xF2, 0x08, 0x40, 0x81, 0x47, 0xD1, 0x0F, 0x00, 0xFE, 0xD0, 0x0F, 0x00])
                                #visibility, for some reason this doesnt do anything, why is this game so dumb
                                patch.add_data(0x14d729, [0x0C, 0x2D, 0x60, 0x00, 0x40, 0x04, 0x43, 0x33, 0xC0, 0x00, 0x01, 0x04, 0x0C, 0x2F, 0x20, 0x15, 0x00, 0x41, 0x00, 0x4B, 0xF1, 0xC0, 0xFD, 0x00])
                                patch.add_data(0x14d752, 0x12)
                                #room 6 visibility
                                patch.add_data(0x2049b4, [0x9b, 0x9b, 0x9b, 0x9b])
                                #trampoline
                                patch.add_data(0x204a39, [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                            if len(shuffled_boss.other_sprites) < 2:
                                #dont show axem yellow
                                # visibility, for some reason this doesnt do anything, why is this game so dumb
                                patch.add_data(0x14d756, 0x12)
                                #room 6 visibility
                                patch.add_data(0x2049bb, [0x9b, 0x9b, 0x9b, 0x9b])
                                patch.add_data(0x204a6a,
                                               [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b])
                            if len(shuffled_boss.other_sprites) < 3:
                                #dont show axem pink
                                # visibility, for some reason this doesnt do anything, why is this game so dumb
                                patch.add_data(0x14d7b0, 0x1c)
                                patch.add_data(0x14d75a, 0x13)
                                # room 6 visibility
                                patch.add_data(0x2049c2, [0x9b, 0x9b, 0x9b, 0x9b])
                                #trampoline
                                patch.add_data(0x204a9b,
                                               [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b])
                            if len(shuffled_boss.other_sprites) < 4:
                                #dont show axem black
                                # visibility, for some reason this doesnt do anything, why is this game so dumb
                                patch.add_data(0x14d7ac, 0x1c)
                                patch.add_data(0x14d75e, 0x13)
                                #room 6 visibility
                                patch.add_data(0x2049c9, [0x9b, 0x9b, 0x9b, 0x9b])
                                #trampoline
                                patch.add_data(0x204acc,
                                               [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                                0x9b])
                            #trampoline bounces
                            patch.add_data(0x204aff, [0xD4, len(shuffled_boss.other_sprites)])
                            #load sprites from whatever boss is there
                            if len(shuffled_boss.other_sprites) >= 1:
                                patch.add_data(0x1dbdcc, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x08]))
                            if len(shuffled_boss.other_sprites) >= 2:
                                patch.add_data(0x1dbdc5, calcpointer(shuffled_boss.other_sprites[1], [0x00, 0x08]))
                            if len(shuffled_boss.other_sprites) >= 3:
                                patch.add_data(0x1dbdbe, calcpointer(shuffled_boss.other_sprites[2], [0x00, 0x08]))
                            if len(shuffled_boss.other_sprites) >= 4:
                                patch.add_data(0x1dbdb7, calcpointer(shuffled_boss.other_sprites[3], [0x00, 0x08]))
                                #why is this loading sequence 5 for pandorite????????????? the event literally says sequence 4
                            if len(shuffled_boss.other_sprites) < 4:
                                spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, False, 393, 2120, 0x20f8a2))
                                bytesFor2120 = [0xF2, 0x89, 0x35, 0x1a, 0xf9]
                                if len(shuffled_boss.other_sprites) < 3:
                                    bytesFor2120.extend([0xF2, 0x89, 0x33, 0x19, 0xf9])
                                    if len(shuffled_boss.other_sprites) < 2:
                                        bytesFor2120.extend([0xF2, 0x89, 0x31, 0x18, 0xf9])
                                        if len(shuffled_boss.other_sprites) < 2:
                                            bytesFor2120.extend([0xF2, 0x89, 0x2f, 0x17, 0xf9])
                                bytesFor2120.append(0xD0)
                                bytesFor2120.extend(calcpointer(3344))
                                bytesFor2120.append(0xFE)
                                for i in range(0x1f7a4d + len(bytesFor2120), 0x1f7a90):
                                    bytesFor2120.append(0x9b)
                                patch.add_data(0x1f7a4d, bytesFor2120)
                            if sequence > 0 or mold > 0:
                                if sequence > 0:
                                    sub_sequence = True
                                elif mold > 0:
                                    sub_sequence = False
                                spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, True, 357, 3332, 0x20f63b))
                                spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, False, 388, 3339, 0x20f88d))
                                spritePhaseEvents.append(SpritePhaseEvent(3, plus, mold, sub_sequence, sequence, True, 394, 3342, 0x20f8a5))
                                spritePhaseEvents.append(SpritePhaseEvent(1, plus, mold, sub_sequence, sequence, False, 392, 15, 0x20f899))
                                if len(shuffled_boss.other_sprites) == 4:
                                    spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, False, 393, 3344, 0x20f8a2))
                        #culex needs special rules
                        else:
                            patch.add_data(0x1dbdcc, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x08]))
                            patch.add_data(0x1dbdc5, calcpointer(shuffled_boss.other_sprites[1], [0x00, 0x08]))
                            patch.add_data(0x1dbdbe, calcpointer(shuffled_boss.other_sprites[2], [0x00, 0x08]))
                            patch.add_data(0x1dbdb7, calcpointer(shuffled_boss.other_sprites[3], [0x00, 0x08]))
                            spritePhaseEvents.append(SpritePhaseEvent([2, 4, 5, 6], 0, 0, True, [sequence, shuffled_boss.other_sprites_sequences[0], shuffled_boss.other_sprites_sequences[1], shuffled_boss.other_sprites_sequences[2], shuffled_boss.other_sprites_sequences[3]], [True, True, True, True, True], 357, 3332, 0x20f63b))
                            spritePhaseEvents.append(SpritePhaseEvent([2, 4, 5, 6], 0, 0, True, [sequence, shuffled_boss.other_sprites_sequences[0], shuffled_boss.other_sprites_sequences[1], shuffled_boss.other_sprites_sequences[2], shuffled_boss.other_sprites_sequences[3]], [True, True, True, False, False], 388, 3339, 0x20f88d))
                            spritePhaseEvents.append(SpritePhaseEvent(1, 0, 0, True, shuffled_boss.other_sprites_sequences[2], True, 365, 15, 0x20f653))
                            spritePhaseEvents.append(SpritePhaseEvent(1, 0, 0, True, shuffled_boss.other_sprites_sequences[1], True, 391, 3341, 0x20f896))
                            spritePhaseEvents.append(SpritePhaseEvent([1, 2, 3], 0, 0, True, [shuffled_boss.other_sprites_sequences[3], shuffled_boss.other_sprites_sequences[3], sequence], [True, False, True], 394, 3342, 0x20f8a5))
                            spritePhaseEvents.append(SpritePhaseEvent([1, 2, 4, 5], 0, 0, True, [sequence, shuffled_boss.other_sprites_sequences[0], shuffled_boss.other_sprites_sequences[1], shuffled_boss.other_sprites_sequences[2], shuffled_boss.other_sprites_sequences[3]], [False, False, False, False, False], 392, 15, 0x20f899))
                            spritePhaseEvents.append(SpritePhaseEvent([2, 4, 5, 6], 0, 0, True, [sequence, shuffled_boss.other_sprites_sequences[0], shuffled_boss.other_sprites_sequences[1], shuffled_boss.other_sprites_sequences[2], shuffled_boss.other_sprites_sequences[3]], [False, False, False, False, False], 393, 3344, 0x20f8a2))
                if location.name == "Magikoopa":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Magikoopa":
                        if freeze or sesw_only:
                            patch.add_data(0x1dbd32, calcpointer(sprite, [0x00, 0x48]))
                        else:
                            patch.add_data(0x1dbd32, calcpointer(sprite, [0x00, 0x40]))
                        # if freeze or sequence > 0 or mold > 0: #never change directions
                        #     sub_sequence = True
                        #     patch.add_data(0x1f881c, 0x9b)
                        #     patch.add_data(0x1f885b, 0x9b)
                        #     patch.add_data(0x1f88cb, 0x9b)
                        #     patch.add_data(0x1f88d3, 0x9b)
                        #     patch.add_data(0x1f8801, 0x9b)
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        if freeze or (not sub_sequence and mold > 0): #dont loop
                            patch.add_data(0x1f88d6, 0x9b)
                            patch.add_data(0x1f8802, 0x9b)
                        if freeze or sequence > 0 or mold > 0: #dont reset properties
                            patch.add_data(0x1f88ca, 0x9b)
                        if invert_se_sw: #change north-south cardinality on everything
                            patch.add_data(0x1f881c, 0x75)
                            patch.add_data(0x1f885b, 0x77)
                            patch.add_data(0x1f88cb, 0x75)
                            patch.add_data(0x1f88d3, 0x77)
                            patch.add_data(0x1f8801, 0x77)
                        #special animations
                        if not freeze:
                            if push_sequence is not False:
                                patch.add_data(0x1f8842, [0x08, 0x50, push_sequence])
                            else:
                                patch.add_data(0x1f8842, [0x9b, 0x9b, 0x9b])
                            if extra_sequence is not False:
                                patch.add_data(0x1f885e, [0x08, 0x50, 0x80 + extra_sequence])
                            elif push_sequence is not False:
                                patch.add_data(0x1f885e, [0x08, 0x50, 0x80 + push_sequence])
                            else:
                                patch.add_data(0x1f885e, [0x9b, 0x9b, 0x9b])
                        else:
                            patch.add_data(0x1f8842, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1f885e, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1f8861, [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1f8881,
                                       [0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                        0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b,
                                        0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1f8855, [0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1f87f1, [0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1f87f4, [0x9b, 0x9b, 0x9b])
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(2, plus, mold, sub_sequence, sequence, False, 266, 2208, 0x20F2Da))
                if location.name == "Boomer":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Boomer":
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc52e, calcpointer(sprite, [0x00, 0x68]))
                        #special animations
                        if not freeze:
                            if push_sequence is not False:
                                patch.add_data(0x1f8a34, [0x08, 0x50, push_sequence])
                            elif extra_sequence is not False:
                                patch.add_data(0x1f8a34, [0x08, 0x40, extra_sequence])
                            elif sequence > 0 or mold > 0:
                                #needed for exor
                                patch.add_data(0x1f8a34, [0x9b, 0x9b, 0x9b])
                            else:
                                patch.add_data(0x1f8a34, [0x08, 0x40, sequence])
                        else:
                            patch.add_data(0x1f8a34, [0x9b, 0x9b, 0x9b])
                            patch.add_data(0x1f8a34, [0x9b, 0x9b, 0x9b])
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 400, 2224, 0x20F8e1))
                if location.name == "Countdown":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "CountDown":
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc463, calcpointer(sprite, [0x00, 0x28]))
                        if shuffled_boss.name in ["Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            if len(shuffled_boss.czar_sprite) > 0:
                                patch.add_data(0x1dc46A, calcpointer(shuffled_boss.czar_sprite[0], [0x00, 0x28]))
                            else:
                                patch.add_data(0x1dc46A, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x28]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(0, plus, mold, sub_sequence, sequence, False, 223, 2363, 0x20F145))
                if location.name == "Clerk":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Clerk":
                        #change sequence 01 of Clerk, wherever he is, if not vanilla, to be his NW facing sprite, to make animations work
                        patch.add_data(0x265f53, 0x02)
                        patch.add_data(0x265f82, 0x43)
                        if freeze or sequence > 0 or mold > 0:
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc55f, calcpointer(sprite, [0x00, 0x08]))
                        if shuffled_boss.name in ["Booster", "Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x1dbf15, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x00]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(9, plus, mold, sub_sequence, sequence, True, 469, 2605, 0x20Fc24))
                        patch.add_data(0x1fe34f, [0x9b, 0x9b, 0x9b])
                if location.name == "Manager":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Manager":
                        # change sequence 01 of Manager, wherever he is, if not vanilla, to be his NW facing sprite, to make animations work
                        patch.add_data(0x36923e, 0x02)
                        patch.add_data(0x36926d, 0x43)
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc57b, calcpointer(sprite, [0x00, 0x28]))
                        if shuffled_boss.name in ["Booster", "Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x1dc0d5, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x00]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(16, plus, mold, sub_sequence, sequence, True, 471, 2617, 0x20Fc3c))
                        patch.add_data(0x1fe69c, [0x9b, 0x9b, 0x9b])
                if location.name == "Director":
                    # chance sequence 01 of Manager, wherever he is, if not vanilla, to be his NW facing sprite, to make animations work
                    patch.add_data(0x369296, 0x02)
                    patch.add_data(0x3692C5, 0x43)
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Director":
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc597, calcpointer(sprite, [0x00, 0x28]))
                        if shuffled_boss.name in ["Booster", "Bundt", "Clerk", "Manager", "Director", "Croco1", "Croco2", "Mack", "Bowyer", "Punchinello", "Johnny", "Megasmilax", "CzarDragon", "Birdo", "Valentina", "Hidon", "Yaridovich", "Boomer"]:
                            patch.add_data(0x1dc50b, calcpointer(shuffled_boss.other_sprites[0], [0x00, 0x20]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(10, plus, mold, sub_sequence, sequence, True, 472, 2621, 0x20Fc51))
                        patch.add_data(0x1fe92e, [0x9b, 0x9b, 0x9b])
                if location.name == "Gunyolk":
                    print(location.name + ": " + shuffled_boss.name)
                    if shuffled_boss.name is not "Gunyolk":
                        if freeze or sequence > 0 or mold > 0: #never change directions
                            sub_sequence = True
                        if sequence == 0 and mold > 0:
                            sub_sequence = False
                        patch.add_data(0x1dc53c, calcpointer(sprite, [0x00, 0x00]))
                        #preload if needed
                        if sequence > 0 or mold > 0:
                            if sequence > 0:
                                sub_sequence = True
                            elif mold > 0:
                                sub_sequence = False
                            spritePhaseEvents.append(SpritePhaseEvent(13, plus, mold, sub_sequence, sequence, True, 470, 2601, 0x20Fc2d))
                        patch.add_data(0x14e839, 0x20)
                        patch.add_data(0x1fe1bd, [0x01, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1c4, [0x01, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1cb, [0x01, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1d2, [0x01, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1d9, [0x01, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1e4, [0x01, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])
                        patch.add_data(0x1fe1ed, [0x01, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b, 0x9b])


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
                if isinstance(event.sequence, list):
                    current_length_of_npc_code += len(event.generate_code_culex())
                else:
                    current_length_of_npc_code += len(event.generate_code())
            for event in spritePhaseEvents:
                if isinstance(event.sequence, list):
                    append_jumps.extend(event.generate_code_culex())
                else:
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
