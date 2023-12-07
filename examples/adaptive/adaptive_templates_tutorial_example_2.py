"""
.. _ref_adaptive_templates_example_2:

Curved Rotor Flux Barriers for SYNCREL U-Shape
==============================================
This example describes a workflow using Adaptive Templates to
create a Synchronous Reluctance machine geometry with curved flux barriers.
This is done using a Motor-CAD Adaptive Templates script, which is provided.
This script works by altering a SYNCREL U-Shape rotor template.
More information on this example can be found in the Motor-CAD Adaptive Templates
tutorial (Example 2), provided with a Motor-CAD installation.
"""

# %%
# Set up example
# --------------
# Setting up this example consists of performing imports,
# specifying the working directory, launching Motor-CAD,
# and disabling all popup messages from Motor-CAD.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~

import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~

mc = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("MessageDisplayState", 2)
mc.set_visible(True)

# %%
# Open relevant file
# ~~~~~~~~~~~~~~~~~~
# Specify the working directory and open the relevant Synchronous Reluctance machine
# template file for this example (i3).

working_folder = os.getcwd()
mc.load_template("i3")
mot_name = "Adaptive_Templates_Example_2"
mc.save_to_file(os.path.join(working_folder, mot_name + ".mot"))

# %%
# Enable adaptive templates
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the relevant parameter to enable Adaptive Templates in the Motor-CAD file.

mc.set_variable("GeometryTemplateType", 1)

# %%
# Load and run adaptive templates script file
# --------------------------------------------
# Load the adaptive templates script file into Motor-CAD.
# The script will run automatically once loaded.
#
# Load adaptive templates script file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mc.load_adaptive_script(
    os.path.join(
        working_folder, "adaptive_template_script_files/UShapeSYNCRELCurvedFluxBarriers.py"
    )
)

