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

"""RPC methods for variables."""
from warnings import warn

from ansys.motorcad.core.datastore import Datastore


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

    def get_array_variable_list(self, array_name):
        """Get the full array of a Motor-CAD array variable as a list.

        Parameters
        ----------
        array_name : str
            Name of the array

        Returns
        -------
        list of int|float|str|bool
            List of values of the Motor-CAD variable
        """
        # Get the array variable as a single string, delimited by colon. Split this string into a
        # list.
        value_string = self.get_variable(array_name)
        value_string = value_string.split(":")
        # Get the first variable of the array, and determine the type of the variable.
        value_0 = self.get_array_variable(array_name, 0)
        value_type = str
        if isinstance(value_0, int):
            value_type = int
        if isinstance(value_0, float):
            value_type = float
        if isinstance(value_0, bool):
            value_type = bool
        # Create a list and append each value to the list. Convert the value if the value_type is
        # not string.
        values = []
        if value_type is not None:
            for value in value_string:
                values.append(value_type(value))
        return values

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

    def set_array_variable_list(self, array_name, variable_list):
        """Set the full array of a Motor-CAD array variable as a list.

        If a single value is provided, every element of the array will be set to this value.

        Parameters
        ----------
        array_name : str
            Name of the array
        variable_list : list of int|float|str|bool
            Values to set the variables to.
        """
        # Get the original array variable to determine the length of the array
        values_orig = self.get_variable(array_name)
        values_orig = values_orig.split(":")

        # If the provided list of variables is longer than the original array, raise an error.
        if isinstance(variable_list, list) and len(variable_list) > len(values_orig):
            raise ValueError(
                f"The array variable {array_name} has length = {len(values_orig)}. The "
                f"variable_list provided has length = "
                f"{len(variable_list)}. Please provide a list of {len(values_orig)} "
                f"values."
            )
        # If a single value is provided, set all values of the array to the same value. Use the
        # original length of the array to determine the number of values to add.
        elif not isinstance(variable_list, list):
            single_value = True
            num_values = len(values_orig)
        # If the provided list of variables is shorter than the original array, set the first n
        # values of the array to the provided values, where n is the length of the provided list.
        # Use the length of the provided list to determine the number of values to add.
        else:
            single_value = False
            num_values = len(variable_list)

        # Loop through all elements of the array, setting the value for each index
        for i in range(num_values):
            if not single_value:
                value = variable_list[i]
            else:
                value = variable_list
            self.set_array_variable(array_name, i, value)

    def get_file_name(self):
        """Get current .mot file name and path.

        Returns
        -------
        str
            Current .mot file path and name
        """
        if self.connection.check_version_at_least("2025.0"):
            method = "GetMotorCADFileName"
            if self.connection.send_and_receive(method) == "":
                warn("No file has been loaded in this MotorCAD instance")
                return None
            else:
                return self.connection.send_and_receive(method)
        else:
            warn(
                "GetMotorCADFileName not available in Motor-CAD "
                + self.connection.program_version
                + ". Returning value of CurrentMotFilePath_MotorLAB"
            )
            if self.get_variable("CurrentMotFilePath_MotorLAB") == "":
                warn("No file has been loaded in this MotorCAD instance")
                return None
            else:
                return self.get_variable("CurrentMotFilePath_MotorLAB")

    def get_datastore(self):
        """Get the whole database from Motor-CAD.

        Returns
        -------
        ansys.motorcad.core.datastore.Datastore
        """
        self.connection.ensure_version_at_least("2026.0")
        method = "GetDataStore"
        datastore_json = self.connection.send_and_receive(method)
        return Datastore.from_json(datastore_json)
