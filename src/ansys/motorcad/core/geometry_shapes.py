"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from math import cos, radians, sin, sqrt

from ansys.motorcad.core.geometry import Coordinate, EntityList, Line, Region, rt_to_xy


def square(width, r_O, th_O):
    """Create a square of given width at a given set of coordinates.

    Parameters
    ----------
    width : float
        Width value.
    r_O : float
        Radial coordinate of the square centre.
    th_O : float
        Angular coordinate of the square centre.

    Returns
    -------
    this_square : ansys.motorcad.core.geometry.Region
        List of four Line entity types.
    """
    x_O, y_O = rt_to_xy(r_O, th_O)

    # calculate half diagonal span of square
    Hyp = sqrt(2) * (width / 2)
    Opp = Hyp * sin(radians(th_O + 45))
    Adj = Hyp * cos(radians(th_O + 45))

    # A
    x_A = x_O - Opp
    y_A = y_O + Adj
    p_A = Coordinate(x_A, y_A)

    # B
    x_B = x_O + Adj
    y_B = y_O + Opp
    p_B = Coordinate(x_B, y_B)

    # C
    x_C = x_O + Opp
    y_C = y_O - Adj
    p_C = Coordinate(x_C, y_C)

    # D
    x_D = x_O - Adj
    y_D = y_O - Opp
    p_D = Coordinate(x_D, y_D)

    # Generate lines
    line_AD = Line(p_A, p_D)
    line_DC = Line(p_D, p_C)
    line_CB = Line(p_C, p_B)
    line_BA = Line(p_B, p_A)

    this_square = Region()
    this_square.entities = EntityList([line_AD, line_DC, line_CB, line_BA])

    return this_square


def eq_triangle_h(height, r_O, th_O):
    """Create an equilateral triangle of given height at a given set of coordinates.

    Parameters
    ----------
    height : float
        Height value.
    r_O : float
        Radial coordinate of the triangle centre.
    th_O : float
        Angular coordinate of the triangle centre.

    Returns
    -------
    this_triangle : list of entities
        List of four Line entity types.
    """
    x_O, y_O = rt_to_xy(r_O, th_O)

    # calculate necessary distances for calculating point coordinates
    h_a = 2 * height / 3
    adj_a = h_a * cos(radians(30 + th_O))
    opp_a = h_a * sin(radians(30 + th_O))
    adj_b = h_a * cos(radians(th_O))
    opp_b = h_a ** sin(radians(th_O))

    # A
    x_A = x_O - h_a * sin(radians(30 + th_O))
    y_A = y_O + h_a * cos(radians(30 + th_O))
    p_A = Coordinate(x_A, y_A)

    # B
    x_B = x_O + h_a * cos(radians(th_O))
    y_B = y_O + h_a * sin(radians(th_O))
    p_B = Coordinate(x_B, y_B)

    # C
    x_C = x_O - h_a * sin(radians(30 - th_O))
    y_C = y_O - h_a * cos(radians(30 - th_O))
    p_C = Coordinate(x_C, y_C)

    # Generate lines
    line_AC = Line(p_A, p_C)
    line_CB = Line(p_C, p_B)
    line_BA = Line(p_B, p_A)

    this_triangle = Region()
    this_triangle.entities = EntityList([line_AC, line_CB, line_BA])

    return this_triangle


def eq_triangle_w(width, r_O, th_O):
    """Create an equilateral triangle of given width at a given set of coordinates.

    Parameters
    ----------
    width : float
        Width value.
    r_O : float
        Radial coordinate of the triangle centre.
    th_O : float
        Angular coordinate of the triangle centre.

    Returns
    -------
    this_triangle : list of entities
        List of four Line entity types.
    """
    height = sqrt(3) * width / 2
    this_triangle = eq_triangle_h(height, r_O, th_O)

    return this_triangle
