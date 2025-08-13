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
Oval Rotor Ducts
================
This scripts uses the adaptive templates functionality to add elliptical rotor ducts.
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
# This script is designed to be run from Motor-CAD template "e2", with Rotor Ducts set to
# 'Rectangular Ducts'. If no Motor-CAD file is open, the e2 template will be loaded, and Rotor
# Ducts set to 'Rectangular Ducts'.
#
#
# To set an adaptive geometry for a Motor-CAD file, a script must be loaded in to the Adaptive
# Templates tab (Geometry -> Editor -> Adaptive Templates) in Motor-CAD and run. When the option
# 'Geometry Templates Type' is set to 'Adaptive', this script is automatically run repeatedly to
# keep the Adaptive Geometry set in Motor-CAD.
#
# .. image:: ../../images/adaptive_templates/OvalRotorDucts_GUI.png
#
# This Python script can also be executed externally. When executed externally, a Motor-CAD instance
# will be launched and a file based on the "e2" template will be saved to a temporary folder. This
# script will be loaded into the Adaptive Templates tab.

# %%
# Perform Required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD. Import MotorCADError for error handling.
# Import the ``Ellipse`` function to create the duct geometry region with Adaptive Templates
# geometry. Import the ``os``, ``shutil``, ``sys``, and ``tempfile`` packages to open and save a
# temporary MOT file if none is open. Import various geometry functions to aid in
# building ellipses.

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/OvalRotorDucts.png'


import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, EntityList
from ansys.motorcad.core.geometry_ellipse import Ellipse

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e2 IPM motor template is loaded, and the file is saved to a temporary folder.
# To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
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
    mc.load_template("e2")

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "SPMOvalDuct"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

    mc.set_variable("RotorDuctType", 4)
    # Make ducts slightly larger to aid in visibility
    mc.set_variable("RotorCircularDuctLayer_ChannelHeight", 6)
    mc.set_variable("RotorCircularDuctLayer_ChannelWidth", 4)

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get the geometry tree to access and modify the motor's geometry
# ---------------------------------------------------------------
# A python representation of the defining geometry of the motor may be fetched at the beginning,
# modified throughout the script, then set at the end to apply the changes. In this case, some
# trimming may be necessary, as motorCAD may have split the duct into two regions to make sure its
# geometry is valid. Since such splitting may or may not be necessary for our new, updated duct
# geometry, it's best and easiest to simply get one duct to retrieve duct information, while
# removing any additional unnecessary ducts from the tree.

gt = mc.get_geometry_tree()

rotor_duct = gt["RotorDuctFluidRegion"]
try:
    gt.remove_node("RotorDuctFluidRegion_1")
except KeyError:
    pass

# %%
# Create and assign new geometry to duct
# --------------------------------------------------------------
# One could use the geometrical information already present within the ducts to generate the new
# ellipses. However, it is simpler in this case to simply retrieve the defining parameters and
# use those to rebuild the duct geometry from the ground up.
# Ellipses are by default drawn to the right of the line connecting their start and end points
# Therefore, the elliptic arc forming the top should go from the outer point to the inner one,
# and the bottom should be formed by reversing that order.

# -----------------------
# Get the duct information specified.
angle = float(mc.get_variable("RotorCircularDuctLayer_OffsetAngle").split(" : ")[0])
height = float(mc.get_variable("RotorCircularDuctLayer_ChannelHeight").split(" : ")[0])
width = float(mc.get_variable("RotorCircularDuctLayer_ChannelWidth").split(" : ")[0])
radius = float(mc.get_variable("RotorCircularDuctLayer_RadialDiameter").split(" : ")[0]) / 2

duplication_angle = 360 / rotor_duct.duplications

# Calculations are equivalent and made simpler for an angle restricted to the range
# [0, duplication_angle)
angle = angle % duplication_angle

inner_point = Coordinate.from_polar_coords(radius - (height / 2), angle)
outer_point = Coordinate.from_polar_coords(radius + (height / 2), angle)

upper_half = Ellipse(
    outer_point,
    inner_point,
    depth=width / 2,
)
lower_half = Ellipse(
    inner_point,
    outer_point,
    depth=width / 2,
)

# Reset the entities defining the ducts geometry to be the newly constructed ellipse
rotor_duct.entities = EntityList()
# Ellipses are in essence long lists of Arcs, so must be combined rather than appended to
# EntityLists
rotor_duct.entities += upper_half
rotor_duct.entities += lower_half

# %%
# Split the region if necessary and set it to MotorCAD
# ----------------------------------------------------
# In order to have valid geometry, a duct must not cross the line at its duplication angle;
# in fact, its geometry must remain in the angular range from 0 to its duplication angle.
# Regions placed on boundaries may still be used, but must be split into linked regions with
# defining geometry contained within the aforementioned section. This process is built into the
# GeometryTree function, fix_duct_geometry, which is applied below to the newly built duct.

gt.fix_duct_geometry(rotor_duct)

# %%
# Set the updated geometry tree to MotorCAD
# ----------------------------------------------------

mc.set_geometry_tree(gt)


# %%
# .. image:: ../../images/adaptive_templates/HalfEllipse.png

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
