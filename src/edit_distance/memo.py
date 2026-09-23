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


class MemoizedEditDistance(EditDistanceEngine):
    """Top-down memoized edit-distance engine."""

    def compute(self) -> AlignmentResult:
        raise NotImplementedError

    def _build_alignment(self, edit_script):
        raise NotImplementedError
