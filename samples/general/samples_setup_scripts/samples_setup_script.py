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

import os

import matplotlib.pyplot as plt


def run_duty_cycle_variable_inputs_sample_old(mc):
    mc.set_variable("MessageDisplayState", 2)

    # %%
    # Load e9 template
    # mc.load_template("e9")
    mc.load_from_file("C:\\Workspace\\MotorCAD_thermal_scripts\\e10_HWJ_vary_temp_3.mot")

    # %%
    # Load script into Motor-CAD
    script_path = os.getcwd().split("samples")[0] + "samples\\general\\thermal_duty_cycle_inputs.py"
    mc.load_script(script_path)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # %%
    # Solve thermal model
    mc.do_transient_analysis()

    # %%
    # Results
    # -------
    mc.set_variable("MessageDisplayState", 2)
    time, winding_temp_average_transient = mc.get_temperature_graph("Winding (Avg)")

    # %%
    # Plot results
    # ~~~~~~~~~~~~
    # Plot results from the simulation.
    plt.figure(1)
    plt.plot(time, winding_temp_average_transient)
    plt.xlabel("Time")
    plt.ylabel("WindingTemp_Average_Transient")
    plt.show()


def run_duty_cycle_variable_inputs_sample(mc):
    mc.set_variable("MessageDisplayState", 2)

    # %%
    # Load e10 template
    mc.load_template("e10")
    # mc.load_from_file("C:\\Workspace\\MotorCAD_thermal_scripts\\e10_HWJ_vary_temp_3.mot")

    # %%
    # Load script into Motor-CAD
    script_path = os.getcwd().split("samples")[0] + "samples\\general\\thermal_duty_cycle_inputs.py"
    mc.load_script(script_path)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # %%
    # Set up Motor-CAD Duty Cycle
    mc.set_variable("ThermalCalcType", 1)  # thermal transient calculation
    mc.set_variable("TransientCalculationType", 1)  # duty cycle calculation
    mc.set_variable("TransientPointsToPlot", 1)  # point storage reduction - plot every point
    mc.set_variable("Transient_Number_Cycles", 1)  # set to 1 cycle
    mc.set_variable("Duty_Cycle_Definition", 0)  # torque-speed definition
    duty_cycle_periods = 5
    mc.set_variable("Duty_Cycle_Num_Periods", duty_cycle_periods)  # 5 Duty Cycle periods
    mc.set_variable("Duty_Cycle_Input_Type", 0)  # per unit torque definition
    mc.set_variable("Reference_Shaft_Torque", 260)  # 260 Nm reference torque
    duty_cycle_times = [20, 40, 30, 40, 10]
    duty_cycle_points = [4, 4, 4, 5, 3]
    duty_cycle_torque = [1, 2.5, 0.1, 3, 0.3]
    duty_cycle_speed_start = [3000, 3000, 6000, 0, 4000]
    duty_cycle_speed_end = [3000, 6000, 0, 4000, 3000]
    for i in range(duty_cycle_periods):
        mc.set_array_variable("Duty_Cycle_Time", i, duty_cycle_times[i])
        mc.set_array_variable("Duty_Cycle_Points", i, duty_cycle_points[i])
        mc.set_array_variable("Duty_Cycle_Torque_Start", i, duty_cycle_torque[i])
        mc.set_array_variable("Duty_Cycle_Speed_Start", i, duty_cycle_speed_start[i])
        mc.set_array_variable("Duty_Cycle_Speed_End", i, duty_cycle_speed_end[i])

    # %%
    # Solve thermal model
    mc.do_transient_analysis()

    # %%
    # Results
    # -------
    mc.set_variable("MessageDisplayState", 2)
    time, winding_temp_average_transient = mc.get_temperature_graph("Winding (Avg)")

    # %%
    # Plot results
    # ~~~~~~~~~~~~
    # Plot results from the simulation.
    plt.figure(1)
    plt.plot(time, winding_temp_average_transient)
    plt.xlabel("Time")
    plt.ylabel("WindingTemp_Average_Transient")
    plt.show()
