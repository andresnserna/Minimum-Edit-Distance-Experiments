"""Initial test suite scaffold for the edit-distance project.

Purpose:
    This module is the starting point for the required A6 test suite. It is meant
    to hold the unit tests for empty strings, identical strings, simple single-
    character edits, no-shared-character cases, non-unit costs, and hand-checked
    examples.

Who should call this:
    This file is intended to be executed by pytest or Python’s unittest runner.

This file is not responsible for:
    - performance benchmarking or empirical plotting
    - final CLI execution against large TSV data files
    - generating the analysis document itself
"""

from __future__ import annotations
from edit_distance.naive import NaiveEditDistance


def test_kitten_to_sitting_distance() -> None:
    """kitten -> sitting should have edit distance 3."""
    result = NaiveEditDistance("kitten", "sitting", 1, 1, 1).compute()
    assert result.distance == 3


def test_flaw_to_lawn_distance() -> None:
    """flaw -> lawn should have edit distance 2."""
    result = NaiveEditDistance("flaw", "lawn", 1, 1, 1).compute()
    assert result.distance == 2
