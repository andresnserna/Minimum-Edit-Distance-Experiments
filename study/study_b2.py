# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B2

# Tabulation Asymptotic Complexity

# Run A3 on strings of growing length n, using |A| = |B| = n. Test the following values of n
# [10,20,40,80,160,320,640,1280]. Fill in a table with the following headers: 
# [n, total_ops, ratio, run time (ms), ratio]. 

# Plot total_operations against n on log-log axes. Do the same for run time 
# (separate graphs of course). When does the ratio between consecutive points stabilize (if it does)?
from __future__ import annotations
import csv
from study.study import Study
from edit_distance.table import TabulatedEditDistance

INPUT_LENGTHS = [10, 20, 40, 80, 160, 320, 640, 1280]
# INPUT_LENGTHS = [160, 320, 640, 1280, 2560, 5120, 10240, 20480]
IMPRACTICAL_THRESHOLD = 30
COUNTER_FIELDS = ("reads", "writes", "comparisons", "calls", "total_operations")

class CaseB2(Study):
    USE_RANDOM_WORD = True

    def run(self) -> None:
      """
      Run table on strings of growing length n, (|A| = |B| = n). Test the following values of n [10,20,40,80,160,320,640,1280]. Plot total_operations against n on log-log axes.
      Saves a CSV results table and comparison plots under study/results.
      """
      result_dir = self.get_results_directory(self.USE_RANDOM_WORD)
      data: list[dict[str, object]] = []   
      thread_timed_out = False
 

      for length in INPUT_LENGTHS:
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
            "status": "skipped" if thread_timed_out else "pending",
            "time_ms": "",
            "distance": "",
         }
         for field in COUNTER_FIELDS:
            data_row[f"table_{field}"] = ""

         if not thread_timed_out:
            status, elapsed, summary, distance, _ = self.run_with_timeout(
               TabulatedEditDistance, string_a, string_b, IMPRACTICAL_THRESHOLD
            )
            data_row["status"] = status
            data_row["time_ms"] = round(elapsed * 1000, 3)
            if summary is not None:
               data_row["distance"] = distance
               for field in COUNTER_FIELDS:
                  data_row[f"table_{field}"] = summary[field]
            else:
               thread_timed_out = True

         data.append(data_row)

      fields = [
         "length", "string_a", "string_b",
         "status", "time_ms", "distance",
         *(f"table_{field}" for field in COUNTER_FIELDS),
      ]

      results_path = result_dir / "b2_results.csv"
      with results_path.open("w", newline="", encoding="utf-8") as results_file:
         writer = csv.DictWriter(results_file, fieldnames=fields)
         writer.writeheader()
         writer.writerows(data)

      completed_rows = [row for row in data if row["status"] == "completed"]

      operation_count_series = Study.build_series(
         "Tabulated",
         completed_rows,
         "length",
         "table_total_operations",
         "o-",
      )
      operation_count_graph = self.generate_graph(
         [operation_count_series],
         result_dir / "b2_operation_counts.png",
         title="B2: Operation counts",
         x_label="Input length (n)",
         y_label="Total operations",
         x_scale="log",
         y_scale="log",
      )
      operation_count_graph.show()

      runtime_series = Study.build_series(
         "Tabulated",
         completed_rows,
         "length",
         "time_ms",
         "o-",
      )
      runtime_graph = self.generate_graph(
         [runtime_series],
         result_dir / "b2_runtime.png",
         title="B2: Runtime",
         x_label="Input length (n)",
         y_label="Runtime (ms)",
         x_scale="log",
         y_scale="log",
      )
      runtime_graph.show()


      timeout_rows = [row for row in data if row["status"] == "timeout"]
      if timeout_rows:
         timeout_length = timeout_rows[0]["length"]
         print(
            f"Tabulated first exceeded the {IMPRACTICAL_THRESHOLD}-second "
            f"limit at length {timeout_length}."
         )
         print("Later tabulated cases were skipped.")
      else:
         print(f"No tabulated input exceeded the {IMPRACTICAL_THRESHOLD}-second limit.")
      print(f"Results saved under {result_dir}.")

def main() -> None:
    CaseB2().run()

if __name__ == "__main__":
    main()