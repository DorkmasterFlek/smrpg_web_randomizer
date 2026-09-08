"""Storage format for a cached `SpriteCollection.render()` result.

Packing the sprite sheets is ~80% of patch assembly (4.6s of a 5.7s `get_patch`),
and its result depends on the seed, the non-cosmetic flags and - among cosmetics -
only on PlayAsStarter, which decides whether the overworld protagonist is Mario or
the starter ally. The first two are fixed for a `Seed` row, so two blobs per seed
cover every re-roll of that permalink, whatever cosmetics are picked.

The render is an *ordered* list of writes, not a mapping: it leads with zero-fill
ranges covering each sprite/animation/tile bank and then overwrites them with the
real data, so the same address appears more than once and the later write must win.
The format below preserves that order and those duplicates exactly.

A blob is only replayable if the packer would have been handed the same free space,
so the reclaim banks are fingerprinted into the header and checked on load. That
covers a change to the pinned dialog floors (see `sprite_reclaim`), to the amount
of space the other reclaim sources give back, or to the packer itself by way of the
build version. A blob that fails any check is not fatal - the caller re-renders,
which is what would have happened with no cache at all.
"""

from __future__ import annotations

import gzip
import hashlib
import struct

FORMAT_VERSION = 1
_MAGIC = b"SMSP"
_VERSION_FIELD = 32
# magic, format version, build version, reclaim fingerprint, write count
_HEADER = struct.Struct(f"<4sB{_VERSION_FIELD}s20sI")
_ENTRY = struct.Struct("<II")

SpriteWrites = list[tuple[int, bytes]]
ReclaimBanks = list[tuple[int, int]]


class SpriteCacheError(Exception):
    """A stored sprite render cannot be replayed against the current build."""


def reclaim_fingerprint(banks: ReclaimBanks) -> bytes:
    """Digest of the free space the packer was given, in the order it saw it."""
    h = hashlib.sha1()
    for start, end in banks:
        h.update(struct.pack("<II", start, end))
    return h.digest()


def _version_tag(version: str) -> bytes:
    return str(version).encode("utf-8")[:_VERSION_FIELD].ljust(_VERSION_FIELD, b"\x00")


def serialize(writes: SpriteWrites, banks: ReclaimBanks, version: str) -> bytes:
    """Encode one render plus the context needed to decide if it still applies."""
    body = bytearray()
    for addr, data in writes:
        blob = bytes(data)
        body += _ENTRY.pack(addr, len(blob))
        body += blob
    header = _HEADER.pack(
        _MAGIC,
        FORMAT_VERSION,
        _version_tag(version),
        reclaim_fingerprint(banks),
        len(writes),
    )
    # mtime=0: gzip stamps the current time into its header by default, which would
    # make two encodings of the same render differ.
    return gzip.compress(bytes(header) + bytes(body), mtime=0)


def deserialize(blob: bytes, banks: ReclaimBanks, version: str) -> SpriteWrites:
    """Decode a render, rejecting one packed against different free space.

    Returns the writes in their original order, duplicate addresses included.

    Raises:
        SpriteCacheError: the blob is malformed, was written by another build, or
            was packed against reclaim banks that no longer match.
    """
    try:
        raw = gzip.decompress(blob)
    except (OSError, EOFError) as exc:
        raise SpriteCacheError(f"blob is not readable gzip: {exc}") from exc

    if len(raw) < _HEADER.size:
        raise SpriteCacheError("blob is shorter than its header")
    magic, fmt, stored_version, fingerprint, count = _HEADER.unpack_from(raw)
    if magic != _MAGIC:
        raise SpriteCacheError("blob is not a sprite render")
    if fmt != FORMAT_VERSION:
        raise SpriteCacheError(f"blob format {fmt}, this build writes {FORMAT_VERSION}")
    if stored_version != _version_tag(version):
        written_by = stored_version.rstrip(b"\x00").decode("utf-8", "replace")
        raise SpriteCacheError(f"blob written by build {written_by!r}, running {version!r}")
    if fingerprint != reclaim_fingerprint(banks):
        raise SpriteCacheError("blob was packed against different reclaim banks")

    writes: SpriteWrites = []
    offset = _HEADER.size
    for _ in range(count):
        if offset + _ENTRY.size > len(raw):
            raise SpriteCacheError("blob ended mid-entry")
        addr, length = _ENTRY.unpack_from(raw, offset)
        offset += _ENTRY.size
        if offset + length > len(raw):
            raise SpriteCacheError(f"entry at 0x{addr:06X} runs past the end of the blob")
        writes.append((addr, raw[offset : offset + length]))
        offset += length
    if offset != len(raw):
        raise SpriteCacheError(f"{len(raw) - offset} trailing bytes after {count} entries")
    return writes
