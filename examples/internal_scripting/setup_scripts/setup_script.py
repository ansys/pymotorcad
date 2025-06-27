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


def run_emag_demo(mc):
    mc.set_variable("MessageDisplayState", 2)
    # Ensure that the BPM Motor Type is set
    mc.set_variable("Motor_Type", 0)

    script_path = os.getcwd().split("examples")[0] + "examples\\internal_scripting\\emag.py"
    mc.load_script(script_path)

    # %%
    # Enable internal scripting and set shaft speed outside limit specified by script
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)
    mc.set_variable("ShaftSpeed", 10000)

    # %%
    # Disable performance tests and perform calculation
    mc.set_variable("TorqueCalculation", False)
    mc.do_magnetic_calculation()

    # %%
    # Results
    # -------
    # Get all messages
    messages = mc.get_messages(0)
    for message in reversed(messages):
        print(message)

    # Check shaft speed was reset by internal script
    print("Shaft speed:" + str(mc.get_variable("ShaftSpeed")))


def run_mech_force_demo(mc):
    mc.set_variable("MessageDisplayState", 2)
    # %%
    # Load e9 template
    mc.load_template("e9")

    script_path = (
        os.getcwd().split("examples")[0] + "examples\\internal_scripting\\mechanical_force.py"
    )
    mc.load_script(script_path)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # %%
    # Solve rotor stress model
    mc.do_multi_force_calculation()

    # %%
    # Results
    # -------
    # Get all messages
    messages = mc.get_messages(2)
    for message in reversed(messages):
        print(message)


def run_mech_stress_demo(mc):
    mc.set_variable("MessageDisplayState", 2)
    # %%
    # Load e9 template
    mc.load_template("e9")
    # %%
    # Load script into Motor-CAD
    script_path = (
        os.getcwd().split("examples")[0] + "examples\\internal_scripting\\mechanical_stress.py"
    )
    mc.load_script(script_path)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # %%
    # Solve rotor stress model
    mc.do_mechanical_calculation()

    # %%
    # Results
    # -------
    # Get all messages
    messages = mc.get_messages(2)
    for message in reversed(messages):
        print(message)


def run_thermal_steady_demo(mc):
    mc.set_variable("MessageDisplayState", 2)
    # Ensure that the BPM Motor Type is set
    mc.set_variable("Motor_Type", 0)
    # %%
    # Load script into Motor-CAD
    script_path = (
        os.getcwd().split("examples")[0] + "examples\\internal_scripting\\thermal_steady_state.py"
    )
    mc.load_script(script_path)

    # %%
    # Solve thermal model to create node numbers
    mc.do_steady_state_analysis()

    # %%
    # Set armature copper loss to check internal script resets this successfully
    mc.set_variable("Armature_Copper_Loss_@Ref_Speed", 12345)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # Solve thermal model and check armature copper loss resets
    mc.do_steady_state_analysis()
    print("Armature copper loss = " + str(mc.get_variable("Armature_Copper_Loss_@Ref_Speed")))

    # %%
    # Results
    # -------
    # Get all messages
    messages = mc.get_messages(3)
    for message in reversed(messages):
        print(message)


def run_thermal_transient_demo(mc):
    mc.set_variable("MessageDisplayState", 2)

    # %%
    # Load e9 template
    mc.load_template("e9")

    # %%
    # Load script into Motor-CAD
    script_path = (
        os.getcwd().split("examples")[0] + "examples\\internal_scripting\\thermal_transient.py"
    )
    mc.load_script(script_path)

    # %%
    # Enable internal scripting
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)

    # %%
    # Enable wet rotor cooling
    mc.set_variable("Wet_Rotor", True)

    # %%
    # Change housing to water jacket
    mc.set_variable("HousingType", 11)
    mc.set_variable("Housing_Water_Jacket", True)

    # %%
    # Our internal script will change the fluid flow rate through the water
    # jacket depending on the time step
    # Set calculation type to transient and set parameters
    mc.set_variable("ThermalCalcType", 1)
    # %%
    # Set simple thermal transient calculation
    mc.set_variable("TransientCalculationType", 0)
    mc.set_variable("Simple_Transient_Period", 3000)
    # %%
    # Set transient definition to torque - 100Nm
    mc.set_variable("Simple_Transient_Definition", 1)
    mc.set_variable("Simple_Transient_Torque", 100)
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
