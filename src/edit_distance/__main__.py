"""Main entry point for the package.

Purpose:
    This module is the executable entry point for the project. It should build the
    CLI, parse the command line, and dispatch to the selected algorithm.

Who should call this:
    This file is invoked by Python when the package is run with:
        python -m edit_distance

This file is not responsible for:
    - implementing the algorithm itself
    - performing experiments or data analysis
    - storing environment-specific runtime state
"""

from __future__ import annotations

from pathlib import Path
from .cli import EditDistanceCLI
from .io import InputParser
from .memo import MemoizedEditDistance
from .naive import NaiveEditDistance
from .table import TabulatedEditDistance

def main() -> int:

    """Minimal checkpoint-1 verification script.

    Reads the sample TSV pairs and prints the distance and total operation count
    for each implemented algorithm using the required tab-separated format.
    """
    data_path = Path(__file__).resolve().parents[2] / "data" / "sample_verification.tsv"
    algorithms = (
        ("naive", NaiveEditDistance),
        ("memo", MemoizedEditDistance),
        ("table", TabulatedEditDistance),

    )

    for method_name, engine_class in algorithms:
        for string_a, string_b, _ in InputParser.load_pairs(data_path):
            result = engine_class(string_a, string_b, 1, 1, 1).compute()
            total_operations = (result.counters_summary or {}).get("total_operations", 0)
            print(f"{method_name}\t{string_a}\t{string_b}\t{result.distance}\t{total_operations}")

    return 0

# def main() -> int:
#     cli = EditDistanceCLI()
#     return cli.run()


if __name__ == "__main__":
    raise SystemExit(main())
