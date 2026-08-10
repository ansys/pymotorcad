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
Thermal FEA with slot base insulation (parallel slot)
=====================================================

This script modifies the standard geometry for a parallel slot for
thermal FEA, to include the Slot Base Insulation in FEA.
"""

import math

# Standard imports
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Line, Region, RegionType

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD()

# Reset geometry to default
mc.reset_adaptive_geometry()

# Use the standard parameter (Ins_Slot_Base_Thickness and Material_Ins_Slot_Base)
depth = mc.get_variable("Ins_Slot_Base_Thickness")
material = mc.get_variable("Material_Ins_Slot_Base")

# Only change the geometry if needed
if depth > 0:
    liner = mc.get_region("Liner")
    stator = mc.get_region("Stator")

    # Find the unit vector we want to project along
    vector = liner.entities[0].end - liner.entities[0].start
    unit_vector = vector / math.sqrt(vector.x**2 + vector.y**2)

    # Points where we will be adding the insulation region
    point_1 = liner.entities[1].start
    point_2 = liner.entities[2].end
    point_3 = point_2 + unit_vector * depth
    point_4 = point_1 + unit_vector * depth

    # Make the new region (PyMotorCAD 0.8/Motor-CAD 2026 R1 should have region type defined)
    if mc.connection.check_version_at_least("2026"):
        insulation = Region(region_type=RegionType.stator_liner)
    else:
        insulation = Region()

    line_1 = Line(point_1, point_2)
    line_2 = Line(point_2, point_3)
    line_3 = Line(point_3, point_4)
    line_4 = Line(point_4, point_1)
    insulation.add_entity(line_1)
    insulation.add_entity(line_2)
    insulation.add_entity(line_3)
    insulation.add_entity(line_4)

    insulation.name = "Insulation slot base"
    insulation.duplications = liner.duplications
    insulation.material = material

    # By setting the parent, we do not need to modify the stator geometry.
    insulation.parent = stator

    # Send region back to Motor-CAD
    mc.set_region(insulation)
