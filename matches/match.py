from __future__ import annotations
from typing import List, Tuple, Callable, TypeVar, NamedTuple, Generic, Any
from toolz import curry
import string


A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class Prioritized(NamedTuple, Generic[A]):
    value: A
    priority: float


PotentialMatch = Tuple[str, str]

Match = Tuple[str, str, Any]


@curry
def cartesian_product(join: Callable[[A, B], C], xs: List[A], ys: List[B]) -> List[C]:
    return [join(x, y) for x in xs for y in ys]


prioritized_match_pairs: Callable[
    [List[Prioritized[str]], List[Prioritized[str]]], List[Prioritized[PotentialMatch]]
] = cartesian_product(
    lambda first, second: Prioritized(
        value=(first.value, second.value),
        priority=first.priority * second.priority,
    )
)


class MatchType:
    @staticmethod
    def sterilize_group(group: List[Tuple[str, float]]) -> List[Prioritized[str]]:
        return [
            Prioritized(*element)
            for element in group
            if all(c in string.printable for c in element[0])
        ]

    @classmethod
    def analyze_groups(
        cls,
        first_group: List[Tuple[str, float]],
        second_group: List[Tuple[str, float]],
    ) -> List[Prioritized[Match]]:
        return cls.find_matches(
            prioritized_match_pairs(
                cls.sterilize_group(first_group), cls.sterilize_group(second_group)
            )
        )
