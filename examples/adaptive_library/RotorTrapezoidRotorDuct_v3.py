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
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, rt_to_xy, EntityList
from ansys.motorcad.core.geometry_drawing import draw_regions

# %%
# Connect to Motor-CAD
mc = pymotorcad.MotorCAD(open_new_instance=False)

def get_rotor_d_axis_mirror_line():
    rotor_radius = mc.get_variable("RotorDiameter")
    number_poles = mc.get_variable("Pole_Number")
    airgap_centre_x, airgap_centre_y = rt_to_xy(rotor_radius, (360 / number_poles) / 2)

    return Line(Coordinate(0, 0), Coordinate(airgap_centre_x, airgap_centre_y))

def add_corner_rounding(P1, P, P2, radius):

    #Check the length between co-ordinates
    PP1 = math.sqrt(math.pow((P.x - P1.x),2) + math.pow((P.y - P1.y),2))
    PP2 = math.sqrt(math.pow((P.x - P2.x), 2) + math.pow((P.y - P2.y), 2))
    PP1_2 = math.sqrt(math.pow((P1.x - P2.x), 2) + math.pow((P1.y - P2.y), 2))

    angle = math.acos((PP1**2 + PP2**2 - PP1_2**2)/(2*PP1*PP2))

    #angle = math.tan(PP1 / PP2)

    # angle = math.atan((P.y - P1.y) / (P.x - P1.x)) - math.atan((P.y - P2.y) / (P.x - P2.x))
    segment = radius / math.tan(angle/2.0)

    if PP1 < radius or PP2 < radius:
        print("corner radius is too large.")

    PO = math.sqrt(math.pow(radius,2) + math.pow(segment,2))

    proportion1 = segment / PP1

    C1_x = P.x - (P.x - P1.x) * proportion1
    C1_y = P.y - (P.y - P1.y) * proportion1
    C1 = Coordinate(C1_x, C1_y)

    proportion2 = segment / PP2

    C2_x = P.x - (P.x - P2.x) * proportion2
    C2_y = P.y - (P.y - P2.y) * proportion2
    C2 = Coordinate(C2_x, C2_y)

    C_x = C1.x + C2.x - P.x
    C_y = C1.y + C2.y - P.y
    C = Coordinate(C_x, C_y)

    PC = math.sqrt(math.pow((P.x - C.x),2) + math.pow((P.y - C.y),2))

    d_x = P.x - C_x
    d_y = P.y - C_y

    PO = math.sqrt(math.pow(d_x,2) + math.pow(d_y,2))

    O_x = P.x - d_x * (PO/PC)
    O_y = P.y - d_y * (PO/PC)
    Origin = Coordinate(O_x, O_y)

    C1_Origin = math.sqrt(math.pow((C1.x - Origin.x), 2) + math.pow((C1.y - Origin.y), 2))
    C2_Origin = math.sqrt(math.pow((C2.x - Origin.x), 2) + math.pow((C2.y - Origin.y), 2))
    C1_C2 = math.sqrt(math.pow((C1.x - C2.x), 2) + math.pow((C1.y - C2.y), 2))

    sweepAngle = math.acos((C1_Origin ** 2 + C2_Origin ** 2 - C1_C2 ** 2) / (2 * C1_Origin * C2_Origin))

    # startAngle = math.atan((C1.y - Origin.y) / (C1.x - Origin.x))
    # endAngle = math.atan((C2.y - Origin.y) / (C2.x - Origin.x))
    # sweepAngle = endAngle - startAngle

    # if sweepAngle < 0:
    #     sweepAngle = -sweepAngle
    #     startAngle = endAngle
    #
    # if sweepAngle > 180:
    #     sweepAngle = 180 - sweepAngle

    return C1, C2, Origin, C1_Origin
# %%
# Get required parameters and objects
# -----------------------------------
# Get the Adaptive parameters specified in Motor-CAD

trapezoid_top_width_ratio = mc.get_adaptive_parameter_value("trapezoid_top_width_ratio")
trapezoid_duct_corner_rad = mc.get_adaptive_parameter_value("trapezoid_corner_radius")

