"""Module containing MotorCAD class for connecting to Motor-CAD exe."""


from ansys.motorcad.core.rpc_client_core import MotorCADCore
from ansys.motorcad.core.rpc_methods_core_old import _RpcMethodsCoreOld
from ansys.motorcad.core.rpc_methods_utility import _RpcMethodsUtility


class MotorCAD(_RpcMethodsCoreOld, _RpcMethodsUtility):
    """Standard MotorCAD object."""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
    ):
        """Connect to existing Motor-CAD instance or open a new one.

        Parameters
        ----------
        port : int
            Port to use for communication
        open_new_instance: Boolean
            Open a new instance or try to connect to existing instance
        enable_exceptions : Boolean
            Show Motor-CAD communication errors as Python exceptions
        enable_success_variable: Boolean
                Motor-CAD methods return a success variable (first object in tuple)

        Returns
        -------
        MotorCAD object
        """
        self.connection = MotorCADCore(
            port, open_new_instance, enable_exceptions, enable_success_variable
        )

        _RpcMethodsCoreOld.__init__(self, mc_connection=self.connection)
        _RpcMethodsUtility.__init__(self, mc_connection=self.connection)


class MotorCADCompatibility(_RpcMethodsCoreOld, _RpcMethodsUtility):
    """Create a MotorCAD object that behaves the same as old ActiveX methods.

    Can be used for old scripts that were written for ActiveX
    """

    def __init__(self):
        """Create MotorCADCompatibility object."""
        port = -1
        open_new_instance = False
        enable_exceptions = False
        enable_success_variable = True

        self.connection = MotorCADCore(
            port,
            open_new_instance,
            enable_exceptions,
            enable_success_variable,
            compatibility_mode=True,
        )

        _RpcMethodsCoreOld.__init__(self, mc_connection=self.connection)
        _RpcMethodsUtility.__init__(self, mc_connection=self.connection)
