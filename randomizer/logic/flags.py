# Flag definitions and logic.

from django.utils.html import mark_safe
from markdown import markdown


# ************************************** Flag classes

class Flag:
    """Class representing a flag with its description, and possible values/choices/options."""
    name = ''
    description = ''
    inverse_description = ''
    value = ''
    hard = False
    modes = ['linear', 'open']
    choices = []
    options = []

    @classmethod
    def description_as_markdown(cls):
        return mark_safe(markdown(cls.description, safe_mode='escape'))

    @classmethod
    def description_or_name_as_markdown(cls):
        if cls.description:
            return mark_safe(markdown(cls.description, safe_mode='escape'))
        else:
            return mark_safe(markdown(cls.name, safe_mode='escape'))

    @classmethod
    def inverse_description_as_markdown(cls):
        return mark_safe(markdown(cls.inverse_description, safe_mode='escape'))

    @classmethod
    def inverse_description_or_name_as_markdown(cls):
        if cls.inverse_description:
            return mark_safe(markdown(cls.inverse_description, safe_mode='escape'))
        else:
            return mark_safe(markdown("(" + cls.name + ")", safe_mode='escape'))

    @classmethod
    def available_in_mode(cls, mode):
        """

        Args:
            mode (str): Mode to check availability.

        Returns:
            bool: True if this flag is available in the given mode, False otherwise.

        """
        return mode in cls.modes


# ******** Star piece shuffle

class SevenStarHunt(Flag):
    name = 'Shuffle seven stars'
    description = "You must find seven Star Pieces instead of six to open the final area."
    inverse_description = "(You do not need to find a seventh Star Piece to open the final area.)"
    value = 'R7'
    modes = ['open']


class BowsersKeepOpen(Flag):
    name = "Include Bowser's Keep locations"
    description = ("Bowser's Keep is open from the start and the boss locations inside the keep may have Star Pieces.  "
                   "The Factory will be opened once you find all Star Pieces.")
    inverse_description = ("(Bowser's Keep will not contain any Star Pieces, and will be opened when you find all your "
                           "Star Pieces.)")
    value = 'Rk'
    modes = ['open']


class CulexStarShuffle(Flag):
    name = "Include Culex's Lair"
    description = "Culex's Lair in Monstro Town may have a Star Piece."
    inverse_description = "(Culex's Lair in Monstro Town will not have a Star Piece.)"
    value = 'Rc'
    hard = True
    modes = ['open']


class StarPieceShuffle(Flag):
    name = 'Randomize star pieces'
    description = ("Assigns six star pieces to random boss locations, excluding Culex's Lair, Bowser's Keep, and the "
                   "Factory. Collect all the star pieces to open Bowser's Keep and progress to the end of the game.")
    inverse_description = "(The star pieces will stay in their original locations.)"
    value = 'R'
    modes = ['open']
    options = [
        SevenStarHunt,
        BowsersKeepOpen,
        CulexStarShuffle,
    ]


# ******** Key item shuffle

class IncludeSeedFertilizer(Flag):
    name = 'Include Seed and Fertilizer'
    description = 'The **Seed** and **Fertilizer** will be included in the key item shuffle.'
    inverse_description = "(The Seed and Fertilizer are not key items, and can be found in their original locations.)"
    value = 'Ks'
    modes = ['open']


class KeyItemShuffle(Flag):
    name = 'Randomize key items'
    description = ("The locations of key items are shuffled amongst each other.  For example, you may find the "
                   "Shed Key at Croco 1 instead of the Rare Frog Coin.\n\nThe items randomized this way are the "
                   "**Rare Frog Coin**, **Cricket Pie**, **Bambino Bomb**, **Castle Key 1**, **Castle Key 2**, "
                   "**Alto Card**, **Tenor Card**, **Soprano Card**, **Greaper Flag**, **Dry Bones Flag**, "
                   "**Big Boo Flag**, **Shed Key**, **Elder Key**, **Cricket Jam**, **Temple Key**, and **Room Key**.")
    inverse_description = "(The key items will stay in their original locations.)"
    value = 'K'
    modes = ['open']
    options = [
        IncludeSeedFertilizer,
    ]


