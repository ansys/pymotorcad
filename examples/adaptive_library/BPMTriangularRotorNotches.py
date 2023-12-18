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

# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, rt_to_xy

# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# get Adaptive parameters specified in Motor-CAD
notch_mid_angle = mc.get_adaptive_parameter_value("notch centre angle")
notch_angular_width = mc.get_adaptive_parameter_value("notch sweep")
notch_depth = mc.get_adaptive_parameter_value("notch depth")
number_notches = int(mc.get_adaptive_parameter_value("notches per pole"))

# get standard template rotor region from Motor-CAD
rotor_region = mc.get_region("Rotor")

rotor_radius = mc.get_variable("RotorDiameter") / 2
rotor_centre = Coordinate(0, 0)
duplication_angle = 360 / rotor_region.duplications

if notch_mid_angle < notch_angular_width / 2:
    # Limit so notch does not cross the lower symmetry boundary
    notch_mid_angle = notch_angular_width / 2
    mc.show_message(
        "Adaptive Parameter: 'notch mid angle' not valid, reset to " + str(notch_mid_angle)
    )
    mc.set_adaptive_parameter_value("notch mid angle", notch_mid_angle)

if notch_mid_angle > duplication_angle - notch_angular_width / 2:
    # Limit so notch does not cross the upper symmetry boundary
    notch_mid_angle = duplication_angle - notch_angular_width / 2
    mc.show_message(
        "Adaptive Parameter: 'notch mid angle' not valid, reset to " + str(notch_mid_angle)
    )
    mc.set_adaptive_parameter_value("notch mid angle", notch_mid_angle)

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

try:
    from setup_scripts.Library_Examples import display_geometry  # noqa: F401

    display_geometry("BPMTriangularRotorNotches")
except ImportError:
    pass
