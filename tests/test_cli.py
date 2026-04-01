"""Test the bambuuzle CLI."""

from __future__ import annotations

import hashlib
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from bambuuzle.cli import main

from .conftest import SAMPLE_GCODE, build_test_3mf


def run_cli(*argv: str) -> None:
    """Run the CLI with the given arguments."""
    with patch("sys.argv", ["bambuuzle", *argv]):
        main()


def test_get_plate_default(tmp_path: Path):
    """get_plate should extract plate 1 by default."""
    src = build_test_3mf(tmp_path / "input.gcode.3mf")
    os.chdir(tmp_path)

    run_cli("get_plate", str(src))

    output = tmp_path / "plate_1.gcode"
    assert output.exists()
    assert output.read_text() == SAMPLE_GCODE


def test_get_plate_specific(tmp_path: Path):
    """get_plate --plate 2 should extract plate 2."""
    src = build_test_3mf(tmp_path / "input.gcode.3mf", plates=2)
    os.chdir(tmp_path)

    run_cli("get_plate", str(src), "--plate", "2")

    output = tmp_path / "plate_2.gcode"
    assert output.exists()
    assert "; plate 2" in output.read_text()


def test_put_plate_overwrites_input(tmp_path: Path):
    """put_plate should overwrite the input file by default."""
    src = build_test_3mf(tmp_path / "input.gcode.3mf")
    os.chdir(tmp_path)

    # Extract, modify, re-insert
    modified_gcode = "G28\n; modified by test\nM84\n"
    (tmp_path / "plate_1.gcode").write_text(modified_gcode)

    run_cli("put_plate", str(src))

    with zipfile.ZipFile(src, "r") as zf:
        gcode = zf.read("Metadata/plate_1.gcode").decode("utf-8")
        md5 = zf.read("Metadata/plate_1.gcode.md5").decode("utf-8")

    assert gcode == modified_gcode
    assert md5 == hashlib.md5(modified_gcode.encode("utf-8")).hexdigest()


def test_put_plate_with_output(tmp_path: Path):
    """put_plate --output should write to a different file."""
    src = build_test_3mf(tmp_path / "input.gcode.3mf")
    out = tmp_path / "output.gcode.3mf"
    os.chdir(tmp_path)

    (tmp_path / "plate_1.gcode").write_text("G28\n")
    run_cli("put_plate", str(src), "--output", str(out))

    assert out.exists()
    # Original should be unchanged
    with zipfile.ZipFile(src, "r") as zf:
        assert zf.read("Metadata/plate_1.gcode").decode("utf-8") == SAMPLE_GCODE


def test_get_plate_missing_plate(tmp_path: Path):
    """get_plate with a nonexistent plate number should raise KeyError."""
    src = build_test_3mf(tmp_path / "input.gcode.3mf")
    os.chdir(tmp_path)

    with pytest.raises(KeyError, match="No plate 5"):
        run_cli("get_plate", str(src), "--plate", "5")


def test_no_command_shows_help(capsys):
    """Running with no command should print help and exit."""
    with pytest.raises(SystemExit) as exc_info:
        run_cli()
    assert exc_info.value.code == 1
