import io
import sys
from os import path

from django.conf import settings

from .utils import read_multi, classproperty, mutate_normal, random, format_multi

tblpath = path.join(settings.BASE_DIR, "randomizer/logic_old/tables")
datapath = path.join(tblpath, "data")

# For importing rom data
sys.path.insert(0, datapath)


MASTER_FILENAME = "master.txt"
TABLE_SPECS = {}
GLOBAL_OUTPUT = None
GLOBAL_TABLE = None
GLOBAL_LABEL = None
GRAND_OBJECT_DICT = {}
NUM_GROUPS_DICT = {}


def set_global_table_filename(filename):
    global GLOBAL_TABLE
    GLOBAL_TABLE = filename

def reset_everything():
    global TABLE_SPECS, GLOBAL_TABLE, GRAND_OBJECT_DICT, NUM_GROUPS_DICT, already_gotten
    TABLE_SPECS = {}
    GLOBAL_TABLE = {}
    GRAND_OBJECT_DICT = {}
    NUM_GROUPS_DICT = {}
    already_gotten = {}


def sort_good_order(objects):
    objects = sorted(objects, key=lambda o: o.__name__)
    objects = [o for o in objects if o.__name__ in TABLE_SPECS]
    while True:
        changed = False
        for o in list(objects):
            if hasattr(o, "after_order"):
                index = objects.index(o)
                for o2 in o.after_order:
                    index2 = objects.index(o2)
                    if index2 > index:
                        objects.remove(o)
                        objects.insert(index2, o)
                        changed = True
        if not changed:
            break
    return objects


class TableSpecs:
    def __init__(self, specfile, pointer=None, count=None,
                 grouped=False, pointed=False):
        self.attributes = []
        self.bitnames = {}
        self.total_size = 0
        self.pointer = pointer
        self.count = count
        self.grouped = grouped
        self.pointed = pointed
        for line in open(specfile):
            line = line.strip()
            if not line or line[0] == "#":
                continue
            line = line.strip().split(',')
            if len(line) == 2:
                name, size, other = line[0], line[1], None
            elif len(line) == 3:
                name, size, other = tuple(line)

            if size[:3] == "bit":
                size, bitnames = tuple(size.split(':'))
                size = 1
                bitnames = bitnames.split(" ")
                self.bitnames[name] = bitnames
            elif size == '?':
                size = 0

            try:
                size = int(size)
                self.total_size += size
            except ValueError:
                a, b = size.split('x')
                self.total_size += (int(a)*int(b))
            self.attributes.append((name, size, other))


