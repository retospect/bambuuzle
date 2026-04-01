"""Test gcode modification and MD5 recomputation."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from bambuuzle import BambuFile
from bambuuzle.bambu_file import transform


def test_modify_gcode_updates_md5(tmp_3mf: Path, tmp_path: Path):
    """Editing gcode and saving should produce a correct MD5."""
    bf = BambuFile.open(str(tmp_3mf))
    original_md5 = bf.plate(1).md5

    bf.plate(1).gcode = bf.plate(1).gcode.replace("M104 S200", "M104 S210")
    assert bf.plate(1).md5 != original_md5

    out = tmp_path / "modified.gcode.3mf"
    bf.save(str(out))

    with zipfile.ZipFile(out, "r") as zf:
        gcode_bytes = zf.read("Metadata/plate_1.gcode")
        md5_in_archive = zf.read("Metadata/plate_1.gcode.md5").decode("utf-8")
        assert md5_in_archive == hashlib.md5(gcode_bytes).hexdigest()
        assert b"M104 S210" in gcode_bytes


def test_modify_gcode_content_persists(tmp_3mf: Path, tmp_path: Path):
    """Modified gcode should be readable after save/reopen."""
    bf = BambuFile.open(str(tmp_3mf))
    new_line = "G1 X200 Y200 E50 F1500 ; added by test\n"
    bf.plate(1).gcode += new_line

    out = tmp_path / "appended.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert new_line.strip() in bf2.plate(1).gcode


def test_transform_convenience(tmp_3mf: Path, tmp_path: Path):
    """The transform() helper should apply a function to a plate's gcode."""
    out = tmp_path / "transformed.gcode.3mf"

    transform(
        str(tmp_3mf),
        str(out),
        lambda g: g.replace("F6000", "F9000"),
    )

    bf = BambuFile.open(str(out))
    assert "F9000" in bf.plate(1).gcode
    assert "F6000" not in bf.plate(1).gcode


def test_replace_entire_gcode(tmp_3mf: Path, tmp_path: Path):
    """Completely replacing gcode should work."""
    bf = BambuFile.open(str(tmp_3mf))
    bf.plate(1).gcode = "G28\nM84\n"

    out = tmp_path / "replaced.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert bf2.plate(1).gcode == "G28\nM84\n"
    expected_md5 = hashlib.md5(b"G28\nM84\n").hexdigest()
    assert bf2.plate(1).md5 == expected_md5
