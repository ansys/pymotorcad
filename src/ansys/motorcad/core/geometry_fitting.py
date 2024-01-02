"""Unit containing functions for drawing geometry from a list of points"""

from enum import Enum
from math import sqrt

from ansys.motorcad.core.geometry import Arc, Line, EntityList


class Orientation(Enum):
    clockwise = 1
    anticlockwise = 2
    collinear = 0


def _orientation(c1, c2, c3):
    """Find the orientation of three coordinates, this can be clockwise, anticlockwise or collinear.

    Parameters
    ----------
    c1 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 1
    c2 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 2
    c3 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 3
    Returns
    -------
        Orientation
    """
    # To find the orientation of three coordinates
    val = (float(c2.y - c1.y) * (c3.x - c2.x)) - (float(c2.x - c1.x) * (c3.y - c2.y))
    if val > 0:
        # Clockwise orientation
        return Orientation.clockwise
    elif val < 0:
        # Anticlockwise orientation
        return Orientation.anticlockwise
    else:
        # Collinear orientation
        return Orientation.collinear

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
    xy_points: List of ansys.motorcad.core.geometry.Coordinate
            List of coordinates.
    line_tolerance: float
            Maximum allowed variation of line entity from original points.
    arc_tolerance: float
            Maximum allowed variation of arc entities from original points.

    Returns
    -------
        ansys.motorcad.core.geometry.EntityList
            List of Line/Arc class objects.
    """
    # xy_points is a list of ordered coordinates

    new_entity_list = EntityList()
    current_index = 0
    xy_dynamic_list = xy_points.copy()

    while len(xy_dynamic_list) > 2:
        # future work need to consider sharp angle case where two separate line entities
        # are required to represent 3 points this could potentially be handled by a maximum
        # arc angle limit
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
                line_entity_complete = check_line_error(
                    xy_points[current_index : current_index + line_segments + 1],
                    slope,
                    b,
                    line_tolerance,
                )
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

                arc_master = Arc.from_coordinates(start_point, mid_point, end_point)

                if arc_master is None:
                    arc_entity_complete = True
                else:
                    arc_entity_complete = check_arc_error(
                        xy_points[current_index : current_index + arc_segments + 1],
                        arc_master.centre,
                        arc_master.radius,
                        arc_tolerance,
                    )

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
            # need to recalculate arc here as last arc calculated in loop is outside error bounds
            # and 1 segment too long
            end_index = current_index + arc_segments
            mid_point = round(arc_segments / 2)

            arc_complete = Arc.from_coordinates(
                xy_points[current_index], xy_points[current_index + mid_point], xy_points[end_index]
            )

            direction = _orientation(
                xy_points[current_index], xy_points[current_index + mid_point], xy_points[end_index]
            )

            if direction == Orientation.clockwise:
                # flip start and end points if direction is clockwise
                add_arc = Arc(
                    arc_complete.end, arc_complete.start, arc_complete.centre, arc_complete.radius
                )
                new_entity_list.append(add_arc)

                for p in range(end_index - current_index):
                    xy_dynamic_list.pop(0)

            else:
                new_entity_list.append(arc_complete)

                for p in range(end_index - current_index):
                    xy_dynamic_list.pop(0)

        current_index = end_index

    # handling end of list where remaining items less than 3 coordinates

    if len(xy_dynamic_list) == 2:
        new_entity_list.append(Line(xy_dynamic_list[0], xy_dynamic_list[1]))

        for p in range(2):
            xy_dynamic_list.pop(0)

    elif len(xy_dynamic_list) == 1:
        xy_dynamic_list.pop(0)

    return new_entity_list
