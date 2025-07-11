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
# 'Rectangular Ducts'. If no Motor-CAD file is open, the e2 template will be loaded.
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
# temporary MOT file if none is open. Import ``deepcopy`` and various geometry functions to aid in
# building ellipses.

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/OvalRotorDucts.png'


from copy import deepcopy
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, Region, RegionType
from ansys.motorcad.core.geometry_ellipse import Ellipse
from ansys.motorcad.core.rpc_client_core import MotorCADError

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
    # The ducts are made slightly larger to aid in visibility
    mc.set_variable("RotorCircularDuctLayer_ChannelHeight", 6)
    mc.set_variable("RotorCircularDuctLayer_ChannelWidth", 4)

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters
# -----------------------
# Get the duct information specified
angle = float(mc.get_variable("RotorCircularDuctLayer_OffsetAngle").split(" : ")[0])
height = float(mc.get_variable("RotorCircularDuctLayer_ChannelHeight").split(" : ")[0])
width = float(mc.get_variable("RotorCircularDuctLayer_ChannelWidth").split(" : ")[0])
radius = float(mc.get_variable("RotorCircularDuctLayer_RadialDiameter").split(" : ")[0]) / 2

# %%
# Create a duct out of upper and lower halves of an ellipse
# ---------------------------------------------------------
# It might be the case that MotorCAD has split the rectangular duct into upper and lower parts
# due to it crossing a line of symmetry. This will often occur for ellipses with the same width and
# height, but not always, so splitting the ellipse in similar way is left until later,
# when calculations can be run on whether it's necessary

try:
    rotor_duct = mc.get_region("RotorDuctFluidRegion")
except MotorCADError:
    rotor_duct = mc.get_region("RotorDuctFluidRegion_1")

duplication_angle = 360 / rotor_duct.duplications

# Calculations are equivalent and made simpler for an angle restricted to the range
# [0, duplication_angle)
angle = angle % duplication_angle

# %%
# Create an initial ellipse without regard for lines of symmetry
# --------------------------------------------------------------
# Ellipses are by default drawn to the right of the line connecting their start and end points
# Therefore, the elliptic arc forming the top should go from the outer point to the inner one,
# and the bottom should reverse that order.
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
rotor_duct.entities += upper_half
rotor_duct.entities += lower_half

# %%
# Split the region if necessary and set it to MotorCAD
# ----------------------------------------------------
# In order to have valid geometry, a region must not cross the line at its duplication angle;
# in fact its geometry must remain in the angular range from 0 to its duplication angle.
# Regions placed on boundaries may still be used, but must be split into linked regions with
# defining geometry contained within the aforementioned section. This principle is applied below.
# Once any necessary splitting is performed, the new duct geometry is set to the regions
# representing ducts, and those ducts are in turn set to the MotorCAD instance created earlier

# Create a brush used to cut away the section of the duct crossing the lower duplication angle (0)
brush1 = Region(region_type=RegionType.airgap)
p1 = Coordinate(0, 0)
p2 = Coordinate(mc.get_variable("Stator_Lam_Dia"), 0)
brush1.entities.append(Line(p2, p1))
brush1.entities.append(Arc(p1, p2, centre=Coordinate(mc.get_variable("Stator_Lam_Dia") / 2, 1)))
# Upper in this case referring to the fact that this region will form the upper half of the ellipse.
# It will be below the other half in terms of relative positioning
truncated_upper = mc.subtract_region(rotor_duct, brush1)[0]

