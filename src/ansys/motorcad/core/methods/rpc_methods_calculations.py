"""RPC methods for calculations."""


class _RpcMethodsCalculations:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def clear_duty_cycle(self):
        """Clear the duty cycle in both the lab and thermal contexts."""
        method = "ClearDutyCycle"
        return self.connection.send_and_receive(method)

    def do_magnetic_thermal_calculation(self):
        """Carry out coupled e-magnetic and thermal calculation."""
        method = "DoMagneticThermalCalculation"
        return self.connection.send_and_receive(method)

    def set_3d_component_visibility(self, group_name, component_name, visibility):
        """Set the visibility of a component specified by group name, and component name.

        Parameters
        ----------
        group_name : str
            "Machine", "Stator", "Rotor", "Shaft Components". If in the thermal context then
            "Mounting"
            and "Outer Casing" are available too.
        component_name : str
            "All", "Lamination", "Wedge". The available component names depends on which model
            is used.
        visibility : int
            0=Invisible to 100=Solid
        """
        method = "Set3DComponentVisibility"
        params = [group_name, component_name, visibility]
        return self.connection.send_and_receive(method, params)

    def calculate_saturation_map(self):
        """Generate electromagnetic saturation and loss data.

        Saturation (flux linkages and inductances) and loss data for use in other
        analysis and modelling tools. The default file extension is .mat and is saved in
        the lab folder in the .mot directory.
        """
        method = "CalculateSaturationMap"
        return self.connection.send_and_receive(method)

    def calculate_torque_envelope(self):
        """Calculate torque envelope for machine."""
        method = "CalculateTorqueEnvelope"
        return self.connection.send_and_receive(method)

    def save_results(self, solution_type):
        """Save the output results from the selected solution (EMagnetic).

        Parameters
        ----------
        solution_type : str
            Only 'EMagnetic' solution type currently available.
        """
        method = "SaveResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def load_results(self, solution_type):
        """Load the output results from the selected solution (EMagnetic).

        Parameters
        ----------
        solution_type : str
            Only 'EMagnetic' solution type currently available.
        """
        method = "LoadResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def calculate_im_saturation_model(self):
        """Calculate saturation lookup tables for IM machines."""
        method = "CalculateIMSaturationModel"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_spatial(self):
        """Calculate 1D force harmonics in Space axis."""
        method = "CalculateForceHarmonics_Spatial"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_temporal(self):
        """Calculate 1D force harmonics in Time axis."""
        method = "CalculateForceHarmonics_Temporal"
        return self.connection.send_and_receive(method)

    def get_force_frequency_domain_amplitude(self, row, column, load_point):
        """Export matrix value from Force Space Time Harmonics matrix from 2D FFT.

        Parameters
        ----------
        row : int
            row index of FFT matrix
        column : int
            column index of FFT matrix
        load_point : int
        """
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, load_point]
        return self.connection.send_and_receive(method, params)

    def update_force_analysis_results(self, fft_data_type):
        """Update force analysis results for selected multiforce operating point.

        Parameters
        ----------
        fft_data_type : int
            0 : 1D Temporal Harmonics, 1 : 1D Spatial Harmonics
        """
        method = "UpdateForceAnalysisResults"
        params = [fft_data_type]
        return self.connection.send_and_receive(method, params)

    def do_multi_force_calculation(self):
        """Calculate forces for multiple operating points."""
        method = "DoMultiForceCalculation"
        return self.connection.send_and_receive(method)

    def do_steady_state_analysis(self):
        """Do thermal steady state analysis."""
        method = "DoSteadyStateAnalysis"
        return self.connection.send_and_receive(method)

    def do_transient_analysis(self):
        """Do thermal transient analysis."""
        method = "DoTransientAnalysis"
        return self.connection.send_and_receive(method)

    def do_magnetic_calculation(self):
        """Run the Motor-CAD magnetic calculation."""
        method = "DoMagneticCalculation"
        return self.connection.send_and_receive(method)

    def do_weight_calculation(self):
        """Run the Motor-CAD weight calculation."""
        method = "DoWeightCalculation"
        return self.connection.send_and_receive(method)

    def do_mechanical_calculation(self):
        """Run the Motor-CAD mechanical calculation."""
        method = "DoMechanicalCalculation"
        return self.connection.send_and_receive(method)

    # ------------------------------------ Internal Scripting ------------------------------------

    def save_script(self, file_path):
        """Save the internal python script to a file.

        The .py extension should be included in the file name.

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be saved. The default
            filepath is the Windows directory in the C: drive. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "SaveScript"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_script(self, script_file):
        """Load a script file into Motor-CAD internal scripting.

        Parameters
        ----------
        script_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadScript"
        params = [script_file]
        return self.connection.send_and_receive(method, params)

    def run_script(self):
        """Run script file in Motor-CAD internal scripting."""
        method = "RunScript"
        return self.connection.send_and_receive(method)
