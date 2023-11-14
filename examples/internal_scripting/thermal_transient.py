"""
.. _ref_internal_scripting_thermal_transient:

Thermal transient
=================
This example demonstrates internal scripting thermal transient functionality
"""

# %%
# Perform required imports
import os

import matplotlib.pyplot as plt

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
mc = pymotorcad.MotorCAD()

# This function is called when "Run" is pressed
def main():
    pass

class thermal_transient():
    def initial(self):
        mc.display_screen('Scripting')
        # initialise water jacket and rotor cooling flow rate
        mc.set_variable('Wet_Rotor_Fluid_Volume_Flow_Rate',0.1)
        mc.set_variable('WJ_Fluid_Volume_Flow_Rate', 0.1)

    def main(self):
        current_time = mc.get_variable('CurrentTime')
        if current_time >= 1000 and current_time < 1500:
            # if between 1000 and 1500 s, stop water jacket coolant flow
            mc.set_variable('WJ_Fluid_Volume_Flow_Rate', 0)
        else:
            # if between 1000 and 1500 s, rotor coolant flow
            mc.set_variable('Wet_Rotor_Fluid_Volume_Flow_Rate', 0)

    def final(self):
        # Called after calculation
        print('Thermal Transient - Final')

"""

# %%
# Load script into Motor-CAD
load_script_from_string(mc, internal_script)

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

# %%
# Note
# ----
# For more information about transient thermal analysis, see the Scripting Control In
# Duty Cycle tutorial, installed under
# C:\ANSYS_Motor-CAD\VersionNumber\Tutorials\Scripting_Control_In_Duty_Cycle.
