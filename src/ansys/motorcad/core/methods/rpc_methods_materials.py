# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""RPC methods for materials."""


class _RpcMethodsMaterials:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_fluid(self, cooling_type, fluid):
        """Set the fluid for a cooling type.

        Parameters
        ----------
        cooling_type : str
            Type of the cooling. Options are ``"InternalFluid"``,
            ``"ExternalFluid"``, ``"ShaftSGFluid"``, ``"RotorWJFluid"``,
            ``"SlotWJFluid"``, ``"HousingWJFluid"``, ``"WetRotorFluid"``,
            ``"SprayCoolingFluid"``, ``"TVentFluid"``,
            ``"Spray_RadialHousing_Fluid"``, ``"Spray_RadialRotor_Fluid"``,
            ``"Spray_RadialHousing_Fluid_F"``, ``"Spray_RadialHousing_Fluid_R"``,
            ``"Spray_RadialRotor_Fluid_F"`` and ``"Spray_RadialRotor_Fluid_R"``.
        fluid :
        """
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.connection.send_and_receive(method, params)

    def set_component_material(self, component_name, material_name):
        """Set the solid material properties of the component from the materials database.

        Parameters
        ----------
        component_name : str
            Component name. In Motor-CAD, you can select **Input Data -> Materials**
            and view the **Component** column to see component names.
        material_name : str
            Name of the solid material.
        """
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.connection.send_and_receive(method, params)

    def get_component_material(self, component_name):
        """Get the solid material name of the component.

        Parameters
        ----------
        component_name : str
            Component name. In Motor-CAD, you can select **Input Data -> Materials**
            and view the **Component** column to see component names.
        """
        method = "GetComponentMaterial"
        params = [component_name]
        return self.connection.send_and_receive(method, params)

    def import_solid_material(self, file_name, material_name):
        """Import the solid material from the materials database.

        Parameters
        ----------
        file_name : str
            Name of the materials database.
        material_name : str
            Name of the solid material.
        """
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def export_solid_material(self, file_name, material_name):
        """Export the solid material to the materials database.

        Parameters
        ----------
        file_name : str
            Name of the materials database.
        material_name : str
            Name of the solid material.
        """
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def delete_solid_material(self, material_name):
        """Delete the solid material from the materials database.

        Parameters
        ----------
        material_name : str
            Name of the solid material.
        """
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_iron_loss_coefficients(self, material_name):
        """Calculate and return the iron loss coefficients for the solid material.

        Parameters
        ----------
        material_name : str
            Name of the solid material.
        """
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_iron_loss_coefficients(self, material_name):
        """Save the calculated iron loss coefficients to the materials database.

        Parameters
        ----------
        material_name : str
            Name of the solid material.
        """
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_magnet_parameters(self, material_name):
        """Calculate parameters for the nonlinear demagnetization model.

        Parameters
        ----------
        material_name : str
            Name of the solid material.
        """
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_magnet_parameters(self, material_name):
        """Save the calculated magnet parameters of the solid material to the materials database.

        Parameters
        ----------
        material_name : str
            Name of the solid material.
        """
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def _get_solid_database(self):
        """BETA - get the solid database from Motor-CAD."""
        method = "GetSolidDatabase"
        return self.connection.send_and_receive(method)

    def select_material_database(self, database_file_path, set_as_default):
        """Select and load a material database to be used in Motor-CAD.

        Parameters
        __________
        database_file_path : str
            File path pointing to the material database (.mdb) to be used in Motor-CAD.

        set_as_default : bool
            Whether specified database should be used as the default solids database.
        """
        method = "SetSolidDatabase"
        params = [database_file_path, set_as_default]
        return self.connection.send_and_receive(method, params)
