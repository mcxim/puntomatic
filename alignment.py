"""
Shamelessly copied from slavianap's github and modified to fit our exact punning needs:
The algorithm now is only allowed to choose paths in which at least one of the words is 
completed, which means that matches after which both words still continue and matches
before which both words have content are penaltied. In other words, the algorithm is
prioritizing matches in which only one of the words has unmatched sounds before the
match and only one word has unmatched sounds after the match. That way, there is a
clear way to combine those words.

The "needleman" parameter runs the algorithm as regular needleman-wunsch.
"""
from enum import IntEnum
import numpy as np
from itertools import accumulate


# Assigning the constants for the scores
class Score(IntEnum):
    MATCH = 1
    MISMATCH = -1
    GAP = -1


# Assigning the constant values for the traceback
class Trace(IntEnum):
    STOP = 0
    LEFT = 1
    UP = 2
    DIAGONAL = 3


def old_smith_waterman(seq1, seq2):
    # Generating the empty matrices for storing scores and tracing
    row = len(seq1) + 1
    col = len(seq2) + 1
    matrix = np.zeros(shape=(row, col), dtype=np.int)
    tracing_matrix = np.zeros(shape=(row, col), dtype=np.int)

    # Initialising the variables to find the highest scoring cell
    max_score = -1
    max_index = (-1, -1)

    # Calculating the scores for all cells in the matrix
    for i in range(1, row):
        for j in range(1, col):
            # Calculating the diagonal score (match score)
            match_value = Score.MATCH if seq1[i - 1] == seq2[j - 1] else Score.MISMATCH
            diagonal_score = matrix[i - 1, j - 1] + match_value

            # Calculating the vertical gap score
            vertical_score = matrix[i - 1, j] + Score.GAP

            # Calculating the horizontal gap score
            horizontal_score = matrix[i, j - 1] + Score.GAP

            # Taking the highest score
            matrix[i, j] = max(0, diagonal_score, vertical_score, horizontal_score)

            # Tracking where the cell's value is coming from
            if matrix[i, j] == 0:
                tracing_matrix[i, j] = Trace.STOP

            elif matrix[i, j] == horizontal_score:
                tracing_matrix[i, j] = Trace.LEFT

            elif matrix[i, j] == vertical_score:
                tracing_matrix[i, j] = Trace.UP

            elif matrix[i, j] == diagonal_score:
                tracing_matrix[i, j] = Trace.DIAGONAL

            # Tracking the cell with the maximum score
            if matrix[i, j] >= max_score:
                max_index = (i, j)
                max_score = matrix[i, j]

    # Initialising the variables for tracing
    aligned_seq1 = ""
    aligned_seq2 = ""
    current_aligned_seq1 = ""
    current_aligned_seq2 = ""
    (max_i, max_j) = max_index

    # Tracing and computing the pathway with the local alignment
    while tracing_matrix[max_i, max_j] != Trace.STOP:
        if tracing_matrix[max_i, max_j] == Trace.DIAGONAL:
            current_aligned_seq1 = seq1[max_i - 1]
            current_aligned_seq2 = seq2[max_j - 1]
            max_i = max_i - 1
            max_j = max_j - 1

        elif tracing_matrix[max_i, max_j] == Trace.UP:
            current_aligned_seq1 = seq1[max_i - 1]
            current_aligned_seq2 = "-"
            max_i = max_i - 1

        elif tracing_matrix[max_i, max_j] == Trace.LEFT:
            current_aligned_seq1 = "-"
            current_aligned_seq2 = seq2[max_j - 1]
            max_j = max_j - 1

        aligned_seq1 = aligned_seq1 + current_aligned_seq1
        aligned_seq2 = aligned_seq2 + current_aligned_seq2

    # Reversing the order of the sequences
    aligned_seq1 = aligned_seq1[::-1]
    aligned_seq2 = aligned_seq2[::-1]

    return aligned_seq1, aligned_seq2


