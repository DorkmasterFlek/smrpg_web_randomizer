from __future__ import annotations

import gzip
import hashlib
import struct
from functools import lru_cache
from typing import TYPE_CHECKING

from randomizer.types.prize import CharacterPrize, Prize, SpellPrize
from randomizer.types.prizelocation import PrizeLocation

if TYPE_CHECKING:
    from randomizer.types.gameworld import GameWorld

FORMAT_VERSION = 2
_MAGIC = b"SMRP"
_HEADER = struct.Struct("<4sB32s32sQHI")
_VERSION_FIELD = 32
_NO_CHARACTER = 0xFF 


class ShufflerCacheError(Exception):
    pass


def _concrete_subclasses(root: type) -> set[type]:
    found: set[type] = set()
    for sub in root.__subclasses__():
        found.add(sub)
        found |= _concrete_subclasses(sub)
    return found


def prize_vocabulary() -> list[str]:
    return sorted(cls.__name__ for cls in _concrete_subclasses(Prize))


def _prize_classes() -> dict[str, type[Prize]]:
    return {cls.__name__: cls for cls in _concrete_subclasses(Prize)}


def _character_vocabulary() -> list[str]:
    return sorted(cls.__name__ for cls in _concrete_subclasses(CharacterPrize))


def location_vocabulary() -> list[str]:
    return sorted(cls.__name__ for cls in _concrete_subclasses(PrizeLocation))


def _location_classes() -> dict[str, type[PrizeLocation]]:
    return {cls.__name__: cls for cls in _concrete_subclasses(PrizeLocation)}


def _vocabulary_digest() -> int:
    """Fingerprint of both vocabularies this build would encode against."""
    joined = "\n".join(location_vocabulary()) + "\v" + "\n".join(prize_vocabulary())
    return int.from_bytes(hashlib.md5(joined.encode()).digest()[:4], "big")


@lru_cache(maxsize=1)
def _amount_carrying_prizes() -> frozenset[str]:
    """Prize classes whose constructor requires the placed amount.

    CoinPrize and FrogCoinPrize are handed a value at placement time rather than
    baking one into the class, so the class name alone is not enough to rebuild
    them. Detected by construction rather than hardcoded, so a new prize of the
    same shape is covered automatically; the vocabulary digest rejects blobs
    written before such a class existed.
    """
    needs: set[str] = set()
    for cls in _concrete_subclasses(Prize):
        try:
            cls()
        except TypeError:
            needs.add(cls.__name__)
        except Exception:
            # Abstract intermediates that read class-level state they do not
            # define; they are never placed, so they need no amount.
            continue
    return frozenset(needs)


def _version_tag(world: GameWorld) -> bytes:
    """The randomizer build a blob was written by, fixed-width for the header"""
    return str(world.version).encode("utf-8")[:_VERSION_FIELD].ljust(_VERSION_FIELD, b"\x00")


def _flags_digest(world: GameWorld) -> bytes:
    return hashlib.md5(world.settings.flag_string.encode()).digest().ljust(32, b"\x00")


