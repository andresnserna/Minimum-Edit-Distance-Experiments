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
from edit_distance.counters import Counters
from edit_distance.memo import MemoizedEditDistance
from edit_distance.naive import NaiveEditDistance
from edit_distance.table import TabulatedEditDistance


def test_kitten_to_sitting_distance() -> None:
    """kitten -> sitting should have edit distance 3."""
    expected = 3
    naive_result = NaiveEditDistance("kitten", "sitting", 1, 1, 1).compute()
    memo_result = MemoizedEditDistance("kitten", "sitting", 1, 1, 1).compute()
    table_result = TabulatedEditDistance("kitten", "sitting", 1, 1, 1).compute()

    results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    mismatched = [name for name, value in results.items() if value != expected]
    if mismatched:
        raise AssertionError(
            f"Expected all algorithms to return {expected} for kitten->sitting, "
            f"but failed: {', '.join(f'{name}={results[name]}' for name in mismatched)}"
        )


def test_flaw_to_lawn_distance() -> None:
    """flaw -> lawn should have edit distance 2."""
    expected = 2
    naive_result = NaiveEditDistance("flaw", "lawn", 1, 1, 1).compute()
    memo_result = MemoizedEditDistance("flaw", "lawn", 1, 1, 1).compute()
    table_result = TabulatedEditDistance("flaw", "lawn", 1, 1, 1).compute()

    results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    mismatched = [name for name, value in results.items() if value != expected]
    if mismatched:
        raise AssertionError(
            f"Expected all algorithms to return {expected} for flaw->lawn, "
            f"but failed: {', '.join(f'{name}={results[name]}' for name in mismatched)}"
        )


def test_counter_methods() -> None:
    """Each event-specific helper should increment the matching counter and total."""
    counter = Counters()

    counter.record_table_or_memo_read()
    counter.record_table_or_memo_write()
    counter.record_character_read()
    counter.record_character_equality_check()
    counter.record_minimum_of_k(4)
    counter.record_base_case_initialization()

    assert counter.reads == 4
    assert counter.writes == 2
    assert counter.comparisons == 4
    assert counter.total_operations == 10
    assert counter.check() is True
    assert "DP table or memo cell" in counter.record_table_or_memo_read.__doc__

def test_emptyA_to_stringB() -> None:
    """ "" -> creek should have edit distance 5, and be all inserts. this test must return the right distance AND edit script to pass"""
    string_a = ""
    string_b = "creek"
    expected = 5
    test_case_name = "\"\" -> creek"

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    distance_results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    edit_script_results = {
        "naive": naive_result.edit_script,
        "memo": memo_result.edit_script,
        "table": table_result.edit_script,
    }
    mismatched_distances = [name for name, value in distance_results.items() if value != expected]
    mismatched_scripts = [name for name, value in edit_script_results.items() if value != expected]

    if mismatched_distances or mismatched_scripts:
        raise AssertionError(
            # TODO: show that it was the distance or script that mismatched, how do i do both without clogging the terminal with empty stuff, do i combine both?
            f"Expected all algorithms to return {expected} for {test_case_name}, "
            f"but failed: {', '.join(f'{name}={results[name]}' for name in mismatched)}"
        )

def test_stringA_to_emptyB() -> None:
    """ girl -> "" should have edit distance 4."""
    string_a = "girl"
    string_b = ""
    expected = 4
    test_case_name = "girl -> \"\""

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    distance_results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    edit_script_results = {
        "naive": naive_result.edit_script,
        "memo": memo_result.edit_script,
        "table": table_result.edit_script,
    }
    mismatched_distances = [name for name, value in distance_results.items() if value != expected]
    mismatched_scripts = [name for name, value in edit_script_results.items() if value != expected]

    if mismatched_distances or mismatched_scripts:
        raise AssertionError(
            # TODO: show that it was the distance or script that mismatched, how do i do both without clogging the terminal with empty stuff, do i combine both?
            f"Expected all algorithms to return {expected} for {test_case_name}, "
            f"but failed: {', '.join(f'{name}={results[name]}' for name in mismatched)}"
        )

def test_null_to_stringB() -> None:
    """ *null* -> "slayyy" should raise an error about missing args."""

    string_a = None
    string_b = "slayyy"
    expected = None #the right type of error, NONE IS WRONG
    test_case_name = "*null* -> \"slayyy\""

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }

    mismatched = [name for name, value in results.items() if value != expected]

    if mismatched:
        raise AssertionError(
            f"Expected all algorithms to return {expected} for {test_case_name}, "
            f"but failed: {', '.join(f'{name}={results[name]}' for name in mismatched)}"
        )
