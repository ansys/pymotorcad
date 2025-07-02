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
Simple parametric sweep for SYNC machine
========================================
This is a simple example showing a two-dimensional parametric sweep for a wound field synchronous
motor varying continuous stator skew and field current.
"""

import math

import ansys.motorcad.core as pymotorcad

# Open connection to Motor-CAD, and open e3 template (Sync machine)
mc = pymotorcad.MotorCAD()
mc.load_template("e3")
# Alternatively, use the following
# mc = pymotorcad.MotorCAD()
# mc.load_from_file('filename.mot')

# Ensure the transient calculation and force calculation are enabled
mc.set_variable("TorqueCalculation", True)
mc.set_variable("ElectromagneticForcesCalc_Load", True)

# Make sure continuous stator skew is enabled
mc.set_variable("SkewType", 1)

# Set up the sweep parameters, in this case for sync machine field current and skew angle
skew_angles = [0, 7.5]
field_currents = [5, 10]

# Run the sweep
for skew_angle in skew_angles:
    for field_current in field_currents:
        # Set the parameter(s) to sweep
        mc.set_variable("StatorSkew", skew_angle)
        mc.set_variable("DCFieldCurrent", field_current)

        # Tell the user what step we are on:
        print("Running skew: " + str(skew_angle) + " Field current: " + str(field_current))

        # Run the calculation
        mc.do_magnetic_calculation()

        # Find many steps have been run
        if mc.get_variable("MotorType_MotorLAB") == "IM":
            try:
                # Variable was renamed in 2024R1, try newer naming first
                numberOfCycles = mc.get_variable("IMSingleLoadNumberCycles_Rotating")
            except pymotorcad.MotorCADError:
                numberOfCycles = mc.get_variable("IMSingleLoadNumberCycles")
        else:
            numberOfCycles = mc.get_variable("TorqueNumberCycles")

        # Get the NVH data matrix
        nvh_data_raw = mc.get_magnetic_3d_graph("NVH_RadiatedPower_Level_OL", 1)

        # Find length of data available
        time_order_items = len(nvh_data_raw.y)
        space_order_items = len(nvh_data_raw.x)
        index_offset_space = math.floor(space_order_items / 2)

        # Iterate over data, storing as a list of tuples, so we can sort to find the biggest
        nvh_list = []
        for raw_time_order in range(time_order_items):
            electrical_order = raw_time_order / numberOfCycles
            for raw_space_order in range(space_order_items):
                space_order = raw_space_order - index_offset_space
                # Store a tuple of sound power level, electrical time order, space order
                nvh_list.append(
                    (
                        nvh_data_raw.data[raw_space_order][raw_time_order],
                        electrical_order,
                        space_order,
                    )
                )

        # Sort the list on NVH, from highest to lowest, and show top 5 orders
        nvh_list.sort(reverse=True)
        print("Sound power level [dB], electrical time order, space order:")
        for i in range(min(5, len(nvh_list))):
            print(nvh_list[i])
        print("")