class TableObject(object):
    region = 'US'
    base_data = b''

    class __metaclass__(type):
        def __iter__(self):
            for obj in self.ranked:
                yield obj

    def __init__(self, pointer=None, groupindex=0, size=None):
        assert hasattr(self, "specs")
        assert isinstance(self.total_size, int)
        self.pointer = pointer
        self.groupindex = groupindex
        self.variable_size = size
        self.index = 0

        # Try to import data module.
        if self.specspointed:
            mname = self.region + '_pointer_data'
        else:
            mname = self.region + '_' + self.__class__.__name__ + '_data'

        m = __import__(mname)
        self.base_data = m.DATA
        self.read_data()

    @classproperty
    def specs(cls):
        return TABLE_SPECS[cls.__name__]

    @classproperty
    def specsattrs(cls):
        return cls.specs.attributes

    @classproperty
    def specspointer(cls):
        return cls.specs.pointer

    @classproperty
    def specscount(cls):
        return cls.specs.count

    @classproperty
    def specsgrouped(cls):
        return cls.specs.grouped

    @classproperty
    def specspointed(cls):
        return cls.specs.pointed

    @classproperty
    def specspointedpointer(cls):
        return cls.specs.pointedpointer

    @classproperty
    def specspointedpoint1(cls):
        return cls.specs.pointedpoint1

    @classproperty
    def specspointedsize(cls):
        return cls.specs.pointedsize

    @classproperty
    def bitnames(cls):
        return cls.specs.bitnames

    @classproperty
    def total_size(cls):
        return cls.specs.total_size

    @classproperty
    def every(cls):
        return get_table_objects(cls)

    @property
    def rank(self):
        return self.index

    @property
    def intershuffle_valid(self):
        return True

    @property
    def catalogue_index(self):
        return self.index

    @classproperty
    def ranked(cls):
        return sorted(cls.every, key=lambda c: (c.rank, c.index))

    def get_similar(self, candidates=None):
        if self.rank < 0:
            return self
        if candidates is None:
            candidates = [c for c in self.ranked if c.rank >= 0]
        candidates = sorted(candidates, key=lambda c: c.rank)
        index = candidates.index(self)
        index = mutate_normal(index, maximum=len(candidates)-1)
        return candidates[index]

    @classmethod
    def get(cls, index):
        if isinstance(index, int):
            return GRAND_OBJECT_DICT[cls, index]
        elif isinstance(index, str) or isinstance(index, str):
            objs = [o for o in cls.every if index in o.name]
            if len(objs) == 1:
                return objs[0]
            elif len(objs) >= 2:
                raise Exception("Too many matching objects.")
            else:
                raise Exception("No matching objects.")
        else:
            raise Exception("Bad index.")

    @classproperty
    def groups(cls):
        returndict = {}
        for obj in cls.every:
            if obj.groupindex not in returndict:
                returndict[obj.groupindex] = []
            returndict[obj.groupindex].append(obj)
        return returndict

    @classmethod
    def getgroup(cls, index):
        return [o for o in cls.every if o.groupindex == index]

    @property
    def group(self):
        return self.getgroup(self.groupindex)

    @classmethod
    def has(cls, index):
        try:
            cls.get(index)
            return True
        except KeyError:
            return False

    def get_bit(self, bitname):
        for key, value in sorted(self.bitnames.items()):
            if bitname in value:
                index = value.index(bitname)
                byte = getattr(self, key)
                bitvalue = byte & (1 << index)
                return bool(bitvalue)
        raise Exception("No bit registered under that name.")

    def set_bit(self, bitname, bitvalue):
        bitvalue = 1 if bitvalue else 0
        for key, value in list(self.bitnames.items()):
            if bitname in value:
                index = value.index(bitname)
                byte = getattr(self, key)
                if bitvalue:
                    byte = byte | (1 << index)
                else:
                    byte = byte & (0xFF ^ (1 << index))
                setattr(self, key, byte)
                return
        raise Exception("No bit registered under that name.")

    @property
    def display_name(self):
        if not hasattr(self, "name"):
            self.name = "%x" % self.index
        if isinstance(self.name, int):
            return "%x" % self.name
        # return "".join([c for c in self.name if c in string.printable])
        return self.name

    @property
    def description(self):
        classname = self.__class__.__name__
        pointer = "%x" % self.pointer if self.pointer else "None"
        desc = "{0} {1:02x} {2} {3}".format(
            classname, self.index, pointer, self.display_name)
        l = [var for var in list(vars(self).keys()) if var not in ('filename', 'base_data')]
        l.sort()
        for var in l:
            desc += "\n    {}: {!r}".format(var, getattr(self, var))
        return desc

    @property
    def long_description(self):
        s = []
        for attr in sorted(dir(self)):
            if attr.startswith('_'):
                continue

            if attr in ["specs", "catalogue"]:
                continue

            if hasattr(self.__class__, attr):
                class_attr = getattr(self.__class__, attr)
                if (isinstance(class_attr, property)
                        or hasattr(class_attr, "__call__")):
                    continue

            try:
                value = getattr(self, attr)
            except AttributeError:
                continue

            if isinstance(value, dict):
                continue

            if isinstance(value, list):
                if value and not isinstance(value[0], int):
                    continue
                value = " ".join(["%x" % v for v in value])

            if isinstance(value, int):
                value = "%x" % value

            s.append((attr, "%s" % value))

        s = ", ".join(["%s: %s" % (a, b) for (a, b) in s])
        s = "%x - %s" % (self.index, s)
        return s

    @classproperty
    def catalogue(self):
        logs = []
        for obj in sorted(self.every, key=lambda o: o.catalogue_index):
            logs.append(obj.log.strip())

        if any(["\n" in log for log in logs]):
            return "\n\n".join(logs)
        else:
            return "\n".join(logs)

    @property
    def log(self):
        return str(self)

    def __repr__(self):
        return self.description

    def get_variable_specsattrs(self):
        specsattrs = [(name, self.variable_size, other)
                      for (name, size, other)
                      in self.specsattrs if size == 0]
        if not specsattrs:
            raise ValueError("No valid specs attributes.")
        elif len(specsattrs) >= 2:
            raise ValueError("Too many specs attributes.")
        return specsattrs

    def read_data(self, pointer=None):
        if pointer is None:
            pointer = self.pointer
        if pointer is None or not self.base_data:
            return

        # Subtract current pointer value from the base.
        if self.specspointed:
            pointer = pointer - self.specspointedpointer
        else:
            pointer = pointer - self.specspointer
        assert(pointer >= 0)

        if self.variable_size is not None:
            specsattrs = self.get_variable_specsattrs()
        else:
            specsattrs = self.specsattrs

        f = io.BytesIO(self.base_data)
        f.seek(pointer)

        for name, size, other in specsattrs:
            if other in [None, "int"]:
                value = read_multi(f, length=size)
            elif other == "str":
                value = f.read(size)
            elif other == "list":
                if not isinstance(size, int):
                    number, numbytes = size.split('x')
                    number, numbytes = int(number), int(numbytes)
                else:
                    number, numbytes = size, 1
                value = []
                for i in range(number):
                    value.append(read_multi(f, numbytes))
            setattr(self, name, value)

        f.close()

    def copy_data(self, another):
        for name, _, _ in self.specsattrs:
            value = getattr(another, name)
            setattr(self, name, value)

    def write_data(self, pointer=None):
        if pointer is None:
            pointer = self.pointer
        if pointer is None:
            return

        if self.variable_size is not None:
            # doesn't seem to work properly
            raise NotImplementedError
            specsattrs = self.get_variable_specsattrs()
        else:
            specsattrs = self.specsattrs

        data = {}
        for name, size, other in specsattrs:
            value = getattr(self, name)
            if other in [None, "int"]:
                data[pointer] = format_multi(value, length=size)
                pointer += size
            elif other == "str":
                assert len(value) == size
                data[pointer] = list(bytes(value))
                pointer += size
            elif other == "list":
                if not isinstance(size, int):
                    number, numbytes = size.split('x')
                    number, numbytes = int(number), int(numbytes)
                else:
                    number, numbytes = size, 1
                assert len(value) == number
                for v in value:
                    data[pointer] = format_multi(v, length=numbytes)
                    pointer += numbytes

        return [data], pointer

    @classmethod
    def write_all(cls):
        data = []

        if not cls.specsgrouped and not cls.specspointed:
            for o in cls.every:
                d, pointer = o.write_data()
                data += d
        elif cls.specsgrouped:
            pointer = cls.specspointer
            numgroups = NUM_GROUPS_DICT[cls]
            for i in range(numgroups):
                objs = [o for o in cls.every if o.groupindex == i]
                if cls.specs.groupednum is None:
                    data.append({pointer: [len(objs)]})
                    pointer += 1
                for o in objs:
                    d, pointer = o.write_data(pointer)
                    data += d
        elif cls.specspointed:
            pointer = cls.specspointer
            size = cls.specspointedsize
            numgroups = NUM_GROUPS_DICT[cls]
            pointedpointer = pointer + (numgroups * size)
            mask = (2 ** (8*size)) - 1
            for i in range(numgroups):
                masked = pointedpointer & mask
                objs = [o for o in cls.every if o.groupindex == i]
                for o in objs:
                    d, pointedpointer = o.write_data(pointedpointer)
                    data += d
                data.append({
                    pointer + (i * size): format_multi(masked, length=size),
                })

        return data

    def cleanup(self):
        return

    @classmethod
    def full_cleanup(cls):
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "cleaned") and cls2.cleaned):
                    raise Exception("Clean order violated: %s %s"
                                    % (cls, cls2))
        for o in cls.every:
            o.cleanup()
        cls.cleaned = True

    @classmethod
    def full_randomize(cls):
        if hasattr(cls, "after_order"):
            for cls2 in cls.after_order:
                if not (hasattr(cls2, "randomized") and cls2.randomized):
                    raise Exception("Randomize order violated: %s %s"
                                    % (cls, cls2))
        cls.groupshuffle()
        cls.intershuffle()
        cls.shuffle_all()
        cls.randomize_all()
        cls.mutate_all()
        cls.randomized = True

    @classmethod
    def mutate_all(cls):
        for o in cls.every:
            if hasattr(o, "mutated") and o.mutated:
                continue
            o.mutate()
            o.mutate_bits()
            o.mutated = True

    @classmethod
    def randomize_all(cls):
        for o in cls.every:
            if hasattr(o, "randomized") and o.randomized:
                continue
            o.randomize()
            o.randomized = True

    @classmethod
    def shuffle_all(cls):
        for o in cls.every:
            if hasattr(o, "shuffled") and o.shuffled:
                continue
            o.shuffle()
            o.shuffled = True

    def mutate(self):
        if not hasattr(self, "mutate_attributes"):
            return

        for attribute in sorted(self.mutate_attributes):
            if isinstance(self.mutate_attributes[attribute], type):
                tob = self.mutate_attributes[attribute]
                index = getattr(self, attribute)
                tob = tob.get(index)
                tob = tob.get_similar()
                setattr(self, attribute, tob.index)
            else:
                minmax = self.mutate_attributes[attribute]
                if type(minmax) is tuple:
                    minimum, maximum = minmax
                else:
                    minimum, maximum = 0, 0xff
                value = getattr(self, attribute)
                if value < minimum or value > maximum:
                    continue
                value = mutate_normal(value, minimum=minimum, maximum=maximum)
                setattr(self, attribute, value)

    def mutate_bits(self):
        if not hasattr(self, "mutate_bit_attributes"):
            return

        for attribute in sorted(self.mutate_bit_attributes):
            try:
                chance = self.mutate_bit_attributes[attribute]
                if random.random() <= chance:
                    value = self.get_bit(attribute)
                    self.set_bit(attribute, not value)
            except:
                no_mutate, size, odds = self.mutate_bit_attributes[attribute]
                value = getattr(self, attribute)
                newvalue = self.mutate_bits(value, size, odds)
                newvalue = newvalue ^ ((value ^ newvalue) & no_mutate)
                setattr(self, attribute, newvalue)

    def randomize(self):
        if not hasattr(self, "randomize_attributes"):
            return

        for attribute in sorted(self.randomize_attributes):
            if isinstance(self.randomize_attributes[attribute], type):
                tob = self.randomize_attributes[attribute]
                candidates = [t for t in tob.every if t.rank >= 0]
                setattr(self, attribute, random.choice(candidates).index)
            else:
                minimum, maximum = self.randomize_attributes[attribute]
                setattr(self, attribute, random.randint(minimum, maximum))

    def shuffle(self):
        if not hasattr(self, "shuffle_attributes"):
            return

        for attributes in sorted(self.shuffle_attributes):
            if len(attributes) == 1:
                attribute = attributes[0]
                value = sorted(getattr(self, attribute))
                random.shuffle(value)
                setattr(self, attribute, value)
                continue
            values = [getattr(self, attribute) for attribute in attributes]
            random.shuffle(values)
            for attribute, value in zip(attributes, values):
                setattr(self, attribute, value)

    @classmethod
    def intershuffle(cls):
        if not hasattr(cls, "intershuffle_attributes"):
            return

        hard_shuffle = False
        if (len(set([o.rank for o in cls.every])) == 1
                or all([o.rank == o.index for o in cls.every])):
            hard_shuffle = True

        for attributes in cls.intershuffle_attributes:
            candidates = [o for o in cls.every
                          if o.rank >= 0 and o.intershuffle_valid]
            if hard_shuffle:
                shuffled = list(candidates)
                random.shuffle(shuffled)
            else:
                candidates = sorted(candidates, key=lambda c: c.rank)
                shuffled = list(candidates)
                max_index = len(candidates)-1
                done = set([])
                for i, o in enumerate(candidates):
                    new_index = i
                    if shuffled[i] in done:
                        continue
                    while random.choice([True, False]):
                        new_index += min(1, (max_index / 10.0))
                    new_index = int(round(new_index))
                    new_index = min(new_index, max_index)
                    a, b = shuffled[i], shuffled[new_index]
                    done.add(a)
                    shuffled[i] = b
                    shuffled[new_index] = a

            if isinstance(attributes, str) or isinstance(attributes, str):
                attributes = [attributes]

            for attribute in attributes:
                swaps = []
                for a, b in zip(candidates, shuffled):
                    aval, bval = getattr(a, attribute), getattr(b, attribute)
                    swaps.append(bval)
                for a, bval in zip(candidates, swaps):
                    setattr(a, attribute, bval)

    @classmethod
    def groupshuffle(cls):
        if (not hasattr(cls, "groupshuffle_enabled")
                or not cls.groupshuffle_enabled):
            return

        numgroups = len(cls.groups)
        shuffled = list(range(numgroups))
        random.shuffle(shuffled)
        swapdict = {}
        for a, b in zip(list(range(numgroups)), shuffled):
            a = cls.getgroup(a)
            b = cls.getgroup(b)
            for a1, b1 in zip(a, b):
                swapdict[a1] = (b1.groupindex, b1.index, b1.pointer)

        for o in cls.every:
            groupindex, index, pointer = swapdict[o]
            o.groupindex = groupindex
            o.index = index
            o.pointer = pointer


