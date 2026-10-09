from __future__ import annotations
from .base import AlignmentResult, EditDistanceEngine
from edit_distance.counters import Counters
from edit_distance.time import TimeTracker
from typing import List


class SmithWaterEditDistance(EditDistanceEngine):
   """
   Smith-Waterman local alignment edit-distance engine. Implements the Smith-Waterman algorithm for computing local alignment scores between two sequences.
   """
   
   def compute(self) -> AlignmentResult:
      timer = TimeTracker()
      timer.start()
      counter = Counters()
      try:
         result = self.compute_helper(counter)
         timer.finish()
         return result
      finally:
         counter.reset()

   def compute_helper(self, counter: Counters) -> AlignmentResult:
      counter.calls += 1
      string_a = self.string_a
      string_b = self.string_b
      distance = 0
      edit_script: List[str] = []

      ...

      return AlignmentResult(
         string_a=string_a,
         string_b=string_b,
         distance=distance,
         edit_script=edit_script,
         alignment_lines=self._build_alignment(edit_script),
         counters_summary=counter.as_dict(),
      )