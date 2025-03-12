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
.. _ref_thermal_duty_cycle_custom_variables:

Thermal Duty Cycle with Custom Variables
========================================

"""

import inspect
import json
import os
import shutil
import tempfile

# %%
# Perform Required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD. Import JSON for writing and reading the
# configuration file.
import ansys.motorcad.core as pymotorcad

# %%
# Connect to Motor-CAD
# --------------------
mc = pymotorcad.MotorCAD(keep_instance_open=True)

# %%
# Disable pop-up messages
mc.set_variable("MessageDisplayState", 2)

# %%
# Load a Motor-CAD file
mc.load_template("e10")

# Open relevant file
working_folder = os.path.join(tempfile.gettempdir(), "thermal_examples")
try:
    shutil.rmtree(working_folder)
except:
    pass
os.mkdir(working_folder)
mot_name = "e10_duty_cycle_custom_variable_example"
mc.save_to_file(working_folder + "\\" + mot_name + ".mot")


# %%
# Define Duty Cycle
# -----------------
# This function defines the duty cycle. It is not necessary if the Motor-CAD file already has a
# Duty Cycle defined.
def define_duty_cycle():
    number_of_duty_cycle_periods = 5
    duty_cycle_points = [4, 4, 4, 5, 3]
    duty_cycle_time = [20, 40, 30, 40, 10]
    duty_cycle_torque_pu = [1, 2.5, 0.1, 3, 0.3]
    duty_cycle_speed_start = [3000, 3000, 6000, 0, 4000]  # rpm
    duty_cycle_speed_end = [3000, 6000, 0, 4000, 3000]  # rpm

    mc.set_variable("Duty_Cycle_Definition", 0)  # Set Torque - Speed definition
    mc.set_variable("Duty_Cycle_Input_Type", 0)  # Set per unit Torque input type
    mc.set_variable("Reference_Shaft_Torque", 225)  # Set reference Shaft Torque in Nm
    mc.set_variable("Duty_Cycle_Num_Periods", number_of_duty_cycle_periods)
    for i in range(number_of_duty_cycle_periods):
        mc.set_array_variable("Duty_Cycle_Points", i, duty_cycle_points[i])
        mc.set_array_variable("Duty_Cycle_Time", i, duty_cycle_time[i])
        mc.set_array_variable("Duty_Cycle_Torque_Start", i, duty_cycle_torque_pu[i])
        mc.set_array_variable("Duty_Cycle_Speed_Start", i, duty_cycle_speed_start[i])
        mc.set_array_variable("Duty_Cycle_Speed_End", i, duty_cycle_speed_end[i])


mc.show_thermal_context()
mc.set_variable("ThermalCalcType", 1)
mc.set_variable("TransientCalculationType", 1)
mc.set_variable("TransientPointsToPlot", 1)
mc.clear_duty_cycle()
define_duty_cycle()
mc.save_to_file(working_folder + "\\" + mot_name + ".mot")
# %%
# Define Custom Variables
# -----------------------

parameter_names = ["HousingWJ_Inlet_Temperature", "WJ_Fluid_Volume_Flow_Rate"]

# get required inputs
if type(parameter_names) != list:
    parameter_names = [parameter_names]
duty_cycle_time = mc.get_variable("Duty_Cycle_Time")
duty_cycle_time = duty_cycle_time.split(" : ")
duty_cycle_periods = len(duty_cycle_time)

# Data to be written
mot_file = mc.get_variable("CurrentMotFilePath_MotorLAB")
json_out = {
    "_comment": "Configuration file for custom Drive Cycle Variables in Motor-CAD Thermal",
    "mot_file": mot_file,
    "duty_cycle_periods": duty_cycle_periods,
    "duty_cycle_time": duty_cycle_time,
    "parameter_names": [],
}

custom_variables_var = []
housing_water_jacket_inlet_temperature = [65.0, 67.5, 70.0, 68.0, 66.0]
housing_water_jacket_flow_rate = [8.0, 7.5, 7.0, 6.8, 6.6]  # l/min
housing_water_jacket_flow_rate = [i * 1.667e-5 for i in housing_water_jacket_flow_rate]  # m^3/s
custom_variables_var.append(housing_water_jacket_inlet_temperature)
custom_variables_var.append(housing_water_jacket_flow_rate)

# Get the custom input variables that were entered and store in an array
for i in range(len(parameter_names)):
    custom_variable_inputs = []
    for period in range(duty_cycle_periods):
        custom_variable_input = float(custom_variables_var[i][period])
        custom_variable_inputs.append(custom_variable_input)
    json_out["parameter_names"].append(parameter_names[i])
    json_out[parameter_names[i]] = custom_variable_inputs

# serialising JSON
json_object = json.dumps(json_out, indent=2)
json_path = mot_file.replace(".mot", r"\drive_cycle_custom_variables.json")
with open(json_path, "w") as outfile:
    outfile.write(json_object)
mc.show_message("Custom Duty Cycle variables exported to JSON file " + json_path)

# %%
# This example outputs the following to the JSON file.

# %%
# .. code-block:: json
#
#     {
#       "_comment": "Configuration file for custom Drive Cycle Variables in Motor-CAD Thermal",
#       "mot_file": "[working_folder]\\e10_duty_cycle_custom_variable_example.mot",
#       "duty_cycle_periods": 5,
#       "duty_cycle_time": [
#         "20",
#         "40",
#         "30",
#         "40",
#         "10"
#       ],
#       "parameter_names": [
#         "HousingWJ_Inlet_Temperature",
#         "WJ_Fluid_Volume_Flow_Rate"
#       ],
#       "HousingWJ_Inlet_Temperature": [
#         65.0,
#         67.5,
#         70.0,
#         68.0,
#         66.0
#       ],
#       "WJ_Fluid_Volume_Flow_Rate": [
#         8.0,
#         7.5,
#         7.0,
#         6.8,
#         6.6
#       ]
#     }


# %%
# Set custom variables
# --------------------
# This function is designed to be run from the "main" function of the "thermal_transient" class
# in the "FUNCTIONS RUN DURING CALCULATIONS" section below
#
# Get the custom variable parameter names and input values for each duty cycle period from
# the JSON configuration file.
# Check the current time in the transient calculation and get the corresponding custom variable
# input values. Set the variables.
def set_custom_variables():
    # set messages to display in linked window
    original_display_state = mc.get_variable("MessageDisplayState")
    mc.set_variable("MessageDisplayState", 2)

    time = mc.get_variable("CurrentTime")
    duty_cycle_time = mc.get_variable("Duty_Cycle_Time")
    duty_cycle_time = duty_cycle_time.split(" : ")
    duty_cycle_time = list(map(float, duty_cycle_time))
    duty_cycle_periods = len(duty_cycle_time)

    duty_cycle_end_time = []
    end_time = 0
    for period in range(duty_cycle_periods):
        end_time += duty_cycle_time[period]
        duty_cycle_end_time.append(end_time)
    cycle_time = duty_cycle_end_time[duty_cycle_periods - 1]

    # need to account for multiple duty cycles
    mult = 0
    if time >= cycle_time:
        mult = time // cycle_time
    time = time - cycle_time * mult

    mc.show_message("time = " + str(time + cycle_time * mult) + " s")

    # find JSON file "drive_cycle_custom_variables.json" located in MOT file folder
    mot_file = mc.get_variable("CurrentMotFilePath_MotorLAB")
    json_path = mot_file.replace(".mot", r"\drive_cycle_custom_variables.json")

    # open JSON file
    with open(json_path, "r") as file:
        data = json.load(file)

    # Get the parameter names from the JSON data
    parameter_names = data["parameter_names"]
    for variable in parameter_names:
        # get the input values from the JSON data
        inputs = data[variable]
        for period in range(duty_cycle_periods):
            if time < duty_cycle_end_time[period]:
                # set the custom variables
                mc.show_message("Set " + variable + " to: " + str(inputs[period]))
                mc.set_variable(variable, inputs[period])
                break
    # return to original message display setting
    mc.set_variable("MessageDisplayState", original_display_state)


# %%
# Define class containing functions for transient thermal calculations
# -----------------------------------------------------------------------
class thermal_transient:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Transient - Initial")
        # Determine whether the transient calculation is Duty Cycle
        self.calc_type = mc.get_variable("ThermalCalcType")
        if self.calc_type == 1:
            print("Duty Cycle calculation")

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Transient State - Main")
        # If the Duty Cycle is being run, set the custom variables
        if self.calc_type == 1:
            set_custom_variables()


# %%
# write to .py file
py_file_path = mot_file.replace(".mot", r"\internal_script.py")
python_output = []
python_output.append(
    """\
