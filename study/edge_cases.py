# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

## Empirical Study B5

# Edge Case Analysis

# Generate random string pairs of varied lengths over alphabets of at least three different sizes.
# Report the A3 edit-operation counts at each length,
# and answer the following question: “Does the runtime of the tabular edit distance algorithm have
# an asymptotically different best and worst case scenario?”

# Input data
# Draw on at least two of: English word pairs, short DNA sequences, and randomly generated
# strings over a controlled alphabet. Whenever you use random strings, state the alphabet size.

from __future__ import annotations
import csv
from pathlib import Path
from edit_distance.io import InputParser
from study.study import Study
from edit_distance.table import TabulatedEditDistance

ALPHABET_SIZES = [10, 26, 95]
DNA_ALPHABET = ["A", "C", "G", "T"]
LENGTHS = [10, 50, 100, 200, 300, 400, 500, 1000, 2000]
IMPRACTICAL_THRESHOLD = 30
OPERATION_FIELDS = ("substitutions", "insertions", "deletions", "matches")
OPERATION_CODES = ("S", "I", "D", ".")
OPERATION_LABELS = ("Substitutions", "Insertions", "Deletions", "Matches")
METRICS = ("total_operations",)


class CaseB5(Study):
   USE_RANDOM_WORD = True

   def run(
      self,
      input_path: str | None = None,
      results_dir: Path | None = None,
   ) -> None:
      """
      Measure edit-operation counts across input lengths and alphabet sizes.
      """
      result_dir = self.get_results_directory(
         self.USE_RANDOM_WORD, results_root=results_dir
      )
      data: list[dict[str, object]] = []
      timed_out_groups: set[tuple[str, int]] = set()

      if input_path is not None:
         for string_a, string_b in InputParser.load_study_pairs(input_path):
            alphabet_size = len(set(string_a + string_b))
            group = ("study_input", alphabet_size)
            data.append(
               self.__run_case(
                  "study_input",
                  alphabet_size,
                  max(len(string_a), len(string_b)),
                  string_a,
                  string_b,
                  group in timed_out_groups,
               )
            )
            if data[-1]["status"] == "timeout":
               timed_out_groups.add(group)
      else:
         for length in LENGTHS:
            for alphabet_size in ALPHABET_SIZES:
               group = ("random_alphabet", alphabet_size)
               alphabet = Study.rand_alphabet(
                  alphabet_size, seed=Study.default_seed
               )
               seed_offset = alphabet_size * 2
               string_a = Study.rand_word(
                  alphabet, length, seed=Study.default_seed + seed_offset + 1
               )
               string_b = Study.rand_word(
                  alphabet, length, seed=Study.default_seed + seed_offset + 2
               )
               data.append(
                  self.__run_case(
                     "random_alphabet",
                     alphabet_size,
                     length,
                     string_a,
                     string_b,
                     group in timed_out_groups,
                  )
               )
               if data[-1]["status"] == "timeout":
                  timed_out_groups.add(group)

            dna_group = ("dna", len(DNA_ALPHABET))
            string_a = Study.rand_word(
               DNA_ALPHABET, length, seed=Study.default_seed + 2 * length + 1
            )
            string_b = Study.rand_word(
               DNA_ALPHABET, length, seed=Study.default_seed + 2 * length + 2
            )
            data.append(
               self.__run_case(
                  "dna",
                  len(DNA_ALPHABET),
                  length,
                  string_a,
                  string_b,
                  dna_group in timed_out_groups,
               )
            )
            if data[-1]["status"] == "timeout":
               timed_out_groups.add(dna_group)

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

      self.__result_dir = result_dir
      if input_path is not None:
         observed_alphabet_sizes = sorted(
            {int(row["alphabet_size"]) for row in data}
         )
         for alphabet_size in observed_alphabet_sizes:
            self.__save_operation_graph(
               data,
               "study_input",
               alphabet_size,
               f"b5_input_alphabet_{alphabet_size}_operations.png",
            )
      else:
         observed_alphabet_sizes = ALPHABET_SIZES
         for alphabet_size in ALPHABET_SIZES:
            self.__save_operation_graph(
               data,
               "random_alphabet",
               alphabet_size,
               f"b5_alphabet_{alphabet_size}_operations.png",
            )
         self.__save_operation_graph(
            data, "dna", len(DNA_ALPHABET), "b5_dna_operations.png"
         )

      random_rows = [
         row
         for row in data
         if row["input_type"]
         in ({"study_input"} if input_path is not None else {"random_alphabet"})
         and row["status"] == "completed"
      ]
      if random_rows:
         styles = ("o-", "s-", "^-", "D-", "v-", "P-")
         runtime_series = [
            Study.build_series(
               (
                  f"Observed alphabet size {alphabet_size}"
                  if input_path is not None
                  else f"Alphabet size {alphabet_size}"
               ),
               [
                  row
                  for row in random_rows
                  if row["alphabet_size"] == alphabet_size
               ],
               "length",
               "run_time_ms",
               styles[index % len(styles)],
            )
            for index, alphabet_size in enumerate(observed_alphabet_sizes)
            if any(row["alphabet_size"] == alphabet_size for row in random_rows)
         ]
         runtime_figure = self.generate_graph(
            runtime_series,
            result_dir / "b5_runtime_by_alphabet_size.png",
            title="B5: Runtime by input length",
            x_label="Input length",
            y_label="Runtime (ms)",
         )
         runtime_figure.show()

      for group in sorted(timed_out_groups):
         print(
            f"B5 {group[0]} alphabet size {group[1]} exceeded the "
            f"{IMPRACTICAL_THRESHOLD}-second limit; later lengths were skipped."
         )
      print(f"Results saved under {result_dir}.")

   def __run_case(
      self,
      input_type: str,
      alphabet_size: int,
      length: int,
      string_a: str,
      string_b: str,
      has_timed_out: bool,
   ) -> dict[str, object]:
      data_row: dict[str, object] = {
         "input_type": input_type,
         "alphabet_size": alphabet_size,
         "length": length,
         "string_a": string_a,
         "string_b": string_b,
         "status": "skipped" if has_timed_out else "pending",
         "run_time_ms": "",
         "distance": "",
         **{f"table_{field}": "" for field in OPERATION_FIELDS},
         **{f"table_{field}": "" for field in METRICS},
      }

      if not has_timed_out:
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
      return data_row

   def __save_operation_graph(
      self,
      data: list[dict[str, object]],
      input_type: str,
      alphabet_size: int,
      graph_name: str,
   ) -> None:
      completed_rows = [
         row
         for row in data
         if row["input_type"] == input_type
         and row["alphabet_size"] == alphabet_size
         and row["status"] == "completed"
      ]
      if not completed_rows:
         print(
            f"Skipping {graph_name}: no completed {input_type!r} "
            f"runs for alphabet size {alphabet_size}."
         )
         return

      styles = ("o-", "s-", "^-", "D-")
      series = [
         Study.build_series(
            label,
            completed_rows,
            "length",
            f"table_{field}",
            style,
         )
         for label, field, style in zip(
            OPERATION_LABELS, OPERATION_FIELDS, styles
         )
      ]
      graph_title = (
         f"B5: Edit operations (alphabet size {alphabet_size})"
         if input_type == "random_alphabet"
         else f"B5: Edit operations ({input_type.upper()}, alphabet size {alphabet_size})"
      )
      figure = self.generate_graph(
         series,
         self.__result_dir / graph_name,
         title=graph_title,
         x_label="Input length",
         y_label="Operation count",
      )
      figure.show()

def main() -> None:
    CaseB5().run()

if __name__ == "__main__":
    main()