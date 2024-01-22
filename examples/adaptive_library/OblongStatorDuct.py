# %%

import math

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, Line, rt_to_xy, xy_to_rt

# from ansys.motorcad.core.geometry_drawing import draw_regions

# %%
# Import the ``geometry`` library. This is used to create Adaptive Templates.


# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~

mc = pymotorcad.MotorCAD(open_new_instance=False)

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("MessageDisplayState", 2)


def check_line_origin_distance(i, duct_region):
    # There are two lines of the rectangular duct which needs to be converted into Arcs
    # the center of arc will be inside the region, hence need to check if the line is
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

    x = math.dist(start_point_xy, end_point_xy)  # chord length/2
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

# Note: script will  only work with user defined  rectangular ducts
# rectangular ducts will be converted to oblong
# input parameter from the user with be height of the Arc

duct_layers = mc.get_variable("CircularDuctLayers")
st_region = mc.get_region("stator")  # get the stator region
duct_height = mc.get_variable("CircularDuctL1ChannelHeight")
duct_width = mc.get_variable("CircularDuctL1ChannelWidth")
duct_area = duct_height * duct_width
duct_arc_height = mc.get_adaptive_parameter_value("Duct Arc Height")
# duct_arc_height=1.5
# mc.set_adaptive_parameter_value("Duct Arc Height",duct_arc_height)

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
        # collide function check incomplete

        # print(duct_region.collides(mc.get_region("ArmatureSlotL1")))

        # draw_regions(duct_region)
        mc.set_region(duct_region)
        # draw_regions(duct_region)
        # elif round(mc.get_region(child_name).area/duct_area,2)==0.5: # half duct


# %%
# draw_regions( mc.get_region("StatorDuctFluidRegion"))
# %%
