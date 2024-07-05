from typing import List, TypeVar, Tuple

A = TypeVar("A")


def possible_splits(arr: Tuple[A, ...]) -> List[Tuple[Tuple[A, ...], Tuple[A, ...]]]:
    return [(arr[:n], arr[n:]) for n in range(1, len(arr) + 1)]

def unfold(f, x):
    while True:
        w, x = f(x)
        yield w

def recursive_iterate(f, x):
    return unfold(lambda y: (y, f(y)), x)
