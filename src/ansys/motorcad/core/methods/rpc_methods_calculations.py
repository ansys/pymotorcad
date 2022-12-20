"""RPC methods for calculations."""


class _RpcMethodsCalculations:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def do_magnetic_thermal_calculation(self):
        """Carry out coupled e-magnetic and thermal calculation."""
        method = "DoMagneticThermalCalculation"
        return self.connection.send_and_receive(method)

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
