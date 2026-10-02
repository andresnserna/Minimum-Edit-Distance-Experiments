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
import multiprocessing
import time
from multiprocessing.connection import Connection
from pathlib import Path
from study.study import Study
from edit_distance.naive import NaiveEditDistance
from edit_distance.memo import MemoizedEditDistance

INPUT_LENGTHS = range(1, 21)
IMPRACTICAL_THRESHOLD = 30
COUNTER_FIELDS = ("reads", "writes", "comparisons", "calls", "total_operations")

def _run_naive_worker(connection: Connection, string_a: str, string_b: str) -> None:
   connection.send(("started",))
   started_at = time.perf_counter()
   try:
      result = NaiveEditDistance(string_a, string_b).compute()
      connection.send(("completed", time.perf_counter() - started_at,
                   result.counters_summary, result.distance))
   except Exception as error:
      connection.send(("error", repr(error)))
   finally:
      connection.close()


def _run_naive_with_timeout(
   string_a: str,
   string_b: str,
   timeout_seconds: float,
) -> tuple[str, float, dict[str, int] | None, int | None]:
   context = multiprocessing.get_context("spawn")
   parent_connection, child_connection = context.Pipe(duplex=False)
   process = context.Process(
      target=_run_naive_worker,
      args=(child_connection, string_a, string_b),
   )
   process.start()
   child_connection.close()

   try:
      while not parent_connection.poll(0.1):
         if not process.is_alive():
            raise RuntimeError("Naive worker exited before starting the computation.")

      start_message = parent_connection.recv()
      if start_message[0] != "started":
         raise RuntimeError(f"Unexpected message from naive worker: {start_message!r}")

      deadline = time.perf_counter() + timeout_seconds
      remaining = deadline - time.perf_counter()
      if remaining <= 0 or not parent_connection.poll(remaining):
         process.terminate()
         process.join()
         return "timeout", timeout_seconds, None, None

      message = parent_connection.recv()
      process.join()
      if message[0] == "error":
         raise RuntimeError(f"Naive worker failed: {message[1]}")
      if message[0] != "completed":
         raise RuntimeError(f"Unexpected message from naive worker: {message!r}")
      return "completed", message[1], message[2], message[3]
   finally:
      parent_connection.close()
      if process.is_alive():
         process.terminate()
         process.join()
      process.close()

class CaseB1(Study):

   def run(self) -> None:
      """
      Run naive and memoized implementations, collect results, plot them.
      Saves a CSV results table and comparison plots under study/results.
      """
      result_dir = Path(__file__).parent / "results"
      result_dir.mkdir(parents=True, exist_ok=True)
      rows: list[dict[str, object]] = []
      naive_timed_out = False

      # setup the thread run
      for length in INPUT_LENGTHS:
         string_a = "a" * length
         string_b = "b" * length
         row: dict[str, object] = {
            "length": length,
            "string_a": string_a,
            "string_b": string_b,
            "naive_status": "skipped" if naive_timed_out else "pending",
            "naive_time_ms": "",
            "naive_distance": "",
            "memo_status": "pending",
            "memo_time_ms": "",
            "memo_distance": "",
         }
         for field in COUNTER_FIELDS:
            row[f"naive_{field}"] = ""
            row[f"memo_{field}"] = ""

         if not naive_timed_out:
            status, elapsed, summary, distance = _run_naive_with_timeout(
               string_a, string_b, IMPRACTICAL_THRESHOLD
            )

            row["naive_status"] = status
            row["naive_time_ms"] = round(elapsed * 1000, 3)

            if summary is not None:
               row["naive_distance"] = distance
               for field in COUNTER_FIELDS:
                  row[f"naive_{field}"] = summary[field]
            else:
               naive_timed_out = True

         memo_started = time.perf_counter()
         memo_result = MemoizedEditDistance(string_a, string_b).compute()
         memo_elapsed = time.perf_counter() - memo_started
         row["memo_status"] = "completed"
         row["memo_time_ms"] = round(memo_elapsed * 1000, 3)
         row["memo_distance"] = memo_result.distance

         for field in COUNTER_FIELDS:
            row[f"memo_{field}"] = memo_result.counters_summary[field]
         rows.append(row)

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
         writer.writerows(rows)

      completed_naive = [row for row in rows if row["naive_status"] == "completed"]
      naive_timeout_rows = [row for row in rows if row["naive_status"] == "timeout"]
      lengths = [row["length"] for row in rows]
      self.generate_graph(
         [
            (
               "Naive",
               [row["length"] for row in completed_naive],
               [row["naive_total_operations"] for row in completed_naive],
               "o-",
            ),
            ("Memoized", lengths, [row["memo_total_operations"] for row in rows], "o-"),
         ],
         result_dir / "b1_operation_counts.png",
         title="B1: Operation counts",
         x_label="Input length (each string)",
         y_label="Total operations",
      )
      self.generate_graph(
         [
            (
               "Naive",
               [row["length"] for row in completed_naive],
               [row["naive_time_ms"] for row in completed_naive],
               "o-",
            ),
            (
               "Naive timed out",
               [row["length"] for row in naive_timeout_rows],
               [row["naive_time_ms"] for row in naive_timeout_rows],
               "x",
            ),
            ("Memoized", lengths, [row["memo_time_ms"] for row in rows], "o-"),
         ],
         result_dir / "b1_runtime.png",
         title="B1: Runtime",
         x_label="Input length (each string)",
         y_label="Runtime (ms)",
         reference_line=(IMPRACTICAL_THRESHOLD * 1000, "30-second cutoff"),
      )

      if naive_timeout_rows:
         timeout_length = naive_timeout_rows[0]["length"]
         print(f"Naive first exceeded the {IMPRACTICAL_THRESHOLD}-second limit at length {timeout_length}.")
         print("Later naive cases were skipped; memoized cases continued.")
      else:
         print(f"No naive input exceeded the {IMPRACTICAL_THRESHOLD}-second limit.")
      print(f"Results and plots saved under {result_dir}.")

def main() -> None:
   CaseB1().run()

if __name__ == "__main__":
   main()