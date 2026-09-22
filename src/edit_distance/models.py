"""Data models for command-line execution and runtime configuration.

Purpose:
    This module captures the configuration values needed to run a single
    algorithm invocation, including costs, implementation choice, and runtime
    flags. The plan is to make the runtime settings explicit and easy to pass
    between the CLI and the engine layer.

Who should call this:
    The CLI should construct this object from user input before dispatching to
    the specific algorithm implementation. Tests can also build it directly.

This file is not responsible for:
    - low-level counter accounting
    - file parsing
    - algorithmic selection logic beyond configuration packaging
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """Runtime parameters for one command execution."""

    input_path: str
    sub_cost: int = 1
    ins_cost: int = 1
    del_cost: int = 1
    impl: str = "table"
    verbose: bool = False
    counters: bool = False
