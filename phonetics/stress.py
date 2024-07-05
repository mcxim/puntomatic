"""
Vowels endings:
- 1 -> Primary stress
- 2 -> Secondary stress
- 0 -> No stress
"""

from .types import Phoneme
from typing import List

STRESS_TO_STRENGTH = {"1": 3, "2": 2, "0": 1}

MINIMUM_STRENGTH = min(STRESS_TO_STRENGTH.values())
MAXIMUM_STRENGTH = max(STRESS_TO_STRENGTH.values())

assert sorted(STRESS_TO_STRENGTH.values()) == list(
    range(MINIMUM_STRENGTH, MAXIMUM_STRENGTH + 1)
), "Strength should be continuous"

STRENGTH_TO_STRESS = dict([reversed(item) for item in STRESS_TO_STRENGTH.items()])


def strength_normalize(strength: int):
    if strength < MINIMUM_STRENGTH:
        return MINIMUM_STRENGTH
    if strength > MAXIMUM_STRENGTH:
        return MAXIMUM_STRENGTH
    return strength


def stress_add(stress: str, value: int) -> str:
    return STRENGTH_TO_STRESS[strength_normalize(STRESS_TO_STRENGTH[stress] + value)]


def vowel_strength(vowel: Phoneme) -> int:
    try:
        return STRESS_TO_STRENGTH.get(vowel[2], -1)
    except IndexError:
        return -1

def ignore_stress(vowel: str):
    return vowel[:2]

def equal_ignore_stress(vowel1: str, vowel2: str):
    return ignore_stress(vowel1) == ignore_stress(vowel2)

def chunks_equal_ignore_stress(chunk1: List[str], chunk2: List[str]):
    return all(map(equal_ignore_stress, chunk1, chunk2))