# ******** Character shuffle flags

class CharacterStats(Flag):
    name = 'Randomize character stats'
    description = "Stats for each character will be randomized."
    inverse_description = ("(The characters will retain their original attack, defense, magic attack, magic defense, "
                           "and speed stats.)")
    value = 'Cs'


class CharacterJoinOrder(Flag):
    name = 'Randomize character join order'
    description = ("Characters join your party at the same spots, but the character you get there is randomized.  The "
                   "character that joins the party will have their stats and starting level scaled for that spot.")
    inverse_description = "(You will start with Mario, Mallow, and Geno, and must recruit Bowser and Peach.)"
    value = 'Cj'


class CharacterLearnedSpells(Flag):
    name = 'Randomize character learned spells'
    description = "The spells each character learns and what level they learn them are randomized."
    inverse_description = "(Characters retain their original spell lists.)"
    value = 'Cl'


class CharacterSpellStats(Flag):
    name = 'Randomize character spell stats'
    description = "The power and FP cost of character magic spells will be randomized."
    inverse_description = "(Base power and FP cost of party spells are unchanged from the original game.)"
    value = 'Cp'


class CharacterShuffle(Flag):
    name = 'Randomize characters'
    value = '@C'
    options = [
        CharacterStats,
        CharacterSpellStats,
        CharacterJoinOrder,
        CharacterLearnedSpells,
    ]


# TODO: ******** Starting character flags

class ChooseStartingCharacter(Flag):
    name = 'Choose starting character'
    value = '@starting'
    choices = [
        # TODO
    ]


# ******** Enemy shuffle flags

class EnemyStats(Flag):
    name = 'Randomize enemy stats'
    description = "Enemy stats and immunities/weaknesses will be randomized."
    inverse_description = ("(The enemies will retain their original attack, defense, m.attack, m.defense, speed, "
                           "weaknesses, and immunities.)")
    value = 'Es'


class EnemyDrops(Flag):
    name = 'Randomize enemy drops'
    description = "The EXP and items received from enemies will be randomized."
    inverse_description = "(Battle prize drops are unchanged from the original game.)"
    value = 'Ed'


class EnemyFormations(Flag):
    name = 'Randomize enemy formations'
    description = "Normal enemy battle formations will be randomized.  Boss formations are not affected."
    inverse_description = "(Random battle formations remain the same as in the original game.)"
    value = 'Ef'


class EnemyAttacks(Flag):
    name = 'Randomize enemy attacks'
    description = "Enemy spells and attacks will have their power and potential status effects randomized."
    inverse_description = ("(Base power and status casts of enemy spells and attacks are unchanged from the original "
                           "game.)")
    value = 'Ea'


class EnemyNoSafetyChecks(Flag):
    name = 'No safety checks'
    description = "Removes safety checks on enemy attack shuffle that prevent abnormally large effects."
    inverse_description = "(Enemy stat shuffling should not skew abnormally high.)"
    value = 'E!'
    hard = True


class EnemyShuffle(Flag):
    name = 'Randomize enemies'
    value = '@E'
    options = [
        EnemyDrops,
        EnemyFormations,
        EnemyStats,
        EnemyAttacks,
        EnemyNoSafetyChecks,
    ]


class BossShuffleCulex(Flag):
    name = 'Include Culex'
    inverse_description = "(Culex will remain in his door in Monstro Town.)"
    value = 'Bc'
    hard = True


class BossShuffleKeepStats(Flag):
    name = "Don't scale stats"
    description = "Boss stats will **not** be scaled to match the battle it's replacing."
    inverse_description = "(Turning the Bs flag off affirms that boss stats will indeed be scaled.)"
    value = 'Bs'
    hard = True


class BossShuffleMusic(Flag):
    name = 'Randomize boss music'
    description = 'Battle music will be randomized for each boss fight.'
    inverse_description = "(Battle music for each location will remain unchanged from the original game.)"
    value = 'Bm'


