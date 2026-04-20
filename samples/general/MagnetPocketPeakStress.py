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
Find peak stress on boundary of region(s)
=========================================
This example shows how to sample the stresses around a magnet pocket

It finds the overall region that makes up the magnet pocket (the pocket region
itself and the magnet), and then samples the stresses along the perimeter of
this region.

This script should be run from the scripting tab after the stress calculation
has been run in Motor-CAD.
"""

import math
import os

# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD()

# Users should run this script from the scripting tab after the stress calculation
# Trigger this automatically for the automated documentation build
if "PYMOTORCAD_DOCS_BUILD" in os.environ:
    mc.set_variable("MessageDisplayState", 2)
    mc.load_template("e10")
    mc.do_mechanical_calculation()

############
# Settings #
############

# Define the region name or names that make up the region of interest (e.g. magnet and pocket)
# Peak stress will be found on the boundary of this region
region_names = ["L1_1Magnet1", "Rotor Pocket_1"]
sample_distance = (
    0.1  # Sampling distance in mm along lines/arcs (end points will always be included)
)

###############
# Main script #
###############

# Get the region(s) we are interested in, combined into a single region object
regions = []
for region_name in region_names:
    regions.append(mc.get_region(region_name))

if len(regions) > 1:
    region = mc.unite_regions(regions[0], regions[1:])
else:
    region = regions[0]

# Get the points that make up the region
points = []
for entity in region.entities:
    length = entity.length
    samples = math.ceil(length / sample_distance)
    for sample in range(samples):
        # Sample points along line. Don't get end point, as this will be start of the next entity
        points.append(entity.get_coordinate_from_distance(entity.start, fraction=sample / samples))

# Get stress result at these points
stresses = []
stress_unit = None
for point in points:
    stress, stress_unit = mc.get_point_value("SVM", point.x, point.y)
    stresses.append(stress)

# Find the max stress, and print the output
max_stress = max(stresses)
print(f"Max von Mises stress: {max_stress} {stress_unit}")
