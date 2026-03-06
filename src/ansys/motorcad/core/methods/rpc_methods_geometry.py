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

"""RPC methods for geometry."""
# from core import MotorCADError


class _RpcMethodsGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_winding_coil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        """Set go and return slots, positions, and turns for the winding coil.

        Parameters
        ----------
        phase : int
        path : int
        coil : int
        go_slot : int
        go_position : str
            Position values for the upper and lower paths of a go slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a go
            slot are ``"L"`` and ``"R"``.
        return_slot : int
        return_position : str
            Position values for the upper and lower paths of a return slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a return
            slot are ``"L"`` and ``"R"``.
        turns : int
        """
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            go_slot,
            go_position,
            return_slot,
            return_position,
            turns,
        ]
        return self.connection.send_and_receive(method, params)

    def get_winding_coil(self, phase, path, coil):
        """Get the go and return slots, positions, and turns for the winding coil.

        In Motor-CAD, you can select **Winding -> Pattern** to see how phases, paths,
        and coils are indexed.

        Parameters
        ----------
        phase : int
        path : int
        coil : int

        Returns
        -------
        GoSlot : int
        GoPosition : str
        ReturnSlot : int
        ReturnPosition : str
        Turns : int
        """
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.connection.send_and_receive(method, params)

    def check_if_geometry_is_valid(self, edit_geometry):
        """Check if the Motor-CAD geometry is valid.

        Parameters
        ----------
        edit_geometry : int
            Indicates if Motor-CAD can try to reset the geometry
            within constraints if the geometry is invalid. Options are:

            - ``1``: Yes. Try and reset the geometry
            - ``0``: No. Do not try to reset the geometry.

        Returns
        -------
        int
            ``1`` if an attempt to reset the geometry has been made, ``O`` otherwise.
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)

    def get_conductor_positions(self):
        """Get the x-y coordinates of conductors in the slot from Motor-CAD.

        Returns
        -------
        conductor_positions_l : list of [float, float]
            list of conductor coordinates where [x-coordinate, y-coordinate] for the left side of
            the slot.
        conductor_positions_l : list of [float, float]
            list of conductor coordinates where [x-coordinate, y-coordinate] for the right side of
            the slot.
        """
        # define lists to store the conductor positions for each side of the slot
        conductor_positions_l = []
        conductor_positions_r = []
        sides = [conductor_positions_l, conductor_positions_r]
        l_r = ["L", "R"]

        # loop through left then right side of the slot, getting the x-y coordinates of conductor
        # positions
        for i in range(len(sides)):
            # Get the x-y conductor positions. These are returned as a single string. The string is
            # a 2D array of values where ";" separates columns of conductors and ":" separates each
            # value.
            conductor_positions_x = self.get_variable(f"ConductorCentre_{l_r[i]}_x")
            conductor_positions_y = self.get_variable(f"ConductorCentre_{l_r[i]}_y")

            # split the string into a list for each column of conductors
            conductor_positions_x = conductor_positions_x.split(" ; ")
            conductor_positions_y = conductor_positions_y.split(" ; ")

            # loop through the strings representing conductor positions for each column and split
            # into individual values.
            for j in range(len(conductor_positions_x)):
                conductor_positions_x[j] = conductor_positions_x[j].split(" : ")
                conductor_positions_y[j] = conductor_positions_y[j].split(" : ")

            # for each x-y conductor position, convert values from string to float and store in a
            # list where indices represent [x_coordinate, y_coordinate].
            # store all conductor position coordinates in a single list for each side of the slot
            # (conductor_positions_l and conductor_positions_r are not sorted by columns).
            for j in range(len(conductor_positions_x)):
                for k in range(len(conductor_positions_x[j])):
                    conductor_position = [
                        float(conductor_positions_x[j][k]),
                        float(conductor_positions_y[j][k]),
                    ]
                    # ignore any unwanted [0, 0] entries that are contained in the strings from
                    # Motor-CAD
                    if conductor_position != [0, 0]:
                        sides[i].append(conductor_position)
        # return the lists of conductor positions for each side of the slot
        return conductor_positions_l, conductor_positions_r
