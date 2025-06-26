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
.. _ref_thermal_duty_cycle_inputs:

Variable inputs for Thermal duty cycle
======================================
This example demonstrates internal scripting thermal transient functionality.
"""

import json

# %%
# Perform required imports
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()


# This function is called when "Run" is pressed
def main():
    pass


# %%
# Define a ``read_parameters`` function to open the ``duty_cycle_custom_variables.json``
# configuration file and import the data as the ``duty_cycle_custom_variables`` dictionary.
#
# The JSON file must be saved to the same directory as the Motor-CAD MOT file. The JSON file is
# displayed below:
#
# .. literalinclude :: ../../../../samples/general/duty_cycle_custom_variables.json
#    :language: json


def read_json():
    # find JSON file "duty_cycle_custom_variables.json" located in MOT file folder
    mot_file = mc.get_variable("CurrentMotFilePath_MotorLAB")
    json_path = mot_file.replace(".mot", r"\duty_cycle_custom_variables.json")
    with open(json_path, "r") as f:
        data = json.load(f)
        return data


# %%
# Define a function to be run from the "main" function of the "thermal_transient" class in the
# "FUNCTIONS RUN DURING CALCULATIONS" section below.
#
# * Get the custom variable parameter names and input values for each duty cycle period from
#   the JSON configuration file.
#
# * Check the current time in the transient calculation and get the corresponding custom variable
#   input values.
#
# * Set the variables.
def set_custom_variables(data):
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


class thermal_transient:
    def initial(self):
        global data
        # Called before calculation
        self.step = 0
        print("Thermal Transient - Initial")
        # Determine whether the transient calculation is Duty Cycle
        self.calc_type = mc.get_variable("ThermalCalcType")
        if self.calc_type == 1:
            print("Duty Cycle calculation")
            # Use the ``read_json`` function to find and open the JSON file located in MOT file
            # folder
            data = read_json()

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Transient State - Main")
        # If the Duty Cycle is being run, set the custom variables
        if self.calc_type == 1:
            set_custom_variables(data)

    def final(self):
        # Called after calculation
        print("Thermal Transient - Final")


# %%
# Note
# ----
# For more information about transient thermal analysis, see the Scripting Control In
# Duty Cycle tutorial, installed under
# C:\ANSYS_Motor-CAD\VersionNumber\Tutorials\Scripting_Control_In_Duty_Cycle.

# %%
# PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
try:
    from samples_setup_scripts.samples_setup_script import run_duty_cycle_variable_inputs_sample
except ImportError:
    pass
else:
    run_duty_cycle_variable_inputs_sample(mc)

mc.set_variable("MessageDisplayState", 0)
