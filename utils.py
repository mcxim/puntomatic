from typing import List, TypeVar, Tuple

A = TypeVar("A")


def possible_splits(arr: Tuple[A, ...]) -> List[Tuple[Tuple[A, ...], Tuple[A, ...]]]:
    return [(arr[:n], arr[n:]) for n in range(1, len(arr) + 1)]
