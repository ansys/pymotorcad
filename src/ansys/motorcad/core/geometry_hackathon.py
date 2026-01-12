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

"""Function for new hackathon ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from copy import deepcopy

import numpy as np
from scipy.interpolate import splev, splrep

from ansys.motorcad.core.geometry import Arc, Coordinate
from ansys.motorcad.core.geometry_fitting import return_entity_list

GEOM_TOLERANCE = 1e-6


class Spline:
    """Python representation of Motor-CAD spline object based upon parameters.

    Parameters
    ----------
    control_points : list of Coordinate
        List of control points that define the spline.
    """

    def __init__(self, control_points):
        """Initialise Spline."""
        self.start = deepcopy(control_points[0])
        self.end = deepcopy(control_points[-1])
        x = []
        y = []
        for point in control_points:
            x.append(point.x)
            y.append(point.y)

        # find spline representation
        self.bspline = splrep(x, y)
        self.bspline_entities = self.get_spline_entities()
        self.length = 0
        for entity in self.bspline_entities:
            self.length += entity.length
        if isinstance(self.bspline_entities[0], Arc):
            self.start_angle = self.bspline_entities[0].start_angle
        else:
            self.start_angle = self.bspline_entities[0].angle
        if isinstance(self.bspline_entities[-1], Arc):
            self.end_angle = self.bspline_entities[-1].end_angle
        else:
            self.end_angle = self.bspline_entities[-1].angle

    def get_spline_points_from_x_values(self, x_values):
        """
        Return list of Coordinates.

        Parameters
        ----------
        x_values : list of float
            list of x values for which Coordinates will be calculated.

        Returns
        -------
        list of Coordinate

        """
        x_new = np.array(x_values)
        y_new = splev(x_new, self.bspline)

        spline_points = []
        for i in range(x_new.size):
            spline_points.append(Coordinate(float(x_new[i]), float(y_new[i])))

        return spline_points

    def get_spline_entities(
        self, n_points=256, line_tolerance=GEOM_TOLERANCE, arc_tolerance=GEOM_TOLERANCE
    ):
        """
        Return EntityList of Line and Arc entities to represent the spline.

        Returns
        -------
        ansys.motorcad.core.geometry.EntityList

        """
        x_start = self.start.x
        x_end = self.end.x

        x_new = np.linspace(x_start, x_end, n_points)
        spline_points = self.get_spline_points_from_x_values(x_new)

        return return_entity_list(spline_points, line_tolerance, arc_tolerance)
