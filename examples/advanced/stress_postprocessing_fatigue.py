# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
.. _ref_fatigue_postprocessing:

Motor-CAD Fatigue post-processing example script
===============================================
This example provides post-processing for Motor-CAD rotor stress results.
The stress results are loaded, and estimates for fatigue are calculated
from Motor-CAD's stress results.
"""

# %%
# Perform required imports
# ------------------------

import pathlib
import tempfile
import uuid

import matplotlib.pyplot as plt
import numpy as np

import ansys.motorcad.core as pymotorcad

# %%
# Classes to store and manipulate stress and FEA data
# ---------------------------------------------------


class Element:
    """Data for a 1st order triangular element and its associated stress and strain

    Parameters
    ----------
    tri_index : int
        The triangle element index number
    node_1 : int
        The ID of the first node in this element
    node_2 : int
        The ID of the second node in this element
    node_3 : int
        The ID of the third node in this element
    x : float
        The X position in mm of the element
    y : float
        The Y position in mm of the element
    s_x : float
        The X direction stress component in MPa
    s_y
        The Y direction stress component in MPa
    t_xy
        The XY plane shear stress in MPa
    sp_1
        The first principal stress in MPa
    sp_2
        The second principal stress in MPa
    svm
        The Von Mises stress in MPa
    u_x
        The X direction displacement in mm
    u_y
        The Y direction displacement in mm

    Attributes
    ----------
    stress_safety_factor : float
        The stress safety factor for the defined number of cycles
    damage : float
        The damage fraction at the defined number of cycles
    """

    def __init__(
        self, tri_index, node_1, node_2, node_3, x, y, s_x, s_y, t_xy, sp_1, sp_2, svm, u_x, u_y
    ):
        self.tri_index = tri_index
        self.node_1 = node_1
        self.node_2 = node_2
        self.node_3 = node_3

        self.x = x
        self.y = y
        self.s_x = s_x
        self.s_y = s_y
        self.t_xy = t_xy
        self.sp_1 = sp_1
        self.sp_2 = sp_2
        self.svm = svm
        self.u_x = u_x
        self.u_y = u_y

        self.stress_safety_factor = 0
        self.damage = 0

    def apply_fatigue_calculation(
        self, ultimate_tensile_stress, required_life, stress_sn, cycles_sn
    ):
        """Calculate the fatigue estimates from the Von Mises stress.

        Assumes that the stress is unidirectional. A cycle is considered from zero stress to the
        maximum stress, therefore the Goodman correction is used, with the mean stress and stress
        amplitude equal to half of the maximum stress.

        Parameters
        ----------
        ultimate_tensile_stress : float
            The material ultimate tensile stress, used in the Goodman correction.
        required_life : float
            The number of cycles required
        stress_sn, cycles_sn : np.ndarray
            Corresponding arrays of stress (MPa) and number of cycles to failure for the material
            (for fully reversed stress).
        """

        elastic_stress = self.svm

        # There are two calculation approaches used:
        # 1: Stress safety factor - Find the permissible stress for the required life, and the
        #    safety factor is the ratio of the actual stress to this stress.
        # 2: Damage - Find the number of cycles achievable at the actual stress. The damage is the
        #    ratio of the achievable cycles to the required cycles.

        # Assumption that stress varies between 0 and max, so mean and amplitude are both half of
        # the maximum
        actual_mean_stress = elastic_stress / 2

        # Using the Goodman method, convert this into an equivalent fully reversing stress amplitude
        # (zero mean)
        if actual_mean_stress >= ultimate_tensile_stress:
            # If above UTS, the life is zero, so the damage must be 100%
            self.damage = 1
        else:
            actual_equivalent_stress = (
                actual_mean_stress
                * ultimate_tensile_stress
                / (ultimate_tensile_stress - actual_mean_stress)
            )
            # Look up the cycles at this stress on the S-N curve (in log-log space)
            # Need to flip the SN data so we have ascending stress data for interpolation
            allowable_cycles = np.power(
                10.0,
                np.interp(
                    np.log10(actual_equivalent_stress),
                    np.log10(np.flip(stress_sn)),
                    np.log10(np.flip(cycles_sn)),
                ),
            )
            self.damage = required_life / allowable_cycles

        # Find the max allowed stress amplitude (fully reversing) at the required number of cycles
        allowable_equivalent_stress = np.power(
            10.0, np.interp(np.log10(required_life), np.log10(cycles_sn), np.log10(stress_sn))
        )
        # Using the Goodman method, convert this into an equivalent maximum stress (0-max)
        allowable_max_stress = (
            2
            * ultimate_tensile_stress
            * allowable_equivalent_stress
            / (allowable_equivalent_stress + ultimate_tensile_stress)
        )
        if elastic_stress > 0:
            self.stress_safety_factor = allowable_max_stress / elastic_stress
        else:
            # Use a large safety factor if actual stress is zero (avoid infinite result or
            # division by zero)
            self.stress_safety_factor = 1e6


class StressRegion:
    """Data for a stressed region, including element stress data and region properties.

    Attributes
    ----------
    region_name : str
        The name of the region
    reg_code : int
        The region identifier code from the FEA
    youngs_modulus : float
        The region's Young's modulus
    poissons_ratio : float
        The region's Poisson's ratio
    elements : list of Element
        List of elements that make up the region
    """

    def __init__(self):
        self.region_name = ""
        self.reg_code = 0
        self.youngs_modulus = 0
        self.poissons_ratio = 0
        self.elements = []

    def add_element(
        self, tri_index, node_1, node_2, node_3, x, y, s_x, s_y, t_xy, sp_1, sp_2, svm, u_x, u_y
    ):
        """Add an element to the region with results from a linear elastic calculation.

        Parameters
        ----------
        tri_index : int
            The triangle element index number
        node_1 : int
            The ID of the first node in this element
        node_2 : int
            The ID of the second node in this element
        node_3 : int
            The ID of the third node in this element
        x : float
            The X position in mm of the element
        y : float
            The Y position in mm of the element
        s_x : float
            The X direction stress component in MPa
        s_y
            The Y direction stress component in MPa
        t_xy
            The XY plane shear stress in MPa
        sp_1
            The first principal stress in MPa
        sp_2
            The second principal stress in MPa
        svm
            The Von Mises stress in MPa
        u_x
            The X direction displacement in mm
        u_y
            The Y direction displacement in mm
        """
        self.elements.append(
            Element(
                tri_index, node_1, node_2, node_3, x, y, s_x, s_y, t_xy, sp_1, sp_2, svm, u_x, u_y
            )
        )

    def get_number_elements(self):
        """Return the number of elements in the region.

        Returns
        -------
        int
            Number of elements in the region.
        """
        return len(self.elements)

    def get_sp1(self):
        """Return the first principal stress as a list in MPa."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].sp_1)
        return result_array

    def get_sp2(self):
        """Return the second principal stress as a list in MPa."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].sp_2)
        return result_array

    def get_svm(self):
        """Return the Von Mises stress as a list in MPa."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].svm)
        return result_array

    def get_stress_safety_factor(self):
        """Return the estimated stress safety factor as a list in MPa."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].stress_safety_factor)
        return result_array

    def get_damage(self):
        """Return the estimated damage as a list."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].damage)
        return result_array

    def get_x(self):
        """Return the X coordinate as a list in mm."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].x)
        return result_array

    def get_y(self):
        """Return the Y coordinate as a list in mm."""
        result_array = []
        for i in range(len(self.elements)):
            result_array.append(self.elements[i].y)
        return result_array

    def apply_fatigue_calculation(
        self, ultimate_tensile_stress, required_life, stress_sn, cycles_sn
    ):
        """Update the Neuber and Glinka estimates using the Von Mises stress for all elements.

        Parameters
        ----------
        ultimate_tensile_stress : float
            The material ultimate tensile stress, used in the Goodman correction.
        required_life : float
            The number of cycles required
        stress_sn, cycles_sn : np.ndarray
            Corresponding arrays of stress (MPa) and number of cycles to failure for the material
            (for fully reversed stress).
        """

        for i in range(len(self.elements)):
            self.elements[i].apply_fatigue_calculation(
                ultimate_tensile_stress, required_life, stress_sn, cycles_sn
            )


class StressRegions:
    """Data on stresses for multiple regions."""

    def __init__(self):
        self._regions = []

    def __getitem__(self, region_number):
        return self._regions[region_number]

    def __setitem__(self, region_number, data):
        self._regions[region_number] = data

    def __len__(self):
        return len(self._regions)

    def add_region(self):
        """Add a new region"""
        self._regions.append(StressRegion())


def get_stress_data(mc, clean_up=True):
    """Load stress data from Motor-CAD

    This function should be called after the stress calculation has been carried out using
    `do_mechanical_calculation`.

    Parameters
    ----------
    mc : pymotorcad.motorcad_methods.MotorCAD
        The PyMotorCAD instance to use.
    clean_up : bool, default True
        If the temporary text file should be deleted after use.

    Returns
    -------
    StressRegions
        The stress information for all regions.
    """
    # Make a temporary filename
    temp_filename = pathlib.Path(tempfile.gettempdir()) / pathlib.Path(str(uuid.uuid4()) + ".txt")

    # The Motor-CAD FEA file always saves with '.' as a decimal separator, independent of regional
    # settings. Empty string for regions means we get all available regions
    mc.save_fea_data(str(temp_filename), 0, 0, "RegCode,X,Y,Sx,Sy,Txy,Sp1,Sp2,SVM,Ux,Uy", "", ",")

    # Open the file
    in_file = open(temp_filename, "r")

    # Read first line, second value will be length of element table (e.g. '1 41230 ElementsTable')
    split_line = in_file.readline().split(sep=" ")
    number_of_elements = int(split_line[1])
    # Skip over 4 redundant lines (blank line, plus descriptive header)
    for i in range(4):
        in_file.readline()

    # Start with an empty set of regions
    stress_regions = StressRegions()

    # Read the element data
    for i in range(number_of_elements):
        split_line = in_file.readline().split(sep=",")
        # The region code is the 5th element, after the TriIndex, Node1, Node2 & Node3
        reg_code = int(split_line[4])

        # Increase the number of regions as required
        while reg_code > len(stress_regions):
            stress_regions.add_region()

        stress_regions[reg_code - 1].add_element(
            tri_index=int(split_line[0]),
            node_1=int(split_line[1]),
            node_2=int(split_line[2]),
            node_3=int(split_line[3]),
            # Note that split_line[4] is the region code, not stored per-element
            x=float(split_line[5]),
            y=float(split_line[6]),
            s_x=float(split_line[7]),
            s_y=float(split_line[8]),
            t_xy=float(split_line[9]),
            sp_1=float(split_line[10]),
            sp_2=float(split_line[11]),
            svm=float(split_line[12]),
            u_x=float(split_line[13]),
            u_y=float(split_line[14]),
        )

    split_line = in_file.readline().split(sep=" ")
    # This should be the 2 XXX NodesTable line
    number_of_nodes = int(split_line[1])

    # Skip over 4 redundant lines (blank line, plus descriptive header)
    for i in range(4):
        in_file.readline()

    # Read the nodal data
    for i in range(number_of_nodes):
        split_line = in_file.readline().split(sep=",")
        # TODO: We could store this data, to get nodal average stresses later.

    split_line = in_file.readline().split(sep=" ")
    # This should be the 3 XXX RegionsTable line
    number_of_regions = int(split_line[1])

    # Skip over 4 redundant lines (blank line, plus descriptive header)
    for i in range(4):
        in_file.readline()

    if number_of_regions > len(stress_regions):
        raise ValueError("RegionsTable and element region codes do not match")

    # Read the region data
    for i in range(number_of_regions):
        split_line = in_file.readline().split(sep=",")
        this_region = int(split_line[0])
        if this_region > len(stress_regions):
            raise ValueError("RegionsTable and element region codes do not match")
        stress_regions[this_region - 1].reg_code = this_region
        stress_regions[this_region - 1].youngs_modulus = float(split_line[1])
        stress_regions[this_region - 1].poissons_ratio = float(split_line[2])
        stress_regions[this_region - 1].region_name = split_line[-1].strip()

    # Tidy up
    in_file.close()
    # Delete the temp file
    if clean_up:
        temp_filename.unlink()
    else:
        print("Temporary file not deleted: " + str(temp_filename))

    return stress_regions


# %%
# Main script, using the classes and methods defined above
# --------------------------------------------------------
#
# Start Motor-CAD
# ~~~~~~~~~~~~~~~
# Load a template (for users this would normally be replaced by `load_from_file()`, and disable
# popup messages.
mc = pymotorcad.MotorCAD()
mc.set_variable("MessageDisplayState", 2)
mc.load_template("e9")

# %%
# Choose which regions to show data for
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
region_names_to_postprocess = ["Rotor"]

# %%
# Set the required life for the fatigue calculation
# This is the number of cycles required from 0 RPM
# to the defined maximum speed
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
required_life = 1000000
maximum_speed = 15000

# %%
# Run the stress calculation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the shaft speed and run the mechanical stress calculation
mc.set_variable("ShaftSpeed", maximum_speed)
mc.do_mechanical_calculation()

# %%
# Read the stress data
# ~~~~~~~~~~~~~~~~~~~~
stress_regions = get_stress_data(mc)

# %%
# Plot the elastic stress data for each region
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for region_name_to_postprocess in region_names_to_postprocess:
    # Find matching regions
    for i in range(len(stress_regions)):
        if stress_regions[i].region_name == region_name_to_postprocess:
            if stress_regions[i].get_number_elements() > 0:
                fig, ax = plt.subplots(1, 2, layout="constrained", sharey=True)
                ax[0].scatter(
                    stress_regions[i].get_sp1(), stress_regions[i].get_sp2(), marker="."
                )  # , c=svm)
                ax[0].set_xlabel("Principal stress 1 [MPa]")
                ax[0].set_ylabel("Principal stress 2 [MPa]")
                ax[1].scatter(
                    stress_regions[i].get_svm(), stress_regions[i].get_sp1(), marker="."
                )  # , c=svm)
                ax[1].scatter(
                    stress_regions[i].get_svm(), stress_regions[i].get_sp2(), marker="x"
                )  # , c=svm)
                ax[1].legend(["Sp1", "Sp2"])
                ax[1].set_xlabel("Von Mises Stress [MPa]")
                ax[1].set_ylabel("Principal Stress [MPa]")
                plt.suptitle(stress_regions[i].region_name)
                plt.show()


# %%
# S-N Data
# ~~~~~~~~
# Fatigue data, assumed to be fully reversed stress

# Ultimate tensile strength in MPa used in Goodman correction
ultimate_tensile_stress = 400

cycles_sn = np.array(
    [
        100000,
        1000000,
        10000000,
    ]
)
stress_sn = np.array(
    [
        260,
        210,
        170,
    ]
)

# %%
# Apply fatigue calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Apply the fatigue calculations to the regions of interest using the region's
# `apply_fatigue_calculation` method, and plot the results.
for region_name_to_postprocess in region_names_to_postprocess:
    # Find matching regions
    for i in range(len(stress_regions)):
        if stress_regions[i].region_name == region_name_to_postprocess:
            # Apply the actual stress correction here
            stress_regions[i].apply_fatigue_calculation(
                ultimate_tensile_stress, required_life, stress_sn, cycles_sn
            )

            # Print the maximum stresses and strains
            print(f"For region {stress_regions[i].region_name}:")
            print(f"Maximum elastic stress " f"{np.max(stress_regions[i].get_svm()):.6} MPa")
            print(f"Maximum damage (0-1): " f"{np.max(stress_regions[i].get_damage()):.6}")
            print(
                f"Minimum safety factor: "
                f"{np.min(stress_regions[i].get_stress_safety_factor()):.6}"
            )

            # Plot:
            fig, ax = plt.subplots(2, 1, layout="constrained")

            # Stress vs safety factor
            ax[0].scatter(
                stress_regions[i].get_svm(),
                stress_regions[i].get_stress_safety_factor(),
                marker=".",
            )
            ax[0].set_xlabel("Stress Von Mises [MPa]")
            ax[0].set_ylabel("Safety Factor [-]")
            # Stress vs damage
            ax[1].scatter(
                stress_regions[i].get_svm(),
                stress_regions[i].get_damage(),
                marker=".",
            )
            ax[1].set_xlabel("Stress Von Mises [MPa]")
            ax[1].set_ylabel("Damage [-]")
            plt.suptitle(stress_regions[i].region_name)
            plt.show()

            # Plot stress including correction, and plastic strain
            # Plot against element data X and Y (check exactly what this corresponds to,
            # assume element centre, but seems to be one node of triangle)
            cm = plt.colormaps["jet"]
            fig, ax = plt.subplots(1, 2, layout="constrained")
            plot1 = ax[0].scatter(
                stress_regions[i].get_x(),
                stress_regions[i].get_y(),
                c=stress_regions[i].get_stress_safety_factor(),
                marker=".",
                cmap=cm,
            )
            plt.colorbar(plot1, ax=ax[0])
            ax[0].set_title("Stress safety factor")

            plot2 = ax[1].scatter(
                stress_regions[i].get_x(),
                stress_regions[i].get_y(),
                c=stress_regions[i].get_damage(),
                marker=".",
                cmap=cm,
            )
            plt.colorbar(plot2, ax=ax[1])
            ax[1].set_title("Damage")

            plt.show()
