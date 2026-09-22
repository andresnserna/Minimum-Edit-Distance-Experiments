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


class NaiveEditDistance(EditDistanceEngine):
    """Recursive edit-distance engine using the straightforward recurrence."""

    def compute(self) -> AlignmentResult:
        raise NotImplementedError

    def _build_alignment(self, edit_script):
        raise NotImplementedError
