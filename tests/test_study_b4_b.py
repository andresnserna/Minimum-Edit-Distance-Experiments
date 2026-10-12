from __future__ import annotations

from edit_distance.counters import Counters
from edit_distance.table import TabulatedEditDistance
from study.cost_weights import INPUT_LENGTHS, SCHEMES
from study.study import Study


def lcs_memo(S1: str, S2: str, m: int, n: int, memo: list[list[int]]) -> int:
    """Compute LCS length with the project's memoized LCS recurrence."""
    if m == 0 or n == 0:
        return 0

    if memo[m][n] != -1:
        return memo[m][n]

    if S1[m - 1] == S2[n - 1]:
        result = 1 + lcs_memo(S1, S2, m - 1, n - 1, memo)
    else:
        left = lcs_memo(S1, S2, m, n - 1, memo)
        right = lcs_memo(S1, S2, m - 1, n, memo)

        result = left if left > right else right

    memo[m][n] = result
    return result


def test_b4_s3_distance_matches_lcs_identity_for_study_inputs() -> None:
    """S3 has no useful substitutions, so its distance is |A| + |B| - 2*LCS."""
    scheme = SCHEMES["S3"]
    assert scheme == {"sub": 3, "ins": 1, "del": 1}

    for length in INPUT_LENGTHS:
        string_a = Study.rand_word(
            Study.eng_alphabet_low,
            length,
            seed=Study.default_seed,
        )
        string_b = Study.rand_word(
            Study.eng_alphabet_low,
            length,
            seed=Study.default_seed + 1,
        )
        result = TabulatedEditDistance(
            string_a,
            string_b,
            sub_cost=scheme["sub"],
            ins_cost=scheme["ins"],
            del_cost=scheme["del"],
        ).compute()
        memo = [[-1] * (len(string_b) + 1) for _ in range(len(string_a) + 1)]
        lcs_length = lcs_memo(
            string_a,
            string_b,
            len(string_a),
            len(string_b),
            memo,
            Counters(),
        )
        expected_distance = (
            len(string_a) + len(string_b) - 2 * lcs_length
        )

        assert result.distance == expected_distance, (
            f"S3 LCS identity failed for input length {length}: "
            f"distance={result.distance}, expected={expected_distance}, "
            f"LCS={lcs_length}"
        )
        assert "S" not in result.edit_script, (
            f"S3 selected a substitution for input length {length}: "
            f"{result.edit_script}"
        )