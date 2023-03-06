"""Module containing the ``MotorCAD`` class for connecting to the Motor-CAD exe."""

from warnings import warn

from ansys.motorcad.core.methods.rpc_methods_utility import _RpcMethodsUtility
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection
from ansys.motorcad.core.rpc_methods_core_old import _RpcMethodsCore, _RpcMethodsCoreOld


class _MotorCADCore(_RpcMethodsCore, _RpcMethodsUtility):
    """Provides the RPC client and core API methods."""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
        reuse_parallel_instances=False,
        use_remote_machine=False
    ):
        self.connection = _MotorCADConnection(
            port,
            open_new_instance,
            enable_exceptions,
            enable_success_variable,
            reuse_parallel_instances,
            use_remote_machine
        )

        _RpcMethodsCore.__init__(self, mc_connection=self.connection)
        _RpcMethodsUtility.__init__(self, mc_connection=self.connection)


class MotorCAD(_MotorCADCore):
    """Connect to an existing Motor-CAD instance or open a new instance.

    Parameters
    ----------
    port : int, default: -1
        Port to use for communication.
    open_new_instance : Boolean, default: True
        Open a new instance or try to connect to an existing instance.
    enable_exceptions : Boolean, default: True
        Whether to show Motor-CAD communication errors as Python exceptions.
    enable_success_variable : Boolean, default: False
        Whether Motor-CAD methods return a success variable (first object in tuple).
    reuse_parallel_instances : Boolean, default: False
        Whether to reuse MotorCAD instances when running in parallel. You must
        free instances after use.

    Returns
    -------
    MotorCAD object.
    """

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
        reuse_parallel_instances=False,
        use_remote_machine=False
    ):
        """Initiate MotorCAD object."""
        _MotorCADCore.__init__(
            self,
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
            reuse_parallel_instances=reuse_parallel_instances,
            use_remote_machine=use_remote_machine
        )


class MotorCADCompatibility(_RpcMethodsCoreOld):
    """Create a MotorCAD object that behaves the same as old ActiveX methods.

    This class contains the old ``camelCase`` function names.
    It can be used to run old scripts that were written for ActiveX.
    """

    warn(
        "This class uses old Motor-CAD function names, which are in ``camelCase``. "
        "For new scripts, use MotorCAD object.",
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
