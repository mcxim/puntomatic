from typing import NamedTuple, List, Dict, Optional
from .stress import stress_add, ignore_stress, get_stress
from .types import Phoneme, Grapheme
from utils import recursive_iterate
from functools import partial

Diphthong = NamedTuple(
    "Diphthong", [("phonemes", List[Phoneme]), ("split_when", List[List[Grapheme]])]
)

VOWELS = ["IY", "IH", "EY", "EH", "AE", "AH", "AA", "AO", "ER", "OW", "UH", "UW"]

# Ended up just going through https://en.wikipedia.org/wiki/ARPABET and defining the ones that
# represent two IPA symbols:
DIPHTHONGS: Dict[Phoneme, Diphthong] = {
    "AY": Diphthong(phonemes=["AA", "IH"], split_when=[["a", "y"]]),
    "AW": Diphthong(
        phonemes=["AA", "UH"], split_when=[["o", "u"], ["a", "u"], ["o", "w"]]
    ),
    "OY": Diphthong(phonemes=["AO", "IH"], split_when=[["o", "y"], ["o", "i"]]),
    "EY": Diphthong(phonemes=["EH", "IH"], split_when=[["e", "i"], ["a", "i"]]),
    # Those ones aren't really diphthongs, but the logic the implemented logic is here too:
    "ER": Diphthong(phonemes=["EH", "R"], split_when=[["e", "r"], ["a", "r"]]),
    "DJ": Diphthong(phonemes=["D", "JH"], split_when=[["d", "j"], ["d", "g"]]),
    # This one has its own IPA symbol, but can really be thought of as just n and g:
    "NG": Diphthong(phonemes=["N", "G"], split_when=[["n", "g"]]),
}


def stress_if_vowel(phoneme: Phoneme, stresses):
    if phoneme in VOWELS:
        return phoneme + next(stresses)
    return phoneme


def unroll_diphthong(diphthong: Phoneme) -> Optional[List[Phoneme]]:
    new_phonemes = DIPHTHONGS[ignore_stress(diphthong)].phonemes
    assert len(new_phonemes) == 2, "Not supported"
    decreaseing_stress = recursive_iterate(
        partial(stress_add, value=-1), get_stress(diphthong)
    )
    result = []
    result.append([stress_if_vowel(new_phonemes[0], decreaseing_stress)])
    result.append([stress_if_vowel(new_phonemes[1], decreaseing_stress)])
    return result
