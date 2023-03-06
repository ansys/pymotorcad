"""PyMotorCAD is a Python RPC-JSON interface for Motor-CAD."""

__version__ = "0.2.dev0"

import ansys.motorcad.core.geometry
from ansys.motorcad.core.motorcad_methods import MotorCAD, MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import (
    MotorCADError,
    set_default_instance,
    set_motorcad_exe,
    set_server_ip,
    how_many_open,
    IS_REMOTE_MACHINE,
    RemoteMachine,
    add_remote_machine
)
