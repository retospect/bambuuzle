"""Test creating Bambu 3MF files from scratch."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from bambuuzle import BambuFile


def test_create_single_plate(tmp_path: Path):
    """Create a file from scratch with one plate."""
    bf = BambuFile()
    bf.add_plate(gcode="G28\nG1 X50 Y50 F3000\nM84\n")

    out = tmp_path / "scratch.gcode.3mf"
    bf.save(str(out))

    with zipfile.ZipFile(out, "r") as zf:
        names = zf.namelist()
        assert "[Content_Types].xml" in names
        assert "_rels/.rels" in names
        assert "3D/3dmodel.model" in names
        assert "Metadata/plate_1.gcode" in names
        assert "Metadata/plate_1.gcode.md5" in names
        assert "Metadata/plate_1.json" in names

        gcode_bytes = zf.read("Metadata/plate_1.gcode")
        md5_hex = zf.read("Metadata/plate_1.gcode.md5").decode("utf-8")
        assert md5_hex == hashlib.md5(gcode_bytes).hexdigest()


def test_create_multiplate(tmp_path: Path):
    """Create a file from scratch with multiple plates."""
    bf = BambuFile()
    bf.add_plate(gcode="G28\n; plate 1\n")
    bf.add_plate(gcode="G28\n; plate 2\n")

    out = tmp_path / "multi.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert len(bf2.plates) == 2
    assert "; plate 1" in bf2.plate(1).gcode
    assert "; plate 2" in bf2.plate(2).gcode


def test_create_with_custom_metadata(tmp_path: Path):
    """Custom metadata dict should be preserved."""
    meta = {"plate_index": 0, "prediction": 600, "custom_key": "test"}
    bf = BambuFile()
    bf.add_plate(gcode="G28\n", metadata=meta)

    out = tmp_path / "custom_meta.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert bf2.plate(1).metadata["custom_key"] == "test"
    assert bf2.plate(1).metadata["prediction"] == 600


def test_create_empty_gcode(tmp_path: Path):
    """An empty gcode string should still produce a valid file."""
    bf = BambuFile()
    bf.add_plate(gcode="")

    out = tmp_path / "empty.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert bf2.plate(1).gcode == ""
    assert bf2.plate(1).md5 == hashlib.md5(b"").hexdigest()


def test_scratch_file_is_valid_zip(tmp_path: Path):
    """A from-scratch file should be a valid ZIP with DEFLATE compression."""
    bf = BambuFile()
    bf.add_plate(gcode="G28\n")

    out = tmp_path / "valid.gcode.3mf"
    bf.save(str(out))

    assert zipfile.is_zipfile(out)
    with zipfile.ZipFile(out, "r") as zf:
        for info in zf.infolist():
            if not info.is_dir() and info.file_size > 0:
                assert info.compress_type == zipfile.ZIP_DEFLATED


def test_auto_plate_numbering(tmp_path: Path):
    """Plates should auto-number sequentially."""
    bf = BambuFile()
    p1 = bf.add_plate(gcode="plate1\n")
    p2 = bf.add_plate(gcode="plate2\n")
    p3 = bf.add_plate(gcode="plate3\n")

    assert p1.number == 1
    assert p2.number == 2
    assert p3.number == 3
