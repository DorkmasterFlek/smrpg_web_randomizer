from .tablereader import sort_good_order
from .utils import utilrandom as random

sourcefile = None
outfile = None
flags = None
seed = None
difficulty = None


def get_outfile():
    global outfile
    return outfile


def get_seed():
    global seed
    return seed


def set_seed(s):
    global seed
    seed = s


def get_flags():
    global flags
    return flags


def set_flags(f):
    global flags
    flags = f


def clean_and_write(objects, seed=None, verbose=True):
    objects = sort_good_order(objects)
    for o in objects:
        if hasattr(o, "flag_description") and verbose:
            print("Cleaning %s." % o.flag_description.lower())
        if isinstance(seed, int):
            random.seed(seed + 1)
        o.full_cleanup()

    data = []
    for o in objects:
        data += o.write_all()
    return data
