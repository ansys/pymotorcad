"""
Trapezoidal ducts
==============================================
Adaptive Templates script to alter rectangular ducts to trapezoidal ducts.
"""
# %%
# Perform required imports
# ------------------------
# Import pymotorcad to access Motor-CAD.
# Import Arc, Coordinate, Line, Region and rt_to_xy
# to define the adaptive template geometry.
# Import os, tempfile and shutil
# to open and save a temporary .mot file if none is open.
import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Coordinate, rt_to_xy, xy_to_rt

# %%

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.set_variable("RotorDuctType", 4)  # selected rectangular ducts
    mc.set_array_variable("RotorCircularDuctLayer_ChannelWidth", 0, 4)  # set duct width

    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "Trapezoidal_duct"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()


# %%
def set_default_parameter(parameter_name, default_value):
    try:
        mc.get_adaptive_parameter_value(parameter_name)
    except pymotorcad.MotorCADError:
        mc.set_adaptive_parameter_value(parameter_name, default_value)


# %%
# Use the ``set_default_parameter`` to set the required parameters if undefined
set_default_parameter("Trapezoid_base_ratio", 0.7)


# %%
# read the regions and draw if needed to debug
rt_region = mc.get_region("Rotor")  # get the rotor region


# %%
def check_line_origin_distance(i, duct_region):
    # There are two lines of the rectangle whose length is equal to width
    # only top line needs to be modified , hence need to check if the line is
    # closer to origin or not
    # index i is line index under investigation and index j is of other line
    # if radius of midpoint of i line is lower than j line , line i is closer is origin
    if i == 0:  # first index of rectangle duct
        j = 1
    elif i == 3:  # last index of rectangle duct
        j = 2
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
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~
mc.set_variable("MessageDisplayState", 2)

## parameters for trapezoid

Trap_ratio = mc.get_adaptive_parameter_value(
    "Trapezoid_base_ratio"
)  # ratio of top width / base width

Trap_W = mc.get_array_variable(
    "RotorCircularDuctLayer_ChannelWidth",
    0,
)
Trap_H = mc.get_array_variable(
    "RotorCircularDuctLayer_ChannelHeight",
    0,
)

# %%
duct_area = Trap_H * Trap_W
for child_name in rt_region.child_names:
    if "RotorDuctFluidRegion" in child_name:
        duct_region = mc.get_region(child_name)
        if round(duct_region.area / duct_area, 2) == 1:  # check if  full duct is drawn
            for i, entity in enumerate(duct_region.entities):
                if round(entity.length / Trap_W, 2) == 1:  # check if  the line is width
                    # additional check in case width = height
                    r_statrt_point, angle_start_point = xy_to_rt(entity.start.x, entity.start.y)
                    r_end_point, angle_end_point = xy_to_rt(entity.end.x, entity.end.y)
                    if abs(angle_end_point - angle_start_point) > 0.05:  # 0.05 degree is tolerance
                        # check if the line located at top or bottom
                        Line_origin = check_line_origin_distance(i, duct_region)
                        if Line_origin == False:
                            del_trap_angle = (
                                (angle_end_point - angle_start_point) * (1 - Trap_ratio) / 2
                            )
                            new_angle_start_point = angle_start_point + del_trap_angle
                            new_angle_end_point = angle_end_point - del_trap_angle
                            new_start_x, new_start_y = rt_to_xy(
                                r_statrt_point, new_angle_start_point
                            )
                            new_end_x, new_end_y = rt_to_xy(r_end_point, new_angle_end_point)
                            new_start_point = Coordinate(new_start_x, new_start_y)
                            new_end_point = Coordinate(new_end_x, new_end_y)
                            duct_region.edit_point(entity.start, new_start_point)
                            duct_region.edit_point(entity.end, new_end_point)
                            print("entity added")
                            mc.set_region(duct_region)

        elif round(duct_region.area / duct_area, 2) == 0.5:  # half duct
            Symm_angle = 360 / duct_region.duplications  # angle of symmetry

            for i, entity in enumerate(duct_region.entities):
                if round(entity.length / Trap_W, 2) == 0.5:  # check if  the line is width
                    # additional check in case width = height
                    r_statrt_point, angle_start_point = xy_to_rt(entity.start.x, entity.start.y)
                    r_end_point, angle_end_point = xy_to_rt(entity.end.x, entity.end.y)
                    if abs(angle_end_point - angle_start_point) > 0.05:  # 0.05 degree is tolerance
                        Line_origin = check_line_origin_distance(i, duct_region)
                        if Line_origin == False:
                            del_trap_angle = (angle_end_point - angle_start_point) * (
                                1 - Trap_ratio
                            )
                            if (
                                angle_start_point - 0 < 1e-10
                                or angle_start_point == 0
                                or round(angle_start_point / Symm_angle, 2) == 1
                            ):  # on symmetry plane
                                new_angle_end_point = angle_end_point - del_trap_angle
                                new_end_x, new_end_y = rt_to_xy(r_end_point, new_angle_end_point)
                                new_end_point = Coordinate(new_end_x, new_end_y)
                                duct_region.edit_point(entity.end, new_end_point)
                            elif (
                                angle_end_point - 0 < 1e-10
                                or round(angle_end_point / Symm_angle, 2) == 1
                            ):  # symmetry plan
                                new_angle_start_point = angle_start_point + del_trap_angle
                                new_start_x, new_start_y = rt_to_xy(
                                    r_statrt_point, new_angle_start_point
                                )
                                new_start_point = Coordinate(new_start_x, new_start_y)
                                duct_region.edit_point(entity.start, new_start_point)

                            print("entity added")
                            mc.set_region(duct_region)


if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
