"""Example Motor-CAD scripting."""
# Install the relevant packages
# Retain pyqt4 compatibility
import os

import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# Initialise ActiveX automation and launch Motor-CAD
print("Start Initialisation")
mcad = pymotorcad.MotorCAD()

# Disable all popup messages from Motor-CAD
mcad.set_variable("MessageDisplayState", 2)

# Open relevant file
working_folder = os.path.dirname(os.path.realpath(__file__))
mcad.load_template("e8")
mcad_name = "e8_mobility"
mcad.save_to_file(os.path.join(working_folder, mcad_name))

mcad.load_from_file(os.path.join(working_folder, mcad_name, ".mot"))

print("Initialisation Complete")
print("Running Simulation")

# Show thermal context
mcad.show_thermal_context()

# Display scripting tab
mcad.display_screen("Scripting")

# Change housing diameter
mcad.set_variable("Housing_Dia", 250)

# Set the WJ Fluid Volume Flow Rate
mcad.set_variable("WJ_Fluid_Volume_Flow_Rate", 0.002)

# Set the WJ Fluid Inlet Temperature
mcad.set_variable("WJ_Fluid_Inlet_Temperature", 25)

# Change the cooling fluid
mcad.set_fluid("HousingWJFluid", "Dynalene HF-LO")

# Heat Transfer Correlation
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

# Save File
mcad.save_to_file(os.path.join(working_folder, "MotorCAD_Thermal_Python.mot"))

# Steady state calculation
try:
    mcad.do_steady_state_analysis()
    mcad.show_message("Thermal calculation successfully completed")
except pymotorcad.MotorCADError:
    mcad.show_message("Thermal calculation failed")


# Retrieve magnet temperature
node_temperature = mcad.get_node_temperature(13)
print("Node Temp = ", node_temperature)

# Retrieve min/max/average values
winding_temperature_min = mcad.get_variable("T_[Winding_Min]")
winding_temperature_max = mcad.get_variable("T_[Winding_Max]")
winding_temperature_average = mcad.get_variable("T_[Winding_Average]")
print("Min = ", winding_temperature_min)
print("Max = ", winding_temperature_max)
print("Average = ", winding_temperature_average)

# Transient Simulation
mcad.set_variable("Transient_Calculation_Type", 0)
mcad.set_variable("Transient_Time_Period", 60)

try:
    mcad.do_transient_analysis()
except pymotorcad.MotorCADError:
    mcad.show_message("Thermal calculation failed")

# Transient Results
num_time_steps = 51
winding_temp_average_transient = []
time = []

for timeStep in range(num_time_steps):
    try:
        (x, y) = mcad.get_temperature_graph_point("Winding (Avg)", timeStep)
        time.append(x)
        winding_temp_average_transient.append(y)
    except pymotorcad.MotorCADError:
        mcad.show_message("Export failed")

# Graph
plt.figure(1)
plt.plot(time, winding_temp_average_transient)
plt.xlabel("Time")
plt.ylabel("WindingTemp_Average_Transient")
plt.show()

mcad.quit()
