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

"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
import math
from math import sqrt

from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, RegionType, rt_to_xy

GEOM_SHAPE_TOLERANCE = 1e-6


def square(width, r_O, th_O, region_type=RegionType.adaptive, motorcad_instance=None):
    """Create a square region of given width at a given set of coordinates.

    .. note::
        This method is deprecated. Use the :class:`Rectangle` class
        with the `width = ` and `height = ` arguments to create a square Rectangle object and the
        :func:`Rectangle.get_region` method to get a Region object.

    Parameters
    ----------
    width : float
        Width value.
    r_O : float
        Radial coordinate of the square centre.
    th_O : float
        Angular coordinate of the square centre.
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected.

    Returns
    -------
    ansys.motorcad.core.geometry.Region
        Region object with four Line entity types.
    """
    corner = Coordinate(*rt_to_xy(r_O, th_O))

    this_square = Rectangle(corner, width=width, height=width)
    this_square.rotate(corner, th_O - 90)

    shift_distance = this_square.centroid - corner
    this_square_region = this_square.get_region(region_type, motorcad_instance)
    this_square_region.translate(-shift_distance.x, -shift_distance.y)

    return this_square_region


def _square_coordinates(width, r_O, th_O):
    """Create a square of given width at a given set of coordinates.

    .. note::
        This method is deprecated. Use the :class:`Rectangle` class
        with the `width = ` and `height = ` arguments to create a square Rectangle object and the
        :func:`Rectangle.get_region` method to get a Region object.

    Parameters
    ----------
    width : float
        Width value.
    r_O : float
        Radial coordinate of the square centre.
    th_O : float
        Angular coordinate of the square centre.

    Returns
    -------
    x_A : float
        X coordinate value for square vertex A.
    y_A : float
        Y coordinate value for square vertex A.
    x_B : float
        X coordinate value for square vertex B.
    y_B : float
        Y coordinate value for square vertex B.
    x_C : float
        X coordinate value for square vertex C.
    y_C : float
        Y coordinate value for square vertex C.
    x_D : float
        X coordinate value for square vertex D.
    y_D : float
        Y coordinate value for square vertex D.
    """
    corner = Coordinate(*rt_to_xy(r_O, th_O))

    this_square = Rectangle(corner, width=width, height=width)
    this_square.rotate(corner, th_O - 90)

    shift_distance = this_square.centroid - corner
    for entity in this_square:
        entity.translate(-shift_distance.x, -shift_distance.y)

    return (
        this_square[0].start.x,
        this_square[0].start.y,
        this_square[1].start.x,
        this_square[1].start.y,
        this_square[2].start.x,
        this_square[2].start.y,
        this_square[3].start.x,
        this_square[3].start.y,
    )


def eq_triangle_h(height, r_O, th_O, region_type=RegionType.adaptive, motorcad_instance=None):
    """Create an equilateral triangle region of given height at a given set of coordinates.

    .. note::
        This method is deprecated. Use the :func:`Triangle.create_triangle_from_dimensions` method
        with the `height = ` argument to create a Triangle object and the
        :func:`Triangle.get_region` method to get a Region object.

    Parameters
    ----------
    height : float
        Height value.
    r_O : float
        Radial coordinate of the triangle centre.
    th_O : float
        Angular coordinate of the triangle centre.
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected.

    Returns
    -------
    ansys.motorcad.core.geometry.Region
        Region object with three Line entity types.
    """
    corner = Coordinate(*rt_to_xy(r_O, th_O))
    this_triangle = create_triangle_from_dimensions(corner, height=height)
    this_triangle.rotate(corner, th_O - 90)

    shift_distance = this_triangle.centroid - corner
    this_triangle_region = this_triangle.get_region(region_type, motorcad_instance)
    this_triangle_region.translate(-shift_distance.x, -shift_distance.y)

    return this_triangle_region


