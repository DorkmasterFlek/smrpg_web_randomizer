# Flag definitions and logic.

from django.utils.html import mark_safe
from markdown import markdown


# ************************************** Flag classes

class Flag:
    """Class representing a flag with its description, and possible values/choices/options."""
    name = ''
    description = ''
    value = ''
    hard = False
    modes = ['linear', 'open']
    choices = []
    options = []

    @classmethod
    def description_as_markdown(cls):
        return mark_safe(markdown(cls.description, safe_mode='escape'))

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
    description = ("You must find seven star pieces instead of six to open the final area.")
    value = 'R7'
    modes = ['open']


class BowsersKeepOpen(Flag):
    name = "Include Bowser's Keep locations"
    description = ("Bowser's Keep is open from the start and the boss locations inside the keep may have star pieces.  "
                   "The Factory will be opened once you find all star pieces.")
    value = 'Rk'
    modes = ['open']


class CulexStarShuffle(Flag):
    name = "Include Culex's Lair"
    description = "Culex's Lair in Monstro Town may have a star piece."
    value = 'Rc'
    hard = True
    modes = ['open']


class StarPieceShuffle(Flag):
    name = 'Randomize star pieces'
    description = ("Assigns six star pieces to random boss locations, excluding Culex's Lair, Bowser's Keep, and the Factory. Collect all the star pieces to open Bowser's Keep and progress to the end of the game.")
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
    value = 'Ks'
    modes = ['open']


class KeyItemShuffle(Flag):
    name = 'Randomize key items'
    description = ("The locations of key items are shuffled amongst each other.  For example, you may find the "
                   "Shed Key at Croco 1 instead of the Rare Frog Coin.\n\nThe items randomized this way are the "
                   "**Rare Frog Coin**, **Cricket Pie**, **Bambino Bomb**, **Castle Key 1**, **Castle Key 2**, "
                   "**Alto Card**, **Tenor Card**, **Soprano Card**, **Greaper Flag**, **Dry Bones Flag**, "
                   "**Big Boo Flag**, **Shed Key**, **Elder Key**, **Cricket Jam**, **Temple Key**, and **Room Key**.")
    value = 'K'
    modes = ['open']
    options = [
        IncludeSeedFertilizer,
    ]


# ******** Character shuffle flags

class CharacterStats(Flag):
    name = 'Randomize character stats'
    description = "Stats for each character will be randomized."
    value = 'Cs'


class CharacterJoinOrder(Flag):
    name = 'Randomize character join order'
    description = ("Characters join your party at the same spots, but the character you get there is randomized.  The "
                   "character that joins the party will have their stats and starting level scaled for that spot.")
    value = 'Cj'


class CharacterLearnedSpells(Flag):
    name = 'Randomize character learned spells'
    description = "The spells each character learns and what level they learn them are randomized."
    value = 'Cl'


class CharacterSpellStats(Flag):
    name = 'Randomize character spell stats'
    description = "The power and FP cost of character magic spells will be randomized."
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
    value = 'Es'


class EnemyDrops(Flag):
    name = 'Randomize enemy drops'
    description = "The EXP and items received from enemies will be randomized."
    value = 'Ed'


class EnemyFormations(Flag):
    name = 'Randomize enemy formations'
    description = "Normal enemy battle formations will be randomized.  Boss formations are not affected."
    value = 'Ef'


class EnemyAttacks(Flag):
    name = 'Randomize enemy attacks'
    description = "Enemy spells and attacks will have their power and potential status effects randomized."
    value = 'Ea'


class EnemyNoSafetyChecks(Flag):
    name = 'No safety checks'
    description = "Removes safety checks on enemy attack shuffle that prevent abnormally large effects."
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
    value = 'Bc'
    hard = True


class BossShuffleKeepStats(Flag):
    name = "Don't scale stats"
    description = "Boss stats will **not** be scaled to match the battle it's replacing."
    value = 'Bs'
    hard = True


class BossShuffleMusic(Flag):
    name = 'Randomize boss music'
    description = 'Battle music will be randomized for each boss fight.'
    value = 'Bm'


class BossShuffle(Flag):
    name = 'Randomize bosses'
    description = ("The positions of bosses are shuffled. Boss stats are roughly scaled to match the battle it's "
                   "replacing. For example, Yaridovich in Bandit's Way would have the HP and stats of Croco 1, but can still cast powerful magic like Water Blast. "
                   "Save often.")
    modes = ['open']
    value = 'B'
    options = [
        BossShuffleMusic,
        BossShuffleCulex,
        BossShuffleKeepStats,
    ]


# ******** Item shuffle flags

class ShopShuffleVanilla(Flag):
    name = "Vanilla shop inventory"
    description = "Shops will only contain items that were available in the original game's shops, shuffled amongst each other."
    value = 'Sv'

class ShopShuffleBalanced(Flag):
    name = "Biased shop inventory"
    description = "Shops that are harder to access will contain better items."
    value = 'Sb'
    
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
    