# ---------- INTERNAL SCRIPT - THERMAL DUTY CYCLE CUSTOM VARIABLES ----------

# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad
import json

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD()


"""
)

python_output.append(inspect.getsource(set_custom_variables))

python_output.append(
    """\


# ---------- FUNCTIONS RUN DURING CALCULATIONS ----------
# These will only run if using "Run During Analysis" selected
# (Scripting -> Settings -> Run During Analysis)

# If "Run During Analysis" is selected then this script will be imported.
# This means that anything other than setting up the MotorCAD object should
# be moved to a function/class to avoid unexpected behaviour

# This class contains functions for thermal transient calculations
class thermal_transient:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Transient - Initial")
        # Determine whether the transient calculation is Duty Cycle
        self.calc_type = mc.get_variable("ThermalCalcType")
        if self.calc_type == 1:
            print("Duty Cycle calculation")

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Transient State - Main")
        # If the Duty Cycle is being run, set the custom variables
        if self.calc_type == 1:
            set_custom_variables()
"""
)

# python_output.append(inspect.getsource(thermal_transient))

with open(py_file_path, "w") as outfile:
    for i in python_output:
        outfile.write(i)

# %%
# Setup internal scripting
# ------------------------
# Set to **Run During Analysis**
mc.set_variable("ScriptAutoRun_PythonClasses", 1)

# %%
# Load this script into Internal **Scripting** tab
mc.load_script(py_file_path)

# %%
# Run Steady State Analysis
# -------------------------
mc.save_to_file(working_folder + "\\" + mot_name + ".mot")

mc.do_transient_analysis()
