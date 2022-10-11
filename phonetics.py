from typing import NamedTuple, List
from cytoolz import valmap
import json
from functools import lru_cache


class PhoneticWord:
    def __init__(self, graphemes: List[str], phonemes: List[str]):
        self.graphemes: List[str] = graphemes
        self.phonemes: List[str] = phonemes

    def _unaligned(self, elements: List[str]):
        return sum(
            [element.split("|") for element in elements if element != "_"],
            start=[],
        )

    @property
    @lru_cache()
    def unaligned_graphemes(self):
        return self._unaligned(self.graphemes)

    @property
    @lru_cache()
    def unaligned_phonemes(self):
        return self._unaligned(self.phonemes)


with open("./alignment.json", "r") as f:
    alignment_table: List[PhoneticWord] = valmap(
        lambda phonetic_word: PhoneticWord(**phonetic_word), json.load(f)
    )


def get_arpabet(word):
    return alignment_table[word].unaligned_phonemes


def phonetic_similarity(first_phoneme, second_phoneme):
    # TODO:  make this smart
    return 1 if first_phoneme == second_phoneme else -1


def phonetic_skippability(phoneme):
    # TODO:  make this smart
    return 1
