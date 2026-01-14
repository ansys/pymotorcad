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
from enum import Enum

import numpy as np
from scipy.interpolate import splev, splrep

from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, RegionType
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


class BSpline:
    """Python representation of Motor-CAD spline object based upon parameters.

    Parameters
    ----------
    control_points : list of Coordinate
        List of control points that define the spline.
    samples : int
        Number of samples to return
    degree : int
        Curve degree
    periodic : bool
        If True, Curve is closed. False, Curve is open.
    """

    def __init__(self, control_points, samples=100, degree=3, periodic=False):
        """Initialise Spline."""
        self.start = deepcopy(control_points[0])
        self.end = deepcopy(control_points[-1])

        x = []
        y = []
        for point in control_points:
            x.append(point.x)
            y.append(point.y)
        control_points = np.array([x, y])

        # If periodic, extend the point array by count+degree+1
        count = len(control_points)

        if periodic:
            factor, fraction = divmod(count + degree + 1, count)
            control_points = np.concatenate(
                (control_points,) * factor + (control_points[:fraction],)
            )
            count = len(control_points)
            degree = np.clip(degree, 1, degree)

        # If open, prevent degree from exceeding count-1
        else:
            degree = np.clip(degree, 1, count - 1)

        # Calculate knot vector
        knots = None
        if periodic:
            knots = np.arange(0 - degree, count + degree + degree - 1, dtype="int")
        else:
            knots = np.concatenate(
                ([0] * degree, np.arange(count - degree + 1), [count - degree] * degree)
            )

        # Calculate query range
        u = np.linspace(periodic, (count - degree), samples)

        # Calculate result
        bspline = np.array(splev(u, (knots, control_points.T, degree))).T

        self.bspline_points = []
        for i in range(len(bspline)):
            this_point = Coordinate(float(bspline[i][0]), float(bspline[i][1]))
            self.bspline_points.append(this_point)

        self.bspline_entities = return_entity_list(
            self.bspline_points, line_tolerance=GEOM_TOLERANCE, arc_tolerance=GEOM_TOLERANCE
        )
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


class ShapeType(Enum):
    """Provides an enumeration for storing Motor-CAD region shape type."""

    rectangle = "Rectangle"
    square = "Square"
    circle = "Circle"
    triangle_ra = "Triangle (right angled)"


#    triangle_is


