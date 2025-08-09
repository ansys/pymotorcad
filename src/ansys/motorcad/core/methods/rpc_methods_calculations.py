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

"""RPC methods for calculations."""


class _RpcMethodsCalculations:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def do_magnetic_thermal_calculation(self):
        """Run coupled e-magnetic and thermal calculations."""
        method = "DoMagneticThermalCalculation"
        return self.connection.send_and_receive(method)

    def calculate_saturation_map(self):
        """Generate electromagnetic saturation and loss data.

        Saturation (flux linkages and inductances) and loss data can be used
        in other analysis and modeling tools. The default MAT file is saved in
        the lab folder in the ``.mot`` directory.
        """
        method = "CalculateSaturationMap"
        return self.connection.send_and_receive(method)

    def calculate_torque_envelope(self):
        """Calculate the torque envelope for the machine."""
        method = "CalculateTorqueEnvelope"
        return self.connection.send_and_receive(method)

    def calculate_im_saturation_model(self):
        """Calculate saturation lookup tables for IM machines."""
        method = "CalculateIMSaturationModel"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_spatial(self):
        """Calculate 1D force harmonics on the space axis."""
        method = "CalculateForceHarmonics_Spatial"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_temporal(self):
        """Calculate 1D force harmonics on the time axis."""
        method = "CalculateForceHarmonics_Temporal"
        return self.connection.send_and_receive(method)

    def get_force_frequency_domain_amplitude(self, row, column, load_point):
        """Export the matrix value from a force space time harmonics matrix for a 2D FFT.

        Parameters
        ----------
        row : int
            Row index of the FFT matrix.
        column : int
            Column index of the FFT matrix.
        load_point : int
        """
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, load_point]
        return self.connection.send_and_receive(method, params)

    def update_force_analysis_results(self, fft_data_type):
        """Update force analysis results for the multiforce operating point.

        Parameters
        ----------
        fft_data_type : int
            FFT data type. Options are:

            - 0: 1D Temporal Harmonics
            - 1: 1D Spatial Harmonics

        """
        method = "UpdateForceAnalysisResults"
        params = [fft_data_type]
        return self.connection.send_and_receive(method, params)

    def do_multi_force_calculation(self):
        """Run the multiforce operating point calculation."""
        method = "DoMultiForceCalculation"
        return self.connection.send_and_receive(method)

    def do_steady_state_analysis(self):
        """Run the thermal steady state analysis."""
        method = "DoSteadyStateAnalysis"
        return self.connection.send_and_receive(method)

    def do_transient_analysis(self):
        """Run the thermal transient analysis."""
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

    def create_winding_pattern(self):
        """Create winding pattern.

        With Motor-CAD version 26R1 or greater, updates winding pattern, properties, and weights, after
        changing winding parameters.
        With Motor-CAD version less than 26R1, refreshes the UI to recreate winding pattern.
        """
        if self.connection.check_version_at_least("2026.1"):
            # Update parameters on the Winding Pattern page.
            method = "CreateWindingPattern"
            return self.connection.send_and_receive(method)
        else:
            # Retain for now, as still lots of work done in the UI on this tab.
            self.display_screen("Scripting")
            self.display_screen("Winding;Definition")

    def create_winding_pattern_rotor(self):
        """Create rotor winding pattern.

        Update the rotor winding and weights and volumes post edit of winding parameters.
        Requires MotorCAD version 26R1 or greater.
        """

        method = "RefreshWindingDefinitionRotor"
        return self.connection.send_and_receive(method)

