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
from matplotlib import pyplot as plt
import pytest

from ansys.motorcad.core.geometry import Coordinate, Line, Region, RegionType
import ansys.motorcad.core.geometry_drawing
from ansys.motorcad.core.geometry_drawing import draw_objects

# from ansys.motorcad.core.rpc_client_core import DEFAULT_INSTANCE, set_default_instance

drawing_flag = False


def set_drawing_flag(*args, **kwargs):
    global drawing_flag
    drawing_flag = True


def create_triangle_reg(bottom_left_coord):
    region = Region(RegionType.stator_air)
    region.name = "region " + str(bottom_left_coord)
    c1 = bottom_left_coord
    c2 = bottom_left_coord + Coordinate(10, 0)
    c3 = bottom_left_coord + Coordinate(5, 5)
    region.add_entity(Line(c1, c2))
    region.add_entity(Line(c2, c3))
    region.add_entity(Line(c3, c1))
    return region


def test_label_recursion(monkeypatch):
    # Stop plt.show() blocking tests
    global drawing_flag
    drawing_flag = False
    monkeypatch.setattr(plt, "show", set_drawing_flag)

    # add your geometry template here using PyMotorCAD
    r1 = create_triangle_reg(Coordinate(0, 0))
    r2 = create_triangle_reg(Coordinate(0, 0.2))
    r3 = create_triangle_reg(Coordinate(0, 0.1))

    draw_objects([r1, r2, r3])

    monkeypatch.setattr(ansys.motorcad.core.geometry_drawing, "_MAX_RECURSION", 1)
    with pytest.warns():
        draw_objects([r1, r2, r3])


# def test_draw_objects_debug(mc, monkeypatch):
#     # Just check it runs for now
#     # Stop plt.show() blocking tests
#     global drawing_flag
#     drawing_flag = False
#     monkeypatch.setattr(plt, "show", set_drawing_flag)
#
#     region = mc.get_region("Stator")
#
#     draw_objects_debug(region)
#     assert drawing_flag is True
#
#     drawing_flag = False
#     save_def_instance = DEFAULT_INSTANCE
#     set_default_instance(mc.connection._port)
#
#     draw_objects_debug(region)
#     assert drawing_flag is False
#
#     set_default_instance(save_def_instance)


# def test_draw_objects(mc, monkeypatch):
#     # Just check it runs for now
#     # Stop plt.show() blocking tests
#     global drawing_flag
#     drawing_flag = False
#
#     monkeypatch.setattr(plt, "show", set_drawing_flag)
#
#     region = mc.get_region("Stator")
#     region2 = mc.get_region("StatorWedge")
#     region3 = mc.get_region("ArmatureSlotL1")
#
#     draw_objects(region)
#     assert drawing_flag is True
#     draw_objects([region, region2, region3])
#
#     # Test overflow of colours
#     region4 = mc.get_region("StatorAir")
#     region5 = mc.get_region("Shaft")
#     draw_objects([region, region2, region3, region4, region5])
#
#     # Test object drawing
#     c1 = Coordinate(0, 0)
#     c2 = Coordinate(4, 0)
#     c3 = Coordinate(4, 4)
#
#     l1 = Line(c1, c2)
#     a1 = Arc(c1, c3, c2, -4)
#     draw_objects(l1)
#     draw_objects([l1, a1])
#
#     draw_objects([c1, c2])
#
#     # Test missing object doesn't break function
#     draw_objects([c1, c2, None])
#
#     with pytest.raises(TypeError):
#         draw_objects([int(10)])