already_gotten = {}


def get_table_objects(objtype):
    pointer = objtype.specspointer
    number = objtype.specscount
    grouped = objtype.specsgrouped
    pointed = objtype.specspointed
    identifier = (objtype, pointer, number)
    if identifier in already_gotten:
        return already_gotten[identifier]

    objects = []

    def add_objects(n, groupindex=0, p=None):
        if p is None:
            p = pointer
        accumulated_size = 0
        for i in range(n):
            obj = objtype(p, groupindex=groupindex)
            obj.index = len(objects)
            objects.append(obj)
            p += obj.total_size
            accumulated_size += obj.total_size
        return accumulated_size

    def add_variable_object(p1, p2):
        size = p2 - p1
        obj = objtype(p1, groupindex=0, size=size)
        obj.index = len(objects)
        objects.append(obj)
        return size

    if not grouped and not pointed:
        add_objects(number)
    elif pointed:
        assert(objtype.total_size > 0)
        size = objtype.specspointedsize
        counter = 0

        mname = objtype.region + '_' + objtype.__name__ + '_data'
        m = __import__(mname)
        f = io.BytesIO(m.DATA)

        while counter < number:
            p = pointer - objtype.specspointer
            assert(p >= 0)
            f.seek(p)
            subpointer = read_multi(f, size) + objtype.specspointedpointer
            f.seek(p + size)
            subpointer2 = read_multi(f, size) + objtype.specspointedpointer
            groupcount = (subpointer2 - subpointer) / objtype.total_size
            if objtype.specspointedpoint1:
                groupcount = 1
            add_objects(groupcount, groupindex=counter, p=subpointer)
            pointer += size
            counter += 1
        NUM_GROUPS_DICT[objtype] = counter

    already_gotten[identifier] = objects

    for o in objects:
        GRAND_OBJECT_DICT[objtype, o.index] = o

    return get_table_objects(objtype)


