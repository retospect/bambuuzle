"""ZIP archive read/write helpers for Bambu 3MF files."""

from __future__ import annotations

import re
import zipfile


def read_archive(path: str) -> dict[str, bytes]:
    """Read all entries from a ZIP archive into memory."""
    entries: dict[str, bytes] = {}
    with zipfile.ZipFile(path, "r") as zf:
        for item in zf.infolist():
            if not item.is_dir():
                entries[item.filename] = zf.read(item.filename)
    return entries


def write_archive(path: str, entries: dict[str, bytes]) -> None:
    """Write entries to a new ZIP archive with DEFLATE compression."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, data in entries.items():
            zf.writestr(filename, data)


def detect_plates(entries: dict[str, bytes]) -> list[int]:
    """Detect plate numbers from archive entries."""
    plates: set[int] = set()
    pattern = re.compile(r"Metadata/plate_(\d+)\.gcode$")
    for filename in entries:
        m = pattern.match(filename)
        if m:
            plates.add(int(m.group(1)))
    return sorted(plates)
