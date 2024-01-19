"""
.. _ref_BPM_Triangular_Rotor_Notches:

Triangular Rotor Notches for IPM
================================
Adaptive Template script to create triangular rotor notches to improve NVH performance.
"""
# %%
# This script is designed to be run from Motor-CAD template "e9".
# If no Motor-CAD file is open,
# the e9 template will be loaded.
#
# This script uses the following adaptive parameters:
#
# * Notch Angle (0)
#
# * Notch Sweep (2)
#
# * Notch Depth (1)
#
# * Notches per Pole (2)
#
# If these parameters are not already set up in the Motor-CAD file,
# the parameters will be automatically set,
# with the default values shown in brackets.

# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD.
# Import Arc, Coordinate, Line, Region and rt_to_xy
# to define the adaptive template geometry.
# Import Path, tempfile and shutil
# to open and save a temporary .mot file if none is open.
from pathlib import Path
import shutil
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry_shapes import triangular_notch

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD,
# the current Motor-CAD instance will be used.
# If the script is run externally,
# and a Motor-CAD instance is currently open,
# that Motor-CAD instance will be used.
# If no Motor-CAD instance is open,
# a new Motor-CAD instance will be opened.
# TODO: Add explanation that adaptive geometry is only set when this script is loaded in.
try:
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
except pymotorcad.MotorCADError:
    # Otherwise open a new instance
    mc = pymotorcad.MotorCAD()
    # TODO: What to do if it isn't already open,
    #  but 'Show GUI when launching Motor-CAD from automation' isn't set?


# %%
# Load file if required
# ---------------------
# Check if a file is loaded already.
# If not, open the e9 IPM motor template,
# save the file to a temporary folder.
if mc.get_variable("CurrentMotFilePath_MotorLAB") == "":
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e9")
    # TODO: Should we keep Motor-CAD open if we have launched a new instance,
    #  so the user can see what's been done?

    # Open relevant file
    working_folder = Path(tempfile.gettempdir()) / "adaptive_library"
    try:
        shutil.rmtree(working_folder)
    except:
        pass

    Path.mkdir(working_folder)
    mot_name = "BPMTriRotorNotches"
    mc.save_to_file(working_folder / (mot_name + ".mot"))

    # Disable adaptive templates
    mc.set_variable("GeometryTemplateType", 0)

# %%
# Set Adaptive Parameters if required
# -----------------------------------
# Four Adaptive Parameters are required
# for this adaptive template.
# These are used to define the
# number of rotor notches to be added,
# their position and size.
#
# If the Adaptive Parameters have already been set in the current Motor-CAD file,
# their current values will be used.
# Otherwise, the Adaptive Parameters will be defined
# and set to default values.
#
# The function ``set_default_parameter`` is defined to check if a parameter exists,
# and if not, create it with a default value.


def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Use the ``set_default_parameter`` to set the required parameters if undefined
set_default_parameter("Notch Angle", 0)
set_default_parameter("Notch Sweep", 2)
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
# Get the standard template rotor region from Motor-CAD.
# Calculate the rotor radius
# and define the rotor centre coordinates.
rotor_region = mc.get_region("Rotor")

rotor_radius = mc.get_variable("RotorDiameter") / 2
duplication_angle = 360 / rotor_region.duplications

# %%
# Add an ``if`` statement to account for the case
# when a notch crosses the lower symmetry boundary.
# This resets ``notch_angle`` to half the ``notch_angular_width``
# away from the boundary.
if notch_angle > (duplication_angle / (2 * number_notches)) - (notch_angular_width / 2):
    # Limit so notch does not cross the lower symmetry boundary
    notch_angle = (duplication_angle / (2 * number_notches)) - notch_angular_width / 2
    mc.show_message("Adaptive Parameter: 'notch angle' not valid, reset to " + str(notch_angle))
    mc.set_adaptive_parameter_value("notch angle", notch_angle)
# if an even number of notches
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
# * Calculate the angular position of the notch
#   in mechanical degrees
#
# * Apply the offset angle. For notches on the left side of the pole,
#   the position is shifted by ``+ notch_angle`` mechanical degrees.
#   For notches on the right side of the pole,
#   the position is shifted by ``- notch_angle`` mechanical degrees.
#
# * Create the notch Region using the ``triangular_notch()``
#   function, imported from ``ansys.motorcad.core.geometry_shapes``.
#   The arguments for the function are:
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
# * set the notch's ``parent`` to the rotor region.
#   This will allow Motor-CAD to treat the notch as a sub-region
#   of the rotor and handle subtractions automatically.
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
