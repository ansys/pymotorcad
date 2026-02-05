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

from ansys.motorcad.core import geometry
from ansys.motorcad.core.geometry import Arc, Line
from ansys.motorcad.core.geometry_shapes import (
    Circle,
    Rectangle,
    Triangle,
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

    triangle = Triangle(points[0], points[1], points[2])

    assert len(triangle) == 3
    assert triangle.is_closed

    for entity in triangle:
        assert isinstance(entity, geometry.Line)
        assert not triangle.is_equilateral
        assert triangle.is_isosceles


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
