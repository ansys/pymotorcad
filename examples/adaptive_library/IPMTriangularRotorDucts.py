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

# %%
# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Line
from ansys.motorcad.core.geometry_drawing import draw_objects_debug

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# Get adaptive parameters
mc.set_adaptive_parameter_default("Triangular Duct Corner Rad 1", 0.5)
mc.set_adaptive_parameter_default("Triangular Duct Corner Rad 2", 0.5)
corner_radius_1 = mc.get_adaptive_parameter_value("Triangular Duct Corner Rad 1")
corner_radius_2 = mc.get_adaptive_parameter_value("Triangular Duct Corner Rad 2")

# %%
# Get necessary objects from Motor-CAD
rotor = mc.get_region("Rotor")
duct = []
for region in rotor.children:
    if "DuctFluid" in region.name:
        duct.append(region)

# %%
# assume there is 1 duct region
# we will create a triangle with the same height and width as the standard template rectangular
# duct.
# The top two vertices of the rectangle will be unchanged, the bottom two vertices will be removed
# and the midpoint of the bottom line will be the new triangle point.
# Identify the line that will be unchanged:
duct = duct[0]
midpoint_radii = []
for entity in duct.entities:
    midpoint_radius, midpoint_th = entity.midpoint.get_polar_coords_deg()
    midpoint_radii.append(midpoint_radius)

triangle_top_line = duct.entities[midpoint_radii.index(max(midpoint_radii))]

# %%
# Find the new triangle point:
new_triangle_point = duct.entities[midpoint_radii.index(min(midpoint_radii))].midpoint

draw_objects_debug([rotor, duct, new_triangle_point])

# %%
# create the two new triangle lines
new_triangle_line_1 = Line(triangle_top_line.end, new_triangle_point)
new_triangle_line_2 = Line(new_triangle_point, triangle_top_line.start)

draw_objects_debug([rotor, triangle_top_line, new_triangle_line_1, new_triangle_line_2])

# %%
# Remove the unnecessary lines from the duct
entities_to_remove = []
for i in range(len(duct.entities)):
    if i != midpoint_radii.index(max(midpoint_radii)):
        entities_to_remove.append(duct.entities[i])

for entity in entities_to_remove:
    duct.remove_entity(entity)

# %%
# Add the new lines to the duct
duct.add_entity(new_triangle_line_1)
duct.add_entity(new_triangle_line_2)

draw_objects_debug([rotor, duct])

# %%
# round the corners
for point in duct.points:
    if point == new_triangle_point:
        duct.round_corner(point, corner_radius_1)
    else:
        duct.round_corner(point, corner_radius_2)

# %%
# set the modified duct in Motor-CAD
mc.set_region(duct)
