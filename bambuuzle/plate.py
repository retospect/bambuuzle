"""Plate data model for Bambu 3MF files."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class Plate:
    """Represents a single plate in a Bambu .gcode.3mf file."""

    number: int
    gcode: str = ""
    metadata: dict = field(default_factory=dict)
    thumbnail_png: bytes | None = None
    thumbnail_small_png: bytes | None = None

    @property
    def md5(self) -> str:
        """Compute MD5 hex digest of the gcode bytes."""
        return hashlib.md5(self.gcode.encode("utf-8")).hexdigest()

    @property
    def gcode_path(self) -> str:
        return f"Metadata/plate_{self.number}.gcode"

    @property
    def md5_path(self) -> str:
        return f"Metadata/plate_{self.number}.gcode.md5"

    @property
    def json_path(self) -> str:
        return f"Metadata/plate_{self.number}.json"

    @property
    def thumbnail_path(self) -> str:
        return f"Metadata/plate_{self.number}.png"

    @property
    def thumbnail_small_path(self) -> str:
        return f"Metadata/plate_{self.number}_small.png"
