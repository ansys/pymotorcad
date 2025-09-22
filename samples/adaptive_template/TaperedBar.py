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

# Keywords: **Tapered Bar**, **Induction Motor**, **motor**
"""
Converting IM parallel tooth bar to tapered tooth bar
=========================================

This script applies the adaptive templates functionality to change
the points at the bottom of parallel tooth to create a tapered tooth bar geometry.
"""


import math
import sys

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, rt_to_xy, xy_to_rt

# Connect to Motor-CAD, using existing instance
# Alternatively, we could open a new instance and load a file with mc.load_from_file()
mc = pymotorcad.MotorCAD()

# Reset geometry to default
mc.reset_adaptive_geometry()

# Disable popup messages
mc.set_variable("MessageDisplayState", 2)


# function to return angle based on chord length
# Used for finding new point based on tooth width at bottom of bar
def chord_angle(cord_length, r):
    angle = 2 * math.asin(cord_length / (2 * r))
    return angle * 180 / math.pi


# Set IM motor type if not already
if not pymotorcad.is_running_in_internal_scripting():
    mc.load_template("i6a")


# Get the bar region
bar = mc.get_region("TopRotorBar")

# Get the points at the bottom corners of bar
# Point1 is away from x axis
point1 = bar.points[3]
point2 = bar.points[5]

# Get the top bar tooth width
# Define adaptive parameter for booth bar tooth width
tooth_width_top = mc.get_variable("Rotor_Tooth_Width_T")
mc.set_adaptive_parameter_default("Rotor Tooth Width Bottom", 4)
tooth_width_bottom = mc.get_adaptive_parameter_value("Rotor Tooth Width Bottom")

# Get the point 1 polar coordinates and modify
point1_r, point_1_t = xy_to_rt(point1.x, point1.y)
chord_length = (tooth_width_top - tooth_width_bottom) / 2
del_angle = chord_angle(chord_length, point1_r)
point1_t_new = point_1_t + del_angle

# Get the point 2 polar coordinates and modify
point2_r, point_2_t = xy_to_rt(point2.x, point2.y)
chord_length = (tooth_width_top - tooth_width_bottom) / 2
del_angle = chord_angle(chord_length, point2_r)
point_2_t_new = point_2_t - del_angle

# Get new region coordinates
x, y = rt_to_xy(point1_r, point1_t_new)
point1_new = Coordinate(x, y)
x, y = rt_to_xy(point2_r, point_2_t_new)
point2_new = Coordinate(x, y)

# Edit points at the bottom of the bar
bar.edit_point(point1, point1_new)
bar.edit_point(point2, point2_new)

# Set corner rounding if needed
bar.round_corner(point1_new, 0.2)
bar.round_corner(point2_new, 0.2)

# Set new region
mc.set_region(bar)

# If we're running this externally, load adaptive template script into Motor-CAD
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