class BossShuffle(Flag):
    name = 'Randomize bosses'
    description = ("The positions of bosses are shuffled. By default, when a boss is moved, its stats are scaled to "
                   "match its new location.")
    inverse_description = "(Bosses will stay in their original locations.)"
    modes = ['open']
    value = 'B'
    options = [
        BossShuffleMusic,
        BossShuffleCulex,
        BossShuffleKeepStats,
    ]


# ******** Chest shuffle flags


class ChestTier1(Flag):
    name = "Restrict to worst items"
    description = "Only the very worst items will appear in chests and as sidequest rewards."
    value = 'T1'
    hard = True


class ChestTier2(Flag):
    name = "Restrict to weak items"
    description = "Only weak equipment and some support/healing items will appear in chests and as sidequest rewards."
    value = 'T2'


class ChestTier3(Flag):
    name = "Exclude best items"
    description = ("Out of all items that could appear in chests and as sidequest rewards, the very best items will be "
                   "left out.")
    value = 'T3'


class ChestTier4(Flag):
    name = "Include all items"
    description = "Any item may appear in a chest or sidequest reward (besides key items)."
    value = 'T4'


class ChestExcludeCoins(Flag):
    name = 'No Coins'
    description = "Chests will not contain coins."
    inverse_description = "(Chests may contain coins.)"
    value = 'Ty'


class ChestExcludeFrogCoins(Flag):
    name = 'No Frog Coins'
    description = "Chests will not contain frog coins."
    inverse_description = "(Chests may contain frog coins.)"
    value = 'Tz'


class ChestExcludeFlowers(Flag):
    name = 'No Flowers'
    description = "Chests will not contain FP flowers."
    inverse_description = "(Chests may contain FP flowers.)"
    value = 'Tf'


class ChestExcludeMushrooms(Flag):
    name = 'No Recovery Mushrooms'
    description = "Chests will not contain heal mushrooms."
    inverse_description = "(Chests may contain heal mushrooms.)"
    value = 'Tm'


class ChestExcludeStars(Flag):
    name = 'No Stars'
    description = "Chests will not contain invincibility stars."
    value = 'T!'
    hard = True


class ChestRandomizeStars(Flag):
    name = 'Shuffle Stars'
    description = "The number and locations of EXP stars are randomized."
    value = 'Tr'


class ChestStarShuffle(Flag):
    name = 'EXP Stars'
    inverse_description = "(EXP stars are not affected by chest shuffle.)"
    value = 'Ts'
    choices = [
        ChestRandomizeStars,
        ChestExcludeStars,
    ]


class ChestKIInclude3DMaze(Flag):
    name = 'Include 3D Maze'
    inverse_description = "(3D Maze will not have a key item.)"
    value = 'Td'


class ChestKIIncludeCulex(Flag):
    name = 'Include Culex\'s Lair'
    inverse_description = "(Culex's lair will not have a key item.)"
    value = 'Tu'
    hard = True


class ChestKIInclude30(Flag):
    name = 'Include 30 Super Jumps'
    inverse_description = "(30 Super Jumps will not have a key item.)"
    value = 'Th'
    hard = True


class ChestKIInclude100(Flag):
    name = 'Include 100 Super Jumps'
    inverse_description = "(100 Super Jumps will not have a key item.)"
    value = 'Ti'
    hard = True


class ChestIncludeKeyItems(Flag):
    name = 'Include Key Items'
    description = "Shuffled chests or sidequest rewards may contain a key item."
    inverse_description = ("(Chests and sidequest rewards will not contain key items, with the exception of the "
                           "Kero Sewers chest.)")
    value = 'Tk'
    hard = True
    options = [
        ChestKIInclude3DMaze,
        ChestKIIncludeCulex,
        ChestKIInclude30,
        ChestKIInclude100,
    ]


class ChestShuffleEmpty(Flag):
    name = 'Empty chests'
    description = 'All chests give the "You missed!" cutscene, and sidequest rewards give you nothing.'
    value = 'Tx'
    hard = True


