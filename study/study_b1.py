# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B1

# When does Naive become unusable?

# Run A1 (naive) against A2 (memo) on inputs of increasing length. Capture both operation counts and run time.
# Find and report the input size at which the naive version becomes impractical on your machine 
# — define "impractical" yourself and state your threshold (e.g. >60 seconds). Plot both
# implementations on shared axes.

# Report calls for both.

from __future__ import annotations
import csv
import time
from study.study import Study
from edit_distance.naive import NaiveEditDistance
from edit_distance.memo import MemoizedEditDistance

INPUT_LENGTHS = range(1, 21)
IMPRACTICAL_THRESHOLD = 30
COUNTER_FIELDS = ("reads", "writes", "comparisons", "calls", "total_operations")

class CaseB1(Study):
   USE_RANDOM_WORD = True

   def run(self) -> None:
      """
      Run naive and memoized implementations, collect results, plot them.
      Saves a CSV results table and comparison plots under study/results.
      """
      result_dir = self.get_results_directory(self.USE_RANDOM_WORD)
      data: list[dict[str, object]] = []
      thread_timed_out = False

      # setup the thread run
      for length in INPUT_LENGTHS:
         # all one char
         # string_a = "a" * length
         # string_b = "b" * length

         # random chars
         # string_a = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)
         # string_b = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed + 1)
         if self.USE_RANDOM_WORD:
            string_a = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)
            string_b = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed + 1)
         else:
            string_a = "a" * length
            string_b = "b" * length
         
         data_row: dict[str, object] = {
            "length": length,
            "string_a": string_a,
            "string_b": string_b,
            "naive_status": "skipped" if thread_timed_out else "pending",
            "naive_time_ms": "",
            "naive_distance": "",
            "memo_status": "pending",
            "memo_time_ms": "",
            "memo_distance": "",
         }
         for field in COUNTER_FIELDS:
            data_row[f"naive_{field}"] = ""
            data_row[f"memo_{field}"] = ""

         if not thread_timed_out:
            status, elapsed, summary, distance, _ = self.run_with_timeout(
               NaiveEditDistance, string_a, string_b, IMPRACTICAL_THRESHOLD
            )

            data_row["naive_status"] = status
            data_row["naive_time_ms"] = round(elapsed * 1000, 3)

            if summary is not None:
               data_row["naive_distance"] = distance
               for field in COUNTER_FIELDS:
                  data_row[f"naive_{field}"] = summary[field]
            else:
               thread_timed_out = True

         memo_started = time.perf_counter()
         memo_result = MemoizedEditDistance(string_a, string_b).compute()
         memo_elapsed = time.perf_counter() - memo_started
         data_row["memo_status"] = "completed"
         data_row["memo_time_ms"] = round(memo_elapsed * 1000, 3)
         data_row["memo_distance"] = memo_result.distance

         for field in COUNTER_FIELDS:
            data_row[f"memo_{field}"] = memo_result.counters_summary[field]
         data.append(data_row)

      fields = [
         "length", "string_a", "string_b",
         "naive_status", "naive_time_ms", "naive_distance",
         *(f"naive_{field}" for field in COUNTER_FIELDS),
         "memo_status", "memo_time_ms", "memo_distance",
         *(f"memo_{field}" for field in COUNTER_FIELDS),
      ]
      
      results_path = result_dir / "b1_results.csv"

      with results_path.open("w", newline="", encoding="utf-8") as results_file:
         writer = csv.DictWriter(results_file, fieldnames=fields)
         writer.writeheader()
         writer.writerows(data)

      completed_naive = [row for row in data if row["naive_status"] == "completed"]
      naive_timeout_rows = [row for row in data if row["naive_status"] == "timeout"]

      naive_operation_series = Study.build_series(
         "Naive",
         completed_naive,
         "length",
         "naive_total_operations",
         "o-",
      )
      memoized_operation_series = Study.build_series(
         "Memoized",
         data,
         "length",
         "memo_total_operations",
         "o-",
      )
      operation_count_series = [naive_operation_series, memoized_operation_series]

      operation_count_graph = self.generate_graph(
         operation_count_series,
         result_dir / "b1_operation_counts.png",
         title="B1: Operation counts",
         x_label="Input length (each string)",
         y_label="Total operations",
      )
      operation_count_graph.show()

      naive_runtime_series = Study.build_series(
         "Naive",
         completed_naive,
         "length",
         "naive_time_ms",
         "o-",
      )
      naive_timeout_series = Study.build_series(
         "Naive timed out",
         naive_timeout_rows,
         "length",
         "naive_time_ms",
         "x",
      )
      memoized_runtime_series = Study.build_series(
         "Memoized",
         data,
         "length",
         "memo_time_ms",
         "o-",
      )
      runtime_series = [
         naive_runtime_series,
         naive_timeout_series,
         memoized_runtime_series,
      ]

      runtime_graph = self.generate_graph(
         runtime_series,
         result_dir / "b1_runtime.png",
         title="B1: Runtime",
         x_label="Input length (each string)",
         y_label="Runtime (ms)",
         y_limits=(0, IMPRACTICAL_THRESHOLD * 1000 * 1.05) if naive_timeout_rows else None,
         reference_line=(
            (IMPRACTICAL_THRESHOLD * 1000, "30-second cutoff")
            if naive_timeout_rows
            else None
         ),
      )
      runtime_graph.show()

      if naive_timeout_rows:
         timeout_length = naive_timeout_rows[0]["length"]
         print(f"Naive first exceeded the {IMPRACTICAL_THRESHOLD}-second limit at length {timeout_length}.")
         print("Later naive cases were skipped; memoized cases continued.")
      else:
         print(f"No naive input exceeded the {IMPRACTICAL_THRESHOLD}-second limit.")
      print(f"Results saved under {result_dir}.")

def main() -> None:
   CaseB1().run()

if __name__ == "__main__":
   main()