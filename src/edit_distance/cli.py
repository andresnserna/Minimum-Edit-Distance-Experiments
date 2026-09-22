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


class EditDistanceCLI:
    """Handles the command-line contract for the assignment."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Edit distance project CLI")

    def build_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser for the main program."""
        raise NotImplementedError

    def parse_args(self, argv: Sequence[str] | None = None):
        """Parse the argument list and return the runtime configuration."""
        raise NotImplementedError

    def run(self, argv: Sequence[str] | None = None) -> int:
        """Execute the CLI and return the process exit code."""
        raise NotImplementedError
