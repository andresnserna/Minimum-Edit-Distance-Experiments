"""Base abstractions for the edit-distance engine.

Purpose:
    This module defines the shared base interfaces and result container types that
    the naive, memoized, and tabulated implementations will use. It keeps the
    project organized around a common contract for distance computation,
    reconstruction, and reporting.

Who should call this:
    This module is intended for use by the concrete algorithm implementations,
    the CLI layer, and the test suite. It should not be called directly by user
    code in normal operation.

This file is not responsible for:
    - parsing command-line arguments
    - reading TSV files
    - writing counters.txt output
    - plotting or empirical study analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class AlignmentResult:
    """Container for the final output of one edit-distance run."""

    string_a: str
    string_b: str
    distance: int
    edit_script: List[str] = field(default_factory=list)
    alignment_lines: List[str] = field(default_factory=list)
    counters_summary: Optional[dict] = None
    TAB = "    "


class EditDistanceEngine:
    """Abstract base class for the three edit-distance implementations."""

    def __init__(self, string_a: str, string_b: str, sub_cost: int = 1, ins_cost: int = 1, del_cost: int = 1):
        self.string_a = string_a
        self.string_b = string_b
        self.sub_cost = sub_cost
        self.ins_cost = ins_cost
        self.del_cost = del_cost

    def _best_choice(self, del_total: int, ins_total: int, sub_total: int) -> str:
        """Select the winning operation among equal-cost minima.

        Priority order for tied minima is: delete, then insert, then substitute.
        """
        min_total = min(del_total, ins_total, sub_total)

        if del_total == min_total:
            return "delete"
        if ins_total == min_total:
            return "insert"
        return "substitute"

    def compute(self) -> AlignmentResult:
        """Compute distance, reconstruction, and alignment for the stored strings."""
        raise NotImplementedError

    def _build_alignment(self, edit_script: List[str]) -> List[str]:
        """Convert an edit script into the three-line block required by the assignment."""
        raise NotImplementedError
    
    def _best_choice(self, del_total: int, ins_total: int, sub_total: int) -> str:
        """
        Return the operation name for the minimum-cost path, including tie-break logic.
        Priority order for tied minima is: delete, then insert, then substitute.
        """
        min_total = min(del_total, ins_total, sub_total)

        if del_total == min_total:
            return "delete"
        if ins_total == min_total:
            return "insert"
        return "substitute"

class EditDistanceResultFormatter:
    """Helper responsible only for formatting the final output rows."""

    @staticmethod
    def format_output(string_a: str, string_b: str, distance: int) -> str:
        return f"{string_a}\t{string_b}\t{distance}"

    @staticmethod
    def format_verbose_block(alignment_lines: List[str]) -> str:
        return "\n".join(f"  {line}" for line in alignment_lines)
