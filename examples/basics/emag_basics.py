"""
.. _ref_emag_basics:

Motor-CAD E-Mag example script
===============================
"""

# %%
# Setup
# -----
# Import the relevant packages
# These must be installed first
# See the Motor-CAD ActiveX tutorial section 7 for more information

import os

import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# User setup
working_folder = os.getcwd()

if os.path.isdir(working_folder) is False:
    print("Working folder does not exist. Please choose a folder that exists and try again.")
    print(working_folder)
    exit()

# %%
# Initialise ActiveX automation and launch Motor-CAD

print("Start Initialisation")
mcad = pymotorcad.MotorCAD()

# %%
# Disable all popup messages from Motor-CAD
mcad.set_variable("MessageDisplayState", 2)
print("Initialisation Complete")
print("Running Simulation")

# %%
# Calculation
# ---------------
# Show magnetic context
mcad.show_magnetic_context()

# %%
# Display scripting tab
mcad.display_screen("Scripting")

# %%
# Set Geometry
mcad.set_variable("Slot_Number", 24)
mcad.set_variable("Tooth_Width", 6)
mcad.set_variable("Magnet_Thickness", 4.5)

# %%
# Custom Winding Example
# This gives an example of the commands needed to create a custom winding pattern
# This will not create a full winding pattern - need to specify parameters for all coils
#
# Set the winding type to custom:
# :code:`mcad.set_variable('MagWindingType', 1)`
#
# Set the Path type to Upper and Lower
# :code:`mcad.set_variable('MagPathType', 1)`
#
# Set the number of phases:
# :code:`mcad.set_variable('MagPhases', 3)`
#
# Set the number of parallel paths:
# :code:`mcad.set_variable('ParallelPaths', 1)`
#
# Set the number of winding layers:
# :code:`mcad.set_variable('WindingLayers', 2)`
#
# Define a coil's parameters with
# :code:`set_winding_coil(phase,
# path, coil, go_slot, go_position, return_slot, return_position, turns)`

# %%
# Set the stator/rotor lamination materials
mcad.set_component_material("Stator Lam (Back Iron)", "M250-35A")
mcad.set_component_material("Rotor Lam (Back Iron)", "M250-35A")

# %%
# Set the torque calculation options
points_per_cycle = 30
number_cycles = 1
mcad.set_variable("TorquePointsPerCycle", points_per_cycle)
mcad.set_variable("TorqueNumberCycles", number_cycles)

# %%
# Disable all performance tests except for transient torque
mcad.set_variable("BackEMFCalculation", False)
mcad.set_variable("CoggingTorqueCalculation", False)
mcad.set_variable("ElectromagneticForcesCalc_OC", False)
mcad.set_variable("TorqueSpeedCalculation", False)
mcad.set_variable("DemagnetizationCalc", False)
mcad.set_variable("ElectromagneticForcesCalc_Load", False)
mcad.set_variable("InductanceCalc", False)
mcad.set_variable("BPMShortCircuitCalc", False)

# %%
# Enable transient torque
mcad.set_variable("TorqueCalculation", True)

# %%
# Set the operating point
mcad.set_variable("Shaft_Speed_[RPM]", 1000)
mcad.set_variable("CurrentDefinition", 0)
mcad.set_variable("PeakCurrent", 3)
mcad.set_variable("DCBusVoltage", 350)
mcad.set_variable("PhaseAdvance", 45)

# %%
# Save the file
filename = os.path.join(working_folder, "../ActiveX_Scripting_EMagnetic.mot")
mcad.save_to_file(filename)

# %%
# Run the simulation and report success
mcad.do_magnetic_calculation()

# %%
# Results
# -------
# Export data to csv file
exportFile = os.path.join(working_folder, "../Export_EMag_Results.csv")
try:
    mcad.export_results("EMagnetic", exportFile)
    print("Results successfully exported")
except pymotorcad.MotorCADError:
    print("Results failed to export")

# %%
# Get results
shaft_torque = mcad.get_variable("ShaftTorque")
line_voltage = mcad.get_variable("PeakLineLineVoltage")

# %%
# Torque graph data
num_torque_points = (points_per_cycle * number_cycles) - 1
rotor_position = []
torque_vw = []

for n in range(num_torque_points):
    (x, y) = mcad.get_magnetic_graph_point("TorqueVW", n)
    rotor_position.append(x)
    torque_vw.append(y)

# %%
# Airgap flux density graph data
loop = 0
success = 0
mech_angle = []
airgap_flux_density = []

# %%
# Keep looking until we cannot find the point
while success == 0:
    try:
        (x, y) = mcad.get_fea_graph_point("B Gap (on load)", 1, loop, 0)
        mech_angle.append(x)
        airgap_flux_density.append(y)
        loop = loop + 1
    except pymotorcad.MotorCADError:
        success = 1

# %%
# Harmonics
mcad.initialise_tab_names()
mcad.display_screen("Graphs;Harmonics;Torque")

num_harmonic_points = (points_per_cycle * number_cycles) + 1
data_point = []
torque = []
for n in range(num_harmonic_points):
    try:
        (x, y) = mcad.get_magnetic_graph_point("HarmonicDataCycle", n)
        data_point.append(x)
        torque.append(y)
    except pymotorcad.MotorCADError:
        print("Results failed to export")


print("Simulation Complete")


# %%
# Plot Results
# ============
# Create Graph
plt.subplot(211)
plt.plot(mech_angle, airgap_flux_density)
plt.xlabel("Mech Angle")
plt.ylabel("Airgap Flux Density")
plt.subplot(212)
plt.plot(rotor_position, torque_vw)
plt.xlabel("Rotor Position")
plt.ylabel("TorqueVW")
plt.figure(2)
plt.plot(data_point, torque)
plt.xlabel("DataPoint")
plt.ylabel("Torque (Nm)")
plt.show()

# %%
# Close Motor-CAD
mcad.quit()

# %%
# If you wish to continue working with this instance of Motor-CAD, use the
# following line instead of Quit:
# :code:`mcad.set_variable('MessageDisplayState', 0)`
