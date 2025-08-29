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
Stress sampling example
=======================
This example shows how to sample the stresses in the rotor bridges.

This script should be run from the scripting tab after the stress calculation
has been run in Motor-CAD.
"""

from math import asin, cos, radians, sin
import os
import sys

# Standard imports
import ansys.motorcad.core as pymotorcad

# Connect to Motor-CAD
mcApp = pymotorcad.MotorCAD()

# Users should run this script from the scripting tab after the stress calculation
# Trigger this automatically for the automated documentation build
if "PYMOTORCAD_DOCS_BUILD" in os.environ:
    mcApp.load_template("e10")
    mcApp.do_mechanical_calculation()

# Sample points is hardcoded to 15 in Motor-CAD for stress averaging
sample_points = 15

# Check the rotor type
rotor_type = mcApp.get_variable("BPMRotor")
# U shape is 13, V web is 11
if rotor_type == 11:
    layers = mcApp.get_variable("VMagnet_Layers")
elif rotor_type == 13:
    layers = mcApp.get_variable("Magnet_Layers")
else:
    sys.exit("Stress sampling only available for V web and U templates")

# Get variables independent of the rotor type
average_stress_location_bridge = mcApp.get_variable("AvStressRadialLocation_Bridge")
rotor_diameter = mcApp.get_variable("RotorDiameter")
poles = mcApp.get_variable("Pole_Number")
pole_pairs = poles / 2

for layer in range(layers):
    if rotor_type == 11:
        # V Web template
        bridge_thickness = mcApp.get_array_variable("BridgeThickness_Array", layer)
        web_thickness = mcApp.get_array_variable("WebThickness_Array", layer)
        pole_arc = radians(mcApp.get_array_variable("PoleArc_Array", layer) / pole_pairs)
        theta_4 = asin(web_thickness / (2 * (rotor_diameter / 2 - bridge_thickness)))
        theta_0 = radians(180 / poles) + pole_arc / 2
        theta_1 = radians(360 / poles) - theta_4
        theta_bridge_span = theta_1 - theta_0
        # Arc covers half the bridge
        delta_theta = theta_bridge_span / 2 / sample_points
        theta = theta_0 + theta_bridge_span / 2
    elif rotor_type == 13:
        # U template
        bridge_thickness = mcApp.get_array_variable("UShape_BridgeThickness_Array", layer)
        web_thickness = mcApp.get_array_variable("UShape_WebThickness_Array", layer)
        outer_thickness = mcApp.get_array_variable("UShape_Thickness_Outer_Array", layer)
        theta_offset = radians(mcApp.get_array_variable("UShape_OuterAngleOffset_Array", layer))
        inner_rad = rotor_diameter / 2 - bridge_thickness

        # The start angle of the FEA model
        theta_0 = radians(360 / poles)

        # The angle to the end of the web
        theta_1 = asin(web_thickness / (2 * inner_rad))

        # We now need to solve for phi (the arc angle from the centre) with
        # cos(theta_offset - theta_1 - phi/2) * sin(phi/2) = outer_thickness / (2 * inner_rad)
        # This is non-trivial, so do this numerically
        test_phi = 0
        found_phi = False
        phi_step = radians(0.01)
        iteration = 0
        last_err = cos(theta_offset - theta_1 - test_phi / 2) * sin(
            test_phi / 2
        ) - outer_thickness / (2 * inner_rad)
        while found_phi == False and iteration < 36000:
            test_phi = test_phi + phi_step
            iteration = iteration + 1
            err = cos(theta_offset - theta_1 - test_phi / 2) * sin(
                test_phi / 2
            ) - outer_thickness / (2 * inner_rad)
            # Check if error has changed sign, if so we are close to the correct solution
            if err * last_err < 0:
                found_phi = True
            else:
                last_err = err
        theta_bridge_span = test_phi

        # Arc covers half the bridge
        delta_theta = theta_bridge_span / 2 / sample_points
        theta = theta_0 - (theta_1 + theta_bridge_span / 2)

    # Common logic for both rotor types
    r0 = rotor_diameter / 2 - bridge_thickness * (1 - average_stress_location_bridge)
    stresses = []
    points = []
    for point in range(sample_points):
        this_theta = theta + point * delta_theta
        x = r0 * cos(this_theta)
        y = r0 * sin(this_theta)
        points.append([x, y])
        stresses.append(mcApp.get_point_value("SVM", x, y)[0])

    # Display results for this layer
    print("Point positions: " + str(points))
    print("Stress at points: " + str(stresses))
    print("Mean stress: " + str(sum(stresses) / len(stresses)))