class ChestShuffle1(Flag):
    name = 'Vanilla shuffle'
    description = ('Chest and sidequest reward contents are the same as the original game, but shuffled within the '
                   'same area.')
    value = 'Tv'
    choices = [
        ChestTier4,
        ChestTier3,
        ChestTier2,
        ChestTier1,
    ]
    options = [
        ChestExcludeCoins,
        ChestExcludeFrogCoins,
        ChestExcludeFlowers,
        ChestExcludeMushrooms,
        ChestExcludeStars,
    ]


class ChestShuffleBiased(Flag):
    name = 'Biased shuffle'
    description = "Chests and sidequest rewards that are harder to access will contain better items."
    value = 'Tb'
    choices = [
        ChestTier4,
        ChestTier3,
        ChestTier2
    ]
    options = [
        ChestExcludeCoins,
        ChestExcludeFrogCoins,
        ChestExcludeFlowers,
        ChestExcludeMushrooms,
        ChestStarShuffle,
        ChestIncludeKeyItems,
    ]


class ChestShuffleChaos(Flag):
    name = 'Chaotic shuffle'
    description = "Any chest or sidequest reward may contain anything."
    value = 'Tc'
    choices = [
        ChestTier4,
        ChestTier3,
        ChestTier2,
        ChestTier1,
    ]
    options = [
        ChestExcludeCoins,
        ChestExcludeFrogCoins,
        ChestExcludeFlowers,
        ChestExcludeMushrooms,
        ChestStarShuffle,
        ChestIncludeKeyItems,
    ]


class ChestShuffleFlag(Flag):
    name = 'Randomize untrapped chest contents & sidequest rewards'
    description = '(note that some locations will not be affected)'
    inverse_description = "(Chest and reward contents will remain unchanged from the original game.)"
    modes = ['open']
    value = '@T'
    choices = [
        ChestShuffleChaos,
        ChestShuffleBiased,
        ChestShuffle1,
        ChestShuffleEmpty,
    ]


class MonstroTownLite(Flag):
    name = 'Monstro rewards only'
    description = ('The Super Suit, Attack Scarf, Quartz Charm, Jinx Belt, and Ghost Medal locations will be shuffled '
                   'within each other.')
    value = 'M1'


class MonstroTownHard(Flag):
    name = 'Monstro rewards and key item rewards'
    description = ('The Super Suit, Attack Scarf, Quartz Charm, Jinx Belt, Ghost Medal, FroggieStick, Zoom Shoes, '
                   'Chomp, Lazy Shell Weapon, and Lazy Shell Armor locations will be shuffled within each other.')
    value = 'M2'


class MonstroExcludeElsewhere(Flag):
    name = 'Exclude elsewhere'
    description = ('The items shuffled by your selected option will not appear in any shops or any other chests or '
                   'reward spots.')
    value = 'Mx'
    hard = True


class MonstroTownShuffle(Flag):
    name = 'Monstro Town Shuffle'
    description = ('Randomize the locations of some special equips. These equips will not appear anywhere else in the '
                   'game.')
    inverse_description = '(The Monstro Town and key item equip rewards will not be shuffled within each other.)'
    modes = ['open']
    value = '@M'
    choices = [
        MonstroTownLite,
        MonstroTownHard,
    ]
    options = [
        MonstroExcludeElsewhere,
    ]


class ReplaceItems(Flag):
    name = 'Replace worst chest items with coins'
    description = 'The lowest ranked items will be replaced with coins in chests.'
    inverse_description = '(You may find low-ranked items in chests.)'
    modes = ['open']
    value = 'Tg'


# ******** Shop shuffle flags


class ShopTier1(Flag):
    name = "Restrict to worst items"
    description = "Only the very worst equipment and support/healing items will appear in shops."
    value = 'S1'
    hard = True


class ShopTier2(Flag):
    name = "Restrict to weak items"
    description = "Only weak equipment and some support/healing items will appear in shops."
    value = 'S2'