# Implementing the Smith Waterman local alignment
def smith_waterman(
    similarity,
    skippability,
    seq1,
    seq2,
    build_empty_element=lambda: [],
    needleman=False,
):
    # Generating the empty matrices for storing scores and tracing
    row = len(seq1) + 1
    col = len(seq2) + 1
    matrix = np.zeros(shape=(row, col), dtype=int)
    tracing_matrix = np.zeros(shape=(row, col), dtype=int)

    if needleman:
        matrix[:, 0] = list(
            accumulate(
                seq1,
                lambda accumulated, new: accumulated - skippability(new),
                initial=0,
            )
        )
        tracing_matrix[:, 0] = [0] + [Trace.UP] * (row - 1)

        matrix[0, :] = list(
            accumulate(
                seq2,
                lambda accumulated, new: accumulated - skippability(new),
                initial=0,
            )
        )
        tracing_matrix[0, :] = [0] + [Trace.LEFT] * (col - 1)

    # Initialising the variables to find the highest scoring cell
    max_score = float("-inf")
    max_index = (-1, -1)

    # Calculating the scores for all cells in the matrix
    for i in range(1, row):
        for j in range(1, col):
            # Calculating the diagonal score (match score)
            match_value = similarity(seq1[i - 1], seq2[j - 1])

            diagonal_score = matrix[i - 1, j - 1] + match_value

            # Calculating the vertical gap score
            vertical_score = matrix[i - 1, j] - skippability(seq1[i - 1])  # - 1

            # Calculating the horizontal gap score
            horizontal_score = matrix[i, j - 1] - skippability(seq2[j - 1])  # - 1

            # Taking the highest score
            matrix[i, j] = max(diagonal_score, vertical_score, horizontal_score)

            if matrix[i, j] == horizontal_score:
                tracing_matrix[i, j] = Trace.LEFT

            elif matrix[i, j] == vertical_score:
                tracing_matrix[i, j] = Trace.UP

            elif matrix[i, j] == diagonal_score:
                tracing_matrix[i, j] = Trace.DIAGONAL

            # Tracking the cell with the maximum score
            if (
                not needleman
                and matrix[i, j] >= max_score
                and (i == row - 1 or j == col - 1)
            ):
                max_index = (i, j)
                max_score = matrix[i, j]

    # Initialising the variables for tracing
    aligned_seq1 = []
    aligned_seq2 = []
    current_aligned_seq1 = []
    current_aligned_seq2 = []
    if needleman:
        (max_i, max_j) = (row - 1, col - 1)
    else:
        (max_i, max_j) = max_index

    # Tracing and computing the pathway with the local alignment

    if needleman:
        loop_condition = lambda i, j: i != 0 or j != 0
    else:
        loop_condition = lambda i, j: i * j > 0

    while loop_condition(max_i, max_j):
        if tracing_matrix[max_i, max_j] == Trace.DIAGONAL:
            current_aligned_seq1 = seq1[max_i - 1]
            current_aligned_seq2 = seq2[max_j - 1]
            max_i = max_i - 1
            max_j = max_j - 1

        elif tracing_matrix[max_i, max_j] == Trace.UP:
            current_aligned_seq1 = seq1[max_i - 1]
            current_aligned_seq2 = build_empty_element()
            max_i = max_i - 1

        elif tracing_matrix[max_i, max_j] == Trace.LEFT:
            current_aligned_seq1 = build_empty_element()
            current_aligned_seq2 = seq2[max_j - 1]
            max_j = max_j - 1

        aligned_seq1.append(current_aligned_seq1)
        aligned_seq2.append(current_aligned_seq2)

    # Reversing the order of the sequences
    aligned_seq1 = aligned_seq1[::-1]
    aligned_seq2 = aligned_seq2[::-1]

    if needleman:
        score = matrix[-1][-1]
    else:
        score = max_score

    return aligned_seq1, aligned_seq2, score, max_i, max_j
