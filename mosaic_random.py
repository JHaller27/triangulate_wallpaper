import random
import sys


seed = None
random_obj = None


def set_seed(val) -> None:
    global seed

    seed = val


def random_seed() -> int:
    return random.randint(0, sys.maxsize)


def get_seed() -> int:
    global seed

    if seed is None:
        seed = random_seed()

    return seed


def get_random() -> random.Random:
    global random_obj

    if random_obj is None:
        random_obj = random.Random(get_seed())

    return random_obj
