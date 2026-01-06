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

import numpy as np
import pytest

from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, RegionType
from ansys.motorcad.core.geometry_fitting import _EntityPointValidation, return_entity_list


def test_return_entity_list():
    c = []

    c.append(Coordinate(7, 11))
    c.append(Coordinate(20, 10))
    c.append(Coordinate(24, 7))
    c.append(Coordinate(24, 0))
    c.append(Coordinate(18, 0))
    c.append(Coordinate(15, 3))
    c.append(Coordinate(14, 5))
    c.append(Coordinate(6, 6))
    c.append(Coordinate(1, 6))
    c.append(Coordinate(1, 7))
    c.append(Coordinate(2, 7))

    # Duplicate coordinates
    c.append(Coordinate(3, 7))
    c.append(Coordinate(3, 7))
    c.append(Coordinate(3, 7))

    c.append(Coordinate(3.2, 7))
    c.append(Coordinate(3.4, 7))
    c.append(Coordinate(3.6, 7))
    c.append(Coordinate(4, 7))
    c.append(Coordinate(7, 11))

    e = return_entity_list(c, 0.001, 0.001)
    expected_points = [
        Coordinate(7, 11),
        Coordinate(24, 7),
        Coordinate(18, 0),
        Coordinate(14, 5),
        Coordinate(1, 6),
        Coordinate(2, 7),
        Coordinate(4, 7),
    ]
    assert e.points == expected_points
    assert isinstance(e[0], Arc)
    assert isinstance(e[1], Arc)
    assert isinstance(e[2], Arc)
    assert isinstance(e[3], Arc)
    assert isinstance(e[4], Arc)
    assert isinstance(e[5], Line)
    assert isinstance(e[6], Line)


def test__TestEntity():
    # Cover any lines of code missed by other tests
    c1 = Coordinate(0, 0)
    c2 = Coordinate(10, 0)

    points = [c1, c2]
    tolerance = 2

    test_entity = _EntityPointValidation("string", points, tolerance)
    with pytest.raises(TypeError):
        test_entity.is_in_tolerance()


def test__TestEntity_is_line_in_tolerance():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(5, 1)
    c3 = Coordinate(10, 0)

    points = [c1, c2, c3]
    l1 = Line(c1, c3)
    tolerance = 2

    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    tolerance = 1
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    tolerance = 0.9
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()


def test__TestEntity_is_arc_in_tolerance():
    centre = Coordinate(0, 0)
    c1 = Coordinate(5, 0)
    c2 = Coordinate(0, 5)
    l1 = Arc(c1, c2, centre, 5)

    tolerance = 1

    # Within angle and tolerance
    t1 = Coordinate.from_polar_coords(5.5, 45)
    points = [c1, t1, c2]
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    # Within angle and at max tolerance
    t1 = Coordinate(6, 0)
    points = [c1, t1, c2]
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    # Within angle and outside tolerance
    t1 = Coordinate.from_polar_coords(6.1, 45)
    points = [c1, t1, c2]
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()

    # Not within angle and in radial tolerance
    t1 = Coordinate.from_polar_coords(5, -45)
    points = [c1, t1, c2]
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()

    # Not within angle and in tolerance
    t1 = c1 - Coordinate(0.5, 0.5)
    assert not l1.coordinate_within_arc_radius(t1)
    points = [c1, t1, c2]
    test_entity = _EntityPointValidation(l1, points, tolerance)
    assert test_entity.is_in_tolerance()


def test_egg_shape():
    def yegg(x, L, B, w, D):
        """
        The "universal" formula for an egg, from Narushin et al., "Egg and math:
        introducing a universal formula for egg shape", *Ann. N.Y. Acad. Sci.*,
        **1505**, 169 (2021).

        x should vary between -L/2 and L/2 where L is the length of the egg; B
        is the maximum breadth of the egg; w is the distance between two vertical
        lines corresponding to the maximum breadth and y-axis (with the origin
        taken to be at the centre of the egg); D is the egg diameter at the point
        a distance L/4 from the pointed end.

        """
        fac1 = np.sqrt(5.5 * L**2 + 11 * L * w + 4 * w**2)
        fac2 = np.sqrt(L**2 + 2 * w * L + 4 * w**2)
        fac3 = np.sqrt(3) * B * L
        fac4 = L**2 + 8 * w * x + 4 * w**2
        return (
            (B / 2)
            * np.sqrt((L**2 - 4 * x**2) / fac4)
            * (
                1
                - (fac1 * (fac3 - 2 * D * fac2) / (fac3 * (fac1 - 2 * fac2)))
                * (
                    1
                    - np.sqrt(
                        L
                        * fac4
                        / (
                            2 * (L - 2 * w) * x**2
                            + (L**2 + 8 * L * w - 4 * w**2) * x
                            + 2 * L * w**2
                            + L**2 * w
                            + L**3
                        )
                    )
                )
            )
        )

    L = 1
    numpoints = 200
    x = np.linspace(-L / 2, L / 2, numpoints)
    y = yegg(x, L, 0.4, 0.1, 0.6)
    ymirror = np.flip(-y)
    xmirror = np.flip(x)
    xtotal = np.concatenate((x, xmirror))
    ytotal = np.concatenate((y, ymirror))

    xypoints = []
    for i in range(np.size(xtotal)):
        c = Coordinate(xtotal[i], ytotal[i])
        xypoints.append(c)

    linetolerance = 0.001
    arctolerance = 0.001
    egg_entities = return_entity_list(xypoints, linetolerance, arctolerance)

    egg_shaped_duct = Region(RegionType.stator_air)
    egg_shaped_duct.name = "Egg_shaped_duct"

    arccount = 0
    linecount = 0
    for ent in egg_entities:
        egg_shaped_duct.add_entity(ent)
        if isinstance(ent, Arc):
            arccount = arccount + 1
        if isinstance(ent, Line):
            linecount = linecount + 1

    assert arccount == 13
    assert linecount == 0
