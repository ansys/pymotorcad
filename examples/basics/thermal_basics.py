"""
.. _ref_thermal_basics:

Motor-CAD thermal analysis
==========================
"""

# %%
# Set up example
# --------------
# Setting up this example consists of performing imports, launching
# Motor-CAD, disabling all popup messages from Motor-CAD, and
# opening the file for the thermal analysis.

# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Import the required packages.
import os

import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~
# Initialize ActiveX automation and launch Motor-CAD.
print("Starting initialization.")
mcad = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~
# Disable all popup messages from Motor-CAD.
mcad.set_variable("MessageDisplayState", 2)

# %%
# Open relevant file
# ~~~~~~~~~~~~~~~~~~
# Specify the working directory and open the relevant file for the
# thermal analysis.
working_folder = os.getcwd()
mcad.load_template("e8")
mcad_name = "e8_mobility"
mcad.save_to_file(os.path.join(working_folder, mcad_name))

mcad.load_from_file(os.path.join(working_folder, mcad_name + ".mot"))

print("Initialization completed.")

# %%
# Create analysis
# ---------------
# Creating the analysis consists of showing the thermal context, displaying
# the **Scripting** tab, setting parameters, and saving the file.

# Show thermal context
# -----------------------
mcad.show_thermal_context()

# %%
# Display the **Scripting** tab.
mcad.display_screen("Scripting")

# %%
# Change the housing diameter.
mcad.set_variable("Housing_Dia", 250)

# %%
# Set the flow rate of the WJ fluid volume.
mcad.set_variable("WJ_Fluid_Volume_Flow_Rate", 0.002)

# %%
# Set the temperature of the WJ fluid inlet.
mcad.set_variable("WJ_Fluid_Inlet_Temperature", 25)

# %%
# Change the cooling fluid.
mcad.set_fluid("HousingWJFluid", "Dynalene HF-LO")

# %%
# Set the heat transfer correlation.
mcad.set_variable("Calc/Input_h[WJ]_Rear_Housing", 1)
mcad.set_array_variable("HousingWJ_CalcInputH_A", 0, 1)

wj_fluid_k = mcad.get_variable("WJ_Fluid_Thermal_Conductivity")
wj_fluid_rho = mcad.get_variable("WJ_Fluid_Density")
wj_fluid_mu = mcad.get_variable("WJ_Fluid_Dynamic_Viscosity")
wj_fluid_u_a = mcad.get_array_variable("HousingWJ_Velocity_A", 0)
wj_fluid_u_r = mcad.get_variable("WJ_Channel_Fluid_Velocity_[Rear]")

h_A = 0.005 * wj_fluid_k * wj_fluid_rho * wj_fluid_u_a / wj_fluid_mu
h_R = 0.005 * wj_fluid_k * wj_fluid_rho * wj_fluid_u_r / wj_fluid_mu

print("h_A = ", h_A)
print("h_R = ", h_R)

mcad.set_array_variable("HousingWJ_InputH_A", 0, h_A)
mcad.set_variable("Input_Value_h[WJ]_Rear_Housing", h_R)

# %%
# Save the file.
mcad.save_to_file(os.path.join(working_folder, "../MotorCAD_Thermal_Python.mot"))

# %%
# Calculate steady state
# ----------------------
# Calculate the steady state.
try:
    mcad.do_steady_state_analysis()
    print("Thermal calculation successfully completed.")
except pymotorcad.MotorCADError:
    print("Thermal calculation failed.")

# %%
# Retrieve the magnet temperature.
node_temperature = mcad.get_node_temperature(13)
print("Node Temp = ", node_temperature)

# %%
# Retrieve the minimum, maximum, and average winding temperatures.
winding_temperature_min = mcad.get_variable("T_[Winding_Min]")
winding_temperature_max = mcad.get_variable("T_[Winding_Max]")
winding_temperature_average = mcad.get_variable("T_[Winding_Average]")
print("Min = ", winding_temperature_min)
print("Max = ", winding_temperature_max)
print("Average = ", winding_temperature_average)

# %%
# Run simulation
# --------------
# Run the transient simulation.
mcad.set_variable("Transient_Calculation_Type", 0)
mcad.set_variable("Transient_Time_Period", 60)

try:
    mcad.do_transient_analysis()
except pymotorcad.MotorCADError:
    print("Thermal calculation failed.")

# %%
# Get the transient results.
num_time_steps = 51
winding_temp_average_transient = []
time = []

for timeStep in range(num_time_steps):
    try:
        (x, y) = mcad.get_temperature_graph_point("Winding (Avg)", timeStep)
        time.append(x)
        winding_temp_average_transient.append(y)
    except pymotorcad.MotorCADError:
        print("Export failed.")

# %%
# Plot results
# ------------
# Plot results from the simulation.
plt.figure(1)
plt.plot(time, winding_temp_average_transient)
plt.xlabel("Time")
plt.ylabel("WindingTemp_Average_Transient")
plt.show()

# %%
# Exit Motor-CAD
# --------------
# Exit Motor-CAD.
mcad.quit()
