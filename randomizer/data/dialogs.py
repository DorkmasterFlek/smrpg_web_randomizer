# Data module for dialog data.

from randomizer.logic import flags
from randomizer.logic import utils
from randomizer.logic.patch import Patch

# This table isn't complete.
# And some of the single char replacements should be done via string.translate,
compression_table = [
    ('\n', '\x01'),
    (' and ', '\x15'),
    (' the', '\x0E'),
    (' you', '\x0F'),
    (' to ', '\x11'),
    ('    ', '\x0A'),
    (' so', '\x17'),
    ('is ', '\x16'),
    ("'s ", '\x12'),
    ('   ', '\x09'),
    (' I ', '\x14'),
    ('  ', '\x08'),
    ('in', '\x10'),
    ('Mario', '\x13'),
    ("'", '\x9B'),
    (':', '\x8E'),
    ('~', '\x3A'),
]

DIALOG_POINTER_BASE_ADDRESS = 0x37e000


def compress(string):
    # TODO: Use \x0B to compress longer spacings..
    for token, char in compression_table:
        string = string.replace(token, char)
    return string + '\x00'  # Null terminate strings.


# Formatting is tricky. Probably should test it out in the game itself.
# 1. Use newlines. If a string goes too long, sometimes it wraps around to the
#    other side and sometimes it softlocks the game. Definitely test these first
#    before updating.
wish_strings = list(map(compress, [
    'I wish for fish.',
    'I weesh for quiche.',
    'I wish I was a little bit taller.',
    'I wish I was a baller.',
    'I wish for more wishes!',
    'I wish for more wishbones!',
    'I wish I was in this game.',
    'SMRPG is the best\nFinal Fantasy!',
    'I wish this was\nEcco the Dolphin.',
    'Hope this is a better\nseed than last time.',
    'When\'s Marvel?',
    'Come here often?',
    'Please let Culex\nbe at Hammer Bros.',
    'I hope can get out of level 3.',
    'Wish I could count to 10.',
    'Oh,\nI wish, I wish\nI hadn\'t killed that fish.',
    'Like the moon over\nthe day, my genius and brawn\nare lost on these fools. \x24Haiku'
]))

wish_dialogs = [
    3111,
    3108,
    3110,
    3109,
    3116,
    3327,
    3114,
    3326,
    3115,
    3106,
    3275,
    3113,
    3325,
    3105,
    3112,
    3107,
]


class Wishes:
    def __init__(self, world):
        self.world = world
        self.wishes = []

    @property
    def name(self):
        return self.__class__.__name__

    def get_patch(self):
        """
        Returns:
            randomizer.logic.patch.Patch: Patch data
        """
        patch = Patch()

        # A big assumption here is that the dialogs aren't getting relocated
        # out if the 0x240000 bank.
        for dialog_id, pointer, wish in self.wishes:
            table_entry = DIALOG_POINTER_BASE_ADDRESS + dialog_id * 2
            patch.add_data(table_entry, utils.ByteField((pointer - 4) & 0xFFFF, num_bytes=2).as_bytes())
            patch.add_data(pointer, wish)

        return patch


quiz_dialogs = list(range(1842, 1882))
wrong_indexes = [[1, 2], [0, 2], [0, 1]]


class Quiz:
    def __init__(self, world):
        self.world = world
        self.questions = []

    @property
    def name(self):
        return self.__class__.__name__

    def get_patch(self):
        """
        Returns:
            randomizer.logic.patch.Patch: Patch data
        """
        patch = Patch()

        for dialog_id, pointer, question in self.questions:
            table_entry = DIALOG_POINTER_BASE_ADDRESS + dialog_id * 2
            patch.add_data(table_entry, utils.ByteField((pointer - 8) & 0xFFFF, num_bytes=2).as_bytes())
            if question:
                patch.add_data(pointer, question)

        return patch


class Question:
    def __init__(self, question, correct, wrong_1, wrong_2):
        self.question = question
        self.correct_answer = correct
        self.wrong_answers = [wrong_1, wrong_2]

    def get_string(self, correct_index):
        answers = [''] * 3
        answers[correct_index] = ' \x07  ' + self.correct_answer + '\n'
        index_1, index_2 = wrong_indexes[correct_index]
        answers[index_1] = ' \x07  ' + self.wrong_answers[0] + '\n'
        answers[index_2] = ' \x07  ' + self.wrong_answers[1] + '\n'
        final_string = self.question + '\x03' + ''.join(answers)
        final_string.rstrip('\n')
        return compress(final_string)


# New quiz questions we added.
quiz_questions = [
    Question('What game gives\nyou the Star Egg?', 'Look The Other Way', 'Blackjack', 'Pokemon'),
    Question('Who is Yoshi\'s nemesis?', 'Boshi', 'Broshi', 'Raz'),
    Question('What can you trade\nthe Shiny Stone for?', 'Carbo Cookie', 'Fireworks', 'A Frog Coin'),
    Question('Which isn\'t a setting\non Monstro Town\'s Pinwheel?', 'Blow', 'Gust', 'Blast'),
]


