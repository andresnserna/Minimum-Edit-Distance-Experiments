# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B5

# Edge Case Analysis

# Generate random string pairs of fixed length n over alphabets of at least three different sizes —
# for example 2, 4, and 26 — holding n constant. Report total_operations for A3 on each,
# and answer the following question: “Does the runtime of the tabular edit distance algorithm have
# an asymptotically different best and worst case scenario?”

# Input data
# Draw on at least two of: English word pairs, short DNA sequences, and randomly generated
# strings over a controlled alphabet. Whenever you use random strings, state the alphabet size.

from __future__ import annotations
import csv
from study.study import Study
from edit_distance.table import TabulatedEditDistance

ALPHABET_SIZES = [10, 26, 95]
DNA_ALPHABET = ["A", "C", "G", "T"]
LENGTH_N  = 10
IMPRACTICAL_THRESHOLD = 30
OPERATION_FIELDS = ("substitutions", "insertions", "deletions", "matches")
OPERATION_CODES = ("S", "I", "D", ".")
OPERATION_LABELS = ("Substitutions", "Insertions", "Deletions", "Matches")
METRICS = ("total_operations",)


class CaseB5(Study):
   USE_RANDOM_WORD = True

   def run(self) -> None:
      """
      Generate random string pairs of fixed length n over alphabets of at least three different sizes (for example 2, 4, and 26) holding n constant. Reports total_operations for A3 on each
      """
      result_dir = self.get_results_directory(self.USE_RANDOM_WORD)
      data: list[dict[str, object]] = []
      thread_timed_out = False

      # EDGE CASE ANALYSIS 1 - random strings
      for alphabet_size in ALPHABET_SIZES:
         alphabet = Study.rand_alphabet(alphabet_size, seed=Study.default_seed)
         string_a = Study.rand_word(alphabet, LENGTH_N, seed=Study.default_seed + 1)
         string_b = Study.rand_word(alphabet, LENGTH_N, seed=Study.default_seed + 2)

         data_row: dict[str, object] = {
            "input_type": "random_alphabet",
            "alphabet_size": alphabet_size,
            "length": LENGTH_N,
            "string_a": string_a,
            "string_b": string_b,
            "status": "skipped" if thread_timed_out else "pending",
            "run_time_ms": "",
            "distance": "",
            **{f"table_{field}": "" for field in OPERATION_FIELDS},
         }

         if not thread_timed_out:
            status, elapsed, summary, distance, edit_script = self.run_with_timeout(
               TabulatedEditDistance,
               string_a,
               string_b,
               IMPRACTICAL_THRESHOLD,
            )
            data_row["status"] = status
            data_row["run_time_ms"] = round(elapsed * 1000, 3)

            if summary is not None:
               if edit_script is None:
                  raise RuntimeError("Completed B5 run did not return an edit script.")
               data_row["distance"] = distance
               for field in METRICS:
                  data_row[f"table_{field}"] = summary[field]
               for field, operation in zip(OPERATION_FIELDS, OPERATION_CODES):
                  data_row[f"table_{field}"] = edit_script.count(operation)
            else:
               thread_timed_out = True

         data.append(data_row)


      # EDGE CASE ANALYSIS 2 - DNA sequences
      for pair_index in range(3):  # Generate three random DNA sequence pairs
         string_a = Study.rand_word(DNA_ALPHABET, LENGTH_N, seed=Study.default_seed + 3 + 2 * pair_index)
         string_b = Study.rand_word(DNA_ALPHABET, LENGTH_N, seed=Study.default_seed + 4 + 2 * pair_index)

         data_row: dict[str, object] = {
            "input_type": "dna",
            "alphabet_size": len(DNA_ALPHABET),
            "length": LENGTH_N,
            "string_a": string_a,
            "string_b": string_b,
            "status": "skipped" if thread_timed_out else "pending",
            "run_time_ms": "",
            "distance": "",
            **{f"table_{field}": "" for field in OPERATION_FIELDS},
         }

         if not thread_timed_out:
            status, elapsed, summary, distance, edit_script = self.run_with_timeout(
               TabulatedEditDistance,
               string_a,
               string_b,
               IMPRACTICAL_THRESHOLD,
            )
            data_row["status"] = status
            data_row["run_time_ms"] = round(elapsed * 1000, 3)

            if summary is not None:
               if edit_script is None:
                  raise RuntimeError("Completed B5 run did not return an edit script.")
               data_row["distance"] = distance
               for field in METRICS:
                  data_row[f"table_{field}"] = summary[field]
               for field, operation in zip(OPERATION_FIELDS, OPERATION_CODES):
                  data_row[f"table_{field}"] = edit_script.count(operation)
            else:
               thread_timed_out = True

         data.append(data_row)

      fields = [
         "input_type",
         "alphabet_size",
         "length",
         "string_a",
         "string_b",
         "status",
         "run_time_ms",
         "distance",
         *(f"table_{field}" for field in OPERATION_FIELDS),
         *(f"table_{field}" for field in METRICS),
      ]

      results_path = result_dir / "b5_results.csv"
      with results_path.open("w", newline="", encoding="utf-8") as results_file:
         writer = csv.DictWriter(results_file, fieldnames=fields)
         writer.writeheader()
         writer.writerows(data)

      graphing_data = {
         (str(row["input_type"]), int(row["alphabet_size"])): row
         for row in data
         if row["status"] == "completed"
      }
      self.__result_dir = result_dir
      self.__graphing_data = graphing_data

      # Graph of alphabet 1: x = operation, y = count of that operation.
      self.__save_operation_graph("random_alphabet", ALPHABET_SIZES[0])

      # Graph of alphabet 2: x = operation, y = count of that operation.
      self.__save_operation_graph("random_alphabet", ALPHABET_SIZES[1])

      # Graph of alphabet 3: x = operation, y = count of that operation.
      self.__save_operation_graph("random_alphabet", ALPHABET_SIZES[2])

      # Graph of DNA sequence: x = operation, y = count of that operation.
      self.__save_operation_graph("dna", len(DNA_ALPHABET))

      # Graph of runtime: x = alphabet size, y = runtime (ms).
      completed_random_rows = [
         row
         for row in data
         if row["input_type"] == "random_alphabet" and row["status"] == "completed"
      ]
      if not completed_random_rows:
         raise RuntimeError("Cannot plot B5 runtime: no random-alphabet run completed.")
      runtime_series = Study.build_series(
         "Tabulated",
         completed_random_rows,
         "alphabet_size",
         "run_time_ms",
         "o-",
      )
      runtime_figure = self.generate_graph(
         [runtime_series],
         result_dir / "b5_runtime_by_alphabet_size.png",
         title="B5: Runtime by alphabet size",
         x_label="Alphabet size",
         y_label="Runtime (ms)",
      )
      runtime_figure.show()

   def __save_operation_graph(self, input_type: str, alphabet_size: int) -> None:
      row = self.__graphing_data.get((input_type, alphabet_size))
      if row is None:
         raise RuntimeError(
            f"Cannot plot B5 operation counts: no completed {input_type!r} "
            f"result for alphabet size {alphabet_size}."
         )
      operation_rows = [
         {"operation_index": index, "operation_count": row[f"table_{field}"]}
         for index, field in enumerate(OPERATION_FIELDS)
      ]
      series = Study.build_series(
         "Tabulated",
         operation_rows,
         "operation_index",
         "operation_count",
         "o-",
      )
      graph_name = (
         f"b5_alphabet_{alphabet_size}_operations.png"
         if input_type == "random_alphabet"
         else "b5_dna_operations.png"
      )
      graph_title = (
         f"B5: Edit operations (alphabet size {alphabet_size})"
         if input_type == "random_alphabet"
         else f"B5: Edit operations ({input_type.upper()}, alphabet size {alphabet_size})"
      )
      figure = self.generate_graph(
         [series],
         self.__result_dir / graph_name,
         title=graph_title,
         x_label="Edit operation",
         y_label="Operation count",
         chart_type="bar",
         x_tick_labels=OPERATION_LABELS,
      )
      figure.show()

def main() -> None:
    CaseB5().run()

if __name__ == "__main__":
    main()