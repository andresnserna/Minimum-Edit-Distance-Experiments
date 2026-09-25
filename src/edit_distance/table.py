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

    def compute(self) -> AlignmentResult:
        # INSTANTIATE Counters and Timer
        counter = Counters()
        timer = TimeTracker()
        timer.start()
        counter.calls += 1 # "compute()" is the find() method here, so by entering it you call the func at least once, but for each recursive call this var will be incremented

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
        self.dp = []
        for i in range(n + 1):
            row = []
            for j in range(m + 1):
                row.append(self.sentinel)
            self.dp.append(row)
            counter.record_base_case_initialization()

    # set these values in the table first 
        for j in range(1, m + 1):
            self.dp[0][j] = j * self.ins_cost
            counter.record_table_or_memo_write()

        for i in range(1, n + 1):
            self.dp[i][0] = i * self.del_cost
            counter.record_table_or_memo_write()

    # TABLE: the loop that fills in our tabulation table so we can return the minimum edit distance from a to b at the last matrix square of dp
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # get the previous cost, the following branches will need it
                prev_cell_diag = self.dp[i - 1][j - 1]
                prev_cell_left = self.dp[i - 1][j]
                prev_cell_up = self.dp[i][j - 1]
                counter.record_table_or_memo_read(3)

                # do the chars match at i?
                if string_a[i - 1] == string_b[j - 1]:
                    counter.record_character_equality_check()
                    # yes, so update this cell with the previous cost, since it will not change, 
                    distance = prev_cell_diag
                # no they don't match, so we need to know what the cost of editing A to B is here
                else:
                    # lets gather our three possible choices
                    delete_cost = self.del_cost + prev_cell_left
                    insert_cost = self.ins_cost + prev_cell_up
                    substitute_cost = self.sub_cost + prev_cell_diag

                    # lets take the lowest one
                    chosen_operation = self._best_choice(delete_cost, insert_cost, substitute_cost)
                    counter.record_minimum_of_k(3, 1)
        
                    if chosen_operation == "delete":
                        distance = delete_cost
                    elif chosen_operation == "insert":
                        distance = insert_cost
                    else: # substitute
                        distance = substitute_cost

                # record that distance to this cell of the dp table
                self.dp[i][j] = distance
                counter.record_table_or_memo_write()

        distance = self.dp[n][m] # after the big 'ol for-loop, the value at this cell in the matrix will have the minimum edit distance from a to b
        counter.record_table_or_memo_write()

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
