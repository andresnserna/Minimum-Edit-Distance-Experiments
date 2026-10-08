# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

from __future__ import annotations
from collections.abc import Mapping, Sequence
import multiprocessing
from numbers import Real
import re
import time
from multiprocessing.connection import Connection
from typing import List, Literal
import random
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from edit_distance.base import EditDistanceEngine


def _run_worker(
   connection: Connection,
   algorithm: type[EditDistanceEngine],
   string_a: str,
   string_b: str,
   costs: Mapping[str, int],
) -> None:
   connection.send(("started",))
   started_at = time.perf_counter()
   try:
      result = algorithm(
         string_a,
         string_b,
         sub_cost=costs["sub"],
         ins_cost=costs["ins"],
         del_cost=costs["del"],
      ).compute()
      if result.counters_summary is None:
         raise RuntimeError("The algorithm did not return a counter summary.")
      connection.send((
         "completed",
         time.perf_counter() - started_at,
         result.counters_summary,
         result.distance,
         result.edit_script,
      ))
   except Exception as error:
      connection.send(("error", repr(error)))
   finally:
      connection.close()

class Study:
   eng_alphabet_low = [chr(i) for i in range(ord('a'), ord('z') + 1)]
   default_seed = 4367
   results_root = Path(__file__).parent / "results"

   def __init__(self):
      pass

   def report_runtime() -> str:
      # a bunch of sys calls that gather machine info, and then report it to the terminal in an organized way
      raise NotImplementedError()

   def get_results_directory(
      self,
      use_random_word: bool,
      scheme_name: str | None = None,
   ) -> Path:
      case_match = re.fullmatch(r"Case([A-Z]\d+)", type(self).__name__)
      if case_match is None:
         raise ValueError(
            f"Study class name {type(self).__name__!r} must follow the CaseB1 pattern."
         )

      input_directory = "rand_word" if use_random_word else "no_rand_word"
      results_directory = self.results_root / f"case_{case_match.group(1).lower()}" / input_directory

      if scheme_name is not None:
         scheme_match = re.fullmatch(r"S(\d+)", scheme_name, re.IGNORECASE)
         if scheme_match is None:
            raise ValueError(f"Invalid cost scheme name: {scheme_name!r}")
         results_directory /= f"scheme {int(scheme_match.group(1))}"

      results_directory.mkdir(parents=True, exist_ok=True)
      return results_directory

   @staticmethod
   def run_with_timeout(
      algorithm: type[EditDistanceEngine],
      string_a: str,
      string_b: str,
      timeout_seconds: float,
      cost_scheme: Mapping[str, int] | None = None,
   ) -> tuple[str, float, dict[str, int] | None, int | None, list[str] | None]:
      costs = {"sub": 1, "ins": 1, "del": 1}
      if cost_scheme is not None:
         unknown_costs = {
            key for key in cost_scheme if key not in costs
         }
         if unknown_costs:
            raise ValueError(f"Unknown edit cost(s): {', '.join(sorted(unknown_costs))}")
         costs.update(cost_scheme)

      if any(
         not isinstance(cost, int) or isinstance(cost, bool) or cost <= 0
         for cost in costs.values()
      ):
         raise ValueError("All edit costs must be positive integers.")

      context = multiprocessing.get_context("spawn")
      parent_connection, child_connection = context.Pipe(duplex=False)
      process = context.Process(
         target=_run_worker,
         args=(child_connection, algorithm, string_a, string_b, costs),
      )
      process.start()
      child_connection.close()

      try:
         while not parent_connection.poll(0.1):
            if not process.is_alive():
               raise RuntimeError("Worker exited before starting the computation.")

         start_message = parent_connection.recv()
         if start_message[0] != "started":
            raise RuntimeError(f"Unexpected message from worker: {start_message!r}")

         deadline = time.perf_counter() + timeout_seconds
         remaining = deadline - time.perf_counter()
         if remaining <= 0 or not parent_connection.poll(remaining):
            process.terminate()
            process.join()
            return "timeout", timeout_seconds, None, None, None

         message = parent_connection.recv()
         process.join()
         if message[0] == "error":
            raise RuntimeError(f"Worker failed: {message[1]}")
         if message[0] != "completed":
            raise RuntimeError(f"Unexpected message from worker: {message!r}")
         return "completed", message[1], message[2], message[3], message[4]
      finally:
         parent_connection.close()
         if process.is_alive():
            process.terminate()
            process.join()
         process.close()

   def generate_graph(
      self,
      series: Sequence[tuple[str, Sequence[float], Sequence[float], str]],
      output_path: Path,
      *,
      title: str,
      x_label: str,
      y_label: str,
      x_scale: Literal["linear", "log"] = "linear",
      y_scale: Literal["linear", "log"] = "linear",
      y_limits: tuple[float | None, float | None] | None = None,
      reference_line: tuple[float, str] | None = None,
      save: bool = True,
      chart_type: Literal["line", "bar"] = "line",
      x_tick_labels: Sequence[str] | None = None,
   ) -> Figure:
      ## ensure that all inputs on the x axis are shown, no approximating or showing half steps. these inputs are whole numbers and should all be shown on the x axis label
      figure, axes = plt.subplots()
      for series_index, (label, x_values, y_values, style) in enumerate(series):
         if chart_type == "bar":
            bar_width = 0.8 / len(series)
            offset = -0.4 + bar_width * (series_index + 0.5)
            axes.bar(
               [x_value + offset for x_value in x_values],
               y_values,
               width=bar_width,
               label=label,
            )
         else:
            axes.plot(x_values, y_values, style, label=label)

      if reference_line is not None:
         value, label = reference_line
         axes.axhline(value, color="red", linestyle="--", label=label)

      axes.set_xlabel(x_label)
      axes.set_ylabel(y_label)
      axes.set_title(title)
      if x_tick_labels is not None:
         if not series or len(series[0][1]) != len(x_tick_labels):
            raise ValueError("x_tick_labels must match the first series' x values.")
         axes.set_xticks(series[0][1], labels=x_tick_labels)
      axes.set_xscale(x_scale)
      axes.set_yscale(y_scale)
      if y_limits is not None:
         axes.set_ylim(*y_limits)
      axes.grid(True, alpha=0.3)
      axes.legend()
      figure.tight_layout()
      if save:
         figure.savefig(output_path, dpi=160)
      return figure

   @staticmethod
   def build_series(label: str, data: Sequence[Mapping[str, object]], x_field: str, y_field: str, style: str) -> tuple[str, list[float], list[float], str]:
      x_values = []
      y_values = []

      for row in data:
         x_value = row[x_field]
         y_value = row[y_field]

         if not isinstance(x_value, Real) or not isinstance(y_value, Real):
            raise TypeError(
               f"Series '{label}' requires numeric values for "
               f"'{x_field}' and '{y_field}'"
            )

         x_values.append(float(x_value))
         y_values.append(float(y_value))

      return (label, x_values, y_values, style)


   def rand_word(alphabet: List[str], length: int, seed: int | None) -> str:
      """
      given an alphabet, the target length, generate a random word. this will be used for edge cases, 
      and the seed is possible to be sent in as well for reproduceability, but can use the machine's 
      random seed if not.
      """
      random_word = ""

      if seed is not None:
         random.seed(seed)
      else:
         random.seed()

      for _ in range(length):
         random_word += random.choice(alphabet)

      return random_word
   
   