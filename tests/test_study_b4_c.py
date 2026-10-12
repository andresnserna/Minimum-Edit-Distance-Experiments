from __future__ import annotations

from edit_distance.table import TabulatedEditDistance
from study.cost_weights import SCHEMES
from study.study import Study

LENGTHS = range(3, 11)
UPPERCASE_ALPHABET = [chr(character) for character in range(ord("A"), ord("Z") + 1)]


def test_b4_s4_finds_asymmetric_random_word_pair() -> None:
    """Find and report a random-word witness to S4's directional edit costs."""
    scheme = SCHEMES["S4"]
    assert scheme == {"sub": 1, "ins": 1, "del": 5}

    witness: tuple[str, str, int, int] | None = None
    for length_a in LENGTHS:
        for length_b in LENGTHS:
            seed = Study.default_seed + length_a * 100 + length_b
            string_a = Study.rand_word(
                UPPERCASE_ALPHABET,
                length_a,
                seed=seed,
            )
            string_b = Study.rand_word(
                UPPERCASE_ALPHABET,
                length_b,
                seed=seed + 1,
            )

            distance_ab = TabulatedEditDistance(
                string_a,
                string_b,
                sub_cost=scheme["sub"],
                ins_cost=scheme["ins"],
                del_cost=scheme["del"],
            ).compute().distance
            distance_ba = TabulatedEditDistance(
                string_b,
                string_a,
                sub_cost=scheme["sub"],
                ins_cost=scheme["ins"],
                del_cost=scheme["del"],
            ).compute().distance

            if distance_ab != distance_ba:
                witness = (string_a, string_b, distance_ab, distance_ba)
                break
        if witness is not None:
            break

    assert witness is not None, "No asymmetric S4 pair found for lengths 3 through 10."
    string_a, string_b, distance_ab, distance_ba = witness
    print(
        "S4 asymmetry witness: "
        f"A={string_a!r}, B={string_b!r}, "
        f"distance(A, B)={distance_ab}, distance(B, A)={distance_ba}"
    )

   #  A='DPA', B='NBJS'; distance(A, B)=4 and distance(B, A)=8.