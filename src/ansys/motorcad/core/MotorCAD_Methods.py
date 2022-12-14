"""Module containing MotorCAD class for connecting to Motor-CAD exe."""

from warnings import warn

from ansys.motorcad.core.methods.rpc_methods_utility import _RpcMethodsUtility
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection
from ansys.motorcad.core.rpc_methods_core_old import _RpcMethodsCore, _RpcMethodsCoreOld


class _MotorCADCore(_RpcMethodsCore, _RpcMethodsUtility):
    """Core class contains RPC client and core API functions."""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
        reuse_parallel_instances=False,
    ):
        self.connection = _MotorCADConnection(
            port,
            open_new_instance,
            enable_exceptions,
            enable_success_variable,
            reuse_parallel_instances,
        )

        _RpcMethodsCore.__init__(self, mc_connection=self.connection)
        _RpcMethodsUtility.__init__(self, mc_connection=self.connection)


class MotorCAD(_MotorCADCore):
    """Connect to existing Motor-CAD instance or open a new one.

    Parameters
    ----------
    port : int, optional
        Port to use for communication
    open_new_instance : Boolean, optional
        Open a new instance or try to connect to existing instance
    enable_exceptions : Boolean, optional
        Show Motor-CAD communication errors as Python exceptions
    enable_success_variable : Boolean, optional
        Motor-CAD methods return a success variable (first object in tuple)
    reuse_parallel_instances : Boolean, optional
        Reuse MotorCAD instances when running in parallel. Need to free instances after use.

    Returns
    -------
    MotorCAD object
    """

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
        reuse_parallel_instances=False,
    ):
        """Initiate MotorCAD object."""
        _MotorCADCore.__init__(
            self,
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
            reuse_parallel_instances=reuse_parallel_instances,
        )


class MotorCADCompatibility(_RpcMethodsCoreOld):
    """Create a MotorCAD object that behaves the same as old ActiveX methods.

    Contains old CamelCase function names.
    Can be used for old scripts that were written for ActiveX
    """

    warn(
        "This class uses old CamelCase Motor-CAD function names. "
        "Please use MotorCAD object for new scripts",
        DeprecationWarning,
    )

    def __init__(
        self,
        port=-1,
        open_new_instance=False,
        enable_exceptions=False,
        enable_success_variable=True,
        reuse_parallel_instances=False,
    ):
        """Create MotorCADCompatibility object."""
        self.connection = _MotorCADConnection(
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
            reuse_parallel_instances=reuse_parallel_instances,
            compatibility_mode=True,
        )

        _RpcMethodsCoreOld.__init__(self, self.connection)
