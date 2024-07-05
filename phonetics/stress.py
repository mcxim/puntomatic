"""
Vowels endings:
- 1 -> Primary stress
- 2 -> Secondary stress
- 0 -> No stress
"""

from .types import Phoneme

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
    return STRESS_TO_STRENGTH.get(vowel, 0)