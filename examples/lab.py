"""Example Motor-CAD scripting."""
# Install Relevant Packages
# Retain pyqt4 compatibility
import os

import matplotlib.pyplot as plt
import scipy.io

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core import MotorCADError

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# Initialise ActiveX automation and launch Motor-CAD
print("Start Initialisation")
mcad = pymotorcad.MotorCAD()

# Open relevant file
working_folder = r"C:/Workspace/pyCharmProjects/RPC_Testing/Compatibility/"
mcad_name = "e8_eMobility"
mcad.load_from_file(os.path.join(working_folder, mcad_name, ".mot"))

# Disable all popup messages from Motor-CAD
mcad.set_variable("MessageDisplayState", 2)
print("Initialisation Complete")
print("Running Simulation")

# Set Lab model build options
mcad.set_variable("ModelType_MotorLAB", 1)
mcad.set_variable("SatModelPoints_MotorLAB", 0)
mcad.set_variable("LossModel_Lab", 0)
mcad.set_variable("ModelBuildSpeed_MotorLAB", 10000)
mcad.set_variable("MaxModelCurrent_MotorLAB", 480)
mcad.set_variable("BuildSatModel_MotorLAB", True)

# Show Lab context
mcad.set_motorlab_context()

# Build model
mcad.clear_model_build_lab()
mcad.build_model_lab()

# Change Operating Modes
mcad.set_variable("OperatingMode_Lab", 0)

# Set E-Magnetic Calculation Options
mcad.set_variable("EmagneticCalcType_Lab", 0)
mcad.set_variable("SpeedMax_MotorLAB", 10000)
mcad.set_variable("Speedinc_MotorLAB", 250)
mcad.set_variable("SpeedMin_MotorLAB", 500)
mcad.set_variable("Imax_MotorLAB", 480)

# Calculate E-Magnetic Performance
try:
    mcad.calculate_magnetic_lab()
    mcad.show_message("Magnetic calculation successfully completed")
except MotorCADError:
    mcad.show_message("Magnetic calculation failed")


# Retrieve results
data = scipy.io.loadmat(os.path.join(working_folder, mcad_name, "Lab", "MotorLAB_elecdata.mat"))
Speed = data["Speed"]
ShaftTorque = data["Shaft_Torque"]
ShaftPower = data["Shaft_Power"]

# Plot Graphs
plt.figure(1)
plt.subplot(211)
plt.plot(Speed, ShaftTorque)
plt.xlabel("Speed")
plt.ylabel("Shaft Torque")
plt.subplot(212)
plt.plot(Speed, ShaftPower)
plt.xlabel("Speed")
plt.ylabel("Shaft Power")
plt.show(block=False)
plt.savefig(os.apth.join(working_folder, "Maximum Torque VS Speed Curve.png"))

# Set Operating Point Calculation Options
mcad.set_variable("OpPointSpec_MotorLAB", 1)
mcad.set_variable("StatorCurrentDemand_Lab", 480)
mcad.set_variable("SpeedDemand_MotorLAB", 4000)
mcad.set_variable("LabThermalCoupling", 0)
mcad.set_variable("LabMagneticCoupling", 0)

# Calculate operating point
mcad.calculate_operating_point_lab()

# Retrieve results
OpPointShaftTorque = mcad.get_variable("LabOpPoint_ShaftTorque")
OpPointEfficiency = mcad.get_variable("LabOpPoint_Efficiency")
print("Operating Point Shaft Torque = ", OpPointShaftTorque)
print("Operating Point Efficiency = ", OpPointEfficiency)

# Finalisation
mcad.quit()
print("Simulation Complete")
