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
Setting material properties to close slot
=========================================

This script applies the adaptive templates functionality to change
the air region in the slot opening to steel, to model a closed slot.
"""

import sys

import ansys.motorcad.core as pymotorcad
import ansys.motorcad.core.geometry as geo

# Connect to Motor-CAD, using existing instance
# Alternatively, we could open a new instance and load a file with mc.load_from_file()
mc = pymotorcad.MotorCAD()


# Reset geometry to default
mc.reset_adaptive_geometry()

# Try to replace the StatorAir region properties, so it behaves like steel
stator_air = mc.get_region("StatorAir")
stator = mc.get_region("Stator")
stator_air.material = stator.material
stator_air.colour = stator.colour

# Set to laminated region type
# (setting as adaptive region type will not be necessary in the future)
stator_air._region_type = geo.RegionType.adaptive
stator_air.lamination_type = "Laminated"
mc.set_region(stator_air)

# If we're running this externally, load adaptive template script into Motor-CAD
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
