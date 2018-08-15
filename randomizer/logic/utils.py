import math
import random


class BitMapSet(set):
    """A class representing a bitmap of a certain length using the set built-in type to track which bits are set."""

    def __init__(self, num_bytes=1, *args, **kwargs):
        """
        :type num_bytes: int
        """
        super().__init__(*args, **kwargs)
        self._num_bytes = num_bytes

    def as_bytes(self):
        """Return bitmap in little endian byte format for ROM patching.

        :rtype: bytearray
        """
        result = 0
        for value in self:
            result |= (1 << value)
        return result.to_bytes(self._num_bytes, 'little')

    def __str__(self):
        return "BitMapSet({})".format(super().__str__())


class ByteField:
    """Base class for an integer value field spanning one or more bytes."""

    def __init__(self, value, num_bytes=1):
        """
        :type value: int
        :type num_bytes: int
        """
        self._value = value
        self._num_bytes = num_bytes

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = int(value)

    def as_bytes(self):
        """Return current value of this stat as a little-endian byte array for the patch.  If the value is less than
        zero, convert this to a signed int in byte format.

        :rtype: bytearray
        """
        if self._value < 0:
            val = self._value + (2 ** (self._num_bytes * 8))
        else:
            val = self._value
        return val.to_bytes(self._num_bytes, 'little')

    def __str__(self):
        return "ByteField(current value: {}, number of bytes: {}".format(self.value, self._num_bytes)


class Stat(ByteField):
    """Base class for a character/enemy stat value."""

    def __init__(self, base, minimum=0x00, maximum=0xff):
        """
        :type base: int
        :type minimum: int
        :type maximum: int
        """
        # Number of bytes this value occupies based on max value.
        if maximum > 0:
            num_bytes = int(math.ceil(math.log2(maximum) / 8))
        else:
            num_bytes = 1

        super().__init__(base, num_bytes)
        self._base = base
        self._min = minimum
        self._max = maximum

    @property
    def base(self):
        """:rtype: int"""
        return self._base

    @property
    def value(self):
        """:rtype: int"""
        return self._value

    @value.setter
    def value(self, value):
        """
        :type value: int
        """
        value = int(value)
        if value < self.min:
            raise ValueError("Provided value {} less than min value {}".format(value, self.min))
        elif value > self.max:
            raise ValueError("Provided value {} greater than max value {}".format(value, self.max))
        self._value = value

    @property
    def min(self):
        """:rtype: int"""
        return self._min

    @property
    def max(self):
        """:rtype: int"""
        return self._max

    def shuffle(self):
        """Randomize stat value based on base value, and restricting to min/max values."""
        self.value = mutate_normal(self.base, self.min, self.max)

    def __str__(self):
        return "Stat(current value: {}, min: {}, max: {}".format(self.value, self.min, self.max)


class Mutator:
    """Mutator class that shuffles stat attributes based on min/max values and a difficulty setting."""
    def __init__(self, difficulty=None):
        # Placeholder for future difficulty option.
        self.difficulty = difficulty

    def mutate_normal(self, value, minimum=0, maximum=0xff):
        """Mutate a value with a given range.
        This is roughly simulating a normal distribution with mean <value>, std deviation approx 1/5 <value>.
        """
        BOOST_AMOUNT = 2.0

        value = max(minimum, min(value, maximum))
        if value > (minimum + maximum) / 2:
            reverse = True
        else:
            reverse = False

        if reverse:
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

        if reverse:
            value = maximum - value
        else:
            value = value + minimum

        # 1/10 chance to chain mutate for more variance.
        if random.randint(1, 10) == 10:
            return self.mutate_normal(value, minimum=minimum, maximum=maximum)
        else:
            value = max(minimum, min(value, maximum))
            value = int(round(value))
            return value


class _GlobalMutator:
    """Container class for the global mutator instance so we can control the difficulty."""
    mutator = Mutator()

    @classmethod
    def get_mutator(cls):
        return cls.mutator

    @classmethod
    def set_difficulty(cls, difficulty):
        cls.mutator.difficulty = difficulty


def mutate_normal(value, minimum=0, maximum=0xff):
    """Mutate a stat value using the global mutator."""
    return _GlobalMutator.get_mutator().mutate_normal(value, minimum, maximum)


def set_difficulty(difficulty):
    """Set the difficulty level for the global mutator that shuffles stats."""
    _GlobalMutator.set_difficulty(difficulty)
