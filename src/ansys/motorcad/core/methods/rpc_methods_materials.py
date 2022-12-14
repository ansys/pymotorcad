"""RPC methods for materials."""


class _RpcMethodsMaterials:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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
