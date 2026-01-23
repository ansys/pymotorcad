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
.. _ref_force_extraction:

Motor-CAD force extraction example script
=========================================

This sets up the operating points and threading options for a force/NVH calculation,
then displays some key force orders from a 2d FFT that may be important for NVH.

"""

# %%
# Import PyMotorCAD and launch Motor-CAD, turning off pop-up messages.
import ansys.motorcad.core as pymotorcad

mc = pymotorcad.MotorCAD()
mc.set_variable("MessageDisplayState", 2)

# %%
# Load a baseline model - in this case a template.
# For users, this would normally be a baseline model.
mc.load_template("e9")

# %%
# Set 90 torque points per cycle, which will give us information up to the 45th electrical order.
# If using an induction motor, use `IMSingleLoadPointsPerCycle_Rotating` instead.
mc.set_variable("TorquePointsPerCycle", 90)

# %%
# Enable multithreading for the force/NVH calculation
mc.set_variable("MultiForceThreading", 0)  # 0 is multithreaded, 1 is single threaded.

# %%
# Set operating points, in this case for speed and torque definition.
operating_points_speed = [250, 8000, 8000]  # RPM
operating_points_torque = [250, 250, 100]  # Nm
num_operating_points = len(operating_points_speed)

# Make sure the table is the correct length before setting value
mc.set_variable("NumLoadPoints", num_operating_points)

# Set the values:
for operating_point in range(num_operating_points):
    mc.set_array_variable(
        "LoadPoint_Speed_Array", operating_point, operating_points_speed[operating_point]
    )
    mc.set_array_variable(
        "LoadPoint_Torque_Array", operating_point, operating_points_torque[operating_point]
    )

# %%
# .. note::
#   For other motor types or options, the following may be needed:
#
#   - All motor types and options: `LoadPoint_Speed_Array`
#   - BPM or similar for torque based definition: `LoadPoint_Torque_Array`
#   - BPM or similar for current/phase advance definition: `LoadPoint_Current_Array`,
#   and `LoadPoint_PhaseAdvance_Array`
#   - SRM: `LoadPoint_Current_Array`, `LoadPoint_OnAngle_Array`, and `LoadPoint_OffAngle_Array`
#   - IM: `LoadPoint_Current_Array` and `LoadPoint_Slip_Array`

# %%
# Run the electromagnetic FEA calculation, which calculates the forces.
mc.do_multi_force_calculation()

# %%
# Define the orders that we want to extract as space and time order pairs. In this case, these
# are some of the important orders for a  48 slot, 8 pole motor.
#
# The orders are defined as pairs of
# [Space order (positive or negative), electrical time order (0 or positive)]:
required_orders = [[0, 12], [0, 24], [8, 2], [-8, 10], [8, 14]]

# %%
# Get information about the results.

# Number of cycles. If using this for an induction motor, use
# `IMSingleLoadNumberCycles_Rotating` instead
electrical_cycles = mc.get_variable("TorqueNumberCycles")

# Maximum number of space orders in results
mech_force_space_order_max = mc.get_variable("ForceMaxOrder_Space_Stator_OL")

# Number of operating points. In this example we have set this earlier in the script
num_operating_points = mc.get_variable("NumLoadPoints")

# Find how many slices (for skew) are available.
if mc.get_variable("SkewType") == 2:
    # Stepped skew
    rotor_slices = mc.get_variable("RotorSkewSlices")
else:
    rotor_slices = 1

# %%
# Find the force density for each slice, at the different operating points and slices:
for rotor_slice in range(rotor_slices):
    print("\nSlice " + str(rotor_slice + 1) + ":")
    for operating_point in range(num_operating_points):
        print("\nOperating point " + str(operating_point + 1) + ":")

        print(
            "Results as: Space order, "
            "Electrical order, "
            "Force density amplitude (N/m^2), "
            "Force density phase (deg):"
        )

        for required_order in required_orders:
            required_space_order = required_order[0]
            required_electrical_time_order = required_order[1]

            # Results stored with negative space orders at the end, so apply offset
            if required_space_order < 0:
                raw_space_order = required_space_order + 2 * mech_force_space_order_max
            else:
                raw_space_order = required_space_order

            # If more than one cycle used, scale between electrical orders and internal orders
            raw_time_order = required_electrical_time_order * electrical_cycles

            # Find the force density using GetMagnetic3DGraphPoint:
            # Note the use of _Th1 for the 1st operating point in the name.
            # Note also that rotor slice numbering starts at 1.
            _, force_density_amplitude = mc.get_magnetic_3d_graph_point(
                "Fr_Density_Stator_FFT_Amplitude_OL" + "_Th" + str(operating_point + 1),
                rotor_slice + 1,
                raw_space_order,
                raw_time_order,
            )

            _, force_density_angle = mc.get_magnetic_3d_graph_point(
                "Fr_Density_Stator_FFT_Angle_OL" + "_Th" + str(operating_point + 1),
                rotor_slice + 1,
                raw_space_order,
                raw_time_order,
            )

            # Apply 2x factor due to FFT symmetry, unless on the 0th time order (mean)
            # This is equivalent to showing results with 'Positive time only'
            if required_electrical_time_order > 0:
                force_density_amplitude = force_density_amplitude * 2

            # Print the result. In a user workflow, this would usually be stored,
            # for example for use as an optimisation metric:
            print(
                str(required_space_order)
                + ",\t"
                + str(required_electrical_time_order)
                + ",\t"
                + str(force_density_amplitude)
                + ",\t"
                + str(force_density_angle)
            )
