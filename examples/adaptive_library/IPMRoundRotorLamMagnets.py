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
Round Rotor Lamination and Magnet Corners
=========================================
This script applies the adaptive templates functionality to modify IPM rotor lamination and magnet
regions from having sharp corners to round corners.
"""
# %%
# .. note::
#    This adaptive templates example uses the geometry tree functionality introduced in Motor-CAD
#    v2026R1. The example is compatible with Motor-CAD v2026R1 and later.

# %%
# With Motor-CAD standard template geometry, we can define corner rounding for Rotor Lamination and
# Magnet regions, however the same radius is used for all magnet corners, and the same radius is
# used for all rotor lamination corners.
#
# With the Motor-CAD Adaptive Templates functionality, we can use the ``Region.round_corners``
# method to separately round regions. For example, for an IPM motor, we can define a one corner
# radius for layer 1 magnets, and a different corner radius for layer 2 magnets.
#
# This Adaptive Templates script sets up corner rounding for the e10 Motor-CAD template file,
# defining separate corner radii for magnets in layers 1 and 2, and separate corner radii for the
# rotor lamination pocket regions for the two magnet layers.

# %%
# .. image:: ../../images/adaptive_templates/IPM_rounded_3.png
#     :width: 600pt

# %%
# This script is designed to be run from Motor-CAD template "e10". If no Motor-CAD file is open, the
# e10 template will be loaded.
#
# This script uses the following adaptive parameters:
#
# * L1 Rotor Lam Corner Radius (0.9)
#
# * L1 Magnet Corner Radius (1.5)
#
# * L2 Rotor Lam Corner Radius (0.5)
#
# * L2 Magnet Corner Radius (1)
#
# If these parameters are not already set up in the Motor-CAD file, the parameters will be
# automatically set, with the default values shown in brackets.

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``deepcopy`` to define the adaptive template geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

from copy import deepcopy

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/IPM_rounded.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import RegionType

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened, the e10
# IPM motor template is loaded, the default **Corner Rounding (Rotor Lamination)** and
# **Corner Rounding (Magnets)** is set to **None (default)** and the file is saved to a temporary
# folder. To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance. Alternatively, use the
# ``MotorCAD()`` method, which closes the Motor-CAD instance after the script is executed.
# os.environ["PYMOTORCAD_DOCS_BUILD"] = "true"
if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e10")
    mc.set_variable("CornerRounding_Rotor", 0)
    mc.set_variable("CornerRounding_Magnets", 0)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e10_IPM_Round_Rotor_Lam_and_Magnets"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required
# ``L1 Rotor Lam Corner Radius``, ``L1 Magnet Corner Radius``, ``L2 Rotor Lam Corner Radius`` and
# ``L2 Magnet Corner Radius`` parameters if undefined.

mc.set_adaptive_parameter_default("L1 Rotor Lam Corner Radius", 0.9)
mc.set_adaptive_parameter_default("L1 Magnet Corner Radius", 1.5)
mc.set_adaptive_parameter_default("L2 Rotor Lam Corner Radius", 0.5)
mc.set_adaptive_parameter_default("L2 Magnet Corner Radius", 1)


# %%
# Get the corner radius adaptive parameter values.
L1_rotor_lam_corner_radius = mc.get_adaptive_parameter_value("L1 Rotor Lam Corner Radius")
L1_magnet_corner_radius = mc.get_adaptive_parameter_value("L1 Magnet Corner Radius")
L2_rotor_lam_corner_radius = mc.get_adaptive_parameter_value("L2 Rotor Lam Corner Radius")
L2_magnet_corner_radius = mc.get_adaptive_parameter_value("L2 Magnet Corner Radius")

# %%
# Get the standard template geometry tree. This can be used to get the magnet regions with
# corners to be rounded. Rotor pocket regions that correspond to the magnets will be
# obtained from the tree. The regions can be drawn for debugging if required.

geometry_tree = mc.get_geometry_tree()

# %%
# Create a dictionary object to store magnet and pocket geometry nodes from the geometry tree
regions_to_round = {}

# %%
# Get the magnet regions from the geometry tree. Find magnets using the RegionType attribute. Store
# the magnets in the ``regions_to_round`` dictionary.
regions_to_round["magnets"] = []
for node in geometry_tree:
    if node.region_type == RegionType.magnet:
        regions_to_round["magnets"].append(geometry_tree.get_node(node))

# %%
# Get the corresponding rotor pocket regions from the geometry tree. Check whether the magnet is a
# child of the rotor pocket. If so, the magnet is completely enclosed by the pocket.
#
# If there is no inner or outer magnet gap, there can be more than one rotor pocket per magnet, so
# the pocket regions are stored as a list.
#
# Store the rotor pockets in the ``regions_to_round`` dictionary along with a boolean to describe
# whether the magnet is a child of the rotor pocket. The indexing is set so that the corresponding
# dictionary items (magnet, rotor pocket list, boolean) have the same index in the dictionary.
regions_to_round["rotor pockets"] = []
regions_to_round["magnet is child of pocket?"] = []
for magnet in regions_to_round["magnets"]:
    magnet_rotor_pockets = []
    if magnet.parent.region_type == RegionType.rotor_pocket:
        magnet_rotor_pockets.append(magnet.parent)
        regions_to_round["magnet is child of pocket?"].append(True)
    else:
        regions_to_round["magnet is child of pocket?"].append(False)
        for node in geometry_tree:
            if node.region_type == RegionType.rotor_pocket:
                for point in node.points:
                    if point in magnet.points:
                        magnet_rotor_pockets.append(node)
                        break
    regions_to_round["rotor pockets"].append(magnet_rotor_pockets)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Create full rotor cutout regions, by uniting the corresponding magnet and rotor pocket
# regions. The corners of the full rotor cutout regions will be rounded to carry out the rotor
# lamination rounding. For the case where the magnet is a child region of the rotor pocket, the
# rotor pocket is already the full cutout region, so it is not necessary to unite regions.
#
# Store the full rotor cutout regions in the ``regions_to_round`` dictionary
# with indexing that corresponds to the magnets.
regions_to_round["full rotor cutouts"] = []
for i in range(len(regions_to_round["magnets"])):
    full_rotor_cutout = []
    magnet = deepcopy(regions_to_round["magnets"][i])
    rotor_pockets = deepcopy(regions_to_round["rotor pockets"][i])
    if regions_to_round["magnet is child of pocket?"][i]:
        regions_to_round["full rotor cutouts"].append(rotor_pockets)
    else:
        magnet.unite(rotor_pockets)
        magnet.key = f"Full Rotor Cutout_{i+1}"
        magnet.name = magnet.key
        full_rotor_cutout.append(magnet)
        regions_to_round["full rotor cutouts"].append(full_rotor_cutout)

# %%
# Round the corners of the magnet geometry regions using the ``round_corners`` Region method. To
# identify the magnet layer, check the magnet region name, which will contain "L1" for layer 1, "L2"
# for layer 2 etc.
for magnet in regions_to_round["magnets"]:
    if "L1" in magnet.name:
        magnet_radius = L1_magnet_corner_radius
    else:
        magnet_radius = L2_magnet_corner_radius
    magnet.round_corners(magnet.points, magnet_radius)

# %%
# Round the corners of the full rotor cutouts using the ``round_corners`` Region method. Check the
# magnet region name to determine which rotor lamination corner radius to use.
#
# Subtract the rounded magnet regions from their corresponding rounded full rotor cutout regions.
# This will result in rounded rotor pocket regions. If more than one rotor pocket region results
# from the ``subtract`` Region method, extra regions are returned. These are added to the
# ``full rotor cutouts`` item in the ``regions_to_round`` dictionary.
for i in range(len(regions_to_round["magnets"])):
    magnet = regions_to_round["magnets"][i]
    if "L1" in magnet.name:
        lam_radius = L1_rotor_lam_corner_radius
    else:
        lam_radius = L2_rotor_lam_corner_radius
    full_rotor_cutout = regions_to_round["full rotor cutouts"][i][0]
    full_rotor_cutout.round_corners(full_rotor_cutout.points, lam_radius)
    if not regions_to_round["magnet is child of pocket?"][i]:
        extras = full_rotor_cutout.subtract(magnet)
        regions_to_round["full rotor cutouts"][i].extend(extras)

# %%
# Update the rotor pocket regions in the geometry tree using the ``replace`` Region method. Replace
# original rotor pocket entities with entities from the rounded pockets.
for i in range(len(regions_to_round["magnets"])):
    original_pockets = regions_to_round["rotor pockets"][i]
    rounded_pockets = regions_to_round["full rotor cutouts"][i]
    for i in range(len(original_pockets)):
        original_pocket = original_pockets[i]
        rounded_pocket = rounded_pockets[i]
        original_pocket.replace(rounded_pocket)

# %%
# Set the updated geometry tree in Motor-CAD.
mc.set_geometry_tree(geometry_tree)

# %%
# .. image:: ../../images/adaptive_templates/IPM_rounded.png
#     :width: 600pt

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
