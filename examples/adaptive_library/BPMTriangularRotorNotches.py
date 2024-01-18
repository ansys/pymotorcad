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
# * Notch Centre Angle (5)
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
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, rt_to_xy

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
set_default_parameter("Notch Centre Angle", 5)
set_default_parameter("Notch Sweep", 2)
set_default_parameter("Notch Depth", 1)
set_default_parameter("Notches per Pole", 2)


# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive Parameters specified in Motor-CAD, and their values
notch_mid_angle = mc.get_adaptive_parameter_value("notch centre angle")
notch_angular_width = mc.get_adaptive_parameter_value("notch sweep")
notch_depth = mc.get_adaptive_parameter_value("notch depth")
number_notches = int(mc.get_adaptive_parameter_value("notches per pole"))

# %%
# Get the standard template rotor region from Motor-CAD.
# Calculate the rotor radius
# and define the rotor centre coordinates.
rotor_region = mc.get_region("Rotor")

rotor_radius = mc.get_variable("RotorDiameter") / 2
rotor_centre = Coordinate(0, 0)
duplication_angle = 360 / rotor_region.duplications

# %%
# Add an ``if`` statement to account for the case
# when a notch crosses the lower symmetry boundary.
# This resets ``notch_mid_angle``
# to half the ``notch_angular_width``.
if notch_mid_angle < notch_angular_width / 2:
    # Limit so notch does not cross the lower symmetry boundary
    notch_mid_angle = notch_angular_width / 2
    mc.show_message(
        "Adaptive Parameter: 'notch mid angle' not valid, reset to " + str(notch_mid_angle)
    )
    mc.set_adaptive_parameter_value("notch mid angle", notch_mid_angle)

# %%
# Add an ``if`` statement to account for the case
# when a notch crosses the upper symmetry boundary.
# This resets ``notch_mid_angle``
# to the ``duplication_angle`` minus
# half the ``notch_angular_width``.
if notch_mid_angle > duplication_angle - notch_angular_width / 2:
    # Limit so notch does not cross the upper symmetry boundary
    notch_mid_angle = duplication_angle - notch_angular_width / 2
    mc.show_message(
        "Adaptive Parameter: 'notch mid angle' not valid, reset to " + str(notch_mid_angle)
    )
    mc.set_adaptive_parameter_value("notch mid angle", notch_mid_angle)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# For each notch to be added:
#
# * Calculate the angular positions for the notch
#   in mechanical degrees
#
#   * Centre Angle, Start Angle and End Angle
#
# * For alternate notches,
#   place the notch on the left or right side of the rotor.
#
#   * For even numbered notches, create notch on the right side of rotor.
#
#     * Notch airgap arc is drawn anti-clockwise,
#       a positive radius is required.
#
#   * For odd numbered notches, create notch on the left side of rotor.
#
#     * Notch airgap arc is drawn clockwise,
#       a negative radius is required.
#
#     * Recalculate the notch start/mid/end angles
#       for the left side of slot using the rotor duplication angle.
#
# * Create the notch Region and set parameters for the  name, colour etc.
#
# * Generate coordinates for the triangular notch
#   using the start/mid/end angles,
#   converting from polar to cartesian coordinates.
#
# * Create the entities (``Line``) that make up the notch Region
#   using notch coordinates.
#
# * Add the entities (``Line``) into the notch Region
#
# * If the notch is closed,
#   set the notches ``parent`` to the rotor region.
#   This will allow Motor-CAD to treat the notch as a sub-region
#   of the rotor and handle subtractions automatically.

for notch_loop in range(0, number_notches):
    notch_name = "Rotor_Notch_" + str(notch_loop + 1)

    notch_multiplier, _ = divmod(notch_loop, 2)
    # Calculate angles of the points we want in mechanical degrees for this notch
    notch_centre_angle = notch_mid_angle * (notch_multiplier + 1)
    notch_start_angle = notch_centre_angle - (notch_angular_width / 2)
    notch_end_angle = notch_centre_angle + (notch_angular_width / 2)

    if notch_loop % 2 == 0:
        # creating notch on right side of rotor, notch airgap arc is drawn
        # anti-clockwise, positive radius required
        epsilon = 1
    else:
        # creating notch on left side of rotor, notch airgap arc is drawn
        # clockwise, negative radius required
        epsilon = -1
        # recalculate the notch start/mid/end angles for left side of slot
        # using rotor duplication angle
        notch_start_angle = duplication_angle - notch_start_angle
        notch_centre_angle = duplication_angle - notch_centre_angle
        notch_end_angle = duplication_angle - notch_end_angle

    # create notch region and set parameters for name colour etc
    notch = Region()
    notch.name = notch_name
    notch.colour = (255, 255, 255)
    notch.duplications = rotor_region.duplications
    notch.material = "Air"

    # generate coordinates for triangular notch using start/mid/end
    # angles above converting from polar to cartesian
    x1, y1 = rt_to_xy(rotor_radius, notch_start_angle)
    x2, y2 = rt_to_xy(rotor_radius - notch_depth, notch_centre_angle)
    x3, y3 = rt_to_xy(rotor_radius, notch_end_angle)

    p1 = Coordinate(x1, y1)
    p2 = Coordinate(x2, y2)
    p3 = Coordinate(x3, y3)

    # using coordinate create entities making up notch region
    line_1 = Line(p3, p2)
    line_2 = Line(p2, p1)
    airgap_arc = Arc(p1, p3, rotor_centre, rotor_radius * epsilon)
    # add entities into notch region
    notch.add_entity(line_1)
    notch.add_entity(line_2)
    notch.add_entity(airgap_arc)

    if notch.is_closed():
        # set the notches parent to the rotor region, this will allow Motor-CAD to treat
        # the notch as a sub-region of the rotor and handle subtractions automatically
        notch.parent = rotor_region
        mc.set_region(notch)

# %%
# .. image:: ../../images/BPMTriangularRotorNotches.png
