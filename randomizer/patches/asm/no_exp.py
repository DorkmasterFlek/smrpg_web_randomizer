"""Zero out the EXP table.

Used when one of the following is true:

* EXPChallenge is set to NONE (no-EXP run).
* BossShuffleScaleStats is set to GODMODE.
* Debug mode is enabled.

Zeroes the per-hit Invincibility Star EXP table at ROM $39:BC44.
Event 3072 indexes this with the low nibble of $70A7 (see
:mod:`star_exp_progression` for the index scheme). The table is 10 word
entries, indices 0-9, ending at $39:BC57. Index 9 is the highest any star
chest or progression tier selects, so 20 zero bytes covers every reachable
entry.

Do not widen this write.
"""


def get_patch() -> dict[int, bytes]:
    return {0x39BC44: bytes(20)}
