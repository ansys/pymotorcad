# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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
Corner Rounding applied to IPM rotor
====================================
This script applies the adaptive templates functionality to modify magnets and rotor pockets in an
IPM rotor to have round (curved) corners.
"""
# %%
# This script uses the following adaptive parameters:
#
# * L1 Rotor Lam Corner Radius (0.6)
#
# * L1 Magnet Corner Radius (1.5)
#
# * L2 Rotor Lam Corner Radius (0.4)
#
# * L2 Magnet Corner Radius (1)
#
# This workflow allows a different corner radius to be applied to each magnet layer. It is an
# alternative to the Standard Template corner rounding options (found under **Input Data -> Settings
# -> Geometry**) which only allows a single corner radius definition for all magnet and all rotor
# lamination geometry components. When using Adaptive Templates, all corner rounding should be
# applied with Adaptive Templates and not using the Standard Template corner rounding option.
#
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Region``, ``deepcopy``
# to define the adaptive template geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

from copy import deepcopy

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/corner_rounding_thumbnail.png'
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
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e10 IPM motor template is loaded, the **Corner Rounding (Rotor Lamination)** and
# **Corner Rounding (Magnets)** options are set to **None (default)** and the file is saved to a
# temporary folder. To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance. Alternatively, use the
# ``MotorCAD()`` method, which closes the Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e10")

    # disable standard template corner rounding
    mc.set_variable("CornerRounding_Rotor", 0)
    mc.set_variable("CornerRounding_Magnets", 0)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e10_round_corners"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# %%
# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Define necessary functions
# --------------------------
# Set adaptive parameter if required
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``set_default_parameter`` function is defined to check if a parameter exists. If not,
# it creates the parameter with a default value.
def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Get list of child region objects
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``get_child_regions`` function is defined to get a list of region objects from a parent region
# with the ``in_region_name`` string in their name. For example, if ``in_region_name = Magnet`` and
# ``parent_region`` is the rotor region object, then the function returns a list of magnet objects.
def get_child_regions(in_region_name, parent_region):
    regions = []
    for name in parent_region.child_names:
        if in_region_name in name:
            regions.append(mc.get_region(name))
    return regions


# %%
# Get list of corresponding rotor pocket region objects for a magnet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``get_magnet_pocket_regions`` function is defined to get a list of rotor pocket region objects
# that share a coordinate with a magnet region.
def get_magnet_pocket_regions(pocket_regions, magnet_region):
    magnet_pockets = []
    for pocket_region in pocket_regions:
        for point in pocket_region.points:
            if point in magnet_region.points:
                magnet_pockets.append(pocket_region)
                break
    return magnet_pockets


# %%
# Get list of full rotor pocket regions for a magnet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``get_full_pocket_regions`` function is defined to combine the magnet and corresponding rotor
# pocket regions to get the full rotor pocket. This is required because the magnet cutout shape is
# not included in the rotor pocket.

# %%
# .. image:: ../../images/adaptive_templates/corner_rounding_1.png
#     :width: 800pt


def get_full_pocket_regions(magnets, rotor_pockets):
    full_pockets = []
    for index in range(len(magnets)):
        magnet = magnets[index]
        if len(rotor_pockets[index]) > 0:
            # copy pocket region to create full pocket region
            full_pocket = deepcopy(rotor_pockets[index][0])
            # Keep pocket properties but replace pocket entities with magnet entities
            full_pocket.replace(magnet)
            # Unite the magnet and pocket entities to form the full pocket region
            for rotor_pocket in rotor_pockets[index]:
                try:
                    full_pocket.unite(rotor_pocket)
                except:
                    rotor_pocket.unite(magnet)
                    full_pocket.update(rotor_pocket)
            full_pockets.append(full_pocket)
    return full_pockets


# %%
# Subtract magnet regions from full rotor pocket regions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``subtract_magnets_from_pockets`` function is defined to round the magnet corners of rotor
# pocket regions by subtracting magnet regions (with rounded corners) from corresponding full rotor
# pocket regions. For each magnet:
#
# * Subtract the rounded magnet region from the corresponding full pocket region using the
#   ``Region.subtract()`` method. Where magnet corners are shared by the magnet region and rotor
#   pocket region, the rounded magnet corners will be applied to the rotor pocket region as well.
#
#   * If this produces more than one rotor pocket region, the ``Region.subtract()`` method returns
#     the additional region objects.
#
#   * Change the name of any additional rotor pocket regions, applying the Standard Template rotor
#     pocket region names.
#
# * Set the modified rotor pocket regions in Motor-CAD.


# %%
# .. image:: ../../images/adaptive_templates/corner_rounding_2.png
#     :width: 800pt
def subtract_magnets_from_pockets(full_pockets, magnets, rotor_pockets):
    if len(full_pockets) > 0:
        for index in range(len(full_pockets)):
            full_pocket = full_pockets[index]
            magnet = magnets[index]
            # Subtract the rounded magnet from the full pocket and return any additional regions
            additional_pocket_regions = full_pocket.subtract(magnet)
            mc.set_region(full_pocket)
            x = 1
            for pocket in additional_pocket_regions:
                pocket.name = rotor_pockets[index][x].name
                mc.set_region(pocket)
                x += 1


# %%
# Get required parameters and objects
# -----------------------------------
# Use the ``set_default_parameter`` to set the required parameters if undefined
set_default_parameter("L1 Rotor Lam Corner Radius", 0.6)
set_default_parameter("L1 Magnet Corner Radius", 1.5)
set_default_parameter("L2 Rotor Lam Corner Radius", 0.4)
set_default_parameter("L2 Magnet Corner Radius", 1)

# %%
# Get the Adaptive Parameters specified in Motor-CAD, and their values
L1_rotor_lam_corner_radius = mc.get_adaptive_parameter_value("L1 Rotor Lam Corner Radius")
L1_magnet_corner_radius = mc.get_adaptive_parameter_value("L1 Magnet Corner Radius")
L2_rotor_lam_corner_radius = mc.get_adaptive_parameter_value("L2 Rotor Lam Corner Radius")
L2_magnet_corner_radius = mc.get_adaptive_parameter_value("L2 Magnet Corner Radius")

# %%
# Get the standard template rotor region. This can be drawn for debugging if required.
rotor = mc.get_region("Rotor")

# %%
# Use the ``get_child_regions`` function to get a list of all rotor pocket regions.

pocket_regions = get_child_regions("Rotor Pocket", rotor)

# %%
# Get the standard template magnet regions. The e10 template has 2 magnets in layer 1 (L1) and 2 in
# layer 2 (L2).

# %%
# .. note::
#    This script is designed to be run from Motor-CAD template "e10", where there are 2 **Magnet
#    Layers**, and the number of **Magnet Segments** is set to **1** for **L1** and **L2**. If the
#    model is modified to have a different magnet configuration, the script will require
#    modification to account for the different number of magnet regions.

L1_magnets = get_child_regions("L1_1Magnet", rotor)
L2_magnets = get_child_regions("L2_1Magnet", rotor)

# %%
# Account for the case where magnet regions are children of the rotor pocket regions (not the rotor
# region). This is the case when there the **Mag Gap Inner** and **Mag Gap Outer** are both more
# than zero.
if len(L1_magnets) == 0:
    for pocket_region in pocket_regions:
        L1_magnets.extend(get_child_regions("L1_1Magnet", pocket_region))

if len(L2_magnets) == 0:
    for pocket_region in pocket_regions:
        L2_magnets.extend(get_child_regions("L2_1Magnet", pocket_region))

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Sort the rotor pocket regions, so that the rotor pockets that correspond to each magnet layer are
# added to a list. The indices of the magnets and corresponding rotor pockets should match. Add the
# corresponding rotor pocket regions for each magnet to the ``L1_rotor_pockets`` and
# ``L2_rotor_pockets`` lists. These are the rotor pocket regions that share coordinates with a
# magnet region. Use the ``get_magnet_pocket_regions`` function to match pocket regions and
# magnet regions.

L1_rotor_pockets = []
for L1_magnet in L1_magnets:
    L1_rotor_pockets.append(get_magnet_pocket_regions(pocket_regions, L1_magnet))

L2_rotor_pockets = []
for L2_magnet in L2_magnets:
    L2_rotor_pockets.append(get_magnet_pocket_regions(pocket_regions, L2_magnet))

# %%
# Full rotor pockets are required so that the magnet corner rounding can be applied to the rotor
# pocket regions. A full rotor pocket is made up of a combined magnet cut out from the rotor and the
# corresponding rotor pockets. Use the ``get_full_pocket_regions`` function to get the regions.
L1_full_pockets = get_full_pocket_regions(L1_magnets, L1_rotor_pockets)
L2_full_pockets = get_full_pocket_regions(L2_magnets, L2_rotor_pockets)

# %%
# For each magnet in the layer, round the magnet region corners using the ``Region().round_corners``
# method and set the modified magnet regions in Motor-CAD.
for magnet in L1_magnets:
    magnet.round_corners(magnet.points, L1_magnet_corner_radius)
    mc.set_region(magnet)
for magnet in L2_magnets:
    magnet.round_corners(magnet.points, L2_magnet_corner_radius)
    mc.set_region(magnet)

# %%
# Round the full rotor pocket corners. Apply corner rounding to the external corners of the rotor
# pockets using the ``Region().round_corners`` method.

if len(L1_full_pockets) > 0:
    for index in range(len(L1_full_pockets)):
        if type(L1_full_pockets[index]) is list:
            for index_2 in range(len(L1_full_pockets[index])):
                full_pocket = L1_full_pockets[index][index_2]
                full_pocket.round_corners(full_pocket.points, L1_rotor_lam_corner_radius)
                mc.set_region(full_pocket)
        else:
            full_pocket = L1_full_pockets[index]
            full_pocket.round_corners(full_pocket.points, L1_rotor_lam_corner_radius)
            mc.set_region(full_pocket)
else:
    for rotor_pocket in pocket_regions:
        for name in rotor_pocket.child_names:
            if "L1" in name:
                rotor_pocket.round_corners(rotor_pocket.points, L1_rotor_lam_corner_radius)
                mc.set_region(rotor_pocket)

if len(L2_full_pockets) > 0:
    for index in range(len(L2_full_pockets)):
        if type(L2_full_pockets[index]) is list:
            for index_2 in range(len(L2_full_pockets[index])):
                full_pocket = L2_full_pockets[index][index_2]
                full_pocket.round_corners(full_pocket.points, L2_rotor_lam_corner_radius)
                mc.set_region(full_pocket)
        else:
            full_pocket = L2_full_pockets[index]
            full_pocket.round_corners(full_pocket.points, L2_rotor_lam_corner_radius)
            mc.set_region(full_pocket)
else:
    for rotor_pocket in pocket_regions:
        for name in rotor_pocket.child_names:
            if "L2" in name:
                rotor_pocket.round_corners(rotor_pocket.points, L2_rotor_lam_corner_radius)
                mc.set_region(rotor_pocket)
# %%
# Round the magnet corners of the pocket regions as well. For each magnet in the layer, subtract
# the magnet from the corresponding full rotor pocket and set the modified pocket region(s) in
# Motor-CAD using the ``subtract_magnets_from_pockets`` function.
subtract_magnets_from_pockets(L1_full_pockets, L1_magnets, L1_rotor_pockets)
subtract_magnets_from_pockets(L2_full_pockets, L2_magnets, L2_rotor_pockets)

# %%
# .. image:: ../../images/adaptive_templates/corner_rounding_result.png
#     :width: 800pt

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