def set_table_specs(filename=None):
    if filename is None:
        filename = GLOBAL_TABLE
    tablesfile = path.join(tblpath, filename)
    for line in open(tablesfile):
        line = line.strip()
        if not line or line[0] == "#":
            continue

        while "  " in line:
            line = line.replace("  ", " ")
        line = line.split()
        groupednum = None
        if len(line) >= 5:
            (objname, tablefilename, pointer, count,
                organization) = tuple(line[:5])
            args = line[5:]
            if organization.lower() not in ["grouped", "pointed", "point1"]:
                raise NotImplementedError
            grouped = True if organization.lower() == "grouped" else False
            pointed = True if organization.lower() == "pointed" else False
            point1 = True if organization.lower() == "point1" else False
            pointed = pointed or point1
            if pointed:
                pointedpointer = int(args[0], 0x10)
                pointedsize = int(args[1]) if len(args) > 1 else 2
            if grouped and len(args) >= 1:
                groupednum = int(args[0])
        else:
            objname, tablefilename, pointer, count = tuple(line)
            grouped = False
            pointed = False
            point1 = False
        pointer = int(pointer, 0x10)
        count = int(count)
        TABLE_SPECS[objname] = TableSpecs(path.join(tblpath, tablefilename),
                                          pointer, count, grouped, pointed)
        if pointed or point1:
            TABLE_SPECS[objname].pointedpointer = pointedpointer
            TABLE_SPECS[objname].pointedsize = pointedsize
            TABLE_SPECS[objname].pointedpoint1 = point1
        if grouped:
            TABLE_SPECS[objname].groupednum = groupednum
