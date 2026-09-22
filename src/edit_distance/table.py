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


class TabulatedEditDistance(EditDistanceEngine):
    """Bottom-up tabulated edit-distance engine."""

    def compute(self) -> AlignmentResult:
        raise NotImplementedError

    def _build_alignment(self, edit_script):
        raise NotImplementedError
