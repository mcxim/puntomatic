from typing import NamedTuple, List, NewType, Dict, Tuple, Optional
import re
from utils import possible_splits
import json
from methodtools import lru_cache
from collections.abc import Mapping
from .stress import vowel_strength
from .diphthongs import DIPHTHONGS
from .types import Phoneme, Grapheme


class PhoneticWord:
    def __init__(
        self,
        graphemes: List[List[Grapheme]],
        phonemes: List[List[Phoneme]],
        unroll_them_diphthongs: bool = True,
    ):
        if len(graphemes) != len(phonemes):
            raise ValueError(
                "Numbers of graphemes and phonemes alignment chunks should match."
            )
        self.graphemes = graphemes
        self.phonemes = phonemes
        if unroll_them_diphthongs:
            self.unroll_diphthongs()

    @classmethod
    def from_stored(cls, stored_graphemes: List[str], stored_phonemes: List[str]):
        graphemes: List[List[Grapheme]] = [
            list(map(Grapheme, grapheme.split("|") if grapheme != "-" else []))
            for grapheme in graphemes
        ]
        phonemes: List[List[Phoneme]] = [
            list(map(Phoneme, phoneme.split("|") if phoneme != "_" else []))
            for phoneme in phonemes
        ]
        return cls(graphemes, phonemes)

    def unroll_diphthongs(self) -> List[List[Phoneme]]:
        # new_phonemes = [
        #     sum((unroll_diphthong(phoneme) for phoneme in chunk), start=[])
        #     for chunk in self.phonemes
        # ]
        for idx, chunk in enumerate(self.phonemes):
            for (phonemes, split_when) in DIPHTHONGS.values():
                if self.graphemes[idx] in split_when:
                    pass

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.__class__(
                self.graphemes[key], self.phonemes[key], unroll_them_diphthongs=False
            )

    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise ValueError("Addition only possible between two PhoneticWords. ")
        return type(self)(
            self.graphemes + other.graphemes,
            self.phonemes + other.phonemes,
            unroll_them_diphthongs=False,
        )

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
    def unaligned_phonemes(self):
        return sum(self.phonemes, start=[])

    # def _slice_by(source_parameter):
    #     @functools.wraps
    #     def slicer(self, start, stop):
    #         pass
    #         # target_parameter = self.OTHER_PARAMETER[source_parameter]
    #         # start_idx = idx_deflate()

    #     return slicer

    # slice_by_grapheme = _slice_by("grapheme")
    # slice_by_phoneme = _slice_by("phoneme")

    @property
    def rhyme_ending(self):
        """
        Returns the end of the word, starting at the most stressed vowel. It is the
        part that is relevant for rhyming.
        """
        phonemes = self.unaligned_phonemes
        (index, strongest_vowel) = max(
            list(enumerate(phonemes))[::-1], key=lambda pair: vowel_strength(pair[1])
        )
        return phonemes[index], phonemes[index + 1 :]


class PhoneticDictionary(Mapping):
    """
    A lazily-computed list of `PhoneticWord`s
    """

    def __init__(self, initial_dictionary: Dict):
        self._raw_dict = initial_dictionary

    def __getitem__(self, key):
        return PhoneticWord.from_stored(**self._raw_dict.__getitem__(key))

    def __iter__(self):
        return iter(self._raw_dict)

    def __len__(self):
        return len(self._raw_dict)

    def pronounce(self, bit_of_language: str) -> Optional[PhoneticWord]:
        try:
            result = self._pronounce_recursive(
                tuple(re.split("[^a-z']+", bit_of_language.lower()))
            )
            if len(result.unaligned_phonemes) > 0:
                return result
            else:
                return None
        except (IndexError, KeyError):
            return None

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
                    PhoneticWord(
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


def get_arpabet(bit_of_language):
    return alignment_table.pronounce(bit_of_language)


def phonetic_similarity(first_phoneme, second_phoneme):
    # TODO:  make this smart
    return 1 if first_phoneme[:2] == second_phoneme[:2] else -1


def phonetic_skippability(phoneme):
    # TODO:  make this smart
    return 1
