from __future__ import annotations
from typing import List
from match import Match, PotentialMatch, Prioritized, MatchType
from alignment import smith_waterman
from phonetics.phonetics import get_arpabet, phonetic_similarity, phonetic_skippability
from operator import attrgetter


class PhoneticMatch(MatchType):
    """
    There are similar-sounding parts in both words.
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