class ShopShuffle(Flag):
    name = 'Randomize shops'
    description = "Shop contents and prices will be shuffled"
    value = 'S'
    choices = [
        ShopTier4,
        ShopTier3,
        ShopTier2,
        ShopTier1
    ]
    options = [
        ShopShuffleVanilla,
        ShopShuffleBalanced
    ]


class FreeShops(Flag):
    name = "'Free' Shops"
    description = "All shop items will cost 1 coin. You will start with 9999 coins and 99 frog coins."
    value = '$'
    
class EquipmentStats(Flag):
    name = 'Randomize equipment stats'
    description = "Stats for equipment will be randomized"
    value = 'Qs'

class ShopInclusion(Flag):
    name = 'Randomize shops'
    description = "Shop contents and prices will be shuffled"
    value = 'S'
    options = [
        SevenStarHunt,
        BowsersKeepOpen,
        CulexStarShuffle,
    ]


class EquipmentBuffs(Flag):
    name = 'Randomize equipment buffs'
    description = ("Special buffs granted by equipment will be randomized (attack/defense boost, "
                   "elemental/status immunities).  See Resources page for an explanation of these.")
    value = 'Qb'


class EquipmentCharacters(Flag):
    name = 'Randomize allowed characters'
    description = "Characters able to equip items will be randomized."
    value = 'Qa'


class EquipmentNoSafetyChecks(Flag):
    name = 'No safety checks'
    description = ("Normally certain namesake items retain their protections: **Fearless Pin**, **Antidote Pin**, "
                   "**Trueform Pin**, and **Wakeup Pin**.  In addition, at least four equipment will have instant KO "
                   "protection.  This flag removes those checks.")
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

class ExperienceSharing(Flag):
    name = 'XP sharing'
    description = 'Earned experience points are not divided among your party members; each receives the full amount.'
    value = 'Xs'


class ExperienceNoRegular(Flag):
    name = 'No XP from regular encounters'
    description = 'Bosses still award XP.'
    value = 'Xx'
    hard = True


class ExperienceFlag(Flag):
    name = 'Experience'
    value = '@X'
    options = [
        ExperienceSharing,
        ExperienceNoRegular,
    ]


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
    modes = ['open']
    value = '@P'
    choices = [
        StarExp1,
        StarExp2,
    ]


# ******** Glitches

class NoGenoWhirlExor(Flag):
    name = 'No Geno Whirl on Exor'
    description = 'Fixes the Exor bug where he is vulnerable to Geno Whirl when the eyes are stunned.'
    value = 'Ge'
    hard = True


class FixMagikoopa(Flag):
    name = "Fix Magikoopa"
    description = 'Fixes Magikoopa bug after King Bomb explodes that prevents him from taking further actions.'
    value = 'Gm'


class Glitches(Flag):
    name = 'Glitches'
    modes = ['open']
    value = '@G'
    options = [
        FixMagikoopa,
        NoGenoWhirlExor,
    ]


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
        ExperienceFlag,
    ]


class ChallengesCategory(FlagCategory):
    name = 'Challenges'
    flags = [
        StarExpChallenge,
    ]


class TweaksCategory(FlagCategory):
    name = 'Tweaks'
    flags = [
        Glitches,
    ]


# ************************************** Preset classes

class Preset:
    name = ''
    description = ''
    flags = ''


class CasualPreset(Preset):
    name = 'Casual'
    description = 'Basic flags for a casual playthrough of the game.'
    flags = 'K R Csj Edf B S Qa Xs'


class IntermediatePreset(Preset):
    name = 'Intermediate'
    description = 'A mild increase in difficulty compared to casual.'
    flags = 'Ks R7 Cspjl Edf B S Qsa Xs'


class AdvancedPreset(Preset):
    name = 'Advanced'
    description = 'More difficult options for advanced players, requiring you to manage your equips more.'
    flags = 'Ks R7k Cspjl Edfsa Bc S Qsba Xs P1 Gm'


class ExpertPreset(Preset):
    name = 'Expert'
    description = 'A highly chaotic shuffle with everything possible enabled and helpful glitches disabled.'
    flags = 'Ks R7kc Cspjl Edfsa! Bmcs S Qsba! Xsx P2 Gme'


# ************************************** Default lists for the site.

# List of categories for the site.
CATEGORIES = (
    KeyItemsCategory,
    CharactersCategory,
    EnemiesCategory,
    ShopsItemsCategory,
    EquipsCategory,
    BattlesCategory,
    ChallengesCategory,
    TweaksCategory,
)

# List of flags flattened out from categories, as well as all their options.
FLAGS = []
for category in CATEGORIES:
    for flag in category.flags:
        FLAGS.append(flag)
        for option in flag.options:
            FLAGS.append(option)

# List of presets.
PRESETS = (
    CasualPreset,
    IntermediatePreset,
    AdvancedPreset,
    ExpertPreset,
)
