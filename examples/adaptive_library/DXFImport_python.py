"""
Custom DXF Geometry
===================
This script applies the adaptive templates functionality to import custom rotor geometry from a
DXF file.
"""


# %%
# If no Motor-CAD file is open, the e8 template is loaded and the geometry is adjusted as
# described earlier.

# %%
# Perform required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD.
# Import the ``os``, ``shutil``, ``sys``, and ``tempfile`` packages
# to open and save a temporary MOT file if none is open.


import os
import shutil
import tempfile

import ansys.motorcad.core as pymotorcad

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e8 IPM motor template is loaded, the geometry changes described earlier are applied and the
# file is saved to a temporary folder.
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

    # Set Standard Template geometry to closely match the imported DXF custom geometry
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


# # %%
# from PIL import Image
# from IPython.display import display
# img = Image.open("C:\\Repos\\pymotorcad\\doc\\source\\images\\DXFImport4.png")
# # .. image:: ../../images/DXFImport4.png
# display(img)


from copy import deepcopy

# %%
from ansys.motorcad.core.geometry import Arc, Region

r2 = mc.get_region_dxf("DXFRegion_Rotor_14")
r3 = mc.get_region_dxf("DXFRegion_Rotor_12")


rt_region = mc.get_region("Rotor")  # get the rotor region
rotor_duct = mc.get_region("RotorDuctFluidRegion_2")
rotor_duct_3 = mc.get_region("RotorDuctFluidRegion_3")

r2_test = Region()
r2_test.entities = deepcopy(r2.entities)
r2_test.name = "custom_DXF"
r2_test.material = rotor_duct.material
r2_test.parent = rt_region
r2_test.duplications = rotor_duct.duplications

r3_test = Region()
r3_test.entities = deepcopy(r3.entities)
r3_test.name = "custom_DXF3"
r3_test.material = rotor_duct.material
r3_test.parent = rt_region
r3_test.duplications = rotor_duct_3.duplications

# if type(entity)== Line:
# print(type(entity))


def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Use the ``set_default_parameter`` to set the required parameters if undefined
set_default_parameter("Arc Factor", 0.8)
set_default_parameter("Line0 Factor", 1)
set_default_parameter("Line3 Factor", 1)


# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive Parameters specified in Motor-CAD, and their values
arc_factor = mc.get_adaptive_parameter_value("Arc Factor")
L0_factor = mc.get_adaptive_parameter_value("Line0 Factor")
L3_factor = mc.get_adaptive_parameter_value("Line3 Factor")


def scale_point(point, fix_point, line_ratio):
    point.x = (1 - line_ratio) * fix_point.x + line_ratio * point.x
    point.y = (1 - line_ratio) * fix_point.y + line_ratio * point.y
    return point


for i, entity in enumerate(r2.entities):
    if type(entity) == Arc:
        # print(type(entity))
        # print(entity.radius)
        r2_test.entities[i].radius = entity.radius * arc_factor
    if i == 0 and L0_factor != 1:
        r2_test.entities[i].end = scale_point(
            r2_test.entities[i].end, r2_test.entities[i].start, L0_factor
        )
        r2_test.entities[i + 1].start = r2_test.entities[i].end
    if i == 3 and L3_factor != 1:
        r2_test.entities[i].start = scale_point(
            r2_test.entities[i].start, r2_test.entities[i].end, L3_factor
        )
        r2_test.entities[i - 1].end = r2_test.entities[i].start

for i, entity in enumerate(r3.entities):
    if type(entity) == Arc:
        # print(type(entity))
        # print(entity.radius)
        r3_test.entities[i].radius = entity.radius * arc_factor
    if i == 0 and L3_factor != 1:
        r3_test.entities[i].end = scale_point(
            r3_test.entities[i].end, r3_test.entities[i].start, L3_factor
        )
        r3_test.entities[i + 1].start = r3_test.entities[i].end
    if i == 3 and L0_factor != 1:
        r3_test.entities[i].start = scale_point(
            r3_test.entities[i].start, r3_test.entities[i].end, L0_factor
        )
        r3_test.entities[i - 1].end = r3_test.entities[i].start

rotor_duct.replace(r2_test)
rotor_duct_3.replace(r3_test)

mc.set_region(rotor_duct)
mc.set_region(rotor_duct_3)


# %%
# .. image:: ../../images/DXFImport4.png

# %%
# Load in Adaptive Templates Script if required
# ---------------------------------------------
# When this script is run externally, the script executes the following:
#
# * Set **Geometry type** to **Adaptive**.
#
# * Load the script into the **Adaptive Templates** tab.
#
# * Go to the **Geometry -> Radial** tab to run the Adaptive Templates script and display the new
#   geometry.

# %%
# .. note::
#    When running in a Jupyter Notebook, you must provide the path for the Adaptive Templates script
#    (PY file) instead of ``sys.argv[0]`` when using the ``load_adaptive_script()`` method.
# if not pymotorcad.is_running_in_internal_scripting():
#     mc.set_variable("GeometryTemplateType", 1)
#     mc.load_adaptive_script(sys.argv[0])
#     mc.display_screen("Geometry;Radial")
# %%