class ShopTier3(Flag):
    name = "Exclude best items"
    description = "Out of all items that could appear in shops, the very best items will be left out."
    value = 'S3'


class ShopTier4(Flag):
    name = "Include all items"
    description = "Any non-key item may appear in a shop."
    value = 'S4'


class ShopShuffleVanilla(Flag):
    name = "Vanilla shop inventory"
    description = ("Shops will only contain items that were available in the original game's shops, shuffled amongst "
                   "each other.")
    value = 'Sv'
    choices = [
        ShopTier4,
        ShopTier3,
        ShopTier2,
        ShopTier1
    ]


class ShopShuffleBalanced(Flag):
    name = "Biased shop inventory"
    description = "Shops that are harder to access will contain better items."
    value = 'Sb'
    choices = [
        ShopTier4,
        ShopTier3,
        ShopTier2
    ]


class ShopShuffleChaotic(Flag):
    name = "Chaotic shop inventory"
    description = "Any shop may contain anything."
    value = 'Sc'
    choices = [
        ShopTier4,
        ShopTier3,
        ShopTier2,
        ShopTier1
    ]


class ShopTierX(Flag):
    name = "Empty shops"
    description = "All shops contain only the Goodie Bag."
    value = 'Sx'
    hard = True


class ShopShuffle(Flag):
    name = 'Randomize shops'
    description = "Shop contents and prices will be shuffled"
    inverse_description = "(Shop contents and item prices remain unchanged from the original game.)"
    value = '@S'
    choices = [
        ShopShuffleChaotic,
        ShopShuffleBalanced,
        ShopShuffleVanilla,
        ShopTierX
    ]


class FreeShops(Flag):
    name = "'Free' Shops"
    description = "All shop items will cost 1 coin. You will start with 9999 coins and 99 frog coins."
    inverse_description = "(Shops are not free, and you start with 0 coins.)"
    value = 'Sf'


# ******** Item shuffle flags

class EquipmentStats(Flag):
    name = 'Randomize equipment stats'
    description = "Attack, defense, magic attack, magic defense, and speed granted by equipment will be randomized"
    inverse_description = ("(Attack, defense, magic attack, magic defense, and speed granted by equipment remain "
                           "unchanged from the original game.)")
    value = 'Qs'


class EquipmentBuffs(Flag):
    name = 'Randomize equipment buffs'
    description = ("Special buffs granted by equipment will be randomized (attack/defense boost, "
                   "elemental/status immunities).  See Resources page for an explanation of these.")
    inverse_description = ("(Immunities and boost multipliers granted by equipment remain unchanged from the original "
                           "game.)")
    value = 'Qb'


class EquipmentCharacters(Flag):
    name = 'Randomize allowed characters'
    description = "Each equip's list of characters that can wear it will be randomized."
    inverse_description = ("(Each equip's list of characters that can wear it will remain unchanged from the original "
                           "game.)")
    value = 'Qa'


class EquipmentNoSafetyChecks(Flag):
    name = 'No safety checks'
    description = ("Normally certain namesake items retain their protections: **Fearless Pin**, **Antidote Pin**, "
                   "**Trueform Pin**, and **Wakeup Pin**.  In addition, at least four equipment will have instant KO "
                   "protection.  This flag removes those checks.")
    inverse_description = ("(Namesake properties such as **Fearless Pin**, **Antidote Pin**, **Trueform Pin**, and "
                           "**Wakeup Pin** remain intact, and at least four pieces of equipment will have instant "
                           "KO protection.)")
    value = 'Q!'
    hard = True


class EquipmentShuffle(Flag):
    name = 'Randomize equipment'
    value = '@Q'
    options = [
        EquipmentStats,
        EquipmentBuffs,
        EquipmentCharacters,
        EquipmentNoSafetyChecks,
    ]


# ******** Experience

class ExperienceBoost2x(Flag):
    name = 'Double XP'
    description = 'XP is doubled'
    value = 'X2'


class ExperienceBoost3x(Flag):
    name = 'Triple XP'
    description = 'XP is tripled to simulate no XP split'
    value = 'X3'