def eq_triangle_w(width, r_O, th_O, region_type=RegionType.adaptive, motorcad_instance=None):
    """Create an equilateral triangle region of given width at a given set of coordinates.

    .. note::
        This method is deprecated. Use the :func:`Triangle.create_triangle_from_dimensions` method
        with the `width = ` argument to create a Triangle object and the
        :func:`Triangle.get_region` method to get a Region object.

    Parameters
    ----------
    width : float
        Width value.
    r_O : float
        Radial coordinate of the triangle centre.
    th_O : float
        Angular coordinate of the triangle centre.
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected.

    Returns
    -------
    ansys.motorcad.core.geometry.Region
        Region object with three Line entity types.
    """
    corner = Coordinate(*rt_to_xy(r_O, th_O))
    this_triangle = create_triangle_from_dimensions(corner, width=width)
    this_triangle.rotate(corner, th_O - 90)

    shift_distance = this_triangle.centroid - corner
    this_triangle_region = this_triangle.get_region(region_type, motorcad_instance)
    this_triangle_region.translate(-shift_distance.x, -shift_distance.y)

    return this_triangle_region


def triangular_notch(
    radius, sweep, centre_angle, depth, region_type=RegionType.adaptive, motorcad_instance=None
):
    """Create a triangular notch for a rotor or stator at given angular position with given size.

    Parameters
    ----------
    radius : float
        Radius value, radius of the Rotor or Stator for which the notch is being defined.
    sweep : float
        Sweep value, the angular distance (in degrees) that the notch spans.
    centre_angle : float
        Angle value, angular coordinate of the notch centre.
    depth : float
        Depth value, depth of the notch.
    region_type: RegionType or str
        Type of region. String must be a valid RegionType.
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected.

    Returns
    -------
    ansys.motorcad.core.geometry.Region
        Region object with two Line and one Arc entity types.
    """
    # calculate necessary angles for the coordinate calculation
    notch_start_angle = centre_angle - sweep / 2
    notch_end_angle = centre_angle + sweep / 2

    # generate coordinates for triangular notch using start/mid/end
    # angles above converting from polar to cartesian
    point_1 = Coordinate(*rt_to_xy(radius, notch_start_angle))
    point_2 = Coordinate(*rt_to_xy(radius, notch_end_angle))
    point_3 = Coordinate(*rt_to_xy(radius - depth, centre_angle))

    # using Triangle class, create a triangle with same vertices as the notch region.
    new_triangle = Triangle(point_1, point_2, point_3)

    # create the triangular notch region from the Triangle
    this_notch_region = new_triangle.get_region(region_type, motorcad_instance)

    # Replace the triangle base line with an Arc between the same points. Use the origin (rotor
    # centre) as the centre for drawing the Arc.
    this_notch_region.entities[0] = Arc(point_1, point_2, centre=Coordinate(0, 0), radius=radius)

    return this_notch_region


class Circle(EntityList):
    """Python representation of circle object based upon centre and radius.

    Parameters
    ----------
    centre : Coordinate
        Centre coordinate.

    radius : float
        Radius of the circle.
    """

    def __init__(self, centre: Coordinate, radius: int):
        """Initialise Circle object."""
        super().__init__()
        self.append(
            Arc(
                Coordinate(centre.x, centre.y - abs(radius)),
                Coordinate(centre.x, centre.y + abs(radius)),
                radius=abs(radius),
                centre=centre,
            )
        )
        self.append(
            Arc(
                Coordinate(centre.x, centre.y + abs(radius)),
                Coordinate(centre.x, centre.y - abs(radius)),
                radius=abs(radius),
                centre=centre,
            )
        )

    @property
    def centroid(self) -> Coordinate:
        """Centroid Coordinate of the Circle."""
        diameter = Line(self[0].start, self[1].start)
        return diameter.midpoint

    @property
    def radius(self) -> float:
        """Radius of the Circle."""
        return abs(self[0].start - self[1].start)


