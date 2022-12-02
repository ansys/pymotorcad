"""This is an example about how to script Motor-CAD."""

# Import the relevant packages - these must be installed first
# See the Motor-CAD ActiveX tutorial section 7 for more information

# Retain pyqt4 compatibility
import os

import matplotlib.pyplot as plt

from ansys.motorcad.core import MotorCADError

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

## User setup
# Change this to a location on your PC where you would like to save the model/results files.
# This folder must exist
# Make sure the folder path ends in \\
workingFolder = "C:/Workspace/pyCharmProjects/RPC_Testing/Compatibility/"

if os.path.isdir(workingFolder) == False:
    print("Working folder does not exist. Please choose a folder that exists and try again.")
    print(workingFolder)
    exit()

# Initialise ActiveX automation and launch Motor-CAD
print("Start Initialisation")
import ansys.motorcad.core as pymotorcad

mcad = pymotorcad.MotorCAD()
# Disable all popup messages from Motor-CAD
mcad.set_variable("MessageDisplayState", 2)
print("Initialisation Complete")
print("Running Simulation")

# Show magnetic context
mcad.show_magnetic_context()

# Display scripting tab
mcad.display_screen("Scripting")

# Set Geometry
mcad.set_variable("Slot_Number", 24)
mcad.set_variable("Tooth_Width", 6)
mcad.set_variable("Magnet_Thickness", 4.5)

# Custom Winding Example
# This gives an example of the commands needed to create a custom winding pattern
# This will not create a full winding pattern - need to specify parameters for all coils
# Set the winding type to custom
# mcad.set_variable('MagWindingType', 1)
# Set the Path type to Upper and Lower
# mcad.set_variable('MagPathType', 1)
# Set the number of phases, parallel paths and winding layers:
# mcad.set_variable('MagPhases', 3)
# mcad.set_variable('ParallelPaths', 1)
# mcad.set_variable('WindingLayers', 2)
# Define a coil's parameters
# SetWindingCoil(Phase, Path, Coil, Goslot, GoPosition, ReturnSlot, ReturnPoisition, Turns)
# mcad.set_winding_coil(2, 1, 3, 4, 'b', 18, 'a', 60)


# Set the stator/rotor lamination materials
mcad.set_component_material("Stator Lam (Back Iron)", "M250-35A")
mcad.set_component_material("Rotor Lam (Back Iron)", "M250-35A")

# Set the torque calculation options
PointsPerCycle = 30
NumberCycles = 1
mcad.set_variable("TorquePointsPerCycle", PointsPerCycle)
mcad.set_variable("TorqueNumberCycles", NumberCycles)

# Disable all performance tests except for transient torque
mcad.set_variable("BackEMFCalculation", False)
mcad.set_variable("CoggingTorqueCalculation", False)
mcad.set_variable("ElectromagneticForcesCalc_OC", False)
mcad.set_variable("TorqueSpeedCalculation", False)
mcad.set_variable("DemagnetizationCalc", False)
mcad.set_variable("ElectromagneticForcesCalc_Load", False)
mcad.set_variable("InductanceCalc", False)
mcad.set_variable("BPMShortCircuitCalc", False)
# Enable transient torque
mcad.set_variable("TorqueCalculation", True)

# Set the operating point
mcad.set_variable("Shaft_Speed_[RPM]", 1000)
mcad.set_variable("CurrentDefinition", 0)
mcad.set_variable("PeakCurrent", 3)
mcad.set_variable("DCBusVoltage", 350)
mcad.set_variable("PhaseAdvance", 45)

# Save the file
filename = workingFolder + "ActiveX_Scripting_EMagnetic.mot"
mcad.save_to_file(filename)

# Run the simulation and report success
mcad.do_magnetic_calculation()


# Export data to csv file
exportFile = workingFolder + "Export_EMag_Results.csv"
try:
    mcad.export_results("EMagnetic", exportFile)
    mcad.show_message("Results successfully exported")
except MotorCADError:
    mcad.show("Results failed to export")

# Get results
ShaftTorque = mcad.get_variable("ShaftTorque")
LineVoltage = mcad.get_variable("PeakLineLineVoltage")

# Torque graph data
NumTorquePoints = (PointsPerCycle * NumberCycles) + 1
RotorPosition = []
TorqueVW = []
for n in range(NumTorquePoints):
    (x, y) = mcad.get_magnetic_graph_point("TorqueVW", n)
    RotorPosition.append(x)
    TorqueVW.append(y)

# Airgap flux density graph data
loop = 0
success = 0
MechAngle = []
AirgapFluxDensity = []
# Keep looking until we cannot find the point
while success == 0:
    try:
        (x, y) = mcad.get_fea_graph_point("B Gap (on load)", 1, loop, 0)
        MechAngle.append(x)
        AirgapFluxDensity.append(y)
        loop = loop + 1
    except MotorCADError:
        success = 1


# Harmonics
mcad.initialise_tab_names()
mcad.display_screen("Graphs;Harmonics;Torque")

NumHarmonicPoints = (PointsPerCycle * NumberCycles) + 1
DataPoint = []
Torque = []
for n in range(NumHarmonicPoints):
    try:
        (x, y) = mcad.get_magnetic_graph_point("HarmonicDataCycle", n)
        DataPoint.append(x)
        Torque.append(y)
    except MotorCADError:
        mcad.show("Results failed to export")


print("Simulation Complete")

# Create Graph
plt.subplot(211)
plt.plot(MechAngle, AirgapFluxDensity)
plt.xlabel("Mech Angle")
plt.ylabel("Airgap Flux Density")
plt.subplot(212)
plt.plot(RotorPosition, TorqueVW)
plt.xlabel("Rotor Position")
plt.ylabel("TorqueVW")
plt.figure(2)
plt.plot(DataPoint, Torque)
plt.xlabel("DataPoint")
plt.ylabel("Torque (Nm)")
plt.show()

# Close Motor-CAD
mcad.quit()
# If you wish to continue working with this instance of Motor-CAD, use the
# following line instead of Quit:
# mcad.set_variable('MessageDisplayState', 0)
