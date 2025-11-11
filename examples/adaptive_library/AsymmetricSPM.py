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
Asymmetric Surface Permanent Magnet Rotor
=========================================
This script applies the adaptive templates functionality to modify a 28 pole surface permanent
magnet rotor to have an asymmetric arrangement of magnets.
"""
# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Region``, ``RegionType``, ``Line``, ``Arc``, ``Coordinate`` and ``rt_to_xy`` for creating
# the adaptive templates geometry.
# Import ``draw_objects`` to plot figures of geometry objects.
# Import ``deepcopy`` to copy geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# from copy import deepcopy

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, RegionType, rt_to_xy  # , Region

# from ansys.motorcad.core.geometry_drawing import draw_objects
# import ansys.motorcad.core.geometry_tree as geo_tree

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened, the a2
# SPM motor template is loaded, the **Magnet Arc [ED]** is set to **100** and the file is saved
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
    mc.load_template("a2")
    mc.set_variable("Magnet_Arc_[ED]", 100)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "a2_Asymmetric_SPM"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required symmetry factor
# (``Symmetry Factor``) and asymmetric magnet offset angle (``Magnet Offset Angle x``, where x is
# the magnet number) parameters if undefined.
mc.set_adaptive_parameter_default("Symmetry factor", 4)
symmetry_factor = mc.get_adaptive_parameter_value("Symmetry factor")

offset_angle_default_values = [1, 2, 3]
offset_angles = []
for i in range(symmetry_factor - 1):
    mc.set_adaptive_parameter_default(f"Magnet Offset Angle {i+1}", offset_angle_default_values[i])
    offset_angles.append(mc.get_adaptive_parameter_value(f"Magnet Offset Angle {i+1}"))

# %%
# Get the standard template regions to be modified. This example works using the geometry tree
# functionality. Get the geometry tree, then get the standard template regions based on the region
# type.
gt = mc.get_geometry_tree()
magnets = gt.get_regions_of_type(RegionType.magnet)
rotor_air = gt.get_regions_of_type(RegionType.rotor_air)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# This example works by changing the number of times that geometry regions are duplicated.
#
# By default, a 28 pole rotor geometry is set up by defining the geometry for one rotor pole, and
# then duplicating this 28 times to form the full motor.
#
# In this example, we will define a new magnet geometry for 4 consecutive rotor poles, and this
# 4-pole magnet geometry will be duplicated 7 times to form the full motor. Instead of the original
# 1 magnet per pole that is defined for the standard template geometry, 4 magnets will be defined.
#
# Modify the duplication angles of the original magnet and rotor air regions.
for magnet in magnets:
    magnet.duplications = magnet.duplications / symmetry_factor
for air_region in rotor_air:
    air_region.duplications = air_region.duplications / symmetry_factor

# %%
# The rotor air regions will be redrawn based on the new magnet positions. To do so, define the full
# rotor air region. Magnet regions will be subtracted from this to form the multiple new rotor air
# regions.
#
# Find the rotor air outer and inner radii (``rad_max`` and ``rad_min``). Use the
# ``Coordinate.get_polar_coords_deg()`` method to return the polar coordinates of point coordinates.
rad_max = 0
rad_min = 10000
for entity in rotor_air[0].entities:
    rad, __ = entity.end.get_polar_coords_deg()
    if rad > rad_max:
        rad_max = rad
    elif rad < rad_min:
        rad_min = rad

# Create the entities for drawing the full rotor air band before it is split into individual
# regions. Use the ``rt_to_xy`` from ``ansys.motorcad.core.geometry`` to convert from polar
# to cartesian coordinates.
p1 = Coordinate(*rt_to_xy(rad_min, 0))
p2 = Coordinate(*rt_to_xy(rad_max, 0))
p3 = Coordinate(*rt_to_xy(rad_max, 360 / rotor_air[0].duplications))
p4 = Coordinate(*rt_to_xy(rad_min, 360 / rotor_air[0].duplications))
full_rotor_air_entities = [
    Line(p1, p2),
    Arc(p2, p3, centre=Coordinate(0, 0)),
    Line(p3, p4),
    Arc(p4, p1, centre=Coordinate(0, 0)),
]
# full_rotor_air_boundary_lower = Line(p1, p2)
# full_rotor_air_arc_outer = Arc(p2, p3, centre=Coordinate(0, 0))
# full_rotor_air_boundary_upper = Line(p3, p4)
# full_rotor_air_arc_inner = Arc(p4, p1, centre=Coordinate(0, 0))

# %%
# Create copies of the original magnet region and rotate the magnets based on the 'offset_angles'.
new_magnets = []
for magnet in magnets:
    new_magnets.append(magnet)
    for i in range(symmetry_factor - 1):
        new_magnet = gt.create_region(region_type=RegionType.magnet, parent=magnet.parent)
        new_magnet.update(magnet)
        new_magnet.name = f"{new_magnet.name}_{i + 1}Offset"
        rot_angle = ((i + 1) * 360 / (magnet.duplications * symmetry_factor)) + offset_angles[i + 1]
        new_magnet.rotate(Coordinate(0, 0), rot_angle)
        new_magnet.magnet_angle = new_magnet.magnet_angle + rot_angle
        if i % 2 == 0:
            new_magnet.magnet_polarity = "S"
            new_magnet.magnet_angle += 180
        # gt._add_region(new_magnet, magnet.parent)
        new_magnets.append(new_magnet)
        # to_draw.append(new_magnet)

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