class Rectangle(Region):
    """Create rectangular geometry region.

    Parameters
    ----------
    width: float
        width of rectangle
    height: float
        height of rectangle
    centre: ansys.motorcad.core.geometry.Coordinate
        Centre of rectangle
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected
    """

    def __init__(
        self, width, height, centre, region_type=RegionType.adaptive, motorcad_instance=None
    ):
        """Initialise Rectangle."""
        super().__init__(region_type, motorcad_instance)
        self.width = width
        self.height = height
        w_start_x = centre.x - width / 2
        w_end_x = centre.x + width / 2

        h_start_y = centre.y - height / 2
        h_end_y = centre.y + height / 2

        self.add_entity(
            Line(
                Coordinate(centre.x - width / 2, centre.y - height / 2),
                Coordinate(centre.x + width / 2, centre.y - height / 2),
            )
        )
        self.add_entity(
            Line(
                Coordinate(centre.x + width / 2, centre.y - height / 2),
                Coordinate(centre.x + width / 2, centre.y + height / 2),
            )
        )
        self.add_entity(
            Line(
                Coordinate(centre.x + width / 2, centre.y + height / 2),
                Coordinate(centre.x - width / 2, centre.y + height / 2),
            )
        )
        self.add_entity(
            Line(
                Coordinate(centre.x - width / 2, centre.y + height / 2),
                Coordinate(centre.x - width / 2, centre.y - height / 2),
            )
        )

        # self.rotation_angle = 0

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        dict
            Dictionary of the Rectangle geometry region represented as JSON.
        """
        region_dict = super()._to_json()

        region_dict["width"] = self.width
        if self.width == self.height:
            region_dict["shape_type"] = ShapeType.square
        else:
            region_dict["shape_type"] = ShapeType.rectangle
            region_dict["height"] = self.height

    # method to receive region from Motor-CAD and create python object
    # @classmethod
    # def _from_json(cls, json, motorcad_instance=None):
    #     """Convert the class from a JSON object.
    #
    #     Parameters
    #     ----------
    #     json: dict
    #         Dictionary representing the geometry region.
    #     motorcad_instance : ansys.motorcad.core.MotorCAD
    #         Motor-CAD instance to connect to. The default is ``None``.
    #     """
    #     has_region_type = "region_type" in json
    #     is_magnet = has_region_type and (json["region_type"] == RegionType.magnet.value)
    #     has_shape_type = "shape_type" in json
    #
    #     if has_shape_type:
    #         if json["shape_type"] == ShapeType.square:
    #             if has_region_type:
    #                 new_region = cls(width = json["width"], height = json["width"],
    #                                  centre= json["centroid"], region_type=json["region_type"],
    #                                  motorcad_instance=motorcad_instance)
    #             else:
    #         elif json["shape_type"] == ShapeType.rectangle:
    #             if has_region_type:
    #                 new_region = cls(width = json["width"], height = json["height"],
    #                                  centre= json["centroid"], region_type=json["region_type"],
    #                                  motorcad_instance=motorcad_instance)
    #             else:
    #                 new_region = cls(width = json["width"], height = json["height"],
    #                                  centre= json["centroid"],
    #                                  motorcad_instance=motorcad_instance)
    #
    #
    #         if has_region_type:
    #             new_region = cls(
    #                 motorcad_instance=motorcad_instance,
    #                 region_type=RegionType(json["region_type"])
    #             )
    #         else:
    #             new_region = cls(motorcad_instance=motorcad_instance)
    #
    #     new_region._add_parameters_from_json(json)
    #
    #     return new_region


class Circle(Region):
    """Create circular geometry region.

    Parameters
    ----------
    radius: float
        radius of circle
    centre: ansys.motorcad.core.geometry.Coordinate
        Centre of circle
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected
    """

    def __init__(self, radius, centre, region_type=RegionType.adaptive, motorcad_instance=None):
        """Initialise Circle."""
        super().__init__(region_type, motorcad_instance)
        self.radius = radius
        point_1 = Coordinate(centre.x, centre.y - radius)
        point_2 = Coordinate(centre.x, centre.y + radius)

        self.add_entity(Arc(point_1, point_2, centre=centre, radius=radius))
        self.add_entity(Arc(point_2, point_1, centre=centre, radius=radius))

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        dict
            Dictionary of the Circle geometry region represented as JSON.
        """
        region_dict = super()._to_json()

        region_dict["radius"] = self.radius
        region_dict["shape_type"] = ShapeType.circle


class TriangleRA(Region):
    """Create right-angled triangular geometry region.

    Parameters
    ----------
    width: float
        width of right-angled triangle
    height: float
        height of right-angled triangle
    square_vertex: ansys.motorcad.core.geometry.Coordinate
        Coordinate of square right-angle corner of triangle
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected
    """

    def __init__(
        self, width, height, square_vertex, region_type=RegionType.adaptive, motorcad_instance=None
    ):
        """Initialise TriangleRA."""
        super().__init__(region_type, motorcad_instance)
        self.width = width
        self.height = height
        point_1 = Coordinate(square_vertex.x, square_vertex.y)
        point_2 = Coordinate(square_vertex.x + width, square_vertex.y)
        point_3 = Coordinate(square_vertex.x, square_vertex.y + height)

        self.add_entity(Line(point_1, point_2))
        self.add_entity(Line(point_2, point_3))
        self.add_entity(Line(point_3, point_1))

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        dict
            Dictionary of the Triangle geometry region represented as JSON.
        """
        region_dict = super()._to_json()

        region_dict["width"] = self.width
        region_dict["height"] = self.height
        region_dict["shape_type"] = ShapeType.triangle_ra
