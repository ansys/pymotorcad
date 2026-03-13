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
Bezier curve rotor pockets
==========================
This script applies the adaptive templates functionality to modify rotor pockets
with a custom curve defined using a Bezier function.
"""
# import copy
import math

# sphinx_gallery_thumbnail_path = 'images/Adaptive_Geometry_Bezier_e4a_3.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, EntityList, Line, get_bezier_points, rt_to_xy
from ansys.motorcad.core.geometry_drawing import draw_objects
from ansys.motorcad.core.geometry_fitting import return_entity_list

# %%
# .. note::
#    This script requires Motor-CAD 2024 R2 or later.

# %%
# This script is designed to be run from a Motor-CAD model based on the e4a template (a 48 slot,
# 8 pole IPM machine). The model is modified from the template by disabling corner rounding for the
# Standard Template geometry:
#
# * Set Corner Rounding (Rotor Lamination) to None (default).
#
# * Set Corner Rounding (Magnets) to None (default).


# %%
# .. image:: ../../images/Adaptive_Geometry_Bezier_e4a_1.png

# %%
# If no Motor-CAD file is open, the e4a template is loaded and the geometry is adjusted as
# described earlier.

# %%
# Perform required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD.
# Import the ``Coordinate``, ``Arc``, ``Line`` and ``rt_to_xy`` objects
# to define the adaptive template geometry.
# Import ``bezier`` used to draw the curve.
# Import the ``os``, ``shutil``, ``sys`` and ``tempfile`` packages
# to open and save a temporary MOT file if none is open.


# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e4a IPM motor template is loaded, the geometry changes described earlier are applied and the
# file is saved to a temporary folder. To keep a new Motor-CAD instance open after executing the
# script, use the ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e4a")

    # Disable corner rounding for Standard Template geometry ready for Adaptive Templates script
    mc.set_variable("CornerRounding_Rotor", 0)  # Rotor Lamination
    mc.set_variable("CornerRounding_Magnets", 0)  # Magnets

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "IPM_Pocket_Bezier"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Set adaptive parameter if required
# ----------------------------------
# The ``set_adaptive_parameter_default`` function checks if a parameter exists. If not,
# it creates the parameter with a default value.
# Set the required ``L1 Bezier Curve Projection``, ``L1 Upper Convex`` and ``L1 Lower Concave``
# parameters if undefined.
mc.set_adaptive_parameter_default("L1 Bezier Curve Projection", 4)
mc.set_adaptive_parameter_default("L1 Upper Convex", -0.3)
mc.set_adaptive_parameter_default("L1 Lower Concave", -0.2)
mc.set_adaptive_parameter_default("Rotor Lam Corner Radius", 0.5)
mc.set_adaptive_parameter_default("Magnet Corner Radius", 0.5)

# %%
# The adaptive parameters are used to define the curved rotor pocket geometry with a Bezier
# function. The parameters relate to the rotor pocket shape as follows:
#
# * ``L1 Bezier Curve Projection``: Defines the rotor pocket extension beyond the magnet edge in the
#   direction of the magnet length in mm.
#
# * ``L1 Upper Convex``: Defines the concave rotor pocket extension beyond the magnet edge in the
#   direction of the magnet thickness. This parameter is dependent on the magnet thickness (a
#   Standard Template parameter).
#
# * ``L1 Lower Concave``: Defines the convex rotor pocket curvature in the direction of the magnet
#   thickness. This parameter is dependent on the magnet thickness (a Standard Template parameter).
#
# .. image:: ../../images/Adaptive_Geometry_Bezier_e4a_2.png


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Get the standard template rotor region. This can be drawn for debugging if required.
rotor_region = mc.get_region("Rotor")
rotor_radius = mc.get_variable("RotorDiameter") / 2
poles = mc.get_variable("Pole_Number")
pole_angle = 360 / (poles * 2)

# %%
# Get the adaptive parameters specified in Motor-CAD, and their values
totalprojection = mc.get_adaptive_parameter_value("L1 Bezier Curve Projection")
upperconvex = mc.get_adaptive_parameter_value("L1 Upper Convex")
lowerconcave = mc.get_adaptive_parameter_value("L1 Lower Concave")
rotor_lam_corner_rad = mc.get_adaptive_parameter_value("Rotor Lam Corner Radius")
magnet_corner_rad = mc.get_adaptive_parameter_value("Magnet Corner Radius")

# %%
# Get the Rotor Pocket regions
Rotor_Pocket_regions = []
for i in rotor_region.child_names:
    if "Pocket" in i:
        Rotor_Pocket_regions.append(mc.get_region(i))

# %%
# Get the magnet regions
Magnet_regions = []
for i in rotor_region.child_names:
    if "Magnet" in i:
        Magnet_regions.append(mc.get_region(i))

# %%
# Find the magnet edge that is shared with the first rotor pocket
for magnet_region in Magnet_regions:
    for i in magnet_region.entities:
        for k in range(len(Rotor_Pocket_regions)):
            rotor_pocket_region = Rotor_Pocket_regions[k]
            MagnetFaceLine = rotor_pocket_region.find_entity_from_coordinates(i.start, i.end)
            if MagnetFaceLine is not None:
                break
        if MagnetFaceLine is not None:
            break


# %%
# Get properties of the magnet edge that are to be used to define the new rotor pocket geometry
# LineLength = MagnetFaceLine.length
StartCoordinate = MagnetFaceLine.start
pocket_end_first_point = MagnetFaceLine.end

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Find the start and end coordinates of the end section of the rotor pocket. These may not be the
# ends of the MagnetFaceLine if there is a gap between magnet and lamination on either long edge
# of the magnet.
distance_1 = 0
distance_2 = 0
for point in rotor_pocket_region.points:
    test_line = Line(point, MagnetFaceLine.end)
    if math.isclose(test_line.gradient, MagnetFaceLine.gradient, abs_tol=0.0001):
        if abs(point - MagnetFaceLine.end) > distance_1:
            distance_1 = abs(point - MagnetFaceLine.end)
            pocket_end_last_point = point
        elif abs(point - MagnetFaceLine.start) > distance_2:
            distance_2 = abs(point - MagnetFaceLine.end)
            pocket_end_first_point = point

pocket_end_line = Line(pocket_end_first_point, pocket_end_last_point)
LineLength = pocket_end_line.length

# draw_objects([rotor_pocket_region, pocket_end_first_point, pocket_end_last_point])

# # Remove all existing entities from the first rotor pocket
# Rotor_Pocket_regions[0].entities.clear()

# %%
# Define the x-y points that are to be used to draw the new rotor pocket. The points are defined
# relative to a vertical magnet edge (parallel to the y axis).

control_points = [
    Coordinate(0.0, 1 * LineLength),
    Coordinate(totalprojection * -0.5, (1 + upperconvex) * LineLength),
    Coordinate(-1 * totalprojection, 0.5 * LineLength),
    Coordinate(totalprojection * -0.5, -0.5 * LineLength),
    Coordinate(totalprojection * -0.25, (1 - 1 * lowerconcave) * LineLength),
    Coordinate(0.0, 0),
]

control_lines = []
last_point = control_points[0]
for i in range(len(control_points) - 1):
    this_point = control_points[i + 1]
    control_lines.append(Line(last_point, this_point))
    last_point = this_point


# %%
# Create set of points for drawing the calculated bezier curve
num_pts = 256
xylist = get_bezier_points(control_points, num_pts)

# %%
# Create a list of entities from the curve points
linetolerance = 0.01
arctolerance = 0.01
bez_curve_entities = return_entity_list(xylist, linetolerance, arctolerance)

# draw the control points and the resulting curve entities
to_draw = control_points
to_draw.extend(control_lines)
to_draw.extend(bez_curve_entities)
draw_objects(to_draw)

# # %%
# # Add the new entities that make up the curve to the first rotor pocket region
# # Counts the number of arcs and lines
# new_entities = []
# arccount = 0
# linecount = 0
# for ent in bez_curve_entities:
#     rotor_pocket_region.add_entity(ent)
#     if isinstance(ent, Arc):
#         arccount = arccount + 1
#     if isinstance(ent, Line):
#         linecount = linecount + 1

# %%
# Translate (move) the rotor pocket region in the x-y plane to the magnet edge
# Rotor_Pocket_regions[0].translate(pocket_end_last_point.x, pocket_end_last_point.y)
for entity in bez_curve_entities:
    entity.translate(pocket_end_last_point.x, pocket_end_last_point.y)
    entity.rotate(pocket_end_last_point, -(90 - MagnetFaceLine.angle))

# %%
# Rotate the rotor pocket region to match the magnet edge
# Rotor_Pocket_regions[0].rotate(StartCoordinate, -(90 - MagnetFaceLine.angle))

# %%
# # Add the magnet edge line to the rotor pocket region
# Rotor_Pocket_regions[0].add_entity(MagnetFaceLine)

# %%
# Add the existing entities to the rotor pocket region, skipping those between the start and end
# points of the pocket end.
entities_to_remove = []
remove_next = False
for i in range(len(rotor_pocket_region.entities)):
    entity = rotor_pocket_region.entities[i]
    if entity.start == pocket_end_first_point:
        entities_to_remove.append(entity)
        remove_next = True
    elif entity.end == pocket_end_last_point:
        entities_to_remove.append(entity)
        remove_next = False
    elif remove_next:
        entities_to_remove.append(entity)
# if the last entity was removed, start again and remove entities at the start of the list
for i in range(len(rotor_pocket_region.entities)):
    entity = rotor_pocket_region.entities[i]
    if entity.end == pocket_end_last_point:
        break
    else:
        entities_to_remove.append(entity)

draw_objects(entities_to_remove)

i = 0
add_new_entities = True
new_entity_list = EntityList()
for entity in rotor_pocket_region.entities:
    if entity in entities_to_remove:
        # rotor_pocket_region.remove_entity(entity)
        if add_new_entities:
            for new_entity in bez_curve_entities:
                new_entity_list.append(new_entity)
                # i += 1
            add_new_entities = False
    else:
        new_entity_list.append(entity)
        # i += 1

rotor_pocket_region.entities = new_entity_list
to_draw = [rotor_pocket_region]
draw_objects(to_draw, draw_points=True)

# %% Round the corners of the magnet and modified rotor pocket
rotor_pocket_region.unite(magnet_region)

# pocket corners to round:
bez_curve_points = []
for i in range(len(bez_curve_entities) - 1):
    entity = bez_curve_entities[i]
    bez_curve_points.append(entity.end)

corners_to_round = []
for point in rotor_pocket_region.points:
    if point not in bez_curve_points:
        corners_to_round.append(point)

rotor_pocket_region.round_corners(corners_to_round, rotor_lam_corner_rad)
magnet_region.round_corners(magnet_region.points, magnet_corner_rad)
rotor_pocket_region.subtract(magnet_region)
draw_objects([rotor_pocket_region, magnet_region])


# %%
# Check that the rotor pocket region is joined up and set the region in Motor-CAD
if Rotor_Pocket_regions[0].is_closed():
    mc.set_region(Rotor_Pocket_regions[0])
mc.set_region(magnet_region)

# %%
# Mirror the first rotor pocket region on the other half of the rotor. Define the mirror line from
# the origin and use the ``Region.mirror()`` method to create a new region named ``mirroredRegion``
# from the rotor pocket region.
mirrorlinex, mirrorliney = rt_to_xy(rotor_radius, pole_angle)
mirrorLine = Line(Coordinate(0, 0), Coordinate(mirrorlinex, mirrorliney))
mirroredRegion = rotor_pocket_region.mirror(mirrorLine)
mirrored_magnet = magnet_region.mirror(mirrorLine)

# %%
# Use the ``Region.replace()`` method to replace the entities in the second rotor pocket with those
# from the new ``mirroredRegion``. The properties of the second rotor pocket (such as name,
# material, colour) are retained.
Rotor_Pocket_regions[1].replace(mirroredRegion)
Magnet_regions[0].replace(mirrored_magnet)

# %%
# Check that the rotor pocket region is joined up and set the region in Motor-CAD
if Rotor_Pocket_regions[1].is_closed():
    mc.set_region(Rotor_Pocket_regions[1])
mc.set_region(Magnet_regions[0])
# %%
# .. image:: ../../images/Adaptive_Geometry_Bezier_e4a_3.png
#     :width: 300pt

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
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
