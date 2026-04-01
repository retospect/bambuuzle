"""Main BambuFile class for reading, modifying, and creating .gcode.3mf files."""

from __future__ import annotations

import json
from collections.abc import Callable

from .archive import detect_plates, read_archive, write_archive
from .plate import Plate
from .templates import (
    CONTENT_TYPES_XML,
    MODEL_XML,
    RELS_XML,
    default_plate_metadata,
)


class BambuFile:
    """Represents a Bambu .gcode.3mf file.

    Usage::

        # Read and modify
        bf = BambuFile.open("print.gcode.3mf")
        bf.plate(1).gcode = modified_gcode
        bf.save("modified.gcode.3mf")

        # Create from scratch
        bf = BambuFile()
        bf.add_plate(gcode="G28\\nG1 X100 Y100 F3000\\n")
        bf.save("new.gcode.3mf")
    """

    def __init__(self) -> None:
        self.plates: list[Plate] = []
        self._extra_entries: dict[str, bytes] = {}

    @classmethod
    def open(cls, path: str) -> BambuFile:
        """Open an existing .gcode.3mf file."""
        bf = cls()
        entries = read_archive(path)
        plate_numbers = detect_plates(entries)

        plate_paths: set[str] = set()
        for n in plate_numbers:
            plate = Plate(number=n)

            gcode_data = entries.get(plate.gcode_path)
            if gcode_data is not None:
                plate.gcode = gcode_data.decode("utf-8")
                plate_paths.add(plate.gcode_path)

            md5_data = entries.get(plate.md5_path)
            if md5_data is not None:
                plate_paths.add(plate.md5_path)

            json_data = entries.get(plate.json_path)
            if json_data is not None:
                plate.metadata = json.loads(json_data.decode("utf-8"))
                plate_paths.add(plate.json_path)

            thumb_data = entries.get(plate.thumbnail_path)
            if thumb_data is not None:
                plate.thumbnail_png = thumb_data
                plate_paths.add(plate.thumbnail_path)

            thumb_small = entries.get(plate.thumbnail_small_path)
            if thumb_small is not None:
                plate.thumbnail_small_png = thumb_small
                plate_paths.add(plate.thumbnail_small_path)

            bf.plates.append(plate)

        for filename, data in entries.items():
            if filename not in plate_paths:
                bf._extra_entries[filename] = data

        return bf

    def plate(self, number: int) -> Plate:
        """Get a plate by its 1-based number."""
        for p in self.plates:
            if p.number == number:
                return p
        raise KeyError(
            f"No plate {number}. Available: {[p.number for p in self.plates]}"
        )

    def add_plate(
        self,
        gcode: str,
        number: int | None = None,
        metadata: dict | None = None,
    ) -> Plate:
        """Add a new plate with the given gcode."""
        if number is None:
            number = max((p.number for p in self.plates), default=0) + 1
        plate = Plate(
            number=number,
            gcode=gcode,
            metadata=metadata or default_plate_metadata(number),
        )
        self.plates.append(plate)
        return plate

    def save(self, path: str) -> None:
        """Save to a .gcode.3mf file. Rebuilds ZIP, recomputes all MD5s."""
        entries: dict[str, bytes] = {}

        # Scaffold entries for from-scratch creation
        if "[Content_Types].xml" not in self._extra_entries:
            entries["[Content_Types].xml"] = CONTENT_TYPES_XML.encode("utf-8")
        if "_rels/.rels" not in self._extra_entries:
            entries["_rels/.rels"] = RELS_XML.encode("utf-8")
        if "3D/3dmodel.model" not in self._extra_entries:
            entries["3D/3dmodel.model"] = MODEL_XML.encode("utf-8")

        # Preserve non-plate entries from original file
        entries.update(self._extra_entries)

        # Write plate entries with fresh MD5s
        for plate in self.plates:
            gcode_bytes = plate.gcode.encode("utf-8")
            entries[plate.gcode_path] = gcode_bytes
            entries[plate.md5_path] = plate.md5.encode("utf-8")
            entries[plate.json_path] = json.dumps(
                plate.metadata, indent=2
            ).encode("utf-8")
            if plate.thumbnail_png is not None:
                entries[plate.thumbnail_path] = plate.thumbnail_png
            if plate.thumbnail_small_png is not None:
                entries[plate.thumbnail_small_path] = plate.thumbnail_small_png

        write_archive(path, entries)


def transform(
    input_path: str,
    output_path: str,
    transform_fn: Callable[[str], str],
    plate_number: int = 1,
) -> None:
    """Convenience: open a file, transform one plate's gcode, save.

    Args:
        input_path: Path to input .gcode.3mf
        output_path: Path to write modified .gcode.3mf
        transform_fn: Function that takes gcode string and returns modified gcode
        plate_number: Which plate to transform (default: 1)
    """
    bf = BambuFile.open(input_path)
    plate = bf.plate(plate_number)
    plate.gcode = transform_fn(plate.gcode)
    bf.save(output_path)
