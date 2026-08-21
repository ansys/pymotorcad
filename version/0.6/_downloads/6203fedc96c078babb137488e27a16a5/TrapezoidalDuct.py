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
Trapezoidal ducts
=================
This script applies the adaptive templates functionality to modify rectangular ducts
into trapezoidal ducts.
"""
# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Coordinate``, ``rt_to_xy``, ``xy_to_rt``
# to define the adaptive template geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/TrapezoidalDuct1.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, rt_to_xy, xy_to_rt

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e10 IPM motor template is loaded and set up with four rectangular rotor ducts, and the file is
# saved to a temporary folder. To keep a new Motor-CAD instance open after executing the script, use
# the``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e10")
    mc.set_variable("RotorDuctType", 4)  # selected rectangular ducts
    mc.set_array_variable("RotorCircularDuctLayer_ChannelWidth", 0, 4)  # set duct width

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "Trapezoidal_duct"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

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
# Check line distance from origin
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The rectangle consists of two lines of length equal to the rectangle width.
# Only the top line requires modification.
# It is necessary to check whether the line is closest to the origin. Index ``i`` is
# the line under investigation. Index ``j`` is the adjacent line. If the radius of midpoint of line
# ``i`` is less than that of line ``j`` , line ``i`` is closer to the origin.


def check_line_origin_distance(i, duct_region):
    if i == 0:  # first index of rectangle duct
        j = 1
    else:
        j = i - 1
    rad_start_i, _ = xy_to_rt(duct_region.entities[i].start.x, duct_region.entities[i].start.y)
    rad_end_i, _ = xy_to_rt(duct_region.entities[i].end.x, duct_region.entities[i].end.y)
    rad_mid_i = (rad_start_i + rad_end_i) / 2
    rad_start_j, _ = xy_to_rt(duct_region.entities[j].start.x, duct_region.entities[j].start.y)
    rad_end_j, _ = xy_to_rt(duct_region.entities[j].end.x, duct_region.entities[j].end.y)
    rad_mid_j = (rad_start_j + rad_end_j) / 2
    if rad_mid_i < rad_mid_j:
        return True
    else:
        return False


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Use the ``set_default_parameter()`` method to set the required ``Trapezoid_base_ratio`` parameter
# if undefined.
set_default_parameter("Trapezoid_base_ratio", 0.7)

# %%
# Set required parameters for the trapezoid: ratio of top width / base width
# (``Trapezoid_base_ratio``), trapezoid width and trapezoid height.
Trap_ratio = mc.get_adaptive_parameter_value("Trapezoid_base_ratio")
Trap_W = mc.get_array_variable(
    "RotorCircularDuctLayer_ChannelWidth",
    0,
)
Trap_H = mc.get_array_variable(
    "RotorCircularDuctLayer_ChannelHeight",
    0,
)

# %%
# Get the standard template rotor region. This can be drawn for debugging if required.
rt_region = mc.get_region("Rotor")  # get the rotor region

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# For each child region of the rotor region:
#
# * Check whether the region is a rotor duct.
#
# * Find the top line that makes up the duct.
#
# * Modify the start and end points of the line.
#
# * Set the region in Motor-CAD.
#
# The script accounts for whether ducts are full ducts or half ducts (the case when a duct spans the
# rotor pole boundary)
duct_area = Trap_H * Trap_W
for child_name in rt_region.child_names:
    if "RotorDuctFluidRegion" in child_name:
        duct_region = mc.get_region(child_name)
        if round(duct_region.area / duct_area, 2) == 1:  # check if  full duct is drawn
            for i, entity in enumerate(duct_region.entities):
                if round(entity.length / Trap_W, 2) == 1:  # check if  the line is width
                    # additional check in case width = height
                    r_start_point, angle_start_point = xy_to_rt(entity.start.x, entity.start.y)
                    r_end_point, angle_end_point = xy_to_rt(entity.end.x, entity.end.y)
                    if abs(angle_end_point - angle_start_point) > 0.05:  # 0.05 degree is tolerance
                        # check if the line located at top or bottom
                        Line_origin = check_line_origin_distance(i, duct_region)
                        if not Line_origin:
                            del_trap_angle = (
                                (angle_end_point - angle_start_point) * (1 - Trap_ratio) / 2
                            )
                            new_angle_start_point = angle_start_point + del_trap_angle
                            new_angle_end_point = angle_end_point - del_trap_angle
                            new_start_x, new_start_y = rt_to_xy(
                                r_start_point, new_angle_start_point
                            )
                            new_end_x, new_end_y = rt_to_xy(r_end_point, new_angle_end_point)
                            new_start_point = Coordinate(new_start_x, new_start_y)
                            new_end_point = Coordinate(new_end_x, new_end_y)
                            duct_region.edit_point(entity.start, new_start_point)
                            duct_region.edit_point(entity.end, new_end_point)
                            mc.set_region(duct_region)

        elif round(duct_region.area / duct_area, 2) == 0.5:  # half duct
            Symm_angle = 360 / duct_region.duplications  # angle of symmetry

            for i, entity in enumerate(duct_region.entities):
                if round(entity.length / Trap_W, 2) == 0.5:  # check if  the line is width
                    # additional check in case width = height
                    r_start_point, angle_start_point = xy_to_rt(entity.start.x, entity.start.y)
                    r_end_point, angle_end_point = xy_to_rt(entity.end.x, entity.end.y)
                    if abs(angle_end_point - angle_start_point) > 0.05:  # 0.05 degree is tolerance
                        Line_origin = check_line_origin_distance(i, duct_region)
                        if not Line_origin:
                            del_trap_angle = (angle_end_point - angle_start_point) * (
                                1 - Trap_ratio
                            )
                            if (
                                angle_start_point - 0 < 1e-10
                                or angle_start_point == 0
                                or round(angle_start_point / Symm_angle, 2) == 1
                            ):  # on symmetry plane
                                new_angle_end_point = angle_end_point - del_trap_angle
                                new_end_x, new_end_y = rt_to_xy(r_end_point, new_angle_end_point)
                                new_end_point = Coordinate(new_end_x, new_end_y)
                                duct_region.edit_point(entity.end, new_end_point)
                            elif (
                                angle_end_point - 0 < 1e-10
                                or round(angle_end_point / Symm_angle, 2) == 1
                            ):  # symmetry plan
                                new_angle_start_point = angle_start_point + del_trap_angle
                                new_start_x, new_start_y = rt_to_xy(
                                    r_start_point, new_angle_start_point
                                )
                                new_start_point = Coordinate(new_start_x, new_start_y)
                                duct_region.edit_point(entity.start, new_start_point)

                            mc.set_region(duct_region)

# %%
# .. image:: ../../images/TrapezoidalDuct1.png
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
