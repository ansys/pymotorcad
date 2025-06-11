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

"""Unit containing functions for exporting an ECE to Twin Builder using Motor-CAD results."""


def write_text_file(
    file_name, data_table, pole_pairs, phase_res, phase_l, id_peak, iq_peak, map_points, mec_deg
):
    """Write data to a text file for Motor-CAD ECE export to Twin Builder.

    Parameters
    ----------
    file_name : string
        File location for the text file to be saved to.
    data_table : numpy array
        Look-up table of Motor-CAD results with the following columns:
        index : list of int
            Index of points.
        flux_d : list of float
            D-axis flux values.
        flux_q : list of float
            Q-axis flux values.
        flux_0 : list of float
            Zeros (?).
        torque : list of float
            Torque values.
    pole_pairs : int
        Number of pole pairs.
    phase_res : float
        Phase resistance.
    phase_l : float
        Phase inductance.
    id_peak : list of float
        D-axis current peak values.
    iq_peak : list of float
        Q-axis current peak values.
    map_points : int
        Number of saturation map points.
    mec_deg : float
        Angular interval between saturation map points in mechanical degrees.
    """
    rows = len(data_table[0])

    file_id = open(file_name, "w")

    # %%
    # Write the number of poles to the TXT file.
    file_id.write("B_BasicData\r\n")
    file_id.write("\tVersion\t1.2\r\n")
    file_id.write(f"\tPoles\t{pole_pairs * 2:.0f}\r\n")
    _ = file_id.write("E_BasicData\r\n\n")

    # %%
    # Write the phase resistance and end winding inductances for each phase to the TXT file.
    file_id.write("B_PhaseImp 3\r\n")
    file_id.write(f"\tWG_Ph1\t{phase_res:.10e}\t{phase_l:.10e}\r\n")
    file_id.write(f"\tWG_Ph2\t{phase_res:.10e}\t{phase_l:.10e}\r\n")
    file_id.write(f"\tWG_Ph3\t{phase_res:.10e}\t{phase_l:.10e}\r\n")
    _ = file_id.write("E_PhaseImp\r\n\n")

    # %%
    # Write the D and Q axis current values to the TXT file.
    file_id.write("B_Sweepings\r\n\n")
    file_id.write(f"\tId_Iq\t( {len(id_peak)} :")
    for i in range(len(id_peak)):
        file_id.write(f"\t{id_peak[i, 0]}")
    file_id.write(")\n")

    file_id.write(f"\t\t( {len(id_peak[0])} :")
    for i in range(len(id_peak[0])):
        file_id.write(f"\t{iq_peak[0, i]}")
    _ = file_id.write(")\n")

    # %%
    # Write the rotor positions to the TXT file.
    file_id.write(f"\tRotate\t( {map_points} :")

    for i in range(map_points):
        file_id.write(f"\t{i * mec_deg:.3f}")
    file_id.write(")\n")
    _ = file_id.write("E_Sweepings\n\n")

    # %%
    # Write the D and Q axis flux and torque values and then close the TXT file.
    file_id.write("B_OutputMatrix DQ0\n")

    for i in range(rows):
        file_id.write(
            f"\t{data_table[0][i]}\t{data_table[1][i]:.10e}\t{data_table[2][i]:.10e}"
            f"\t{data_table[3][i]:.10e}"
            f"\t{data_table[4][i]:.10e}\r\n"
        )
    file_id.write("E_OutputMatrix\n")

    file_id.close()
