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
.. _ref_sync_potier_diagram:

SYNC Short circuit current and Vacuum curve Potier diagram.
===========================================================
This example script allows a correct short-circuit calculation such that:
the input current used to get DQ axis parameters is equal to the short circuit current.
Recommended to be used with SYNC generators.
User has to provide input values for DC field current, relaxation (damping) factor and tolerance.
The script also calculates the Vacuum curve (Open circuit Back-EMF) and plots both of them to create
the Potier diagram.
The script also searches for the optimal field current for a certain generator operating point.
"""
# %%
# Perform required imports
# ------------------------
import csv
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
# ----------------
mc = pymotorcad.MotorCAD()

# %%
# Setup calculation
# -----------------
# We will define the working and results directory and make sure the results directory exists
full_path = mc.get_file_name()
path = Path(full_path)
working_dir = path.parent
mot_name = path.stem

results_dir = working_dir / mot_name / "results"    # Define results directory
results_dir.mkdir(parents=True, exist_ok=True)  # Ensure "results" directory exists

# %%
# We will define the inputs for the calculation of the short circuit and vacuum curve:
# Rated voltage (Vrms), Rated (VA), Power Factor (-), DC current array (A), and relaxation factor
# as well as the settings for the optimal field current search function:
# tolerance, max_iter, and current_step.
rated_voltage = 6800    # Rated voltage (Vrms)
rated_VA = 416000   # Rated apparent power (VA)
rated_pf = 0.9  # Rated power factor (-)
rated_power = rated_VA * rated_pf   # Rated power (W)
rated_current = rated_power / (np.sqrt(3 / 2) * rated_voltage * rated_pf)  # peak value
r_load = rated_power / (3 / 2) / (np.power(rated_current, 2))  # AC load resistance
load_impedance = r_load / rated_pf  # AC load impedance
x_load = np.sqrt(np.power(load_impedance, 2) - np.power(r_load, 2))  # AC load reactance

dc_current = [10, 20, 40, 50, 80, 100, 150] # DC current array that will be used to calculate the short circuit currents and open circuit voltage
relaxation_factor = 0.2 # relaxation factor used in the calculation of the short circuit current
tolerance = 0.01 # Tolerance used to find optimal field current for a certain rated voltage in (=1%)
max_iter = 200  # Maximum number of iteration possible in the optimal field current search function
current_step = 1 # Current step used in the optimal field current search function (A)

# %%
# Optimal field current search function
# -------------------------------------
# We will define a function to find the optimal field current for a certain operating point
def find_field_current_simple(
    mc, rated_voltage, if0, ifk, step=current_step, tol=tolerance, max_iter=max_iter
):
    """
    Search function.

    Adjust DC field current in steps until terminal voltage matches rated voltage within tolerance.
    """
    i_f = if0 + ifk
    # Set passive generator conditions
    mc.set_variable("DriveType_BPM", 1)  # calculated currents
    mc.set_variable("BPMDriveMode", 3)  # passive generator
    mc.set_variable("TorqueCalculation", True)
    mc.set_variable("BackEMFCalculation", True)
    mc.set_variable("InductanceCalc", True)
    mc.set_variable("PassiveGeneratorLoadType", 1)  # AC Load
    mc.set_variable("ACLoadResistance", r_load)
    speed = mc.get_variable("ShaftSpeed")
    poles = mc.get_variable("RotorSlots")
    frequency = speed * poles / 120
    l_load = x_load / (2 * frequency * np.pi)
    mc.set_variable("ACLoadInductance", l_load)

    mc.set_variable("CoggingTorqueCalculation", False)
    mc.set_variable("TorqueSpeedCalculation", False)
    mc.set_variable("OnLoadLossCalculation", False)

    mc.set_variable("ElectromagneticForcesCalc_OC", False)
    mc.set_variable("ElectromagneticForcesCalc_Load", False)

    for _ in range(max_iter):
        mc.set_variable("DCFieldCurrent", float(i_f))

        mc.do_magnetic_calculation()
        Vt = float(mc.get_variable("RmsLineLineVoltage"))

        error = (Vt - rated_voltage) / rated_voltage
        if abs(error) <= tol:
            return i_f, Vt

        # Adjust up or down by fixed step
        if Vt < rated_voltage:
            i_f += step
        else:
            i_f -= step

        i_f = max(i_f, 10)  # keep non-negative

    raise RuntimeError(f"Failed to converge: last i_f={i_f:.1f} A, Vt={Vt:.1f} V")

# %%
# Main function
# -------------
# This function is called when "Run" is pressed
def main():
    """Call when Run is pressed."""
    mc.set_variable("MessageDisplayState", 2)
    mc.set_variable("CurrentDefinition", 0)

    short_circuit_currents = []
    back_emf_voltages = []

    # Short circuit calculation
    for DCC in dc_current:
        mc.set_variable("DCFieldCurrent", DCC)
        mc.set_variable("PhaseAdvance", 90)
        # Reduce calculations for fast execution
        mc.set_variable("TorqueCalculation", False)
        mc.set_variable("BackEMFCalculation", False)
        mc.set_variable("CoggingTorqueCalculation", False)
        mc.set_variable("TorqueSpeedCalculation", False)
        mc.set_variable("OnLoadLossCalculation", False)
        mc.set_variable("InductanceCalc", False)

        mc.set_variable("ElectromagneticForcesCalc_OC", False)
        mc.set_variable("ElectromagneticForcesCalc_Load", False)

        while True:
            peakCurrent = mc.get_variable("PeakCurrent")

            mc.do_magnetic_calculation()
            shortCircuitCurrent = mc.get_variable("ShortCircuitLineCurrent")
            shortCircuitCurrent = np.round(shortCircuitCurrent, 3)
            print(f"DC Current = {DCC} A, Short Circuit Current = {shortCircuitCurrent} A")

            if abs(peakCurrent - shortCircuitCurrent) / peakCurrent < tolerance:
                print("Calculated Short Circuit Current = " + str(shortCircuitCurrent))
                short_circuit_currents.append(shortCircuitCurrent)
                break
            else:
                new_peak_current = (
                    1 - relaxation_factor
                ) * peakCurrent + relaxation_factor * shortCircuitCurrent
                mc.set_variable("PeakCurrent", new_peak_current)

    # Open circuit Back-EMF calculation
    for DCC in dc_current:
        mc.set_variable("DCFieldCurrent", DCC)
        mc.set_variable("PhaseAdvance", 0)
        # Reduce calculations for fast execution
        mc.set_variable("TorqueCalculation", False)
        mc.set_variable("BackEMFCalculation", True)  # Enable just EMF calculation
        mc.set_variable("CoggingTorqueCalculation", False)
        mc.set_variable("TorqueSpeedCalculation", False)
        mc.set_variable("OnLoadLossCalculation", False)
        mc.set_variable("InductanceCalc", False)

        mc.set_variable("ElectromagneticForcesCalc_OC", False)
        mc.set_variable("ElectromagneticForcesCalc_Load", False)
        mc.do_magnetic_calculation()
        backEMF = mc.get_variable("RMSBackEMFLine")
        backEMF = np.round(backEMF, 3)
        print(f"DC Current = {DCC} A, Back EMF Voltage = {backEMF} V")
        back_emf_voltages.append(backEMF)

    mc.set_variable("MessageDisplayState", 0)

    # --- Per-unit conversion ---
    scc_pu = [val / rated_current for val in short_circuit_currents]
    emf_pu = [val / rated_voltage for val in back_emf_voltages]

    # --- Interpolation helper ---
    def interp_field_at_pu(x_vals, y_vals, target=1.0):
        return np.interp(target, y_vals, x_vals)  # linear interpolation

    if0 = interp_field_at_pu(dc_current, emf_pu, 1.0)  # field current at 1 p.u. EMF
    ifk = interp_field_at_pu(dc_current, scc_pu, 1.0)  # field current at 1 p.u. SCC
    Kc = if0 / ifk

    print(f"Rated Voltage = {rated_voltage} V, Rated Current = {rated_current} A")
    print(f"if0 = {if0:.2f} A, ifk = {ifk:.2f} A, Kc = {Kc:.3f}")

    # --- Write merged results into single CSV ---
    csv_path = os.path.join(results_dir, "SCC_EMF_perunit_results.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["DC Field Current (A)", "SCC (A)", "EMF (V)", "SCC (p.u.)", "EMF (p.u.)"])
        for DCC, scc, emf, sccpu, emfpu in zip(
            dc_current, short_circuit_currents, back_emf_voltages, scc_pu, emf_pu
        ):
            writer.writerow([DCC, scc, emf, sccpu, emfpu])

        # Append summary at bottom
        writer.writerow([])
        writer.writerow(["Rated Voltage (V)", rated_voltage])
        writer.writerow(["Rated Current (A)", rated_current])
        writer.writerow(["if0 (A)", if0])
        writer.writerow(["ifk (A)", ifk])
        writer.writerow(["Kc", Kc])

    print(f"All results saved to '{csv_path}'.")

    # --- Find optimal field current for rated terminal voltage ---
    i_opt, Vt_opt = find_field_current_simple(
        mc, rated_voltage, if0, ifk, step=current_step, tol=tolerance
    )
    print(f"Optimal DC field current = {i_opt:.1f} A, Terminal Voltage = {Vt_opt:.1f} V")

    # Append to CSV
    with open(csv_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([])
        writer.writerow(["Optimal DC Field Current (A)", i_opt])
        writer.writerow(["Terminal Voltage at Opt (V)", Vt_opt])
        writer.writerow(["Error (%)", 100.0 * (Vt_opt - rated_voltage) / rated_voltage])

    # Plot per-unit curves with markers at i_f0 and i_fk
    plt.figure(figsize=(8, 5))
    plt.plot(dc_current, emf_pu, "r--x", label="EMF (p.u.)")
    plt.plot(dc_current, scc_pu, "b-o", label="SCC (p.u.)")

    # Mark interpolation points
    plt.axhline(1.0, color="gray", linestyle="--")
    # Markers for if0 and ifk
    plt.axvline(if0, color="r", linestyle=":", label=f"if0 = {if0:.1f} A")
    plt.axvline(ifk, color="b", linestyle=":", label=f"ifk = {ifk:.1f} A")

    # Marker for i_opt
    plt.plot(i_opt, Vt_opt / rated_voltage, "g*", markersize=14, label=f"i_opt = {i_opt:.1f} A")

    plt.title("Per-Unit SCC & EMF vs DC Field Current")
    plt.xlabel("DC Field Current (A)")
    plt.ylabel("Per Unit Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(os.path.join(results_dir, "SCC_EMF_perunit_Kc_iopt_plot.png"))
    plt.show()


if __name__ == "__main__":
    main()
