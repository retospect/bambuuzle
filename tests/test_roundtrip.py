"""Test open -> save -> reopen roundtrip preserves data."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

from bambuuzle import BambuFile

from .conftest import SAMPLE_GCODE


def test_roundtrip_single_plate(tmp_3mf: Path, tmp_path: Path):
    """Open a file, save it, reopen — gcode and metadata should match."""
    bf = BambuFile.open(str(tmp_3mf))
    out = tmp_path / "roundtrip.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert len(bf2.plates) == 1
    assert bf2.plate(1).gcode == SAMPLE_GCODE
    assert bf2.plate(1).metadata == bf.plate(1).metadata


def test_roundtrip_multiplate(tmp_3mf_multiplate: Path, tmp_path: Path):
    """Roundtrip with multiple plates preserves all plates."""
    bf = BambuFile.open(str(tmp_3mf_multiplate))
    assert len(bf.plates) == 2

    out = tmp_path / "roundtrip_multi.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert len(bf2.plates) == 2
    assert bf2.plate(1).gcode == bf.plate(1).gcode
    assert bf2.plate(2).gcode == bf.plate(2).gcode


def test_roundtrip_preserves_extra_entries(tmp_3mf: Path, tmp_path: Path):
    """Non-plate entries like [Content_Types].xml survive a roundtrip."""
    bf = BambuFile.open(str(tmp_3mf))
    out = tmp_path / "roundtrip_extras.gcode.3mf"
    bf.save(str(out))

    with zipfile.ZipFile(out, "r") as zf:
        names = zf.namelist()
        assert "[Content_Types].xml" in names
        assert "_rels/.rels" in names
        assert "3D/3dmodel.model" in names


def test_roundtrip_md5_matches(tmp_3mf: Path, tmp_path: Path):
    """MD5 in the archive matches the actual gcode content after roundtrip."""
    bf = BambuFile.open(str(tmp_3mf))
    out = tmp_path / "roundtrip_md5.gcode.3mf"
    bf.save(str(out))

    with zipfile.ZipFile(out, "r") as zf:
        gcode_bytes = zf.read("Metadata/plate_1.gcode")
        md5_bytes = zf.read("Metadata/plate_1.gcode.md5")
        expected_md5 = hashlib.md5(gcode_bytes).hexdigest()
        assert md5_bytes.decode("utf-8") == expected_md5


def test_roundtrip_thumbnail_passthrough(tmp_3mf: Path, tmp_path: Path):
    """Thumbnails pass through a roundtrip unchanged."""
    bf = BambuFile.open(str(tmp_3mf))
    original_thumb = bf.plate(1).thumbnail_png
    assert original_thumb is not None

    out = tmp_path / "roundtrip_thumb.gcode.3mf"
    bf.save(str(out))

    bf2 = BambuFile.open(str(out))
    assert bf2.plate(1).thumbnail_png == original_thumb
