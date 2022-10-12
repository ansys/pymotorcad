"""Module containing MotorCAD class for connecting to Motor-CAD exe."""


from ansys.motorcad.core.rpc_client_core import _MotorCADConnection
from ansys.motorcad.core.rpc_methods_core_old import _RpcMethodsCoreOld
from ansys.motorcad.core.rpc_methods_utility import _RpcMethodsUtility


class _MotorCADCore(_RpcMethodsCoreOld, _RpcMethodsUtility):
    """Core class contains RPC client and core API functions."""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
    ):
        self.connection = _MotorCADConnection(
            port, open_new_instance, enable_exceptions, enable_success_variable
        )

        _RpcMethodsCoreOld.__init__(self, mc_connection=self.connection)
        _RpcMethodsUtility.__init__(self, mc_connection=self.connection)


class MotorCAD(_MotorCADCore):
    """Standard MotorCAD object for users."""

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
        _MotorCADCore.__init__(
            self,
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
        )


class MotorCADCompatibility(_MotorCADCore):
    """Create a MotorCAD object that behaves the same as old ActiveX methods.

    Can be used for old scripts that were written for ActiveX
    """

    def __init__(self):
        """Create MotorCADCompatibility object."""
        port = -1
        open_new_instance = False
        enable_exceptions = False
        enable_success_variable = True

        _MotorCADCore.__init__(
            self,
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
        )
