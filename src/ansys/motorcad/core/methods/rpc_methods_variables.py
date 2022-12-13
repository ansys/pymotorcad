"""RPC methods for variables."""


class _RpcMethodsVariables:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def get_array_variable_2d(self, array_name, array_index1, array_index2):
        """Get value from 2D array at element [array_index1,array_index2].

        Parameters
        ----------
        array_name : str
            Name of array
        array_index1 : int
            First index of array
        array_index2 : int
            Second index of array

        Returns
        -------
        int|float|str|bool
            Value of Motor-CAD variable
        """
        method = "GetArrayVariable_2d"
        params = [array_name, array_index1, array_index2]
        return self.connection.send_and_receive(method, params)

    def set_array_variable_2d(self, array_name, array_index1, array_index2, new_value):
        """Set value of 2D array at element [array_index1,array_index2].

        Parameters
        ----------
        array_name : str
            Name of array
        array_index1 : int
            First index of array
        array_index2 : int
            Second index of array
        new_value : int|float|str|bool
            Value of Motor-CAD variable to be set
        """
        method = "SetArrayVariable_2d"
        params = [array_name, array_index1, array_index2, {"variant": new_value}]
        return self.connection.send_and_receive(method, params)

    def restore_compatibility_settings(self):
        """Restores the model compatibility settings to default values (to use latest methods)."""
        method = "RestoreCompatibilitySettings"
        return self.connection.send_and_receive(method)

    def get_variable(self, variable_name):
        """Get a Motor-CAD variable.

        Parameters
        ----------
        variable_name : str
            Name of variable

        Returns
        -------
        int|float|str|bool
            Value of Motor-CAD variable
        """
        method = "GetVariable"
        params = [variable_name]
        return self.connection.send_and_receive(method, params)

    def get_array_variable(self, array_name, array_index):
        """Get a Motor-CAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
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
            Position in array
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetArrayVariable"
        params = [array_name, array_index, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Materials ------------------------------------

    def set_fluid(self, cooling_type, fluid):
        """Set fluid for specified cooling type.

        Cooling types: InternalFluid, ExternalFluid, ShaftSGFluid, RotorWJFluid, SlotWJFluid,
        HousingWJFluid, WetRotorFluid, SprayCoolingFluid, Spray_RadialHousing_Fluid, TVentFluid.
        """
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.connection.send_and_receive(method, params)

    def set_component_material(self, component_name, material_name):
        """Set the solid material properties of the named component from the materials database.

        Component names are found under Input Data -> Materials (Component column).
        """
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.connection.send_and_receive(method, params)

    def get_component_material(self, component_name):
        """Get the current solid material name of the named component.

        Component names are found under Input Data -> Materials (Component column).
        """
        method = "GetComponentMaterial"
        params = [component_name]
        return self.connection.send_and_receive(method, params)

    def import_solid_material(self, file_name, material_name):
        """Import the solid material from the materials database."""
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def export_solid_material(self, file_name, material_name):
        """Export the solid material to the materials database."""
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def delete_solid_material(self, material_name):
        """Delete the solid material from the materials database."""
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_iron_loss_coefficients(self, material_name):
        """Calculate and return iron loss coefficients for the specified material."""
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_iron_loss_coefficients(self, material_name):
        """Save the calculated iron loss coefficients to the solids database."""
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_magnet_parameters(self, material_name):
        """Calculate parameters for nonlinear demagnetisation model."""
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_magnet_parameters(self, material_name):
        """Save the calculated magnet parameters of the selected material to the solids database."""
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)
