"""
.. _ref_BPM_Triangular_Rotor_Notches:

Triangular Rotor Notches for IPM
================================
This script applies the adaptive templates functionality to create triangular rotor notches to
improve NVH performance.
"""
# %%
# .. note::
#    For more information on the use of Adaptive Templates in Motor-CAD, and how to create, modify
#    and debug Adaptive Templates Scripts, see :ref:`ref_adaptive_templates_UG` in the
#    :ref:`ref_user_guide`.
#
# .. note::
#    Adaptive Templates in Motor-CAD require v2024.1.2 (Motor-CAD 2024 R1 Update) or later and
#    PyMotorCAD v0.4.1. To update PyMotorCAD in Motor-CAD, go to Scripting -> Settings -> PyMotorCAD
#    updates and select 'Update to Latest Release'.
#
# This script is designed to be run from Motor-CAD template "e9". If no Motor-CAD file is open, the
# e9 template will be loaded.
#
# This script uses the following adaptive parameters:
#
# * Notch Angle (-4)
#
# * Notch Sweep (5)
#
# * Notch Depth (1)
#
# * Notches per Pole (2)
#
# If these parameters are not already set up in the Motor-CAD file, the parameters will be
# automatically set, with the default values shown in brackets.
#
# To set an adaptive geometry for a Motor-CAD file, a script must be loaded in to the Adaptive
# Templates tab (Geometry -> Editor -> Adaptive Templates) in Motor-CAD and run. When the option
# 'Geometry Templates Type' is set to 'Adaptive', this script is automatically run repeatedly to
# keep the Adaptive Geometry set in Motor-CAD.
#
# .. image:: ../../images/Adaptive_Templates_GUI_Screenshot.png
#
# This Python script can also be executed externally. When executed externally, a Motor-CAD instance
# will be launched and a file based on the "e9" template will be saved to a temporary folder. This
# script will be loaded into the Adaptive Templates tab.

# %%
# Perform Required imports
# ------------------------
# Import the ``pymotorcad`` package to access Motor-CAD. Import the ``triangular_notch`` function to
# create the notch geometry region with Adaptive Templates geometry. Import the ``os``, ``shutil``,
# ``sys``, and ``tempfile`` packages to open and save a temporary MOT file if none is open.

# sphinx_gallery_thumbnail_number = -1
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry_shapes import triangular_notch

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e9 IPM motor template is loaded, and the file is saved to a temporary folder.
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
    mc.load_template("e9")

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "BPMTriRotorNotches"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# Set Adaptive Parameters if required
# -----------------------------------
# Four Adaptive Parameters are required for this adaptive template. These are used to define the
# number of rotor notches to be added, their position and size.
#
# If the Adaptive Parameters have already been set in the current Motor-CAD file, their current
# values will be used. Otherwise, the Adaptive Parameters will be defined and set to default values.
#
# The function ``set_default_parameter`` is defined to check if a parameter exists, and if not,
# create it with a default value.


def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Use the ``set_default_parameter`` to set the required parameters if undefined
set_default_parameter("Notch Angle", -4)
set_default_parameter("Notch Sweep", 5)
set_default_parameter("Notch Depth", 1)
set_default_parameter("Notches per Pole", 2)


# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive Parameters specified in Motor-CAD, and their values
notch_angle = mc.get_adaptive_parameter_value("notch angle")
notch_angular_width = mc.get_adaptive_parameter_value("notch sweep")
notch_depth = mc.get_adaptive_parameter_value("notch depth")
number_notches = int(mc.get_adaptive_parameter_value("notches per pole"))

# %%
# Get the standard template rotor region from Motor-CAD. Calculate the rotor radius and define the
# rotor centre coordinates.
rotor_region = mc.get_region("Rotor")

rotor_radius = mc.get_variable("RotorDiameter") / 2
duplication_angle = 360 / rotor_region.duplications

# %%
# Add an ``if`` statement to account for the case when a notch crosses the symmetry boundary. This
# resets ``notch_angle`` to half the ``notch_angular_width`` away from the boundary.
if notch_angle > (duplication_angle / (2 * number_notches)) - (notch_angular_width / 2):
    # Limit so notch does not cross the symmetry boundary
    notch_angle = (duplication_angle / (2 * number_notches)) - notch_angular_width / 2
    mc.show_message("Adaptive Parameter: 'notch angle' not valid, reset to " + str(notch_angle))
    mc.set_adaptive_parameter_value("notch angle", notch_angle)

# %%
# Add an ``if`` statement to account for the case when notches overlap at the centre of the pole.
# This resets ``notch_angle`` to:
#
# * Half the ``notch_angular_width`` away from the pole centre when there are an even number of
#   notches
#
# * The full ``notch_angular_width`` away from the pole centre when there are an odd number of
#   notches
if number_notches % 2 == 0:
    x = -1
else:
    x = -2

if notch_angle < -((duplication_angle / (2 * number_notches)) - (notch_angular_width / 2)):
    # Limit so notches do not overlap at centre of pole
    notch_angle = x * ((duplication_angle / (2 * number_notches)) - notch_angular_width / 2)
    mc.show_message("Adaptive Parameter: 'notch angle' not valid, reset to " + str(notch_angle))
    mc.set_adaptive_parameter_value("notch angle", notch_angle)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# For each notch to be added:
#
# * Calculate the angular position of the notch in mechanical degrees
#
# * Apply the offset angle. For notches on the left side of the pole, the position is shifted by
#   ``+ notch_angle`` mechanical degrees. For notches on the right side of the pole, the position is
#   shifted by ``- notch_angle`` mechanical degrees.
#
# * Create the notch Region using the ``triangular_notch()`` function, imported from
#   ``ansys.motorcad.core.geometry_shapes``. The arguments for the function are:
#
#   * rotor_radius
#
#   * notch_angular_width
#
#   * notch_centre_angle
#
#   * notch_depth
#
# * Define the properties for the notch region
#
#   * name
#
#   * colour
#
#   * duplication angle
#
#   * material
#
# * set the notch's ``parent`` to the rotor region. This will allow Motor-CAD to treat the notch as
#   a sub-region of the rotor and handle subtractions automatically.
#
# * If the notch is closed, set the region in Motor-CAD.

for notch_loop in range(0, number_notches):
    notch_name = "Rotor_Notch_" + str(notch_loop + 1)

    # angular position of notch
    notch_centre_angle = ((2 * notch_loop) + 1) * (duplication_angle / (2 * number_notches))

    # Offset angle by notch_angle
    if notch_centre_angle < duplication_angle / 2:
        notch_centre_angle = notch_centre_angle - notch_angle
    if notch_centre_angle > duplication_angle / 2:
        notch_centre_angle = notch_centre_angle + notch_angle

    # generate a triangular notch region
    notch = triangular_notch(rotor_radius, notch_angular_width, notch_centre_angle, notch_depth)

    # notch properties
    notch.name = notch_name
    notch.colour = (255, 255, 255)
    notch.duplications = rotor_region.duplications
    notch.material = "Air"
    notch.parent = rotor_region

    if notch.is_closed():
        mc.set_region(notch)

# %%
# .. image:: ../../images/BPMTriangularRotorNotches.png
#     :width: 300pt

# %%
# Load in Adaptive Templates script if required
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
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
