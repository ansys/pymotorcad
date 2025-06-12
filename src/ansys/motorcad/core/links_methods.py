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
    txt_file, data_table, pole_pairs, phase_res, phase_l, id_peak, iq_peak, map_points, mec_deg
):
    """Write data to a text file for Motor-CAD ECE export to Twin Builder.

    Parameters
    ----------
    txt_file : string
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

    file_id = open(txt_file, "w")

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


def write_SML_file(
    sml_file,
    mot_name,
    data_table,
    pole_pairs,
    phase_res,
    phase_l,
    id_peak,
    iq_peak,
    map_points,
    mec_deg,
):
    """Write data to an SML file for Motor-CAD ECE export to Twin Builder.

    Parameters
    ----------
    sml_file : string
        File location for the SML file to be saved to.
    mot_name : string
        Name of the MOT file from which the ECE model is exported. Should be string.ascii_letters
        or numbers only.
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
    file_id = open(sml_file, "w")
    file_id.write(f"MODELDEF ECE_{mot_name}\r\n")
    file_id.write("{\r\n")
    file_id.write("PORT electrical: A0;\r\n")
    file_id.write("PORT electrical: X0;\r\n")
    file_id.write("PORT electrical: B0;\r\n")
    file_id.write("PORT electrical: Y0;\r\n")
    file_id.write("PORT electrical: C0;\r\n")
    file_id.write("PORT electrical: Z0;\r\n")
    file_id.write("PORT ROTATIONAL_V: ROT1;\r\n")
    file_id.write("PORT ROTATIONAL_V: ROT2;\r\n")

    file_id.write(f"PORT REAL IN: ra0 = {phase_res:.3f};\r\n")
    file_id.write(f"PORT REAL IN: la0 = {phase_l:.0e};\r\n")
    file_id.write("PORT REAL IN: IniIa0 = 0;\r\n")
    file_id.write("PORT REAL IN: IniIb0 = 0;\r\n")
    file_id.write("PORT REAL IN: IniIc0 = 0;\r\n")
    file_id.write("PORT REAL OUT: Fluxa0 = AM_Fluxa0.I;\r\n")
    file_id.write("PORT REAL OUT: Fluxb0 = AM_Fluxb0.I;\r\n")
    file_id.write("PORT REAL OUT: Fluxc0 = AM_Fluxc0.I;\r\n")
    file_id.write("PORT REAL OUT: Fluxd0 = AMFd.I;\r\n")
    file_id.write("PORT REAL OUT: Fluxq0 = AMFq.I;\r\n")

    file_id.write("PORT REAL IN ANGLE[deg]: IniPos = 0;\r\n")
    file_id.write("PORT REAL OUT ANGLE[deg]: Pos = VM_Mdeg.V;\r\n\n")

    file_id.write("INTERN  R        Ra0  N1:=A0, N2:=N_1  ( R:=ra0 );\r\n")
    file_id.write("INTERN  L        La0  N1:=N_1, N2:=N_2  ( L:=la0, I0:=IniIa0 );\r\n")
    file_id.write("INTERN  AM       AMa0  N1:=N_2, N2:=N_3  ;\r\n")
    file_id.write("INTERN  EV       Ema0  N1:=N_3, N2:=X0  ( QUANT:=VMa0.V, FACT:=-1 ); \r\n")
    file_id.write("INTERN  L        Lma0  N1:=N_4, N2:=GND  ( L:=1 ); \r\n")
    file_id.write("INTERN  VM       VMa0  N1:=N_4, N2:=GND  ; \r\n")
    file_id.write("INTERN  AM       AM_Fluxa0  N1:=N_5, N2:=N_4  ; \r\n")
    file_id.write(
        "INTERN  II       Fluxad  N1:=GND, N2:=N_5  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V) ); \r\n"
    )
    file_id.write(
        "INTERN  II       Fluxaq  N1:=GND, N2:=N_5  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V) ); \r\n"
    )
    file_id.write("INTERN  II       Fluxao  N1:=GND, N2:=N_5  ( QUANT:=AMFo.I, FACT:=1 ); \r\n")
    file_id.write("INTERN  II       Fluxa0  N1:=GND, N2:=N_5  ( QUANT:=AMo.I, FACT:=0 ); \r\n\n")

    file_id.write("INTERN  R        Rb0  N1:=B0, N2:=N_6  ( R:=ra0 ); \r\n")
    file_id.write("INTERN  L        Lb0  N1:=N_6, N2:=N_7  ( L:=la0, I0:=IniIb0 );\r\n")
    file_id.write("INTERN  AM       AMb0  N1:=N_7, N2:=N_8  ; \r\n")
    file_id.write("INTERN  EV       Emb0  N1:=N_8, N2:=Y0  ( QUANT:=VMb0.V, FACT:=-1 );  \r\n")
    file_id.write("INTERN  L        Lmb0  N1:=N_9, N2:=GND  ( L:=1 ); \r\n")
    file_id.write("INTERN  VM       VMb0  N1:=N_9, N2:=GND  ; \r\n")
    file_id.write("INTERN  AM       AM_Fluxb0  N1:=N_10, N2:=N_9  ; \r\n")
    file_id.write(
        "INTERN  II       Fluxbd  N1:=GND, N2:=N_10  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V-2*PI/3)"
        " );"
        "\r\n"
    )
    file_id.write(
        "INTERN  II       Fluxbq  N1:=GND, N2:=N_10  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V-2*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write("INTERN  II       Fluxbo  N1:=GND, N2:=N_10" "  ( QUANT:=AMFo.I, FACT:=1 ); \r\n")
    file_id.write(
        "INTERN  II       Fluxb0  N1:=GND, N2:=N_10" "  ( QUANT:=AMo.I, FACT:=0 ); \r\n\n"
    )

    file_id.write("INTERN  R        Rc0  N1:=C0, N2:=N_11  " "( R:=ra0 ); \r\n")
    file_id.write("INTERN  L        Lc0  N1:=N_11, N2:=N_12" "  ( L:=la0, I0:=IniIc0 ); \r\n")
    file_id.write("INTERN  AM       AMc0  N1:=N_12, N2:=N_13" "  ;  \r\n")
    file_id.write("INTERN  EV       Emc0  N1:=N_13, N2:=Z0" "  ( QUANT:=VMc0.V, FACT:=-1 ); \r\n")
    file_id.write("INTERN  L        Lmc0  N1:=N_14, N2:=GND" "  ( L:=1 ); \r\n")
    file_id.write("INTERN  VM       VMc0  N1:=N_14, N2:=GND" "  ;\r\n")
    file_id.write("INTERN  AM       AM_Fluxc0  N1:=N_15," " N2:=N_14  ;\r\n")
    file_id.write(
        "INTERN  II       Fluxcd  N1:=GND, N2:=N_15  ( QUANT:=AMFd.I, FACT:=cos(VM_Erad.V-4*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write(
        "INTERN  II       Fluxcq  N1:=GND, N2:=N_15  ( QUANT:=AMFq.I, FACT:=sin(VM_Erad.V-4*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write("INTERN  II       Fluxco  N1:=GND," " N2:=N_15  ( QUANT:=AMFo.I, FACT:=1 ); \r\n")
    file_id.write("INTERN  II       Fluxc0  N1:=GND," " N2:=N_15  ( QUANT:=AMo.I, FACT:=0 );\r\n\n")

    file_id.write("INTERN  AM" "       AMFd  N1:=N_16, N2:=GND  ; \r\n")
    file_id.write("INTERN" "  AM       AMFq  N1:=N_17, N2:=GND  ;\r\n")
    file_id.write("INTERN" "  AM       AMFo  N1:=N_18, N2:=GND  ; \r\n\n")

    file_id.write(
        "INTERN  II       Id0  N1:=GND, N2:=N_19  ( QUANT:=AMa0.I, FACT:=2/3*cos(VM_Erad.V) ); \r\n"
    )
    file_id.write(
        "INTERN  II       Id1  N1:=GND, N2:=N_19  ( QUANT:=AMb0.I, FACT:=2/3*cos(VM_Erad.V-2*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write(
        "INTERN  II       Id2  N1:=GND, N2:=N_19  ( QUANT:=AMc0.I, FACT:=2/3*cos(VM_Erad.V-4*PI/3)"
        " );"
        "\r\n"
    )
    file_id.write("INTERN  AM       AM0  N1:=N_19," " N2:=GND  ;\r\n")
    file_id.write(
        "INTERN  II       Iq0  N1:=GND, N2:=N_20"
        "  ( QUANT:=AMa0.I, FACT:=2/3*sin(VM_Erad.V) ); "
        "\r\n"
    )
    file_id.write(
        "INTERN  II       Iq1  N1:=GND, N2:=N_20  ( QUANT:=AMb0.I, FACT:=2/3*sin(VM_Erad.V-2*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write(
        "INTERN  II       Iq2  N1:=GND, N2:=N_20  ( QUANT:=AMc0.I, FACT:=2/3*sin(VM_Erad.V-4*PI/3)"
        " ); "
        "\r\n"
    )
    file_id.write("INTERN  AM       AM1  N1:=N_20," " N2:=GND  ; \r\n")
    file_id.write("INTERN  II       I00  N1:=GND," " N2:=N_21  ( QUANT:=AMa0.I, FACT:=1/3 ); \r\n")
    file_id.write("INTERN  II       I01  N1:=GND," " N2:=N_21  ( QUANT:=AMb0.I, FACT:=1/3 ); \r\n")
    file_id.write("INTERN  II       I02  N1:=GND," " N2:=N_21  ( QUANT:=AMc0.I, FACT:=1/3 ); \r\n")
    file_id.write("INTERN  " "AM       AMo  N1:=N_21, N2:=GND  ; \r\n\n")

    file_id.write("INTERN  " "VM       VM_Speed  N1:=N_23, N2:=N_22  ; \r\n")
    file_id.write(
        "UMODEL  D2D      "
        'D2D1 N1:=N_23, N2:=ROT1 ( NATURE_1:="electrical",'
        ' NATURE_2:="Rotational_V" ) SRC: DLL( File:="Domains.dll");\r\n'
    )
    file_id.write(
        "UMODEL  D2D      "
        'D2D2 N1:=N_22, N2:=ROT2 ( NATURE_1:="electrical",'
        ' NATURE_2:="Rotational_V" ) SRC: DLL( File:="Domains.dll");\r\n'
    )
    file_id.write(
        "INTERN  IV       " "Gx  N1:=GND," " N2:=N_24  ( QUANT:=VM_Speed.V, FACT:=57.29578 ); \r\n"
    )
    file_id.write("INTERN  C" "        " "Cx  N1:=N_24, N2:=GND  ( C:=1, V0:=IniPos ); \r\n")
    file_id.write("INTERN  VM" "" "       VM_Mdeg  N1:=N_24, N2:=GND  ; \r\n")
    file_id.write(
        "INTERN  IV" "" "       Ipos  N1:=GND, N2:=N_25  ( QUANT:=VM_Mdeg.V, FACT:=1 ); \r\n"
    )
    file_id.write("INTERN  AM" "" "       AM2  N1:=N_25, N2:=N_26  ; \r\n")
    file_id.write(
        f"INTERN  R        Rpos  N1:=N_26, N2:=GND  " f"( R:={0.0174533 * pole_pairs:.7f} ); \r\n"
    )
    file_id.write("INTERN  VM" "" "       VM_Erad  N1:=N_26, N2:=GND  ;\r\n\n")

    file_id.write(
        f"INTERN  NDSRC    PECE_{mot_name}  N0:=GND,"
        " N1:=N_16, N2:=GND, N3:=N_17,"
        " N4:=GND, N5:=N_18, N6:=N_22, N7:=N_23 \ \r\n"
    )
    file_id.write(
        " ( QUANT:={ AM0.I, AM1.I, AM2.I }," ' SRC:={ isrc, isrc, isrc, isrc }, TableData:="\ \r\n'
    )
    file_id.write(f".MODEL ECE_{mot_name}_table pwl TABLE=(")
    file_id.write(f" {len(id_peak)},")

    index = 0

    for i in range(len(id_peak)):
        file_id.write(f" {id_peak[i, 0]}")
        file_id.write(",")
        if i == (len(id_peak) - 1):
            file_id.write("\ \n")
            file_id.write(" 0,")

    for r in range(len(id_peak)):
        file_id.write(f" {len(id_peak[0])},")
        for i in range(len(id_peak[0])):
            file_id.write(f" {iq_peak[0, i]}")
            file_id.write(",")
            if i == (len(id_peak[0]) - 1):
                file_id.write("\ \n")
                file_id.write(" 0,")

        for k in range(len(id_peak[0])):
            file_id.write(f" {map_points},")
            for i in range(map_points):
                file_id.write(f" {i * mec_deg:.3f}")
                file_id.write(",")
                if i == (map_points - 1):
                    file_id.write("\ \n")
                    file_id.write(" 4,")

            for j in range(1, 5):
                for i in range(map_points):
                    file_id.write(f" {data_table[int(j), int(index + i)]:.6f}")
                    file_id.write(",")
                    if (
                        r == (len(id_peak) - 1)
                        and k == (len(id_peak[0]) - 1)
                        and j == 4
                        and i == (map_points - 1)
                    ):
                        file_id.write(") LINEAR LINEAR PERIODIC\ \r\n")
                        file_id.write(' DEEPSPLINE" );\r\n')
                        file_id.write("}\r\n")
                    elif i == (map_points - 1):
                        file_id.write("\ \n")
            index = index + map_points

    file_id.close()
