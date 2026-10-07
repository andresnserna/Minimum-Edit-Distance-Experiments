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
import multiprocessing
import time
from multiprocessing.connection import Connection
from pathlib import Path
from study.study import Study
from edit_distance.table import TabulatedEditDistance

INPUT_LENGTHS = [10, 20, 40, 80, 160, 320, 640, 1280]
# INPUT_LENGTHS = [10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120, 10240]
IMPRACTICAL_THRESHOLD = 30
COUNTER_FIELDS = ("reads", "writes", "comparisons", "calls", "total_operations")

def _run_thread_worker(connection: Connection, string_a: str, string_b: str) -> None:
   connection.send(("started",))
   started_at = time.perf_counter()
   try:
      result = TabulatedEditDistance(string_a, string_b).compute()
      connection.send(("completed", time.perf_counter() - started_at, result.counters_summary, result.distance))
   except Exception as error:
      connection.send(("error", repr(error)))
   finally:
      connection.close()

def _run_b2_with_timeout(
   string_a: str,
   string_b: str,
   timeout_seconds: float,
) -> tuple[str, float, dict[str, int] | None, int | None]:
   context = multiprocessing.get_context("spawn")
   parent_connection, child_connection = context.Pipe(duplex=False)
   process = context.Process(
      target=_run_thread_worker,
      args=(child_connection, string_a, string_b),
   )
   process.start()
   child_connection.close()

   try:
      while not parent_connection.poll(0.1):
         if not process.is_alive():
            raise RuntimeError("Thread worker exited before starting the computation.")

      start_message = parent_connection.recv()
      if start_message[0] != "started":
         raise RuntimeError(f"Unexpected message from thread worker: {start_message!r}")

      deadline = time.perf_counter() + timeout_seconds
      remaining = deadline - time.perf_counter()
      if remaining <= 0 or not parent_connection.poll(remaining):
         process.terminate()
         process.join()
         return "timeout", timeout_seconds, None, None

      message = parent_connection.recv()
      process.join()
      if message[0] == "error":
         raise RuntimeError(f"Thread worker failed: {message[1]}")
      if message[0] != "completed":
         raise RuntimeError(f"Unexpected message from Thread worker: {message!r}")
      return "completed", message[1], message[2], message[3]
   finally:
      parent_connection.close()
      if process.is_alive():
         process.terminate()
         process.join()
      process.close()

class CaseB2(Study):
    def run(self) -> None:
      """
      Run table on strings of growing length n, (|A| = |B| = n). Test the following values of n [10,20,40,80,160,320,640,1280]. Plot total_operations against n on log-log axes.
      Saves a CSV results table and comparison plots under study/results.
      """
      result_dir = Path(__file__).parent / "results"
      result_dir.mkdir(parents=True, exist_ok=True)
      data: list[dict[str, object]] = []   
      thread_timed_out = False
 

      for length in INPUT_LENGTHS:
         # all one char
         # string_a = "a" * length
         # string_b = "b" * length
         
         # random chars
         string_a = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)
         string_b = Study.rand_word(Study.eng_alphabet_low, length, seed=Study.default_seed)

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
            status, elapsed, summary, distance = _run_b2_with_timeout(
               string_a, string_b, IMPRACTICAL_THRESHOLD
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