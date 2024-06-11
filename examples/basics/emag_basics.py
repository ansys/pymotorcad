"""
.. _ref_emag_basics:

Motor-CAD E-magnetic example script
===================================
This example provides a Motor-CAD E-magnetic script. This script
creates a partial custom winding pattern to change
parameter values, run the analysis, and plot results. To create
a full winding pattern, parameters must be specified
for all coils.
"""

# %%
# Set up example
# --------------
# Setting up this example consists of performing imports, specifying the
# working directory, launching Motor-CAD, and disabling all popup
# messages from Motor-CAD.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Import ``pymotorcad`` to access Motor-CAD. Import ``pyplot`` from ``matplotlib`` to display
# graphics. Import ``os``, ``shutil``, ``sys``, and ``tempfile`` to open and save a temporary MOT
# file if none is open.


import os
import shutil
import tempfile

import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

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
mot_name = "EMagnetic"
# mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# working_folder = os.getcwd()
#
# if os.path.isdir(working_folder) is False:
#     print("Working folder does not exist. Choose a folder that exists and try again.")
#     print(working_folder)
#     exit()

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~

print("Starting initialization.")
mc = pymotorcad.MotorCAD(keep_instance_open=True)

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("MessageDisplayState", 2)
print("Initialisation completed.")
print("Running simulation.")

# %%
# Create analysis
# ---------------
# Creating the analysis consists of showing the magnetic context, displaying
# the **Scripting** tab, setting the geometry and parameters, and saving
# the file.
#
# Show the magnetic context.
mc.show_magnetic_context()

# %%
# Display the **Scripting** tab.
mc.display_screen("Scripting")

# %%
# Ensure that the BPM Motor Type is set.
mc.set_variable("Motor_Type", 0)

# %%
# Set the geometry.
mc.set_variable("Slot_Number", 24)
mc.set_variable("Tooth_Width", 6)
mc.set_variable("Magnet_Thickness", 4.5)

# %%
# Set parameters for creating the custom winding pattern.
#
# The following code creates only a partial winding pattern.
#
# Set the winding type to custom:
mc.set_variable("MagneticWindingType", 2)  # :code:`mc.set_variable('MagWindingType', 1)`

#
# Set the path type to upper and lower:
mc.set_variable("MagPathType", 1)  # :code:`mc.set_variable('MagPathType', 1)`
#
# Set the number of phases:
mc.set_variable("MagPhases", 3)  # :code:`mc.set_variable('MagPhases', 3)`
#
# Set the number of parallel paths:
mc.set_variable("ParallelPaths", 1)  # :code:`mc.set_variable('ParallelPaths', 1)`
#
# Set the number of winding layers:
mc.set_variable("WindingLayers", 2)  # :code:`mc.set_variable('WindingLayers', 2)`
#
# Define a coil's parameters:
mc.set_winding_coil(2, 1, 3, 4, "b", 18, "a", 60)
# :code:`set_winding_coil(phase,
# path, coil, go_slot, go_position, return_slot, return_position, turns)`

# %%
# Set the stator/rotor lamination materials.
mc.set_component_material("Stator Lam (Back Iron)", "M250-35A")
mc.set_component_material("Rotor Lam (Back Iron)", "M250-35A")

# %%
# Set the torque calculation options.
points_per_cycle = 30
number_cycles = 1
mc.set_variable("TorquePointsPerCycle", points_per_cycle)
mc.set_variable("TorqueNumberCycles", number_cycles)

# %%
# Disable all performance tests except the ones for transient torque.
mc.set_variable("BackEMFCalculation", False)
mc.set_variable("CoggingTorqueCalculation", False)
mc.set_variable("ElectromagneticForcesCalc_OC", False)
mc.set_variable("TorqueSpeedCalculation", False)
mc.set_variable("DemagnetizationCalc", False)
mc.set_variable("ElectromagneticForcesCalc_Load", False)
mc.set_variable("InductanceCalc", False)
mc.set_variable("BPMShortCircuitCalc", False)

# %%
# Enable transient torque.
mc.set_variable("TorqueCalculation", True)

# %%
# Set the operating point.
mc.set_variable("Shaft_Speed_[RPM]", 1000)
mc.set_variable("CurrentDefinition", 0)
mc.set_variable("PeakCurrent", 3)
mc.set_variable("DCBusVoltage", 350)
mc.set_variable("PhaseAdvance", 45)

# %%
# Save the file.
filename = os.path.join(working_folder, "../ActiveX_Scripting_EMagnetic.mot")
mc.save_to_file(filename)

# %%
# Run simulation
# --------------
# Run the simulation.
mc.do_magnetic_calculation()

# %%
# Export results to CSV file
# --------------------------
# Export results to a CSV file.
exportFile = os.path.join(working_folder, "../Export_EMag_Results.csv")
try:
    mc.export_results("EMagnetic", exportFile)
    print("Results successfully exported.")
except pymotorcad.MotorCADError:
    print("Results failed to export.")

# %%
# Get and analyze results
# -----------------------
# Get torque and voltage data.
shaft_torque = mc.get_variable("ShaftTorque")
line_voltage = mc.get_variable("PeakLineLineVoltage")

# %%
# Graph the torque data.
num_torque_points = points_per_cycle * number_cycles
rotor_position = []
torque_vw = []

for n in range(num_torque_points):
    (x, y) = mc.get_magnetic_graph_point("TorqueVW", n)
    rotor_position.append(x)
    torque_vw.append(y)

# %%
# Graph the airgap flux density data.
loop = 0
success = 0
mech_angle = []
airgap_flux_density = []

# %%
# Keep looking until you cannot find the point.
while success == 0:
    try:
        (x, y) = mc.get_fea_graph_point("B Gap (on load)", 1, loop, 0)
        mech_angle.append(x)
        airgap_flux_density.append(y)
        loop = loop + 1
    except pymotorcad.MotorCADError:
        success = 1

# %%
# Graph the harmonic data.
mc.initialise_tab_names()
mc.display_screen("Graphs;Harmonics;Torque")

num_harmonic_points = (points_per_cycle * number_cycles) + 1
data_point = []
torque = []
for n in range(num_harmonic_points):
    try:
        (x, y) = mc.get_magnetic_graph_point("HarmonicDataCycle", n)
        data_point.append(x)
        torque.append(y)
    except pymotorcad.MotorCADError:
        print("Results failed to export.")


print("Simulation completed.")


# %%
# Plot results
# ------------
# Plot results from the simulation.
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
# Exit Motor-CAD
# --------------
# Exit Motor-CAD.
mc.quit()

# %%
# If you want to continue working with this instance of Motor-CAD, rather
# than using the preceding command, use this command:
# :code:`mc.set_variable('MessageDisplayState', 0)`
