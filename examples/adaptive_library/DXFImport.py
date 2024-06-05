"""
Custom DXF Geometry
===================
This script applies the adaptive templates functionality to import custom rotor geometry from a
.dxf file.
"""
# %%
# .. note::
#    For more information on how to add imported DXF geometries to Adaptive Templates in Motor-CAD,
#    see :ref:`ref_adaptive_templates_UG` in the :ref:`ref_user_guide`.
#
# .. note::
#    DXF Import for Adaptive Templates in Motor-CAD requires v2024.2.0.6 (Motor-CAD 2024 R2) or
#    later and PyMotorCAD v0.4.2. To update PyMotorCAD in Motor-CAD, go to
#    **Scripting -> Settings** and select 'Update to Latest Release' under PyMotorCAD updates.

# %%
# This script is designed to be run from Motor-CAD template "e8". The "e8" template file contains an
# imported custom geometry from a .dxf file. The template should be adjusted slightly to more
# closely match the imported custom geometry before running the Adaptive Templates script.
# The following Standard Template geometry changes should be made:
#
# * Set L1 Mag Gap Inner and L2 Mag Gap Inner to 0 mm (for Magnet Layers 1 and 2).
#
# * Set L2 Web Thickness to 18 mm (for Magnet Layer 2).
#
# * Set L2 Pole Arc [ED] to 105 electrical degrees (for Magnet Layer 2).
#
# * Set L2 RDuct Rad Dia to 123.8 mm (for Rotor Duct Layer 2).
#
# * Set L2 RDuct Dia to 4.94 mm (for Rotor Duct Layer 2).

# %%
# .. image:: ../../images/DXFImport1_2.png

# %%
# If no Motor-CAD file is open, the e8 template will be loaded and the geometry will be adjusted as
# described above.

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/Adaptive_DXF_Import_5.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e8 IPM motor template is loaded, the geometry changes described above are applied and the file
# is saved to a temporary folder.
# To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e8")

    # Set Standard Template geometry to closely match the imported .dxf custom geometry
    mc.set_array_variable(
        "VShape_Magnet_ClearanceInner", 0, 0
    )  # Set the Magnet Inner Gap to 0 mm for Layer 1
    mc.set_array_variable(
        "VShape_Magnet_ClearanceInner", 1, 0
    )  # Set the Magnet Inner Gap to 0 mm for Layer 2
    mc.set_array_variable("WebThickness_Array", 1, 18)  # Set the Web Thickness to 18 mm for Layer 2
    mc.set_array_variable("PoleArc_Array", 1, 105)  # Set the Pole Arc to 105 ED for Layer 2
    mc.set_array_variable(
        "RotorCircularDuctLayer_RadialDiameter", 1, 123.8
    )  # Set the Rotor Duct Radial Diameter to 123.8 mm for Layer 2
    mc.set_array_variable(
        "RotorCircularDuctLayer_ChannelDiameter", 1, 4.94
    )  # Set the Rotor Duct Diameter to 4.94 mm for Layer 2

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e8_DXF_Import"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required region objects
# ---------------------------
# Identify the required regions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method will replace existing template regions with corresponding imported regions. For
# example, the Standard Template geometry region "RotorDuctFluidRegion_2" will be replaced by an
# custom region from the imported .dxf file.
#
# .. image:: ../../images/DXFImport2.png
#
# The name of the corresponding .dxf region can be found under **Import** in the Geometry tree in
# the **Geometry -> Editor -> Geometry** tab in Motor-CAD. Imported regions are displayed by
# selecting the checkbox. For example, the corresponding imported .dxf region for template region
# "RotorDuctFluidRegion_2" is named "DXFRegion_Rotor_14".
#
# .. image:: ../../images/DXFImport3.png
#
# This method will replace the entities (lines and arcs) of "RotorDuctFluidRegion_2" with entities
# from "DXFRegion_Rotor_14". The geometry will be replaced, while the properties of the region
# "RotorDuctFluidRegion_2" are retained (name, material, colour etc.).

# %%
# Get existing template regions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The regions in the existing template geometry that we wish to replace with custom regions from the
# imported .dxf geometry will be stored in a list. Use the ``get_region()`` method to get the
# required regions and store these in the ``standard_regions`` list.
standard_regions = [
    mc.get_region("Rotor Pocket_1"),
    mc.get_region("Rotor Pocket_2"),
    mc.get_region("Rotor Pocket_4"),
    mc.get_region("Rotor Pocket_5"),
    mc.get_region("RotorDuctFluidRegion_2"),
    mc.get_region("RotorDuctFluidRegion_3"),
]

# %%
# Get imported .dxf regions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The imported .dxf regions that we wish to replace the existing regions with will be stored in the
# a list. Use the ``get_region_dxf()`` method to get the required regions and store in the
# ``replacement_regions`` list. The indices of the regions in the ``standard_regions`` and
# ``replacement_regions`` lists must match such that the corresponding standard and replacement
# regions share the same index (for example, the "RotorDuctFluidRegion_2" and "DXFRegion_Rotor_14"
# regions are both the fifth element of their respective lists).
replacement_regions = [
    mc.get_region_dxf("DXFRegion_Rotor_6"),
    mc.get_region_dxf("DXFRegion_Rotor_7"),
    mc.get_region_dxf("DXFRegion_Rotor_10"),
    mc.get_region_dxf("DXFRegion_Rotor_11"),
    mc.get_region_dxf("DXFRegion_Rotor_14"),
    mc.get_region_dxf("DXFRegion_Rotor_12"),
]

# %%
# Replace the ``standard_regions`` with the ``replacement_regions``
# -----------------------------------------------------------------
# For each standard region, use the ``Region.replace()`` method to replace the region with its
# corresponding imported .dxf region. The ``Region.replace()`` method replaces the entities
# (lines and arcs) of a region with entities from another region. The geometry entities will be
# replaced, while the properties of the original regions are retained (name, material, colour
# etc.).
#
# For more information on the ``Region.replace()`` method see the entry under ``Region`` in
# :ref:`ref_geometry_functions` in the :ref:`ref_API_Reference`.
#
# Once the entities have been replaced, use the ``set_region()`` method to set the modified region
# in Motor-CAD.
for index in range(len(standard_regions)):
    i = standard_regions[index]
    i.replace(replacement_regions[index])
    mc.set_region(i)

# %%
# .. image:: ../../images/DXFImport4.png

# %%
# Load in Adaptive Templates Script if required
# ---------------------------------------------
# When this script is run externally, the following is executed:
#
# * Set Geometry type to "Adaptive"
#
# * Load the script into the Adaptive Templates tab
#
# * Go to the Geometry -> Radial tab to run the Adaptive Templates Script and display the new
#   geometry

# %%
# .. note::
#    When running in a Jupyter Notebook, the path for the Adaptive Templates script (PY file) must
#    be given instead of ``sys.argv[0]`` when using the ``load_adaptive_script()`` method.
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