# %%
# The script that was loaded in is shown below:
#
# UShapeSYNCRELCurvedFluxBarriers.py script file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# %%
#
# .. code:: python
#
#   """Adaptive Templates script to alter SYNCREL U-Shape
#   rotor template to use curved rotor pockets.
#   This script does not support:
#       Zero inner/outer layer thickness
#       Inner/outer posts
#   """
#   import ansys.motorcad.core as pymotorcad
#   from ansys.motorcad.core.geometry import Arc, Coordinate, Line, rt_to_xy, xy_to_rt
#
#   # Connect to Motor-CAD
#   mc = pymotorcad.MotorCAD(open_new_instance=False)
#
#
#   def get_barrier_centre_and_radius(coordinate_1, coordinate_2, coordinate_3, arc_direction):
#       """Calculate barrier arc centre and radius coordinates.
#
#       Parameters
#       ----------
#       coordinate_1 : Coordinate
#           Arc start coordinate.
#
#       coordinate_2 : Coordinate
#           Extra coordinate on arc
#
#       coordinate_3 : Coordinate
#           Arc end coordinate
#
#       arc_direction : Integer
#           Direction to create arc between start/end
#
#       Returns
#       -------
#       radius : float
#           Arc radius
#
#       centre : Coordinate
#           Arc centre coordinate
#       """
#       _, start_t = xy_to_rt(coordinate_1.x, coordinate_1.y)
#       _, end_t = xy_to_rt(coordinate_3.x, coordinate_3.y)
#
#       a = (
#           coordinate_1.x * (coordinate_2.y - coordinate_3.y)
#           - coordinate_1.y * (coordinate_2.x - coordinate_3.x)
#           + coordinate_2.x * coordinate_3.y
#           - coordinate_3.x * coordinate_2.y
#       )
#       b = (
#           (coordinate_1.x**2 + coordinate_1.y**2) * (coordinate_3.y - coordinate_2.y)
#           + (coordinate_2.x**2 + coordinate_2.y**2) * (coordinate_1.y - coordinate_3.y)
#           + (coordinate_3.x**2 + coordinate_3.y**2) * (coordinate_2.y - coordinate_1.y)
#       )
#       c = (
#           (coordinate_1.x**2 + coordinate_1.y**2) * (coordinate_2.x - coordinate_3.x)
#           + (coordinate_2.x**2 + coordinate_2.y**2) * (coordinate_3.x - coordinate_1.x)
#           + (coordinate_3.x**2 + coordinate_3.y**2) * (coordinate_1.x - coordinate_2.x)
#       )
#       centre = Coordinate((-b / a) / 2, (-c / a) / 2)
#       radius = Line(centre, coordinate_1).length * arc_direction
#
#       return radius, centre
#
#
#   def get_pockets_include_corner_rounding():
#       """Whether corner rounding should be applied to pocket.
#
#       Returns
#       -------
#           boolean
#       """
#       return (mc.get_variable("CornerRounding_Rotor") == 1) and (
#           mc.get_variable("CornerRoundingRadius_Rotor") > 0
#       )
#
#
#   def get_rotor_mirror_line():
#       """Create mirror line through rotor from origin to airgap.
#
#       Returns
#       -------
#           Line
#       """
#       rotor_radius = mc.get_variable("RotorDiameter")
#       number_poles = mc.get_variable("Pole_Number")
#       airgap_centre_x, airgap_centre_y = rt_to_xy(rotor_radius, (360 / number_poles) / 2)
#
#       return Line(Coordinate(0, 0), Coordinate(airgap_centre_x, airgap_centre_y))
#
#
#   def get_coordinates(pocket, coordinate_indices, mirror_line=None):
#       """Get list of coordinates from pocket using coordinate_indices.
#       Coordinates ordered : start, end, extra coordinate on arc.
#
#       Parameters
#       ----------
#       pocket : Region
#           Pocket region
#
#       coordinate_indices : list of integer
#           Pocket region coordinate indices
#
#       mirror_line : Line
#           Mirror line to generate extra coordinate on arc
#
#       Returns
#       -------
#           list of Coordinate
#       """
#       coordinates = [pocket.points[index] for index in coordinate_indices]
#       if mirror_line is not None:
#           # mirror first coordinate to generate third coordinate on arc
#           coordinates.append(coordinates[0].mirror(mirror_line))
#
#       return coordinates
#
#
#   def get_coordinates_no_centre_post(pocket):
#       """Get list of coordinates to use to generate top and bottom arcs for pocket.
#       Coordinates ordered : start, end, extra coordinate for each arc.
#
#       Returns
#       -------
#           list of Coordinate
#       """
#       # return coordinates at indices from pocket.points, these indices match up with
#       # coordinates from each pocket region with/without corner rounding
#       # coordinate index ordering [start, end, centre, start, end, centre]
#       # indices have been selected using Motor-CAD geometry editor
#       if get_pockets_include_corner_rounding():
#           return get_coordinates(pocket, [2, 8, 5, 11, 17, 14])
#       else:
#           return get_coordinates(pocket, [1, 5, 3, 6, 0, 8])
#
#
#   def get_coordinates_centre_post(pocket):
#       """Get list of coordinates to use to generate top and bottom arcs for pocket.
#       Coordinates ordered : start, end, extra coordinate for each arc.
#
#       Parameters
#       ----------
#       pocket : Region
#           Pocket region
#
#       Returns
#       -------
#           list of Coordinate
#       """
#       # mirror required to generate the third point on arc, this third point is required
#       # to calculate the centre and radius of arc, the mirror line mirrors  the start point
#       # of each pocket arc to generate this third point
#       mirror = get_rotor_mirror_line()
#       # return coordinates at indices from pocket.points, these indices match up with
#       # coordinates from each pocket region with/without corner rounding
#       # coordinate index ordering [start, end, centre, start, end, centre]
#       # indices have been selected using Motor-CAD geometry editor
#       if get_pockets_include_corner_rounding():
#           return get_coordinates(pocket, [2, 5], mirror) + get_coordinates(
#               pocket, [8, 11], mirror_line=mirror
#           )
#       else:
#           return get_coordinates(pocket, [1, 3], mirror) + get_coordinates(
#               pocket, [4, 0], mirror_line=mirror
#           )
#
#
#   def update_pocket_geometry(pocket, coordinates):
#       """Update the pocket entities to create curved pocket using input coordinates.
#
#       Parameters
#       ----------
#       pocket : Region
#           Pocket region
#
#       coordinates : list of Coordinate
#           Coordinates to generate arcs with in region
#       """
#       entities = []
#       # create list of arc entities from coordinates
#       for element in range(0, len(coordinates), 3):
#           if (element + 1) % 2 == 0:
#               # clockwise arc
#               arc_direction = -1
#           else:
#               # ant-clockwise arc
#               arc_direction = 1
#
#           # get arc radius and centre point from three coordinates across the arc
#           radius, centre = get_barrier_centre_and_radius(
#               coordinates[element],  #   arc start coordinate
#               coordinates[element + 1],  #   arc end coordinate
#               coordinates[element + 2],  #   arc third coordinate
#               arc_direction,
#           )
#           entities.append(
#               Arc(
#                   coordinates[element],
#                   coordinates[element + 1],
#                   centre,
#                   radius,
#               )
#           )
#       # remove entities between start and end coordinates of each arc then insert into pocket
#       for count, element in enumerate(range(0, len(coordinates), 3)):
#           start_index = pocket.points.index(coordinates[element])
#           end_index = pocket.points.index(coordinates[element + 1])
#           if end_index == 0:
#               end_index = len(pocket.points)
#
#           # use index of start/end coordinates to remove pockets entities between them
#           for index in reversed(range(start_index, end_index)):
#               pocket.entities.pop(index)
#
#           pocket.insert_entity(start_index, entities[count])
#
#
#   def get_pocket_name(index):
#       """Return unique pocket name used in Motor-CAD.
#
#       Parameters
#       ----------
#       index : integer
#           Current pocket index
#
#       Returns
#       -------
#           string
#       """
#       if index == 0:
#           return "Rotor Pocket"
#       else:
#           return "Rotor Pocket_" + str(index)
#
#
#   pocket_number = 0
#   number_layers = mc.get_variable("Magnet_Layers")
#
#   for layer in range(number_layers):
#       # get U-Shape layer parameters
#       outer_thickness = mc.get_array_variable("UShape_Thickness_Outer_Array", layer)
#       outer_post_width = mc.get_array_variable("UShape_Post_Outer_Array", layer)
#       inner_thickness = mc.get_array_variable("UShape_Thickness_Inner_Array", layer)
#       inner_post_width = mc.get_array_variable("UShape_Post_Inner_Array", layer)
#       centre_post_width = mc.get_array_variable("UShape_CentrePost_Array", layer)
#
#       if (inner_thickness == 0) or (outer_thickness == 0):
#           message_string = (
#               "Unable to create curved barrier for layer "
#               + str(layer)
#               + ". No inner/outer thickness."
#           )
#           raise Exception(message_string)
#       elif (outer_post_width > 0) or (inner_post_width > 0):
#           message_string = (
#               "Unable to create curved barrier for layer "
#               + str(layer)
#               + ". Inner/Outer post width > 0"
#           )
#           raise Exception(message_string)
#
#       # get pocket from Motor-CAD using unique name
#       pocket_left = mc.get_region(get_pocket_name(pocket_number))
#
#       if centre_post_width == 0:
#           # no centre post, single rotor pocket in layer
#           new_coordinates = get_coordinates_no_centre_post(pocket_left)
#       else:
#           # centre post, two pockets per layer
#           new_coordinates = get_coordinates_centre_post(pocket_left)
#
#       update_pocket_geometry(pocket_left, new_coordinates)
#       # increment pocket number to get next pocket from Motor-CAD
#       pocket_number += 1
#
#       if pocket_left.is_closed():
#           # set region back into Motor-CAD
#           mc.set_region(pocket_left)
#
#       if centre_post_width > 0:
#           # mirror left barrier/pocket region across the rotor using mirror line
#           pocket_right = pocket_left.mirror(get_rotor_mirror_line(), unique_name=False)
#           pocket_right.name = get_pocket_name(pocket_number)
#           # increment pocket number to get next pocket from Motor-CAD
#           pocket_number += 1
#
#           if pocket_right.is_closed():
#               # set region back into Motor-CAD
#               mc.set_region(pocket_right)

