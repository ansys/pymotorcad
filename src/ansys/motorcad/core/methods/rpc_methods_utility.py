"""This unit contains functions which are inherited by _MotorCADCore.

They only have access to functions within _MotorCADConnection and are visible to the user at
the first level of the class e.g. MotorCAD.is_open
"""
import psutil

from ansys.motorcad.core.rpc_client_core import MotorCADError


class _RpcMethodsUtility:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def is_open(self):
        """Check if Motor-CAD exe is still running.

        Returns
        -------
        boolean
            True if Motor-CAD exe is running.
        """
        if self.connection.pid != -1:
            return psutil.pid_exists(self.connection.pid)
        else:
            raise MotorCADError("Motor-CAD process not created")
