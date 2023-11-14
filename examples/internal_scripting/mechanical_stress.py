"""
.. _ref_internal_scripting_mechanical_stress:

Mechanical stress
=================
This example demonstrates internal scripting mechanical stress functionality
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
import ansys.motorcad.core as pymotorcad
mcApp = pymotorcad.MotorCAD()

# This function is called when "Run" is pressed
def main():
    pass

class mechanical_stress():
    def initial(self):
        # Called before calculation
        mcApp.set_variable('ShaftSpeed',1500)

    def final(self):
        # Called after calculation
        yield_stress = mcApp.get_variable('YieldStress_RotorLam')
        max_stress = mcApp.get_variable('MaxStress_RotorLam')

        print('Max Stress: ' + str(max_stress))

        safety_factor = yield_stress / max_stress

        print('Safety factor is: ' + str(round(safety_factor,3)))
"""

# %%
# Load script into Motor-CAD
load_script_from_string(mc, internal_script)

# %%
# Enable internal scripting
mc.set_variable("ScriptAutoRun_PythonClasses", 1)

# %%
# Solve rotor stress model
mc.do_mechanical_calculation()

# %%
# Results
# ~~~~~~~
# Get all messages
messages = mc.get_messages(2)
for message in reversed(messages):
    print(message)
