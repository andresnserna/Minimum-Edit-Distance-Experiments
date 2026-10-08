# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B3

# Memoized vs. Tabulated

# Compare A2 and A3 on identical inputs across all of:
# - total_operations
# - Run time (ms)
# - table cells allocated, for A3 this will be the size of the full table; for A2 it will be the
#   number of memo entries actually created (is there a formula to find this, or is it input dependent?)
# - maximum recursion depth reached for A2

# These two implementations compute the same recurrence and will have very similar operation
# counts. If your implementations are correct, the operation counts should be similar, but what
# about their run times? The number of cells allocated?

from __future__ import annotations
import csv
from study.study import Study
from edit_distance.memo import MemoizedEditDistance
from edit_distance.table import TabulatedEditDistance

INPUT_LENGTHS = range(1, 30)
IMPRACTICAL_THRESHOLD = 30
METRICS = ("total_operations", "cells_allocated", "max_recursion_depth")

class CaseB3(Study):
    USE_RANDOM_WORD = False

    def run(self) -> None:
        """
        Compare memo and table on identical inputs across all of: total_operations, Run time (ms), table cells allocated, maximum recursion depth reached for memo.\n
        For memo, cells_allocated counts computed memo entries; for table, it counts
        the full allocated DP table. max_recursion_depth is only applicable to memo.
        """
        result_dir = self.get_results_directory(self.USE_RANDOM_WORD)
        data: list[dict[str, object]] = []
        memo_timed_out = False
        table_timed_out = False

        for length in INPUT_LENGTHS:
            if self.USE_RANDOM_WORD:
                string_a = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)
                string_b = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed + 1)
            else:
                # all one char
                string_a = "a" * length
                string_b = "b" * length

            data_row: dict[str, object] = {
                "length": length,
                "string_a": string_a,
                "string_b": string_b,
            }
            for prefix, algorithm, has_timed_out in (
                ("memo", MemoizedEditDistance, memo_timed_out),
                ("table", TabulatedEditDistance, table_timed_out),
            ):
                status = "skipped" if has_timed_out else "pending"
                elapsed = 0.0
                summary: dict[str, int] | None = None

                if not has_timed_out:
                    status, elapsed, summary, _, _ = self.run_with_timeout(
                        algorithm,
                        string_a,
                        string_b,
                        IMPRACTICAL_THRESHOLD,
                    )

                data_row[f"{prefix}_status"] = status
                data_row[f"{prefix}_run_time_ms"] = (
                    round(elapsed * 1000, 3) if status != "skipped" else ""
                )

                for field in METRICS:
                    data_row[f"{prefix}_{field}"] = (
                        summary[field]
                        if summary is not None
                            and (field != "max_recursion_depth"
                                or prefix == "memo")
                                    else ""
                    )

                if status == "timeout":
                    if prefix == "memo":
                        memo_timed_out = True
                    else:
                        table_timed_out = True

            data.append(data_row)

        csv_fields = ["length", "string_a", "string_b",
                      "memo_status", "memo_run_time_ms",
                      *(f"memo_{field}" for field in METRICS),
                      "table_status", "table_run_time_ms",
                      *(f"table_{field}" for field in METRICS)]

        results_path = result_dir / "b3_results.csv"

        with results_path.open("w", newline="", encoding="utf-8") as results_file:
            writer = csv.DictWriter(results_file, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(data)

        memo_completed_rows = [row for row in data if row["memo_status"] == "completed"]
        table_completed_rows = [row for row in data if row["table_status"] == "completed"]

        graph_specs = (
            (
                "total_operations",
                "B3: Operation counts",
                "Total operations",
                "b3_operation_counts.png",
            ),
            (
                "run_time_ms",
                "B3: Runtime",
                "Runtime (ms)",
                "b3_runtime.png",
            ),
            (
                "cells_allocated",
                "B3: DP cells allocated",
                "Cells allocated",
                "b3_cells_allocated.png",
            ),
        )
        for metric, title, y_label, filename in graph_specs:
            memo_series = Study.build_series(
                "Memoized",
                memo_completed_rows,
                "length",
                f"memo_{metric}",
                "o-",
            )
            table_series = Study.build_series(
                "Tabulated",
                table_completed_rows,
                "length",
                f"table_{metric}",
                "s-",
            )
            figure = self.generate_graph(
                [memo_series, table_series],
                result_dir / filename,
                title=title,
                x_label="Input length (n)",
                y_label=y_label,
                y_scale="log",
                save=False,
            )
            axes = figure.axes[0]
            axes.set_xticks(list(INPUT_LENGTHS))
            axes.tick_params(axis="x", labelrotation=45)
            figure.set_size_inches(14, 6)
            figure.tight_layout()
            figure.savefig(result_dir / filename, dpi=160)
            figure.show()

        recursion_series = Study.build_series(
            "Memoized",
            memo_completed_rows,
            "length",
            "memo_max_recursion_depth",
            "o-",
        )
        _, lengths, depths, _ = recursion_series
        recursion_figure = self.generate_graph(
            [recursion_series],
            result_dir / "b3_memo_recursion_depth.png",
            title="B3: Memoized maximum recursion depth",
            x_label="Input length (n)",
            y_label="Maximum recursion depth",
            save=False,
        )
        recursion_axes = recursion_figure.axes[0]
        recursion_axes.clear()
        positions = list(range(len(lengths)))
        recursion_axes.barh(positions, depths, label="Memoized")
        recursion_axes.set_yticks(
            positions,
            labels=[str(int(length)) for length in lengths],
        )
        recursion_axes.invert_yaxis()
        recursion_axes.xaxis.tick_top()
        recursion_axes.xaxis.set_label_position("top")
        recursion_axes.set_xlabel("Maximum recursion depth")
        recursion_axes.set_ylabel("Input length (n)")
        recursion_axes.set_title("B3: Memoized maximum recursion depth")
        recursion_axes.grid(True, axis="x", alpha=0.3)
        recursion_axes.set_axisbelow(True)
        recursion_axes.legend()
        recursion_figure.set_size_inches(10, 8)
        recursion_figure.tight_layout()
        recursion_figure.savefig(result_dir / "b3_memo_recursion_depth.png", dpi=160)
        recursion_figure.show()

        # Run naive and memoized implementations, collect results, plot them.
        print(f"Results and graphs saved under {result_dir}.")


def main() -> None:
    CaseB3().run()

if __name__ == "__main__":
    main()