class ExperienceBoost(Flag):
    name = 'XP boost'
    description = 'Earned experience points are increased for faster levelling.'
    inverse_description = "(Earned experience points are the same as the vanilla game.)"
    value = '@X'
    choices = [
        ExperienceBoost2x,
        ExperienceBoost3x,
    ]


class ExperienceNoRegular(Flag):
    name = 'No XP from regular encounters'
    description = 'Only bosses will award XP.'
    inverse_description = "(You will receive EXP from all fights normally.)"
    value = 'Xx'
    hard = True


# ******** Star exp progression challenge

class StarExp1(Flag):
    name = 'Balanced'
    description = ("* 0 stars - 2 exp\n"
                   "* 1 star - 4 exp\n"
                   "* 2 stars - 5 exp\n"
                   "* 3 stars - 6 exp\n"
                   "* 4 stars - 8 exp\n"
                   "* 5 stars - 9 exp\n"
                   "* 6/7 stars - 11 exp")
    value = 'P1'


class StarExp2(Flag):
    name = 'Difficult'
    description = ("* 0 stars - 1 exp\n"
                   "* 1 star - 2 exp\n"
                   "* 2 stars - 3 exp\n"
                   "* 3 stars - 5 exp\n"
                   "* 4 stars - 6 exp\n"
                   "* 5 stars - 7 exp\n"
                   "* 6/7 stars - 11 exp")
    value = 'P2'
    hard = True


class StarExpChallenge(Flag):
    name = 'Star EXP progression challenge'
    description = 'Invincibility stars give exp based on the number of star pieces collected.'
    inverse_description = '(Invincibility stars grant the amount of EXP given in the original game.)'
    modes = ['open']
    value = '@P'
    choices = [
        StarExp1,
        StarExp2,
    ]


# ******** Minigame challenges


class BallSolitaireShuffle(Flag):
    name = 'Randomize Ball Solitaire'
    description = 'The layout for the Ball Solitaire minigame will be randomized.'
    inverse_description = '(Ball Solitaire minigame will be the same as vanilla.)'
    value = 'Nb'


class MagicButtonShuffle(Flag):
    name = 'Randomize Magic Buttons'
    description = 'The layout for the Magic Buttons minigame will be randomized.'
    inverse_description = '(Magic Buttons minigame will be the same as vanilla.)'
    value = 'Nm'


class QuizShuffle(Flag):
    name = 'Randomize Dr. Topper quiz'
    description = 'The question pool for the Dr. Topper quiz will include new unique questions.'
    inverse_description = '(Dr. Topper quiz question pool will be the same as vanilla.)'
    value = 'Nq'


class Minigames(Flag):
    name = 'Minigames'
    modes = ['open']
    value = '@N'
    options = [
        BallSolitaireShuffle,
        MagicButtonShuffle,
        # TODO: Uncomment this when the quiz shuffle is implemented!
        # QuizShuffle,
    ]


# ******** Glitches

class NoGenoWhirlExor(Flag):
    name = 'No Geno Whirl on Exor'
    description = 'Fixes the Exor bug where he is vulnerable to Geno Whirl when the eyes are stunned.'
    inverse_description = ('(You may used a Timed Hit Geno Whirl to instantly KO Exor when its eye protection is '
                           'removed.)')
    value = 'Ge'
    hard = True


class FixMagikoopa(Flag):
    name = "Fix Magikoopa"
    description = 'Fixes Magikoopa bug after King Bomb explodes that prevents him from taking further actions.'
    inverse_description = '(Magikoopa will remain disabled for the remainder of the fight if King Bomb uses Big Bang.)'
    value = 'Gm'


class NoMackSkip(Flag):
    name = "No Mack Skip"
    description = 'You will not be able to skip the boss in Mushroom Kingdom.'
    inverse_description = '(You may attempt to skip the boss in Mushroom Kingdom.)'
    value = 'Gs'


