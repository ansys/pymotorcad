# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""RPC methods for FEA geometry.

Advanced functions. See FEA_Geometry_Scripting tutorial for more information
"""


class _RpcMethodsFEAGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def do_slot_finite_element(self):
        """Run slot FEA."""
        method = "DoSlotFiniteElement"
        return self.connection.send_and_receive(method)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, r_or_x, t_or_y, calculation, expression
    ):
        """Add or edit a point in the path editor."""
        method = "SetFEAPathPoint"
        params = [
            path_name,
            path_location,
            coord_system,
            r_or_x,
            t_or_y,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_arc(
        self,
        path_name,
        path_location,
        r,
        theta_start,
        theta_end,
        points,
        fea_method,
        calculation,
        expression,
    ):
        """Add or edit an arc in the path editor."""
        method = "SetFEAPathArc"
        params = [
            path_name,
            path_location,
            r,
            theta_start,
            theta_end,
            points,
            fea_method,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_line(
        self,
        path_name,
        path_location,
        coord_system,
        r_or_x_start,
        t_or_y_start,
        r_or_x_end,
        t_or_y_end,
        points,
        calculation,
        expression,
    ):
        """Add or edit a line in the path editor."""
        method = "SetFEAPathLine"
        params = [
            path_name,
            path_location,
            coord_system,
            r_or_x_start,
            t_or_y_start,
            r_or_x_end,
            t_or_y_end,
            points,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def save_fea_data(self, file, first_step, final_step, outputs, regions, separator):
        """Save raw data for the current FEA solution.

        Parameters
        ----------
        file : str
            File location to write to.
        first_step : int
            First step of results required (for transient calculation).
        final_step : int
            Final step of results required (for transient calculation).
        outputs : str
            FEA data requested, for example RegCode, B, Pt. Multiple outputs be passed as a
            comma-separated string, for example 'RegCode,B,Pt'.
        regions : str
            FEA region names that data is wanted for, for example L1_1Magnet1N1, Rotor,
            ArmatureSlotR2. Multiple regions must be passed as a comma-separated string,
            for example 'L1_1Magnet1N1,Rotor,ArmatureSlotR2'.
            An empty string will include all FEA regions.
        separator : str
            Separator used in writing the output file.
        """
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.connection.send_and_receive(method, params)

    def get_region_value(self, expression, region_name):
        """Calculate the integral value for an expression of a region."""
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.connection.send_and_receive(method, params)

    def get_region_loss(self, expression, region_name, radius1, radius2, angle1, angle2):
        """Calculate the loss value for an expression of a region.

        This method is valid for a magnetic solution only.
        The region is bounded by the radii and angles that are specified in parameters.

        Radii and angle values of 0 give all region losses.
        Losses calculated are per unit length and are only for the FEA areas modeled.

        For total losses, you must multiply by the symmetry factor.
        """
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.connection.send_and_receive(method, params)

    def get_point_value(self, parameter, x, y):
        """Get a point value from the Motor-CAD FEA.

        Parameters
        ----------
        parameter : str|int
            Motor-CAD shading function.
        x : float
            Value for the x coordinate.
        y : float
            Value for the y coordinate.

        Returns
        -------
        value : float
            Value from the FEA.
        units : string
            Units for ``parameter``, which is the Motor-CAD shading function.
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Custom Geometry ------------------------------------

    def _get_region_properties_xy(self, x, y):
        """Get properties of region from name and coordinates.

        Returns list of parameters. Currently only used for testing other geometry functions.
        EXPERIMENTAL FUNCTION - LIKELY TO CHANGE.
        """
        method = "GetRegionProperties_XY"
        params = [x, y]
        return self.connection.send_and_receive(method, params)
