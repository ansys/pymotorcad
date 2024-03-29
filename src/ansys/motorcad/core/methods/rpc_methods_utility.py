"""This unit contains functions that are inherited by _MotorCADCore.

They only have access to methods within _MotorCADConnection and are visible to the user at
the first level of the class. For example, ``MotorCAD.is_open``.
"""
import psutil

from ansys.motorcad.core.rpc_client_core import MotorCADError


class _RpcMethodsUtility:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def is_open(self):
        """Check if the Motor-CAD executable file is running.

        Returns
        -------
        bool
            ``True`` if the Motor-CAD executable file is still running,
            ``False`` if this file is not running.
        """
        if self.connection.pid != -1:
            return psutil.pid_exists(self.connection.pid)
        else:
            raise MotorCADError("Motor-CAD process is not created.")

    def is_file_loaded(self):
        """Check if a Motor-CAD file is loaded.

        Returns
        -------
        bool
            ``True`` if a Motor-CAD file is loaded,
            ``False`` if no file is loaded in Motor-CAD.
        """
        return not self.get_variable("CurrentMotFilePath_MotorLAB")