# %%
# Improve model performance with adaptive template
# -------------------------------------------------
# The Adaptive Script that was loaded and run has changed
# the geometry of the rotor pocket regions to become curved.
#
# Alter the model to improve the model performance using the Adaptive
# Templates script. Ratio-based parameterisation will be used.
#
# Set geometry parameterisation to ratio-based
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("GeometryParameterisation", 1)

# %%
# Set rotor geometry parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Units for the Bridge Thickness, Inner Thickness and Outer Thickness are in mm.
# U Magnet Web Thickness, U Magnet Diameter are ratios.
#
# Set geometry parameters for layer 1:

mc.set_array_variable("UShape_BridgeThickness_Array", 0, 0.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 0, 3.5)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 0, 0.14)
mc.set_array_variable("RatioArray_UMagnetDiameter", 0, 0.3)

# %%
# Set geometry parameters for layer 2:

mc.set_array_variable("UShape_BridgeThickness_Array", 1, 0.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 1, 3.0)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 1, 0.15)
mc.set_array_variable("RatioArray_UMagnetDiameter", 1, 0.35)

# %%
# Set geometry parameters for layer 3:

mc.set_array_variable("UShape_BridgeThickness_Array", 2, 0.5)
mc.set_array_variable("UShape_Thickness_Outer_Array", 2, 1.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 2, 2.5)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 2, 0.2)
mc.set_array_variable("RatioArray_UMagnetDiameter", 2, 0.5)

