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
Round Parallel Slot Bottom
==========================
This script applies the adaptive templates functionality to modify parallel slot bottoms from
having square corners to round corners.
"""
# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD. Import ``draw_objects_debug`` to plot figures of
# geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/RoundParSlotBttm.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry_drawing import draw_objects_debug

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened, the e3
# WFSM motor template is loaded, the **Slot Type** is set to **Parallel Slot** and the file is saved
# to a temporary folder. To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance. Alternatively, use the
# ``MotorCAD()`` method, which closes the Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e3")
    mc.set_variable("SlotType", 2)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e3_WFSM_Round_Parallel_Slot"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required ``Slot Bttm Corner Radius``
# parameter if undefined.
mc.set_adaptive_parameter_default("Slot Bttm Corner Radius", 0.5)

# %%
# Get the slot bottom corner radius adaptive parameter value.
radius = mc.get_adaptive_parameter_value("Slot Bttm Corner Radius")

# %%
# Get the standard template regions with corners to be rounded. These can be drawn for debugging if
# required.
stator = mc.get_region("Stator")
winding_1 = mc.get_region("ArmatureSlotL1")
winding_2 = mc.get_region("ArmatureSlotR1")
stator_slot = mc.get_region("StatorSlot")
liner = mc.get_region("Liner")
impreg = mc.get_region("Impreg")

# %%
# Get the slot corner coordinates to be rounded. Plot the corner coordinates and the stator region
# using the ``draw_objects_debug`` function to ensure you have selected the correct points.
corners = [stator.entities[5].end, stator.entities[7].end]
draw_objects_debug([stator, corners[0], corners[1]])

# %%
# Define the impregration corner coordinates to be rounded. Draw the impregnation region and corner
# coordinates using the ``draw_objects_debug`` function.
impreg_corners = [impreg.entities[1].end, impreg.entities[3].end]
draw_objects_debug([stator, impreg, impreg_corners[0], impreg_corners[1]])

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Round the slot bottom corners for all regions that share these corner coordinates using the
# ``Region.round_corners`` method. Armature winding regions only have 1 of the two corners, so use
# the ``Region.round_corner`` method for these regions.
stator.round_corners(corners, radius)
stator_slot.round_corners(corners, radius)
liner.round_corners(corners, radius)
winding_1.round_corner(corners[1], radius)
winding_2.round_corner(corners[0], radius)

# %%
# Round the impregnation corners for the liner and impregnation regions using the
# ``Region.round_corners`` method.
liner.round_corners(impreg_corners, radius)
impreg.round_corners(impreg_corners, radius)

# %%
# Set the edited regions in Motor-CAD.
mc.set_region(stator)
mc.set_region(stator_slot)
mc.set_region(winding_1)
mc.set_region(winding_2)
mc.set_region(liner)
mc.set_region(impreg)

# %%
# .. image:: ../../images/adaptive_templates/RoundParSlotBttm.png
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
