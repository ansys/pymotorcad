# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Motor-CAD EMag Twin Builder ECE
=============================
This example provides a Motor-CAD script for exporting
an equivalent circuit extraction (ECE) model for permanent
magnet synchronous motors (PMSMs) from Motor-CAD to Ansys
Twin Builder.
"""

# %%
# .. note::
#    This example requires the use of a JSON configuration file. The ``ece_config.json`` file should
#    be saved to the same directory as this example Python script. You can download the
#    ``ece_config.json`` file from:
#    https://github.com/ansys/pymotorcad/blob/main/examples/links/ece_config.json

# %%
#
# .. image:: ../../images/twinbuilder_ECE/EMag_TwinBuilder_ECE.png
#
# Set up example
# --------------
# Setting up this example consists of performing imports, launching
# Motor-CAD, disabling all popup messages from Motor-CAD, and
# importing the initial settings.

# %%
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Import the required packages.

# sphinx_gallery_thumbnail_path = 'images/twinbuilder_ECE/EMag_TwinBuilder_ECE_thumbnail_2.png'
import json
import math
import os
import shutil
import string
import tempfile

import matplotlib.pyplot as plt
import numpy as np
from scipy import io

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.links_methods import write_SML_file, write_text_file

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~
# Initialise automation and launch Motor-CAD.
print("Starting initialisation.")
mc = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~
# Disable all popup messages from Motor-CAD.
mc.set_variable("MessageDisplayState", 2)


# %%
# Import and save initial settings
# --------------------------------
# Define the ``read_parameters`` function to import initial settings from a JSON file and return a
# dictionary:
def read_parameters(json_file):
    """Read input parameters."""
    with open(json_file, "r") as f:
        param_dict = json.load(f)
    return param_dict


# %%
# Specify the working directory. The Motor-CAD file and results are saved to a temporary folder.
# Alternatively, you can set the working directory to an appropriate file location on your computer.
working_folder = os.path.join(tempfile.gettempdir(), "twinbuilder_ECE_export")
try:
    shutil.rmtree(working_folder)
except:
    pass
os.mkdir(working_folder)

# %%
# Use the ``read_parameters`` function to open the ``ece_config.json`` configuration file and import
# the data as the ``in_data`` dictionary.
#
# The JSON configuration file must be saved to the same directory as this Python script. The
# ``ece_config.json`` file can be downloaded from the PyMotorCAD GitHub repository:
# https://github.com/ansys/pymotorcad/blob/main/examples/links/ece_config.json

json_file = os.path.join(os.getcwd(), "ece_config.json")
in_data = read_parameters(json_file)

# %%
# The necessary data is extracted from the ``in_data`` dictionary. The JSON configuration file
# contains:
#
# * The Motor-CAD MOT filename to be used for the ECE export. If the file exists in the same
#   directory as this Python script, it will be copied to the ``working_folder`` location. If the
#   file does not exist in the same directory as this Python script or the ``working_folder``
#   location, the script opens the e8 Motor-CAD template by default.
#
# * Operating parameters for the electric machine (shaft speed, DC bus voltage, temperature, maximum
#   current, current resolution and number of points per cycle for the torque calculation). If using
#   an input file, the file in the ``working_folder`` will be modified by setting the operating
#   parameter input settings.
#
# * The filenames to be used for the results files that are exported (map, text file and SML file).
#   Exported files are saved to the working directory, in a subfolder named ``Results``.

file_name = in_data["mot_file"]
mot_file = os.path.join(working_folder, file_name)

shaft_speed = in_data["shaft_speed"]
dc_bus_voltage = float(in_data["dc_bus_voltage"])
machine_temp = float(in_data["machine_temp"])
Id_max = float(in_data["Id_max"])
current_step = float(in_data["current_step"])
points_per_cycle = float(in_data["torque_points_per_cycle"])

results_folder = os.path.join(working_folder, "Results")
try:
    shutil.rmtree(results_folder)
except:
    pass
os.mkdir(results_folder)
map_name = os.path.join(results_folder, in_data["map_name"])
txt_file = os.path.join(results_folder, in_data["txt_file"])
sml_file = os.path.join(results_folder, in_data["sml_file"])

# %%
# Load the Motor-CAD file. If the ``mot_file`` specified in the JSON configuration file exists in
# the same directory as this Python script, open the MOT file. If the file does not exist in the
# same directory as this Python script, check the ``working_folder`` for the Motor-CAD file. The
# file will be modified by setting the operating parameter input settings and saved to the
# ``working_folder``.
#
# If the file does not exist in the same directory as this Python script or the ``working_folder``,
# load the e8 IPM motor template and save the file to the working directory. Use the ``mot_file``
# filename that was taken from the JSON configuration file. Save input settings to a Motor-CAD MOT
# file.
if os.path.isfile(os.path.join(os.getcwd(), file_name)):
    shutil.copy(os.path.join(os.getcwd(), file_name), mot_file)
    print(f"Motor-CAD file copied from {os.path.join(os.getcwd(), file_name)} to {mot_file}.")
    mc.load_from_file(mot_file)
    print("Opening " + mot_file)
elif os.path.isfile(mot_file):
    mc.load_from_file(mot_file)
    print("Opening " + mot_file)
else:
    mc.load_template("e8")
    mc.save_to_file(mot_file)
    print("Opening Motor-CAD e8 template and saving to " + mot_file)

# %%
# Determine alignment angle
# -------------------------
# Set up calculation
# ~~~~~~~~~~~~~~~~~~
# Set up the Motor-CAD E-Magnetic calculation to run the open circuit back EMF calculation, so that
# the drive offset angle can be determined. Define the calculation settings as taken from the JSON
# configuration file.
#
# * Set the number of points per cycle for the torque calculation in Motor-CAD.
mc.set_variable("TorquePointsPerCycle", points_per_cycle)

# %%
# * Set the shaft speed for the calculation.
mc.set_variable("ShaftSpeed", shaft_speed)

# %%
# * Set the **Line Current Definition** option to **Peak** and set the peak current to zero.
mc.set_variable("CurrentDefinition", 0)
mc.set_variable("PeakCurrent", 0)

# %%
# * Set the DC bus voltage.
mc.set_variable("DCBusVoltage", dc_bus_voltage)

# %%
# * Set the armature winding, magnet and shaft temperatures.
mc.set_variable("ArmatureConductor_Temperature", machine_temp)
mc.set_variable("Magnet_Temperature", machine_temp)
mc.set_variable("Shaft_Temperature", machine_temp)

# %%
# * Set the **E-Magnetic <-> Thermal Coupling** option to **No Coupling**.
mc.set_variable("MagneticThermalCoupling", 0)

# %%
# * Select the **Back EMF** and deselect the **Cogging Torque** open circuit calculations. Deselect
#   the **On Load Torque** and **Torque Speed Curve** calculations.
mc.set_variable("BackEMFCalculation", True)
mc.set_variable("CoggingTorqueCalculation", False)
mc.set_variable("TorqueCalculation", False)
mc.set_variable("TorqueSpeedCalculation", False)

# %%
# Run simulation
# ~~~~~~~~~~~~~~
# Run the Motor-CAD E-Magnetic open circuit back EMF calculation and obtain the results.
#
# Save the Motor-CAD file with the updated calculation settings and run the E-Magnetic calculation.
# Use a ``try`` statement to print an error message if the calculation is not successful.
mc.save_to_file(mot_file)
try:
    mc.do_magnetic_calculation()
except pymotorcad.MotorCADError:
    print("Calculation failed.")

# %%
# Get the graph results for flux linkage versus angle (in electric degrees) for the A phase.
e_deg, flux_a = mc.get_magnetic_graph("FluxLinkageOCPh1")

# %%
# Plot results
# ~~~~~~~~~~~~
# Plot flux linkage in the A phase.
plt.figure(1)
plt.plot(e_deg, flux_a)
plt.xlabel("Position [EDeg]")
plt.ylabel("FluxLinkageA")
plt.title("A_Phase Flux Linkage")
plt.show()

# %%
# Calculate the alignment angle
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get the drive offset angle (the angle used to align the south pole axis of the rotor with the
# magnetic axis of the first phase).
drive_offset = mc.get_variable("DriveOffsetAngleLoad")
print("Drive Offset Angle = " + str(drive_offset) + " °")
# %%
# Calculate the alignment angle from the drive_offset offset angle.
alignment_angle = 90 + drive_offset

# %%
# This correlation can be confirmed by the open circuit calculation results: the negative peak of
# the flux linkage for the first phase is at 90 electric degrees, and the drive offset angle is 0.

# %%
# Calculate the number of rotor positions
# ---------------------------------------
# The number of rotor positions (or torque points per cycle) is calculated. The number of points
# is determined such that the look-up tables are generated starting from the alignment angle.
#
# Get the number of pole pairs, used to calculate the rotor positions.
p = mc.get_variable("Pole_Number") / 2

# %%
# Calculate the number of rotor positions based on the alignment angle and a specified angular
# interval (120 electric degrees). Only values for 120 electric degree intervals are used to
# generate the look-up tables. The minimum number of rotor positions is set to 30.
max_elec_degree = 120
fac = []
d = 2
n = alignment_angle
while n >= d:
    if n % d == 0:
        fac.append(d)
        n /= d
    else:
        d = d + 1
elec_deg = fac[len(fac) - 1]
i = 1
while (max_elec_degree / elec_deg) < 30:
    elec_deg = fac[len(fac) - 1 - i]
    i += 1
m_period = max_elec_degree / p
mec_deg = float(float(elec_deg) / float(p))
points_per_cycle = 360 / elec_deg

# %%
# Calculate the saturation map
# ----------------------------
# Use the **Saturation and Loss Map Export** tool in Motor-CAD to calculate and export the
# saturation map.
#
# Set up calculation
# ~~~~~~~~~~~~~~~~~~
# Get the phase resistance and end winding inductance output parameter values from Motor-CAD. These
# will be used when generating the TXT and SML files for the ECE export.
phase_res = mc.get_variable("ArmatureWindingResistancePh")
phase_l = mc.get_variable("EndWdgInductance_Used")

# %%
# Define the Motor-CAD calculation settings:
#
# * Set the number of torque points per cycle (rotor positions)
mc.set_variable("TorquePointsPerCycle", points_per_cycle)
# %%
#  * Set the filename and path for the saturation map to be exported to
mc.set_variable("SaturationMap_ExportFile", map_name)
# %%
# * Set the calculation **Input Definition** to **D/Q Axis Currents**, **Calculation Method** to
#   **FEA Calculations**, **FEA Calculation Type** to **Full Cycle (default)** and **Results** to
#   **Varying with rotor position**.
mc.set_variable("SaturationMap_InputDefinition", 1)
mc.set_variable("SaturationMap_CalculationMethod", 1)
mc.set_variable("SaturationMap_FEACalculationType", 1)
mc.set_variable("SaturationMap_ResultType", 1)
# %%
# Do not export the loss map.
mc.set_variable("LossMap_Export", False)
# %%
# Set the **D Axis Current** and **Q Axis Current** parameters (maximum, step size and minimum).
mc.set_variable("SaturationMap_Current_D_Max", Id_max)
mc.set_variable("SaturationMap_Current_D_Step", current_step)
mc.set_variable("SaturationMap_Current_D_Min", -Id_max)
mc.set_variable("SaturationMap_Current_Q_Max", Id_max)
mc.set_variable("SaturationMap_Current_Q_Step", current_step)
mc.set_variable("SaturationMap_Current_Q_Min", -Id_max)

# %%
# Run simulation
# ~~~~~~~~~~~~~~
# Save the Motor-CAD file with the updated calculation settings and run the Motor-CAD E-Magnetic
# saturation map calculation. Use a ``try`` statement to print an error message if the calculation
# is not successful.
mc.save_to_file(mot_file)
try:
    mc.calculate_saturation_map()
except pymotorcad.MotorCADError:
    print("Map calculation failed.")

# %%
# Load the saturation map
# -----------------------
# Import the saturation map data that was calculated and exported from Motor-CAD as the
# ``mat_file_data`` dictionary.
mat_file_data = io.loadmat(map_name)

# %%
# Extract data from the ``mat_file_data`` dictionary:
#
# * The D and Q peak current.
#
# * The flux linkages for D and Q axes and the 3 phases.
#
# * The rotor position.
#
# * The electromagnetic torque.
#
# * The phase advance.
id_peak = mat_file_data["Id_Peak"]
iq_peak = mat_file_data["Iq_Peak"]
angular_flux_linkage_d = mat_file_data["Angular_Flux_Linkage_D"]
angular_flux_linkage_q = mat_file_data["Angular_Flux_Linkage_Q"]
angular_flux_linkage_1 = mat_file_data["Angular_Flux_Linkage_Phase_1"]
angular_flux_linkage_2 = mat_file_data["Angular_Flux_Linkage_Phase_2"]
angular_flux_linkage_3 = mat_file_data["Angular_Flux_Linkage_Phase_3"]
angular_rotor_position = mat_file_data["Angular_Rotor_Position"]
angular_electromagnetic_torque = mat_file_data["Angular_Electromagnetic_Torque"]
phase_advance = mat_file_data["Phase_Advance"]

# %%
# Generate the look-up table
# --------------------------
# For each input current combination and rotor position, the D and Q axis flux linkages, the
# homopolar component of the flux (approximated to zero) and the torque values are stored in the
# ``final_table`` numpy array (look-up table).

d_values = len(id_peak)
q_values = len(id_peak[0])
comb = d_values * q_values
map_points = int((max_elec_degree / elec_deg) + 1)
rot_pos = (max_elec_degree / p) + 1
ind = 0
index_1 = []
flux_d_2 = []
flux_q_3 = []
flux_0_4 = []
torque_5 = []
id_6 = []
iq_7 = []
phase_ad_8 = []
rotor_pos_9 = []
final_table = []
skip = math.ceil(alignment_angle / elec_deg)

for i in range(d_values):
    for j in range(q_values):
        for k in range(int(skip), int(skip - map_points), (-1)):
            ind = ind + 1
            if k < 0:
                kprimo = int(points_per_cycle + k)
                index_1.append(ind - 1)
                flux_d_2.append(angular_flux_linkage_d[i, j, kprimo])
                flux_q_3.append(angular_flux_linkage_q[i, j, kprimo])
                flux_0_4.append(0)
                torque_5.append(-angular_electromagnetic_torque[i, j, kprimo])
                id_6.append(id_peak[i, j])
                iq_7.append(iq_peak[i, j])
                phase_ad_8.append(phase_advance[i, j])
                rotor_pos_9.append(angular_rotor_position[i, j, kprimo])
            else:
                index_1.append(ind - 1)
                flux_d_2.append(angular_flux_linkage_d[i, j, k])
                flux_q_3.append(angular_flux_linkage_q[i, j, k])
                flux_0_4.append(0)
                torque_5.append(-angular_electromagnetic_torque[i, j, k])
                id_6.append(id_peak[i, j])
                iq_7.append(iq_peak[i, j])
                phase_ad_8.append(phase_advance[i, j])
                rotor_pos_9.append(angular_rotor_position[i, j, k])

final_table = np.array(
    [index_1, flux_d_2, flux_q_3, flux_0_4, torque_5, id_6, iq_7, phase_ad_8, rotor_pos_9]
)

# %%
# Plot results
# ------------
# Plot the D-Q flux.
plt.figure(2)
plt.plot(index_1, flux_d_2, "r", index_1, flux_q_3, "b", linewidth=1.0)
plt.xlabel("Points")
plt.ylabel("Flux [Vs]")
plt.legend(["Psid", "Psiq"], loc="lower right")
plt.title("D-Q Flux")
plt.show()

# %%
# Plot the torque.
plt.figure(3)
plt.plot(index_1, torque_5, "r", linewidth=2.0)
plt.ylabel("Torque [Nm]")
plt.xlabel("Points")
plt.title("Torque")
plt.show()

# %%
# Plot D-flux linkages versus the q-axis current.
plt.figure(3)
for i in range(d_values):
    plt.plot(
        iq_peak[0, :], angular_flux_linkage_q[i, :, skip], label="Id=" + str(id_peak[i, 0]) + "A"
    )
plt.ylabel("Flux [Vs]")
plt.xlabel("Iq [A]")
plt.legend(fontsize=8, loc="lower right")
plt.title("D-Flux vs Iq")
plt.show()

# %%
# Plot Q-flux linkages versus the q-axis current.
plt.figure(4)
for i in range(d_values):
    plt.plot(
        iq_peak[0, :], angular_flux_linkage_d[:, i, skip], label="Id=" + str(id_peak[i, 0]) + "A"
    )
plt.legend(fontsize=8, loc="lower right")
plt.ylabel("Flux [Vs]")
plt.xlabel("Iq [A]")
plt.title("Q-Flux vs Iq")
plt.show()

# %%
# Write TXT and SML files
# -----------------------
# To create the ECE model in Ansys Twin Builder, a SML file is generated from the exported Motor-CAD
# data. A TXT file is also generated.
#
# Write the TXT text
# ~~~~~~~~~~~~~~~~~~
# Generate the TXT file, using the path and filename that was taken from the ``ece_config.json``
# configuration file. The TXT file is generated using the ``write_text_file`` method from the
# ``ansys.motorcad.core.links_methods`` unit.

write_text_file(txt_file, final_table, p, phase_res, phase_l, id_peak, iq_peak, map_points, mec_deg)

# %%
# Write the SML file
# ~~~~~~~~~~~~~~~~~~
# Generate the SML that will be loaded into Ansys Twin Builder to generate the ECE model. The SML
# file uses the phase resistance and end winding inductance and data from the look-up table. The
# SML file is saved using the path and filename taken from the ``ece_config.json`` configuration
# file. The SML file is generated using the ``write_SML_file`` method from the
# ``ansys.motorcad.core.links_methods`` unit.

mot_name = mot_file.replace(".mot", "")
mot_name = "".join(i for i in mot_file if i in string.ascii_letters + "0123456789")
write_SML_file(
    sml_file, mot_name, final_table, p, phase_res, phase_l, id_peak, iq_peak, map_points, mec_deg
)
# %%
# Generating the ECE component
# ----------------------------
# To generate the component, within Ansys Electronics Desktop, go to the menu bar and select
# **Tools -> Project Tools -> Import Twin Builder Models**. Select the SML file and click **Open**.
# Click **OK** in the **Import Components** window.
#
# .. image:: ../../images/twinbuilder_ECE/twinbuilder_procedure_1.png
# %%
# A new project component **ECE_e8_eMobility** is added to
# **Component Libraries / Project Components**. Drag the ECE component into the
# **Schematic Capture** window.
#
# .. image:: ../../images/twinbuilder_ECE/twinbuilder_procedure_2.png
# %%
# Right-click on the ECE component and select **Edit Symbol -> Edit Pin Locations...** to open the
# **Pin Location Editor** window. Rearrange the pins such that **A0**, **B0**, **C0** and **ROT2**
# are on the left and **X0**, **Y0**, **Z0** and **ROT1** are on the right. Click **OK** to close
# the window.
#
# .. image:: ../../images/twinbuilder_ECE/twinbuilder_procedure_3.png
# %%
# To open the **Parameters** tab, double-click on the ECE component. The phase resistance (**ra0**)
# (at the armature conductor temperature) and armature end winding inductance (**la0**) imported
# from the Motor-CAD model.
#
# .. image:: ../../images/twinbuilder_ECE/twinbuilder_procedure_4.png

# %%
# For more information on using the ECE component in Twin Builder, see the tutorial supplied with
# Motor-CAD (**TwinBuilder_ECE_Tutorial**).
