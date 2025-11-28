# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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
Square Stator IPM motor
=======================
This script applies the adaptive templates functionality to modify the stator into a square shape.
"""
# %%
# The modified stator is a square of width and height equal to the original round stator diameter.
# To adjust the size, change the **Stator Lam Dia** standard template parameter value. The square
# corners are filleted by a distance defined by a new adaptive parameter (**Square fillet**).
# .. note::
#    This example modifies the symmetry of the stator region. By default, Motor-CAD standard
#    template geometry uses 1 stator region per slot. This example modifies the symmetry so that
#    the model geometry has 4 stator regions, each spanning a quarter of the machine. This means
#    that the **Symmetry** setting under **Model Size** on the
#    **Input Data -> Settings -> Calculation** tab in Motor-CAD must be set to **Full Non-Symmetry**
#    for the FEA calculation to solve.
#
# .. note::
#    This example modifies the stator back iron so that it is larger than the original round stator.
#    This means that the **Air region boundary** setting under **Surrounding Air Region** on the
#    **Input Data -> Settings -> Calculation** tab in Motor-CAD must be set to **Circle** and the
#    **Circle Diameter** should be set to at least **300 mm** for the FEA calculation to solve. This
#    is to ensure that the stator is surrounded by air when the FEA calculation is solved. In this
#    example, if the **Square fillet** is 0 mm and the **Stator Lam Dia** is kept at the default
#    198 mm, the outermost point of the stator is at a radius of around 140 mm. Therefore, the
#    surrounding air **Circle Diameter** must be more than 280 mm.
#
# .. image:: ../../images/adaptive_templates/square_stator_surrounding_air.png
#     :width: 600pt


# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD. Import ``Coordinate``, ``Line`` and ``RegionType`` from
# ``ansys.motorcad.core.geometry`` to create the necessary geometry objects. Import ``draw_objects``
# to plot figures of geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

from copy import deepcopy

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/square_stator_4.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, Line, RegionType
from ansys.motorcad.core.geometry_drawing import draw_objects

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur:
#
# * open a new Motor-CAD instance,
#
# * load the e10 SPM motor template,
#
# * set the **Symmetry** setting under **Model Size** to **Full Non-Symmetry**
#   (**Input Data -> Settings -> Calculation** tab),
#
# * set the **Air region boundary** setting under **Surrounding Air Region** to **Circle**
#   (**Input Data -> Settings -> Calculation** tab),
#
# * set the **Circle Diameter** to **300 mm**,
#
# * set the **Housing** type to **Square**,
#
# * save the file to a temporary folder.
# To keep a new Motor-CAD instance open after executing the script, use the
# ``MotorCAD(keep_instance_open=True)`` option when opening the new instance. Alternatively, use the
# ``MotorCAD()`` method, which closes the Motor-CAD instance after the script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    if not "PYMOTORCAD_DOCS_BUILD" in os.environ:
        mc.set_visible(True)
    mc.load_template("e10")
    mc.set_variable("MagneticSymmetry", 3)  # set Full Non-Symmetry
    mc.set_variable("SurroundingAirRegion_Boundary", 1)  # set Square Housing
    mc.set_variable("SurroundingAirRegion_CircleDiameter", 300)  # set Square Housing
    mc.set_variable("HousingType", 1)  # set Square Housing

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "e10_square_stator"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Define necessary functions
# --------------------------
# Define a function to modify a region by filleting corners. Shorten entities that are adjacent to
# the corner by a specified distance, and insert a new line between the shortened entities.
def fillet(region, corner, distance):
    if distance < 0.1:
        return
    new_entity_start = None
    new_entity_end = None
    new_entity_index = None
    i = 0
    for entity in region.entities:
        if entity.end == corner:
            new_entity_end = entity.get_coordinate_from_distance(entity.end, distance=distance)
            entity.end = new_entity_end
        elif entity.start == corner:
            new_entity_start = entity.get_coordinate_from_distance(entity.start, distance=distance)
            entity.start = new_entity_start
            new_entity_index = i
        i += 1
    if new_entity_start and new_entity_end:
        new_line = Line(new_entity_end, new_entity_start)
        region.insert_entity(new_entity_index, new_line)


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the required standard template objects and the adaptive parameter values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required ``Square fillet`` parameters
# if undefined. This will be used to define the distance to fillet the square stator corners by.
mc.set_adaptive_parameter_default("Square fillet", 25)
fillet_distance = mc.get_adaptive_parameter_value("Square fillet")

# %%
# Get the geometry tree. Use the ``get_regions_of_type`` method to get the original stator region.
gt = mc.get_geometry_tree()
stator = gt.get_regions_of_type(RegionType.stator)[0]

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# To change the stator from a circular shape to a square, the symmetry must be modified. The e10
# template has 48 slots, and the round stator has 48-fold symmetry. The Motor-CAD standard template
# geometry is generated based on a stator region which is duplicated 48 times to build the circular
# stator.

# %%
# .. image:: ../../images/adaptive_templates/square_stator_1.png
#     :width: 600pt

# %%
# A square stator has 4-fold symmetry, so the adaptive templates geometry needs to be
# generated based on a stator region which is duplicated 4 times.

# %%
# .. image:: ../../images/adaptive_templates/square_stator_2.png
#     :width: 600pt

# Remove the outer arc and upper boundary of the original stator. These are the first and second
# entities in the list. Use the ``draw_objects`` function to visualise the change.
draw_objects(stator, draw_points=True)
orig_entities_to_remove = [stator.entities[0], stator.entities[1]]
for entity in orig_entities_to_remove:
    stator.remove_entity(entity)
draw_objects(stator.entities)

# %%
# The original stator has a single slot, but the square stator needs to have a quarter of the stator
# slots (12 for a 48 pole machine). Generate the extra slots by copying the original stator slot
# entities and rotating them around the origin.
#
# The lower boundary line is the only remaining entity that should not be copied and rotated. It is
# the last entity in the entity list. Append the other entities to a list.
lower_boundary_line = stator.entities[-1]
entities_to_copy_and_rotate = []
for entity in stator.entities:
    if entity != lower_boundary_line:
        entities_to_copy_and_rotate.append(entity)

# %%
# For each slot to be added to the stator (11 times for a 48-slot stator), use ``deep_copy`` to
# create copies of the entities. The entities must be in anti-clockwise order going around the
# region, so the ``entities_to_copy_and_rotate`` list is reversed.
#
# Rotate entities around the origin (centre of the motor) by the appropriate angle.
#
# Append the copied entities to a list. The first entity in the list is closest to the lower
# boundary line (at 0°). The last entity in the list is closest to the upper boundary line.
copied_entities = []
for i in range(int((stator.duplications / 4) - 1)):
    for entity in reversed(entities_to_copy_and_rotate):
        copied_entity = deepcopy(entity)
        copied_entity.rotate(Coordinate(0, 0), ((i + 1) * 360) / stator.duplications)
        copied_entities.append(copied_entity)

# %%
# Draw the slot entities to check that the new entities have been correctly defined.
to_draw = entities_to_copy_and_rotate
to_draw.extend(copied_entities)
draw_objects(to_draw)

# %%
# Insert the new entities to the stator region. Insert each entity at index 0 to ensure the
# anti-clockwise ordering.
for i in range(len(copied_entities)):
    stator.insert_entity(0, copied_entities[i])

# %%
# Create the new upper boundary line of the stator region. Create a copy of the lower boundary line,
# reverse and rotate it around the origin. Insert the new upper boundary line to the stator region
# at index 0.
#
# These lines determine the width and height of the new square stator. The width and height are
# equal to the original round stator diameter. To adjust the size, change the **Stator Lam Dia**
# standard template parameter value.
upper_boundary_line = deepcopy(lower_boundary_line)
upper_boundary_line.reverse()
upper_boundary_line.rotate(Coordinate(0, 0), 360 / 4)
stator.insert_entity(0, upper_boundary_line)

# %%
# Draw the stator entities.
draw_objects(stator.entities)

# %%
# The only missing entities are the square stator outer edges. The corner is at the same
# x-coordinate as the lower boundary line (the last entity) end point and the same y-coordinate as
# the upper boundary line (the first entity) start point. Create the new vertical and horizontal
# lines (edges of the square stator) using the corner coordinate and the boundary line start and end
# points. Insert the new horizontal line as the first entity, and add the vertical entity as the
# last entity in the stator region entity list.

corner_point = Coordinate(stator.entities[-1].end.x, stator.entities[0].start.y)
new_line_vert = Line(stator.entities[-1].end, corner_point)
new_line_horiz = Line(corner_point, stator.entities[0].start)
stator.insert_entity(0, new_line_horiz)
stator.add_entity(new_line_vert)

# %%
# Use the ``fillet`` function to fillet the corner of the square. Use the adaptive parameter value
# ``fillet_distance`` to define the distance to shorten the adjacent sides of the square region by.
fillet(stator, corner_point, fillet_distance)

# %%
# Set the number of stator duplications to 4 from the original 48.
stator.duplications = 4

# %%
# Use the ``subtract`` method to subtract the new square stator region from the original housing, to
# update the cut-out shape in the housing.
housing = gt.get_regions_of_type(RegionType.housing)[0]

draw_objects([stator, housing])

housing.subtract(stator)

draw_objects([stator, housing])

# %% Set the modified geometry tree in Motor-CAD.
mc.set_geometry_tree(gt)

# %%
# Draw the updated geometry tree.
draw_objects(gt)

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
