"""Minimal templates for creating Bambu 3MF files from scratch."""

CONTENT_TYPES_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType=\
"application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType=\
"application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Default Extension="gcode" ContentType="text/x.gcode"/>
</Types>"""

RELS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns=\
"http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" \
Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""

MODEL_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources/>
  <build/>
</model>"""


def default_plate_metadata(plate_number: int) -> dict:
    """Return minimal plate metadata dict for a new plate."""
    return {
        "plate_index": plate_number - 1,
        "prediction": 0,
        "weight": 0.0,
        "outside": False,
        "bed_type": "auto",
    }
