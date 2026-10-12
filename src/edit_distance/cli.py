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
from pathlib import Path
from typing import Sequence

from .base import EditDistanceResultFormatter
from .io import InputParser
from .memo import MemoizedEditDistance
from .models import RuntimeConfig
from .naive import NaiveEditDistance
from .smith_water import SmithWaterEditDistance
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
            help="Path to a TSV input file. Study cases accept *_study.tsv files.",
        )
        parser.add_argument(
            "--results_dir",
            type=str,
            help="Top-level directory for study outputs. Defaults to study/results.",
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
            choices=["naive", "memo", "table", "smith-water"],
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
        study_group = parser.add_mutually_exclusive_group()
        study_group.add_argument(
            "--caseb1",
            dest="study_case",
            action="store_const",
            const="b1",
            help="Run empirical study B1.",
        )
        study_group.add_argument(
            "--caseb2",
            dest="study_case",
            action="store_const",
            const="b2",
            help="Run empirical study B2.",
        )
        study_group.add_argument(
            "--caseb3",
            dest="study_case",
            action="store_const",
            const="b3",
            help="Run empirical study B3.",
        )
        study_group.add_argument(
            "--case_cost_schemes",
            dest="study_case",
            action="store_const",
            const="cost_weights",
            help="Run the B4 cost-weight study.",
        )
        study_group.add_argument(
            "--case_edge",
            dest="study_case",
            action="store_const",
            const="edge_cases",
            help="Run the B5 edge-case study.",
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
            "smith-water": SmithWaterEditDistance,
        }
        return mapping[impl_name]

    def _execute(self, config: RuntimeConfig) -> int:
        """Execute the selected implementation against the provided input."""
        if config.study_case is not None:
            if config.input_path is not None:
                input_path = Path(config.input_path)
                if not input_path.name.endswith("_study.tsv"):
                    self.parser.error(
                        "Study input files must have a name ending in '_study.tsv'."
                    )
                if not input_path.is_file():
                    self.parser.error(f"Study input file not found: {input_path}")
            results_dir = (
                Path(config.results_dir).expanduser()
                if config.results_dir is not None
                else None
            )
            self._run_study(config.study_case, config.input_path, results_dir)
            return 0

        if config.results_dir is not None:
            self.parser.error("--results_dir can only be used with a study flag.")

        if config.input_path is None:
            self.parser.error("--input is required when no study case is selected.")

        impl_cls = self._resolve_impl(config.impl)
        pairs = InputParser.load_pairs(config.input_path)

        for string_a, string_b, _ in pairs:
            if config.impl == "smith-water":
                algorithm = impl_cls(string_a, string_b)
            else:
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

    @staticmethod
    def _run_study(
        study_case: str,
        input_path: str | None,
        results_dir: Path | None = None,
    ) -> None:
        """Import and run the selected empirical study."""
        if study_case == "b1":
            from study.study_b1 import CaseB1

            study = CaseB1()
        elif study_case == "b2":
            from study.study_b2 import CaseB2

            study = CaseB2()
        elif study_case == "b3":
            from study.study_b3 import CaseB3

            study = CaseB3()
        elif study_case == "cost_weights":
            from study.cost_weights import CaseB4

            study = CaseB4()
        elif study_case == "edge_cases":
            from study.edge_cases import CaseB5

            study = CaseB5()
        else:
            raise ValueError(f"Unknown study case: {study_case!r}")
        study.run(input_path=input_path, results_dir=results_dir)

    def parse_args(self, argv: Sequence[str] | None = None):
        """Parse the argument list and return the runtime configuration."""
        args = self.build_parser().parse_args(argv)

        if args.study_case is None:
            self._validate_costs(args.sub, args.ins, args.delete_cost)

        return RuntimeConfig(
            input_path=args.input,
            sub_cost=args.sub,
            ins_cost=args.ins,
            del_cost=args.delete_cost,
            impl=args.impl,
            verbose=args.verbose,
            counters=args.counters,
            study_case=args.study_case,
            results_dir=args.results_dir,
        )

    def run(self, argv: Sequence[str] | None = None) -> int:
        """Execute the CLI and return the process exit code."""
        config = self.parse_args(argv)
        return self._execute(config)