class NoOHKO(Flag):
    name = "No instant KOs on boss allies"
    description = ('You will not be able to use Geno Whirl or Pure Water to OHKO any allies to a boss (Mallow Clone, '
                   'Mad Mallet, Fautso, etc).')
    inverse_description = ('(Some boss allies may be susceptible to Geno Whirl, and Belome 2\'s clones will still be '
                           'susceptible to Pure Water.)')
    value = 'Gk'


class Glitches(Flag):
    name = 'Boss Glitch & Exploit Removals'
    modes = ['open']
    value = '@G'
    options = [
        NoMackSkip,
        FixMagikoopa,
        NoOHKO,
        NoGenoWhirlExor,
    ]


class PoisonMushroom(Flag):
    name = 'Change Fake Mushroom\'s Status'
    description = 'Randomize the status effect inflicted on a party member with the Fake Mushroom.'
    inverse_description = '(The Fake Mushroom will always turn you into a mushroom.)'
    mode = ['open']
    value = '-fakeout'


# ************************************** Category classes

class FlagCategory:
    name = ''
    flags = []


class KeyItemsCategory(FlagCategory):
    name = 'Key Items/Star Pieces'
    flags = [
        KeyItemShuffle,
        StarPieceShuffle,
    ]


class CharactersCategory(FlagCategory):
    name = 'Characters'
    flags = [
        CharacterShuffle,
    ]


class EnemiesCategory(FlagCategory):
    name = 'Enemies/Bosses'
    flags = [
        EnemyShuffle,
        BossShuffle,
    ]


class ChestCategory(FlagCategory):
    name = 'Treasures & Rewards'
    flags = [
        ChestShuffleFlag,
        ReplaceItems,
        MonstroTownShuffle,
    ]


class ShopsItemsCategory(FlagCategory):
    name = 'Shops'
    flags = [
        ShopShuffle,
        FreeShops
    ]


class EquipsCategory(FlagCategory):
    name = 'Equipment'
    flags = [
        EquipmentShuffle,
    ]


class BattlesCategory(FlagCategory):
    name = 'Battles'
    flags = [
        ExperienceBoost,
        ExperienceNoRegular,
    ]


class ChallengesCategory(FlagCategory):
    name = 'Challenges'
    flags = [
        StarExpChallenge,
        Minigames,
    ]


class TweaksCategory(FlagCategory):
    name = 'Tweaks'
    flags = [
        Glitches,
        PoisonMushroom,
    ]


# ************************************** Preset classes

class Preset:
    name = ''
    description = ''
    flags = ''


class CasualPreset(Preset):
    name = 'Casual'
    description = 'Basic flags for a casual playthrough of the game.'
    flags = 'K R Csj Edf B Tc4yg M1 Sc4 Qa X2'


class IntermediatePreset(Preset):
    name = 'Intermediate'
    description = 'A mild increase in difficulty compared to casual.'
    flags = 'Ks R7 Cspjl Edf B Tc3yg M1 Sb4 Qsa X2'


class AdvancedPreset(Preset):
    name = 'Advanced'
    description = 'More difficult options for advanced players, requiring you to manage your equips more.'
    flags = 'Ks R7k Cspjl Edfsa Bc Tb2kd M2 Sb2 Qsba X2 P1 Gm -fakeout'


class ExpertPreset(Preset):
    name = 'Expert'
    description = 'A highly chaotic shuffle with everything difficult enabled and helpful glitches disabled.'
    flags = 'Ks R7kc Cspjl Edfsa! Bmcs Tb2kduhi M2x Sv1 Qsba! X2x P2 Gsmke -fakeout'


# ************************************** Default lists for the site.

# List of categories for the site.
CATEGORIES = (
    KeyItemsCategory,
    CharactersCategory,
    ChestCategory,
    ShopsItemsCategory,
    EnemiesCategory,
    EquipsCategory,
    BattlesCategory,
    ChallengesCategory,
    TweaksCategory,
)

# List of presets.
PRESETS = (
    CasualPreset,
    IntermediatePreset,
    AdvancedPreset,
    ExpertPreset,
)