def serialize(world: GameWorld) -> bytes:
    vocab = {name: i + 1 for i, name in enumerate(prize_vocabulary())}
    chars = {name: i for i, name in enumerate(_character_vocabulary())}
    loc_vocab = location_vocabulary()

    by_name = {cls.__name__: loc for cls, loc in world.locations.items()}
    unknown = set(by_name) - set(loc_vocab)
    if unknown:
        raise ShufflerCacheError(f"locations outside the vocabulary: {sorted(unknown)}")

    needs_amount = _amount_carrying_prizes()
    mask = bytearray((len(loc_vocab) + 7) // 8)
    body = bytearray()
    tail = bytearray()
    amounts = bytearray()
    for i, name in enumerate(loc_vocab):
        location = by_name.get(name)
        if location is None:
            continue
        mask[i // 8] |= 1 << (i % 8)
        prize = location.prize
        if prize is None:
            body += struct.pack("<H", 0)
            continue
        prize_name = type(prize).__name__
        if prize_name not in vocab:
            raise ShufflerCacheError(f"prize {prize_name} is not in the vocabulary")
        body += struct.pack("<H", vocab[prize_name])
        if isinstance(prize, SpellPrize):
            character = prize.character
            tail.append(_NO_CHARACTER if character is None else chars[character.__name__])
        if prize_name in needs_amount:
            amounts += struct.pack("<H", int(prize.amount))

    seed = int(world.seed) if isinstance(world.seed, int) else 0
    header = _HEADER.pack(
        _MAGIC,
        FORMAT_VERSION,
        _version_tag(world),
        _flags_digest(world),
        seed,
        len(by_name),
        _vocabulary_digest(),
    )
    # mtime=0: gzip stamps the current time into its header by default, which
    # would make two encodings of the same placement differ.
    return gzip.compress(
        header + bytes(mask) + bytes(body) + bytes(tail) + bytes(amounts), 9, mtime=0
    )


def apply(world: GameWorld, blob: bytes) -> None:
    raw = gzip.decompress(blob)
    magic, version, build, flags_digest, seed, count, vocab = _HEADER.unpack_from(raw)
    if magic != _MAGIC:
        raise ShufflerCacheError("not a placement cache blob")
    if version != FORMAT_VERSION:
        raise ShufflerCacheError(
            f"cache format {version}, this build writes {FORMAT_VERSION}"
        )
    if build != _version_tag(world):
        raise ShufflerCacheError(
            f"cached placement was made by randomizer version "
            f"{build.rstrip(bytes(1)).decode('utf-8', 'replace')!r}, this build is "
            f"{str(world.version)!r}; regenerate"
        )
    if vocab != _vocabulary_digest():
        raise ShufflerCacheError(
            "cached placement was written against a different set of location or "
            "prize classes; regenerate"
        )
    if flags_digest != _flags_digest(world):
        raise ShufflerCacheError("cached placement was made for different flags")
    if isinstance(world.seed, int) and seed != int(world.seed):
        raise ShufflerCacheError(f"cached placement is for seed {seed}")

    vocab = prize_vocabulary()
    classes = _prize_classes()
    char_names = _character_vocabulary()
    loc_vocab = location_vocabulary()
    loc_classes = _location_classes()

    mask_at = _HEADER.size
    mask_len = (len(loc_vocab) + 7) // 8
    mask = raw[mask_at : mask_at + mask_len]
    present = [
        name
        for i, name in enumerate(loc_vocab)
        if mask[i // 8] >> (i % 8) & 1
    ]
    if len(present) != count:
        raise ShufflerCacheError(
            f"cache header says {count} locations, mask marks {len(present)}"
        )

    present_set = set(present)
    rebuilt: dict[type, object] = {
        cls: loc
        for cls, loc in world.locations.items()
        if cls.__name__ in present_set
    }
    for name in present:
        cls = loc_classes.get(name)
        if cls is None:
            raise ShufflerCacheError(f"cache references unknown location {name}")
        if cls not in rebuilt:
            try:
                rebuilt[cls] = cls()
            except TypeError as exc:
                # The world should already hold every location the blob names;
                # needing to build one means set_locations produced a different
                # set than the run that wrote the blob.
                raise ShufflerCacheError(
                    f"cached placement names {name}, which this world does not "
                    f"have and which cannot be rebuilt from its class alone"
                ) from exc
    world.locations = rebuilt  # type: ignore[assignment]

    needs_amount = _amount_carrying_prizes()
    body_at = mask_at + mask_len
    tail_at = body_at + count * 2
    # The amounts section follows the spell tail, whose length is only known
    # after walking the body, so count the spell prizes up front.
    spell_count = 0
    for i in range(count):
        (index,) = struct.unpack_from("<H", raw, body_at + i * 2)
        if index and issubclass(classes[vocab[index - 1]], SpellPrize):
            spell_count += 1
    amount_at = tail_at + spell_count
    for i, name in enumerate(present):
        (index,) = struct.unpack_from("<H", raw, body_at + i * 2)
        location = world.locations[loc_classes[name]]
        if index == 0:
            location.set_prize(None)
            world.notify_prize_placed(location, None)
            continue
        prize_cls = classes[vocab[index - 1]]
        if prize_cls.__name__ in needs_amount:
            (amount,) = struct.unpack_from("<H", raw, amount_at)
            amount_at += 2
            prize = prize_cls(amount)
        else:
            prize = prize_cls()
        if isinstance(prize, SpellPrize):
            owner = raw[tail_at]
            tail_at += 1
            if owner != _NO_CHARACTER:
                prize.set_character(classes[char_names[owner]])
        location.set_prize(prize)
        world.notify_prize_placed(location, prize)


__all__ = ["FORMAT_VERSION", "ShufflerCacheError", "apply", "prize_vocabulary", "serialize"]
