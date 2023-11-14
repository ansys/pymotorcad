"""
.. _ref_internal_scripting_emag:

E-magnetic
==========
This example demonstrates internal scripting E-Mag functionality
"""

import os

# %%
# Perform required imports
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()

# %%
# Disable pop-up messages
mc.set_variable("MessageDisplayState", 2)


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
# Create internal script
# This could also be saved in a separate file
internal_script = """
import ansys.motorcad.core as pymotorcad
mcApp = pymotorcad.MotorCAD()

# This function is called when "Run" is pressed
def main():
    pass

class emagnetic():
    def initial(self):
        mcApp.display_screen('Scripting')
        shaft_speed = mcApp.get_variable('ShaftSpeed')
        if shaft_speed > 1000:
            print('Shaft speed is too high. Resetting to 500')
            mcApp.set_variable('ShaftSpeed',500)

    def final(self):
        loss_total = mcApp.get_variable('loss_total')
        # display total loss rounded to 2dp if available
        print('total loss is: ' + str(round(loss_total,2)))
        mcApp.display_screen('Calculation')
"""

# %%
# Save script string to file and load into Motor-CAD
load_script_from_string(mc, internal_script)

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
# ~~~~~~~
# Get all messages
messages = mc.get_messages(0)
for message in reversed(messages):
    print(message)

# Check shaft speed was reset by internal script
print("Shaft speed:" + str(mc.get_variable("ShaftSpeed")))