duct_centre_rad_dia = mc.get_array_variable("RotorCircularDuctLayer_RadialDiameter", 0)
trapezoid_duct_height = mc.get_array_variable("RotorCircularDuctLayer_ChannelHeight", 0)
trapezoid_duct_width = mc.get_array_variable("RotorCircularDuctLayer_ChannelWidth", 0)


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
Coord1 = duct_bottom_half.entities.points[1]

#draw_regions(duct_bottom_half)

C1, C2, Origin1, corner_rad1 = add_corner_rounding(Coord0, Coord1, Coord2, trapezoid_duct_corner_rad)
C3, C4, Origin2, corner_rad2 = add_corner_rounding(Coord1, Coord2, Coord3, trapezoid_duct_corner_rad)

# Clears all
duct_bottom_half.entities.clear()

# future
# duct_bottom_half.clear_entities()

#Add new entities:
line_1 = Line(Coord0, C1)
Corner_Round_Arc1 = Arc(C1, C2, Origin1, corner_rad1)
line_2 = Line(C2, C3)
Corner_Round_Arc2 = Arc(C3, C4, Origin2, corner_rad2)
line_3 = Line(C4, Coord3)
line_4 = Line(Coord3, Coord0)

duct_bottom_half.add_entity(line_1)
duct_bottom_half.add_entity(Corner_Round_Arc1)
duct_bottom_half.add_entity(line_2)
duct_bottom_half.add_entity(Corner_Round_Arc2)
duct_bottom_half.add_entity(line_3)
duct_bottom_half.add_entity(line_4)

#draw_regions(duct_bottom_half)

duct_top_half = mc.get_region("RotorDuctFluidRegion_1")

Coord0 = duct_top_half.entities.points[0]
Coord1 = duct_top_half.entities.points[3]
Coord2 = duct_top_half.entities.points[2]
Coord3 = duct_top_half.entities.points[1]

d_axis_mirror_line = get_rotor_d_axis_mirror_line()

C1_mirror = Coordinate.mirror(C1, d_axis_mirror_line)
C2_mirror = Coordinate.mirror(C2, d_axis_mirror_line)
C3_mirror = Coordinate.mirror(C3, d_axis_mirror_line)
C4_mirror = Coordinate.mirror(C4, d_axis_mirror_line)
Origin1_mirror = Coordinate.mirror(Origin1, d_axis_mirror_line)
Origin2_mirror = Coordinate.mirror(Origin2, d_axis_mirror_line)

# Clears all
duct_top_half.entities.clear()

#Add new entities:
line_1 = Line(Coord0, C1_mirror)
Corner_Round_Arc1 = Arc(C1_mirror, C2_mirror, Origin1_mirror, -corner_rad1)
line_2 = Line(C2_mirror, C3_mirror)
Corner_Round_Arc2 = Arc(C3_mirror, C4_mirror, Origin2_mirror, -corner_rad2)
line_3 = Line(C4_mirror, Coord3)
line_4 = Line(Coord3, Coord0)

duct_top_half.add_entity(line_1)
duct_top_half.add_entity(Corner_Round_Arc1)
duct_top_half.add_entity(line_2)
duct_top_half.add_entity(Corner_Round_Arc2)
duct_top_half.add_entity(line_3)
duct_top_half.add_entity(line_4)

#draw_regions(duct_top_half)

# set region back into Motor-CAD (updates the default region)
if duct_bottom_half.is_closed():
    mc.set_region(duct_bottom_half)
else:
    print(duct_bottom_half.name + "is not a closed region.")

# set region back into Motor-CAD (updates the default region)
if duct_top_half.is_closed():
    mc.set_region(duct_top_half)
else:
    print(duct_top_half.name + "is not a closed region.")



#draw_regions(rotor_region)

#test = 1

#square_coords = get_coordinates(duct_bottom_half)


#duct_circular_dia = mc.get_array_variable("RotorCircularDuctLayer_ChannelDiameter", 0)

# rotor_radius = mc.get_variable("RotorDiameter") / 2
# rotor_centre = Coordinate(0, 0)
# duplication_angle = 360 / rotor_region.duplications


