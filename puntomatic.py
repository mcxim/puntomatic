from __future__ import annotations
from ctypes import alignment

from typing import Tuple, List, TypeVar, Callable, NamedTuple, Generic, Any
from operator import attrgetter
from cytoolz import curry
import string

import gensim.downloader as api

from alignment import smith_waterman
from phonetics import (
    get_arpabet,
    phonetic_similarity,
    phonetic_skippability,
    alignment_table,
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

    @staticmethod
    def _sterilize_group(group: List[Tuple[str, float]]) -> List[Prioritized[str]]:
        return [
            Prioritized(*element)
            for element in group
            if all(c in string.printable for c in element[0])
        ]

    def analyze_groups(
        self,
        first_group: List[Tuple[str, float]],
        second_group: List[Tuple[str, float]],
    ) -> List[Prioritized[Match]]:
        return self.find_matches(
            prioritized_match_pairs(
                self._sterilize_group(first_group), self._sterilize_group(second_group)
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
            # TODO: make this monadic and pretty somehow:
            first_phonemes = get_arpabet(first)
            if not first_phonemes:
                continue
            first_phonemes = first_phonemes.unaligned_phonemes
            second_phonemes = get_arpabet(second)
            if not second_phonemes:
                continue
            second_phonemes = second_phonemes.unaligned_phonemes
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

    def find_matches(
        self, options: List[Prioritized[PotentialMatch]]
    ) -> List[Prioritized[Match]]:
        matches: List[Prioritized[Match]] = []
        for ((first, second), priority) in options:
            # TODO: make this monadic and pretty somehow:
            first_phonemes = get_arpabet(first)
            if not first_phonemes:
                continue
            first_phonemes = first_phonemes.rhyme_ending
            second_phonemes = get_arpabet(second)
            if not second_phonemes:
                continue
            second_phonemes = second_phonemes.rhyme_ending
            (alignment_in_first, alignment_in_second, score, _, _) = smith_waterman(
                lambda x, y: 1 if x == y else -1,
                lambda x: 2,
                first_phonemes,
                second_phonemes,
                needleman=True,
            )
            print(score)
            if score > 1:
                matches.append(
                    Prioritized(
                        value=(
                            first,
                            second,
                            "{} {}".format(alignment_in_first, alignment_in_second),
                        ),
                        priority=priority * score,
                    )
                )
        return sorted(matches, key=attrgetter("priority"), reverse=True)
