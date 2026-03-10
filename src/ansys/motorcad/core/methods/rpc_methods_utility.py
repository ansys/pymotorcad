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
