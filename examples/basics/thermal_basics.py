"""
.. _ref_thermal_basics:

Motor-CAD thermal example script
================================
This example provides a Motor-CAD thermal script.
"""

# %%
# Set up example
# --------------
# To set up the example, perform imports, specify the working directory, launch Motor-CAD, and
# disable all popup messages from Motor-CAD. The e8 IPM motor template is loaded for the thermal
# analysis.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Import ``pymotorcad`` to access Motor-CAD. Import ``pyplot`` from ``matplotlib`` to display
# graphics. Import ``os``, ``shutil``  and ``tempfile`` to open and save a temporary MOT
# file if none is open.

# sphinx_gallery_thumbnail_number = -2
import os
import shutil
import tempfile

import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

# %%
# Specify working directory
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the file to a temporary folder
working_folder = os.path.join(tempfile.gettempdir(), "basic_examples")
try:
    shutil.rmtree(working_folder)
except:
    pass
os.mkdir(working_folder)
mot_name = "e8_Thermal"

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~
# Connect to Motor-CAD and open a new Motor-CAD instance. To keep a new Motor-CAD instance open
# after executing the script, use the ``MotorCAD(keep_instance_open=True)`` option when opening the
# new instance.
print("Starting initialisation.")
mc = pymotorcad.MotorCAD(keep_instance_open=True)

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~
# Disable all popup messages from Motor-CAD by setting the ``MessageDisplayState`` parameter to 2.
#
# .. note::
#    This will also disable crucial popups, for example prompts to save data or overwrite data, or
#    dialogs used to reconcile differences in material data between the database and MOT file. In
#    each case the default action will be taken. This setting will persist until Motor-CAD is
#    closed.
mc.set_variable("MessageDisplayState", 2)

# %%
# Open template file
# ~~~~~~~~~~~~~~~~~~
# This example is based on the e8 IPM motor template. Open the template and save the file to the
# temporary folder.
mc.load_template("e8")
mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# %%
# Set Motor-CAD to Thermal
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Show the Thermal context in Motor-CAD and ensure that the BPM
# Motor Type is set.
mc.show_thermal_context()
mc.set_variable("Motor_Type", 0)
print("Initialisation completed.")

# %%
# Set up analysis
# ---------------
# Setting up the analysis consists of setting the geometry and thermal input data parameters and
# saving the file.
#
# Geometry setup
# ~~~~~~~~~~~~~~
# Display the **Scripting** tab and set the housing outer diameter to 250 mm.
#
# .. note::
#    To set parameter values via automation with the GUI visible, a different tab must be displayed.
#    The **Scripting** tab is chosen because no parameters on this tab will be changed in this
#    script. It is best practice to display the **Scripting** tab when changing input parameters by
#    automation. This is required only if the GUI is shown.
mc.display_screen("Scripting")
mc.set_variable("Housing_Dia", 250)

# %%
# Thermal input data setup
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Set the housing water jacket cooling parameters:
#
# * Fluid volume flow rate (in units of m\ :sup:`3`/s).
#
# * Fluid inlet temperature (in units of °C).
#
# * Fluid used by the HWJ (from material database).
mc.set_variable("WJ_Fluid_Volume_Flow_Rate", 0.002)
mc.set_variable("WJ_Fluid_Inlet_Temperature", 25)
mc.set_fluid("HousingWJFluid", "Dynalene HF-LO")

# %%
# Disable the option for *Active Cooling Only*, so that the HWJ channel also cools the front and
# rear housing segments.
mc.set_variable("Water_Jacket_Active_Cooling_Only", 0)

# %%
# Enable the *Input h* option to allow user input of the heat transfer coefficients for HWJ cooling
# of the rear and active segments of the housing.
mc.set_variable("Calc/Input_h[WJ]_Rear_Housing", 1)
mc.set_array_variable("HousingWJ_CalcInputH_A", 0, 1)

# %%
# Get fluid properties (thermal conductivity, density and dynamic viscosity) and the fluid
# velocities for the rear and active segments of the housing. Calculate new heat transfer
# coefficients for the rear and active segments of the housing. Run a steady state thermal
# calculation to ensure that the fluid properties and velocities are correctly calculated based on
# the model changes made earlier.
#
# .. note::
#    Some Motor-CAD output parameters are not automatically updated when an input parameter is set.
#    Outputs will be updated when a steady state thermal calculation runs. Alternatively, the
#    relevant tab (for example, *Input Data -> Housing Water Jacket -> Heat Transfer*) can be
#    displayed - however this may not be suitable when running Motor-CAD without the GUI.
mc.do_steady_state_analysis()
wj_fluid_k = mc.get_variable("WJ_Fluid_Thermal_Conductivity")
wj_fluid_rho = mc.get_variable("WJ_Fluid_Density")
wj_fluid_mu = mc.get_variable("WJ_Fluid_Dynamic_Viscosity")
wj_fluid_u_r = mc.get_variable("WJ_Channel_Fluid_Velocity_[Rear]")
wj_fluid_u_a = mc.get_array_variable("HousingWJ_Velocity_A", 0)

h_R = 0.005 * wj_fluid_k * wj_fluid_rho * wj_fluid_u_r / wj_fluid_mu
h_A = 0.005 * wj_fluid_k * wj_fluid_rho * wj_fluid_u_a / wj_fluid_mu

print("h_A = ", h_A)
print("h_R = ", h_R)

# %%
# Set the calculated heat transfer coefficients for HWJ cooling of the rear and active segments of
# the housing.
mc.set_array_variable("HousingWJ_InputH_A", 0, h_A)
mc.set_variable("Input_Value_h[WJ]_Rear_Housing", h_R)

# %%
# Save the file.
mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# %%
# Calculate steady state
# ----------------------
# Calculate the steady state.
try:
    mc.do_steady_state_analysis()
    print("Thermal calculation successfully completed.")
except pymotorcad.MotorCADError:
    print("Thermal calculation failed.")

# %%
# Retrieve the magnet temperature.
node_temperature = mc.get_node_temperature(13)
print("Node Temp = ", node_temperature)

# %%
# Retrieve the minimum, maximum, and average winding temperatures.
winding_temperature_min = mc.get_variable("T_[Winding_Min]")
winding_temperature_max = mc.get_variable("T_[Winding_Max]")
winding_temperature_average = mc.get_variable("T_[Winding_Average]")
print("Min = ", winding_temperature_min)
print("Max = ", winding_temperature_max)
print("Average = ", winding_temperature_average)

# %%
# Run simulation
# --------------
# Run the transient simulation.
mc.set_variable("Transient_Calculation_Type", 0)
mc.set_variable("Transient_Time_Period", 60)

try:
    mc.do_transient_analysis()
except pymotorcad.MotorCADError:
    print("Thermal calculation failed.")

# %%
# Get the transient results.
num_time_steps = 51
winding_temp_average_transient = []
time = []

for timeStep in range(num_time_steps):
    try:
        (x, y) = mc.get_temperature_graph_point("Winding (Avg)", timeStep)
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
mc.quit()
