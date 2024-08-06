"""
Oblong ducts
=================
This script applies the adaptive templates functionality to modify rectangular ducts
into oblong ducts.
"""
# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Arc``, ``Line``, ``Coordinate``, ``rt_to_xy``, ``xy_to_rt``, ``math`` 
# to define the adaptive template geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_number = -1
import os
import shutil
import sys
import tempfile
import math

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Line, Coordinate, rt_to_xy, xy_to_rt

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e9 IPM motor template is loaded and set up with rectangular stator ducts, and the file is
# saved to a temporary folder. To keep a new Motor-CAD instance open after executing the script, use
# the ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e9")
    mc.set_variable("StatorDuctType", 4)  # selected rectangular ducts
    mc.set_variable("CircularDuctLayers", 1)  # set number of duct layers
    mc.set_variable("CircularDuctL1RadialDiameter", 180)  # set number of duct radial diameter
    mc.set_variable("CircularDuctL1ChannelWidth", 2)  # set duct width
    mc.set_variable("CircularDuctL1ChannelHeight", 3)  # set duct height

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "Oblong_duct"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
# Define necessary functions
# --------------------------
# Set adaptive parameter if required
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The ``set_default_parameter`` function is defined to check if a parameter exists. If not,
# it creates the parameter with a default value.
def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Check line distance from origin
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The rectangle consists of two lines of length equal to the rectangle width.
# Only the top  and bottom lines requires modification.
# It is necessary to check whether the line is closest to the origin. As this will affect the center
# of arcs needs to convert the lines. Index ``i`` is
# the line under investigation. Index ``j`` is the adjacent line. If the radius of midpoint of line
# ``i`` is less than that of line ``j`` , line ``i`` is closer to the origin.


def check_line_origin_distance(i, duct_region):
    if i == 0:  # first index of rectangle duct
        j = 1
    else:
        j = i - 1
    rad_start_i, _ = xy_to_rt(duct_region.entities[i].start.x, duct_region.entities[i].start.y)
    rad_end_i, _ = xy_to_rt(duct_region.entities[i].end.x, duct_region.entities[i].end.y)
    rad_mid_i = (rad_start_i + rad_end_i) / 2
    rad_start_j, _ = xy_to_rt(duct_region.entities[j].start.x, duct_region.entities[j].start.y)
    rad_end_j, _ = xy_to_rt(duct_region.entities[j].end.x, duct_region.entities[j].end.y)
    rad_mid_j = (rad_start_j + rad_end_j) / 2
    if rad_mid_i < rad_mid_j:
        return True
    else:
        return False

# %%
# Generate arc associated with oblong duct
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Two separate functions are needed depending  on full duct or half duct (due to symmetry) 
def get_arc_radius_center(entity_start, entity_end, height, Line_origin):
    # Generate arc radius and center based on
    # line and arc height
    start_point_xy = [entity_start.x, entity_start.y]
    end_point_xy = [entity_end.x, entity_end.y]
    x = math.dist(start_point_xy, end_point_xy) / 2  # chord length/2
    y = height
    # conversion to polar coordinates
    start_point_r, start_point_t = xy_to_rt(entity_start.x, entity_start.y)
    end_point_r, end_piont_t = xy_to_rt(entity_end.x, entity_end.y)
    r = (x**2 + y**2) / (2 * y)  # radius
    if Line_origin == True:
        center_r = (start_point_r + end_point_r) / 2 + (r - y)
    else:
        center_r = (start_point_r + end_point_r) / 2 - (r - y)
    center_t = (start_point_t + end_piont_t) / 2
    center_x, center_y = rt_to_xy(center_r, center_t)
    center = Coordinate(center_x, center_y)  # center point
    return r, center


def get_arc_radius_center_halfduct(entity_start, entity_end, height, Line_origin, Symm_angle):
    # Generate arc radius, center, start and  end point based on for half duct
    # line and arc height
    start_point_xy = [entity_start.x, entity_start.y]
    end_point_xy = [entity_end.x, entity_end.y]

    x = math.dist(start_point_xy, end_point_xy)  # chord length
    y = height
    start_point_r, start_point_t = xy_to_rt(entity_start.x, entity_start.y)
    end_point_r, end_piont_t = xy_to_rt(entity_end.x, entity_end.y)
    r = (x**2 + y**2) / (2 * y)  # radius
    if Line_origin == True:
        # line is closer to origin
        center_r = (start_point_r + end_point_r) / 2 + (r - y)
        if start_point_t == 0 or round(start_point_t / Symm_angle, 2) == 1:
            # start point is on symmetry boundary of geometry
            center_t = start_point_t
            new_start_x, new_start_y = rt_to_xy(start_point_r - height, start_point_t)
            new_end_x, new_end_y = entity_end.x, entity_end.y
        elif end_piont_t == 0 or round(end_piont_t / Symm_angle, 2) == 1:
            # end  point is on symmetry boundary of geometry
            center_t = end_piont_t
            new_start_x, new_start_y = entity_start.x, entity_start.y
            new_end_x, new_end_y = rt_to_xy(end_point_r - height, end_piont_t)
    else:
        # Line is far from origin
        center_r = (start_point_r + end_point_r) / 2 - (r - y)
        if start_point_t == 0 or round(start_point_t / Symm_angle, 2) == 1:
            # start point is on symmetry boundary of geometry
            center_t = start_point_t
            new_start_x, new_start_y = rt_to_xy(start_point_r + height, start_point_t)
            new_end_x, new_end_y = entity_end.x, entity_end.y
        elif end_piont_t == 0 or round(end_piont_t / Symm_angle, 2) == 1:
            # end point is on symmetry boundary of geometry
            center_t = end_piont_t
            new_start_x, new_start_y = entity_start.x, entity_start.y
            new_end_x, new_end_y = rt_to_xy(end_point_r + height, end_piont_t)

    center_x, center_y = rt_to_xy(center_r, center_t)
    center = Coordinate(center_x, center_y)  # center point
    new_start_point = Coordinate(new_start_x, new_start_y)
    new_end_point = Coordinate(new_end_x, new_end_y)
    return r, center, new_start_point, new_end_point
