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
Round Magnets for Axial Flux BPM
================================
This script applies the adaptive templates functionality to modify magnets into round shapes.
"""
# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD. Import ``draw_objects`` to plot figures of geometry
# objects.
# Import ``RegionMagnet``, ``Coordinate`` and ``Arc`` for creating adaptive templates geometry
# objects.
# Import ``math`` for calculating new geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

import math

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/axial_flux_round_magnet.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, RegionMagnet

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur:
#
# * open a new Motor-CAD instance,
#
# * load the e14 Axial Flux BPM motor template,
#
# * save the file to a temporary folder.
# To keep a new Motor-CAD instance open after executing the script, use the
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
    mc.load_template("e14")

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e14_AFM_Round_Magnets"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the required standard template parameter values and the adaptive parameters
# and their values.
#
# Get original magnet regions
old_magnet_region = [mc.get_region("1Magnet1"), mc.get_region("1Magnet2")]

# Get required parameters
magnet_embed_depth = mc.get_variable("Magnet_Embed_Depth")
rotor_lam_diameter = mc.get_variable("AFM_D_Rotor")
pole_number = mc.get_variable("Pole_Number")

# %%
# Use the ``get_adaptive_parameter_value`` method to add the adaptive parameters
mc.set_adaptive_parameter_default("Magnet Radius", 13)

# %%
# Get adaptive parameters
magnet_radius = mc.get_adaptive_parameter_value("Magnet Radius")

# %%
# Set magnet thickness based on radius parameter.
mc.set_variable("Magnet_Thickness", 2 * magnet_radius)

# %%
# Compute magnet radius from rotor center to magnet center
radius_magnet_center = rotor_lam_diameter / 2 - magnet_embed_depth - magnet_radius

# Limit magnet radius to avoid crossing symmetry boundary
max_magnet_radius = (2 * math.pi * radius_magnet_center / pole_number) / 2
if magnet_radius * 2 > 2 * math.pi * radius_magnet_center / pole_number:
    magnet_radius = max_magnet_radius
    mc.show_message(f"Adaptive Parameter: 'Magnet Radius' too large, reset to {magnet_radius}")
    mc.set_adaptive_parameter_value("Magnet Radius", magnet_radius)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Create new round magnet region
# Properties
new_magnet_region = RegionMagnet()

# %%
# Circle parameters
angle = 360 / (pole_number * 2) * math.pi / 180
cx = math.cos(angle) * radius_magnet_center
cy = math.sin(angle) * radius_magnet_center

# %%
# Draw circular magnet using arcs
pts = [
    Coordinate(cx + magnet_radius, cy),
    Coordinate(cx, cy + magnet_radius),
    Coordinate(cx - magnet_radius, cy),
    Coordinate(cx, cy - magnet_radius),
    Coordinate(cx + magnet_radius, cy),
]

for i in range(4):
    new_magnet_region.add_entity(Arc(pts[i], pts[i + 1], centre=Coordinate(cx, cy)))

# %%
# Replace the old region geometry for both original magnets, validate and set the modified regions
# in Motor-CAD.
for magnet in old_magnet_region:
    magnet.replace(new_magnet_region)
    if new_magnet_region.is_closed():
        mc.set_region(magnet)
    else:
        raise RuntimeError("Circular region not closed")

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
