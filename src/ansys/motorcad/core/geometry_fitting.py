from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from math import dist, sqrt


def orientation(c1, c2, c3):
    """find the orientation of three coordinates

     Parameters
     ----------
     c1: ansys.motorcad.core.geometry.Coordinate
     c2: ansys.motorcad.core.geometry.Coordinate
     c3: ansys.motorcad.core.geometry.Coordinate

     Returns
     -------
     int
     """

    # to find the orientation of three coordinates
    val = (float(c2.y - c1.y) * (c3.x - c2.x)) - \
          (float(c2.x - c1.x) * (c3.y - c2.y))
    if val > 0:
        # Clockwise orientation
        return 1
    elif val < 0:
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0


def coordinates_to_arc(c1, c2, c3):
    """Takes three coordinates and converts to an arc

    Parameters
    ----------
     c1: ansys.motorcad.core.geometry.Coordinate
     c2: ansys.motorcad.core.geometry.Coordinate
     c3: ansys.motorcad.core.geometry.Coordinate

    Returns
    -------
    ansys.motorcad.core.geometry.Arc
    """

    mid_x1 = (c1.x + c2.x) / 2
    mid_y1 = (c1.y + c2.y) / 2

    # avoid divide by zero errors in case of vertical lines
    if (c2.x - c1.x) == 0:
        slope1 = 0
    else:
        slope1 = (c2.y - c1.y) / (c2.x - c1.x)

    if (c3.x - c2.x) == 0:
        slope2 = 0
    else:
        slope2 = (c3.y - c2.y) / (c3.x - c2.x)

    mid_x2 = (c2.x + c3.x) / 2
    mid_y2 = (c2.y + c3.y) / 2

    if slope1 != 0 and slope2 != 0 and slope1 != slope2:

        perpendicular_slope_1 = -1 / slope1
        perpendicular_slope_2 = -1 / slope2

        x_intersect = (mid_y1 - mid_y2 + perpendicular_slope_2 * mid_x2 - perpendicular_slope_1 * mid_x1) / (
                perpendicular_slope_2 - perpendicular_slope_1)
        y_intersect = perpendicular_slope_1 * (x_intersect - mid_x1) + mid_y1

    elif slope1 == slope2:
        # lines are parallel so no point of intersection
        return None

    elif slope1 == 0 and slope2 == 0 or slope1 == slope2:
        # three points are on a straight line, no arc is possible
        return None

    elif slope1 == 0:
        # if line 1 is either vertical or horizontal
        if (c2.x - c1.x) == 0:
            y_intersect = mid_y1
            perpendicular_slope_2 = -1 / slope2
            x_intersect = ((y_intersect - mid_y2) / perpendicular_slope_2) + mid_x2
        else:
            x_intersect = mid_x1
            perpendicular_slope_2 = -1 / slope2
            y_intersect = perpendicular_slope_2 * (x_intersect - mid_x2) + mid_y2

    elif slope2 == 0:
        # if line 2 is either vertical or horizontal
        if (c3.x - c2.x) == 0:
            y_intersect = mid_y2
            perpendicular_slope_1 = -1 / slope1
            x_intersect = ((y_intersect - mid_y1) / perpendicular_slope_1) + mid_x1
        else:
            x_intersect = mid_x2
            perpendicular_slope_1 = -1 / slope1
            y_intersect = perpendicular_slope_1 * (x_intersect - mid_x1) + mid_y1

    radius = dist([c1.x, c1.y], [x_intersect, y_intersect])

    coord_centre = Coordinate(x_intersect, y_intersect)

    arc_out = Arc(c1, c3, coord_centre, radius)

    return arc_out


def check_line_error(c_xy, slope, b, tolerance):
    """

    Parameters
    ----------
    c_xy: List
        List of coordinates of type ansys.motorcad.core.geometry.Coordinate
    slope: float
        slope of line equation
    b: float
        b from line equation y=mx+b
    tolerance: float
        allowed variation of points from line

    Returns
    -------
    boolean
    """
    error_flag = False

    for xy in c_xy:
        y_calc = slope * xy.x + b
        y_array = abs(xy.y - y_calc)
        if y_array > tolerance:
            error_flag = True

    return error_flag


