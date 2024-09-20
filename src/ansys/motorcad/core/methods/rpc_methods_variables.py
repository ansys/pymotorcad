# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""RPC methods for variables."""
from logging import raiseExceptions
from warnings import warn

class _RpcMethodsVariables:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def get_array_variable_2d(self, array_name, array_index1, array_index2):
        """Get a value from a 2D array at element ``[array_index1,array_index2]``.

        Parameters
        ----------
        array_name : str
            Name of the array.
        array_index1 : int
            First index of the array.
        array_index2 : int
            Second index of the array.

        Returns
        -------
        int|float|str|bool
            Value of the Motor-CAD variable.
        """
        method = "GetArrayVariable_2d"
        params = [array_name, array_index1, array_index2]
        return self.connection.send_and_receive(method, params)

    def set_array_variable_2d(self, array_name, array_index1, array_index2, new_value):
        """Set the value of a 2D array at element ``[array_index1,array_index2]``.

        Parameters
        ----------
        array_name : str
            Name of the array.
        array_index1 : int
            First index of the array.
        array_index2 : int
            Second index of the array.
        new_value : int|float|str|bool
            Value to set the Motor-CAD variable to.
        """
        method = "SetArrayVariable_2d"
        params = [array_name, array_index1, array_index2, {"variant": new_value}]
        return self.connection.send_and_receive(method, params)

    def restore_compatibility_settings(self):
        """Restore model compatibility settings to default values to use the latest methods."""
        method = "RestoreCompatibilitySettings"
        return self.connection.send_and_receive(method)

    def get_variable(self, variable_name):
        """Get a Motor-CAD variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.

        Returns
        -------
        int|float|str|bool
            Value of the Motor-CAD variable.
        """
        method = "GetVariable"
        params = [variable_name]
        return self.connection.send_and_receive(method, params)

    def get_array_variable(self, array_name, array_index):
        """Get a Motor-CAD array variable.

        Parameters
        ----------
        array_name : str
            Name of the array.
        array_index : int
            Position variable in the array.

        Returns
        -------
        int|float|str|bool
            Value of the Motor-CAD variable
        """
        method = "GetArrayVariable"
        params = [array_name, array_index]
        return self.connection.send_and_receive(method, params)

    def set_variable(self, variable_name, variable_value):
        """Set a Motor-CAD variable.

        Parameters
        ----------
        variable_name : str
            Name of the variable.
        variable_value : int|float|str|bool
            Value to set the variable to.
        """
        method = "SetVariable"
        params = [variable_name, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    def set_array_variable(self, array_name, array_index, variable_value):
        """Set a Motor-CAD array variable.

        Parameters
        ----------
        array_name : str
            Name of the array.
        array_index : int
            Index in the array.
        variable_value : int|float|str|bool
            Value to set the variable to.
        """
        method = "SetArrayVariable"
        params = [array_name, array_index, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    def get_file_name(self):
        """Get current .mot file name and path.

        Returns
        -------
        str
            Current .mot file path and name
        """
        method = "GetMotorCADFileName"
        if self.connection.send_and_receive(method) == "":
            warn("No file has been loaded in this MotorCAD instance")
            return None
        else:
            return self.connection.send_and_receive(method)



