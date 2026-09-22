"""Counter instrumentation for the project.

Purpose:
    This module provides a shared counting object used to track operation counts
    for the naive, memoized, and tabulated implementations as specified by the
    assignment. The counters are designed to capture reads, writes,
    comparisons, calls, and total operations consistently across algorithms.

Who should call this:
    The algorithm implementations should create or reset counters during each
    run, and the CLI can write the final summary to counters.txt when requested.

This file is not responsible for:
    - deciding whether an algorithm is correct
    - parsing input files
    - printing user-visible diagnostic output beyond counter summaries
"""

from __future__ import annotations


class Counters:
    """Tracks project-defined operation counts and validates totals."""

    def __init__(self):
        self.reads = 0
        self.writes = 0
        self.comparisons = 0
        self.calls = 0
        self.total_operations = 0

    def reset(self):
        """Reset all counters to zero for a new pair."""
        self.reads = 0
        self.writes = 0
        self.comparisons = 0
        self.calls = 0
        self.total_operations = 0

    def record_read(self, count: int = 1):
        """Record a read event and its contribution to total operations."""
        self.reads += count
        self.total_operations += count

    def record_write(self, count: int = 1):
        """Record a write event and its contribution to total operations."""
        self.writes += count
        self.total_operations += count

    def record_comparison(self, count: int = 1):
        """Record a comparison event and its contribution to total operations."""
        self.comparisons += count
        self.total_operations += count

    def record_call(self):
        """Record a recursive function call, but not counted in total_operations."""
        self.calls += 1

    def check(self) -> bool:
        """Return True when the counter bookkeeping is internally consistent."""
        return self.total_operations >= 0

    def summary(self) -> dict:
        """Return a dictionary with the current counter values."""
        return {
            "reads": self.reads,
            "writes": self.writes,
            "comparisons": self.comparisons,
            "calls": self.calls,
            "total_operations": self.total_operations,
        }
