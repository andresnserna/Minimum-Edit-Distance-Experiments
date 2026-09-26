"""Command-line layer for the edit-distance project.

Purpose:
    This module is the user-facing entry point for parsing flags, validating cost
    values, selecting an implementation, and invoking the engine for each input
    pair. It is also responsible for formatting the output required by the
    assignment.

Who should call this:
    The entry point should call this module; tests may also call helper methods
    if they want to validate parsing or selection behavior without invoking the
    full program.

This file is not responsible for:
    - the actual DP recurrence logic
    - raw file-reading internals beyond dispatching to the parser
    - the empirical study and measurement code
"""

from __future__ import annotations

import argparse
from typing import Sequence

from .base import EditDistanceResultFormatter
from .io import InputParser
from .memo import MemoizedEditDistance
from .models import RuntimeConfig
from .naive import NaiveEditDistance
from .table import TabulatedEditDistance


class EditDistanceCLI:
    """Handles the command-line contract for the assignment."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Edit distance project CLI")

    def build_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser for the main program."""
        parser = argparse.ArgumentParser(description="Edit distance project CLI")

        parser.add_argument(
            "--input",
            type=str,
            required=True,
            help="Path to the TSV file containing input string pairs.",
        )
        parser.add_argument(
            "--sub",
            type=int,
            default=1,
            help="Substitution cost. Default: 1.",
        )
        parser.add_argument(
            "--ins",
            type=int,
            default=1,
            help="Insertion cost. Default: 1.",
        )
        parser.add_argument(
            "--del",
            dest="delete_cost",
            type=int,
            default=1,
            help="Deletion cost. Default: 1.",
        )
        parser.add_argument(
            "--impl",
            choices=["naive", "memo", "table"],
            default="table",
            help="Which edit-distance implementation to run.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print the verbose alignment block for each result.",
        )
        parser.add_argument(
            "--counters",
            action="store_true",
            help="Emit counter summaries alongside the final distance results.",
        )

        self.parser = parser
        return parser

    def _validate_costs(self, sub_cost: int, ins_cost: int, del_cost: int) -> None:
        """Validate cost values before dispatching to an algorithm."""
        if sub_cost <= 0 or ins_cost <= 0 or del_cost <= 0:
            raise ValueError("All edit costs must be positive integers.")

    def _resolve_impl(self, impl_name: str):
        """Map the selected implementation name to its algorithm class."""
        mapping = {
            "naive": NaiveEditDistance,
            "memo": MemoizedEditDistance,
            "table": TabulatedEditDistance,
        }
        return mapping[impl_name]

    def _execute(self, config: RuntimeConfig) -> int:
        """Execute the selected implementation against the provided input."""
        impl_cls = self._resolve_impl(config.impl)
        pairs = InputParser.load_pairs(config.input_path)

        for string_a, string_b, _ in pairs:
            algorithm = impl_cls(
                string_a,
                string_b,
                sub_cost=config.sub_cost,
                ins_cost=config.ins_cost,
                del_cost=config.del_cost,
            )
            result = algorithm.compute()

            print(EditDistanceResultFormatter.format_output(string_a, string_b, result.distance))

            if config.verbose:
                block = EditDistanceResultFormatter.format_verbose_block(result.alignment_lines)
                if block:
                    print(block)

            if config.counters:
                summary = getattr(result, "counters_summary", None)
                if summary is None:
                    summary = {"distance": result.distance}
                print(f"  counters={summary}")

        return 0 if pairs else 1

    def parse_args(self, argv: Sequence[str] | None = None):
        """Parse the argument list and return the runtime configuration."""
        args = self.build_parser().parse_args(argv)

        self._validate_costs(args.sub, args.ins, args.delete_cost)

        return RuntimeConfig(
            input_path=args.input,
            sub_cost=args.sub,
            ins_cost=args.ins,
            del_cost=args.delete_cost,
            impl=args.impl,
            verbose=args.verbose,
            counters=args.counters,
        )

    def run(self, argv: Sequence[str] | None = None) -> int:
        """Execute the CLI and return the process exit code."""
        config = self.parse_args(argv)
        return self._execute(config)
