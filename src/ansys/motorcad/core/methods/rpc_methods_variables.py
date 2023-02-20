"""RPC methods for variables."""


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
            Value of the Motor-CAD variable to set.
        """
        method = "SetArrayVariable_2d"
        params = [array_name, array_index1, array_index2, {"variant": new_value}]
        return self.connection.send_and_receive(method, params)

    def restore_compatibility_settings(self):
        """Restore the model compatibility settings to the default values (to use the latest methods)."""
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
            Position variable in array

        Returns
        -------
        int|float|str|bool
            Value of Motor-CAD variable
        """
        method = "GetArrayVariable"
        params = [array_name, array_index]
        return self.connection.send_and_receive(method, params)

    def set_variable(self, variable_name, variable_value):
        """Set a Motor-CAD variable.

        Parameters
        ----------
        variable_name : str
            Name of variable
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetVariable"
        params = [variable_name, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    def set_array_variable(self, array_name, array_index, variable_value):
        """Set a Motor-CAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
        array_index : int
            Index in the array.
        variable_value : int|float|str|bool
            Value to set the variable to.
        """
        method = "SetArrayVariable"
        params = [array_name, array_index, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)
