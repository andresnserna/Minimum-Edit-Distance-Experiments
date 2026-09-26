"""Top-level script wrapper for the project.

Purpose:
    This module is a convenience entry point for running the project directly from
    the repository root without requiring an installed package. It forwards all
    execution to the package entry point.

Who should call this:
    Developers and graders can call this file directly from the workspace root.

This file is not responsible for:
    - defining the actual edit-distance algorithms
    - handling the empirical study itself
    - acting as a replacement for package-level CLI parsing
"""

from edit_distance.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
