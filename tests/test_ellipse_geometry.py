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

from math import sqrt

import pytest

from ansys.motorcad.core.geometry import GEOM_TOLERANCE, Arc, Coordinate, EntityList, Line
from ansys.motorcad.core.geometry_ellipse import Ellipse


@pytest.fixture(scope="function")
def simple_ellipse1():
    ellipse = EntityList()
    start = Coordinate(20, 0)
    end = Coordinate(0, 25)
    arc1 = Arc(start, Coordinate(12.07371797687105, 19.930556557981706), radius=29.020733180994984)
    arc2 = Arc(Coordinate(12.07371797687105, 19.930556557981706), end, radius=16.912499819563305)
    ellipse.append(arc1)
    ellipse.append(arc2)
    return ellipse


@pytest.fixture(scope="function")
def simple_ellipse2():
    ellipse = EntityList()
    p1 = Coordinate(20, 0)
    p2 = Coordinate(25.0979226410278, 12.08202697974112)
    p3 = Coordinate(21.313708498984763, 21.31370849898476)
    p4 = Coordinate(12.082026979741125, 25.0979226410278)
    p5 = Coordinate(0, 20)
    arc1 = Arc(p1, p2, radius=17.410542542997014)
    arc2 = Arc(p2, p3, radius=12.921306060296521)
    arc3 = Arc(p3, p4, radius=12.921306060296521)
    arc4 = Arc(p4, p5, radius=17.410542542997014)
    ellipse.append(arc1)
    ellipse.append(arc2)
    ellipse.append(arc3)
    ellipse.append(arc4)
    return ellipse


@pytest.fixture(scope="function")
def simple_ellipse3():
    ellipse = EntityList()
    p1 = Coordinate(20, 0)
    p2 = Coordinate(24.071236064510757, 9.840101601163148)
    p3 = Coordinate(19.899494936611667, 19.899494936611664)
    p4 = Coordinate(9.840101601163152, 24.071236064510757)
    p5 = Coordinate(0, 20)
    arc1 = Arc(p1, p2, radius=13.900084950663532)
    arc2 = Arc(p2, p3, radius=14.243232665293618)
    arc3 = Arc(p3, p4, radius=14.243232665293618)
    arc4 = Arc(p4, p5, radius=13.900084950663532)
    ellipse.append(arc1)
    ellipse.append(arc2)
    ellipse.append(arc3)
    ellipse.append(arc4)
    return ellipse


def test_ellipse_construction1(simple_ellipse1):
    # Test basic functionality
    p1 = Coordinate(20, 0)
    p2 = Coordinate(0, 25)
    origin = Coordinate(0, 0)
    ellipse = Ellipse(p1, p2, centre=origin, angle=0)
    assert simple_ellipse1 == ellipse


def test_ellipse_construction2():
    # Test depth construction
    p1 = Coordinate(20, 0)
    p2 = Coordinate(0, 20)
    ellipse = Ellipse(p1, p2, depth=16)
    max_dist = 0
    start = p1 - (p1 - p2) / 2
    for arc in ellipse:
        end = arc.end
        dist = Line(start, end).length
        if dist > max_dist:
            max_dist = dist
    assert 16 - GEOM_TOLERANCE <= max_dist <= 16 + GEOM_TOLERANCE


def test_ellipse_construction3(simple_ellipse2):
    # Test depth inversion
    p1 = Coordinate(20, 0)
    p2 = Coordinate(0, 20)
    ellipse = Ellipse(p1, p2, depth=-16)
    max_dist = 0
    start = p1 - (p1 - p2) / 2
    for arc in ellipse:
        end = arc.end
        dist = Line(start, end).length
        if dist > max_dist:
            max_dist = dist
    assert 16 - GEOM_TOLERANCE <= max_dist <= 16 + GEOM_TOLERANCE


def test_ellipse_construction4(simple_ellipse3):
    # Test depth construction when a minor axis is required
    p2 = Coordinate(20, 0)
    p1 = Coordinate(0, 20)
    ellipse = Ellipse(p1, p2, depth=14)
    min_dist = 100
    start = p1 - (p1 - p2) / 2
    for arc in ellipse:
        end = arc.end
        dist = Line(start, end).length
        if dist < min_dist:
            min_dist = dist
    assert 14 - GEOM_TOLERANCE <= min_dist <= 14 + GEOM_TOLERANCE


