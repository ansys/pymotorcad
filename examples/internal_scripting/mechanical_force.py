"""
.. _ref_internal_scripting_mechanical_force:

Mechanical force
================
This example demonstrates internal scripting mechanical force functionality
This will compute the operating conditions for some requested torque values
and display the natural frequencies for the 0th and 8th modes.

"""

# %%
# Perform required imports

import os

import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()

# %%
# Disable pop-up messages
mc.set_variable("MessageDisplayState", 2)

# %%
# Load e9 template
mc.load_template("e9")


# %%
# Function to load script from a string
def load_script_from_string(mc_instance, script_string):
    # %%
    # Save script string to file and load into Motor-CAD
    internal_script_file = open("temp_example_file.py", "w")
    internal_script_file.write(script_string)

    internal_script_file_path = os.path.realpath(internal_script_file.name)

    internal_script_file.close()

    mc_instance.load_script(internal_script_file_path)


# %%
# Create internal script.
# This could also be saved in a separate file
internal_script = """
import numpy as np
import ansys.motorcad.core as pymotorcad
mcApp = pymotorcad.MotorCAD()

# This function is called when "Run" is pressed
def main():
    pass

class mechanical_forces():
    def initial(self):
        # Called before calculation
        # For each operating point, set requested torque and speed
        # (using this mode requires that a Lab model has been built)
        # Note that if a lab model isn't available, MultiForceLoadPointDefinition
        # can be set to 1 (Current and Phase), and
        # LoadPoint_Current_Array and LoadPoint_PhaseAdvance_Array set
        # IM operating points are set with speed, current, and LoadPoint_Slip_Array
        NVH_Duty_Speed  = np.concatenate((250, 6000, 9000), axis = None)
        NVH_Duty_Torque = np.concatenate((40, 20, 10), axis = None)
        mcApp.set_variable('NumLoadPoints', len(NVH_Duty_Speed))
        for i in range(len(NVH_Duty_Speed)):
            mcApp.set_array_variable('LoadPoint_Speed_Array', i,  float(NVH_Duty_Speed[i]))
            mcApp.set_array_variable('LoadPoint_Torque_Array', i, float(NVH_Duty_Torque[i]))

        # Set number of steps per cycle - for speed just use 30 in this example. 90 would be
        # a more usual minimum
        # If calculating for an induction machine (IM), use IMSingleLoadPointsPerCycle instead
        mcApp.set_variable('TorquePointsPerCycle', 30)

    def final(self):
        # Called after calculation
        # Example modal results
        o_Natural_Freq_Mode_0 = mcApp.get_magnetic_graph_point("NVH_NaturalFrequency", 0)
        o_Natural_Freq_Mode_8 = mcApp.get_magnetic_graph_point("NVH_NaturalFrequency", 8)

        mcApp.show_message(" Natural_Freq_Mode_0 " + str(o_Natural_Freq_Mode_0))
        mcApp.show_message(" Natural_Freq_Mode_8 " + str(o_Natural_Freq_Mode_8))
"""

# %%
# Load script into Motor-CAD
load_script_from_string(mc, internal_script)

# %%
# Enable internal scripting
mc.set_variable("ScriptAutoRun_PythonClasses", 1)

# %%
# Solve rotor stress model
mc.do_multi_force_calculation()

# %%
# Results
# ~~~~~~~
# Get all messages
messages = mc.get_messages(2)
for message in reversed(messages):
    print(message)
# %%
# Note
# ~~~~
# For further details, please see the E-NVH tutorial.
