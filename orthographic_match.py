from __future__ import annotations
from typing import List
from match import Match, PotentialMatch, Prioritized, MatchType
from alignment import smith_waterman
from operator import attrgetter


class OrthographicMatch(MatchType):
    """
    Parts of both words are spelt similarly.
    """

    @classmethod
    def find_matches(
        cls, options: List[Prioritized[PotentialMatch]]
    ) -> List[Prioritized[Match]]:
        matches: List[Prioritized[Match]] = []
        for ((first, second), priority) in options:
            (
                match_in_first,
                match_in_second,
                score,
                idx_in_first,
                idx_in_second,
            ) = smith_waterman(
                lambda x, y: 1 if x == y else -1, lambda x: 1, first, second
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
