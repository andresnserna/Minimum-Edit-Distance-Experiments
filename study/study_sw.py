from __future__ import annotations

import csv
import random
from pathlib import Path

from edit_distance.memo import MemoizedEditDistance
from edit_distance.smith_water import SmithWaterEditDistance
from edit_distance.table import TabulatedEditDistance
from study.study import Study

INPUT_LENGTHS = [10, 25, 50, 100, 200, 400, 600, 800, 1000]
SHARED_FRACTION = 0.5
IMPRACTICAL_THRESHOLD = 10
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
COUNTER_FIELDS = (
    "reads",
    "writes",
    "comparisons",
    "calls",
    "total_operations",
    "cells_allocated",
)
ALGORITHMS = (
    ("smith_waterman", SmithWaterEditDistance, "o-"),
    ("memoized", MemoizedEditDistance, "s-"),
    ("tabulated", TabulatedEditDistance, "^-"),
)


class _SmithWatermanStudyEngine(SmithWaterEditDistance):
    """Adapt Smith–Waterman to the shared Study worker constructor."""

    def __init__(
        self,
        string_a: str,
        string_b: str,
        sub_cost: int = 1,
        ins_cost: int = 1,
        del_cost: int = 1,
    ) -> None:
        super().__init__(string_a, string_b)


def make_shared_subsequence(
    length: int,
    fraction: float = SHARED_FRACTION,
    seed: int = Study.default_seed,
) -> tuple[str, str, str]:
    """Generate equal-length strings containing the same random contiguous block."""
    if length < 1:
        raise ValueError("length must be at least 1.")
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be greater than 0 and at most 1.")

    generator = random.Random(seed)
    shared_length = min(length, max(1, int(length * fraction)))
    shared = "".join(generator.choice(ALPHABET) for _ in range(shared_length))

    def make_string() -> str:
        prefix_length = generator.randrange(length - shared_length + 1)
        suffix_length = length - shared_length - prefix_length
        prefix = "".join(generator.choice(ALPHABET) for _ in range(prefix_length))
        suffix = "".join(generator.choice(ALPHABET) for _ in range(suffix_length))
        return prefix + shared + suffix

    return make_string(), make_string(), shared


class CaseSW(Study):
    """Compare Smith–Waterman, memoized edit distance, and tabulated edit distance."""

    def run(self) -> Path:
        result_dir = Study.results_root / "case_sw"
        result_dir.mkdir(parents=True, exist_ok=True)
        result_path = result_dir / "sw_results.csv"
        data: list[dict[str, object]] = []
        stopped_algorithms: dict[str, str] = {}

        for length in INPUT_LENGTHS:
            string_a, string_b, shared = make_shared_subsequence(
                length,
                seed=Study.default_seed + length,
            )
            for name, algorithm, _ in ALGORITHMS:
                stopped_status = stopped_algorithms.get(name)
                status = "skipped" if stopped_status is not None else "pending"
                elapsed_ms: float | str = ""
                result_value: int | float | str = ""
                summary: dict[str, int] | None = None
                edit_script: list[str] | None = None
                error_message = ""

                if status == "pending":
                    worker_algorithm = (
                        _SmithWatermanStudyEngine
                        if name == "smith_waterman"
                        else algorithm
                    )
                    try:
                        status, elapsed, summary, result, edit_script = (
                            self.run_with_timeout(
                                worker_algorithm,
                                string_a,
                                string_b,
                                IMPRACTICAL_THRESHOLD,
                            )
                        )
                    except RuntimeError as error:
                        status = "error"
                        error_message = str(error)
                        stopped_algorithms[name] = status
                    else:
                        elapsed_ms = round(elapsed * 1000, 3)
                        if result is not None:
                            result_value = result
                        if status in {"timeout", "error"}:
                            stopped_algorithms[name] = status
                else:
                    error_message = f"Skipped after prior {stopped_status}."

                row: dict[str, object] = {
                    "length": length,
                    "shared_fraction": SHARED_FRACTION,
                    "shared_length": len(shared),
                    "shared_subsequence": shared,
                    "string_a": string_a,
                    "string_b": string_b,
                    "algorithm": name,
                    "status": status,
                    "runtime_ms": elapsed_ms,
                    "score_or_distance": result_value,
                    "error": error_message,
                    "edit_script": " ".join(edit_script) if edit_script is not None else "",
                }
                row.update(
                    {
                        f"counter_{field}": (
                            summary[field] if summary is not None else ""
                        )
                        for field in COUNTER_FIELDS
                    }
                )
                data.append(row)

        fields = [
            "length",
            "shared_fraction",
            "shared_length",
            "shared_subsequence",
            "string_a",
            "string_b",
            "algorithm",
            "status",
            "runtime_ms",
            "score_or_distance",
            "error",
            "edit_script",
            *(f"counter_{field}" for field in COUNTER_FIELDS),
        ]
        with result_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

        self._save_operation_graph(data, result_dir / "sw_operation_counts.png")
        self._save_runtime_graph(data, result_dir / "sw_runtime.png")

        for algorithm, status in stopped_algorithms.items():
            print(
                f"{algorithm} stopped after {status}; later input lengths "
                "are recorded as skipped."
            )
        print(f"Smith–Waterman comparison results saved under {result_dir}.")
        return result_path

    def _save_operation_graph(
        self, data: list[dict[str, object]], output_path: Path
    ) -> None:
        series = self._build_algorithm_series(data, "counter_total_operations")
        if not series:
            raise RuntimeError("Cannot plot operation counts: no runs completed.")
        figure = self.generate_graph(
            series,
            output_path,
            title="Smith–Waterman vs. edit-distance operation counts",
            x_label="Input length",
            y_label="Total operations",
            chart_type="bar",
        )
        figure.show()

    def _save_runtime_graph(
        self, data: list[dict[str, object]], output_path: Path
    ) -> None:
        series = self._build_algorithm_series(data, "runtime_ms")
        if not series:
            raise RuntimeError("Cannot plot runtimes: no runs completed.")
        figure = self.generate_graph(
            series,
            output_path,
            title="Smith–Waterman vs. edit-distance runtime",
            x_label="Input length",
            y_label="Runtime (ms)",
        )
        figure.show()

    @staticmethod
    def _build_algorithm_series(
        data: list[dict[str, object]], value_field: str
    ) -> list[tuple[str, list[float], list[float], str]]:
        series = []
        for name, _, style in ALGORITHMS:
            rows = [
                row
                for row in data
                if row["algorithm"] == name and row["status"] == "completed"
            ]
            if rows:
                series.append(
                    Study.build_series(
                        name.replace("_", " ").title(),
                        rows,
                        "length",
                        value_field,
                        style,
                    )
                )
        return series


def main() -> None:
    CaseSW().run()


if __name__ == "__main__":
    main()
