"""
.. _ref_internal_scripting_thermal_steady_state:

Thermal steady-state
====================
This example demonstrates internal scripting thermal steady-state functionality
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

class thermal_steady():
    # Select nodes to update
    housing_node = 1
    ambient_node = 0
    def initial(self):
        # Adjust Losses
        mcApp.display_screen('Scripting')
        mcApp.set_variable('Armature_Copper_Loss_@Ref_Speed',200)

    def main(self):
        pass

    def final(self):
        # Called after calculation
        print('Thermal Steady State - Final')
"""

# %%
# Load script into Motor-CAD
load_script_from_string(mc, internal_script)

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
# We will update the resistance between nodes with the following equation:
# resistance = (0.01 × ambient_temp) + 1
internal_script = """
import ansys.motorcad.core as pymotorcad
mcApp = pymotorcad.MotorCAD()

# This function is called when "Run" is pressed
def main():
    pass

class thermal_steady():
    # Select nodes to update
    housing_node = 1
    ambient_node = 0
    def initial(self):
        # Adjust Losses
        mcApp.display_screen('Scripting')
        mcApp.set_variable('Armature_Copper_Loss_@Ref_Speed',200)

    def main(self):
        ambient_temp = mcApp.get_variable('T_Ambient')
        resistance = (ambient_temp * 0.01) + 1
        mcApp.set_resistance_value('Custom Resistance',self.ambient_node,
                                   self.housing_node, resistance,'')
        print(str(resistance))

    def final(self):
        # Get temperature from node
        housing_temp = mcApp.get_node_temperature(self.housing_node)
        print('Housing Temperature: ' + str(round(housing_temp,1)))
"""

# %%
# Load script into Motor-CAD
load_script_from_string(mc, internal_script)

# %%
# Do steady-state analysis with new internal script
mc.do_steady_state_analysis()

# %%
# Results
# -------
# Get all messages
messages = mc.get_messages(3)
for message in reversed(messages):
    print(message)
