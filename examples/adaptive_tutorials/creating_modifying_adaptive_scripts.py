"""
.. _ref_creating_adaptive_scripts:

Creating and Modifying Adaptive Scripts
==============================================
This example describes how to create and modify Adaptive Templates scripts.
Adaptive Templates scripts are loaded into Motor-CAD to set up custom geometry templates.
Adaptive Template Scripts should be created outside Motor-CAD,
using a Python Integrated Development Environment (IDE) (such as PyCharm).
Using an IDE allows for faster creation of the script,
allowing access to autocompletion, code correction
and other features which are not available in the Motor-CAD scripting interface.

This is essential when writing complex scripts, allowing issues with the script to be fixed
and the inspection of Python objects (for example geometry regions from Motor-CAD).
"""

# %%
# For more information on the Synchronous Reluctance machine geometry with curved flux barriers
# used for this example, please see :ref:`ref_adaptive_templates_example_2`
# and :ref:`ref_SYNC_Curve_Flux_Barriers`.
#
# Set up example
# --------------
# Setting up this example consists of performing imports,
# specifying the working directory, launching Motor-CAD,
# and disabling all popup messages from Motor-CAD.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~

import os
from pathlib import Path
import shutil
import tempfile

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# Import the ``geometry`` library. This is used to create Adaptive Templates.

from ansys.motorcad.core.geometry import Arc, Coordinate, Line, rt_to_xy, xy_to_rt
from ansys.motorcad.core.geometry_drawing import draw_regions

# %%
# Import the ``geometry_drawing`` library to use the geometry drawing feature


# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~

mc = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("MessageDisplayState", 2)

# %%
# Open relevant file
# ~~~~~~~~~~~~~~~~~~
# Specify the working directory and open the relevant Synchronous Reluctance machine
# template file for this example (i3).

working_folder = Path(tempfile.gettempdir()) / "adaptive_example"
try:
    shutil.rmtree(working_folder)
except:
    pass
mc.load_template("i3")
mot_name = "Adaptive_Templates_Example_2"
Path.mkdir(working_folder)
mc.save_to_file(working_folder / (mot_name + ".mot"))

# %%
# Working on the adaptive templates example
# -----------------------------------------
# Work on the synchronous reluctance machine example motor
# with curved flux barriers using adaptive templates
# (:ref:`ref_adaptive_templates_example_2`).
#
# Adaptive templates should be disabled when working on a script
# from an external IDE.
# This allows the IDE to access the Standard Template Geometry.
# Set the Geometry Templates Type to Standard (from Adaptive)

mc.set_variable("GeometryTemplateType", 0)

# %%
# Instead of loading a script into Motor-CAD,
# as done in the :ref:`ref_adaptive_templates_example_2` example,
# the following script is run externally.
# The following script is very similar to that in the
# :ref:`ref_adaptive_templates_example_2` example,
# but uses the geometry drawing feature to plot the geometry regions.
#
# Adaptive_Templates_Example_2_Debug.py script
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Adaptive Templates script to alter SYNCREL U-Shape rotor template to use curved rotor pockets.
# This script does not support:
# Zero inner/outer layer thickness
# Inner/outer posts