def check_arc_error(c_xy, c_x0y0, radius, tolerance):
    """

    Parameters
    ----------
    c_xy: List
        List of coordinates of type ansys.motorcad.core.geometry.Coordinate
    c_x0y0: ansys.motorcad.core.geometry.Coordinate
        Coordinate representing arc centre
    radius: float
        Radius of arc
    tolerance: float
        allowed variation of points from arc

    Returns
    -------
    boolean
    """
    error_flag = False

    for i in range(len(c_xy)):
        radius_calculated = sqrt((c_xy[i].x - c_x0y0.x) ** 2 + (c_xy[i].y - c_x0y0.y) ** 2)

        radius_error = abs(radius - radius_calculated)

        if radius_error > tolerance:
            error_flag = True

    return error_flag


def return_entity_list(xy_points, line_tolerance, arc_tolerance):
    """

    Parameters
    ----------
    xy_points: List
            List of coordinates of type ansys.motorcad.core.geometry.Coordinate
    line_tolerance: float
            Maximum allowed variation of line entity from original points
    arc_tolerance: float
            Maximum allowed variation of arc entities from original points

    Returns
    -------
        List
        List of Line/Arc class objects representing entities.
    """
    # xy_points is a list of ordered co-ordinates

    new_entity_list = []
    current_index = 0
    xy_dynamic_list = xy_points.copy()

    while len(xy_dynamic_list) > 2:
        # future work need to consider sharp angle case where two separate line entities
        # are required to represent 3 points this could potentially be handled by a maximum arc angle limit
        line_segments = 1
        arc_segments = 1
        arc_entity_complete = False
        line_entity_complete = False

        while line_entity_complete is False:
            line_segments = line_segments + 1

            # loops through extending line until the tolerance is reached
            if len(xy_dynamic_list) >= line_segments + 1:
                start_point = xy_points[current_index]
                end_point = xy_points[current_index + line_segments]

                line_master = Line(start_point, end_point)
                slope = line_master.gradient
                b = start_point.y - slope * start_point.x
                line_entity_complete = check_line_error(xy_points[current_index:current_index + line_segments + 1],
                                                        slope, b, line_tolerance)
            else:
                line_entity_complete = True

        if line_entity_complete:
            line_segments = line_segments - 1

        while arc_entity_complete is False:
            # loops through extending the arc until the tolerance is reached
            arc_segments = arc_segments + 1

            if len(xy_dynamic_list) >= arc_segments + 1:
                start_point = xy_points[current_index]
                end_point = xy_points[current_index + arc_segments]
                mid_point = xy_points[current_index + round(arc_segments / 2)]

                arc_master = coordinates_to_arc(start_point, mid_point, end_point)

                if arc_master is None:
                    arc_entity_complete = True
                else:
                    arc_entity_complete = check_arc_error(xy_points[current_index:current_index + arc_segments + 1],
                                                          arc_master.centre, arc_master.radius, arc_tolerance)

            else:
                arc_entity_complete = True

        if arc_entity_complete:
            arc_segments = arc_segments - 1

        if line_segments >= arc_segments:
            end_index = current_index + line_segments
            new_entity_list.append(Line(xy_points[current_index], xy_points[end_index]))

            for p in range(end_index - current_index):
                xy_dynamic_list.pop(0)

        else:
            # need to recalculate arc here as last arc calculated in loop is outside error bounds and 1 segment too long
            end_index = current_index + arc_segments
            mid_point = round(arc_segments / 2)

            arc_complete = coordinates_to_arc(xy_points[current_index], xy_points[current_index + mid_point],
                                              xy_points[end_index])

            direction = orientation(xy_points[current_index], xy_points[current_index + mid_point],
                                    xy_points[end_index])

            if direction == 1:

                # flip start and end points if direction is clockwise
                add_arc = Arc(arc_complete.end, arc_complete.start, arc_complete.centre, arc_complete.radius)
                new_entity_list.append(add_arc)

                for p in range(end_index - current_index):
                    xy_dynamic_list.pop(0)

            else:
                new_entity_list.append(arc_complete)

                for p in range(end_index - current_index):
                    xy_dynamic_list.pop(0)

        current_index = end_index

    # handling end of list where remaining items less than 3 co-ordinates

    if len(xy_dynamic_list) == 2:
        new_entity_list.append(Line(xy_dynamic_list[0], xy_dynamic_list[1]))

        for p in range(2):
            xy_dynamic_list.pop(0)

    elif len(xy_dynamic_list) == 1:
        xy_dynamic_list.pop(0)

    return new_entity_list


def coordinates_equal(c1, c2):
    """

    Parameters
    ----------
    c1: ansys.motorcad.core.geometry.Coordinate
    c2: ansys.motorcad.core.geometry.Coordinate

    Returns
    -------
    bool
    """
    if (c1.x == c2.x) and (c1.y == c2.y):
        equal = True
    else:
        equal = False

    return equal
