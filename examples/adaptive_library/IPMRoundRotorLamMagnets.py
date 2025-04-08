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
os.environ["PYMOTORCAD_DOCS_BUILD"] = "true"
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
# Define necessary functions
# --------------------------
# Corners to round
# ~~~~~~~~~~~~~~~~
# For a region that shares an entity with another region, create a list of corner coordinates to
# be rounded. Points that are shared by both regions are not to be rounded.
#
# For example: if the region to round is the rotor pocket shown below, where a line is shared with
# a magnet region, then a list of the points circled in green will be returned. The points circled
# in red (shared with the magnet region) are not returned by the function.

# %%
# .. image:: ../../images/adaptive_templates/IPM_rounded_1.png
#     :width: 600pt


def corners_to_round(region_to_round, other_regions):
    corner_list = []
    other_region_points = []
    if type(other_regions) == list:
        for other_region in other_regions:
            other_region_points.extend(other_region.points)
    else:
        other_region_points.extend(other_regions.points)

    for point in region_to_round.points:
        if point not in other_region_points:
            corner_list.append(point)
    return corner_list


# %%
# Get magnet cutout
# ~~~~~~~~~~~~~~~~~
# For a corresponding magnet and rotor pocket region, get a region that represents the entire region
# cutout of the rotor lamination.
#
# For example, for the rotor pocket and magnet regions, the entire region cutout is shown below.


# %%
# .. image:: ../../images/adaptive_templates/IPM_rounded_2.png
#     :width: 600pt
def get_magnet_cutout(magnets, pocket):
    # copy pocket region to create magnet cut out region
    magnet_cut_out = deepcopy(pocket)
    # Keep pocket properties but replace pocket entities with magnet entities
    if type(magnets) == list:
        magnets_utd = deepcopy(magnets[0])
        magnets_utd.unite(magnets[1])
        magnet_cut_out.replace(magnets_utd)
    else:
        magnet_cut_out.replace(magnets)
    # unite magnet cut out and original pocket to form entire magnet cut out region
    try:
        magnet_cut_out.unite(pocket)
    except:
        pocket.unite(magnets)
        magnet_cut_out.update(pocket)
    return magnet_cut_out


# %%
# Round magnet pockets
# ~~~~~~~~~~~~~~~~~~~~
# For a given magnet region and entire rotor pocket region (with magnet cutout), round the
# corresponding rotor pocket region using the ``Region.round_corners`` method and the
# ``corners_to_round`` function defined above.
def round_magnet_pockets(magnets, full_pocket, rotor_lam_corner_radius):
    if type(magnets) == list:
        for magnet in magnets:
            full_pocket.subtract(magnet)
    else:
        full_pocket.subtract(magnets)

    full_pocket.round_corners(corners_to_round(full_pocket, magnets), rotor_lam_corner_radius)


# %%
# Round magnet and pockets
# ~~~~~~~~~~~~~~~~~~~~~~~~
# For a given magnet region:
#
# * Get the corresponding rotor pocket regions.
#
# * Get the entire rotor pocket region using the ``get_magnet_cutout`` function defined above.
#
# * Round the magnet region corners using the ``Region.round_corners`` method.
#
# * Round the rotor pocket region corners using the ``round_magnet_pockets`` function defined above.
def round_magnet_and_pockets(
    magnet_region, rotor_region, magnet_corner_radius, rotor_lam_corner_radius
):
    # get corresponding pocket regions
    pockets = []
    for region in rotor_region.children:
        if "Pocket" in region.name:
            pocket_region = region
            for point in pocket_region.points:
                if point in magnet_region.points:
                    pockets.append(pocket_region)
                    break

    # get entire pocket
    for index in range(len(pockets)):
        pockets[index] = get_magnet_cutout(magnet_region, pockets[index])

    # round magnet
    magnet_region.round_corners(magnet_region.points, magnet_corner_radius)
    mc.set_region(magnet_region)

    # round pockets
    for index_1 in range(len(pockets)):
        if index_1 > 0:
            for index_2 in range(index_1):
                pockets[index_1].subtract(pockets[index_2])
        round_magnet_pockets(magnet_region, pockets[index_1], rotor_lam_corner_radius)
        mc.set_region(pockets[index_1])


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
# Get the necessary standard template regions. These are the magnet regions with corners to be
# rounded, and the rotor region. Rotor pocket regions that correspond to the magnets will be
# obtained from the list of rotor child regions. The regions can be drawn for debugging if
# required.

rotor = mc.get_region("Rotor")

L1_1Magnet2 = mc.get_region("L1_1Magnet2")
L1_1Magnet1 = mc.get_region("L1_1Magnet1")

L2_1Magnet2 = mc.get_region("L2_1Magnet2")
L2_1Magnet1 = mc.get_region("L2_1Magnet1")

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Use the ``round_magnet_and_pockets`` function to round the magnet regions and their corresponding
# rotor pocket regions.
round_magnet_and_pockets(L1_1Magnet2, rotor, L1_magnet_corner_radius, L1_rotor_lam_corner_radius)
round_magnet_and_pockets(L1_1Magnet1, rotor, L1_magnet_corner_radius, L1_rotor_lam_corner_radius)

round_magnet_and_pockets(L2_1Magnet2, rotor, L2_magnet_corner_radius, L2_rotor_lam_corner_radius)
round_magnet_and_pockets(L2_1Magnet1, rotor, L2_magnet_corner_radius, L2_rotor_lam_corner_radius)


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