# %%
# Get required parameters and objects
# -----------------------------------
# From Motor-CAD, get the adaptive parameters and their values.
#
# Use the ``set_default_parameter()`` method to set the required ``Duct Arc Height`` parameter
# if undefined.
set_default_parameter("Duct Arc Height", 0.7)


# %%
# Set required parameters for the oblong: height of arc ``Duct Arc Height``, duct width and duct height.
duct_arc_height = mc.get_adaptive_parameter_value("Duct Arc Height")
duct_height = mc.get_variable("CircularDuctL1ChannelHeight")
duct_width = mc.get_variable("CircularDuctL1ChannelWidth")
duct_area = duct_height * duct_width

# %%
# Get the standard template stator region. This can be drawn for debugging if required.
st_region = mc.get_region("stator")  # get the stator region

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# For each child region of the stator region:
#
# * Check whether the region is a stator duct.
#
# * Find the top and bottom lines that makes up the duct.
#
# * Modify the lines with respective arcs.
#
# * Set the region in Motor-CAD.
#
# The script accounts for whether ducts are full ducts or half ducts (the case when a duct spans the
# rotor pole boundary)

for child_name in st_region.child_names:
    if "StatorDuctFluidRegion" in child_name:
        duct_region = mc.get_region(child_name)
        if round(duct_region.area / duct_area, 2) == 1:  # check if  full duct is drawn
            for i, entity in enumerate(duct_region.entities):
                if round(entity.length / duct_width, 2) == 1:  # check if the line is duct width
                    # additional check in case width = height
                    _, angle_start_point_angle = xy_to_rt(entity.start.x, entity.start.y)
                    _, angle_end_point_angle = xy_to_rt(entity.end.x, entity.end.y)
                    if (
                        abs(angle_end_point_angle - angle_start_point_angle) > 0.05
                    ):  # 0.05 degree is tolerance
                        # get radius and center
                        # convert this line segment to Arc
                        Line_origin = check_line_origin_distance(
                            i, duct_region
                        )  # line near of far from origin
                        radius, center = get_arc_radius_center(
                            entity.start, entity.end, duct_arc_height, Line_origin
                        )
                        Duct_Arc = Arc(entity.start, entity.end, center, radius)
                        print("entity added")
                        duct_region.entities[i] = Duct_Arc

        elif round(duct_region.area / duct_area, 2) == 0.5:  # if the half duct is drawn
            Symm_angle = 360 / duct_region.duplications  # angle of symmetry
            for i, entity in enumerate(duct_region.entities):
                if (
                    round(entity.length / duct_width, 2) == 0.5
                ):  # check if  the line is half duct width
                    # additional check in case width/2 = height
                    _, angle_start_point_angle = xy_to_rt(entity.start.x, entity.start.y)
                    _, angle_end_point_angle = xy_to_rt(entity.end.x, entity.end.y)
                    if (
                        abs(angle_end_point_angle - angle_start_point_angle) > 0.05
                    ):  # 0.05 degree is tolerance
                        # get radius and center
                        # convert this line segment to Arc
                        Line_origin = check_line_origin_distance(i, duct_region)
                        radius, center, start_point, end_point = get_arc_radius_center_halfduct(
                            entity.start, entity.end, duct_arc_height, Line_origin, Symm_angle
                        )
                        Duct_Arc = Arc(start_point, end_point, center, radius)
                        print("entity added")
                        duct_region.entities[i] = Duct_Arc
                elif round(entity.length / duct_height, 2) == 1:
                    # modify the line on symmetry planes
                    rad_start_point, angle_start_point = xy_to_rt(entity.start.x, entity.start.y)
                    rad_end_point, angle_end_point = xy_to_rt(entity.end.x, entity.end.y)
                    if angle_start_point == 0 and angle_end_point == 0:
                        # line located at x=0
                        entity.start.x = entity.start.x - duct_arc_height
                        entity.end.x = entity.end.x + duct_arc_height
                    elif (
                        round(angle_start_point / Symm_angle, 2) == 1
                        and round(angle_end_point / Symm_angle, 2) == 1
                    ):
                        # line on symmetry plane
                        # start and end point follow anticlockwise naming convention
                        rad_start_point = rad_start_point + duct_arc_height
                        rad_end_point = rad_end_point - duct_arc_height
                        new_start_x, new_start_y = rt_to_xy(rad_start_point, angle_start_point)
                        new_end_x, new_end_y = rt_to_xy(rad_end_point, angle_end_point)
                        start_point = Coordinate(new_start_x, new_start_y)
                        end_point = Coordinate(new_end_x, new_end_y)
                        print("entity added")
                        duct_region.entities[i] = Line(start_point, end_point)
 

        mc.set_region(duct_region)

# %%
# .. image:: ../../images/OblongDuct.png
#     :width: 300pt

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