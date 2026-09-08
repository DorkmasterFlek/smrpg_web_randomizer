from __future__ import annotations
import random
from typing import TYPE_CHECKING

from ...types.flags import (
    RandomTadpolePondSong, RandomSunkenShipPassword,
    MarioPaletteChoice, MallowPaletteChoice, GenoPaletteChoice,
    BowserPaletteChoice, ToadstoolPaletteChoice,
)
from smrpgpatchbuilder.datatypes.numbers.classes import ByteField

if TYPE_CHECKING:
    from ...types.gameworld import GameWorld


"""
IMPORTANT NOTES ABOUT MODIFYING:
* The fontset is only UPPER CASE A-Z, space and period. Everything else looks like a space.
* The font/color is dependant on the Y position. Dunno why.
* Credits space is very limited. If we run out of cards, can't add more cards, but could add more titles to those cards.
** Changing this might be hard.
** Dunno if the length is hard coded in the code, or if moving the string table would solve the space problem.
* Watch the whole credits! There's a chance it can freeze at the end or corrupt the firework screen if you do it wrong.

"""

EMPTY_STRING = "                                       "

END_CREDITS_DELAY_1 = 34
END_CREDITS_DELAY_2 = 40
BEGIN_TITLES_DELAY = 50
END_TITLES_DELAY = 40

# Blank pause before the dedication, in credits "delay units" (summed end_thing
# delay bytes; ~1.5 real frames each), spread across the byte-fill blocks. The
# memorial is tuned to fade in ~4:38 into the credits music; added panels
# (tadpole/sunken) pushed it to ~5:04, so the pause is trimmed to pull it back.
# Keep this >= 2x the filler block count (~48) so BOTH delay halves of every
# block stay nonzero, matching the legacy (23,23) blocks - the earlier pause=0
# attempt gave all-zero delays and the dedication vanished. If the memorial ever
# fails to render, raise this (1012 = the legacy value, definitely in-window but
# lands it late).
PRE_MEMORIAL_PAUSE_UNITS = 60

# Each filler block carries two single-byte frame delays; keep each half <= 127
# to stay well inside the proven range, so one block holds up to 254 frames.
MAX_FILLER_DELAY = 127

# The dedication is tuned to fade in at a fixed point in the credits music
# (~4:38). The number of real panels before it VARIES by seed (tadpole / sunken
# / palette panels add content), so the filler count is COMPUTED to compensate:
# more content => fewer filler panels, keeping the dedication's wall-clock time
# constant. finalize() estimates the content's running time from its measured
# transition count, then sizes the filler to reach the target. These are
# stopwatch-calibrated approximations - change MEMORIAL_FADE_SECONDS to move the
# target; nudge the two rates if the fit drifts. The credits engine spends a
# large fixed time per panel TRANSITION, so only the filler COUNT matters for
# timing (the byte-padding draws inside each panel are nearly free).
MEMORIAL_FADE_SECONDS = 4 * 60 + 38   # 4:38 - when the dedication should fade in
CREDITS_INTRO_SECONDS = 15            # run-up before the first credit panel
SEC_PER_CONTENT_EVENT = 1.83          # avg seconds per real-content transition
SEC_PER_FILLER_PANEL = 4.7            # seconds the engine spends per filler panel


def to_str(string):
    return (
        "".join([chr(i + ord("A") - 1) for i in string])
        .replace("\\", " ")
        .replace("[", ".")
    )


def inv_str(string: str) -> bytes:
    """Convert a credits string to ROM bytes.

    Format: length byte followed by encoded characters where A=1, B=2, etc.
    Special characters: space='\\', period='[', underscore=']'
    """
    string = string.replace(" ", "\\").replace(".", "[").replace("_", "]")
    length_byte = bytes([len(string)])
    char_bytes = bytes([ord(c) - ord("A") + 1 for c in string])
    return length_byte + char_bytes

