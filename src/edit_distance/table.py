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
        self.sentinel = 0

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
        counter.record_cell_allocation((n + 1) * (m + 1))

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
                # TESTING FOR CHK 1... REMOVE FOR FINAL
                # self._print_matrix("DP table:", self.dp)

        distance = self.dp[n][m] # after the big 'ol for-loop, the value at this cell in the matrix will have the minimum edit distance from a to b
        counter.record_table_or_memo_write()
        edit_script = self._reconstruct_edit_script()
        alignment_lines = self._build_alignment(edit_script)

    # Conclusion: build the return object
        result = AlignmentResult(
            string_a = self.string_a,
            string_b = self.string_b,
            distance=distance,
            edit_script=edit_script,
            alignment_lines=alignment_lines,
            counters_summary = counter.as_dict()
        )

        timer.finish()
        # TESTING FOR CHK 1... REMOVE FOR FINAL
        # self._print_matrix("DP table:", self.dp)
        return result        
    
    def _reconstruct_edit_script(self) -> List[str]:
        operations: List[str] = []
        index_a = len(self.string_a)
        index_b = len(self.string_b)

        while index_a > 0 and index_b > 0:
            if self.string_a[index_a - 1] == self.string_b[index_b - 1]:
                operations.append(".")
                index_a -= 1
                index_b -= 1
                continue

            delete_total = self.del_cost + self.dp[index_a - 1][index_b]
            insert_total = self.ins_cost + self.dp[index_a][index_b - 1]
            substitute_total = self.sub_cost + self.dp[index_a - 1][index_b - 1]
            choice = self._best_choice(delete_total, insert_total, substitute_total)

            if choice == "delete":
                operations.append("D")
                index_a -= 1
            elif choice == "insert":
                operations.append("I")
                index_b -= 1
            else:
                operations.append("S")
                index_a -= 1
                index_b -= 1

        operations.extend(["D"] * index_a)
        operations.extend(["I"] * index_b)
        return list(reversed(operations))
