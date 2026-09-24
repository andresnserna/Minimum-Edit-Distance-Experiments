"""Memoized edit-distance implementation.

Purpose:
    This module defines the top-down dynamic-programming algorithm. It caches the
    value for each subproblem so the same states are not recomputed repeatedly.

Who should call this:
    The CLI or a test harness should instantiate this class when the user selects
    the memoized implementation.

This file is not responsible for:
    - bottom-up table construction
    - low-level command-line argument validation
    - research or plotting output
"""

from __future__ import annotations
from .base import AlignmentResult, EditDistanceEngine
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from typing import List

class MemoizedEditDistance(EditDistanceEngine):
    """Top-down memoized edit-distance engine."""

    def __init__(self, string_a, string_b, sub_cost=1, ins_cost=1, del_cost=1):
        super().__init__(string_a, string_b, sub_cost, ins_cost, del_cost)
        self.memo = None
        self.sentinel = -1 # what we fill the memo table with by default

    def compute(self) -> AlignmentResult:
        # the compute method is called to initialize the memoization table and start the recursive computation, the bulk of the work is done in the _distance method
       
        # INSTANTIATE Counters and Timer
        timer = TimeTracker()
        timer.start()
        counter = Counters()
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
        # self.memo = [[self.sentinel for _ in range(m + 1)] for _ in range(n + 1)]
        self.memo = []
        for i in range(n + 1):
            row = []
            for j in range(m + 1):
                row.append(self.sentinel)
            self.memo.append(row)
            counter.record_base_case_initialization()

    # MEMO: this is the recursive solver, that will fill in the memoization table as it goes to subproblems
        distance = self._distance(0, 0, counter)

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
    
    def _distance(self, m, n, counter: Counters) -> int:
    # MEMO base cases: one string is exhausted
        if m == len(self.string_a): # ("", "abc") → distance = 3 insertions
            return (len(self.string_b) - n) * self.ins_cost
        
        if n == len(self.string_b): # ("abc", "") → distance = 3 deletions
            return (len(self.string_a) - m) * self.del_cost

    # MEMO cache check
        if self.memo[m][n] != -1: # if the value has already been computed, return it
            counter.record_table_or_memo_read()
            return self.memo[m][n]

    # MEMO match case
        # ("abc", "abd") → distance = 0 + recurse("bc", "bd"), 
        # this is where the subproblem is solved recursively, and the result is stored in the memoization table
        if self.string_a[m] == self.string_b[n]: 
            counter.record_character_equality_check()
            distance = self._distance(m + 1, n + 1)
    # MEMO mismatch case
        # ("abc", "xyz") → distance = min(delete_cost, insert_cost, substitute_cost)
        ## delete_cost = self.del_cost + self._distance(m + 1, n)
        ## insert_cost = self.ins_cost + self._distance(m, n + 1)
        ## substitute_cost = self.sub_cost + self._distance(m + 1, n + 1)
        else:  
            delete_cost = self.del_cost + self._distance(m + 1, n)
            insert_cost = self.ins_cost + self._distance(m, n + 1)
            substitute_cost = self.sub_cost + self._distance(m + 1, n + 1)

            # CAUTION: tie breaker logic
            chosen_operation = self._best_choice(delete_cost, insert_cost, substitute_cost)
            counter.record_minimum_of_k(3)

            if chosen_operation == "delete":
                distance = delete_cost
            elif chosen_operation == "insert":
                distance = insert_cost
            else: # substitute
                distance = substitute_cost

        self.memo[m][n] = distance # add the computed distance to the memoization table for caching
        counter.record_table_or_memo_write()
        return distance

    def _build_alignment(self, edit_script):
        raise NotImplementedError
