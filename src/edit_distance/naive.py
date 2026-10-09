from __future__ import annotations
from .base import AlignmentResult, EditDistanceEngine
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from typing import List

class NaiveEditDistance(EditDistanceEngine):
    """Recursive edit-distance engine using the straightforward recurrence."""

    def compute(self) -> AlignmentResult:
        timer = TimeTracker()
        timer.start()
        counter = Counters()
        try:
            result = self.compute_helper(counter)
            timer.finish()
            return result
        finally:
            counter.reset()

    def compute_helper(self, counter: Counters) -> AlignmentResult:
        counter.calls += 1
        string_a = self.string_a
        string_b = self.string_b
        distance = 0
        edit_script: List[str] = []
        # alignment_lines: List[str] = []
        # counters_summary = None
   
    # NAIVE base case 1: if either string is empty
        if len(string_a) == 0: # ("", "abc") → distance = 3 insertions
            distance = len(string_b) * self.ins_cost
            edit_script = ["I"] * len(string_b)

        elif len(string_b) == 0: # ("abc", "") → distance = 3 deletions
            distance = len(string_a) * self.del_cost
            edit_script = ["D"] * len(string_a)

    # NAIVE base case 2: if both strings match
        elif string_a == string_b: # ("abc", "abc") → distance = 0
            counter.record_string_equality_check(string_a, string_b)
            distance = 0
            edit_script = ["."] * len(string_a)

        else:
    # NAIVE recursive case 1: if both strings are non-empty and do not match, but the first characters match
    # ("abc", "abd") → distance = 0 + recurse("bc", "bd")
            if string_a[0] == string_b[0]:
                counter.record_character_equality_check()
                result = NaiveEditDistance(
                    string_a[1:], 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute_helper(counter)
                distance = result.distance
                edit_script = ["."] + result.edit_script

            else: 
    # NAIVE recursive case 2: both strings are non-empty, do not match, and the first characters do not match
    # ("abc", "xyz") → distance = local_lowest_cost + recurse("bc", "yz")
    # local_cost + recursive_cost(child)
                del_result = NaiveEditDistance(
                    string_a[1:], 
                    string_b, 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute_helper(counter)

                ins_result = NaiveEditDistance(
                    string_a, 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute_helper(counter)

                sub_result = NaiveEditDistance(
                    string_a[1:], 
                    string_b[1:], 
                    self.sub_cost, 
                    self.ins_cost, 
                    self.del_cost
                ).compute_helper(counter)

                del_total = self.del_cost + del_result.distance
                ins_total = self.ins_cost + ins_result.distance
                sub_total = self.sub_cost + sub_result.distance

                best_choice = self._best_choice(del_total, ins_total, sub_total)
                counter.record_minimum_of_k(3) # finding minimum of the three values: del, ins, sub

                if best_choice == "delete":
                    distance = del_total
                    edit_script = ["D"] + del_result.edit_script
                elif best_choice == "insert":
                    distance = ins_total
                    edit_script = ["I"] + ins_result.edit_script
                else:
                    distance = sub_total
                    edit_script = ["S"] + sub_result.edit_script

        return AlignmentResult(
            string_a=string_a,
            string_b=string_b,
            distance=distance,
            edit_script=edit_script,
            alignment_lines=self._build_alignment(edit_script),
            counters_summary=counter.as_dict(),
        )

