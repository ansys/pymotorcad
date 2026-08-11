# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        keep_instance_open=False,
        url="",
        timeout=2,
        use_blackbox_licence=None,
        use_new_license_type=None,
        show_gui=None,
        full_headless_beta=False,
    ):
        self.connection = _MotorCADConnection(
            port,
            open_new_instance,
            enable_exceptions,
            enable_success_variable,
            reuse_parallel_instances,
            keep_instance_open,
            url=url,
            timeout=timeout,
            use_blackbox_licence=use_blackbox_licence,
            use_new_license_type=use_new_license_type,
            show_gui=show_gui,
            full_headless_beta=full_headless_beta,
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
        Whether to reuse Motor-CAD instances when running in parallel. You must
        free instances after use.
    keep_instance_open : Boolean, default: False
        Whether to keep the Motor-CAD instance open after the instance becomes free.
    url: string, default = ""
        Full url for Motor-CAD connection. Assumes we are connecting to existing instance.
    use_blackbox_licence : bool, default: None
        Ask Motor-CAD to consume blackbox licence. If set to None, existing Motor-CAD
        behaviour will be used. True enables the blackbox licence, False disables it.
    use_new_license_type : bool, default: None
        Select the licence type for Motor-CAD. True uses the new licence type, False uses the
        original. If None, the Motor-CAD default behaviour is used.
    show_gui : bool, default: None
        Whether to show the Motor-CAD GUI. True shows the GUI, False hides it.
        If None, the Motor-CAD default behaviour is used.
    full_headless_beta : bool, default: False
        Launch Motor-CAD using the MotorCAD_Console executable instead of the standard one.
        This is a beta setting and will be incorporated into ``show_gui`` in a future release.

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
        keep_instance_open=False,
        url="",
        use_blackbox_licence=None,
        use_new_license_type=None,
        show_gui=None,
        full_headless_beta=False,
    ):
        """Initiate MotorCAD object."""
        _MotorCADCore.__init__(
            self,
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
            reuse_parallel_instances=reuse_parallel_instances,
            keep_instance_open=keep_instance_open,
            url=url,
            use_blackbox_licence=use_blackbox_licence,
            use_new_license_type=use_new_license_type,
            show_gui=show_gui,
            full_headless_beta=full_headless_beta,
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
        keep_instance_open=False,
    ):
        """Create MotorCADCompatibility object."""
        self.connection = _MotorCADConnection(
            port=port,
            open_new_instance=open_new_instance,
            enable_exceptions=enable_exceptions,
            enable_success_variable=enable_success_variable,
            reuse_parallel_instances=reuse_parallel_instances,
            keep_instance_open=keep_instance_open,
            compatibility_mode=True,
        )

        _RpcMethodsCoreOld.__init__(self, self.connection)