# There's a way to do perfect allocations with DYNAMIC PROGRAMMING,
# but I'm not doing that.
def allocate_string(string_length: int, free_list: dict[int, int]) -> int | None:
    for base in sorted(free_list, key=lambda x: free_list[x]):
        if free_list[base] >= string_length:
            size = free_list[base]
            del free_list[base]
            free_list[base + string_length] = size - string_length
            return base
    # If we get this far, we couldn't find space for the string.
    return None


def _distribute_filler_frames(
    num_blocks: int, total_frames: int
) -> list[tuple[int, int]]:
    """Split total_frames across num_blocks invisible filler blocks.

    Each block gets one delay pair (d1, d2); the sum across all blocks equals
    total_frames exactly, so the pre-dedication pause is independent of how many
    blocks the byte budget happens to allow. Frames are spread as evenly as
    possible and each half stays <= MAX_FILLER_DELAY (the single-byte delay cap).
    """
    if num_blocks <= 0:
        return []
    base, extra = divmod(total_frames, num_blocks)
    blocks: list[tuple[int, int]] = []
    for i in range(num_blocks):
        frames = base + (1 if i < extra else 0)
        d1 = (frames + 1) // 2
        d2 = frames // 2
        assert d1 <= MAX_FILLER_DELAY and d2 <= MAX_FILLER_DELAY, (
            f"filler block delay {d1}/{d2} exceeds {MAX_FILLER_DELAY}; "
            f"too few blocks ({num_blocks}) for {total_frames} frames"
        )
        blocks.append((d1, d2))
    return blocks


