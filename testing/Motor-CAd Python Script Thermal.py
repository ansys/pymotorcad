# Install the relevant packages
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core import MotorCADError
import matplotlib.pyplot as plt

# Retain pyqt4 compatibility
import os

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# Initialise ActiveX automation and launch Motor-CAD
print('Start Initialisation')
mcad = pymotorcad.MotorCAD()

# Open relevant file
workingFolder = "C:/Workspace/pyCharmProjects/RPC_Testing/Compatibility/"
mcad_name = 'e8_eMobility'
filename = workingFolder + mcad_name + '.mot'
mcad.load_from_file(filename)

# Disable all popup messages from Motor-CAD
mcad.set_variable('MessageDisplayState', 2)
print('Initialisation Complete')
print('Running Simulation')

# Show thermal context
mcad.show_thermal_context()

# Display scripting tab
mcad.display_screen('Scripting')

# Change housing diameter
mcad.set_variable('Housing_Dia', 250)

# Set the WJ Fluid Volume Flow Rate
mcad.set_variable('WJ_Fluid_Volume_Flow_Rate', 0.002)

# Set the WJ Fluid Inlet Temperature
mcad.set_variable('WJ_Fluid_Inlet_Temperature', 25)

# Change the cooling fluid
mcad.set_fluid('HousingWJFluid', 'Dynalene HF-LO')

# Heat Transfer Correlation
mcad.set_variable('Calc/Input_h[WJ]_Rear_Housing', 1)
mcad.set_array_variable('HousingWJ_CalcInputH_A', 0, 1)

WJ_Fluid_K = mcad.get_variable('WJ_Fluid_Thermal_Conductivity')
WJ_Fluid_Rho = mcad.get_variable('WJ_Fluid_Density')
WJ_Fluid_Mu = mcad.get_variable('WJ_Fluid_Dynamic_Viscosity')
WJ_Fluid_U_A = mcad.get_array_variable('HousingWJ_Velocity_A', 0)
WJ_Fluid_U_R = mcad.get_variable('WJ_Channel_Fluid_Velocity_[Rear]')

h_A = 0.005 * WJ_Fluid_K * WJ_Fluid_Rho * WJ_Fluid_U_A / WJ_Fluid_Mu
h_R = 0.005 * WJ_Fluid_K * WJ_Fluid_Rho * WJ_Fluid_U_R / WJ_Fluid_Mu

print('h_A = ', h_A)
print('h_R = ', h_R)

mcad.set_array_variable('HousingWJ_InputH_A', 0, h_A)
mcad.set_variable('Input_Value_h[WJ]_Rear_Housing', h_R)

# Save File
mcad.save_to_file(workingFolder + 'MotorCAD_Thermal_Python.mot')

# Steady state calculation
try:
    mcad.do_steady_state_analysis()
    mcad.show_message("Thermal calculation successfully completed")
except MotorCADError:
    mcad.show_message("Thermal calculation failed")



# Retrieve magnet temperature
NodeTemperature = mcad.get_node_temperature(13)
print('Node Temp = ', NodeTemperature)

# Retrieve min/max/average values
WindingTemperature_Min = mcad.get_variable('T_[Winding_Min]')
WindingTemperature_Max = mcad.get_variable('T_[Winding_Max]')
WindingTemperature_Average = mcad.get_variable('T_[Winding_Average]')
print('Min = ', WindingTemperature_Min)
print('Max = ', WindingTemperature_Max)
print('Average = ', WindingTemperature_Average)

# Transient Simulation
mcad.set_variable('Transient_Calculation_Type', 0)
mcad.set_variable('Transient_Time_Period', 60)

try:
    mcad.do_transient_analysis()
except MotorCADError:
    mcad.show_message("Thermal calculation failed")

# Transient Results
NumTimeSteps = 51
WindingTemp_Average_Transient = []
Time = []

for timeStep in range(NumTimeSteps):
    try:
        (x, y) = mcad.get_temperature_graph_point('Winding (Avg)', timeStep)
        Time.append(x)
        WindingTemp_Average_Transient.append(y)
    except MotorCADError:
        mcad.show_message("Export failed")

# Graph
plt.figure(1)
plt.plot(Time, WindingTemp_Average_Transient)
plt.xlabel('Time')
plt.ylabel('WindingTemp_Average_Transient')
plt.show()

mcad.quit()