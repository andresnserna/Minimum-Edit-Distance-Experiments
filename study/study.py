# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

from __future__ import annotations
from collections.abc import Mapping, Sequence
from numbers import Real
from typing import List, Literal
import random
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class Study:
   eng_alphabet_low = [chr(i) for i in range(ord('a'), ord('z') + 1)]
   default_seed = 4367

   def __init__(self):
      pass

   def report_runtime() -> str:
      # a bunch of sys calls that gather machine info, and then report it to the terminal in an organized way
      raise NotImplementedError()

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
   ) -> Figure:
      figure, axes = plt.subplots()
      for label, x_values, y_values, style in series:
         axes.plot(x_values, y_values, style, label=label)

      if reference_line is not None:
         value, label = reference_line
         axes.axhline(value, color="red", linestyle="--", label=label)

      axes.set_xlabel(x_label)
      axes.set_ylabel(y_label)
      axes.set_title(title)
      axes.set_xscale(x_scale)
      axes.set_yscale(y_scale)
      if y_limits is not None:
         axes.set_ylim(*y_limits)
      axes.grid(True, alpha=0.3)
      axes.legend()
      figure.tight_layout()
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
   
   