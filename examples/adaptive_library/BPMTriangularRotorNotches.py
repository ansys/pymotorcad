"""
.. _ref_BPM_Triangular_Rotor_Notches:

Triangular Rotor Notches for IPM
================================
Adaptive Template script to create triangular rotor notches to improve NVH performance.
"""
# %%
# This script is designed to be run from Motor-CAD template "e9".
#
# This script requires the following adaptive parameters:
#
# * Notch Centre Angle
#
# * Notch Sweep
#
# * Notch Depth
#
# * Notches per Pole

# %%
# Setup PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)

try:
    from setup_scripts.Library_Examples import define_parameters, example_setup

    example_setup("e9", "BPMTriRotorNotches")
    define_parameters(
        ["Notch Centre Angle", "Notch Sweep", "Notch Depth", "Notches per Pole"], [5, 2, 1, 2]
    )
except ImportError:
    pass

# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD.
# Import Arc, Coordinate, Line, Region and rt_to_xy
# to define the adaptive template geometry.
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate
from ansys.motorcad.core.geometry_shapes import triangular_notch

# %%
# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive parameters specified in Motor-CAD
# Note that notch sweep is in mechanical degrees
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

    # angular position of duct
    notch_centre_angle = ((2 * notch_loop) + 1) * (
        duplication_angle / (2 * number_notches)
    ) + notch_mid_angle

    # notch_multiplier, _ = divmod(notch_loop, 2)
    # Calculate angles of the points we want in mechanical degrees for this notch
    # notch_centre_angle = notch_mid_angle * (notch_multiplier + 1)
    # notch_start_angle = notch_centre_angle - (notch_angular_width / 2)
    # notch_end_angle = notch_centre_angle + (notch_angular_width / 2)

    # if notch_loop % 2 == 0:
    #     # creating notch on right side of rotor, notch airgap arc is drawn
    #     # anti-clockwise, positive radius required
    #     epsilon = 1
    # else:
    #     # creating notch on left side of rotor, notch airgap arc is drawn
    #     # clockwise, negative radius required
    #     epsilon = -1
    #     # recalculate the notch start/mid/end angles for left side of slot
    #     # using rotor duplication angle
    #     notch_start_angle = duplication_angle - notch_start_angle
    #     notch_centre_angle = duplication_angle - notch_centre_angle
    #     notch_end_angle = duplication_angle - notch_end_angle

    # create notch region and set parameters for name colour etc
    notch = triangular_notch(
        rotor_radius,
        rotor_centre,
        epsilon,
        notch_start_angle,
        notch_centre_angle,
        notch_end_angle,
        notch_depth,
    )
    notch.name = notch_name
    notch.colour = (255, 255, 255)
    notch.duplications = rotor_region.duplications
    notch.material = "Air"

    if notch.is_closed():
        # set the notches parent to the rotor region, this will allow Motor-CAD to treat
        # the notch as a sub-region of the rotor and handle subtractions automatically
        notch.parent = rotor_region
        mc.set_region(notch)

# %%
# Display geometry for  PyMotorCAD Documentation Example
# -------------------------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
# try:
#     from setup_scripts.Library_Examples import display_geometry  # noqa: F401
#
#     display_geometry("BPMTriangularRotorNotches")
# except ImportError:
#     pass
