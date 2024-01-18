"""
.. _ref_Square_Rotor_Ducts:

Square Rotor Ducts
==================
Adaptive Template script to create square rotor ducts.
"""
# %%
# This script is designed to be run from Motor-CAD template "e10".
#
# This script requires the following adaptive parameters:
#
# * SqDuct Rad Dia
#
# * SqDuct Channels per Pole
#
# * SqDuct Width
#
# * SqDuct Angle

# %%
# Setup PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)

try:
    from setup_scripts.Library_Examples import define_parameters, example_setup

    example_setup("e10", "SquareRotorDucts")
    define_parameters(
        ["SqDuct Rad Dia", "SqDuct Channels per Pole", "SqDuct Width", "SqDuct Angle"],
        [55, 2, 3, -11],
    )
except ImportError:
    pass
# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD.
# Import Coordinate, Line, Region and rt_to_xy
# to define the adaptive template geometry.
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate
from ansys.motorcad.core.geometry_shapes import square

# %%
# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive parameters specified in Motor-CAD
sqduct_rad_dia = mc.get_adaptive_parameter_value("sqduct rad dia")
sqduct_channels_per_pole = int(mc.get_adaptive_parameter_value("sqduct channels per pole"))
sqduct_width = mc.get_adaptive_parameter_value("sqduct width")
sqduct_angle = mc.get_adaptive_parameter_value("sqduct angle")

# %%
# Get the standard template rotor region from Motor-CAD.
# Calculate the rotor radius
# and define the rotor centre coordinates.
rotor_region = mc.get_region("Rotor")

rotor_radius = mc.get_variable("RotorDiameter") / 2
rotor_centre = Coordinate(0, 0)
duplication_angle = 360 / rotor_region.duplications

# number of ducts per pole
number_ducts = sqduct_channels_per_pole

for duct_loop in range(0, number_ducts):
    duct_name = "Square_Rotor_Duct_" + str(duct_loop + 1)

    # angular position of duct
    duct_centre_angle = ((2 * duct_loop) + 1) * (
        duplication_angle / (2 * number_ducts)
    ) + sqduct_angle

    # generate a square region
    duct = square(sqduct_width, sqduct_rad_dia / 2, duct_centre_angle)

    # duct properties
    duct.name = duct_name
    duct.colour = (255, 255, 255)
    duct.duplications = rotor_region.duplications
    duct.material = "Air"
    duct.parent = rotor_region

    # Set the duct region in Motor-CAD
    if duct.is_closed():
        mc.set_region(duct)
