import random

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

def compress(string):
  # TODO: Use \x0B to compress longer spacings..
  for token, char in compression_table:
    string = string.replace(token, char)
  return string + '\0'

# Might wanna upgrade to a SQL table or something...

# Formatting is tricky. Probably should test it out in the game itself.
# 1. Use newlines. If a string goes too long, sometimes it wraps around to the
#    other side and sometimes it softlocks the game. Definitely test these first
#    before updating.
wish_strings = list(map(compress, [
    '\n\n     I wish for fish.',
    '\n\n     I weesh for quiche.',
    '\n\n     I wish I was a little bit taller.',
    '\n\n     I wish I was a baller.',
    '\n\n     I wish for more wishes!',
    '\n\n     I wish for more wishbones!',
    '\n\n     I wish I was in this game.',
    '\n\n     SMRPG is the best\n     Final Fantasy!',
    '\n\n     I wish this was\n     Ecco the Dolphin.',
    '\n\n     (Hope this is a better\n     seed than last time)',
    '\n\n     When\'s Marvel?',
    '\n\n     Come here often?',
    '\n\n     Please let Culex\n at Hammer Bros.',
    '\n\n     I hope can get out of level 3.',
    '\n\n     Wish I could count to 10',
    '\n     Oh,\n     I wish, I wish\n     I hadn\'t killed that fish.',
    ' Like the moon over\n the day, my genius and brawn\n are lost on these fools. \x24Haiku'
]))

