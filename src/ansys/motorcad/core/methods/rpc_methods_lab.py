"""RPC methods for Motor-CAD Lab."""
# from shreya_custom_loss_test import add_external_custom_loss


class _RpcMethodsLab:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def calculate_test_performance_lab(self):
        """Calculate the test performance.

        Results are saved in the MOT file results folder as ``MotorLAB_caldata.mat``.
        """
        method = "CalculateTestPerformance_Lab"
        return self.connection.send_and_receive(method)

    def export_duty_cycle_lab(self):
        """Export the calculated duty cycle data to the thermal model."""
        method = "ExportDutyCycle_Lab"
        return self.connection.send_and_receive(method)

    def get_model_built_lab(self):
        """Test if the Lab model must be built or rebuilt before running calculations.

        Returns
        -------
        bool
            ``True`` if the Lab model has been built and is valid for the current settings,
            ``False`` otherwise.
        """
        method = "GetModelBuilt_Lab"
        return self.connection.send_and_receive(method)

    def show_results_viewer_lab(self, calculation_type):
        """Load the results viewer for the specified Lab calculation type.

        Parameters
        ----------
        calculation_type : str
            Type of calculation. Options are ``"Electromagnetic"``, ``"Thermal"``,
            ``"Generator"``, ``"Duty Cycle"``, and ``"Calibration"``.
        """
        method = "ShowResultsViewer_Lab"
        params = [calculation_type]
        return self.connection.send_and_receive(method, params)

    def export_figure_lab(self, calculation_type, variable, file_name):
        """Export an image of the Lab results graph.

        Parameters
        ----------
        calculation_type : str
            Type of calculation. Options are ``"Electromagnetic"``, ``"Thermal"``,
            ``"Generator"``, ``"Duty Cycle"``, and ``"Calibration"``.
        variable : str
           Variable to plot on the Y axis (2D graphs) or Z axis (3D graphs). For
           example, ``"Shaft Torque"``.
        file_name : str
            Name of the image file.
        """
        method = "ExportFigure_Lab"
        params = [calculation_type, variable, file_name]
        return self.connection.send_and_receive(method, params)

    def calculate_generator_lab(self):
        """Calculate generator performance.

        Results are saved in the MOT file results folder as ``LabResults_Generator.mat``.
        """
        method = "CalculateGenerator_Lab"
        return self.connection.send_and_receive(method)

    def load_external_model_lab(self, file_path):
        """Load an external model data file.

        This parameter is used when the Lab link type is set to ``Custom`` or ``Ansys Maxwell``.

        Parameters
        ----------
        file_path : str
            Full path to the data file, including the file name. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "LoadExternalModel_Lab"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def clear_model_build_lab(self):
        """Clear the Lab model build."""
        method = "ClearModelBuild_Lab"
        return self.connection.send_and_receive(method)

    def build_model_lab(self):
        """Build the Lab model."""
        method = "BuildModel_Lab"
        return self.connection.send_and_receive(method)

    def calculate_operating_point_lab(self):
        """Run the Lab operating point calculation."""
        method = "CalculateOperatingPoint_Lab"
        return self.connection.send_and_receive(method)

    def calculate_magnetic_lab(self):
        """Run the Lab magnetic calculation."""
        method = "CalculateMagnetic_Lab"
        return self.connection.send_and_receive(method)

    def calculate_thermal_lab(self):
        """Run the Lab thermal calculation."""
        method = "CalculateThermal_Lab"
        return self.connection.send_and_receive(method)

    def calculate_duty_cycle_lab(self):
        """Run the Lab duty cycle."""
        method = "CalculateDutyCycle_Lab"
        return self.connection.send_and_receive(method)

    def add_internal_custom_loss(self, name, function, type, thermal_node):
        """ Add Internal Custom Loss.

        Parameters
        ----------
        name : str
        function : str
        type : str
            Thermal loss type. Options are ``"Electrical"`` and ``"Mechanical"``,
        thermal_node : int

        Returns
        -------

        """
        if type not in ["Electrical", "Mechanical"]:
            raise ValueError("Thermal Loss Type must be Electrical or Mechanical")
        else:
            no_internal_losses = self.get_variable("NumCustomLossesInternal_Lab")
            self.set_variable("NumCustomLossesInternal_Lab", no_internal_losses + 1)
            self.set_array_variable("CustomLoss_name_internal_lab", no_internal_losses, name)
            self.set_array_variable("CustomLoss_Function_Internal_Lab", no_internal_losses, function)
            self.set_array_variable("CustomLoss_Type_Internal_Lab", no_internal_losses, type)
            self.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_internal_losses, thermal_node)

    def add_external_custom_loss(self, name, power_function, voltage_function):
        """ Add External Custom Loss.

        Parameters
        ----------
        name : str
        power_function : str
        voltage_function : str

        Returns
        -------

        """
        no_external_losses = self.get_variable("NumCustomLossesExternal_Lab")
        self.set_variable("NumCustomLossesExternal_Lab", no_external_losses + 1)
        self.set_array_variable('CustomLoss_Name_External_Lab', no_external_losses, name)
        self.set_array_variable('CustomLoss_PowerFunction_External_Lab', no_external_losses, power_function)
        self.set_array_variable('CustomLoss_VoltageFunction_External_Lab', no_external_losses, voltage_function)