class ConvexPolygon(EntityList):
    """Python representation of a regular convex polygon object with N sides.

    A regular shape with N lines of equal length.

    Parameters
    ----------
    centre : Coordinate
        Centre coordinate.

    number_of_sides : int
        Number of sides of the shape.

    side_length : float
        Length of each side of the shape.
    """

    def __init__(self, centre: Coordinate, number_of_sides, side_length: float):
        """Initialise N-sided convex polygon object."""
        super().__init__()
        if number_of_sides < 3:
            raise TypeError("Polygon must have at least 3 sides.")
        y_diff = (side_length / 2) * (1 / math.tan(math.pi / number_of_sides))
        ref_point = Coordinate(centre.x - side_length / 2, centre.y - y_diff)
        last_point = ref_point
        for i in range(number_of_sides):
            new_point = Coordinate(ref_point.x, ref_point.y)
            new_point.rotate(centre, (i + 1) * (360 / number_of_sides))
            self.append(Line(last_point, new_point))
            last_point = new_point

    @property
    def centroid(self) -> Coordinate:
        """Centroid Coordinate of the Convex Polygon."""
        # if even number of sides
        n = len(self)
        if n % 2 == 0:
            y = Line(self[0].midpoint, self[int(n / 2)].midpoint)
            return y.midpoint
        else:
            line_a = Line(self[0].midpoint, self[int((n / 2) + 0.5)].start)
            line_b = Line(self[0].end, self[int((n / 2) + 0.5)].midpoint)
            return line_a.get_line_intersection(line_b)

    @property
    def angle(self) -> float:
        """Angle of the Convex Polygon.

        Zero when the base is parallel to the x-axis.
        """
        return self[0].angle


class Rectangle(EntityList):
    """Create a rectangle of given width and height from a corner Coordinate.

    Parameters
    ----------
    corner : Coordinate
        Corner coordinate to draw the rectangle from.
    width : float
        Width value.
    height : float
        Height value.
    """

    def __init__(self, corner: Coordinate, width: float, height: float):
        """Initialise Rectangle object."""
        super().__init__()

        # generate points
        points = [
            Coordinate(corner.x + width, corner.y),
            Coordinate(corner.x + width, corner.y + height),
            Coordinate(corner.x, corner.y + height),
            corner,
        ]

        # Generate lines
        last_point = points[-1]
        for point in points:
            self.append(Line(last_point, point))
            last_point = point

    @property
    def width(self) -> float:
        """Width of Rectangle."""
        return self[0].length

    @property
    def height(self) -> float:
        """Height of Rectangle."""
        return self[1].length

    @property
    def angle(self) -> float:
        """Angle of Rectangle.

        Zero when the base is parallel to the x-axis.
        """
        return self[0].angle

    @property
    def is_square(self) -> bool:
        """When True, width and height of the Rectangle are equal length."""
        if self.width == self.height:
            return True
        else:
            return False

    @property
    def centroid(self) -> Coordinate:
        """Centroid Coordinate of square."""
        median_lines = [
            Line(self[0].midpoint, self[2].midpoint),
            Line(self[1].midpoint, self[3].midpoint),
        ]
        centroid = median_lines[0].get_intersection(median_lines[1])
        if len(centroid) > 1:
            distance = centroid[0] - centroid[1]
            if distance < GEOM_SHAPE_TOLERANCE:
                return centroid[0]
            else:
                # could not find centroid
                return None
        else:
            return centroid[0]


