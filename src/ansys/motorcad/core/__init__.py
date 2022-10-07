"""motorcad.core."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

from ansys.motorcad.core.MotorCAD_Methods import *
