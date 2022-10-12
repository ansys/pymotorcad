"""motorcad.core."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))

from ansys.motorcad.core.MotorCAD_Methods import MotorCAD, MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import (
    MotorCADError,
    set_default_instance,
    set_motorcad_exe,
    set_server_ip,
)
