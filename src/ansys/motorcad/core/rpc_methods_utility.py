"""rpc_methods_utility."""
import psutil

from ansys.motorcad.core.rpc_client_core import MotorCADError


class _RpcMethodsUtility:
    def __init__(self, mc_connection):
        self.mc_connection = mc_connection

    def is_open(self):
        """Check if Motor-CAD exe is still running.

        Returns
        -------
        boolean
            True if Motor-CAD exe is running.
        """
        if self._pid != -1:
            return psutil.pid_exists(self._pid)
        else:
            raise MotorCADError("Motor-CAD process not created")
