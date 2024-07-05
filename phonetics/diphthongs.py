from typing import NamedTuple, List, Dict, Optional
from .stress import stress_add
from .types import Phoneme, Grapheme

Diphthong = NamedTuple(
    "Diphthong", [("phonemes", List[Phoneme]), ("split_when", List[List[Grapheme]])]
)

VOWELS = ["IY", "IH", "EY", "EH", "AE", "AH", "AA", "AO", "ER", "OW", "UH", "UW"]

DIPHTHONGS: Dict[Phoneme, Diphthong] = {
    "AY": Diphthong(phonemes=["AA", "IH"], split_when=[["a", "y"]]),
    "AW": Diphthong(
        phonemes=["AA", "UH"], split_when=[["o", "u"], ["a", "u"], ["o", "w"]]
    ),
    "OY": Diphthong(phonemes=["AO", "IH"], split_when=[["o", "y"], ["o", "i"]]),
    "ER": Diphthong(phonemes=["EH", "R"], split_when=[["e", "r"]]),
}


def stress_if_vowel(phoneme: Phoneme, stress):
    if phoneme in VOWELS:
        return phoneme + stress
    return phoneme


def unroll_diphthong(maybe_diphthong: Phoneme) -> Optional[List[Phoneme]]:
    stress = maybe_diphthong[-1]
    arpabet = maybe_diphthong[:-1]
    if stress.isdigit() and arpabet in DIPHTHONGS.keys():
        new_phonemes = DIPHTHONGS[arpabet].phonemes
        assert len(new_phonemes) == 2, "Not supported"
        return [
            [stress_if_vowel(new_phonemes[0], stress)],
            [stress_if_vowel(new_phonemes[1], stress_add(stress, -1))]
        ]

    return None