wish_dialogs = [
    3111,
    3108,
    3110,
    3109,
    3116, #3327
    3327,
    3114, #3326
    3326,
    3115,
    3106, #3275
    3275,
    3113, #3325
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
            table_entry = 0x37E000 + dialog_id * 2
            patch.add_data(table_entry, utils.ByteField((pointer - 4) & 0xFFFF, num_bytes=2).as_bytes())
            if wish:
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
            table_entry = 0x37E000 + dialog_id * 2
            patch.add_data(table_entry, utils.ByteField((pointer - 8) & 0xFFFF, num_bytes=2).as_bytes())
            if question:
                patch.add_data(pointer, question)

        return patch

class Question:
    def __init__(self, question, correct, wrong_1, wrong_2, name=''):
        self.question = question + '\x03\n'         # 0x03 is a page break
        self.correct = ' \x07  (' + correct + ')\n' # 0x07 is the select arrow
        self.wrong_1 = ' \x07  (' + wrong_1 + ')\n'
        self.wrong_2 = ' \x07  (' + wrong_2 + ')\n'
        self.name = name

    def get_string(self, correct_index):
        answers = [''] * 3
        answers[correct_index] = self.correct
        random.shuffle(wrong_indexes[correct_index][::])
        index_1,index_2 = wrong_indexes[correct_index]
        answers[index_1] = self.wrong_1
        answers[index_2] = self.wrong_2
        answers[2] = answers[2][:-1] # Remove the newline
        name = self.name
        if name:
          name += ': '
        return compress(''.join([name, self.question] + answers))

# Hand compacted...
cruel_question = '?\x03\x01\x07\x081\x01\x07\x082\x01\x07\x083\x00'
quiz_questions = [
    Question('What game gives\n you the Star Egg?', 'Look the other way', 'Blackjack', 'Pokemon', 'PatCdr')
]

backfill_questions = [
    Question('How much...does a\n female beetle cost?', '1 coin', '50 coins', 'A frog coin', 'DR. T'), # 0 1842
    Question('What does Belome\n really like to turn people into?', 'Scarecrows', 'Ice cream cones', 'Mushrooms', 'DR. T'), # 0 1843
    Question('What is Raini\'s\n husband\'s name?', 'Raz', 'Romeo', 'Gaz', 'DR. T'), # 0 1844
    Question('What\'s the name of\n the boss at the Sunken Ship?', 'Johnny', 'Jimmy', 'Jackson', 'DR. T'), # 0 1845
    Question('Booster is what\n generation?', '7th', '8th', '78th', 'DR. T'), # 0 1846
    Question('Where was the 3rd\n Star Piece found?', 'Moleville', 'Forest Maze', 'Star Hill', 'DR. T'), # 0 1847
    Question('Johnny loves WHICH\n beverage?...', 'Currant juice', 'Grape juice', 'Boysenberry smoothie', 'DR. T'), # 0 1848
    Question('In the Moleville blues,\n it\'s said that the moles are\n covered in what?', 'Soil', 'Dirt', 'Slugs', 'DR. T'), # 0 1849
    Question('What color are the\n curtains in Mario\'s house?', 'Blue', 'Green', 'Red', 'DR. T'), # 0 1850
    Question('Yaridovich is what?', 'A boss', 'A new breed of cattle', 'A special attack', 'DR. T'), # 0 1851
    Question('The boy at the inn in\n Mushroom Kingdom was playing\n with...What?', 'Game Boy', 'Super NES', 'Virtual Boy', 'DR. T'), # 0 1852
    Question('What did Carroboscis\n turn into?', 'A carrot', 'A beet', 'A radish', 'DR. T'), # 0 1853
    Question('Who is the famous\n sculptor in Nimbus Land?', 'Garro', 'Gaz', 'Goya', 'DR. T'), # 0 1854
    Question('What is Hinopio in\n charge of at the middle counter?', 'The inn', 'Weapons', 'Items', 'DR. T'), # 0 1855
    Question('Who is the ultimate\n enemy in this adventure?', 'Smithy', 'Bowser', 'Goomba', 'DR. T'), # 0 1856
    Question('Who is the leader of\n The Axem Rangers?', 'Red', 'Black', 'Green', 'DR. T'), # 0 1857
    Question('What\'s the name of\n Jagger\'s "sensei#?', 'Jinx', 'Dinky', 'Johnny', 'DR. T'), # 1 1858
    Question('How many underlings\n does Croco have?', '3', '2', '4', 'DR. T'), # 1 1859
    Question('What was Toadstool\n doing when she was kidnapped by\n Bowser?', 'She was looking at flowers', 'She was playing cards', 'She was digging for worms', 'DR. T'), # 1 1860
    Question('Who is the famous\n composer at Tadpole Pond?', 'Toadofsky', 'Toadoskfy', 'Frogfucius', 'DR. T'), # 1 1861
    Question('Which monster does\n not appear in Booster Tower?', 'Terrapin', 'Jester', 'Bob-omb', 'DR. T'), # 1 1862
    Question('The boy getting his\n picture taken at Marrymore\n can\'t wait \'til which season?', 'Skiing', 'Hunting', 'Baseball', 'DR. T'), # 1 1863
    Question('What technique does\n Bowser learn at Level 15?', 'Crusher', 'Bowser Crush', 'Terrorize', 'DR. T'), # 1 1864
    Question('What words does\n Shy Away use when he sings?', 'La dee dah:', 'Dum dee dah:', 'Dum lee lah:', 'DR. T'), # 1 1865
    Question('What does Birdo\n come out of?', 'An eggshell', 'A barrel', 'A basket', 'DR. T'), # 1 1866
    Question('What\'s the first\n monster you see in the Pipe Vault?', 'Sparky', 'Goomba', 'Chompweed', 'DR. T'), # 1 1867
    Question('What\'s the password\n in the Sunken Ship?', 'Pearls', 'Corals', 'Oyster', 'DR. T'), # 1 1868
    Question('What was Mallow \n asked to get for Frogfucius?', 'Cricket Pie', 'Honey Syrup', 'Carbo Cookie', 'DR. T'), # 1 1869
    Question('Mite is Dyna\'s...\n WHAT?', 'Little brother', 'Big sister', 'Second cousin', 'DR. T'), # 1 1870
    Question('What does the Red\n Essence do?', 'Gives you strength', 'Makes you sleepy', 'Relieves back pain', 'DR. T'), # 1 1871
    Question('How long have the\n couple inside the chapel been\n waiting for their wedding?', '30 minutes', '1 hour', '45 minutes', 'DR. T'), # 1 1872
    Question('What do Culex, Jinx,\n and Goomba have in common?', 'They live in Monstro Town', 'They are immortal', 'They all like bratwurst', 'DR. T'), # 1 1873
    Question('What is the 4th\n selection on the Menu screen?', 'Equip', 'Important Items', 'Special Items', 'DR. T'), # 2 1874
    Question('The man getting his\n picture taken at Marrymore\n hates what?', 'Getting his picture taken', 'Getting married', 'Mowing the lawn on Sundays', 'DR. T'), # 2 1875
    Question('Where was the 1st\n Star Piece found?', 'Mushroom Kingdom', 'Bowser\'s Keep', 'Mario\'s Pad', 'DR. T'), # 2 1876
    Question('How many legs does\n Wiggler have?', '6', '10', '8', 'DR. T'), # 2 1877
    Question('What\'s the full name\n of the boss at the Sunken Ship?', 'Jonathan Jones', 'Johnny Jones', 'Jesse James Jones', 'DR. T'), # 2 1878
    Question('Who helped you up the\n cliff at Land\'s End?', 'Sky Troopas', 'Sky Troops', 'Flying Troopa', 'DR. T'), # 2 1879
    Question('What color is the\n end of Dodo\'s beak?', 'Red', 'Yellow', 'Orange', 'DR. T'), # 2 1880
    Question('What\'s the chef\'s\n name at Marrymore?', 'Torte', 'Blintz', 'Gateau', 'DR. T'), # 2 1881
]
