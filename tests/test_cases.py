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
import pytest
from edit_distance.base import AlignmentResult
from edit_distance.counters import Counters
from edit_distance.io import OutputWriter
from edit_distance.memo import MemoizedEditDistance
from edit_distance.naive import NaiveEditDistance
from edit_distance.table import TabulatedEditDistance
from edit_distance.__main__ import main
import io
import contextlib

def assert_distance(test_case_name: str, expected: int, results: dict[str, int]) -> None:
    mismatched = {name: value for name, value in results.items() if value != expected}
    assert not mismatched, (
        f"Expected distance {expected} for {test_case_name}; "
        f"mismatched results: {mismatched}"
    )

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
    assert_distance(test_case_name, expected, distance_results)

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
    assert_distance(test_case_name, expected, distance_results)

def test_null_to_stringB() -> None:
    """Each engine should reject None as an input string."""
    engines = (NaiveEditDistance, MemoizedEditDistance, TabulatedEditDistance)

    for engine in engines:
        with pytest.raises(TypeError):
            engine(None, "slayyy", 1, 1, 1).compute()

# def test_checkpoint1_output_script() -> None:
#     """The project should print verification rows for each sample pair and algorithm."""
#     output = io.StringIO()

#     with contextlib.redirect_stdout(output):
#         exit_code = main()

#     assert exit_code == 0
#     rows = output.getvalue().strip().splitlines()
#     assert len(rows) == 15 # because testing 3 algorithms, 5 tests in each

#     for row in rows:
#         columns = row.split("\t")
#         assert len(columns) == 5
#         assert columns[0] in {"naive", "memo", "table"}
#         assert columns[3].isdigit()
#         assert columns[4].isdigit()

def test_beer_to_beans_distance() -> None:
    """Beer to beans should have edit distance 3."""
    string_a = "beer"
    string_b = "beans"
    expected = 3
    test_case_name = "beer -> beans"

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    distance_results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    assert_distance(test_case_name, expected, distance_results)

def test_write_counters(tmp_path) -> None:
    """
    Test that the summary output is of the right format, and that the counters file that was written to is in the right format \n
    Output format: A    B   distance
    """
    string_a = "A"
    string_b = "B"
    result = AlignmentResult(string_a, string_b, distance=1)
    counters_path = tmp_path / "counters.txt"

    OutputWriter.write_counters(counters_path, result)
    OutputWriter.write_counters(str(counters_path), result)

    assert counters_path.read_text(encoding="utf-8") == "A\tB\t1\nA\tB\t1\n"

    invalid_path = tmp_path / "counters.tsv"
    with pytest.warns(RuntimeWarning, match="expected a .txt file"):
        OutputWriter.write_counters(invalid_path, result)
    assert not invalid_path.exists()

def test_write_counters2(tmp_path) -> None:
    """
    Test that the summary output is of the right format, and that the counters file that was written to is in the right format \n
    Output format: A    B   distance \n
    this test if for cat -> bar
    """
    string_a = "cat"
    string_b = "bar"
    distance = 2
    result = AlignmentResult(string_a, string_b, distance)
    counters_path = tmp_path / "counters.txt"

    OutputWriter.write_counters(counters_path, result)
    OutputWriter.write_counters(str(counters_path), result)

    assert counters_path.read_text(encoding="utf-8") == "cat\tbar\t2\ncat\tbar\t2\n"

    invalid_path = tmp_path / "counters.tsv"
    with pytest.warns(RuntimeWarning, match="expected a .txt file"):
        OutputWriter.write_counters(invalid_path, result)
    assert not invalid_path.exists()

def test_algo_and_script() -> None:
    """
      test the algorithms, and test that they wrote the right edit script
    """

    raise NotImplementedError

def test_singleA_to_stringB() -> None:
    """ a -> clock should have edit distance 5, and be [edit script]. this test must return the right distance AND edit script to pass"""
    string_a = "a"
    string_b = "clock"
    expected = 5
    test_case_name = "a -> clock"

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    distance_results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    assert_distance(test_case_name, expected, distance_results)

def test_stringA_to_singleB() -> None:
    """ clock -> a should have edit distance 5, and be [edit script]. this test must return the right distance AND edit script to pass"""
    string_a = "clock"
    string_b = "a"
    expected = 5
    test_case_name = "clock -> a"

    naive_result = NaiveEditDistance(string_a, string_b, 1, 1, 1).compute()
    memo_result = MemoizedEditDistance(string_a, string_b, 1, 1, 1).compute()
    table_result = TabulatedEditDistance(string_a, string_b, 1, 1, 1).compute()

    distance_results = {
        "naive": naive_result.distance,
        "memo": memo_result.distance,
        "table": table_result.distance,
    }
    assert_distance(test_case_name, expected, distance_results)