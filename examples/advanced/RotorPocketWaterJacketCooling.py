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
This script modifies the Motor-CAD thermal circuit by applying a thermal resistance correction to
account for direct magnet cooling by the rotor water jacket ducts.
"""
# %%
# .. note::
#    This example uses Motor-CAD Geometry Tree functionality, introduced in v2026.1.1 (Motor-CAD
#    2026 R1) and PyMotorCAD v0.8.4 or later.

# %%
# This script is designed to be run either from the **Scripting -> Python Scripting** tab in
# Motor-CAD, or as an external Python script. It works in conjunction with a separate adaptive
# templates Python script (:ref:`ref_IPM_Rotor_Pocket_Fluid_Ducts`), which must be loaded in to the
# **Geometry -> Editor -> Adaptive Templates** tab in Motor-CAD. You can download the
# ``RotorPocketFluidDucts.py`` adaptive templates script from:
# https://github.com/ansys/pymotorcad/blob/main/samples/adaptive_template/RotorPocketFluidDucts.py
#
# There are two parts to this example:
#
# * Using the ``RotorPocketFluidDucts.py`` adaptive templates script, modify the rotor geometry so
#   that Motor-CAD uses the IPM rotor pockets as ducts for rotor water jacket cooling.
#
#  .. image:: ../../images/thermal_rotor_pocket_wj_1.png

# %%
# * Using this ``RotorPocketWaterJacketCooling.py`` script, modify the Motor-CAD thermal circuit
#   so that the rotor water jacket fluid directly cools the magnets as well as the rotor lamination.
#   Without this modification, only the rotor lamination will be directly cooled by the rotor water
#   jacket fluid, because the Motor-CAD thermal module does not automatically recognise that the
#   ducts are in contact with magnets. By default, Motor-CAD always assumes that rotor ducts are
#   only in contact with the rotor lamination, and not with the magnets.
#
#  .. image:: ../../images/thermal_rotor_pocket_wj_2.png

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``RegionType`` for creating the adaptive templates geometry.
# Import ``deepcopy`` to copy geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.


# sphinx_gallery_thumbnail_path = 'images/thermal_rotor_pocket_wj_thumbnail.png'
from copy import deepcopy
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
# instance is used. Make sure that the Adaptive Templates script is also loaded into the
# **Geometry -> Editor -> Adaptive Templates** tab so that the necessary geometry modifications are
# implemented.
#
# If the script is run externally, these actions occur:
#
# * Open a new Motor-CAD instance
#
# * Load the e4a IPM motor template
#
# * Set up rotor ducts that overlap the rotor pockets
#
# * Disable **Shaft Spiral Groove** cooling
#
# * Enable **Rotor Water Jacket** cooling
#
# * Save the file to a temporary folder
#
# To keep a new Motor-CAD instance open after executing the script,
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

    # Set up two layers of rotor ducts, so that there is one duct overlapping each rotor pocket
    mc.set_variable("RotorCircularDuctLayers", 2)
    e = 1
    for i in range(2):
        mc.set_array_variable("RotorCircularDuctLayer_RadialDiameter", i, 93)
        mc.set_array_variable("RotorCircularDuctLayer_Channels", i, 8)
        mc.set_array_variable("RotorCircularDuctLayer_ChannelDiameter", i, 3)
        mc.set_array_variable("RotorCircularDuctLayer_OffsetAngle", i, e * 2)
        e *= -1

    # Disable Shaft Spiral Groove cooling and enable Rotor Water Jacket cooling
    mc.set_variable("Shaft_Spiral_Groove", False)
    mc.set_variable("Rotor_Water_Jacket", True)

    # Create a temporary working folder directory and save the Motor-CAD file
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
# Adaptive Templates Script
# --------------------------------
# A separate Adaptive Templates script (:ref:`ref_IPM_Rotor_Pocket_Fluid_Ducts`) must be loaded in
# to the **Geometry -> Editor -> Adaptive Templates** tab. The script is displayed below. You can
# copy the text and paste it into the tab, or download the file from:
# https://github.com/ansys/pymotorcad/blob/main/samples/adaptive_template/RotorPocketFluidDucts.py

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
# Define a function to get the perimeter of a given Motor-CAD geometry region. The perimeter is
# calculated by summing the lengths of all the region entities (lines and arcs).
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
# Define a function to get the length of a region perimeter that is in contact with one or more
# other regions. This will be used to calculate the amount of contact between the rotor pocket and
# the magnet, versus the contact between the rotor pocket and the lamination.
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
# Define a function to modify the thermal circuit to account for the fact that the fluid in the
# rotor pockets is in direct contact with the magnets as well as the rotor lam. By default, the
# Motor-CAD thermal circuit does not recognise that after adaptive templates script modification of
# the geometry, the rotor water jacket should be directly cooling the magnets.
#
# Calculate the appropriate thermal resistances between the fluid and the magnets, and add these
# new thermal resistances to the thermal circuit.
#
# Update the existing thermal resistances between the fluid and the rotor lam, by setting resistance
# multipliers.
#
# The thermal resistance correction is applied based on the contact distances between the fluid duct
# (rotor pocket) wall and the magnets and rotor lam. The contact distance is calculated by comparing
# the entities of the geometry regions.
#
# This function should be run before any thermal calculations. It should be run any time the rotor
# water jacket parameters (for example fluid volume flow rate) or ducts are changed, so that the
# thermal resistances can be correctly updated.
def modify_thermal_circuit():
    # Get the rotor pocket and magnet regions from the geometry tree.
    gt = mc.get_geometry_tree()
    rotor_pockets = gt.get_regions_of_type(RegionType.rotor_duct)
    magnets = gt.get_regions_of_type(RegionType.magnet)

    # Get the total rotor pocket perimeter distance and the length of the perimeter that is in
    # contact with magnet regions using the ``region perimeter`` and ``perimeter_in_contact``
    # functions.
    total_pocket_perimeter = 0.0
    total_magnet_contact_distance = 0.0
    for rotor_pocket in rotor_pockets:
        total_pocket_perimeter += region_perimeter(rotor_pocket)
        for magnet in magnets:
            try:
                total_magnet_contact_distance += perimeter_in_contact(rotor_pocket, [magnet])
            except:
                pass

    # Calculate the ratios for the rotor pocket duct contact distances with both magnet and
    # rotor lamination.
    fluid_magnet_contact_ratio = total_magnet_contact_distance / total_pocket_perimeter
    fluid_lam_contact_ratio = 1 - fluid_magnet_contact_ratio

    # Define the central thermal circuit node numbers for the magnet, rotor lam and rotor water
    # jacket fluid.
    magnet_node_number = 13
    rotor_lam_node_number = 15
    fluid_rotor_wj_node_number = 74

    # Get the node numbers and original thermal resistances for all axial slices and store in lists.
    # Use the ``get_offset_node_number`` method to get the offset node numbers for each axial slice.
    #
    # Get the rotor water jacket heat transfer coefficient and duct surface area for each axial
    # slice, calculated based on the assumption that the rotor duct is only in contact with rotor
    # lamination. Use the heat transfer coefficient and dissipation area to calculate an original
    # thermal resistance value, before correction.
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

        # Get the RWJ heat transfer coefficient for each axial slice.
        rwj_h = mc.get_array_variable("RotorWJ_h", i)

        # Get the RWJ duct surface area for each axial slice (converted to m^2)
        rwj_area = mc.get_array_variable("RotorWJ_Area_Dissipation", i) * 1e-6

        # Get the thermal resistance between the fluid node and rotor lam (calculated by Motor-CAD
        # based on the assumption that the fluid is only in contact with rotor lam).
        rwj_rt_orig.append(1 / (rwj_h * rwj_area))
        # print(f"Original RWJ thermal resistance = {rwj_rt_orig[-1]}")

    # Define new thermal resistances between fluid and magnet nodes. The new resistance will be the
    # original resistance divided by the contact ratio.
    for i in range(len(magnet_node_numbers)):
        mc.set_resistance_value(
            "Magnet to Fluid",
            magnet_node_numbers[i],
            fluid_rotor_wj_node_numbers[i],
            rwj_rt_orig[i] / fluid_magnet_contact_ratio,
            "New thermal resistance for RWJ cooling of magnets",
        )

    # Set resistance multipliers for the existing thermal resistances between rotor lam and fluid
    # nodes. The multiplier will be (1/fluid_lam_contact_ratio) to account for the fact that only a
    # portion of the fluid duct is in contact with the rotor lamination (with the rest in contact
    # with the magnet).
    for i in range(len(rotor_lam_node_numbers)):
        mc.set_resistance_multiplier(
            "Rotor Lam to Fluid",
            rotor_lam_node_numbers[i],
            fluid_rotor_wj_node_numbers[i],
            1 / fluid_lam_contact_ratio,
            "Scale thermal resistance for RWJ cooling of rotor lam",
        )


# %%
# Define the ``main`` function that is called when **Run** is clicked in the Motor-CAD
# **Scripting -> Python Scripting** tab. This function calls the ``modify_thermal_circuit``
# function.
def main():
    modify_thermal_circuit()


# %%
# Functions run during calculations
# ---------------------------------
# These will only run if **Run During Analysis** is enabled on the **Scripting -> Settings** tab in
# Motor-CAD.
#
# Thermal steady state calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define a class that contains functions to run during steady-state thermal calculations.
#
# Add the ``modify_thermal_circuit`` function to the ``initial`` function of the class. The function
# will be called whenever a steady state thermal calculation is run in Motor-CAD. The function will
# be called **before** the calculation.
#
# Modify the thermal circuit before the calculation. If any parameters have been changed that
# alter the rotor water jacket cooling, the thermal resistances are recalculated and applied in the
# thermal circuit.
class thermal_steady:
    def initial(self):
        # Recalculate and apply the thermal resistances before the calculation
        modify_thermal_circuit()

# %%
# Thermal transient calculations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define a class that contains functions to run during transient thermal calculations. As with the
# steady state thermal calculation, run the ``modify_thermal_circuit`` function in the ``initial``
# function of the class, so that the thermal circuit is modified before the calculation.
#
# If any rotor water jacket parameters change during the transient (such as speed dependent flow
# rate during a duty cycle) then the ``modify_thermal_circuit`` function should also be called
# during the ``main`` function of the ``thermal_transient`` class.
class thermal_transient:
    def initial(self):
        # Recalculate and apply the thermal resistances before the calculation
        modify_thermal_circuit()

    # def main(self):
    #     # Called before each time step in calculation
    #     self.step = self.step + 1
    #     print("Step: " + str(self.step) + ". Thermal Transient State - Main")
    #     modify_thermal_circuit()


# %%
# Load in Python script if required
# ---------------------------------
# When this script is run externally, the script executes the following:
#
# * Load the adaptive templates script into the **Geometry -> Editor -> Adaptive Templates** tab in
#   Motor-CAD
#
# * Set **Geometry type** to **Adaptive**
#
# * Go to the **Geometry -> Radial** tab to run the Adaptive Templates script and display the new
#   geometry
#
# * Save a copy of this script to a ``ScriptFiles`` subfolder in the Motor-CAD working directory
#
# * Load this script into the **Scripting -> Python Scripting** tab in Motor-CAD
#
# * Enable **Run During Analysis** on the **Scripting -> Settings** tab
#
# * Run the script to carry out the thermal circuit modifications

# %%
# .. note::
#    This script expects to be located in a subfolder ``advanced`` inside a ``examples`` folder. It
#    also expects the adaptive templates script to be located in a subfolder ``adaptive_template``
#    inside a ``samples`` folder. If the script is run externally, the script will attempt to copy
#    the script files based on these directory paths. If you save the scripts in a different folder
#    structure, you will need to modify the script to point to the correct locations of the scripts.
#
# .. note::
#    When running in a Jupyter Notebook, you must provide the path for the script (PY file) instead
#    of ``sys.argv[0]`` when using the ``load_script()`` method.
if not pymotorcad.is_running_in_internal_scripting():
    # Create the ``ScriptFiles`` subfolder in the working directory if it does not already exist
    script_folder = mc.get_variable("CurrentMotFileDir_MotorLAB") + "ScriptFiles"
    try:
        os.mkdir(script_folder)
    except:
        pass

    # Get the adaptive templates script from ``samples\adaptive_template\RotorPocketFluidDucts.py``.
    # Copy the script to the ``ScriptFiles`` folder.
    adaptive_template_file = sys.argv[0].replace(
        f"examples\\advanced\\{os.path.basename(sys.argv[0])}",
        "samples\\adaptive_template\\RotorPocketFluidDucts.py",
    )
    adaptive_template_file_new = script_folder + "\\RotorPocketFluidDucts.py"
    shutil.copy(adaptive_template_file, adaptive_template_file_new)

    # Enable adaptive templates geometry and load in the adaptive templates script file
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(adaptive_template_file_new)
    mc.display_screen("Geometry;Radial")

    # Load this script into the Motor-CAD Scripting tab, and set it to run during analysis. Then,
    # run the script.
    script_file = script_folder + "\\" + os.path.basename(sys.argv[0])
    shutil.copy(sys.argv[0], script_file)
    mc.load_script(script_file)
    mc.set_variable("ScriptAutoRun_PythonClasses", 1)
    mc.run_script()
