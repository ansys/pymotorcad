"""PyMotorCAD is a Python RPC-JSON interface for Motor-CAD."""
try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

import ansys.motorcad.core.geometry
from ansys.motorcad.core.motorcad_methods import MotorCAD, MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import (
    MotorCADError,
    MotorCADWarning,
    is_running_in_internal_scripting,
    set_default_instance,
    set_motorcad_exe,
    set_server_ip,
)

# Read from the pyproject.toml
# major, minor, patch
__version__ = importlib_metadata.version("ansys-motorcad-core")
