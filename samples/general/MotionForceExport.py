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
Force export for Ansys Motion
=============================
This example shows how to export forces for Ansys Motion multibody analysis software, and includes
more options for controlling the offset required to align the forces with the structural model.
The file names and offset parameters are set in the main script near the end of this file.

This script should be run from the scripting tab or an external IDE, after the force calculation
has been run in Motor-CAD.
"""

import math

import ansys.motorcad.core as pymotorcad

###############################################################################
# Utility functions for export:
###############################################################################


def write_name_value_pair(file, name, value, indent_level, quoted_value, comma_end):
    # Name
    line_string = '"' + name + '"'
    # Colon as a delimiter before value
    line_string = line_string + " : "
    # Value, in quotes as required
    if quoted_value:
        line_string = line_string + '"' + value + '"'
    else:
        line_string = line_string + value
    # Pad with 4 spaces per indent level
    for i in range(indent_level * 4):
        line_string = " " + line_string
    if comma_end:
        line_string = line_string + ","
    # Write output line
    file.write(line_string + "\n")


def unv_float_str(value):
    formatted_output = f"{value:.8f}"
    # Always use '.' as a decimal separator
    return formatted_output.replace(",", ".")


def unv_float_long_str(value):
    formatted_output = f"{value:25.16e}"
    # Always use '.' as a decimal separator
    return formatted_output.replace(",", ".")


def unv_float_short_str(value):
    formatted_output = f"{value:13.5e}"
    # Always use '.' as a decimal separator
    return formatted_output.replace(",", ".")


def int_str_fixed_length_10(value):
    return f"{value:10d}"


def int_str_fixed_length_6(value):
    return f"{value:6d}"


def write_motion_load_point_definition(mc, file, load_point_loop, num_duplications):
    speed = mc.get_array_variable("LoadPoint_Speed_Array", load_point_loop)
    file.write("loadPointDefinition : {\n")
    file.write("    {\n")
    write_name_value_pair(file, "speedPoint", unv_float_str(speed), 2, False, True)
    write_name_value_pair(file, "speedUnit", "rpm", 2, True, True)
    write_name_value_pair(file, "symmetryMultiplier", str(num_duplications), 2, False, True)
    file.write("    }\n")
    file.write("}\n\n")


def get_electrical_periods_per_revolution(mc):
    # Handles SRM and BPM. Does not handle PMDC. For IM, this is per synchronous rotation
    poles = mc.get_variable("Pole_Number")
    if mc.get_variable("Motor_Type") == 2:
        # SRM
        return poles
    else:
        # Others
        return int(poles / 2)


def get_number_force_cycles(mc):
    # How many cycles have been run
    if mc.get_variable("Motor_Type") == 1:
        # IM
        try:
            # Variable was renamed in 2024R1, try newer naming first
            electrical_cycles = mc.get_variable("IMSingleLoadNumberCycles_Rotating")
        except pymotorcad.MotorCADError:
            electrical_cycles = mc.get_variable("IMSingleLoadNumberCycles")
    else:
        electrical_cycles = mc.get_variable("TorqueNumberCycles")
    return electrical_cycles


def get_num_duplications(mc, elec_cycles_per_mechanical):
    elec_cycles_run = get_number_force_cycles(mc)
    if elec_cycles_run > 1:
        if elec_cycles_run == elec_cycles_per_mechanical:
            # No duplication needed, one mechanical cycle run
            return 1
        elif elec_cycles_run % elec_cycles_per_mechanical:
            # No duplication needed, an integer number of mechanical cycles run
            return 1
        else:
            # Non-integer number of mechanical cycles run, duplication needed
            return elec_cycles_per_mechanical
    else:
        # One cycle run, duplication needed
        return elec_cycles_per_mechanical


def write_unv_general_header(file):
    # Header file data set is 151
    file.write("    -1\n")
    file.write("   151\n")
    # model file name:
    file.write("transient node force from Motor-CAD 2D solver\n")
    # model file description (or NONE)
    file.write("NONE\n")
    # program used
    file.write("PyMotorCAD Script\n")
    # date and time information (or NONE)
    file.write("NONE\n")
    file.write("    -1\n")


def write_unv_units_header(file):
    file.write("    -1\n")
    file.write("   164\n")
    # 1 = SI, followed by description, then 2 = Relative temperature mode
    file.write("  1 SI - mks (Newton/m)  2\n")
    # Unit factors to convert to SI units (length, force, temp, temp offset)
    file.write("  1.00000e+00  1.00000e+00  1.00000e+00\n")
    file.write("  0.00000e+00\n")
    file.write("    -1\n")


def mechanical_node_positions(
    node_number,
    number_of_nodes,
    stator_bore_radius,
    offset_angle_degrees,
    slice_centre_x,
    slice_centre_y,
    slice_centre_z,
):
    node_angle = node_number / number_of_nodes * 360 - offset_angle_degrees
    sin_angle = math.sin(math.radians(node_angle))
    cos_angle = math.cos(math.radians(node_angle))
    node_x = slice_centre_x + stator_bore_radius * cos_angle
    node_y = slice_centre_y - stator_bore_radius * sin_angle
    node_z = slice_centre_z
    return [node_x, node_y, node_z, cos_angle, sin_angle]


def get_mesh_node_id(position_id, num_nodes_stator, num_nodes_rotor, is_stator, is_main_node):
    """Find internal 'dummy fea' mesh ID for position on stator or rotor.
    Mod operation is applied to position ID, so we can 'loop' around machine."""

    if is_stator:
        internal_position_id = position_id % num_nodes_stator
        start_node = 1
    else:
        internal_position_id = position_id % num_nodes_rotor
        start_node = (num_nodes_stator * 2) + 1

    # Main node IDs are 0, 2, 4, ... + offset
    # Secondary node IDs are 1, 3, 5, ... + offset
    if is_main_node:
        return start_node + 2 * internal_position_id
    else:
        return start_node + 2 * internal_position_id + 1


def get_timestep_delta(mc, load_point, num_steps):
    rpm = mc.get_array_variable("LoadPoint_Speed_Array", load_point)
    if mc.get_variable("Motor_Type") == 1:
        slip = mc.get_array_variable("LoadPoint_Slip_Array", load_point)
        syncronous_rpm = rpm / (1 - slip)
    else:
        syncronous_rpm = rpm
    rotational_frequency = syncronous_rpm / 60
    return 1 / rotational_frequency / num_steps


def duplicate_magnetic_3d_data(magnetic_3d_data, num_duplications):
    if num_duplications < 2 or len(magnetic_3d_data.y) < 2:
        # Don't need to do anything, or can't
        return magnetic_3d_data
    else:
        # Duplicate. Y is electrical angle, and last point is a duplicate of the first
        original_length = len(magnetic_3d_data.y) - 1
        # Output also needs duplicated final point for consistency
        final_length = original_length * num_duplications + 1
        # Number of points also has a duplicate at end, but as we're just
        # duplicating in time, we can treat the last point like any other one
        num_points = len(magnetic_3d_data.x)

        # Duplicate time information
        new_y = []
        angle_start = magnetic_3d_data.y[0]
        angle_step = magnetic_3d_data.y[1] - magnetic_3d_data.y[0]
        for time_index in range(final_length):
            new_y.append(angle_start + time_index * angle_step)

        new_data = []
        for point_index in range(num_points):
            new_data_values = []
            for time_index in range(final_length):
                lookup_index = time_index % original_length
                new_data_values.append(magnetic_3d_data.data[point_index][lookup_index])
            new_data.append(new_data_values)

        # Replace original y and data with new
        magnetic_3d_data.data = new_data
        magnetic_3d_data.y = new_y

        return magnetic_3d_data


def export_to_motion_unv(
    mc,
    unv_filename,
    amesh_filename,
    anf_filename,
    offset_angle_degrees,
    slice_centre_x,
    slice_centre_y,
    slice_centre_z,
):
    num_load_points = mc.get_variable("numLoadPoints")
    electrical_periods_per_revolution = get_electrical_periods_per_revolution(mc)
    num_duplications = get_num_duplications(mc, electrical_periods_per_revolution)

    # Create the UNV file
    unv_file = open(unv_filename, mode="w")
    unv_file.write("metaData : {\n")
    write_name_value_pair(
        unv_file, "MaxwellSimulationType", "2D, Element-based (Surface)", 1, True, False
    )
    unv_file.write("},\n\n")
    for i in range(num_load_points):
        write_motion_load_point_definition(mc, unv_file, i, num_duplications)
    unv_file.close()
    # Get the force data from Motor-CAD for stator and rotor, just to find number of nodes and steps
    forces_stator_tangential_per_slice = mc.get_magnetic_3d_graph("Ft_Stator_OL_Lumped", 1)
    forces_rotor_tangential_per_slice = mc.get_magnetic_3d_graph("Ft_Rotor_OL_Lumped", 1)
    # Duplicate forces for a whole mechanical cycle if required
    forces_stator_tangential_per_slice = duplicate_magnetic_3d_data(
        forces_stator_tangential_per_slice, num_duplications
    )
    forces_rotor_tangential_per_slice = duplicate_magnetic_3d_data(
        forces_rotor_tangential_per_slice, num_duplications
    )

    # Check number of points and steps to output
    num_nodes_stator = len(forces_stator_tangential_per_slice.x) - 1
    num_nodes_rotor = len(forces_rotor_tangential_per_slice.x) - 1
    num_steps = len(forces_rotor_tangential_per_slice.y) - 1
    # Find stator and rotor radius.
    # This will not handle things like banding/sleeve so could be improved if needed
    stator_bore_radius = mc.get_variable("Stator_Bore") / 2
    rotor_radius = stator_bore_radius - mc.get_variable("Airgap")
    # Create the .amesh file
    amesh_file = open(amesh_filename, mode="w")
    write_unv_general_header(amesh_file)
    write_unv_units_header(amesh_file)
    # Write nodal information (2411)
    amesh_file.write("    -1\n")
    amesh_file.write("  2411\n")
    amesh_file.write("\n")
    # Stator nodes
    amesh_file.write("Stator nodes:\n")
    amesh_file.write("{\n")
    for internal_node_id in range(num_nodes_stator):
        node_x, node_y, node_z, cos_angle, sin_angle = mechanical_node_positions(
            internal_node_id,
            num_nodes_stator,
            stator_bore_radius,
            offset_angle_degrees,
            slice_centre_x,
            slice_centre_y,
            slice_centre_z,
        )

        # For all node definitions, format is
        # Node ID, followed by export coordinate system, displacement coordinate system, colour,
        # position X position Y position Z

        # Main node
        mesh_node_id = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, True, True
        )
        amesh_file.write(int_str_fixed_length_10(mesh_node_id) + "         1         1         1\n")
        amesh_file.write(
            unv_float_long_str(node_x / 1000)
            + unv_float_long_str(node_y / 1000)
            + unv_float_long_str(node_z / 1000)
            + "\n"
        )
        # Outer node
        mesh_node_id = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, True, False
        )
        amesh_file.write(int_str_fixed_length_10(mesh_node_id) + "         1         1         1\n")
        amesh_file.write(
            unv_float_long_str(node_x / 1000 * 1.1)
            + unv_float_long_str(node_y / 1000 * 1.1)
            + unv_float_long_str(node_z / 1000)
            + "\n"
        )
    amesh_file.write("}\n")
    amesh_file.write("\n")
    # Rotor nodes
    amesh_file.write("Rotor nodes:\n")
    amesh_file.write("{\n")
    for internal_node_id in range(num_nodes_rotor):
        node_x, node_y, node_z, cos_angle, sin_angle = mechanical_node_positions(
            internal_node_id,
            num_nodes_rotor,
            rotor_radius,
            offset_angle_degrees,
            slice_centre_x,
            slice_centre_y,
            slice_centre_z,
        )

        # For all node definitions, format is
        # Node ID, followed by export coordinate system, displacement coordinate system, colour,
        # position X position Y position Z

        # Main node
        mesh_node_id = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, False, True
        )
        amesh_file.write(int_str_fixed_length_10(mesh_node_id) + "         1         1         1\n")
        amesh_file.write(
            unv_float_long_str(node_x / 1000)
            + unv_float_long_str(node_y / 1000)
            + unv_float_long_str(node_z / 1000)
            + "\n"
        )
        # Outer node
        mesh_node_id = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, False, False
        )
        amesh_file.write(int_str_fixed_length_10(mesh_node_id) + "         1         1         1\n")
        amesh_file.write(
            unv_float_long_str(node_x / 1000 * 0.9)
            + unv_float_long_str(node_y / 1000 * 0.9)
            + unv_float_long_str(node_z / 1000)
            + "\n"
        )
    amesh_file.write("}\n")
    amesh_file.write("    -1\n")
    # Element information (2412). There will be 2 triangular elements per force node
    # Track element ID
    element_id = 1
    amesh_file.write("    -1\n")
    amesh_file.write("  2412\n")
    amesh_file.write("\n")
    amesh_file.write("Stator connectivity matrix:\n")
    amesh_file.write("{\n")
    for internal_node_id in range(num_nodes_stator):
        # Element ID, FEA descriptor ID (61 for triangular), physical property table (0),
        # material property table (0), color (11), number of nodes (3)

        # First triangle
        amesh_file.write(
            int_str_fixed_length_10(element_id)
            + "        61         0         0        11         3\n"
        )
        mesh_node_id_1 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, True, True
        )
        mesh_node_id_2 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, True, False
        )
        mesh_node_id_3 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, True, True
        )
        amesh_file.write(
            int_str_fixed_length_10(mesh_node_id_1)
            + int_str_fixed_length_10(mesh_node_id_2)
            + int_str_fixed_length_10(mesh_node_id_3)
            + "\n"
        )
        element_id = element_id + 1

        # Second triangle
        amesh_file.write(
            int_str_fixed_length_10(element_id)
            + "        61         0         0        11         3\n"
        )
        mesh_node_id_1 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, True, False
        )
        mesh_node_id_2 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, True, False
        )
        mesh_node_id_3 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, True, True
        )
        amesh_file.write(
            int_str_fixed_length_10(mesh_node_id_1)
            + int_str_fixed_length_10(mesh_node_id_2)
            + int_str_fixed_length_10(mesh_node_id_3)
            + "\n"
        )
        element_id = element_id + 1
    amesh_file.write("}\n")
    amesh_file.write("\n")
    amesh_file.write("Rotor connectivity matrix:\n")
    amesh_file.write("{\n")
    for internal_node_id in range(num_nodes_rotor):
        # Element ID, FEA descriptor ID (61 for triangular), physical property table (0),
        # material property table (0), color (11), number of nodes (3)

        # First triangle
        amesh_file.write(
            int_str_fixed_length_10(element_id)
            + "        61         0         0        11         3\n"
        )
        mesh_node_id_1 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, False, False
        )
        mesh_node_id_2 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, False, True
        )
        mesh_node_id_3 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, False, False
        )
        amesh_file.write(
            int_str_fixed_length_10(mesh_node_id_1)
            + int_str_fixed_length_10(mesh_node_id_2)
            + int_str_fixed_length_10(mesh_node_id_3)
            + "\n"
        )
        element_id = element_id + 1

        # Second triangle
        amesh_file.write(
            int_str_fixed_length_10(element_id)
            + "        61         0         0        11         3\n"
        )
        mesh_node_id_1 = get_mesh_node_id(
            internal_node_id, num_nodes_stator, num_nodes_rotor, False, True
        )
        mesh_node_id_2 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, False, True
        )
        mesh_node_id_3 = get_mesh_node_id(
            internal_node_id + 1, num_nodes_stator, num_nodes_rotor, False, False
        )
        amesh_file.write(
            int_str_fixed_length_10(mesh_node_id_1)
            + int_str_fixed_length_10(mesh_node_id_2)
            + int_str_fixed_length_10(mesh_node_id_3)
            + "\n"
        )
        element_id = element_id + 1
    amesh_file.write("}\n")
    amesh_file.write("    -1\n")
    amesh_file.close()
    # Force file
    if mc.get_variable("Motor_Type") == 1:
        # IM, don't include last duplicated point
        num_output_steps = num_steps
    else:
        num_output_steps = num_steps + 1
    anf_file = open(anf_filename, "w")
    slice_width = min(
        mc.get_variable("Stator_Lam_Length"), mc.get_variable("Rotor_Lam_Length")
    ) * mc.get_array_variable("RotorSkewLengthProp_Array", 0)
    slice_width = slice_width / 1000
    for load_point in range(num_load_points):
        load_point_rpm = mc.get_array_variable("LoadPoint_Speed_Array", load_point)
        delta_time = get_timestep_delta(mc, load_point, num_steps)

        # Get the force data for this operating point
        forces_stator_tangential_per_slice = mc.get_magnetic_3d_graph(
            "Ft_Stator_OL_Lumped" + "_Th" + str(load_point + 1), 1
        )
        forces_stator_radial_per_slice = mc.get_magnetic_3d_graph(
            "Fr_Stator_OL_Lumped" + "_Th" + str(load_point + 1), 1
        )
        forces_rotor_tangential_per_slice = mc.get_magnetic_3d_graph(
            "Ft_Rotor_OL_Lumped" + "_Th" + str(load_point + 1), 1
        )
        forces_rotor_radial_per_slice = mc.get_magnetic_3d_graph(
            "Fr_Rotor_OL_Lumped" + "_Th" + str(load_point + 1), 1
        )

        # Duplicate forces for a whole mechanical cycle if required
        forces_stator_tangential_per_slice = duplicate_magnetic_3d_data(
            forces_stator_tangential_per_slice, num_duplications
        )
        forces_stator_radial_per_slice = duplicate_magnetic_3d_data(
            forces_stator_radial_per_slice, num_duplications
        )
        forces_rotor_tangential_per_slice = duplicate_magnetic_3d_data(
            forces_rotor_tangential_per_slice, num_duplications
        )
        forces_rotor_radial_per_slice = duplicate_magnetic_3d_data(
            forces_rotor_radial_per_slice, num_duplications
        )

        anf_file.write("forceData\n")
        write_motion_load_point_definition(mc, anf_file, load_point, num_duplications)
        write_unv_general_header(anf_file)
        write_unv_units_header(anf_file)

        for this_step in range(num_output_steps):
            rotor_angle_deg = this_step * delta_time * (load_point_rpm / 60) * 360

            # Find step index to lookup data, Normally same as this_step,
            # except if looping for end point
            if this_step == num_steps:
                step_index = 0
            else:
                step_index = this_step

            # Write nodal force information (2414)
            anf_file.write("    -1\n")
            anf_file.write("  2414\n")
            # Analysis dataset label
            anf_file.write("     1\n")
            # Analysis dataset name
            anf_file.write("Exported by Motor-CAD: Transient data: Force\n")
            # Dataset location, 1 is data at nodes
            anf_file.write("     1\n")

            # ID line 1
            anf_file.write("NONE\n")
            # ID line 2
            anf_file.write("Data written by Motor-CAD\n")
            # ID line 3
            anf_file.write("NONE\n")
            # ID line 4
            anf_file.write("time\n")
            # ID line 5
            anf_file.write("NONE\n")
            # Format information: 1=Structural, 4=Transient, 2=3DoF vector,
            # 9=Reaction Force, 2=Single precision float, 3=Number of values for the data
            anf_file.write("         1         4         2         9         2         3\n")
            # Integer analysis data (1-8), including timestep:
            anf_file.write(
                "         0         0         1         0         0         0"
                + int_str_fixed_length_10(
                    this_step + 1,
                )
                + "         0\n"
            )
            # Integer analysis data  (9-10), not used:
            anf_file.write(
                "         0         0         0         0         0         0         0         0\n"
            )
            # Floating point data (1-6), including time for timestep:
            anf_file.write(
                unv_float_short_str(this_step * delta_time)
                + "  0.00000e+00  0.00000e+00  0.00000e+00  0.00000e+00  0.00000e+00\n"
            )
            # Floating point data (7-12), not used:
            anf_file.write(
                "- 0.00000e+00  0.00000e+00  0.00000e+00  0.00000e+00  0.00000e+00  0.00000e+00\n"
            )

            # Nodal force information:

            # Stator
            for internal_node_id in range(num_nodes_stator):
                mesh_node_id = get_mesh_node_id(
                    internal_node_id, num_nodes_stator, num_nodes_rotor, True, True
                )
                node_x, node_y, node_z, cos_angle, sin_angle = mechanical_node_positions(
                    internal_node_id,
                    num_nodes_stator,
                    stator_bore_radius,
                    offset_angle_degrees,
                    slice_centre_x,
                    slice_centre_y,
                    slice_centre_z,
                )
                this_fx = (
                    forces_stator_radial_per_slice.data[internal_node_id][step_index] * cos_angle
                    + forces_stator_tangential_per_slice.data[internal_node_id][step_index]
                    * sin_angle
                ) / slice_width
                this_fy = (
                    -1
                    * forces_stator_radial_per_slice.data[internal_node_id][step_index]
                    * sin_angle
                    + forces_stator_tangential_per_slice.data[internal_node_id][step_index]
                    * cos_angle
                ) / slice_width
                anf_file.write(int_str_fixed_length_6(mesh_node_id) + "\n")
                anf_file.write(
                    unv_float_short_str(this_fx)
                    + unv_float_short_str(this_fy)
                    + unv_float_short_str(0)
                    + "\n"
                )

            # Rotor
            for internal_node_id in range(num_nodes_rotor):
                mesh_node_id = get_mesh_node_id(
                    internal_node_id, num_nodes_stator, num_nodes_rotor, False, True
                )
                node_x, node_y, node_z, cos_angle, sin_angle = mechanical_node_positions(
                    internal_node_id,
                    num_nodes_rotor,
                    rotor_radius,
                    rotor_angle_deg + offset_angle_degrees,
                    slice_centre_x,
                    slice_centre_y,
                    slice_centre_z,
                )
                this_fx = (
                    forces_rotor_radial_per_slice.data[internal_node_id][step_index] * cos_angle
                    - forces_rotor_tangential_per_slice.data[internal_node_id][step_index]
                    * sin_angle
                ) / slice_width
                this_fy = (
                    -1
                    * forces_rotor_radial_per_slice.data[internal_node_id][step_index]
                    * sin_angle
                    - forces_rotor_tangential_per_slice.data[internal_node_id][step_index]
                    * cos_angle
                ) / slice_width
                anf_file.write(int_str_fixed_length_6(mesh_node_id) + "\n")
                anf_file.write(
                    unv_float_short_str(this_fx)
                    + unv_float_short_str(this_fy)
                    + unv_float_short_str(0)
                    + "\n"
                )

            # End of step
            anf_file.write("    -1\n")
        # End of load point
        anf_file.write("\n")
    anf_file.close()


###############################################################################
# Main script:
###############################################################################
unv_filename = "Output.unv"
amesh_filename = "Output.amesh"
anf_filename = "Output.anf"

# The offset_angle_degrees sets the position of the centre of a stator tooth relative to the X axis
# If this is set to zero, the first stator tooth is aligned with the X axis.
offset_angle_degrees = 0
slice_centre_x = 0
slice_centre_y = 0
slice_centre_z = 0

# Connect to Motor-CAD. This assumes that Motor-CAD is already running, and the model required is
# open and the model has been solved (or results loaded).
mc = pymotorcad.MotorCAD()

if mc.get_variable("SkewType") == 2:
    # Rotor skew type
    slices = mc.get_variable("RotorSkewSlices")
else:
    # No stepped rotor skew
    slices = 1

# Error for now if skew slices > 1.
# This could be extended, so we write different AMESH and ANF files per slice
if slices > 1:
    print("Only one rotor skew slice currently supported")
    exit(-1)

# Do the export
try:
    export_to_motion_unv(
        mc,
        unv_filename,
        amesh_filename,
        anf_filename,
        offset_angle_degrees,
        slice_centre_x,
        slice_centre_y,
        slice_centre_z,
    )
except pymotorcad.MotorCADError as e:
    print("Motion export files not generated. Please check that force results are available")
    print("Exception raised:")
    print(e)
