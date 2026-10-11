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
.. _ref_IPM_Rotor_Pocket_Fluid_Ducts:
Using IPM Rotor Pockets as Fluid Ducts
======================================

This script applies the adaptive templates functionality to modify IPM rotor pockets to be used as
ducts for cooling models.
"""
# %%
# Perform required imports
# ------------------------
import sys

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import RegionType

# %%
# Connect to Motor-CAD, using existing instance
# Alternatively, we could open a new instance and load a file with mc.load_from_file()
# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# get the geometry tree and get rotor duct, rotor pocket and rotor regions from the tree.
gt = mc.get_geometry_tree()
rotor_ducts = gt.get_regions_of_type(RegionType.rotor_duct)
rotor_pockets_orig = gt.get_regions_of_type(RegionType.rotor_pocket)
rotor = gt.get_regions_of_type(RegionType.rotor)[0]

# %%
# Loop through the ducts and rotor pockets. Find the duct that overlaps each pocket and replace the
# duct entities with the pocket entities. Remove the pocket from the geometry tree.
for duct in rotor_ducts:
    for pocket in rotor_pockets_orig:
        # to check whether the regions overlap, try a subtraction.
        temp = mc.subtract_region(pocket, duct)
        # tolerance 0.0001 mm
        if temp[0].area < pocket.area - 0.0001:  # If the area is smaller, the regions overlap
            # print(f"{duct.name} and {pocket.name} match")
            duct.replace(pocket)
            gt.remove_region(pocket)

# %%
# Set the geometry tree to make the changes
mc.set_geometry_tree(gt)

# If we're running this externally, load adaptive template script into Motor-CAD
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
