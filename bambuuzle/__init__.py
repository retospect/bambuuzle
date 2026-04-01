"""bambuuzle — Extract and re-insert gcode from Bambu Lab .gcode.3mf files."""

from importlib.metadata import version

__version__ = version("bambuuzle")

from .bambu_file import BambuFile
from .plate import Plate

__all__ = ["BambuFile", "Plate", "__version__"]