def get_barrier_centre_and_radius(coordinate_1, coordinate_2, coordinate_3, arc_direction):
    """Calculate barrier arc centre and radius coordinates.

    Parameters
    ----------
    coordinate_1 : Coordinate
        Arc start coordinate.

    coordinate_2 : Coordinate
        Extra coordinate on arc

    coordinate_3 : Coordinate
        Arc end coordinate

    arc_direction : Integer
        Direction to create arc between start/end

    Returns
    -------
    radius : float
        Arc radius

    centre : Coordinate
        Arc centre coordinate
    """
    _, start_t = xy_to_rt(coordinate_1.x, coordinate_1.y)
    _, end_t = xy_to_rt(coordinate_3.x, coordinate_3.y)

    a = (
        coordinate_1.x * (coordinate_2.y - coordinate_3.y)
        - coordinate_1.y * (coordinate_2.x - coordinate_3.x)
        + coordinate_2.x * coordinate_3.y
        - coordinate_3.x * coordinate_2.y
    )
    b = (
        (coordinate_1.x**2 + coordinate_1.y**2) * (coordinate_3.y - coordinate_2.y)
        + (coordinate_2.x**2 + coordinate_2.y**2) * (coordinate_1.y - coordinate_3.y)
        + (coordinate_3.x**2 + coordinate_3.y**2) * (coordinate_2.y - coordinate_1.y)
    )
    c = (
        (coordinate_1.x**2 + coordinate_1.y**2) * (coordinate_2.x - coordinate_3.x)
        + (coordinate_2.x**2 + coordinate_2.y**2) * (coordinate_3.x - coordinate_1.x)
        + (coordinate_3.x**2 + coordinate_3.y**2) * (coordinate_1.x - coordinate_2.x)
    )
    centre = Coordinate((-b / a) / 2, (-c / a) / 2)
    radius = Line(centre, coordinate_1).length * arc_direction

    return radius, centre


def get_pockets_include_corner_rounding():
    """Whether corner rounding should be applied to pocket.

    Returns
    -------
        boolean
    """
    return (mc.get_variable("CornerRounding_Rotor") == 1) and (
        mc.get_variable("CornerRoundingRadius_Rotor") > 0
    )


def get_rotor_mirror_line():
    """Create mirror line through rotor from origin to airgap.

    Returns
    -------
        Line
    """
    rotor_radius = mc.get_variable("RotorDiameter")
    number_poles = mc.get_variable("Pole_Number")
    airgap_centre_x, airgap_centre_y = rt_to_xy(rotor_radius, (360 / number_poles) / 2)

    return Line(Coordinate(0, 0), Coordinate(airgap_centre_x, airgap_centre_y))


def get_coordinates(pocket, coordinate_indices, mirror_line=None):
    """Get list of coordinates from pocket using coordinate_indices.
    Coordinates ordered : start, end, extra coordinate on arc.

    Parameters
    ----------
    pocket : Region
        Pocket region

    coordinate_indices : list of integer
        Pocket region coordinate indices

    mirror_line : Line
        Mirror line to generate extra coordinate on arc

    Returns
    -------
        list of Coordinate
    """
    coordinates = [pocket.points[index] for index in coordinate_indices]
    if mirror_line is not None:
        coordinates.append(coordinates[0].mirror(mirror_line))

    return coordinates


def get_coordinates_no_centre_post(pocket):
    """Get list of coordinates to use to generate top and bottom arcs for pocket.
    Coordinates ordered : start, end, extra coordinate for each arc.

    Returns
    -------
        list of Coordinate
    """
    if get_pockets_include_corner_rounding():
        return get_coordinates(pocket, [2, 8, 5, 11, 17, 14])
    else:
        return get_coordinates(pocket, [1, 5, 3, 6, 0, 8])


def get_coordinates_centre_post(pocket):
    """Get list of coordinates to use to generate top and bottom arcs for pocket.
    Coordinates ordered : start, end, extra coordinate for each arc.

    Parameters
    ----------
    pocket : Region
        Pocket region

    Returns
    -------
        list of Coordinate
    """
    mirror = get_rotor_mirror_line()
    if get_pockets_include_corner_rounding():
        return get_coordinates(pocket, [2, 5], mirror) + get_coordinates(
            pocket, [8, 11], mirror_line=mirror
        )
    else:
        return get_coordinates(pocket, [1, 3], mirror) + get_coordinates(
            pocket, [4, 0], mirror_line=mirror
        )


