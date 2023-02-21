"""RPC methods for materials."""


class _RpcMethodsMaterials:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_fluid(self, cooling_type, fluid):
        """Set the fluid for a cooling type.

        Parameters
        ----------
        cooling_type: str
        Type of the cooling. Options are ``"InternalFluid"``, ``"ExternalFluid"``,
        ``"ShaftSGFluid"``, ``"RotorWJFluid"``, ``"SlotWJFluid"``, ``"HousingWJFluid"``,
        ``"WetRotorFluid"``, ``"SprayCoolingFluid"``, ``"Spray_RadialHousing_Fluid"``,
        and ``"TVentFluid"``.
        """
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.connection.send_and_receive(method, params)

    def set_component_material(self, component_name, material_name):
        """Set the solid material properties of the component from the materials database.

        Parameters
        ----------
        component_name: str
            Component name. In Motor-CAD, you can select **Input Data -> Materials**
            and view the **Component** column to see component names.
        material_name: str
            Name of the solid material.
        """
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.connection.send_and_receive(method, params)

    def get_component_material(self, component_name):
        """Get the solid material name of the component.

        Parameters
        ----------
        component_name: str
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
        file_name: str
            Name of the materials database.
        material_name: str
            Name of the solid material.
        """
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def export_solid_material(self, file_name, material_name):
        """Export the solid material to the materials database.

        Parameters
        ----------
        file_name: str
            Name of the materials database.
        material_name: str
            Name of the solid material.
        """
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def delete_solid_material(self, material_name):
        """Delete the solid material from the materials database."""
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_iron_loss_coefficients(self, material_name):
        """Calculate and return the iron loss coefficients for the solid material.

        Parameters
        ----------
        material_name: str
            Name of the solid material.
        """
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_iron_loss_coefficients(self, material_name):
        """Save the calculated iron loss coefficients to the materials database.

        Parameters
        ----------
        material_name: str
            Name of the solid material.
        """
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_magnet_parameters(self, material_name):
        """Calculate parameters for the nonlinear demagnetisation model.

        Parameters
        ----------
        material_name: str
            Name of the solid material.
        """
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_magnet_parameters(self, material_name):
        """Save the calculated magnet parameters of the solid material to the materials database.

        Parameters
        ----------
        material_name: str
            Name of the solid material.
        """
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)
