from __future__ import annotations
import pytest
from edit_distance import SmithWaterEditDistance
from edit_distance.counters import Counters


def test_paper_example() -> None:
    result = SmithWaterEditDistance(
        "AAUGCCAUUGACGG",
        "CAGCCUCGCUUAG",
    ).compute()

    assert result.distance == pytest.approx(10 / 3)
    assert result.alignment_lines == [
        "G C C A U U G",
        "G C C - U C G",
        ". . . D . S .",
    ]
    assert result.alignment_range_a == (3, 10)
    assert result.alignment_range_b == (2, 8)


def test_returns_best_local_subsequence_alignment() -> None:
    result = SmithWaterEditDistance(
        "XXABCYY",
        "ZZABCWW",
        match_score=2,
        mismatch_score=-3,
    ).compute()

    assert result.distance == 6
    assert result.edit_script == [".", ".", "."]
    assert result.alignment_lines == ["A B C", "A B C", ". . ."]
    assert result.alignment_range_a == (2, 5)
    assert result.alignment_range_b == (2, 5)
    assert result.counters_summary is not None
    assert result.counters_summary["cells_allocated"] == 8 * 8
    assert result.time_summary is not None
    assert result.time_summary["total_TIME"] >= 0


def test_no_match() -> None:
    result = SmithWaterEditDistance(
        "A",
        "B",
        match_score=1,
        mismatch_score=-2,
        gap_cost=lambda length: 1,
    ).compute()

    assert result.distance == 0
    assert result.edit_script == []
    assert result.alignment_lines == ["", "", ""]


def test_custom_similarity_function_scores_character_pairs() -> None:
    result = SmithWaterEditDistance(
        "A",
        "B",
        similarity_score=lambda char_a, char_b: 2 if (char_a, char_b) == ("A", "B") else -1,
        gap_cost=lambda length: length,
    ).compute()

    assert result.distance == 2
    assert result.edit_script == ["S"]
    assert result.alignment_lines == ["A", "B", "S"]


def test_length_dependent_gap_is_used_in_recurrence() -> None:
    result = SmithWaterEditDistance(
        "ABC",
        "AC",
        match_score=2,
        mismatch_score=-3,
        gap_cost=lambda length: length / 2,
    ).compute()

    assert result.distance == 3.5
    assert result.edit_script == [".", "D", "."]
    assert result.alignment_lines == ["A B C", "A - C", ". D ."]


def test_maximum_counter_tracks_candidate_comparisons() -> None:
    counter = Counters()
    counter.record_maximum_of_k(4, 2)

    assert counter.comparisons == 6
    assert counter.total_operations == 6
    assert counter.check()
