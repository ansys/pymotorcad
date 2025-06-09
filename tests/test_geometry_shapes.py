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

from ansys.motorcad.core import geometry
from ansys.motorcad.core.geometry import Arc, Line
from ansys.motorcad.core.geometry_shapes import (
    eq_triangle_h,
    eq_triangle_w,
    square,
    triangular_notch,
)


def test_square():
    points = [
        geometry.Coordinate(-1, 0),
        geometry.Coordinate(-1, 2),
        geometry.Coordinate(1, 2),
        geometry.Coordinate(1, 0),
    ]
    test_square = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            test_square.add_entity(geometry.Line(point, points[0]))
        else:
            test_square.add_entity(geometry.Line(point, points[count + 1]))

    function_square = square(2, 1, 0)

    assert function_square == test_square


def test_square_repositioning():
    points_upper = [
        geometry.Coordinate(1.8027756377319948, 1.8027756377319946),
        geometry.Coordinate(2.6348259320698384, 2.3574758339572237),
        geometry.Coordinate(3.1895261282950678, 1.5254255396193799),
        geometry.Coordinate(2.357475833957224, 0.9707253433941507),
    ]
    test_square_upper = geometry.Region()

    for count, point in enumerate(points_upper):
        if count == len(points_upper) - 1:
            test_square_upper.add_entity(geometry.Line(point, points_upper[0]))
        else:
            test_square_upper.add_entity(geometry.Line(point, points_upper[count + 1]))

    function_square_upper = square(1, 3, 45)

    assert function_square_upper == test_square_upper

    points_lower = [
        geometry.Coordinate(2.3533936216582085, 0.9805806756909203),
        geometry.Coordinate(3.333974297349129, 1.1766968108291045),
        geometry.Coordinate(3.5300904324873126, 0.19611613513818416),
        geometry.Coordinate(2.5495097567963922, 1.1102230246251565e-16),
    ]
    test_square_lower = geometry.Region()

    for count, point in enumerate(points_lower):
        if count == len(points_lower) - 1:
            test_square_lower.add_entity(geometry.Line(point, points_lower[0]))
        else:
            test_square_lower.add_entity(geometry.Line(point, points_lower[count + 1]))

    function_square_lower = square(1, 3, 0)

    assert function_square_lower == test_square_lower


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
