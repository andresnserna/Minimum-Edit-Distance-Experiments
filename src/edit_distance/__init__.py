"""Edit distance project package.

Purpose:
    This package provides the base structure for the COSC 4367 edit-distance
    assignment. It contains the CLI entry point, shared model objects, counter
    instrumentation, input parsing utilities, and the algorithm classes that will
    compute naive, memoized, and tabulated edit distance.

Who should call this:
    The package is intended to be invoked through the CLI or imported by tests
    that validate algorithm behavior and output formatting.

This file is not responsible for:
    - implementing the recurrence logic itself
    - performing final data analysis or plotting
    - reading project-specific performance data from disk
"""

__all__ = [
    "AlignmentResult",
    "Counters",
    "EditDistanceEngine",
    "EditDistanceCLI",
]
