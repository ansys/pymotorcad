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
Using IPM Rotor Pockets for Water Jacket Cooling
================================================
This script applies the adaptive templates functionality to modify IPM rotor pockets to be used as
ducts for the Rotor Water Jacket cooling model.
"""
# %%
# .. note::
#    This example uses Motor-CAD Geometry Tree functionality, introduced in v2026.1.1 (Motor-CAD
#    2026 R1) and PyMotorCAD v0.8.4 or later.

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``RegionType`` for creating the adaptive templates geometry.
# Import ``deepcopy`` to copy geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.


from copy import deepcopy

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/asymmetric_SPM_thumbnail.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import RegionType

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Scripting tab in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: open a new Motor-CAD instance, load the e4a
# IPM motor template, set up some rotor ducts that overlap the rotor pockets and save
# the file to a temporary folder. To keep a new Motor-CAD instance open after executing the script,
# use the ``MotorCAD(keep_instance_open=True)`` option when opening the new instance. Alternatively,
# use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e4a")
    mc.set_variable("RotorDuctType", 1)  # set Circular Rotor Ducts
    mc.set_variable("RotorCircularDuctLayers", 2)
    e = 1
    for i in range(2):
        mc.set_array_variable("RotorCircularDuctLayer_RadialDiameter", i, 93)
        mc.set_array_variable("RotorCircularDuctLayer_Channels", i, 8)
        mc.set_array_variable("RotorCircularDuctLayer_ChannelDiameter", i, 3)
        mc.set_array_variable("RotorCircularDuctLayer_OffsetAngle", i, e * 2)
        e *= -1
    mc.set_variable("Shaft_Spiral_Groove", False)
    mc.set_variable("Rotor_Water_Jacket", True)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e4a_RotorPocketWJ"
    mc.save_to_file(working_folder + "\\" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Define Adaptive Templates Script
# --------------------------------
# The following script should be loaded in to the adaptive templates tab.

# %%
# .. code-block:: python
#
#    import ansys.motorcad.core as pymotorcad
#    from ansys.motorcad.core.geometry import RegionType
#
#    # Connect to Motor-CAD
#    motorcad_instance = pymotorcad.MotorCAD(open_new_instance=False)
#
#    # Reset geometry to default
#    motorcad_instance.reset_adaptive_geometry()
#
#    # add your geometry template here using PyMotorCAD
#    gt = motorcad_instance.get_geometry_tree()
#    rotor_ducts = gt.get_regions_of_type(RegionType.rotor_duct)
#    rotor_pockets_orig = gt.get_regions_of_type(RegionType.rotor_pocket)
#    rotor = gt.get_regions_of_type(RegionType.rotor)[0]
#
#    for duct in rotor_ducts:
#        for pocket in rotor_pockets_orig:
#            temp = mc.subtract_region(pocket, duct)
#            # tolerance 0.0001 mm
#            if temp[0].area < pocket.area - 0.0001:
#                # print(f"{duct.name} and {pocket.name} match")
#                duct.replace(pocket)
#                gt.remove_region(pocket)
#
#    motorcad_instance.set_geometry_tree(gt)


# %%
# Define required functions
# -------------------------


# %%
# This function is called when "Run" is pressed
def main():
    modify_thermal_circuit()


# %%
def region_perimeter(region):
    """
    Get the perimeter of a given region.

    Parameters
    ----------
    region : ansys.motorcad.core.geometry.Region object
        The region to get the perimeter for.

    Returns
    -------
    perimeter : float
        The perimeter of the given region.

    """
    perimeter = 0.0
    for entity in region.entities:
        perimeter += entity.length
    return perimeter


# %%
def perimeter_in_contact(region, regions):
    """
    Get the length of perimeter of a given region that is in contact with another region or regions.

    Parameters
    ----------
    region : ansys.motorcad.core.geometry.Region object
        The region to get the perimeter for.
    regions : list of ansys.motorcad.core.geometry.Region object
        List of other regions that are in contact with region.

    Returns
    -------
    contact_distance : float
        The length of the contact between two regions.

    """
    mc_i = region._motorcad_instance

    # if the regions are in contact, they can be united to make a combined region
    combined_region = mc_i.unite_regions(region, regions)

    # Take the combined region and subtract regions to get a new version of the original region,
    # which will have the same entities as the regions. Compare the entities of the new region and
    # the regions to see which entities are shared.
    for this_region in regions:
        new_region = combined_region.subtract(this_region)
        if len(new_region) > 0:
            print(
                f"more than one region created by subtracting {this_region.name} from the "
                f"combined_region!"
            )
    new_region = combined_region

    # Check for shared entities between region and regions. Check for shared entities by comparing
    # each new_region entities to each entity of regions. The shared entities will most likely be
    # defined with opposite start and end points, so also compare to the reversed version of each
    # entity of the regions.
    shared_entities = []
    for entity_i in new_region.entities:
        for this_region in regions:
            for entity_j in this_region.entities:
                reversed_entity = deepcopy(entity_j)
                reversed_entity.reverse()
                if entity_i == entity_j or entity_i == reversed_entity:
                    shared_entities.append(entity_i)

    contact_distance = 0.0
    for entity in shared_entities:
        contact_distance += entity.length

    return contact_distance


# %%
def modify_thermal_circuit():
    """
    Modify the thermal circuit to account for the fact that the fluid in the rotor pockets is in
    direct contact with the magnets as well as the rotor lam. By default, the Motor-CAD thermal
    circuit does not recognise that after adaptive templates script modification of the geometry,
    the rotor water jacket should be directly cooling the magnets.

    Calculate the appropriate thermal resistances between the fluid and the magnets, and add these
    new thermal resistances to the thermal circuit.

    Update the existing thermal resistances between the fluid and the rotor lam, by setting
    resistance multipliers.

    The thermal resistance correction is applied based on the contact distances between the fluid
    duct (rotor pocket) wall and the magnets and rotor lam. The contact distance is calculated by
    comparing the entities of the geometry regions.

    # This function should be run before any thermal calculations. It should be run any time the
    # rotor water jacket parameters (for example fluid volume flow rate) or ducts are changed, so
    # that the thermal resistances can be correctly updated.
    """

    # get the total perimeter length of rotor fluid ducts (pockets).
    gt = mc.get_geometry_tree()
    rotor_pockets = gt.get_regions_of_type(RegionType.rotor_duct)
    magnets = gt.get_regions_of_type(RegionType.magnet)
    total_pocket_perimeter = 0.0
    total_magnet_contact_distance = 0.0
    for rotor_pocket in rotor_pockets:
        total_pocket_perimeter += region_perimeter(rotor_pocket)
        for magnet in magnets:
            try:
                total_magnet_contact_distance += perimeter_in_contact(rotor_pocket, [magnet])
            except:
                pass
    # calculate the ratios for the fluid duct wall with both magnet and rotor lamination
    fluid_magnet_contact_ratio = total_magnet_contact_distance / total_pocket_perimeter
    fluid_lam_contact_ratio = 1 - fluid_magnet_contact_ratio

    # define the central node numbers for the magnet, rotor lam and rotor water jacket fluid.
    magnet_node_number = 13
    rotor_lam_node_number = 15
    fluid_rotor_wj_node_number = 74

    # get the node numbers and original thermal resistances for all axial slices
    num_axial_slices = mc.get_variable("AxialSliceDefinition") * 2 + 1
    magnet_node_numbers = []
    rotor_lam_node_numbers = []
    fluid_rotor_wj_node_numbers = []
    rwj_rt_orig = []
    for i in range(num_axial_slices):
        magnet_node_numbers.append(mc.get_offset_node_number(magnet_node_number, i + 1, 1))
        rotor_lam_node_numbers.append(mc.get_offset_node_number(rotor_lam_node_number, i + 1, 1))
        fluid_rotor_wj_node_numbers.append(
            mc.get_offset_node_number(fluid_rotor_wj_node_number, i + 1, 1)
        )

        # get the RWJ heat transfer coefficient for each axial slice.
        rwj_h = mc.get_array_variable("RotorWJ_h", i)

        # get the RWJ duct surface area for each axial slice (converted to m^2)
        rwj_area = mc.get_array_variable("RotorWJ_Area_Dissipation", i) * 1e-6

        # get the thermal resistance between the fluid node and rotor lam (calculated by Motor-CAD
        # based on the assumption that the fluid is only in contact with rotor lam).
        rwj_rt_orig.append(1 / (rwj_h * rwj_area))
        # print(f"Original RWJ thermal resistance = {rwj_rt_orig[-1]}")

    # Define new resistances between fluid and magnet nodes. The new resistance will be the original
    # resistance divided by the contact ratio.
    for i in range(len(magnet_node_numbers)):
        # rt_magnet = (rwj_rt_orig*fluid_lam_contact_ratio)/fluid_magnet_contact_ratio
        # print(rt_magnet)
        mc.set_resistance_value(
            "Magnet to Fluid",
            magnet_node_numbers[i],
            fluid_rotor_wj_node_numbers[i],
            rwj_rt_orig[i] / fluid_magnet_contact_ratio,
            "New thermal resistance for RWJ cooling of magnets",
        )

    # set resistance multiplier for existing resistances between rotor lam and fluid nodes. The
    # multiplier will be (1/fluid_lam_contact_ratio) to account for the fact that only a portion of
    # the rotor lam is in contact with the fluid.
    for i in range(len(rotor_lam_node_numbers)):
        mc.set_resistance_multiplier(
            "Rotor Lam to Fluid",
            rotor_lam_node_numbers[i],
            fluid_rotor_wj_node_numbers[i],
            1 / fluid_lam_contact_ratio,
            "Scale thermal resistance for RWJ cooling of rotor lam",
        )


# %%
# ---------- FUNCTIONS RUN DURING CALCULATIONS ----------
# These will only run if using "Run During Analysis" selected
# (Scripting -> Settings -> Run During Analysis)

# If "Run During Analysis" is selected then this script will be imported.
# This means that anything other than setting up the MotorCAD object should
# be moved to a function/class to avoid unexpected behaviour


# %%
# This class contains functions for steady-state thermal calculations
class thermal_steady:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Steady State - Initial")
        modify_thermal_circuit()

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Steady State - Main")

    def final(self):
        # Called after calculation
        print("Thermal Steady State - Final")


# %%
# This class contains functions for transient thermal calculations
class thermal_transient:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Transient - Initial")
        modify_thermal_circuit()

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Transient State - Main")

    def final(self):
        # Called after calculation
        print("Thermal Transient - Final")


# %%
# Load in Python script if required
# ---------------------------------
# When this script is run externally, the script executes the following:
#
# * Save a copy of the script to the ScriptFiles folder in the Motor-CAD working directory.
#
# * Load the script into the **Scripting -> Python Scripting** tab.
#
# * Go to the **Geometry -> Radial** tab to run the Adaptive Templates script and display the new
#   geometry.

# %%
# .. note::
#    When running in a Jupyter Notebook, you must provide the path for the script (PY file) instead
#    of ``sys.argv[0]`` when using the ``load_script()`` method.
if not pymotorcad.is_running_in_internal_scripting():
    script_folder = mc.get_variable("CurrentMotFileDir_MotorLAB") + "ScriptFiles"
    try:
        shutil.rmtree(script_folder)
    except:
        pass
    os.mkdir(script_folder)

    # Load the adaptive templates script
    adaptive_template_file = sys.argv[0].replace(
        f"examples\\advanced\\{os.path.basename(sys.argv[0])}",
        "samples\\adaptive_template\\RotorPocketFluidDucts.py",
    )
    adaptive_template_file_new = script_folder + "\\RotorPocketFluidDucts.py"
    shutil.copy(adaptive_template_file, adaptive_template_file_new)
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(adaptive_template_file_new)
    mc.display_screen("Geometry;Radial")

    # load the script into the Motor-CAD Scripting tab, and set it to run during analysis.
    script_file = script_folder + "\\" + os.path.basename(sys.argv[0])
    shutil.copy(sys.argv[0], script_file)
    mc.load_script(script_file)
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)
