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

"""RPC methods for graphs."""
from dataclasses import dataclass
import math

from ansys.motorcad.core.rpc_client_core import MotorCADError


@dataclass
class Magnetic3dGraph:
    """Class for x, y and data from a magnetic 3d graph."""

    x: list
    y: list
    data: list


def _dft_real(time_domain):
    """
    Calculate a discrete fourier transform from a real valued list.

    Parameters
    ----------
    time_domain : list of real
        time domain data

    Returns
    -------
    real_components : list
        Real components of the dft.
    imaginary_components : list
        Imaginary components of the dft.
    """
    real_components = []
    imaginary_components = []
    length_input = len(time_domain)
    # Discard terms above Nyquist limit
    length_output = length_input // 2 + 1
    for i in range(length_output):
        real_component = 0
        imag_component = 0
        for j in range(length_input):
            real_component = (
                real_component
                + time_domain[j] * math.cos(i * j * 2 * math.pi / length_input) / length_input
            )
            imag_component = (
                imag_component
                - time_domain[j] * math.sin(i * j * 2 * math.pi / length_input) / length_input
            )
        real_components.append(real_component)
        imaginary_components.append(imag_component)
    return real_components, imaginary_components


class _RpcMethodsGraphs:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def _get_graph(self, graphing_func, *args):
        """Get an array from a Motor-CAD graph.

        Parameters
        ----------
        graphing_func : func
            graph function to use eg. get_magnetic_graph_point
        *args : str, int
            Args for selected graphing function

        Returns
        -------
        x_array : list
            Values of x coordinates from the graph.
        y_array : list
            Values of y coordinates from the graph.
        """
        loop = 0
        x_points = []
        y_points = []
        # turning off message poput window
        save_message_display_state = self.get_variable("MessageDisplayState")
        self.set_variable("MessageDisplayState", 2)
        try:
            while True:
                try:
                    x, y = graphing_func(*args, loop)

                    y_points.append(y)
                    x_points.append(x)
                    loop += 1
                except MotorCADError as e:
                    if "Point requested is greater than number of points available" in str(e):
                        break
                    else:
                        raise
        finally:
            # switching on again the message window
            self.set_variable("MessageDisplayState", save_message_display_state)
        return x_points, y_points

    def get_magnetic_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to retrieve the x and y coordinate values from.

        Returns
        -------
        xValue : float
             Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_temperature_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD thermal graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to get the x and y coordinate values from.

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_power_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD power graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to get x and y coordinate values from.

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_3d_graph_point(self, graph_name, slice_number, point_number, time_step_number):
        """Get a point from a Motor-CAD magnetic 3D graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number : int
            Which skew slice to get results from. Slice 1 is the first.

        point_number : int
            Point number to get x and y coordinate values from.
        time_step_number

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graph_name}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    def get_fea_graph_point(self, graph_id, slice_number, point_number, time_step_number):
        """Get a point from a Motor-CAD FEA graph.

        Parameters
        ----------
        graph_id : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number : int
            Which skew slice to get results from. Slice 1 is the first.

        point_number : int
            Point number to get x and y coordinate values from.
        time_step_number

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graph_id}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph(self, graph_name):
        """Get graph points from a Motor-CAD Magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        Returns
        -------
        x_values : list
            Value of x coordinates from graph
        y_values : list
            Value of y coordinates from graph
        """
        if self.connection.check_version_at_least("2025.0"):
            method = "GetGenericGraph"
            params = [{"variant": graph_name}, "MagneticDataSource", -1, -1]
            return self.connection.send_and_receive(method, params)
        else:
            return self._get_graph(self.get_magnetic_graph_point, graph_name)

    def get_magnetic_graph_harmonics(self, graph_name):
        """Get harmonic analysis from Motor-CAD magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        Returns
        -------
        order_values : list
            Value of harmonic orders from graph
        amplitude_values : list
            Value of harmonic amplitudes from graph
        angle_values : list
            Value of harmonic angles from graph in degrees
        """
        x, y = self.get_magnetic_graph(graph_name)
        # Find x-axis limits and range, as this is needed to find the phase information
        min_x = min(x)
        cycles = (max(x) - min(x)) / 360

        # y normally contains a duplicated final point (360deg=0deg), so discard this point.
        y_no_duplicate = y[: len(y) - 1]

        # Carry out FFT only get up to the Nyquist limit, using real valued inputs
        y_fft_real, y_fft_imag = _dft_real(y_no_duplicate)

        # Apply normalisation.
        for i in range(len(y_fft_real)):
            if i > 0:
                # Multiply by 2 to account for the positive and negative frequency component
                y_fft_real[i] = 2 * y_fft_real[i]
                y_fft_imag[i] = 2 * y_fft_imag[i]
            else:
                # 0th component does not need to be doubled
                y_fft_real[i] = y_fft_real[i]
                y_fft_imag[i] = y_fft_imag[i]

        # Get amplitude and angle:
        y_mag = []
        y_ang = []
        for i in range(len(y_fft_real)):
            y_mag.append(math.sqrt(y_fft_real[i] ** 2 + y_fft_imag[i] ** 2))
            y_ang.append(math.degrees(math.atan2(y_fft_imag[i], y_fft_real[i])))

        # Motor-CAD harmonic plot convention shifts the angles by 90 degrees.
        # Also consider the phase angle of the first point:
        for i in range(len(y_ang)):
            y_ang[i] = y_ang[i] + 90 - (min_x * i / cycles)
            if y_ang[i] > 180:
                y_ang[i] = y_ang[i] - 360
            if y_ang[i] < -180:
                y_ang[i] = y_ang[i] + 360

        # For very small magnitudes, the angle information is not meaningful, so set to zero
        for i in range(len(y_ang)):
            if math.isclose(y_mag[i], 0, abs_tol=1e-8):
                y_ang[i] = 0

        # Generate an index list for plotting
        y_index = []
        for i in range(len(y_ang)):
            y_index.append(i / cycles)

        return [y_index, y_mag, y_ang]

    def get_temperature_graph(self, graph_name):
        """Get graph points from a Motor-CAD transient temperature graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        Returns
        -------
        x_values : list
            value of x coordinates from graph
        y_values : list
            value of y coordinates from graph
        """
        if self.connection.check_version_at_least("2025.0"):
            method = "GetGenericGraph"
            params = [{"variant": graph_name}, "TransientDataSource", -1, -1]
            return self.connection.send_and_receive(method, params)
        else:
            return self._get_graph(self.get_temperature_graph_point, graph_name)

    def get_power_graph(self, graph_name):
        """Get graph points from a Motor-CAD transient power loss graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        Returns
        -------
        x_values : list
            value of x coordinates from graph
        y_values : list
            value of y coordinates from graph
        """
        if self.connection.check_version_at_least("2025.0"):
            method = "GetGenericGraph"
            params = [{"variant": graph_name}, "PowerDataSource", -1, -1]
            return self.connection.send_and_receive(method, params)
        else:
            return self._get_graph(self.get_power_graph_point, graph_name)

    def get_heatflow_graph(self, graph_name):
        """Get graph points from a Motor-CAD heat flow graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        Returns
        -------
        x_values : list
            value of x coordinates from graph
        y_values : list
            value of y coordinates from graph
        """
        self.connection.ensure_version_at_least("2025.0")
        method = "GetGenericGraph"
        params = [{"variant": graph_name}, "HeatFlowDataSource", -1, -1]
        return self.connection.send_and_receive(method, params)

    def get_fea_graph(self, graph_name, slice_number, point_number=0):
        """Get graph points from a Motor-CAD FEA graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number : int
            Which skew slice to get results from. Slice 1 is the first.
        point_number : int
            Point number to get x and y coordinate arrays from for
            transient graphs.

        Returns
        -------
        x_values : list
            value of x coordinates from graph
        y_values : list
            value of y coordinates from graph
        """
        self.connection.ensure_version_at_least("2025.0")
        method = "GetGenericGraph"
        params = [{"variant": graph_name}, "FEAPathDataSource", slice_number, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_3d_graph(self, graph_name, slice_number):
        """Get graph points from a Motor-CAD Magnetic 3d graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number : int
            Which skew slice to get results from. Slice 1 is the first.

        Returns
        -------
        Magnetic3dGraph
            Class containing x, y and data as lists
        """
        self.connection.ensure_version_at_least("2025.0")
        method = "GetMagnetic3DGraph"
        params = [{"variant": graph_name}, slice_number]
        graph_3d_dict = self.connection.send_and_receive(method, params)
        return Magnetic3dGraph(**graph_3d_dict)
