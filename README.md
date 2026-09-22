# COSC 4367 Project 1 — Edit Distance Engine

This project is the scaffold for the edit-distance assignment described in the project specification. The goal is to implement and compare three versions of the Levenshtein-style alignment engine:

- naive recursive search
- top-down memoized dynamic programming
- bottom-up tabulated dynamic programming

This repository is intentionally a base project skeleton. It contains the expected package layout, CLI entry points, test directory, data folder, and the core classes needed to start implementation without locking onto a single algorithm yet.

## Intended audience

This code is meant to be used by:

- the main CLI entry point for grading runs
- test code that validates distance correctness on sample pairs
- algorithm implementations that need a shared counter and result model

## Responsibilities and boundaries

The code in this repository is intentionally split so that each file has a narrow responsibility:

- CLI code parses command-line flags and invokes the correct implementation.
- engine classes compute edit distance and reconstruction data.
- counter instrumentation tracks operation counts.
- data-loading code reads the TSV pairs.
- tests validate correctness and edge conditions.

This repository does not implement the actual recurrence logic yet. It only provides the structure that the full solution will build on.

## Planned runtime interface

The final implementation should support commands in this shape:

```bash
python -m edit_distance --input data/sample_verification.tsv --sub 1 --ins 1 --del 1 --impl table --verbose --counters
```

The project also supports a test-only execution path for small verification cases, which will be added once the engine logic is implemented.

## Project layout

```text
.
├── README.md
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── data/
│   └── sample_verification.tsv
├── src/
│   └── edit_distance/
│       ├── __init__.py
│       ├── __main__.py
│       ├── base.py
│       ├── cli.py
│       ├── counters.py
│       ├── io.py
│       └── models.py
├── tests/
│   ├── __init__.py
│   └── test_cases.py
└── main.py
```

## Quick start

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m edit_distance --help
```

## Notes

- No external dependencies are required for the base implementation.
- The project is intentionally scaffolded for Python, matching the assignment’s language options.
- This is a starting point only; algorithms, counters, and reconstruction logic are intentionally left for the implementation phase.