class Credits(object):
    def __init__(self, table_offset=0):
        self.strings = {}
        self.inv_strings = {}
        self.acc: list[int] = []
        self.tail: list[int] = []
        self._saved_acc: list[int] | None = None
        self.table_offset = table_offset
        self.current_credits = []
        self.current_titles = []
        # Count of credit "transitions" (end_thing* calls). Snapshotted at
        # begin_tail() into main_events to size the compensating filler.
        self.content_events: int = 0
        self.main_events: int | None = None

    def begin_tail(self):
        """Redirect subsequent builder calls into the tail buffer.

        Tail content is emitted by finalize() after the invisible filler
        padding, so it plays as the very last real panel of the credits.
        """
        assert self._saved_acc is None, "begin_tail already active"
        assert not self.tail, "tail already populated"
        self.main_events = self.content_events
        self._saved_acc = self.acc
        self.acc = self.tail

    def end_tail(self):
        """Stop redirecting to the tail; restore the main accumulator."""
        assert self._saved_acc is not None, "begin_tail not active"
        self.acc = self._saved_acc
        self._saved_acc = None

    def add(self, x, y, font, string, scroll=0):
        assert len(string) <= len(EMPTY_STRING)
        if string in self.inv_strings:
            dex = self.inv_strings[string]
        else:
            dex = len(self.strings) + self.table_offset
            self.strings[dex] = string
            self.inv_strings[string] = dex
        self.acc += [0xE3, 0x12, dex, x, y, font, scroll]

    def end_thing(self, delay):
        self.content_events += 1
        self.acc += [
            0xE3,
            0x00,
            0x0F,
            0x02,
            0x0B,
            0x16,
            0x00,
            0x01,
            0x03,
            0x04,
            0x10,
            delay,
            0x01,
        ]

    def end_thing_2(self, delay):
        self.content_events += 1
        self.acc += [
            0xE3,
            0x00,
            0x0F,
            0x02,
            0x16,
            0x0B,
            0x00,
            0x01,
            0x03,
            0x04,
            0x10,
            delay,
            0x00,
        ]

    def end_thing_3(self, delay):
        self.content_events += 1
        self.acc += [
            0xE3,
            0x00,
            0x0F,
            0x02,
            0x16,
            0x0B,
            0x00,
            0x09,
            0x0B,
            0x04,
            0x10,
            delay,
            0x00,
        ]

    def end_thing_4(self, delay):
        self.content_events += 1
        self.acc += [
            0xE3,
            0x00,
            0x0F,
            0x02,
            0x0B,
            0x16,
            0x00,
            0x09,
            0x0B,
            0x04,
            0x10,
            delay,
            0x00,
        ]

    def clear(self, words):
        for x, y, font in words:
            self.add(x, y, font, EMPTY_STRING)
        del words[:]

    # Yeah, got into a OpenGL vibe here.
    def begin_credits(self):
        pass

    def add_credit(self, x, y, font, string, scroll=0):
        self.current_credits.append((x, y, font))
        self.add(x, y, font, string, scroll)  # 7

    def end_credits(self, delay_1, delay_2):  # 26
        self.end_thing(delay_1)
        self.end_thing_2(delay_2)
        self.clear(self.current_credits)

    def begin_titles(self, delay):
        self.end_thing_3(delay)  # 13
        self.clear(self.current_titles)  # 7

    def add_title(self, x, y, font, string, scroll=0):
        self.current_titles.append((x, y, font))
        self.add(x, y, font, string, scroll)  # 7

    def end_titles(self, delay):
        self.end_thing_4(delay)  # 13

    def empty_title(self):
        self.acc += [0xE3, 0, 0, 0, 0, 0, 0]

    def finalize(self) -> dict[int, bytearray]:
        assert self._saved_acc is None, "begin_tail never closed before finalize"
        credit_start = 0x3FDBB0
        credit_len = 3380
        string_table_start = 0x3FE8E4
        string_table_size = len(self.strings) * 2

        # Layout plan (deterministic):
        #   [main content] [pre-dedication filler panels] [dedication] [0x02 idle]
        # The filler panels are invisible blank transitions whose COUNT positions
        # the dedication at the target wall-clock time; the trailing 0x02 idle
        # command freezes the engine on the blank post-dedication screen until the
        # music ends and the fireworks take over (see below).
        filler_budget = credit_len - len(self.acc) - len(self.tail)
        assert filler_budget >= 1, (
            f"main ({len(self.acc)}) + tail ({len(self.tail)}) leave no room in "
            f"{credit_len} bytes for the idle terminator; reduce main content"
        )
        # Size the filler so the dedication is reached at ~MEMORIAL_FADE_SECONDS:
        # estimate the content's running time from its measured transition count,
        # then add enough invisible blank filler panels (each ~SEC_PER_FILLER_PANEL
        # of engine time) to reach the target. More seed content => fewer filler
        # panels, so the dedication's wall-clock time stays constant. Clamp to the
        # byte budget (26 B per empty panel: end_thing + end_thing_2).
        main_events = (
            self.content_events if self.main_events is None else self.main_events
        )
        content_seconds = CREDITS_INTRO_SECONDS + main_events * SEC_PER_CONTENT_EVENT
        panels = round((MEMORIAL_FADE_SECONDS - content_seconds) / SEC_PER_FILLER_PANEL)
        # Clamp to the byte budget, reserving >=1 byte for the trailing 0x02
        # terminator; allow 0 panels if the content already runs past the target
        # (then the dedication simply follows the content as early as possible).
        panels = max(0, min(panels, (filler_budget - 1) // 26))
        pause_units = min(PRE_MEMORIAL_PAUSE_UNITS, panels * 2 * MAX_FILLER_DELAY)

        self.current_credits.clear()
        self.current_titles.clear()
        for delay_1, delay_2 in _distribute_filler_frames(panels, pause_units):
            self.begin_credits()
            self.end_credits(delay_1, delay_2)

        # Dedication panel runs last (the final visible content)...
        self.acc += self.tail

        # ...then a single IDLE terminator. Credits opcode 0x02's handler is just
        # JMP $0C5F (at $C2:12AF): it re-runs every frame WITHOUT advancing the
        # command pointer, so the engine freezes on the blank post-dedication
        # screen until the music ends and the fireworks scene takes over - exactly
        # how vanilla ends its stream (its final byte is 0x02). This replaces both
        # the old zero pad (opcode 0x00 is a real command that marched off the
        # buffer into the string table = a crash) and the cycling hold panels
        # (which left the credits text-region window set, corrupting the
        # fireworks). Only the first 0x02 is ever reached; the rest fill to 3380.
        self.acc += (credit_len - len(self.acc)) * [0x02]

        free_list = {
            0x3f9c40: 952,
            string_table_start + string_table_size: 2080 - string_table_size
        }

        patch: dict[int, bytearray] = {}
        patch[credit_start] = bytearray(self.acc)
        for i in range(len(self.strings)):
            string = inv_str(self.strings[i])
            base = allocate_string(len(string), free_list)
            assert base is not None, "Ran out of space for credits strings!"
            patch[base] = bytearray(string)
            patch[string_table_start + i*2] = bytearray(ByteField(base & 0xFFFF, num_bytes=2).as_bytes())

        # Underscore
        patch[0x3FFDDA] = bytearray(b"\x3f\xc0\x7f\x80")
        return patch


# LINE 1, LINE 2, LINE 3. put EMPTY_STRING if you don't have anything.
DEV_MESSAGES = [
    ("DONT TRY IT...ALANIM.", "I ALREADY DID IT.", "   PAST ALANIM"),
    ("NOW TRY IT", "BLINDFOLDED", "     PATCDR"),
    ("IF YOU CAN READ THIS", "IT MEANS I FIXED IT", "...MAYBE. PIDGEZERO_ONE"),
    ("OHH I GOTTA THINK", "OF SOMETHING FUNNY", "       YAKI"),
    ("WHY ARE YOU", "USING ZSNES", "    DORKMASTER FLEK"),
]


def get_palette_authors(world: GameWorld) -> list[str]:
    """Collect unique palette authors from the world's selected palettes.

    Returns a list of unique author names (no duplicates), excluding palettes
    that have no author attribute (i.e., defaults).
    """
    authors = []
    palettes = [
        getattr(world, 'mario_palette', None),
        getattr(world, 'mallow_palette', None),
        getattr(world, 'geno_palette', None),
        getattr(world, 'bowser_palette', None),
        getattr(world, 'toadstool_palette', None),
    ]

    for palette in palettes:
        if palette is not None and hasattr(palette, 'author') and palette.author:
            if palette.author not in authors:
                authors.append(palette.author)

    return authors


def pad_author_line(author1: str, author2: str, total_length: int = 25) -> str:
    """Combine two author names into a single line with space padding.

    The line will be exactly total_length characters, with spaces between
    the two names (not at the beginning or end).
    """
    combined_len = len(author1) + len(author2)
    padding_needed = total_length - combined_len
    if padding_needed < 1:
        padding_needed = 1  # At least one space between names
    return author1 + " " * padding_needed + author2


def find_best_author_pairs(authors: list[str], max_line_length: int = 25) -> list[tuple[str, str]]:
    """Find the best pairing of authors so each combined line fits within max_line_length.

    Returns a list of (author1, author2) tuples. For odd numbers of authors,
    the longest name is placed alone at the end.
    """
    if len(authors) <= 1:
        return [(authors[0], "")] if authors else []

    # Sort by length for easier pairing (shortest with longest)
    sorted_authors = sorted(authors, key=len)

    # For odd number, put the longest on its own line (last)
    if len(sorted_authors) % 2 == 1:
        longest = sorted_authors.pop()  # Remove longest
    else:
        longest = None

    pairs = []
    # Pair shortest with longest remaining, working inward
    while len(sorted_authors) >= 2:
        short = sorted_authors.pop(0)
        long = sorted_authors.pop()

        # Check if they fit together (need at least 1 space between)
        if len(short) + len(long) + 1 <= max_line_length:
            pairs.append((short, long))
        else:
            # If they don't fit, try to find a better match
            # This is a simple greedy approach; could be improved
            pairs.append((short, long))

    # Add the longest name alone if odd number of authors
    if longest:
        pairs.append((longest, ""))

    return pairs


def add_palette_author_credits(credits: Credits, authors: list[str]) -> None:
    """Add palette author credits based on the number of authors.

    Layout varies by count:
    - 1 author: single centered line
    - 2 authors: two separate lines
    - 3 authors: three separate lines
    - 4 authors: two lines with paired names
    - 5 authors: three lines, first two paired, third alone (longest name)
    """
    if not authors:
        return

    credits.begin_credits()

    if len(authors) == 1:
        credits.add_credit(0x80, 0x40, 0x81, authors[0])

    elif len(authors) == 2:
        credits.add_credit(0x80, 0xC0, 0xC0, authors[0])
        credits.add_credit(0x80, 0x80, 0x81, authors[1])

    elif len(authors) == 3:
        credits.add_credit(0x80, 0x80, 0xC0, authors[0])
        credits.add_credit(0x80, 0x40, 0x81, authors[1])
        credits.add_credit(0x80, 0x00, 0xC2, authors[2])

    elif len(authors) == 4:
        pairs = find_best_author_pairs(authors)
        line1 = pad_author_line(pairs[0][0], pairs[0][1])
        line2 = pad_author_line(pairs[1][0], pairs[1][1])
        credits.add_credit(0x80, 0xC0, 0xC0, line1)
        credits.add_credit(0x80, 0x80, 0x81, line2)

    elif len(authors) >= 5:
        # Take first 5 authors only
        authors_to_use = authors[:5]
        pairs = find_best_author_pairs(authors_to_use)
        # pairs will be [(short1, long1), (short2, long2), (longest, "")]
        line1 = pad_author_line(pairs[0][0], pairs[0][1])
        line2 = pad_author_line(pairs[1][0], pairs[1][1])
        line3 = pairs[2][0]  # Longest name alone
        credits.add_credit(0x80, 0x80, 0xC0, line1)
        credits.add_credit(0x80, 0x40, 0x81, line2)
        credits.add_credit(0x80, 0x00, 0xC2, line3)

    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)


# Takes world because everything does.
# If we every implement stats, we'll need it, probably.
def update_credits(world: GameWorld) -> dict[int, bytearray]:
    credits = Credits()

    # Don't need this for the first title.
    # credits.begin_title(BEGIN_TITLES_DELAY)

    # This is what the remake does. We can do it too to make room for randomizer credits.
    credits.add_title(0x80, 0x00, 0x08, "SINCE MCMXCVI")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "BASED ON THE WORK OF")
    credits.add_credit(0x80, 0x40, 0x81, "THE ORIGINAL")
    credits.add_credit(0x80, 0x00, 0xC2, "DEVELOPMENT STAFF")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # Randomizer credits strt here.
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "ORIGINAL CONCEPT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0xC0, 0xC0, "ABYSSONYM")
    credits.add_credit(0x80, 0x80, 0x81, "LACKATTACK")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 25
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "CORE REWRITE")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x40, 0x81, "PIDGEZERO_ONE")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)


    # 25
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "CORE DEVELOPMENT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "ALANIM")
    credits.add_credit(0x80, 0x40, 0x81, "DORKMASTER FLEK")
    credits.add_credit(0x80, 0x00, 0xC2, "PATCDR")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "FEATURE DEVELOPMENT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "YAKIBOMB         FORALIAS")
    credits.add_credit(0x80, 0x40, 0x81, "SWINCH              IKUYO")
    credits.add_credit(0x80, 0x00, 0xC2, "ABYSSONYM")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "WEFFJEBSTER      CHAOSICX")
    credits.add_credit(0x80, 0x40, 0x81, "CODANTHEBARBARIAN")
    credits.add_credit(0x80, 0x00, 0xC2, "AMAZING AMPHAROS")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "POSTGAME DEMAKE DEVELOPMENT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x40, 0x81, "ANAXEMRANGER")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "DEMAKE DEV SUPPORT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0xC0, 0xC0, "PIDGEZERO_ONE")
    credits.add_credit(0x80, 0x80, 0x81, "CLEARTONIC")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "ARCHIPELAGO DEVELOPMENT LEAD")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x40, 0x81, "ROSALIE")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "ARCHIPELAGO DEV SUPPORT")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0xC0, 0xC0, "SOLIDUS SNAKE")
    credits.add_credit(0x80, 0x80, 0x81, "BIGMALLETMAN")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "BINGO DESIGN")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x40, 0x81, "CYNAS")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "TEST WRITING")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0xC0, 0xC0, "SERAPHIN EVELES")
    credits.add_credit(0x80, 0x80, 0x81, "WONDERJ")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "SPRITE DESIGN")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "XIRR")
    credits.add_credit(0x80, 0x40, 0x81, "SYSL")
    credits.add_credit(0x80, 0x00, 0xC2, "MR DEAN")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "SMBAI")
    credits.add_credit(0x80, 0x40, 0x81, "SEANCASS")
    credits.add_credit(0x80, 0x00, 0xC2, "ALANIM")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)
    
    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "MINAMIYO          EGGTALK")
    credits.add_credit(0x80, 0x40, 0x81, "NIMBUS      PIDGEZERO_ONE")
    credits.add_credit(0x80, 0x00, 0xC2, "AJ NITRO      MISTER MIKE")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # Show palette credits if any non-default palette is selected
    palette_flags = [
        MarioPaletteChoice, MallowPaletteChoice, GenoPaletteChoice,
        BowserPaletteChoice, ToadstoolPaletteChoice,
    ]
    if any(world.settings.get_flag(f).selected.name != "DEFAULT" for f in palette_flags):
        palette_authors = get_palette_authors(world)
        if palette_authors:
            credits.begin_titles(BEGIN_TITLES_DELAY)
            credits.add_title(0x80, 0x00, 0x08, "SELECTED ALLY PALETTES")
            credits.end_titles(END_TITLES_DELAY)

            add_palette_author_credits(credits, palette_authors)

    # 26
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "WRITING")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0xC0, 0xC0, "CYNAS       PIDGEZERO_ONE")
    credits.add_credit(0x80, 0x80, 0x81, "BROATMEAL            SYSL")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 27
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "QA AND RESEARCH")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "FLARE       INTHENAMEOFDT")
    credits.add_credit(0x80, 0x40, 0x81, "LOCKECOLELIVE  GOZENGATTA")
    credits.add_credit(0x80, 0x00, 0xC2, "CAVIN               SMBAI")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "TINYWETBLANKET      MADDI")
    credits.add_credit(0x80, 0x40, 0x81, "WEFFJEBSTER     BROATMEAL")
    credits.add_credit(0x80, 0x00, 0xC2, "SNESCHALMERS     SEANCASS")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "KATSTASAPH          OXWAS")
    credits.add_credit(0x80, 0x40, 0x81, "CYNAS            XELECIUM")
    credits.add_credit(0x80, 0x00, 0xC2, "AWILLSANDWICH")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "GUNTHERRIDEL     INVARIEL")
    credits.add_credit(0x80, 0x40, 0x81, "MINAMIYO       CALERELIYA")
    credits.add_credit(0x80, 0x00, 0xC2, "SPACE COW      SAXXON FOX")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "ATEATREE          LYLOVIR")
    credits.add_credit(0x80, 0x40, 0x81, "GOODMORNINGCRONO")
    credits.add_credit(0x80, 0x00, 0xC2, "ANTHONY MULBERRY")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 29
    if world.settings.isflag_enabled(RandomTadpolePondSong):

        credits.begin_titles(BEGIN_TITLES_DELAY)
        credits.add_title(0x80, 0x00, 0x08, "SELECTED MELODY BAY TUNES")
        credits.end_titles(END_TITLES_DELAY)

        credits.begin_credits()
        tadpole_submitters = world.song_authors
        if len(tadpole_submitters) == 1:
            credits.add_credit(0x80, 0x40, 0x81, tadpole_submitters[0])
        elif len(tadpole_submitters) == 2:
            credits.add_credit(0x80, 0xC0, 0xC0, tadpole_submitters[0])
            credits.add_credit(0x80, 0x80, 0x81, tadpole_submitters[1])
        else:
            credits.add_credit(0x80, 0x80, 0xC0, tadpole_submitters[0])
            credits.add_credit(0x80, 0x40, 0x81, tadpole_submitters[1])
            credits.add_credit(0x80, 0x00, 0xC2, tadpole_submitters[2])
        credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 30
    if world.settings.isflag_enabled(RandomSunkenShipPassword):

        credits.begin_titles(BEGIN_TITLES_DELAY)
        credits.add_title(0x80, 0x00, 0x08, "SELECTED SHIP PASSWORD")
        credits.end_titles(END_TITLES_DELAY)

        credits.begin_credits()
        credits.add_credit(0x80, 0x40, 0x81, world.password_author)
        credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 31
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "SPECIAL THANKS")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "DARKKEFKA       DOOMSDAY")
    credits.add_credit(0x80, 0x40, 0x81, "GIANGURGOLO        OMEGA")
    credits.add_credit(0x80, 0x00, 0xC2, "WILL               DJFOX")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 32
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "INSPIRATION")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "ALTTP AND OOT RANDOMIZER")
    credits.add_credit(0x80, 0x40, 0x81, "FFIV FREE ENTERPRISE")
    credits.add_credit(0x80, 0x00, 0xC2, "GOOD QUOTATIONS")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # new
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "IF YOU WANT YOUR NAME HERE...")
    credits.end_titles(END_TITLES_DELAY)

    dev_line1, dev_line2, dev_line3 = random.choice(DEV_MESSAGES)
    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "VISIT")
    credits.add_credit(0x80, 0x40, 0x81, "RANDOMIZER.SMRPGSPEEDRUNS.COM")
    credits.add_credit(0x80, 0x00, 0xC2, "TO CONTRIBUTE")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # 38
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "SPECIAL DEV MESSAGE")
    credits.end_titles(END_TITLES_DELAY)

    dev_line1, dev_line2, dev_line3 = random.choice(DEV_MESSAGES)
    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, dev_line1)
    credits.add_credit(0x80, 0x40, 0x81, dev_line2)
    credits.add_credit(0x80, 0x00, 0xC2, dev_line3)
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # Clear the titles
    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.end_titles(END_TITLES_DELAY)

    # 33
    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "THANK YOU SMRPG COMMUNITY.")
    credits.add_credit(0x80, 0x40, 0x81, "WITHOUT YOU...")
    credits.add_credit(0x80, 0x00, 0xC2, "NONE OF THIS WOULD BE POSSIBLE.")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # Redirect dedication into the tail buffer so the filler plays BEFORE it
    # and the dedication panel is the final real content the engine processes.
    # finalize() fills the leftover bytes with invisible blocks; PRE_MEMORIAL_
    # PAUSE_UNITS (top of file, default 0) controls how long they linger before
    # the dedication. The dedication therefore follows the last real panel,
    # shifted later only by that pause.
    credits.begin_tail()

    credits.begin_titles(BEGIN_TITLES_DELAY)
    credits.add_title(0x80, 0x00, 0x08, "DEDICATED TO THE MEMORY OF")
    credits.end_titles(END_TITLES_DELAY)

    credits.begin_credits()
    credits.add_credit(0x80, 0x80, 0xC0, "TINYWETBLANKET")
    credits.add_credit(0x80, 0x40, 0x81, "THANK YOU MIKAYLA")
    credits.add_credit(0x80, 0x00, 0xC2, "FOR EVERYTHING")
    credits.end_credits(END_CREDITS_DELAY_1, END_CREDITS_DELAY_2)

    # Fade the "DEDICATED TO" title so it exits alongside the dedication
    # text instead of lingering on screen during the final zero tail.
    credits.begin_titles(1)
    credits.end_titles(1)

    credits.end_tail()

    return credits.finalize()
