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

"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from math import cos, radians, sin, sqrt

from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, Region, rt_to_xy


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
        Region type with four Line entity types.
    """
    x_A, y_A, x_B, y_B, x_C, y_C, x_D, y_D = _square_coordinates(width, r_O, th_O)

    p_A = Coordinate(x_A, y_A)
    p_B = Coordinate(x_B, y_B)
    p_C = Coordinate(x_C, y_C)
    p_D = Coordinate(x_D, y_D)

    # Generate lines
    line_AD = Line(p_A, p_D)
    line_DC = Line(p_D, p_C)
    line_CB = Line(p_C, p_B)
    line_BA = Line(p_B, p_A)

    this_square = Region()
    this_square.entities = EntityList([line_AD, line_DC, line_CB, line_BA])

    return this_square


def _square_coordinates(width, r_O, th_O):
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
    x_A : float
        X coordinate value for square vertex A.
    y_A : float
        Y coordinate value for square vertex A.
    x_B : float
        X coordinate value for square vertex B.
    y_B : float
        Y coordinate value for square vertex B.
    x_C : float
        X coordinate value for square vertex C.
    y_C : float
        Y coordinate value for square vertex C.
    x_D : float
        X coordinate value for square vertex D.
    y_D : float
        Y coordinate value for square vertex D.
    """
    x_O, y_O = rt_to_xy(r_O, th_O)

    # calculate half diagonal span of square
    Hyp = sqrt(2) * (width / 2)
    Opp = Hyp * sin(radians(th_O + 45))
    Adj = Hyp * cos(radians(th_O + 45))

    # A
    x_A = x_O - Opp
    y_A = y_O + Adj

    # B
    x_B = x_O + Adj
    y_B = y_O + Opp

    # C
    x_C = x_O + Opp
    y_C = y_O - Adj

    # D
    x_D = x_O - Adj
    y_D = y_O - Opp

    return x_A, y_A, x_B, y_B, x_C, y_C, x_D, y_D


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
    this_triangle : ansys.motorcad.core.geometry.Region
        Region type with three Line entity types.
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
    this_triangle : ansys.motorcad.core.geometry.Region
        Region type with three Line entity types.
    """
    height = sqrt(3) * width / 2
    this_triangle = eq_triangle_h(height, r_O, th_O)

    return this_triangle


def triangular_notch(radius, sweep, centre_angle, depth):
    """Create a triangular notch for a rotor or stator at given angular position with given size.

    Parameters
    ----------
    radius : float
        Radius value, radius of the Rotor or Stator for which the notch is being defined.
    sweep : float
        Sweep value, the angular distance (in degrees) that the notch spans.
    centre_angle : float
        Angle value, angular coordinate of the notch centre.
    depth : float
        Depth value, depth of the notch.

    Returns
    -------
    this_triangular_notch : ansys.motorcad.core.geometry.Region
        Region type with two Line and one Arc entity types.
    """
    # calculate necessary angles for the coordinate calculation
    rotor_centre = Coordinate(0, 0)
    notch_start_angle = centre_angle - sweep / 2
    notch_end_angle = centre_angle + sweep / 2

    # generate coordinates for triangular notch using start/mid/end
    # angles above converting from polar to cartesian
    x1, y1 = rt_to_xy(radius, notch_start_angle)
    x2, y2 = rt_to_xy(radius - depth, centre_angle)
    x3, y3 = rt_to_xy(radius, notch_end_angle)

    p1 = Coordinate(x1, y1)
    p2 = Coordinate(x2, y2)
    p3 = Coordinate(x3, y3)

    # using coordinate create entities making up notch region
    line_1 = Line(p3, p2)
    line_2 = Line(p2, p1)
    airgap_arc = Arc(p1, p3, rotor_centre, radius)

    # create the triangular notch region and add the 2 lines and 1 arc to the region
    this_triangular_notch = Region()
    this_triangular_notch.entities = EntityList([line_1, line_2, airgap_arc])

    return this_triangular_notch
