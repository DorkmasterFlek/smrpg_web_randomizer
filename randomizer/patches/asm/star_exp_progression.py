"""Star EXP progression curve for the "Star Pieces" / "Bosses" EXP challenge.

The battle engine reads per-hit Invincibility Star EXP from a word table at
ROM $39:BC44. Event 3072 (E3072_FLOWER_STAR_FC_OR_MUSHROOM_CHEST) picks the
entry: it copies $70A7 (ITEM_ID) into $7000, masks it with 0x000F, and hands
the low nibble to SetEXPPacketTo7000. The high nibble (0x10) is what marked
the chest an EXP star in the dispatch further up the script, so only bits
0-3 select a table index.

Vanilla table (word entries, high byte always 0)::

    idx  0   1   2   3   4   5   6   7   8   9  10-13
    exp  1   2   5   8  13  11   0   5   6   9    0

In the default ("Vanilla") EXP star mode both progression bits are clear,
event 3072 falls straight through to EVENT_3072_copy_var_to_var_81, and each
star chest keeps the index baked into its own EXPStarPrize - which is how the
vanilla per-location amounts (1/2/5/8/11/5/6/9) are reproduced. This module
must not be applied in that mode.

When PROGRESSIVE_STAR_EXP_ENABLED or PROGRESSIVE_BOSS_EXP_ENABLED is set,
event 3072 *overwrites* $70A7 before the mask, so the chest's own index is
discarded and the index comes from progress instead:

    star pieces   0    1    2    3    4    5   6/7
    bosses beat   0   1+   3+   6+  10+  15+   21+
    table index   0    1    2    3    4    5     7

Left on the vanilla table that yields 1, 2, 5, 8, 13, 11, 5 - which peaks at
4 stars and then *falls*, so the "progression" regresses. This module writes
the curve the upstream randomizer used for this challenge's "Balanced"
setting (StarExp1, flag value P1) so the reward actually climbs::

    exp   2    4    5    6    8    9    11

Table index 6 is deliberately left at its vanilla value: no progress tier and
no EXPStarPrize ever selects it, and upstream skipped $39:BC50 for the same
reason. Indices 8 and 9 (the Land's End star-2 / star-3 prizes) are likewise
untouched - they are unreachable while either progression bit is set.

Mutually exclusive with :mod:`no_exp`, which zeroes the whole table. The
no-EXP path (EXPChallenge NONE, godmode, or debug mode) also rewrites event
3072's SetVarToConst operands to 0 and never sets either progression bit, so
the caller must gate these two patches as if/elif, not two independent ifs.
"""

# ROM offset of table index 0. Entries are 2 bytes apart; only the low byte
# carries a value, so each write is a single byte at an even offset.
_EXP_TABLE = 0x39BC44

# Balanced curve, by table index. Index 6 is absent on purpose (see above).
_BALANCED = {
    0: 2,   # 0 star pieces  / 0 bosses
    1: 4,   # 1 star piece   / 1+ bosses
    2: 5,   # 2 star pieces  / 3+ bosses
    3: 6,   # 3 star pieces  / 6+ bosses
    4: 8,   # 4 star pieces  / 10+ bosses
    5: 9,   # 5 star pieces  / 15+ bosses
    7: 11,  # 6-7 star pieces / 21+ bosses
}


def get_patch() -> dict[int, bytes]:
    return {
        _EXP_TABLE + index * 2: bytes([exp]) for index, exp in _BALANCED.items()
    }
