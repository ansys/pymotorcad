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
from ansys.motorcad.core.geometry import Arc, RegionType
from ansys.motorcad.core.geometry_shapes import circular_notch


def test_circular_notch():
    p1 = geometry.Coordinate(-0.9999999999999996, 1.7320508075688774)
    p2 = geometry.Coordinate(6.123233995736766e-17, 1.0)
    p3 = geometry.Coordinate(1.0000000000000002, 1.7320508075688772)

    test_notch = geometry.Region(region_type=RegionType.stator)
    test_notch.add_entity(Arc.from_coordinates(p1, p2, p3))
    test_notch.add_entity(Arc(p3, p1, geometry.Coordinate(0, 0)))

    function_notch = circular_notch(2, 60, 90, 1)

    assert function_notch == test_notch