def update_pocket_geometry(pocket, coordinates):
    """Update the pocket entities to create curved pocket using input coordinates.

    Parameters
    ----------
    pocket : Region
        Pocket region

    coordinates : list of Coordinate
        Coordinates to generate arcs with in region
    """
    entities = []
    # create list of arc entities from coordinates
    for element in range(0, len(coordinates), 3):
        if (element + 1) % 2 == 0:
            # clockwise arc
            arc_direction = -1
        else:
            # ant-clockwise arc
            arc_direction = 1

        # get arc radius and centre point from three coordinates across the arc
        radius, centre = get_barrier_centre_and_radius(
            coordinates[element],  # arc start coordinate
            coordinates[element + 1],  # arc end coordinate
            coordinates[element + 2],  # arc third coordinate
            arc_direction,
        )
        entities.append(
            Arc(
                coordinates[element],
                coordinates[element + 1],
                centre,
                radius,
            )
        )
    # remove entities between start and end coordinates of each arc then insert into pocket
    for count, element in enumerate(range(0, len(coordinates), 3)):
        start_index = pocket.points.index(coordinates[element])
        end_index = pocket.points.index(coordinates[element + 1])
        if end_index == 0:
            end_index = len(pocket.points)

        # use index of start/end coordinates to remove pockets entities between them
        for index in reversed(range(start_index, end_index)):
            pocket.entities.pop(index)

        pocket.insert_entity(start_index, entities[count])


def get_pocket_name(index):
    """Return unique pocket name used in Motor-CAD.

    Parameters
    ----------
    index : integer
        Current pocket index

    Returns
    -------
        string
    """
    if index == 0:
        return "Rotor Pocket"
    else:
        return "Rotor Pocket_" + str(index)


pocket_number = 0
number_layers = mc.get_variable("Magnet_Layers")

pockets_all_layers = []

for layer in range(number_layers):
    pockets_single_layer = []

    # get U-Shape layer parameters
    outer_thickness = mc.get_array_variable("UShape_Thickness_Outer_Array", layer)
    outer_post_width = mc.get_array_variable("UShape_Post_Outer_Array", layer)
    inner_thickness = mc.get_array_variable("UShape_Thickness_Inner_Array", layer)
    inner_post_width = mc.get_array_variable("UShape_Post_Inner_Array", layer)
    centre_post_width = mc.get_array_variable("UShape_CentrePost_Array", layer)

    if (inner_thickness == 0) or (outer_thickness == 0):
        message_string = (
            "Unable to create curved barrier for layer "
            + str(layer)
            + ". No inner/outer thickness."
        )
        raise Exception(message_string)
    elif (outer_post_width > 0) or (inner_post_width > 0):
        message_string = (
            "Unable to create curved barrier for layer "
            + str(layer)
            + ". Inner/Outer post width > 0"
        )
        raise Exception(message_string)

    # get pocket from Motor-CAD using unique name
    pocket_left = mc.get_region(get_pocket_name(pocket_number))

    if centre_post_width == 0:
        # no centre post, single rotor pocket in layer
        new_coordinates = get_coordinates_no_centre_post(pocket_left)
    else:
        # centre post, two pockets per layer
        new_coordinates = get_coordinates_centre_post(pocket_left)

    update_pocket_geometry(pocket_left, new_coordinates)
    # increment pocket number to get next pocket from Motor-CAD
    pocket_number += 1

    if pocket_left.is_closed():
        # set region back into Motor-CAD
        mc.set_region(pocket_left)
        # add pocket to layer list for drawing
        pockets_single_layer.append(pocket_left)

    if centre_post_width > 0:
        # mirror left barrier/pocket region across the rotor using mirror line
        pocket_right = pocket_left.mirror(get_rotor_mirror_line(), unique_name=False)
        pocket_right.name = get_pocket_name(pocket_number)
        # increment pocket number to get next pocket from Motor-CAD
        pocket_number += 1

        if pocket_right.is_closed():
            # set region back into Motor-CAD
            mc.set_region(pocket_right)
            # add pocket to layer list for drawing
            pockets_single_layer.append(pocket_left)

    # add pocket regions in this layer to all layers list
    pockets_all_layers = pockets_all_layers + pockets_single_layer

    # draw all pockets in layer
    draw_regions(pockets_single_layer)

# draw all regions
draw_regions(pockets_all_layers)
