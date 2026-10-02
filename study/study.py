# You will measure and evaluate operation counts and raw execution time for this study.
   
# Operation counts as instrumented above allow us to accurately describe our algorithms. They
# are deterministic, machine-independent, and reproducible.

# Run time describes this implementation, on this machine, on this day. It is noisy and it includes
# everything the language runtime does on your behalf. If I run your code on my machine, I should
# see the same operations but gather a different run time. If I run the code at a fresh startup vs
# when I have 50 Google Chrome tabs open, I might expect a difference in performance, etc.

from __future__ import annotations
from collections.abc import Sequence
from pathlib import Path
from matplotlib import pyplot as plt

class Study:

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
      reference_line: tuple[float, str] | None = None,
   ) -> None:
      plt.figure()
      for label, x_values, y_values, style in series:
         plt.plot(x_values, y_values, style, label=label)

      if reference_line is not None:
         value, label = reference_line
         plt.axhline(value, color="red", linestyle="--", label=label)

      plt.xlabel(x_label)
      plt.ylabel(y_label)
      plt.title(title)
      plt.grid(True, alpha=0.3)
      plt.legend()
      plt.tight_layout()
      plt.savefig(output_path, dpi=160)
      plt.close()

   def rand_word(alphabet: List, length: int, seed: int | None) -> str:
      """
      given an alphabet, the target length, generate a random word. this will be used for edge cases, 
      and the seed is possible to be sent in as well for reproduceability, but can use the machine's 
      random seed if not.
      """
      random_word = ""

      # impl

      return random_word
   
   