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


def main() -> int:
    """Entry point for the package-level executable."""
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
