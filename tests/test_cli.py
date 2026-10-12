from edit_distance.cli import EditDistanceCLI
from edit_distance.models import RuntimeConfig
from edit_distance.naive import NaiveEditDistance
from edit_distance.memo import MemoizedEditDistance
from edit_distance.table import TabulatedEditDistance
from edit_distance.smith_water import SmithWaterEditDistance
import contextlib
import io
from pathlib import Path

import pytest

def test_parse_args_builds_runtime_config() -> None:
    cli = EditDistanceCLI()
    config = cli.parse_args([
        "--input",
        "data/sample_verification.tsv",
        "--sub",
        "2",
        "--ins",
        "3",
        "--del",
        "4",
        "--impl",
        "memo",
        "--verbose",
        "--counters",
    ])

    assert isinstance(config, RuntimeConfig)
    assert config.input_path == "data/sample_verification.tsv"
    assert config.sub_cost == 2
    assert config.ins_cost == 3
    assert config.del_cost == 4
    assert config.impl == "memo"
    assert config.verbose is True
    assert config.counters is True


def test_resolve_impl_returns_expected_class() -> None:
    cli = EditDistanceCLI()

    assert cli._resolve_impl("naive") is NaiveEditDistance
    assert cli._resolve_impl("memo") is MemoizedEditDistance
    assert cli._resolve_impl("table") is TabulatedEditDistance
    assert cli._resolve_impl("smith-water") is SmithWaterEditDistance


def test_smith_water_cli_runs_local_alignment(tmp_path) -> None:
    input_file = tmp_path / "pairs.tsv"
    input_file.write_text("XXABCYY\tZZABCWW\n", encoding="utf-8")
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        EditDistanceCLI().run([
            "--input", str(input_file),
            "--impl", "smith-water",
            "--verbose",
        ])

    assert output.getvalue().splitlines() == [
        "XXABCYY\tZZABCWW\t3.0",
        "  A B C",
        "  A B C",
        "  . . .",
    ]


def test_verbose_flag_prints_alignment_for_each_implementation(tmp_path) -> None:
    input_file = tmp_path / "pairs.tsv"
    input_file.write_text("kitten\tsitting\t3\n", encoding="utf-8")
    expected_output = [
        "kitten\tsitting\t3",
        "  k i t t e n -",
        "  s i t t i n g",
        "  S . . . S . I",
    ]

    for implementation in ("naive", "memo", "table"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            EditDistanceCLI().run([
                "--input", str(input_file),
                "--impl", implementation,
                "--verbose",
            ])
        assert output.getvalue().splitlines() == expected_output


def test_alignment_is_not_printed_without_verbose(tmp_path) -> None:
    input_file = tmp_path / "pairs.tsv"
    input_file.write_text("kitten\tsitting\t3\n", encoding="utf-8")
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        EditDistanceCLI().run(["--input", str(input_file), "--impl", "table"])

    assert output.getvalue().splitlines() == ["kitten\tsitting\t3"]


@pytest.mark.parametrize(
    ("flag", "module_name", "class_name"),
    [
        ("--caseb1", "study.study_b1", "CaseB1"),
        ("--caseb2", "study.study_b2", "CaseB2"),
        ("--caseb3", "study.study_b3", "CaseB3"),
        ("--case_cost_schemes", "study.cost_weights", "CaseB4"),
        ("--case_edge", "study.edge_cases", "CaseB5"),
    ],
)
def test_study_flags_dispatch_input_path(
    flag: str,
    module_name: str,
    class_name: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import importlib

    input_file = tmp_path / "small_study.tsv"
    input_file.write_text("abc\txyz\n", encoding="utf-8")
    results_directory = tmp_path / "custom-results"
    captured: list[tuple[str | None, Path | None]] = []
    module = importlib.import_module(module_name)
    study_class = getattr(module, class_name)
    monkeypatch.setattr(
        study_class,
        "run",
        lambda self, input_path=None, results_dir=None: captured.append(
            (input_path, results_dir)
        ),
    )

    assert EditDistanceCLI().run(
        [
            flag,
            "--input",
            str(input_file),
            f"--results_dir={results_directory}",
        ]
    ) == 0
    assert captured == [(str(input_file), results_directory)]


def test_edge_study_flag_allows_generated_inputs_without_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import study.edge_cases

    captured: list[tuple[str | None, Path | None]] = []
    monkeypatch.setattr(
        study.edge_cases.CaseB5,
        "run",
        lambda self, input_path=None, results_dir=None: captured.append(
            (input_path, results_dir)
        ),
    )

    assert EditDistanceCLI().run(["--case_edge"]) == 0
    assert captured == [(None, None)]


def test_regular_algorithm_still_requires_input_file() -> None:
    with pytest.raises(SystemExit, match="2"):
        EditDistanceCLI().run([])


def test_study_input_must_use_study_tsv_suffix(tmp_path: Path) -> None:
    input_file = tmp_path / "pairs.tsv"
    input_file.write_text("abc\txyz\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="2"):
        EditDistanceCLI().run(["--caseb1", "--input", str(input_file)])


def test_only_one_study_flag_can_be_selected() -> None:
    with pytest.raises(SystemExit, match="2"):
        EditDistanceCLI().run(["--caseb1", "--caseb2"])


def test_results_dir_is_rejected_without_study_flag(tmp_path: Path) -> None:
    input_file = tmp_path / "pairs.tsv"
    input_file.write_text("abc\txyz\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="2"):
        EditDistanceCLI().run(
            ["--input", str(input_file), "--results_dir", str(tmp_path / "out")]
        )


def test_b4_keeps_scheme_subdirectories_under_custom_results_root(
    tmp_path: Path,
) -> None:
    from study.cost_weights import CaseB4

    custom_root = tmp_path / "custom-results"
    scheme_directory = CaseB4().get_results_directory(
        use_random_word=True,
        scheme_name="S3",
        results_root=custom_root,
    )

    assert scheme_directory == (
        custom_root / "case_b4" / "rand_word" / "scheme 3"
    )
    assert scheme_directory.is_dir()
