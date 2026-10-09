# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B4

# Cost weights

# Run each of the following cost schemes against the same input set. Report, for each scheme
# and each string pair: the distance, and the composition of the optimal edit script (counts of S, I,
# D, and matches).

# Scheme sub ins del
# S1      1   1   1
# S2      2   1   1
# S3      3   1   1
# S4      1   1   5

# Then answer these three questions in your report.
#    (a) The substitution threshold. Across S1-S3, substitution should go from common to
# completely absent. State the general condition on the three costs under which substitution can
# appear in some optimal script, and prove it in a short paragraph. This should be a succinct
# argument, not a research paper

#    (b) The LCS identity. Under S3, verify that for every pair in your data,
# distance(A, B) = |A| + |B| − 2 · LCS(A, B)
# Computer LCS using our code from September 17th. Explain why this identity holds when
# substitution is dominated and fails when it is not.

#    (c) Symmetry. Under S4, find a concrete pair where distance(A, B) ≠ distance(B, A).
# Explain why. Then state the condition on the costs under which edit distance is symmetric.

# Methodology requirements

# Your report must state: machine (CPU, RAM, OS), programming language and version,
# repetitions per data point and how you aggregated them (mean, median, maximum and
# minimum, etc), whether warm-up runs were discarded, and how input strings were generated.


from __future__ import annotations
import csv
from study.study import Study
from edit_distance.memo import MemoizedEditDistance
from edit_distance.table import TabulatedEditDistance
from edit_distance.naive import NaiveEditDistance

SCHEMES = {
   "S1": {"sub": 1, "ins": 1, "del": 1},
   "S2": {"sub": 2, "ins": 1, "del": 1},
   "S3": {"sub": 3, "ins": 1, "del": 1},
   "S4": {"sub": 1, "ins": 1, "del": 5},
}
METRICS = (
   "distance",
   "run_time_ms",
   "substitutions",
   "insertions",
   "deletions",
   "matches",
   "edit_script",
)
SCRIPT_METRICS = {
   "S": "substitutions",
   "I": "insertions",
   "D": "deletions",
   ".": "matches",
}
ALGORITHMS = (
   ("naive", NaiveEditDistance),
   ("memo", MemoizedEditDistance),
   ("table", TabulatedEditDistance),
)
INPUT_LENGTHS = range(1, 30)
IMPRACTICAL_THRESHOLD = 30

