from __future__ import annotations
from typing import List
from match import Match, PotentialMatch, Prioritized, MatchType
from phonetics.phonetics import get_arpabet
from alignment import smith_waterman
from operator import attrgetter


class RhymeMatch(MatchType):
    """
    The words rhyme - the stressed syllable is the same and the rest if similar.
    """

    @classmethod
    def find_matches(
        cls, options: List[Prioritized[PotentialMatch]]
    ) -> List[Prioritized[Match]]:
        matches: List[Prioritized[Match]] = []
        for ((first, second), priority) in options:
            # TODO: make this monadic and pretty somehow:
            first_phonemes = get_arpabet(first)
            if not first_phonemes:
                continue
            (first_stressed, first_phonemes) = first_phonemes.rhyme_ending
            second_phonemes = get_arpabet(second)
            if not second_phonemes:
                continue
            (second_stressed, second_phonemes) = second_phonemes.rhyme_ending
            if first_stressed[:2] != second_stressed[:2]:
                continue
            (alignment_in_first, alignment_in_second, score, _, _) = smith_waterman(
                lambda x, y: 1 if x == y else -1,
                lambda x: 1,
                first_phonemes,
                second_phonemes,
                needleman=True,
            )
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
