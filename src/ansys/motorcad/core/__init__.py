"""motorcad.core."""

__version__ = "0.1.dev2"

import ansys.motorcad.core.geometry
from ansys.motorcad.core.motorcad_methods import MotorCAD, MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import (
    MotorCADError,
    set_default_instance,
    set_motorcad_exe,
    set_server_ip,
)
