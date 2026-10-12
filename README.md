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

## Running empirical studies from the CLI

Pass exactly one study flag to run a study. An optional `*_study.tsv` file
replaces the study's built-in generated input pairs. Use `--results_dir` to
choose a custom top-level output directory; studies retain their own subfolder
layout beneath it (including B4's per-scheme folders):

```bash
PYTHONPATH=src:. python -m edit_distance --caseb1 --input data/example_study.tsv --results_dir=results
PYTHONPATH=src:. python -m edit_distance --caseb2 --input data/example_study.tsv --results_dir=results
PYTHONPATH=src:. python -m edit_distance --caseb3 --input data/example_study.tsv --results_dir=results
PYTHONPATH=src:. python -m edit_distance --case_cost_schemes --input data/example_study.tsv --results_dir=results
PYTHONPATH=src:. python -m edit_distance --case_edge --input data/example_study.tsv --results_dir=results
```

The study TSV format is two tab-separated strings per row; blank lines and
comment lines are ignored. `--case_edge` also works without `--input`, in which
case it uses the study's generated controlled-alphabet and DNA cases. Without
any study flag, `--input` remains required for a regular edit-distance run.
Study outputs are written in the corresponding `study/results/case_*`
directory by default. With `--results_dir=results`, for example, B1 writes to
`results/case_b1/rand_word/`, and B4 writes to
`results/case_b4/rand_word/scheme 1/` through `scheme 4/`.

## Smith–Waterman local alignment

The `SmithWaterEditDistance` engine implements the local-similarity recurrence
from Smith and Waterman (1981), including a zero floor, global matrix maximum,
and length-dependent gap costs:

```python
from edit_distance import SmithWaterEditDistance

result = SmithWaterEditDistance("XXABCYY", "ZZABCWW").compute()
print(result.distance)  # best local alignment score
print(result.alignment_lines)
```

Its defaults use a match score of `1`, a mismatch score of `-1/3`, and a gap
weight `W_k = 1 + k/3`. Pass `match_score`, `mismatch_score`, and a callable
`gap_cost(k)` to use other scoring parameters; a `similarity_score(a, b)`
callable can replace the match/mismatch score rule. The 0-based, half-open
`alignment_range_a` and `alignment_range_b` fields identify the selected
segments in the original inputs. The algorithm is also available through the
CLI as `--impl smith-water`. Its `distance` field contains the local-alignment
score (which may be fractional), not a global edit distance.

To compare Smith–Waterman against the memoized and tabulated global
edit-distance implementations on reproducible inputs containing a shared
subsequence, run:

```bash
PYTHONPATH=src:. python -m study.study_sw
```

The study writes `sw_results.csv`, `sw_operation_counts.png`, and
`sw_runtime.png` under `study/results/case_sw`. The CSV labels the Smith–Waterman
value as a local score and records operation counts, runtime, input strings,
and any timeout or worker error for each algorithm and input length.

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
PYTHONPATH=src python -m edit_distance
```

## Notes
- the quick start instructions are for checkpoint #1 only