class Triangle(EntityList):
    """Create a triangle from three Coordinates.

    Parameters
    ----------
    corner_1 : Coordinate
        First corner coordinate of triangle.
    corner_2 : Coordinate
        Second corner coordinate of triangle.
    corner_3 : Coordinate
        Third corner coordinate of triangle.
    """

    def __init__(self, corner_1: Coordinate, corner_2: Coordinate, corner_3: Coordinate):
        """Initialise Triangle object."""
        super().__init__()
        # generate points
        points = [
            corner_2,
            corner_3,
            corner_1,
        ]

        # generate lines
        last_point = points[-1]
        for point in points:
            self.append(Line(last_point, point))
            last_point = point

    @property
    def is_isosceles(self) -> bool:
        """When True the two non-base lines of the triangle are equal length."""
        if math.isclose(self[1].length, self[2].length, abs_tol=GEOM_SHAPE_TOLERANCE):
            return True
        else:
            return False

    @property
    def is_equilateral(self) -> bool:
        """When True, all three lines of the triangle are equal length."""
        if math.isclose(self[1].length, self[2].length, abs_tol=GEOM_SHAPE_TOLERANCE):
            if math.isclose(self[0].length, self[1].length, abs_tol=GEOM_SHAPE_TOLERANCE):
                return True
            else:
                return False
        else:
            return False

    @property
    def width(self) -> float:
        """Width of the Triangle."""
        if self.is_isosceles:
            width = self[0].length
        else:
            width = self._calculate_width()
        return width

    @property
    def height(self) -> float:
        """Height of the Triangle."""
        if self.is_isosceles:
            distance_vector = self[0].midpoint - self[1].end
            height = sqrt(distance_vector.x**2 + distance_vector.y**2)
        else:
            height = self._calculate_height()
        return height

    @property
    def angle(self) -> float:
        """Angle of the Triangle.

        Zero when the base is parallel to the x-axis.
        """
        return self[0].angle

    @property
    def centroid(self) -> Coordinate:
        """Centroid Coordinate of Triangle."""
        median_lines = [
            Line(self[0].start, self[1].midpoint),
            Line(self[1].start, self[2].midpoint),
            Line(self[2].start, self[0].midpoint),
        ]
        centroid = median_lines[0].get_intersection(median_lines[1])
        centroid.extend(median_lines[1].get_intersection(median_lines[2]))
        distance = []
        for i in range(len(centroid) - 1):
            point_1 = centroid[i]
            point_2 = centroid[i + 1]
            distance_vector = point_1 - point_2
            distance.append(sqrt(distance_vector.x**2 + distance_vector.y**2))
        if max(distance) < GEOM_SHAPE_TOLERANCE:
            return centroid[0]
        else:
            # could not find centroid
            return None

    def _calculate_height(self) -> float:
        """Calculate height of Triangle."""
        max_y = 0
        for point in self.points:
            point_rotated = Coordinate(point.x, point.y)
            point_rotated.rotate(self[0].start, -self.angle)
            if point_rotated.y - self[0].start.y > max_y:
                max_y = point_rotated.y - self[0].start.y
        return max_y

    def _calculate_width(self) -> float:
        """Calculate width of Triangle."""
        min_x = 1 / GEOM_SHAPE_TOLERANCE
        max_x = -1 / GEOM_SHAPE_TOLERANCE
        for point in self.points:
            point_rotated = Coordinate(point.x, point.y)
            point_rotated.rotate(self[0].start, -self.angle)
            if point_rotated.x < min_x:
                min_x = point_rotated.x
            elif point_rotated.x > max_x:
                max_x = point_rotated.x
        return max_x - min_x


def create_triangle_from_dimensions(corner: Coordinate, width=None, height=None) -> Triangle:
    """Create an Isosceles triangle of given width and height from a corner Coordinate.

    If only one of width and height are provided, an equilateral triangle will be created.

    Parameters
    ----------
    corner : Coordinate
        Corner coordinate to draw the triangle from.
    width : float, optional
        Width value.
    height : float, optional
        Height value.
    """
    # if width and height provided, draw an Isosceles triangle
    if width and height:
        pass
    # if only width provided:
    # * draw an equilateral triangle
    # * calculate height from width
    elif width:
        height = sqrt(3) * width / 2
    # if only height provided:
    # * draw an equilateral triangle
    # * calculate width from height
    elif height:
        width = 2 * height / sqrt(3)
    # if neither width nor height is provided, raise value error
    else:
        raise ValueError(
            "No width or height provided. You must provide the width and height for an "
            "Isosceles triangle. You must provide either the width or height for an equilateral"
            "triangle."
        )

    # generate points
    return Triangle(
        corner,
        Coordinate(corner.x + width, corner.y),
        Coordinate(corner.x + width / 2, corner.y + height),
    )


class Hexagon(ConvexPolygon):
    """Python representation of a regular hexagon object based upon centre and length of each side.

    A regular hexagon with 6 lines of equal length.

    Parameters
    ----------
    centre : Coordinate
        Centre coordinate.

    side_length : float
        Length of each side of the hexagon.
    """

    def __init__(self, centre: Coordinate, side_length: float):
        """Initialise Hexagon object."""
        super().__init__(centre, 6, side_length)

    @property
    def width(self) -> float:
        """Width of Hexagon in the direction parallel to the base."""
        return 2 * self[0].length

    @property
    def height(self) -> float:
        """Height of Hexagon in the direction perpendicular to the base."""
        return sqrt(3) * self[0].length
