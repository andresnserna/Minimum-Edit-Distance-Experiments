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
from typing import List, Tuple


class InputParser:
    """Parses TSV files containing string pairs and optional expected distances."""

    @staticmethod
    def load_pairs(path: str | Path) -> List[Tuple[str, str, int | None]]:
        """Read a TSV file and return a list of (A, B, expected_distance) records."""
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        pairs: List[Tuple[str, str, int | None]] = []
        for raw_line in file_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            split_columns = line.split("\t")
            columns = []
            for part in split_columns:
                columns.append(part.strip())

            if len(columns) < 2:
                raise ValueError(f"Malformed TSV row: {raw_line!r}")

            string_a = columns[0]
            string_b = columns[1]
            expected_distance = None
            if len(columns) >= 3 and columns[2] not in ("", "null", "None"):
                expected_distance = int(columns[2])

            pairs.append((string_a, string_b, expected_distance))

        return pairs

    @staticmethod
    def load_study_pairs(path: str | Path) -> List[Tuple[str, str]]:
        """Read a study pair file that contains only A and B columns."""
        study_pairs: List[Tuple[str, str]] = []

        for pair in InputParser.load_pairs(path):
            string_a, string_b, _ = pair
            study_pairs.append((string_a, string_b))

        return study_pairs


class OutputWriter:
    """Encapsulates the formatting and writing of final result lines."""

    @staticmethod
    def write_counters(path: str | Path, summary: dict) -> None:
        """Write a single line summary to the counters file."""
        raise NotImplementedError
