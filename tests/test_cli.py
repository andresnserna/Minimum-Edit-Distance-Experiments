from edit_distance.cli import EditDistanceCLI
from edit_distance.models import RuntimeConfig
from edit_distance.naive import NaiveEditDistance
from edit_distance.memo import MemoizedEditDistance
from edit_distance.table import TabulatedEditDistance
import contextlib
import io


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
