"""Example Motor-CAD scripting."""
# Install Relevant Packages
# Retain pyqt4 compatibility
import os

import matplotlib.pyplot as plt
import scipy

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
mcad.save_to_file(os.path.join(working_folder, mcad_name, ".mot"))

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
except pymotorcad.MotorCADError:
    mcad.show_message("Magnetic calculation failed")


# Retrieve results
data = scipy.io.loadmat(os.path.join(working_folder, mcad_name, "Lab", "MotorLAB_elecdata.mat"))
speed = data["Speed"]
shaft_torque = data["Shaft_Torque"]
shaft_power = data["Shaft_Power"]

# Plot Graphs
plt.figure(1)
plt.subplot(211)
plt.plot(speed, shaft_torque)
plt.xlabel("Speed")
plt.ylabel("Shaft Torque")
plt.subplot(212)
plt.plot(speed, shaft_power)
plt.xlabel("Speed")
plt.ylabel("Shaft Power")
plt.show(block=False)
plt.savefig(os.path.join(working_folder, "Maximum Torque VS Speed Curve.png"))

# Set Operating Point Calculation Options
mcad.set_variable("OpPointSpec_MotorLAB", 1)
mcad.set_variable("StatorCurrentDemand_Lab", 480)
mcad.set_variable("SpeedDemand_MotorLAB", 4000)
mcad.set_variable("LabThermalCoupling", 0)
mcad.set_variable("LabMagneticCoupling", 0)

# Calculate operating point
mcad.calculate_operating_point_lab()

# Retrieve results
op_point_shaft_torque = mcad.get_variable("LabOpPoint_ShaftTorque")
op_point_efficiency = mcad.get_variable("LabOpPoint_Efficiency")
print("Operating Point Shaft Torque = ", op_point_shaft_torque)
print("Operating Point Efficiency = ", op_point_efficiency)

# Finalisation
mcad.quit()
print("Simulation Complete")