# Case if it does not cross the lower boundary
if all(isinstance(arc, Arc) for arc in truncated_upper.entities):
    # Create a brush used to cut away the section of the duct crossing the upper duplication angle
    brush2 = Region(region_type=RegionType.airgap)
    p1 = Coordinate(0, 0)
    p2 = Coordinate.from_polar_coords(mc.get_variable("Stator_Lam_Dia"), duplication_angle)
    brush2.entities.append(Line(p1, p2))
    brush2.entities.append(Arc(p2, p1, radius=mc.get_variable("Stator_Lam_Dia") / 2))
    truncated_lower = mc.subtract_region(rotor_duct, brush2)[0]

    # Case if it crosses upper boundary
    if not all(isinstance(arc, Arc) for arc in truncated_lower.entities):
        # The other section may be calculated from the one already acquired without need
        # of another brush
        truncated_upper = mc.subtract_region(rotor_duct, truncated_lower)[0]
        # Since the duct crosses the upper angle, the duplication angle must be subtracted
        # to return the section hanging out to a valid spot
        truncated_upper.rotate(Coordinate(0, 0), -duplication_angle)

        # Depending on the symmetry of the ducts, the ellipses might be split while the squares are
        # not. This may result in additional required regions that must be created in the script
        try:
            duct_lower = mc.get_region("RotorDuctFluidRegion_1")
            duct_lower.entities = truncated_lower.entities

            duct_upper = mc.get_region("RotorDuctFluidRegion_2")
            duct_upper.entities = truncated_upper.entities
        # In the aforementioned case, create new regions with appropriate names,
        # then remove the old one
        except MotorCADError:
            duct_lower = mc.get_region("RotorDuctFluidRegion")
            duct_lower.entities = truncated_lower.entities
            duct_lower.name = "RotorDuctFluidRegion_1"

            duct_upper = deepcopy(duct_lower)
            duct_upper.entities = truncated_upper.entities
            duct_upper.name = "RotorDuctFluidRegion_2"

            mc.delete_region(mc.get_region("RotorDuctFluidRegion"))

        # Region linkage is lost during the fetching process and must be reset
        duct_upper.linked_region = duct_lower
        duct_lower.linked_region = duct_upper

        mc.set_region(duct_upper)
        mc.set_region(duct_lower)

    # Case when no splitting was necessary
    else:
        # It might be the case that the rectangular duct was split while the elliptical one was not
        # In that case, the name conventions will be off and there will be an extra region:
        # that case is accounted for below by fixing the names and removing the extra region
        rotor_duct.name = "RotorDuctFluidRegion"
        try:
            old_duct1 = mc.get_region("RotorDuctFluidRegion_1")
            mc.delete_region(old_duct1)
            old_duct2 = mc.get_region("RotorDuctFluidRegion_2")
            mc.delete_region(old_duct2)
        except MotorCADError:
            pass

        mc.set_region(rotor_duct)

# Case if it crosses lower boundary
else:
    # The other section may be calculated from the one already acquired without need
    # of another brush
    truncated_lower = mc.subtract_region(rotor_duct, truncated_upper)[0]
    # Since the duct crosses the lower angle, the duplication angle must be added
    # to return the section hanging out to a valid spot
    truncated_lower.rotate(Coordinate(0, 0), duplication_angle)

    # Depending on the symmetry of the ducts, the ellipses might be split while the squares are not
    # This may result in additional required regions that must be created in the script
    try:
        duct_lower = mc.get_region("RotorDuctFluidRegion_1")
        duct_lower.entities = truncated_lower.entities

        duct_upper = mc.get_region("RotorDuctFluidRegion_2")
        duct_upper.entities = truncated_upper.entities
    # In the aforementioned case, create new regions with appropriate names, then remove the old one
    except MotorCADError:
        duct_lower = mc.get_region("RotorDuctFluidRegion")
        duct_lower.entities = truncated_lower.entities
        duct_lower.name = "RotorDuctFluidRegion_1"

        duct_upper = deepcopy(duct_lower)
        duct_upper.entities = truncated_upper.entities
        duct_upper.name = "RotorDuctFluidRegion_2"

        mc.delete_region(mc.get_region("RotorDuctFluidRegion"))

    # Region linkage is lost during the fetching process and must be reset
    duct_upper.linked_region = duct_lower
    duct_lower.linked_region = duct_upper

    mc.set_region(duct_upper)
    mc.set_region(duct_lower)


# %%
# .. image:: ../../images/adaptive_templates/OvalRotorDucts_Split.png

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
