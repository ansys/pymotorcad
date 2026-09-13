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

"""
Modifying the geometry of slot wedge ends to a triangular shape
===============================================================

This script applies the adaptive templates functionality to modify
the wedge region near the slot opening from having rectangle ends to pointed ends.
"""

# %%
# This script is designed to be run from the i7 Motor-CAD template (a 54 slot, form wound IM
# generator), however it should be compatible with any Motor-CAD models with form wound slots.
# If no Motor-CAD file is open, the i7 template is loaded.

# %%
# .. image:: ../../images/adaptive_templates/triangular_slot_wedge_1.png
#     :width: 500pt

# %%
# Perform required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD.
# Import the ``draw_objects`` function to plot images of Motor-CAD geometry objects.
# Import the ``RegionType``, ``Line``, ``Coordinate``, ``EntityList``, and ``Region`` objects
# to define the adaptive template geometry.
# Import the ``os``, ``shutil``, ``sys`` and ``tempfile`` packages

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/triangular_slot_wedge.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, Line, Region, RegionType
from ansys.motorcad.core.geometry_drawing import draw_objects

# %%
# Connect to Motor-CAD
# --------------------
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e7 IM generator template is loaded and the file is saved to a temporary folder. To keep a new
# Motor-CAD instance open after executing the script, use the ``MotorCAD(keep_instance_open=True)``
# option when opening the new instance. Alternatively, use the ``MotorCAD()`` method, which closes
# the Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("i7")

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e7_IM_Triangular_Slot_Wedge"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# Get required parameters and objects
# -----------------------------------
# Get the geometry tree object and use this to get the original wedge and stator regions.
gt = mc.get_geometry_tree()
wedge = gt.get_regions_of_type(RegionType.wedge)[0]
stator = gt.get_regions_of_type(RegionType.stator)[0]

# %%
# Get the geometry parameters from Motor-CAD that define the slot and wedge dimensions.
# These will be used to define the new hexagonal wedge geometry.
slot_width = mc.get_variable("Slot_Width")
wedge_inset = mc.get_variable("Wedge_Inset")
wedge_thickness = mc.get_variable("Wedge_Thickness")

# %%
# Create the Adaptive Templates geometry
# --------------------------------------

# %%
# Create construction regions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the necessary vertices for creating construction regions (a rectangle and a triangle)
# on the right-hand side of the wedge. The left-hand side will be created by mirroring the regions.
# Create these regions around the origin, with the wedge bottom parallel to the x-axis.
# The regions will subsequently be translated and rotated into the same coordinate system as the
# original wedge.

#             e
#   ______________ d
#  | /|       |\ |
#  |/ |       | \|
#  |\ |       | /| c
#  |_\|_______|/_|
#             a   b
point_a = Coordinate(slot_width / 2, -wedge_thickness / 2)
point_b = Coordinate(slot_width / 2 + wedge_inset, -wedge_thickness / 2)
point_c = Coordinate(slot_width / 2 + wedge_inset, 0)
point_d = Coordinate(slot_width / 2 + wedge_inset, +wedge_thickness / 2)
point_e = Coordinate(slot_width / 2, wedge_thickness / 2)

# %%
# Create a rectangle region that covers the portion of the original wedge that is inset in the
# stator on the right-hand side of the wedge. This will be used for modifying the original wedge and
# stator regions.
rectangle_r = Region(RegionType.stator_air, mc)
rectangle_r.entities.extend(
    [Line(point_a, point_b), Line(point_b, point_d), Line(point_d, point_e), Line(point_e, point_a)]
)

# %%
# Create a triangle region that covers the portion of the new wedge that is inset in the stator on
# the right-hand side of the wedge. This will be used for modifying the original wedge and stator
# regions.
triangle_r = Region(RegionType.wedge, mc)
triangle_r.entities.extend([Line(point_a, point_c), Line(point_c, point_e), Line(point_e, point_a)])

# %%
# Define a mirror line along the y-axis
mirror_line = Line(Coordinate(0, -10), Coordinate(0, 10))

# %%
# Create rectangle and triangle construction regions on the left side of the wedge
rectangle_l = rectangle_r.mirror(mirror_line)
triangle_l = triangle_r.mirror(mirror_line)

# %%
# Plot images of the rectangle and triangle regions
draw_objects([rectangle_r, triangle_r, rectangle_l, triangle_l])

# %%
# Transform the new construction regions into original coordinate system by translating and rotating
# based on the original wedge centroid and the angle of the bottom line of the original wedge.
for region in [rectangle_r, triangle_r, rectangle_l, triangle_l]:
    region.translate(wedge.centroid.x, wedge.centroid.y)
    region.rotate(wedge.centroid, wedge.entities[0].angle)

# %%
# Draw the construction regions along with the wedge to ensure that the transformation was correctly
# applied.
draw_objects([wedge, rectangle_r, triangle_r, rectangle_l, triangle_l])

# %%
# Modify the wedge region
# ~~~~~~~~~~~~~~~~~~~~~~~
# Modify the wedge region using the new construction regions (rectangles and triangles).
# First subtract the rectangles from the original wedge and draw the result.
wedge.subtract(rectangle_r)
wedge.subtract(rectangle_l)

draw_objects([wedge, triangle_r, triangle_l])

# %%
# Then unite the wedge with the triangular regions to create the new wedge geometry and draw the
# result.
wedge.unite(triangle_r)
wedge.unite(triangle_l)

draw_objects(wedge)

# %%
# Modify the stator region
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Modify the stator region using the new construction regions (rectangles and triangles).
# Unite the original stator region with the rectangle regions to fill in the original wedge cut-out.
stator.unite(rectangle_r)
stator.unite(rectangle_l)

# %%
# Subtract the triangular regions from the stator to cutout the new wedge geometry from the stator.
# Draw the resulting modified stator region.
stator.subtract(triangle_r)
stator.subtract(triangle_l)

draw_objects(stator)

# %%
# Set modified geometry in Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the geometry tree (which contains the modified wedge and stator regions) in Motor-CAD to
# update the geometry.
mc.set_geometry_tree(gt)

# %%
# Load in Adaptive Templates script if required
# ---------------------------------------------
# When this script is run externally, the script executes the following:
#
# * Set **Geometry type** to **Adaptive**.
#
# * Load the script into the **Adaptive Templates** tab.
#
# * Go to the **Geometry -> Radial** tab to run the Adaptive Templates script and display the new
#   geometry.

# %%
# .. note::
#    When running in a Jupyter Notebook, you must provide the path for the Adaptive Templates script
#    (PY file) instead of ``sys.argv[0]`` when using the ``load_adaptive_script()`` method.
# If this script is run externally, load the adaptive template script into Motor-CAD.
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
