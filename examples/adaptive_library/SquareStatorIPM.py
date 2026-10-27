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
Square Stator IPM motor
=======================
This script applies the adaptive templates functionality to modify the stator into a square shape.
"""
# %%
# The modified stator is a square of width and height equal to the original round stator diameter.
# To adjust the size, change the **Stator Lam Dia** standard template parameter value. The square
# corners are chamfered by a distance defined by a new adaptive parameter (**Square chamfer**).
#
# .. note::
#    This example requires Motor-CAD v2026R1 or later. Motor-CAD v2027R1 introduces the ability to
#    take advantage of the model symmetry to speed up calculations.
#
# .. note::
#    This example modifies the symmetry of the stator region. By default, Motor-CAD standard
#    template geometry uses 1 stator region per slot. This example modifies the symmetry so that
#    the model geometry has 4 stator regions, each spanning a quarter of the machine.
#
#    * When using Motor-CAD v2026R1, the **Symmetry** setting under **Model Size** on the
#      **Input Data -> Settings -> Calculation** tab in Motor-CAD must be set to
#      **Full Non-Symmetry** for the FEA calculation to solve.
#
#    * When using Motor-CAD v2027R1 or later, the **Symmetry** setting under **Model Size** on the
#      **Input Data -> Settings -> Calculation** tab in Motor-CAD can be set to
#      **User Specified symmetry**, with:
#
#      * **Symmetry factor** = **4**
#
#      * **Slot/Pole Symmetry** set to **Multiple**
#
#      * **Stator Duplications** = **12**
#
#      to take advantage of the machine symmetry and speed up the FEA calculations.
#
# .. note::
#    This example modifies the stator back iron so that it is larger than the original round stator.
#    This means that the **Air region boundary** setting under **Surrounding Air Region** on the
#    **Input Data -> Settings -> Calculation** tab in Motor-CAD must be set to **Circle** and the
#    **Circle Diameter** should be set to at least **300 mm** for the FEA calculation to solve. This
#    is to ensure that the stator is surrounded by air when the FEA calculation is solved. In this
#    example, if the **Square chamfer** is 0 mm and the **Stator Lam Dia** is kept at the default
#    198 mm, the outermost point of the stator is at a radius of around 140 mm. Therefore, the
#    surrounding air **Circle Diameter** must be more than 280 mm.
#
# .. image:: ../../images/adaptive_templates/square_stator_surrounding_air.png
#     :width: 300pt
#     :align: center


# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD. Import ``RegionType``, ``EntityList``, ``Coordinate``,
# ``Line`` and  ``Arc`` from ``ansys.motorcad.core.geometry`` to create the necessary geometry
# objects. Import ``draw_objects`` to plot figures of geometry objects.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/adaptive_templates/square_stator_4.png'
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, RegionType
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
# * load the e10 IPM motor template,
#
# * with a try/except block, check whether the **Slot/Pole Symmetry** variable is available
#   (Motor-CAD v2027R1 and later):
#
#   * if so:
#
#     * ensure that **Magnetic FEA Regions Method** is set to **Improved**,
#
#     * set **Symmetry** to **User Specified symmetry**,
#
#     * set **Symmetry factor** = **4**,
#
#     * set **Slot/Pole Symmetry** to **Multiple**,
#
#     * set the **Stator Duplications** = **12**,
#
#   * if not, set the **Symmetry** setting under **Model Size** to **Full Non-Symmetry**
#     (**Input Data -> Settings -> Calculation** tab),
#
# * set the **Air region boundary** setting under **Surrounding Air Region** to **Circle**
#   (**Input Data -> Settings -> Calculation** tab),
#
# * set the **Circle Diameter** to **300 mm** (**Input Data -> Settings -> Calculation** tab),
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
    try:
        mc.set_variable("MagneticSlotPoleSymmetryType", 1) # Set **Slot/Pole Symmetry** to **Multiple**
        mc.set_variable("MagneticFEARegionsMethod", 1)  # set Magnetic FEA Regions Method to Improved
        mc.set_variable("MagneticSymmetry", 2)  # set User Specified symmetry
        mc.set_variable("MagneticSymmetryFactor", 4)  # set Symmetry factor to 4
        mc.set_variable("MagneticFEADuplications_Stator", 12)  # set Stator Duplications to 12

    except pymotorcad.MotorCADError as e:
        if "Error in SetVariable: Could not find MagneticSlotPoleSymmetryType" in str(e):
            mc.set_variable("MagneticSymmetry", 3)  # set Full Non-Symmetry
        else:
            raise e

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
    mc.save_to_file(f"{working_folder}\\{mot_name}.mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the required standard template objects and the adaptive parameter values.
#
# Use the ``set_adaptive_parameter_default`` method to set the required ``Square chamfer``
# parameters if undefined. This will be used to define the distance to chamfer the square stator
# corners by.
mc.set_adaptive_parameter_default("Square chamfer", 25)
chamfer_distance = mc.get_adaptive_parameter_value("Square chamfer")

# %%
# Get the geometry tree. Use the ``get_regions_of_type`` method to get the original stator region.
# Get the Armature Slot, Wedge and Stator Air regions and store these in a ``stator_children``
# list.
gt = mc.get_geometry_tree()
stator_region = gt.get_regions_of_type(RegionType.stator)[0]

stator_children = []
stator_children.extend(gt.get_regions_of_type(RegionType.slot_split))
stator_children.extend(gt.get_regions_of_type(RegionType.wedge))
stator_children.extend(gt.get_regions_of_type(RegionType.stator_air))

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# To change the stator from a circular shape to a square, the symmetry must be modified. The e10
# template has 48 slots, and the round stator has 48-fold symmetry. The Motor-CAD standard template
# geometry is generated based on a stator region which is duplicated 48 times to build the circular
# stator.

# %%
# .. image:: ../../images/adaptive_templates/square_stator_1.png
#     :width: 800pt

# %%
# A square stator has 4-fold symmetry, so the adaptive templates geometry needs to be
# generated based on a stator region which is duplicated 4 times.

# %%
# .. image:: ../../images/adaptive_templates/square_stator_2.png
#     :width: 800pt
#
# Note that the square stator region images above do not have slots cut out. In this example, the
# subtraction of the slots from the stator is handled by setting the Armature Slot, Wedge and Stator
# Air regions as child regions of the Stator region.

# %%
# Make regions children of the Stator region
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# By default, the Armature Slot, Wedge and Stator Air regions are not children of the Stator region
# in the geometry tree. When regions are children of another regions, the subtraction of regions is
# automatically handled by Motor-CAD. Therefore, to ensure that the Armature Slot, Wedge and Stator
# Air regions are automatically subtracted from the new square Stator region, the parent of these
# regions must be set to the Stator region. This means that it is not necessary to manually rotate
# and duplicate the slot geometry and the Adaptive Templates script can be kept simple.
#
# .. image:: ../../images/adaptive_templates/square_stator_5.png
#
# Loop through the ``stator_children`` list of regions and set the parent of
# each region to be the Stator region.
for region in stator_children:
    region.parent = stator_region

# %%
# Create new square stator entities
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# To create the new square stator region geometry, create a new list of entities. The first entity
# is the lower boundary line of the stator region, which is the last entity in the original stator
# region entity list.
square_stator_entities = EntityList()
square_stator_entities.append(stator_region.entities[-1])

# %%
# Create a new upper boundary line by creating a copy of the lower boundary line and rotating it by
# 90 degrees around the origin. Add the new upper boundary line to the new square stator entity
# list and draw the lower and upper boundary lines.
square_stator_entities.append(Line(square_stator_entities[0].end, square_stator_entities[0].start))
square_stator_entities[1].rotate(Coordinate(0, 0), 90)

draw_objects(square_stator_entities)

# %%
# Create the lines that define the outer edges of the square stator. If the ``chamfer distance``
# adaptive parameter value is more than zero, shorten both lines by that value.
square_stator_entities.insert(
    1,
    Line(
        square_stator_entities[0].end,
        Coordinate(
            square_stator_entities[0].end.x, square_stator_entities[-1].start.y - chamfer_distance
        ),
    ),
)
square_stator_entities.insert(
    2,
    Line(
        Coordinate(
            square_stator_entities[0].end.x - chamfer_distance, square_stator_entities[-1].start.y
        ),
        square_stator_entities[-1].start,
    ),
)

# %%
# Insert the diagonal line to chamfer the corner of the square if the ``chamfer distance`` adaptive
# parameter value is more than zero. Draw updated list of square stator entities.

if chamfer_distance > 0:
    square_stator_entities.insert(
        2, Line(square_stator_entities[1].end, square_stator_entities[2].start)
    )

draw_objects(square_stator_entities)

# %%
# Add the inner arc to complete the list of square stator entities.
square_stator_entities.append(
    Arc(square_stator_entities[-1].end, square_stator_entities[0].start, centre=Coordinate(0, 0))
)

# %%
# Replace the Stator entities
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Replace the original EntityList of the Stator region with the new square stator EntityList. Set
# the duplication number of the Stator to the new symmetry factor (4) and draw the modified stator.
# The original duplication number of the Stator region was 48.
stator_region.entities = square_stator_entities
stator_region.duplications = 4

draw_objects(stator_region)

# %%
# Use the ``subtract`` method to subtract the new square stator region from the original housing, to
# update the cut-out shape in the housing.
housing = gt.get_regions_of_type(RegionType.housing)[0]

draw_objects([stator_region, housing])

housing.subtract(stator_region)

draw_objects([stator_region, housing])

# %%
# Set the modified geometry tree in Motor-CAD.
mc.set_geometry_tree(gt)

# %%
# Draw the updated geometry tree.
draw_objects(gt, legend=False, axes=False, full_geometry=True)

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
