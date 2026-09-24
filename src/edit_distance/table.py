"""Tabulated edit-distance implementation.

Purpose:
    This module introduces the bottom-up dynamic-programming algorithm. It builds
    the full DP table and reconstructs the optimal path from the stored
    decisions, which is the most natural iterative counterpart to the recurrence.

Who should call this:
    The CLI or a test harness should instantiate this class when the user selects
    the table implementation.

This file is not responsible for:
    - recursive naive search or memoization logic
    - input-file interpretation beyond the values passed in
    - external analysis scripts or plots
"""

from __future__ import annotations
from .base import AlignmentResult, EditDistanceEngine
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from typing import List


class TabulatedEditDistance(EditDistanceEngine):
    """Bottom-up tabulated edit-distance engine."""

    def __init__(self, string_a, string_b, sub_cost=1, ins_cost=1, del_cost=1):
        super().__init__(string_a, string_b, sub_cost, ins_cost, del_cost)
        self.dp = None
        self.sentinel = 0 # what we fill the memo table with by default


    def compute(self) -> AlignmentResult:
        # INSTANTIATE Counters and Timer
        counter = Counters()
        timer = TimeTracker()
        timer.start()

        # VARIABLES FOR RETURN
        string_a = self.string_a
        string_b = self.string_b
        distance = 0
        edit_script: List[str] = []
        alignment_lines: List[str] = []
        counters_summary = None

        # VARIABLES FOR THIS FUNCTION
        n = len(self.string_a)
        m = len(self.string_b)
        self.dp = [[self.sentinel for _ in range(m + 1)] for _ in range(n + 1)]

    # TABLE: the loop that fills in our tabulation table so we can return the minimum edit distance from a to b at the last matrix square of dp
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                raise NotImplementedError

        # TABLE base case 1: one string is empty
        # TABLE match case: 
        # TABLE mismatch case: 

        distance = self.dp[m][n] # after the big 'ol for-loop, the value at this cell in the matrix will have the minimum edit distance from a to b

    # Conclusion: build the return object
        result = AlignmentResult(
            string_a = self.string_a,
            string_b = self.string_b,
            distance=distance,
            edit_script=edit_script,
            alignment_lines=alignment_lines,
            counters_summary=counters_summary
        )

        timer.finish()
        return result

    def _build_alignment(self, edit_script):
        raise NotImplementedError