# %%
# Set geometry parameters for layer 4:

mc.set_array_variable("UShape_BridgeThickness_Array", 3, 0.5)
mc.set_array_variable("UShape_Thickness_Outer_Array", 3, 1.0)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 3, 0.35)
mc.set_array_variable("RatioArray_UMagnetDiameter", 3, 0.8)

# %%
# Set corner rounding for rotor pockets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enable the option to include corner rounding
# by setting the following to 'Single definition for all':

mc.set_variable("CornerRounding_Rotor", 1)

# %%
# Set the Rotor Lamination Corner Radius (units are mm):

mc.set_variable("CornerRoundingRadius_Rotor", 0.8)

# %%
# The curved flux barriers have now been set up
# for this Synchronous Reluctance Machine example.

# %%
# Display the example design geometry
# ------------------------------------
# Take a screenshot of the geometry that was set up using
# adaptive templates and save to the working directory.
#
# Screenshot the geometry
# ~~~~~~~~~~~~~~~~~~~~~~~

mc.initialise_tab_names()
mc.save_screen_to_file("Radial", os.path.join(working_folder, "Radial_Geometry_Screenshot.png"))

# %%
# Load, process and display the image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load the saved image

img = mpimg.imread(os.path.join(working_folder, "Radial_Geometry_Screenshot.png"))

# %%
# Crop the image to focus on the rotor geometry that was customised using
# adaptive templates

img_cropped = img[56:341, 250:535, :]

# %%
# Display the cropped image

imgplot = plt.imshow(img_cropped)
plt.axis("off")
plt.show()

# %%
# The customised rotor geometry is shown for this Synchronous Reluctance Machine
# example. The flux barriers have been curved using the imported script,
# and the rotor pocket parameters were adjusted to improve the model.
