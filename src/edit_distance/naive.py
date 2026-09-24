"""Naive recursive edit-distance implementation.

Purpose:
    This module defines the naive algorithm class for the project. It is meant to
    be the baseline implementation that enumerates candidate edit scripts directly
    through recursion and computes the minimum cost.

Who should call this:
    The CLI or a test harness should instantiate this class when the user selects
    the naive implementation.

This file is not responsible for:
    - memoization or tabulation optimizations
    - final CLI parsing or user interaction
    - empirical study measurements
"""

from __future__ import annotations
from .base import AlignmentResult, EditDistanceEngine
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from typing import List


class NaiveEditDistance(EditDistanceEngine):
    """Recursive edit-distance engine using the straightforward recurrence."""

    def compute(self) -> AlignmentResult:
        # PRECONDITION: none, EditDistanceEngine constructor already validated the strings and costs
        
        # INSTANTIATE Counters and Timer
        timer = TimeTracker()
        timer.start()
        counter = Counters()

        # VARIABLES FOR RETURN
        string_a = self.string_a
        string_b = self.string_b
        distance = 0
        edit_script: List[str] = []
        alignment_lines: List[str] = []
        counters_summary = None

        counter.calls += 1 # "compute()" is the find() method here, so by entering it you call the func at least once, but for each recursive call this var will be incremented
   
    # NAIVE base case 1: if either string is empty
        if len(string_a) == 0: # ("", "abc") → distance = 3 insertions
            # TODO: add counting here
            # TODO: update edit_script and alignment_lines to reflect the insertions

            distance = len(string_b) * self.ins_cost

        elif len(string_b) == 0: # ("abc", "") → distance = 3 deletions
            # TODO: add counting here
            # TODO: update edit_script and alignment_lines to reflect the insertions

            distance = len(string_a) * self.del_cost

    # NAIVE base case 2: if both strings match
        elif string_a == string_b: # ("abc", "abc") → distance = 0
            # TODO: add counting here
            # TODO: update edit_script and alignment_lines to reflect the insertions

            distance = 0

        else:
    # NAIVE recursive case 1: if both strings are non-empty and do not match, but the first characters match
    # ("abc", "abd") → distance = 0 + recurse("bc", "bd")
            if string_a[0] == string_b[0]:
                counter.record_character_equality_check()
                # TODO: update edit_script and alignment_lines to reflect the insertions
                
                result = NaiveEditDistance(
                    string_a[1:], 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute()
                distance = result.distance

            else: 
    # NAIVE recursive case 2: both strings are non-empty, do not match, and the first characters do not match
    # ("abc", "xyz") → distance = local_lowest_cost + recurse("bc", "yz")
    # local_cost + recursive_cost(child)
                # TODO: add counting here
                # TODO: update edit_script and alignment_lines to reflect the insertions
                del_result = NaiveEditDistance(
                    string_a[1:], 
                    string_b, 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute()

                ins_result = NaiveEditDistance(
                    string_a, 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute()

                sub_result = NaiveEditDistance(
                    string_a[1:], 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute()

                del_total = self.del_cost + del_result.distance
                ins_total = self.ins_cost + ins_result.distance
                sub_total = self.sub_cost + sub_result.distance

                best_choice = self._best_choice(del_total, ins_total, sub_total)
                counter.record_minimum_of_k(3) # finding minimum of the three values: del, ins, sub

                if best_choice == "delete":
                    distance = del_total
                elif best_choice == "insert":
                    distance = ins_total
                else:
                    distance = sub_total


        # Conclusion: build the return object
        result = AlignmentResult(
            string_a=string_a,
            string_b=string_b,
            distance=distance,
            edit_script=edit_script,
            alignment_lines=alignment_lines,
            counters_summary=counters_summary,
        )
        timer.finish()
        return result

    def _build_alignment(self, edit_script):
        raise NotImplementedError
