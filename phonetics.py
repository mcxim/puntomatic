from typing import NamedTuple, List, NewType, Dict, Tuple
import re

from click import option
from utils import possible_splits
from string import ascii_lowercase
from cytoolz import valmap
import json
from methodtools import lru_cache
from collections.abc import Mapping

Phoneme = NewType("Phoneme", str)
Grapheme = NewType("Grapheme", str)


class PhoneticWord:
    def __init__(self, graphemes: List[str], phonemes: List[str]):
        self.graphemes: List[List[Grapheme]] = [
            list(map(Grapheme, grapheme.split("|") if grapheme != "-" else []))
            for grapheme in graphemes
        ]
        self.phonemes: List[List[Phoneme]] = [
            list(map(Phoneme, phoneme.split("|") if phoneme != "_" else []))
            for phoneme in phonemes
        ]

    @classmethod
    def from_lists(cls, graphemes: List[List[Grapheme]], phonemes: List[List[Phoneme]]):
        new_phonecit_word = cls([], [])
        new_phonecit_word.graphemes = graphemes
        new_phonecit_word.phonemes = phonemes
        return new_phonecit_word

    def __str__(self) -> str:
        grapheme_line = []
        phoneme_line = []
        for slot in range(len(self.graphemes)):
            grapheme_str = " ".join(self.graphemes[slot])
            phoneme_str = " ".join(self.phonemes[slot])
            max_len = max(len(grapheme_str), len(phoneme_str))
            grapheme_line.append(grapheme_str.center(max_len))
            phoneme_line.append(phoneme_str.center(max_len))
        return "|".join(grapheme_line) + "\n" + "|".join(phoneme_line)

    @property
    @lru_cache()
    def unaligned_phonemes(self):
        return sum(self.phonemes, start=[])

    def _slice_by(parameter):
        def slicer(self, start, stop):

            pass

        return slicer

    slice_by_grapheme = _slice_by("grapheme")
    slice_by_phoneme = _slice_by("phoneme")


class PhoneticDictionary(Mapping):
    """
    A lazily-computed list of `PhoneticWord`s
    """

    def __init__(self, initial_dictionary: Dict):
        self._raw_dict = initial_dictionary

    def __getitem__(self, key):
        return PhoneticWord(**self._raw_dict.__getitem__(key))

    def __iter__(self):
        return iter(self._raw_dict)

    def __len__(self):
        return len(self._raw_dict)

    def pronounce(self, bit_of_language: str) -> PhoneticWord:
        return self._pronounce_recursive(
            tuple(re.split("[^a-z']+", bit_of_language.lower()))
        )

    @lru_cache()
    def _pronounce_recursive(self, words: Tuple[str, ...]) -> PhoneticWord:
        if len(words) == 1:
            return self.__getitem__(words[0])
        options = []
        for init, rest in possible_splits(words):
            try:
                pronounced_init = self.__getitem__("-".join(init))
                pronounced_rest = self._pronounce_recursive(rest)
                options.append(
                    PhoneticWord.from_lists(
                        graphemes=[
                            *pronounced_init.graphemes,
                            [],
                            *pronounced_rest.graphemes,
                        ],
                        phonemes=[
                            *pronounced_init.phonemes,
                            [],
                            *pronounced_rest.phonemes,
                        ],
                    )
                )
            except (KeyError, IndexError):
                continue
        return options[-1]


with open("./alignment.json", "r") as f:
    alignment_table: PhoneticDictionary = PhoneticDictionary(json.load(f))


def get_arpabet(word):
    return alignment_table[word].unaligned_phonemes


def phonetic_similarity(first_phoneme, second_phoneme):
    # TODO:  make this smart
    return 1 if first_phoneme == second_phoneme else -1


def phonetic_skippability(phoneme):
    # TODO:  make this smart
    return 1
