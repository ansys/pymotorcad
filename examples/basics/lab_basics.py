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
.. _ref_lab_basics:

Motor-CAD Lab model example script
==================================
This example provides a Motor-CAD Lab model script.
"""

# %%
# Set up example
# --------------
# Setting up this example consists of performing imports, launching
# Motor-CAD, disabling all popup messages from Motor-CAD, and opening
# the file for the lab model.
#
# Perform required imports

import os

import matplotlib.pyplot as plt
from scipy import io

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~

print("Starting initialization.")
mcad = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mcad.set_variable("MessageDisplayState", 2)

# %%
# Open relevant file
# ~~~~~~~~~~~~~~~~~~
# Specify the working directory and open the relevant file for
# the lab model.

working_folder = os.getcwd()
mcad.load_template("e8")
mcad_name = "e8_mobility"
mcad.save_to_file(os.path.join(working_folder, mcad_name + ".mot"))

print("Initialization completed.")

# %%
# Build model
# -----------
# Set build options for the lab model.
mcad.set_variable("ModelType_MotorLAB", 1)
mcad.set_variable("SatModelPoints_MotorLAB", 0)
mcad.set_variable("LossModel_Lab", 0)
mcad.set_variable("ModelBuildSpeed_MotorLAB", 10000)
mcad.set_variable("MaxModelCurrent_MotorLAB", 480)
mcad.set_variable("BuildSatModel_MotorLAB", True)

# %%
# Show the lab context.
mcad.set_motorlab_context()

# %%
# Build the model.
mcad.clear_model_build_lab()
mcad.build_model_lab()

# %%
# Change operating modes.
mcad.set_variable("OperatingMode_Lab", 0)

# %%
# Calculate e-magnetic performance
# --------------------------------
# Set e-magnetic calculation options.
mcad.set_variable("EmagneticCalcType_Lab", 0)
mcad.set_variable("SpeedMax_MotorLAB", 10000)
mcad.set_variable("Speedinc_MotorLAB", 250)
mcad.set_variable("SpeedMin_MotorLAB", 500)
mcad.set_variable("Imax_MotorLAB", 480)

# %%
# Calculate e-magnetic performance.
try:
    mcad.calculate_magnetic_lab()
    print("Magnetic calculation successfully completed.")
except pymotorcad.MotorCADError:
    print("Magnetic calculation failed.")

# %%
# Retrieve results.
data = io.loadmat(os.path.join(working_folder, mcad_name, "Lab", "MotorLAB_elecdata.mat"))
speed = data["Speed"]
shaft_torque = data["Shaft_Torque"]
shaft_power = data["Shaft_Power"]

# %%
# Plot results
# ------------
# Plot torque/speed curve results.
plt.figure(1)
plt.subplot(211)
plt.plot(speed, shaft_torque)
plt.xlabel("Speed")
plt.ylabel("Shaft Torque")
plt.subplot(212)
plt.plot(speed, shaft_power)
plt.xlabel("Speed")
plt.ylabel("Shaft Power")
plt.show(block=False)
plt.savefig(os.path.join(working_folder, "../Maximum Torque VS Speed Curve.png"))

# %%
# Calculate operating point
# -------------------------
# Set operating point calculation options.
mcad.set_variable("OpPointSpec_MotorLAB", 1)
mcad.set_variable("StatorCurrentDemand_Lab", 480)
mcad.set_variable("SpeedDemand_MotorLAB", 4000)
mcad.set_variable("LabThermalCoupling", 0)
mcad.set_variable("LabMagneticCoupling", 0)

# %%
# # Calculate operating point.
mcad.calculate_operating_point_lab()

# %%
# Retrieve results.
op_point_shaft_torque = mcad.get_variable("LabOpPoint_ShaftTorque")
op_point_efficiency = mcad.get_variable("LabOpPoint_Efficiency")
print("Operating Point Shaft Torque = ", op_point_shaft_torque)
print("Operating Point Efficiency = ", op_point_efficiency)


# %%
# Exit Motor-CAD
# --------------
# Exit Motor-CAD.
mcad.quit()
print("Simulation completed.")
