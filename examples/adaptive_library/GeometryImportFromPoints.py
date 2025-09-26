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

"""
.. _ref_Geometry_Import_From_Points:

Geometry Import from Points
===========================
Adaptive Template script to update magnet pockets from external X/Y points.
"""
# %%
# .. image:: ../../images/Adaptive_Geometry_FromPoints.png

# %%
# .. note::
#    For more information on the use of Adaptive Templates in Motor-CAD, and how to create, modify
#    and debug Adaptive Templates Scripts, see :ref:`ref_adaptive_templates_UG` in the
#    :ref:`ref_user_guide`.
#
# .. note::
#    Adaptive Templates in Motor-CAD require v2024.1.2 (Motor-CAD 2024 R1 Update) or later and
#    PyMotorCAD v0.4.1. To update PyMotorCAD in Motor-CAD, go to Scripting -> Settings -> PyMotorCAD
#    updates and select 'Update to Latest Release'.
#
# This script is designed to be run from Motor-CAD template "e10". If no Motor-CAD file is open, the
# e10 template will be loaded.
#
# Overview
# --------
#
# Using PyMotorCAD's geometry fitting tools, a series of
# points can be imported (for example the nodal coordinates
# on the boundary of a FEA mesh that has been optimised for stress),
# and these points used to construct a series of lines and arcs to
# represent the geometry.
#
# Required files
# --------------
# The files Pocket_1.txt, Pocket_2.txt, Pocket_3.txt, and Pocket_4.txt should be downloaded and
# placed in the same folder as the mot file. These can be downloaded from
# https://github.com/ansys/pymotorcad/blob/main/examples/adaptive_library/Points/
#
#
# Example model
# -------------
#
# In this case, the Motor-CAD e10 template is used as a starting point,
# and the following modifications made to the standard geometry:
#
# *To avoid interference between magnet and lamination:*
#
# * L1 magnet separation changed from 2.84 to 2.8 mm
# * L2 magnet separation changed from 1.56 to 1.5 mm
#
# *To create a small clearance between magnet and pocket, so small differences
# in imported geometry do not cause errors:*
#
# * L1 and L2 mag gap outer set to 0.01
#
# Sorting points
# --------------
#
# In this example, the points are loaded from one text file for each rotor
# pocket. However, the points are not in order (because they are exported from
# an external FEA mesh, and the nodal numbering is not increasing monotonically
# around the rotor pocket.
#
# Therefore the points must be sorted before use. In this case, we can use a
# simple approach, where we choose a starting point, and then find the closest
# point. From the second point, we then find the closest point, until all points
# have been used. This method will fail in cases with coarse point spacing and
# acute angles, but works well for smooth curves as we have here.


# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD

import math
import os
import pathlib
import sys

# sphinx_gallery_thumbnail_path = 'images/Adaptive_Geometry_FromPoints.png'
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate
from ansys.motorcad.core.geometry_fitting import return_entity_list

# %%
# Utility function to get distance between two coordinates
# --------------------------------------------------------


def coordinate_distance(coordinate_1, coordinate_2):
    rel_x = coordinate_1.x - coordinate_2.x
    rel_y = coordinate_1.y - coordinate_2.y
    return math.sqrt(rel_x * rel_x + rel_y * rel_y)


# %%
# Update region based on text file of X and Y points
# --------------------------------------------------


def replace_magnet_pocket(
    motor_cad, pocket_name, magnet_name, file_name, line_tolerance, arc_tolerance
):
    xy_coord_file = open(file_name, "r")
    data_lines = xy_coord_file.readlines()
    xy_coord_file.close()

    xy_data = []
    for data_line in data_lines:
        split_line = data_line.split()
        # Read data. split_line[[0] is node ID, which we ignore. Also, convert from m to mm
        xy_data.append(Coordinate(float(split_line[1]) * 1000, float(split_line[2]) * 1000))

    # Sort the xy_data to get a continuous line (join-the-dots!)
    # Note this may fail if we have sharp internal corners, where the next point isn't the closest
    # If this is a problem, we could weight the distance by how the target point aligns with the
    # direction of the previous line segment.
    xy_data_sorted = []
    # Always start at the first point in the list, then find the next closed unused point
    xy_data_sorted.append(xy_data.pop(0))
    while len(xy_data) > 0:
        min_dist = 1e9  # Initial large value
        min_index = 0  # Initial assumption
        for point_id in range(len(xy_data)):
            dist = coordinate_distance(xy_data_sorted[-1], xy_data[point_id])
            if dist < min_dist:
                min_dist = dist
                min_index = point_id
        xy_data_sorted.append(xy_data.pop(min_index))

    # Duplicate the first point as the last point, so we get a closed region
    xy_data_sorted.append(xy_data_sorted[0])

    # Curve fitting to these points
    curve_entities = return_entity_list(xy_data_sorted, line_tolerance, arc_tolerance)

    rotor_pocket = motor_cad.get_region(pocket_name)
    rotor_pocket.entities.clear()
    for entity in curve_entities:
        rotor_pocket.add_entity(entity)

    magnet_region = motor_cad.get_region(magnet_name)
    magnet_region.parent = rotor_pocket

    if rotor_pocket.is_closed():
        motor_cad.set_region(rotor_pocket)

    motor_cad.set_region(magnet_region)


# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e10 IPM motor template is loaded, the geometry changes described earlier are applied and the
# file is saved. To keep a new Motor-CAD instance open after executing the
# script, use the ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e10")
    mc.save_to_file(os.getcwd() + "/ModifiedPocketE10.mot")

    # Set Standard Template geometry ready for Adaptive Templates script
    mc.set_array_variable(
        "MagnetSeparation_Array", 0, 2.8
    )  # L1 magnet separation changed from 2.84 to 2.8 mm
    mc.set_array_variable(
        "MagnetSeparation_Array", 1, 1.5
    )  # L2 magnet separation changed from 1.56 to 1.5 mm
    mc.set_array_variable(
        "VShape_Magnet_ClearanceOuter", 0, 0.01
    )  # L1 and L2 mag gap outer set to 0.01
    mc.set_array_variable(
        "VShape_Magnet_ClearanceOuter", 1, 0.01
    )  # L1 and L2 mag gap outer set to 0.01


# Reset geometry to default
mc.reset_adaptive_geometry()

# Find the mot 'Points' directory, where the .txt files should be stored
mot_file = pathlib.Path(mc.get_file_name())
point_folder = mot_file.parent / "Points"

# Replace pocket geometry from (Node, X, Y) list in file
replace_magnet_pocket(mc, "Rotor Pocket", "L1_1Magnet2", point_folder / "Pocket_1.txt", 0.01, 0.01)
replace_magnet_pocket(
    mc, "Rotor Pocket_1", "L1_1Magnet1", point_folder / "Pocket_2.txt", 0.01, 0.01
)
replace_magnet_pocket(
    mc, "Rotor Pocket_2", "L2_1Magnet2", point_folder / "Pocket_3.txt", 0.01, 0.01
)
replace_magnet_pocket(
    mc, "Rotor Pocket_3", "L2_1Magnet1", point_folder / "Pocket_4.txt", 0.01, 0.01
)

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

if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