def test_ellipse_construction5():
    # Test shortcut to create an arc when necessary
    p1 = Coordinate(20, 0)
    p2 = Coordinate(0, 20)
    ellipse = Ellipse(p1, p2, depth=10 * sqrt(2))
    min_dist = 100
    start = p1 - (p1 - p2) / 2
    for arc in ellipse:
        end = arc.end
        dist = Line(start, end).length
        if dist < min_dist:
            min_dist = dist
    assert 10 * sqrt(2) - GEOM_TOLERANCE <= min_dist <= 10 * sqrt(2) + GEOM_TOLERANCE

    ellipse2 = Ellipse(p1, p2, centre=Coordinate(0, 0), angle=0)
    assert len(ellipse2) == 1


def test_ellipse_direction():
    # Test that ellipse by default passes to the right of the line connecting start and end
    p1 = Coordinate(10, 0)
    p2 = Coordinate(-10, 0)
    assert Ellipse(p1, p2, depth=5)[0].end.y > 0
    assert Ellipse(p2, p1, depth=5)[0].end.y < 0

    p3 = Coordinate(0, 10)
    p4 = Coordinate(0, -10)

    assert Ellipse(p3, p4, depth=5)[0].end.x < 0
    assert Ellipse(p4, p3, depth=5)[0].end.x > 0


def test_ellipse_reverse():
    # Test ordering
    p2 = Coordinate(20, 0)
    p1 = Coordinate(0, 25)
    ellipse = Ellipse(p1, p2, centre=Coordinate(0, 0), angle=0)
    assert ellipse.start == p1
    assert ellipse.end == p2


def test_ellipse_truncation():
    # Test ordering
    p2 = Coordinate(0, 25)
    p1 = Coordinate(-20, 0)
    ellipse = Ellipse(p2, p1, centre=Coordinate(0, 0), angle=0)
    assert ellipse.start == p2
    assert ellipse.end == p1


def test_ellipse_n():
    # Test manual precision
    p1 = Coordinate(25, 0)
    p2 = Coordinate(0, 20)
    ellipse = Ellipse(p1, p2, centre=Coordinate(0, 0), angle=0, n=2)
    assert len(ellipse) == 2
    ellipse = Ellipse(p1, p2, centre=Coordinate(0, 0), angle=0, n=5)
    assert len(ellipse) == 5


def test_ellipse_warnings_and_errors():
    origin = Coordinate(0, 0)
    # When eccentricity is required but not given
    with pytest.raises(Exception, match="Eccentricity must be given for mirrored points"):
        test_ellipse = Ellipse(Coordinate(10, 0), Coordinate(0, 10), angle=-45, centre=origin)

    # When points are not mirrored, but x1 = -x2, or y1 = -y2
    with pytest.raises(
        ZeroDivisionError, match="Invalid points: proposed shape must be an ellipse or elliptic arc"
    ):
        test_ellipse = Ellipse(Coordinate(20, 10), Coordinate(-30, -10), angle=0, centre=origin)

    # When points do not form an ellipse (more generally)
    with pytest.raises(
        ValueError, match="Invalid points: proposed shape must be an ellipse or elliptic arc"
    ):
        test_ellipse = Ellipse(Coordinate(5, 5), Coordinate(-4, 0), angle=0, centre=origin)

    # When automatic or manual selection of n may be too great
    with pytest.warns(
        UserWarning, match="Curvature may be too extreme. Less detail or curvature recommended"
    ):
        test_ellipse = Ellipse(Coordinate(2, 0), Coordinate(0, 1), n=50, angle=0, centre=origin)


def test_ellipse_mirror_detection():
    origin = Coordinate(0, 0)
    x = 10
    y = 10
    p1 = Coordinate(x, y)
    # Test each of the 3 reflections for which eccentricity is required
    with pytest.raises(Exception, match="Eccentricity must be given for mirrored points"):
        test_ellipse = Ellipse(p1, Coordinate(-x, y), angle=0, centre=origin)
    with pytest.raises(Exception, match="Eccentricity must be given for mirrored points"):
        test_ellipse = Ellipse(p1, Coordinate(-x, -y), angle=0, centre=origin)
    with pytest.raises(Exception, match="Eccentricity must be given for mirrored points"):
        test_ellipse = Ellipse(p1, Coordinate(x, -y), angle=0, centre=origin)
