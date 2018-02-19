import random
import sys


def read_multi(f, length=2, reverse=True):
    vals = list(f.read(length))
    if reverse:
        vals = list(reversed(vals))
    value = 0
    for val in vals:
        if isinstance(val, bytes):
            val = ord(val)
        value = value << 8
        value = value | val
    return value


def format_multi(value, length=2, reverse=True):
    vals = []
    while value:
        vals.append(value & 0xFF)
        value = value >> 8
    if len(vals) > length:
        raise Exception("Value length mismatch.")

    while len(vals) < length:
        vals.append(0x00)

    if not reverse:
        vals = reversed(vals)

    return vals


def write_multi(f, value, length=2, reverse=True):
    vals = format_multi(value, length, reverse)

    # Python 2/3 compatibility
    if sys.version_info.major < 3:
        f.write(''.join(map(chr, vals)))
    else:
        f.write(bytes(vals))


utilrandom = random.Random()
utran = utilrandom
random = utilrandom


def mutate_bits(value, size=8, odds_multiplier=2.0):
    bits_set = bin(value).count('1')
    bits_unset = size - bits_set
    assert bits_unset >= 0
    lowvalue = min(bits_set, bits_unset)
    lowvalue = max(lowvalue, 1)
    multiplied = int(round(size * odds_multiplier))
    for i in range(size):
        if random.randint(1, multiplied) <= lowvalue:
            value ^= (1 << i)
    return value


def shuffle_bits(value, size=8, odds_multiplier=None):
    numbits = bin(value).count("1")
    if numbits:
        digits = random.sample(list(range(size)), numbits)
        newvalue = 0
        for d in digits:
            newvalue |= (1 << d)
        value = newvalue
    if odds_multiplier is not None:
        value = mutate_bits(value, size, odds_multiplier)
    return value


BOOST_AMOUNT = 2.0


def mutate_normal(value, minimum=0, maximum=0xFF,
                  reverse=False, smart=True, chain=True, return_float=False):
    value = max(minimum, min(value, maximum))
    rev = reverse
    if smart:
        if value > (minimum + maximum) / 2:
            rev = True
        else:
            rev = False

    if rev:
        value = maximum - value
    else:
        value = value - minimum

    BOOST_FLAG = False
    if value < BOOST_AMOUNT:
        value += BOOST_AMOUNT
        if value > 0:
            BOOST_FLAG = True
        else:
            value = 0

    if value > 0:
        half = value / 2.0
        a, b = random.random(), random.random()
        value = half + (half * a) + (half * b)

    if BOOST_FLAG:
        value -= BOOST_AMOUNT

    if rev:
        value = maximum - value
    else:
        value = value + minimum

    if chain and random.randint(1, 10) == 10:
        return mutate_normal(value, minimum=minimum, maximum=maximum,
                             reverse=reverse, smart=smart, chain=True)
    else:
        value = max(minimum, min(value, maximum))
        if not return_float:
            value = int(round(value))
        return value


class classproperty(property):
    def __get__(self, inst, *kargs):
        return self.fget(*kargs)
