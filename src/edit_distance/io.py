"""Input and output helpers for the project.

Purpose:
    This module is responsible for reading the verification and study TSV files,
    validating their format, and providing a clean way to iterate over string
    pairs. It should not perform algorithm work or determine edit distance.

Who should call this:
    The CLI and test harnesses should call this module when loading input files.

This file is not responsible for:
    - computing edit distance
    - generating empirical study reports
    - writing final alignment blocks to the console
"""

from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Tuple


class InputParser:
    """Parses TSV files containing string pairs and optional expected distances."""

    @staticmethod
    def load_pairs(path: str | Path) -> List[Tuple[str, str, int | None]]:
        """Read a TSV file and return a list of (A, B, expected_distance) records."""
        raise NotImplementedError

    @staticmethod
    def load_study_pairs(path: str | Path) -> List[Tuple[str, str]]:
        """Read a study pair file that contains only A and B columns."""
        raise NotImplementedError


class OutputWriter:
    """Encapsulates the formatting and writing of final result lines."""

    @staticmethod
    def write_counters(path: str | Path, summary: dict) -> None:
        """Write a single line summary to the counters file."""
        raise NotImplementedError
