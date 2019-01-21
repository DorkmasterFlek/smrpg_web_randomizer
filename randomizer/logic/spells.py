# Spell randomization logic.

from . import utils

from randomizer.data import spells


def _randomize_spell(spell):
    """Perform randomization for this spell.

    Args:
        spell(randomizer.data.spells.Spell):
    """
    spell.fp = utils.mutate_normal(spell.fp, minimum=1, maximum=99)

    # Don't shuffle power for Geno Boost, it causes problems if it deals damage.
    if not isinstance(spell, spells.GenoBoost):
        spell.power = utils.mutate_normal(spell.power)

    # Don't shuffle hit rate for healing spells or Geno Boost.  We don't want those to ever be able to miss.
    if not isinstance(spell, (spells.GenoBoost, spells.Therapy, spells.GroupHug, spells.HPRain, spells.Recover,
                              spells.MegaRecover)):
        # If the spell is instant death, cap hit rate at 99% so items that protect from this actually work.
        # Protection forces the attack to miss, but 100% hit rate can't "miss" so it hits anyway.
        if spell.instant_ko:
            max_hit_rate = 99
        else:
            max_hit_rate = 100
        spell.hit_rate = utils.mutate_normal(spell.hit_rate, minimum=1, maximum=max_hit_rate)


def randomize_all(world):
    """Randomize everything for spells for a single seed.

    :type world: randomizer.logic.main.GameWorld
    """
    if world.settings.randomize_spell_stats:
        # Randomize spell stats.
        for spell in world.spells:
            _randomize_spell(spell)

        # Randomize starting FP if we're randomizing spell stats.
        world.starting_fp = utils.mutate_normal(world.starting_fp, minimum=1, maximum=99)

    # If we're generating a debug mode seed for testing, set max FP to start.
    if world.debug_mode:
        world.starting_fp = 99
