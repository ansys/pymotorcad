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

# %%
# Perform Required imports
# ------------------------
# Import pymotorcad to access Motor-CAD.
# Import Arc, Coordinate, Line, Region and rt_to_xy
# to define the adaptive template geometry.
import ansys.motorcad.core as pymotorcad
import math
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, rt_to_xy
from ansys.motorcad.core.geometry_drawing import draw_regions

# %%
# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

def get_rotor_d_axis_mirror_line():
    rotor_radius = mc.get_variable("RotorDiameter")
    number_poles = mc.get_variable("Pole_Number")
    airgap_centre_x, airgap_centre_y = rt_to_xy(rotor_radius, (360 / number_poles) / 2)

    return Line(Coordinate(0, 0), Coordinate(airgap_centre_x, airgap_centre_y))

# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive parameters specified in Motor-CAD

trapezoid_top_width_ratio = mc.get_adaptive_parameter_value("trapezoid_top_width_ratio")

duct_centre_rad_dia = mc.get_array_variable("RotorCircularDuctLayer_RadialDiameter", 0)
trapezoid_duct_height = mc.get_array_variable("RotorCircularDuctLayer_ChannelHeight", 0)
trapezoid_duct_width = mc.get_array_variable("RotorCircularDuctLayer_ChannelWidth", 0)
trapezoid_duct_corner_rad = mc.get_array_variable("RotorRectangularDuctLayer_CornerRadius", 0)

# get pocket from Motor-CAD using unique name
duct_bottom_half = mc.get_region("RotorDuctFluidRegion_2")

#draw_regions(duct_bottom_half)

entity0 = duct_bottom_half.entities[0]

Coord0 = duct_bottom_half.entities.points[0]
Coord1 = duct_bottom_half.entities.points[1]
Coord2 = duct_bottom_half.entities.points[2]
Coord3 = duct_bottom_half.entities.points[3]

# Calculate the new y value
New_y = (trapezoid_duct_width / 2.0) * trapezoid_top_width_ratio

Coord1_New = Coordinate(Coord1.x, New_y)

# Method 1: edit the existing point
duct_bottom_half.edit_point(Coord1, Coord1_New)

# set region back into Motor-CAD (updates the default region)
if duct_bottom_half.is_closed():
    mc.set_region(duct_bottom_half)
else:
    print(duct_bottom_half.name + "is not a closed region.")

#draw_regions(duct_bottom_half)

duct_top_half = mc.get_region("RotorDuctFluidRegion_1")

d_axis_mirror_line = get_rotor_d_axis_mirror_line()

MirroredCoord = Coordinate.mirror(Coord1_New, d_axis_mirror_line)

Coord4 = duct_top_half.entities.points[3]

duct_top_half.edit_point(Coord4, MirroredCoord)

# set region back into Motor-CAD (updates the default region)
if duct_top_half.is_closed():
    mc.set_region(duct_top_half)
else:
    print(duct_top_half.name + "is not a closed region.")

#draw_regions(duct_top_half)

#rotor_region = mc.get_region("Rotor")

#draw_regions(rotor_region)

#test = 1

#square_coords = get_coordinates(duct_bottom_half)


#duct_circular_dia = mc.get_array_variable("RotorCircularDuctLayer_ChannelDiameter", 0)

# rotor_radius = mc.get_variable("RotorDiameter") / 2
# rotor_centre = Coordinate(0, 0)
# duplication_angle = 360 / rotor_region.duplications