def generate_rando_questions(world):
    acc = []
    cake_right, cake_wrong = 'Vanilla', 'Chocolate'
    if world.settings.is_flag_enabled(flags.PaletteSwaps):
        cake_right, cake_wrong = 'Chocolate', 'Vanilla'
    acc.append(Question('What flavor were Raspberry and Bundt?', cake_right, cake_wrong, 'Snozzberry'))
    return acc


# Vanilla questions to backfill with if we don't have enough other ones.
backfill_questions = [
    Question('How much...does a\nfemale beetle cost?', '1 coin', '50 coins', 'A frog coin'),
    Question('What does Belome\nreally like to turn people into?', 'Scarecrows', 'Ice cream cones', 'Mushrooms'),
    Question('What is Raini\'s\nhusband\'s name?', 'Raz', 'Romeo', 'Gaz'),
    Question('What\'s the name of\nthe boss at the Sunken Ship?', 'Johnny', 'Jimmy', 'Jackson'),
    Question('Booster is what\ngeneration?', '7th', '8th', '78th'),
    Question('Where was the 3rd\nStar Piece found?', 'Moleville', 'Forest Maze', 'Star Hill'),
    Question('Johnny loves WHICH\nbeverage?...', 'Currant juice', 'Grape juice', 'Boysenberry smoothie'),
    Question('In the Moleville blues,\nit\'s said that the moles are\ncovered in what?', 'Soil', 'Dirt', 'Slugs'),
    Question('What color are the\ncurtains in Mario\'s house?', 'Blue', 'Green', 'Red'),
    Question('Yaridovich is what?', 'A boss', 'A new breed of cattle', 'A special attack'),
    Question('The boy at the inn in\nMushroom Kingdom was playing\nwith...What?', 'Game Boy', 'Super NES',
             'Virtual Boy'),
    Question('What did Carroboscis\nturn into?', 'A carrot', 'A beet', 'A radish'),
    Question('Who is the famous\nsculptor in Nimbus Land?', 'Garro', 'Gaz', 'Goya'),
    Question('What is Hinopio in\ncharge of at the middle counter?', 'The inn', 'Weapons', 'Items'),
    Question('Who is the ultimate\nenemy in this adventure?', 'Smithy', 'Bowser', 'Goomba'),
    Question('Who is the leader of\nThe Axem Rangers?', 'Red', 'Black', 'Green'),
    Question('What\'s the name of\nJagger\'s "sensei#?', 'Jinx', 'Dinky', 'Johnny'),
    Question('How many underlings\ndoes Croco have?', '3', '2', '4'),
    Question('What was Toadstool\ndoing when she was kidnapped by\nBowser?', 'She was looking at flowers',
             'She was playing cards', 'She was digging for worms'),
    Question('Who is the famous\ncomposer at Tadpole Pond?', 'Toadofsky', 'Toadoskfy', 'Frogfucius'),
    Question('Which monster does\nnot appear in Booster Tower?', 'Terrapin', 'Jester', 'Bob-omb'),
    Question('The boy getting his\npicture taken at Marrymore\ncan\'t wait \'til which season?', 'Skiing', 'Hunting',
             'Baseball'),
    Question('What technique does\nBowser learn at Level 15?', 'Crusher', 'Bowser Crush', 'Terrorize'),
    Question('What words does\nShy Away use when he sings?', 'La dee dah:', 'Dum dee dah:', 'Dum lee lah:'),
    Question('What does Birdo\ncome out of?', 'An eggshell', 'A barrel', 'A basket'),
    Question('What\'s the first\nmonster you see in the Pipe Vault?', 'Sparky', 'Goomba', 'Chompweed'),
    Question('What\'s the password\nin the Sunken Ship?', 'Pearls', 'Corals', 'Oyster'),
    Question('What was Mallow \nasked to get for Frogfucius?', 'Cricket Pie', 'Honey Syrup', 'Carbo Cookie'),
    Question('Mite is Dyna\'s...\nWHAT?', 'Little brother', 'Big sister', 'Second cousin'),
    Question('What does the Red\nEssence do?', 'Gives you strength', 'Makes you sleepy', 'Relieves back pain'),
    Question('How long have the\ncouple inside the chapel been\nwaiting for their wedding?', '30 minutes', '1 hour',
             '45 minutes'),
    Question('What do Culex, Jinx,\nand Goomba have in common?', 'They live in Monstro Town', 'They are immortal',
             'They all like bratwurst'),
    Question('What is the 4th\nselection on the Menu screen?', 'Equip', 'Important Items', 'Special Items'),
    Question('The man getting his\npicture taken at Marrymore\nhates what?', 'Getting his picture taken',
             'Getting married', 'Mowing the lawn on Sundays'),
    Question('Where was the 1st\nStar Piece found?', 'Mushroom Kingdom', 'Bowser\'s Keep', 'Mario\'s Pad'),
    Question('How many legs does\nWiggler have?', '6', '10', '8'),
    Question('What\'s the full name\nof the boss at the Sunken Ship?', 'Jonathan Jones', 'Johnny Jones',
             'Jesse James Jones'),
    Question('Who helped you up the\ncliff at Land\'s End?', 'Sky Troopas', 'Sky Troops', 'Flying Troopa'),
    Question('What color is the\nend of Dodo\'s beak?', 'Red', 'Yellow', 'Orange'),
    Question('What\'s the chef\'s\nname at Marrymore?', 'Torte', 'Blintz', 'Gateau'),
]
