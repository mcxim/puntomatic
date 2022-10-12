from __future__ import annotations

from typing import Tuple, List, TypeVar, Callable, NamedTuple, Generic, Any
from operator import attrgetter
from cytoolz import curry

import gensim.downloader as api

from alignment import smith_waterman
from phonetics import (
    get_arpabet,
    phonetic_similarity,
    phonetic_skippability,
    alignment_table
)

model = api.load("word2vec-google-news-300")


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

    description: str

    def find_matches(
        self,
        options: List[Prioritized[PotentialMatch]],
    ) -> List[Prioritized[Match]]:
        """Finds matching pairs and constructs a combined word"""
        raise NotImplementedError

    def analyze_groups(
        self, first_group: List[Prioritized[str]], second_group: List[Prioritized[str]]
    ) -> List[Prioritized[Match]]:
        return self.find_matches(
            prioritized_match_pairs(
                list(map(Prioritized._make, first_group)),
                list(map(Prioritized._make, second_group)),
            )
        )


class PhoneticMatch(MatchType):
    description = """There are similar-sounding parts in both words, 
    prioritizing matcfhes in which only one of the words has unmatched sounds before
    the match and only one word has unmatched sounds after the match. That way, there
    is a clear way to combine those words.
    """

    def find_matches(
        self, options: List[Prioritized[PotentialMatch]]
    ) -> List[Prioritized[Match]]:
        matches: List[Prioritized[Match]] = []
        for ((first, second), priority) in options:
            try:
                first_phonemes = get_arpabet(first)
                second_phonemes = get_arpabet(second)
            except KeyError:
                continue
            (
                match_in_first,
                match_in_second,
                score,
                idx_in_first,
                idx_in_second,
            ) = smith_waterman(
                phonetic_similarity,
                phonetic_skippability,
                first_phonemes,
                second_phonemes,
            )
            if score > 1:
                matches.append(
                    Prioritized(
                        value=(
                            first,
                            second,
                            "{} {} {} {}".format(
                                match_in_first,
                                match_in_second,
                                idx_in_first,
                                idx_in_second,
                            ),
                        ),
                        priority=priority * score,
                    )
                )
        return sorted(matches, key=attrgetter("priority"), reverse=True)


class OrthographicMatch(MatchType):
    description = """Parts of the two words are spelt similarly"""

    def find_matches(self, options: List[Prioritized[PotentialMatch]]):
        matches: List[Prioritized[Match]] = []
        for ((first, second), priority) in options:
            (
                match_in_first,
                match_in_second,
                score,
                idx_in_first,
                idx_in_second,
            ) = smith_waterman(
                lambda x, y: 1 if x == y else -1, lambda x: 2, first, second
            )
            if score > 1:
                matches.append(
                    Prioritized(
                        value=(
                            first,
                            second,
                            "{} {} {} {}".format(
                                match_in_first,
                                match_in_second,
                                idx_in_first,
                                idx_in_second,
                            ),
                        ),
                        priority=priority * score,
                    )
                )
        return sorted(matches, key=attrgetter("priority"), reverse=True)


class Rhyme(MatchType):
    description = """Matching syllables in the ends of the two words"""
