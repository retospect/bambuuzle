"""bambuuzle — Extract and re-insert gcode from Bambu Lab .gcode.3mf files."""

from .bambu_file import BambuFile
from .plate import Plate

__version__ = "0.1.0"
__all__ = ["BambuFile", "Plate", "__version__"]
