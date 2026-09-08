"""TitleScreen: reproduce the randomizer's custom intro / title screen.

The randomizer ships a custom title screen (the "Super Mario RPG" main title
and the opening title-card graphics). These are large,
*static* (seed-independent) GFX blobs that the legacy open_mode.json base
patch injected, and that smrpgpatchbuilder's render() methods do **not**
regenerate (the title screen is not a randomizer data collection). Dropping
them was proven non-neutral - diff_open_mode --drop-range 0x3F21D4 31209
yields hundreds of differing runs.

Because the data is ~33 KB of static bytes, it is stored as a checked-in binary
asset (title_screen.bin) rather than inline bytes(...) literals, and
this loader streams it back into the patch. The asset is a flat sequence of
records::

    [u32 file_offset LE][u32 length LE][length bytes] ...

Entries (render-disjoint AND render-range-clean, verified via
diff_open_mode + smrpg-patch-audit; HiROM file offsets):

* 0x3F1948 / 0x3F197C / 0x3F1983 (~2 KB) - title-card / opening
  GFX (LazyShell "Intro" editor writes the title card at 0x3F1913).
* 0x3F21D4 (31,209 B) - main title GFX (LazyShell writes main title at
  0x3F216E; the open-mode diff starts at 0x3F21D4). The LC_LZ3 stream itself
  starts at 0x3F216F and now ends at 0x3F96F1; the record's trailing bytes are
  past the terminator and unread.

To regenerate title_screen.bin from a fresh open-mode ROM, re-extract those
open_mode.json entries (see the generator in the deconstruction notes).

NOTE: open mode leaves the title *mode selector* (0x09E640), title
*coordinates* (0x09E66B-0x09EF51) and the opening *palette* (0x3F0080)
at vanilla, so they are intentionally not carried here. Other render-disjoint
$FE-$FF data is also NOT carried here and needs separate classification:
the bootup-logo / map region 0x3EFD02 (overlaps
WorldMapLocationCollection.render's curated range - may be render-managed
under some flags), the custom location names 0x3EFD8F+ ("Inner Factory",
"To Pipe Vault", ...), and the $FE:2Dxx data block.
"""

import os
import struct

_ASSET = os.path.join(os.path.dirname(__file__), "title_screen.bin")


def get_patch() -> dict[int, bytes]:
    """Stream the custom title-screen records from title_screen.bin."""
    out: dict[int, bytes] = {}
    with open(_ASSET, "rb") as handle:
        blob = handle.read()
    pos = 0
    while pos < len(blob):
        offset, length = struct.unpack_from("<II", blob, pos)
        pos += 8
        out[offset] = blob[pos : pos + length]
        pos += length
    return out
