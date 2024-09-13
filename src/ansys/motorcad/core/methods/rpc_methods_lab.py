"""RPC methods for Motor-CAD Lab."""
k_num_custom_losses_internal_lab = "NumCustomLossesInternal_Lab"
k_custom_loss_name_internal_lab = "CustomLoss_name_internal_lab"
k_custom_loss_function_internal_lab = "CustomLoss_Function_Internal_Lab"
k_custom_loss_type_internal_lab = "CustomLoss_Type_Internal_Lab"
k_custom_loss_thermal_node_internal_lab = "CustomLoss_ThermalNode_Internal_Lab"
k_num_custom_losses_external_lab = "NumCustomLossesExternal_Lab"
k_custom_loss_name_external_lab = "CustomLoss_Name_External_Lab"
k_custom_loss_power_function_external_lab = "CustomLoss_PowerFunction_External_Lab"
k_custom_loss_voltage_function_external_lab = "CustomLoss_VoltageFunction_External_Lab"

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
        """Add an internal custom loss.

        Parameters
        ----------
        name : str
            Name of lab internal custom loss
        function : str
            Function of lab internal custom loss
        type : str
            Type of lab internal custom loss. Options are Electrical or Mechanical
        thermal_node : int
            Thermal node of lab internal custom loss

        """
        type = type.capitalize()
        # Internal Custom Loss Type is case-sensitive in MotorCAD.
        # Added a line to match the required format.
        if type not in ["Electrical", "Mechanical"]:
            raise ValueError("Thermal Loss Type must be Electrical or Mechanical")
        if not self.get_node_exists(thermal_node):
            raise ValueError("Thermal node does not exist")
        else:
            no_internal_losses = self.get_variable(k_num_custom_losses_internal_lab)
            self.set_variable(k_num_custom_losses_internal_lab, no_internal_losses + 1)
            self.set_array_variable(k_custom_loss_name_internal_lab, no_internal_losses, name)
            self.set_array_variable(
                k_custom_loss_function_internal_lab, no_internal_losses, function
            )
            self.set_array_variable(k_custom_loss_type_internal_lab, no_internal_losses, type)
            self.set_array_variable(
                k_custom_loss_thermal_node_internal_lab, no_internal_losses, thermal_node
            )

    def add_external_custom_loss(self, name, power_function, voltage_function):
        """Add an external custom loss.

        Parameters
        ----------
        name : str
            Name of lab external custom loss
        power_function : str
            Power function for lab external custom loss
        voltage_function : str
            Function for voltage drop for lab external custom loss

        """
        no_external_losses = self.get_variable(k_num_custom_losses_external_lab)
        self.set_variable(k_num_custom_losses_external_lab, no_external_losses + 1)
        self.set_array_variable(k_custom_loss_name_external_lab, no_external_losses, name)
        self.set_array_variable(
            k_custom_loss_power_function_external_lab, no_external_losses, power_function
        )
        self.set_array_variable(
            k_custom_loss_voltage_function_external_lab, no_external_losses, voltage_function
        )

    def remove_internal_custom_loss(self, name):
        """Remove an internal custom loss by name.

        Parameters
        ----------
        name : str
            Name of lab internal custom loss

        """
        index = self._get_index_from_name(
            name, k_num_custom_losses_internal_lab, k_custom_loss_name_internal_lab
        )
        self._motorcad_array_pop(
            index,
            k_num_custom_losses_internal_lab,
            [
                k_custom_loss_name_internal_lab,
                k_custom_loss_function_internal_lab,
                k_custom_loss_type_internal_lab,
                k_custom_loss_thermal_node_internal_lab,
            ],
        )

    def remove_external_custom_loss(self, name):
        """Remove an external custom loss by name.

        Parameters
        ----------
        name : str
            Name of lab external custom loss

        """
        index = self._get_index_from_name(
            name, k_num_custom_losses_external_lab, k_custom_loss_name_external_lab
        )
        self._motorcad_array_pop(
            index,
            k_num_custom_losses_external_lab,
            [
                k_custom_loss_name_external_lab,
                k_custom_loss_power_function_external_lab,
                k_custom_loss_voltage_function_external_lab,
            ],
        )

    def _motorcad_array_pop(self, index, var_length_array, list_of_var_names):
        """Remove variables at a specified location within an array.

        Parameters
        ----------
        index : int
            Index of array to remove
        var_length_array : str
            Variable which specifies the length of the array
        list_of_var_names : list
            List of variables to pop

        """
        array_length = self.get_variable(var_length_array)

        for i in range(index + 1, array_length):
            for j in range(len(list_of_var_names)):
                self.set_array_variable(
                    list_of_var_names[j], i - 1, self.get_array_variable(list_of_var_names[j], i)
                )

        self.set_variable(var_length_array, array_length - 1)

    def _get_index_from_name(self, name, var_length_array, variable_name):
        """Retrieve index of a specified variable name within an array.

        Parameters
        ----------
        name : str
            Specified name to find
        var_length_array : str
            Variable which specifies the length of the array
        variable_name : str
            Variable that holds the list of names

        """
        array_length = self.get_variable(var_length_array)
        for i in range(array_length):
            if name == self.get_array_variable(variable_name, i):
                index = i
                break
        else:
            raise NameError("Provided name is not listed")
        return index
