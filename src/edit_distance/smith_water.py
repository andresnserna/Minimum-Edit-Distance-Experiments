from __future__ import annotations

from collections.abc import Callable

from .base import AlignmentResult, EditDistanceEngine
from .counters import Counters
from .time import TimeTracker

GapCost = Callable[[int], float]
SimilarityScore = Callable[[str, str], float]


class SmithWaterEditDistance(EditDistanceEngine):
    """Smith–Waterman local alignment using length-dependent gap weights."""

    def __init__(
        self,
        string_a: str,
        string_b: str,
        match_score: float = 1.0,
        mismatch_score: float = -1.0 / 3.0,
        gap_cost: GapCost | None = None,
        similarity_score: SimilarityScore | None = None,
    ) -> None:
        super().__init__(string_a, string_b)
        self.match_score = match_score
        self.mismatch_score = mismatch_score
        self.gap_cost = (
            gap_cost if gap_cost is not None else lambda length: 1.0 + length / 3.0
        )
        self.similarity_score = similarity_score
        self.dp: list[list[float]] = []
        self._traceback: list[list[tuple[str, int] | None]] = []

    def compute(self) -> AlignmentResult:
        timer = TimeTracker()
        timer.function_name = type(self).__name__
        timer.start()
        counter = Counters()
        try:
            result = self.compute_helper(counter)
            timer.finish()
            result.time_summary = timer.as_dict()
            return result
        finally:
            counter.reset()

    def compute_helper(self, counter: Counters) -> AlignmentResult:
        counter.calls += 1
        string_a = self.string_a
        string_b = self.string_b
        length_a = len(string_a)
        length_b = len(string_b)

        self.dp = [[0.0] * (length_b + 1) for _ in range(length_a + 1)]
        self._traceback = [
            [None] * (length_b + 1) for _ in range(length_a + 1)
        ]
        counter.record_cell_allocation((length_a + 1) * (length_b + 1))
        counter.record_base_case_initialization(length_a + length_b + 1)

        best_score = 0.0
        best_position = (0, 0)

        for i in range(1, length_a + 1):
            for j in range(1, length_b + 1):
                char_a = string_a[i - 1]
                char_b = string_b[j - 1]
                if self.similarity_score is None:
                    counter.record_character_equality_check()
                    substitution_score = (
                        self.match_score if char_a == char_b else self.mismatch_score
                    )
                else:
                    counter.record_character_read(2)
                    substitution_score = self.similarity_score(char_a, char_b)

                counter.record_table_or_memo_read()
                candidates: list[tuple[float, str, int]] = [
                    (self.dp[i - 1][j - 1] + substitution_score, "diagonal", 1),
                    (0.0, "stop", 0),
                ]

                for gap_length in range(1, i + 1):
                    counter.record_table_or_memo_read()
                    candidates.append(
                        (
                            self.dp[i - gap_length][j] - self.gap_cost(gap_length),
                            "delete",
                            gap_length,
                        )
                    )

                for gap_length in range(1, j + 1):
                    counter.record_table_or_memo_read()
                    candidates.append(
                        (
                            self.dp[i][j - gap_length] - self.gap_cost(gap_length),
                            "insert",
                            gap_length,
                        )
                    )

                score, operation, gap_length = max(
                    candidates, key=lambda candidate: candidate[0]
                )
                counter.record_maximum_of_k(len(candidates))
                self.dp[i][j] = score
                if operation != "stop":
                    self._traceback[i][j] = (operation, gap_length)
                counter.record_table_or_memo_write()

                if score > best_score:
                    best_score = score
                    best_position = (i, j)

        edit_script = self._reconstruct_edit_script(*best_position)
        alignment_lines = self._build_local_alignment(edit_script, *best_position)
        start_a = best_position[0] - sum(
            operation in {".", "S", "D"} for operation in edit_script
        )
        start_b = best_position[1] - sum(
            operation in {".", "S", "I"} for operation in edit_script
        )
        return AlignmentResult(
            string_a=string_a,
            string_b=string_b,
            distance=best_score,
            edit_script=edit_script,
            alignment_lines=alignment_lines,
            counters_summary=counter.as_dict(),
            alignment_range_a=(start_a, best_position[0]),
            alignment_range_b=(start_b, best_position[1]),
        )

    def _reconstruct_edit_script(self, row: int, column: int) -> list[str]:
        operations: list[str] = []
        while row > 0 and column > 0 and self.dp[row][column] > 0:
            predecessor = self._traceback[row][column]
            if predecessor is None:
                break

            operation, gap_length = predecessor
            if operation == "diagonal":
                operations.append(
                    "."
                    if self.string_a[row - 1] == self.string_b[column - 1]
                    else "S"
                )
                row -= 1
                column -= 1
            elif operation == "delete":
                operations.extend(["D"] * gap_length)
                row -= gap_length
            else:
                operations.extend(["I"] * gap_length)
                column -= gap_length

        operations.reverse()
        return operations

    def _build_local_alignment(
        self, edit_script: list[str], end_row: int, end_column: int
    ) -> list[str]:
        aligned_a: list[str] = []
        aligned_b: list[str] = []
        operations: list[str] = []
        index_a = end_row - sum(
            operation in {".", "S", "D"} for operation in edit_script
        )
        index_b = end_column - sum(
            operation in {".", "S", "I"} for operation in edit_script
        )

        for operation in edit_script:
            if operation in {".", "S"}:
                aligned_a.append(self.string_a[index_a])
                aligned_b.append(self.string_b[index_b])
                index_a += 1
                index_b += 1
            elif operation == "D":
                aligned_a.append(self.string_a[index_a])
                aligned_b.append("-")
                index_a += 1
            else:
                aligned_a.append("-")
                aligned_b.append(self.string_b[index_b])
                index_b += 1
            operations.append(operation)

        return [" ".join(aligned_a), " ".join(aligned_b), " ".join(operations)]
