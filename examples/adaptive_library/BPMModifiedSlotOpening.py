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
.. _ref_BPM_Modified_Slot_Opening:

Modified Stator Slot Opening
============================
Adaptive Template script to modify the shape of the stator slot opening.
"""
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
# This script uses the following adaptive parameters:
#
# * Depth Ratio (0.2)
#
# * Width Ratio (0.5)
#
#
# If these parameters are not already set up in the Motor-CAD file, the parameters will be
# automatically set, with the default values shown in brackets.
#
# To set an adaptive geometry for a Motor-CAD file, a script must be loaded in to the Adaptive
# Templates tab (Geometry -> Editor -> Adaptive Templates) in Motor-CAD and run. When the option
# 'Geometry Templates Type' is set to 'Adaptive', this script is automatically run repeatedly to
# keep the Adaptive Geometry set in Motor-CAD.
#
# This Python script can also be executed externally. When executed externally, a Motor-CAD instance
# will be launched and a file based on the "e10" template will be saved to a temporary folder. This
# script will be loaded into the Adaptive Templates tab.

# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD. Import os, tempfile and shutil to open and save a
# temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/ModifiedSlotOpening_tn.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, RegionType, rt_to_xy
from ansys.motorcad.core.geometry_drawing import draw_objects

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e10 IPM motor template is loaded and the file is saved to a temporary folder.
#
# This example works by adding a new band of air, separate to the airgap region, at the stator inner
# edge, and by reducing the size of the airgap in the standard template geometry. The airgap should
# be reduced while keeping the rotor and slot geometry unchanged, as well as the outer edge of the
# stator.
#
# The e10 template file is modified by reducing the airgap by a small amount (0.1 mm). To do so, the
# following parameters are modified:
#
# * **Airgap** set to **0.9 mm** (originally 1 mm),
#
# * **Tooth Tip Depth** to **1.1 mm** (originally 1 mm),
#
# * **Stator Bore** to **142.34 mm** (originally 142.54 mm),
#
# * **Slot Depth** to **13.93 mm** (originally 13.83 mm).
#
# A useful way to check that the correct parameters have been modified is to export the original
# geometry (with original airgap thickness) as a DXF file, and then import the DXF file. This means
# that the original geometry is displayed over the modified geometry.

# %%
# .. image:: ../../images/adaptive_templates/ModifiedSlotOpening_1.png
#     :width: 800pt

# %%
# To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

air_band_thickness = 0.1

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e10")

    # Set parameters
    airgap_orig = mc.get_variable("Airgap")
    mc.set_variable("Airgap", airgap_orig - air_band_thickness)
    tooth_tip_depth_orig = mc.get_variable("Tooth_Tip_Depth")
    mc.set_variable("Tooth_Tip_Depth", tooth_tip_depth_orig + air_band_thickness)
    stator_bore_orig = mc.get_variable("Stator_Bore")
    mc.set_variable("Stator_Bore", stator_bore_orig - 2 * air_band_thickness)
    slot_depth_orig = mc.get_variable("Slot_Depth")
    mc.set_variable("Slot_Depth", slot_depth_orig + air_band_thickness)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "BPMModifiedSlotOpening"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# Set Adaptive Parameters if required
# -----------------------------------
# Two Adaptive Parameters are required for this adaptive template. These are used to define the
# size of the stator notches to be added either side of the slot opening.
#
# If the Adaptive Parameters have already been set in the current Motor-CAD file, their current
# values will be used. Otherwise, the Adaptive Parameters will be defined and set to default values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required parameters if undefined.
mc.set_adaptive_parameter_default("Depth", 0.2)
mc.set_adaptive_parameter_default("Width", 0.5)


# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive Parameters specified in Motor-CAD, and their values
depth = mc.get_adaptive_parameter_value("Depth")
width = mc.get_adaptive_parameter_value("Width")

# %%
# Get the standard template stator and stator air regions from Motor-CAD. Calculate the outer radius
# of the airgap and the new stator inner edge radius.
stator = mc.get_region("Stator")
stator_air = mc.get_region("StatorAir")

airgap_outer_radius = stator.entities[-1].start.x
stator_new_inner_radius = airgap_outer_radius + air_band_thickness


# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Create the entities that form the new air band that will sit outside the airgap region. Create a
# new region for this air band. Combined with the airgap region, this results in the full airgap.
#
# Draw the air band and stator regions.
air_band = Region(RegionType.stator_air)
air_band.material = "Air"
air_band.colour = [255, 255, 255]
air_band.motorcad_instance = mc
air_band.parent = stator

air_band_entities = [
    Line(
        Coordinate(*rt_to_xy(airgap_outer_radius, 0)),
        Coordinate(*rt_to_xy(stator_new_inner_radius, 0)),
    ),
    Arc(
        Coordinate(*rt_to_xy(stator_new_inner_radius, 0)),
        Coordinate(*rt_to_xy(stator_new_inner_radius, 360 / stator.duplications)),
        centre=Coordinate(0, 0),
    ),
    Line(
        Coordinate(*rt_to_xy(stator_new_inner_radius, 360 / stator.duplications)),
        Coordinate(*rt_to_xy(airgap_outer_radius, 360 / stator.duplications)),
    ),
    Arc(
        Coordinate(*rt_to_xy(airgap_outer_radius, 360 / stator.duplications)),
        Coordinate(*rt_to_xy(airgap_outer_radius, 0)),
        centre=Coordinate(0, 0),
    ),
]
air_band.entities = air_band_entities

draw_objects([stator, air_band])

# %%
# To modify the slot opening, two triangular notch regions either side of the opening will be
# created. Use the adaptive parameter values and the original tooth tip depth and stator inner edge
# length to calculate the coordinates for the lower notch region (closest to the x-axis).
original_tooth_tip_depth = stator_air.entities[0].length - air_band_thickness
original_stator_inner_arc_length = (
    air_band.entities[1].length - stator_air.entities[-1].length
) / 2
depth_distance = original_tooth_tip_depth * depth
width_distance = original_stator_inner_arc_length * width

ref_point = stator_air.entities[0].get_coordinate_from_distance(
    stator_air.entities[0].start, air_band_thickness
)

new_depth_point = stator_air.entities[0].get_coordinate_from_distance(ref_point, depth_distance)
new_width_point = air_band.entities[1].get_coordinate_from_distance(ref_point, -width_distance)

# %%
# Create a notch region and define the entities using the new points.
notch = Region(RegionType.stator_air)
notch.motorcad_instance = mc
notch_entities = [
    Line(ref_point, new_width_point),
    Line(new_width_point, new_depth_point),
    Line(new_depth_point, ref_point),
]
notch.entities = notch_entities

# %%
# Create a mirror line and mirror the notch to create the second notch on the other side of the slot
# opening.
mirror_line = Line(
    Coordinate(0, 0), Coordinate(*rt_to_xy(stator_new_inner_radius, 180 / stator.duplications))
)
notch_mirrored = notch.mirror(mirror_line)

# %%
# Unite the air band and notch regions to form a full new air region.
air_band.unite([notch, notch_mirrored])

# %%
# Subtract the stator air region from the full new air region. This will return two new air band and
# notch regions.
air_band_regions = mc.subtract_region(air_band, stator_air)

# %%
# Set the new air regions in Motor-CAD. Previously, the air band region parent was set to the stator
# region. With the new air regions children of the stator, Motor-CAD automatically handles the
# region subtraction.
#
# Draw the regions to see the modification.
i = 1
for region in air_band_regions:
    region.name = f"StatorNotch{i}"
    mc.set_region(region)
    i += 1
draw_objects([stator, air_band_regions[0], air_band_regions[1], stator_air])


# %%
# Load in Adaptive Templates Script if required
# ---------------------------------------------
# When the script is run externally:
#
# * Set Geometry type to "Adaptive"
#
# * Load the script into the Adaptive Templates tab
#
# * Go to the Geometry -> Radial tab to run the Adaptive Templates Script and display the new
#   geometry


if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")

# %%
# .. image:: ../../images/adaptive_templates/ModifiedSlotOpening_2.png
#     :width: 800pt
