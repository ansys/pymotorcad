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
import math

import pytest

from ansys.motorcad.core import geometry
from ansys.motorcad.core.geometry import GEOM_TOLERANCE, Arc, Line
from ansys.motorcad.core.geometry_shapes import (
    Circle,
    ConvexPolygon,
    Hexagon,
    Rectangle,
    Triangle,
    _square_coordinates,
    create_triangle_from_dimensions,
    eq_triangle_h,
    eq_triangle_w,
    square,
    triangular_notch,
)


def test_square():
    points = [
        geometry.Coordinate(-1, -1),
        geometry.Coordinate(-1, 1),
        geometry.Coordinate(1, 1),
        geometry.Coordinate(1, -1),
    ]
    test_square = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            test_square.add_entity(geometry.Line(point, points[0]))
        else:
            test_square.add_entity(geometry.Line(point, points[count + 1]))

    function_square = square(2, 0, 0)

    assert function_square == test_square


def test_square_coordinates():
    # test for old function that is deprecated
    points = [
        geometry.Coordinate(-1, 1),
        geometry.Coordinate(1, 1),
        geometry.Coordinate(1, -1),
        geometry.Coordinate(-1, -1),
    ]

    x0, y0, x1, y1, x2, y2, x3, y3 = _square_coordinates(2, 0, 0)
    assert math.isclose(x0, points[0].x, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(y0, points[0].y, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(x1, points[1].x, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(y1, points[1].y, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(x2, points[2].x, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(y2, points[2].y, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(x3, points[3].x, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(y3, points[3].y, abs_tol=GEOM_TOLERANCE)


def test_eq_triangle_h():
    points = [
        geometry.Coordinate(0.6666666666666667, 0.5773502691896257),
        geometry.Coordinate(0.6666666666666667, -0.5773502691896257),
        geometry.Coordinate(1.6666666666666665, 0.0),
    ]
    test_triangle = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            test_triangle.add_entity(geometry.Line(point, points[0]))
        else:
            test_triangle.add_entity(geometry.Line(point, points[count + 1]))

    function_triangle = eq_triangle_h(1, 1, 0)

    assert function_triangle == test_triangle


def test_eq_triangle_w():
    points = [
        geometry.Coordinate(0.666666666666666, 0.5773502691896257),
        geometry.Coordinate(0.6666666666666667, -0.5773502691896257),
        geometry.Coordinate(1.6666666666666665, 0.0),
    ]
    test_triangle = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            test_triangle.add_entity(geometry.Line(point, points[0]))
        else:
            test_triangle.add_entity(geometry.Line(point, points[count + 1]))

    function_triangle = eq_triangle_w(0.5773502691896257 * 2, 1, 0)

    assert function_triangle == test_triangle


def test_triangular_notch():
    p1 = geometry.Coordinate(-0.9999999999999996, 1.7320508075688774)
    p2 = geometry.Coordinate(6.123233995736766e-17, 1.0)
    p3 = geometry.Coordinate(1.0000000000000002, 1.7320508075688772)

    test_notch = geometry.Region()
    test_notch.add_entity(Line(p1, p2))
    test_notch.add_entity(Line(p2, p3))
    test_notch.add_entity(Arc(p3, p1, geometry.Coordinate(0, 0)))

    function_notch = triangular_notch(2, 60, 90, 1)

    assert function_notch == test_notch


def test_Circle():
    radius = 5
    centre = geometry.Coordinate(10, 10)

    circle = Circle(centre, radius)

    assert len(circle) == 2
    assert circle.is_closed
    for entity in circle:
        assert isinstance(entity, geometry.Arc)
        assert entity.radius == radius
        assert entity.centre == centre
    assert circle.radius == radius
    assert circle.centroid == centre


def test_Rectangle():
    width = 5
    height = 8
    corner = geometry.Coordinate(10, 10)

    rectangle = Rectangle(corner, width, height)

    assert len(rectangle) == 4
    assert rectangle.is_closed
    i = 0
    for entity in rectangle:
        assert isinstance(entity, geometry.Line)
        if i % 2 == 0:
            assert entity.length == width
        else:
            assert entity.length == height
        i += 1
    assert rectangle.centroid == geometry.Coordinate(12.5, 14)
    assert math.isclose(rectangle.angle, 0, abs_tol=GEOM_TOLERANCE)
    rectangle.rotate(rectangle.centroid, 15)
    assert math.isclose(rectangle.angle, 15, abs_tol=GEOM_TOLERANCE)
    assert not rectangle.is_square

    # remove a line and check that centroid cannot be returned
    rectangle.remove(rectangle[3])
    with pytest.raises(IndexError) as e:
        centre = rectangle.centroid
    assert "list index out of range" in str(e)

    # special case of Rectangle (square)
    width = 5
    corner = geometry.Coordinate(10, 10)

    this_square = Rectangle(corner, width, width)

    assert len(this_square) == 4
    assert this_square.is_closed
    for entity in this_square:
        assert isinstance(entity, geometry.Line)
        assert entity.length == width
    assert this_square.is_square


def test_Triangle():
    points = [geometry.Coordinate(1, 2.2), geometry.Coordinate(2.2, 1), geometry.Coordinate(4, 4)]

    triangle_i = Triangle(points[0], points[1], points[2])

    assert len(triangle_i) == 3
    assert triangle_i.is_closed

    for entity in triangle_i:
        assert isinstance(entity, geometry.Line)
    assert not triangle_i.is_equilateral
    assert triangle_i.is_isosceles
    assert math.isclose(triangle_i.width, 1.7, abs_tol=0.1)
    assert math.isclose(triangle_i.height, 3.4, abs_tol=0.1)
    assert math.isclose(triangle_i.angle, -45, abs_tol=0.01)

    # non isosceles triangle
    points = [geometry.Coordinate(1, 2.2), geometry.Coordinate(3, 1.5), geometry.Coordinate(4, 4)]

    triangle = Triangle(points[0], points[1], points[2])

    assert len(triangle) == 3
    assert triangle.is_closed

    for entity in triangle:
        assert isinstance(entity, geometry.Line)
    assert not triangle.is_equilateral
    assert not triangle.is_isosceles
    assert math.isclose(triangle.width, 2.2, abs_tol=0.1)
    assert math.isclose(triangle.height, 2.7, abs_tol=0.1)
    assert math.isclose(triangle.angle, -19.3, abs_tol=0.1)


def test_create_triangle_from_dimensions():
    width = 1.6970562748477143
    height = 3.394112549695428
    corner = geometry.Coordinate(1, 2.2)

    points = [geometry.Coordinate(1, 2.2), geometry.Coordinate(2.2, 1), geometry.Coordinate(4, 4)]

    triangle = create_triangle_from_dimensions(corner, width, height)

    assert len(triangle) == 3
    assert triangle.is_closed

    for entity in triangle:
        assert isinstance(entity, geometry.Line)
        assert not triangle.is_equilateral
        assert triangle.is_isosceles

    # rotate triangle to match the angle of the points.
    new_base_line = geometry.Line(points[0], points[1])
    triangle.rotate(corner, new_base_line.angle)

    for i in range(3):
        assert points[i] == triangle.points[i]

    # create an equilateral triangle EntityList
    triangle_eq = create_triangle_from_dimensions(corner, width)
    assert triangle_eq.is_equilateral

    # don't create triangle without necessary arguments
    with pytest.raises(ValueError) as e:
        triangle_err = create_triangle_from_dimensions(corner)
    assert "No width or height provided" in str(e)


def test_ConvexPolygon():
    centre = geometry.Coordinate(0, 0)
    length = 5
    max_sides_for_testing = 15

    for sides in range(max_sides_for_testing):
        if sides < 3:
            with pytest.raises(TypeError) as e_info:
                polygon = ConvexPolygon(centre, sides, length)
            assert "Polygon must have at least 3 sides" in str(e_info.value)
        else:
            polygon = ConvexPolygon(centre, sides, length)

            assert len(polygon) == sides
            assert polygon.is_closed
            for entity in polygon:
                assert isinstance(entity, geometry.Line)
            assert polygon.centroid == centre
            assert math.isclose(polygon.angle, 0, abs_tol=GEOM_TOLERANCE)
            polygon.rotate(centre, 15)
            assert math.isclose(polygon.angle, 15, abs_tol=GEOM_TOLERANCE)


def test_Hexagon():
    centre = geometry.Coordinate(0, 0)
    length = 5

    hexagon = Hexagon(centre, length)

    assert hexagon.is_closed
    assert len(hexagon) == 6
    for entity in hexagon:
        assert isinstance(entity, geometry.Line)
    assert hexagon.centroid == centre
    assert math.isclose(hexagon.angle, 0, abs_tol=GEOM_TOLERANCE)
    hexagon.rotate(centre, 15)
    assert math.isclose(hexagon.angle, 15, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(hexagon.width, 10, abs_tol=GEOM_TOLERANCE)
    assert math.isclose(hexagon.height, 8.7, abs_tol=0.1)
