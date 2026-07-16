# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Adjusting IPM Rotor Pocket Shape
================================
This script applies the adaptive templates functionality to modify the shape of IPM rotor pockets
by shifting the original vertices and applying corner rounding.
"""
# %%
# .. note::
#    This example uses Motor-CAD Geometry Tree functionality, introduced in v2026.1.1 (Motor-CAD
#    2026 R1) and PyMotorCAD v0.8.4 or later.
#
# The vertices that define the shape of the rotor pockets are shifted to new positions based on
# adaptive parameters, and a corner radius is applied to each corner.

# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Region``, ``RegionType``, ``Line``, ``Arc``, ``Coordinate``, ``rt_to_xy`` and
# ``EntityList`` for creating the adaptive templates geometry.
# Import ``draw_objects`` to plot figures of geometry objects.
# Import ``deepcopy`` to copy geometry objects.
# Import ``isclose`` to check similar numbers based on a tolerance.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

from copy import deepcopy
from math import isclose

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/asymmetric_SPM_thumbnail.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, RegionType, rt_to_xy
from ansys.motorcad.core.geometry_drawing import draw_objects

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: open a new Motor-CAD instance, load the e4a
# IPM motor template, disable corner rounding for the standard template geometry (rotor lamination
# and magnets) and save the file to a temporary folder. To keep a new Motor-CAD instance open after
# executing the script, use the ``MotorCAD(keep_instance_open=True)`` option when opening the new
# instance. Alternatively, use the ``MotorCAD()`` method with no arguments, which closes the
# Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e4a")
    mc.set_variable("CornerRounding_Rotor", 0)  # Disable Corner Rounding
    mc.set_variable("CornerRounding_Magnets", 0)

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e4a_IPM_Custom_Rotor_Pockets"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# Define required functions
# -------------------------
# Define a function to make the rotor pocket regions parent of the magnet regions in the geometry
# tree.
#
# Get the magnet and the rotor pocket regions from the geometry tree based on the ``RegionType``,
# then identify which magnet regions sit in each rotor pocket by trying to unite the regions. If
# a magnet is in contact with the rotor pocket, then they can be successfully united.
#
# Replace the rotor pocket region entities with those of the united rotor pocket and magnet region,
# which is the region that is cut out of the rotor lamination.
#
# Set each magnet region's parent to the rotor pocket region.
#
# If the regions do not touch, then the magnet does not sit in this rotor pocket and we can pass
# on to the next iteration of the magnet loop. Raise any other errors that may occur when trying to
# unite the regions.


def make_pockets_parents_of_magnet_regions(geometry_tree, mc_i):
    """Make pockets parents of magnet regions.

    Parameters
    ----------
    geometry_tree : ansys.motorcad.core.geometry.geometry_tree object

    mc_i : ansys.motorcad.core.MotorCAD object"""
    magnet_regions = geometry_tree.get_regions_of_type(region_type=RegionType.magnet)
    pocket_regions = geometry_tree.get_regions_of_type(region_type=RegionType.rotor_pocket)

    for pocket_region in pocket_regions:
        for magnet_region in magnet_regions:
            # Try to unite the rotor pocket and magnet regions
            try:
                united_region = mc.unite_regions(pocket_region, [magnet_region])

                # Unite the pocket and magnet to form full cut-out region by replacing the pocket's
                # entities with those of the united region.
                pocket_region.replace(united_region)

                # Set magnet region's parent to the rotor pocket region
                # print(f"Make {pocket.name} parent of {magnet.name}.")
                magnet_region.parent = pocket_region

            except pymotorcad.MotorCADError as e:
                if "regions do not touch" in str(e):
                    pass
                else:
                    raise e


# %%
# Define a function to check whether a region sits to the right of the mirror line, based on its
# centroid coordinate.
def region_below_mirror_line(region):
    mirror_line = Line(Coordinate(0, 0), Coordinate(*rt_to_xy(10000, region.duplication_angle / 2)))
    y_mirror_line = mirror_line.gradient * region.centroid.x + mirror_line.y_intercept
    if y_mirror_line > region.centroid.y:
        return True
    else:
        return False


# %%
# Define a function to return the magnet regions are children of a rotor pocket region.
def child_magnet_regions(rotor_pocket_region):
    child_magnet_regions = []
    # identify the magnet regions that sit in this rotor pocket
    for child in rotor_pocket_region.children:
        if child.region_type == RegionType.magnet:
            child_magnet_regions.append(child)
    return child_magnet_regions


# %%
# Get required parameters and objects
# -----------------------------------
# Get the standard template regions to be modified. This example works using the geometry tree
# functionality. Get the geometry tree.
gt = mc.get_geometry_tree()

# %%
# Use the ``make_pockets_parents_of_magnet_regions`` to make the rotor pocket regions parents of the
# magnet regions.
make_pockets_parents_of_magnet_regions(gt, mc)

# %%
# Get regions from the geometry tree.
rotor = gt["Rotor"]
rotor_pockets_unsorted = gt.get_regions_of_type(RegionType.rotor_pocket)

# %%
# Sort the rotor pockets into two lists. The first list contains rotor pockets that sit to the right
# of the mirror line (on one side of the rotor). The second list contains the rotor pockets that sit
# on the other side of the rotor. Get the magnet regions that sit within the rotor pockets using the
# ``Region.children`` method, and store the regions in lists using the same logic.
rotor_pockets = [[], []]
magnets = [[], []]
for rotor_pocket in rotor_pockets_unsorted:
    if region_below_mirror_line(rotor_pocket):
        n = 0
    else:
        n = 1
    rotor_pockets[n].append(rotor_pocket)
    pocket_magnets = []
    for region in rotor_pocket.children:
        if region.region_type == RegionType.magnet:
            pocket_magnets.append(region)
    magnets[n].append(pocket_magnets)

# %%
# Identify control points
# ~~~~~~~~~~~~~~~~~~~~~~~
# Define the control points that will be used to adjust the rotor pocket shape. The control points
# are the vertices of the rotor pocket regions, and can be shifted to define a new rotor pocket
# shape. A corner radius can be applied to each vertex.
#
# Define whether to also include the midpoints of the rotor pocket entities as points to be moved.
# if True, the midpoints of the rotor pocket entities will be included as control points. This
# increases the number of degrees of freedom for defining the new rotor pocket shape. The original
# entities will be split in half. If False, only the original rotor pocket vertices will be used as
# control points for defining the new rotor pocket shape.
include_midpoints = False

# %%
# Loop through the regions on one side of the rotor, then by IPM layer. The e4a template only has
# 1 magnet layer. To identify only the rotor pocket vertices, the magnet vertices are added to a
# list of forbidden points.
side = 0
layer = 0
forbidden_points = []

for rotor_pocket in rotor_pockets[side]:
    # identify the magnet regions that sit in this rotor pocket
    for magnet in child_magnet_regions(rotor_pocket):
        forbidden_points.extend(magnet.points)

# %%
# The long sides of the rotor pockets should remain unchanged. Identify the longest entities and
# add the start and end points of these to the forbidden points list.
#
# If the midpoints of the rotor pocket entities are also to be included as control points, split the
# original entities (not including the long sides).
for pocket in rotor_pockets[side]:
    len_max = 0
    # find length of longest entity in pocket
    entity_lengths = []
    for entity in pocket.entities:
        entity_lengths.append(entity.length)
    len_max = max(entity_lengths)
    # add the longest entity points to forbidden_points
    for entity in pocket.entities:
        if isclose(entity.length, len_max, abs_tol=0.01 * len_max):
            forbidden_points.extend([entity.start, entity.end])
    # optionally, increase the number of degrees of freedom by also including midpoints of the rotor
    # pockets. To do this, split the original pocket end entities in half.
    if include_midpoints:
        new_entities = EntityList()
        entities_to_replace = []
        entities_to_add = []
        for entity in pocket.entities:
            split_entity = False
            if entity.start not in forbidden_points:
                if entity.end not in forbidden_points:
                    split_entity = True
                    # if midpoints are to be included, split the original entities
                    if type(entity) == Line:
                        new_entities.append(Line(entity.start, entity.midpoint))
                        new_entities.append(Line(entity.midpoint, entity.end))
                    else:
                        new_entities.append(
                            Arc(
                                entity.start,
                                entity.midpoint,
                                centre=entity.centre,
                                radius=entity.radius,
                            )
                        )
                        new_entities.append(
                            Arc(
                                entity.midpoint,
                                entity.end,
                                centre=entity.centre,
                                radius=entity.radius,
                            )
                        )
            if not split_entity:
                new_entities.append(entity)
        pocket.entities = new_entities

# %%
# Loop through the rotor pockets and find the pocket vertices. These are the points that define the
# shape of the rotor pocket end.
#
# Group the points into sub-lists for each end of the rotor pocket.
points_to_edit_orig = []  # list of lists of points to be edited
i = 0
for pocket in rotor_pockets[side]:
    pocket_end_points = []  # list of consecutive points to be edited
    last_point = deepcopy(pocket.points)[-1]
    # Loop through rotor pocket points and add allowed points to a list.
    # Consecutive points are added to the points_to_edit_orig list in sub-lists. Points at one end
    # of the pocket will be in points_to_edit_orig[0] and points at the other end will be in
    # points_to_edit_orig[1].
    for point in deepcopy(pocket.points):
        # add pocket points to a list
        if point not in forbidden_points:
            pocket_end_points.append(point)
        else:
            # if the point is forbidden, and the previous point was allowed, then this is the end of
            # a list of consecutive allowed points. Append the previous list to the
            # points_to_edit_orig list and start a new list for the next group of consecutive
            # allowed points.
            if last_point not in forbidden_points:
                points_to_edit_orig.append(pocket_end_points)
                pocket_end_points = []
        last_point = point

    # if the first and last lists of consecutive allowed points are the same end of the pocket,
    # combine the lists. Check this by checking whether the first and last points of the pocket are
    # both allowed.
    if deepcopy(pocket.points)[0] not in forbidden_points:
        if deepcopy(pocket.points)[-1] not in forbidden_points:
            points_to_edit_orig[i] = pocket_end_points + points_to_edit_orig[i]
        else:
            points_to_edit_orig.append(pocket_end_points)
    else:
        points_to_edit_orig.append(pocket_end_points)
    i = len(points_to_edit_orig)

# %%
# Define adaptive parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the adaptive parameters that will be used to adjust the rotor pocket vertices. Each vertex
# will have three adaptive parameters: a radial shift, an angular direction and a corner radius.
#
# Define strings that will be used for the parameter names for each vertex.
adaptive_parameters_p_point = ["shift rad", "shift th", "corner radius"]

# %%
# If undefined, set up the adaptive parameters for each control point with default values of 0.
for i in range(len(rotor_pockets[side])):
    magnet = child_magnet_regions(rotor_pockets[side][i])[0]
    for j in range(2):
        for k in range(len(points_to_edit_orig[(2 * i) + j])):
            for parameter in adaptive_parameters_p_point:
                mc.set_adaptive_parameter_default(f"{magnet.name} end {j} point {k} {parameter}", 0)

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Loop through the rotor pockets on one side of the rotor

l = 0
for i in range(len(rotor_pockets[side])):
    pocket = rotor_pockets[side][i]
    magnet = child_magnet_regions(pocket)[0]

    # get magnet ends
    len_min = 10000
    entity_lengths = []
    magnet_ends = []
    for entity in magnet.entities:
        entity_lengths.append(entity.length)
    len_min = min(entity_lengths)
    for entity in magnet.entities:
        if isclose(entity.length, len_min, abs_tol=0.01 * len_min):
            magnet_ends.append(entity)
    for j in range(len(magnet_ends)):
        # to_draw = [rotor, rotor_pockets[side][i]]
        # to_draw.extend(points_to_edit_orig[(2*i)+j])
        # to_draw.extend([magnet_ends[j].start, magnet_ends[j].end])
        # draw_objects(to_draw)

        # transform the points into new coordinate system relative to the magnet end
        points_rel_to_magnet = []
        for point in points_to_edit_orig[(2 * i) + j]:
            point_rel_to_magnet = Coordinate(point.x, point.y)
            point_rel_to_magnet.rotate(magnet_ends[j].end, 180 - magnet_ends[j].angle)
            point_rel_to_magnet.translate(-magnet_ends[j].end.x, -magnet_ends[j].end.y)
            points_rel_to_magnet.append(point_rel_to_magnet)

        # move pocket points
        translated_points = []
        for k in range(len(points_rel_to_magnet)):
            point_shift = Coordinate(
                *rt_to_xy(
                    mc.get_adaptive_parameter_value(
                        f"{magnet.name} end {j} point {k} {adaptive_parameters_p_point[0]}"
                    ),
                    mc.get_adaptive_parameter_value(
                        f"{magnet.name} end {j} point {k} {adaptive_parameters_p_point[1]}"
                    ),
                )
            )
            if point_shift != Coordinate(0, 0):
                # shift the original points to get the translated points
                translated_point_x = points_rel_to_magnet[k].x + point_shift.x
                translated_point_y = points_rel_to_magnet[k].y + point_shift.y
                translated_point = Coordinate(translated_point_x, translated_point_y)
                # go back to original coordinate system
                translated_point.translate(magnet_ends[j].end.x, magnet_ends[j].end.y)
                translated_point.rotate(magnet_ends[j].end, -(180 - magnet_ends[j].angle))
                pocket.edit_point(points_to_edit_orig[(2 * i) + j][k], translated_point)
                translated_points.append(translated_point)
            else:
                translated_points.append(points_to_edit_orig[(2 * i) + j][k])

        # corner rounding
        for k in range(len(translated_points)):
            corner_radius = mc.get_adaptive_parameter_value(
                f"{magnet.name} end {j} point {k} {adaptive_parameters_p_point[2]}"
            )
            point = translated_points[k]
            pocket.round_corner(point, corner_radius)

    # mirror the modified pocket
    pocket_mirror = rotor_pockets[side + 1][i]
    poles = pocket_mirror.duplications
    mirror_line = Line(Coordinate(0, 0), Coordinate(*rt_to_xy(100, pocket.duplication_angle / 2)))
    mirrored_pocket_mod = pocket.mirror(mirror_line)
    pocket_mirror.replace(mirrored_pocket_mod)

# %%
# Set the modified geometry tree in Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the geometry tree and draw the geometry tree.
mc.set_geometry_tree(gt)

draw_objects(gt, full_geometry=True, axes=False)

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