class CaseB4(Study):
   USE_RANDOM_WORD = True

   def run(self) -> None:
      """
      Run each cost scheme against the same input set and record distance and edit-script composition.
      Report for each scheme and each string pair: the distance, and the composition of the optimal edit
      script (counts of S, I, D, and matches)\n

      Saves one CSV results table per cost scheme under study/results.
      """
      result_root = self.get_results_directory(self.USE_RANDOM_WORD)
      data_by_scheme: dict[str, list[dict[str, object]]] = {}

      for scheme_name, scheme_costs in SCHEMES.items():
         result_dir = self.get_results_directory(self.USE_RANDOM_WORD, scheme_name)
         scheme_data: list[dict[str, object]] = []
         timed_out = {name: False for name, _ in ALGORITHMS}

         for pair_index, length in enumerate(INPUT_LENGTHS, start=1):
            if self.USE_RANDOM_WORD:
               string_a = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)
               string_b = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed + 1)
            else:
               string_a = "a" * length
               string_b = "b" * length

            data_row: dict[str, object] = {
               "scheme": scheme_name,
               "sub_cost": scheme_costs["sub"],
               "ins_cost": scheme_costs["ins"],
               "del_cost": scheme_costs["del"],
               "pair_index": pair_index,
               "length": length,
               "string_a": string_a,
               "string_b": string_b,
            }

            for prefix, algorithm in ALGORITHMS:
               status = "skipped" if timed_out[prefix] else "pending"
               elapsed = 0.0
               distance: int | None = None
               edit_script: list[str] | None = None

               if not timed_out[prefix]:
                  status, elapsed, _, distance, edit_script = self.run_with_timeout(
                     algorithm,
                     string_a,
                     string_b,
                     IMPRACTICAL_THRESHOLD,
                     cost_scheme=scheme_costs,
                  )

               data_row[f"{prefix}_status"] = status
               data_row[f"{prefix}_run_time_ms"] = (
                  round(elapsed * 1000, 3) if status != "skipped" else ""
               )
               data_row[f"{prefix}_distance"] = distance if distance is not None else ""

               if edit_script is None:
                  for metric in SCRIPT_METRICS.values():
                     data_row[f"{prefix}_{metric}"] = ""
                  data_row[f"{prefix}_edit_script"] = ""
               else:
                  for operation, metric in SCRIPT_METRICS.items():
                     data_row[f"{prefix}_{metric}"] = edit_script.count(operation)
                  data_row[f"{prefix}_edit_script"] = " ".join(edit_script)

               if status == "timeout":
                  timed_out[prefix] = True

            scheme_data.append(data_row)

         data_by_scheme[scheme_name] = scheme_data
         csv_fields = [
            "scheme", "sub_cost", "ins_cost", "del_cost",
            "pair_index", "length", "string_a", "string_b",
            *(
               column
               for prefix, _ in ALGORITHMS
                  for column in (
                     f"{prefix}_status",
                     *(f"{prefix}_{field}" for field in METRICS),
                  )
            ),
         ]

         results_path = result_dir / f"b4_{scheme_name}_results.csv"
         with results_path.open("w", newline="", encoding="utf-8") as results_file:
            writer = csv.DictWriter(results_file, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(data_by_scheme[scheme_name])

         ## graph S1: x = operation (sub, ins, del, match) with the 3 algorithms as bars inside, y = count of operation
         ## graph S2: x = operation (sub, ins, del, match) with the 3 algorithms as bars inside, y = count of operation
         ## graph S3: x = operation (sub, ins, del, match) with the 3 algorithms as bars inside, y = count of operation
         ## graph S4: x = operation (sub, ins, del, match) with the 3 algorithms as bars inside, y = count of operation
         operation_names = ("substitutions", "insertions", "deletions", "matches")
         operation_labels = ("Substitutions", "Insertions", "Deletions", "Matches")
         # Aggregate operation counts across completed pairs for the operation-category chart.
         operation_totals = {
            prefix: [
               sum(
                  int(row[f"{prefix}_{operation}"])
                  for row in scheme_data
                  if row[f"{prefix}_status"] == "completed"
               )
               for operation in operation_names
            ]
            for prefix, _ in ALGORITHMS
         }

         operation_rows = [
            {
               "operation_index": operation_index,
               "operation_label": operation_label,
               **{
                  prefix: operation_totals[prefix][operation_index]
                  for prefix, _ in ALGORITHMS
               },
            }
            for operation_index, operation_label in enumerate(operation_labels)
         ]
         operation_series = [
            Study.build_series(
               prefix.capitalize(),
               operation_rows,
               "operation_index",
               prefix,
               "o-",
            )
            for prefix, _ in ALGORITHMS
         ]
         operation_figure = self.generate_graph(
            operation_series,
            result_dir / f"b4_{scheme_name}_operations.png",
            title=f"{scheme_name}: Edit-script composition",
            x_label="Edit operation",
            y_label="Total operation count",
            chart_type="bar",
            x_tick_labels=operation_labels,
         )
         operation_figure.show()

         ## distance graph: x = string pairs (just use their indices), y = edit distance for the 3 algorithms
         distance_series = []
         for prefix, _ in ALGORITHMS:
            completed_rows = [
               row for row in scheme_data
               if row[f"{prefix}_status"] == "completed"
            ]
            distance_series.append(
               Study.build_series(
                  prefix.capitalize(),
                  completed_rows,
                  "pair_index",
                  f"{prefix}_distance",
                  "o-",
               )
            )

         distance_figure = self.generate_graph(
            distance_series,
            result_dir / f"b4_{scheme_name}_distances.png",
            title=f"{scheme_name}: Edit distance by input pair",
            x_label="Input-pair index",
            y_label="Edit distance",
         )
         distance_figure.show()

      print(f"B4 results saved under {result_root}.")

def main() -> None:
    CaseB4().run()

if __name__ == "__main__":
    main()