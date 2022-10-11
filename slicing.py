from typing import Union
from itertools import takewhile, accumulate
from math import modf
from fractions import Fraction


def idx_inflate(matrix, flat_index: Union[Fraction, int]):
    iterator_matrix = iter(matrix)
    scan = list(
        takewhile(
            lambda accumulated_elements: accumulated_elements <= flat_index,
            accumulate(
                iterator_matrix,
                lambda accumulated_elements, new_elements: accumulated_elements
                + len(new_elements),
                initial=0,
            ),
        )
    )
    return (Fraction(flat_index) - scan[-1]) / len(matrix[len(scan) - 1]) + (
        len(scan) - 1
    )


def idx_deflate(matrix, real_index: Fraction):
    whole_index = int(real_index)
    ratio = real_index - whole_index
    return sum(len(array) for array in matrix[:whole_index]) + ratio * len(
        matrix[whole_index]
    )
