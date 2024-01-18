"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from math import cos, radians, sin, sqrt

from ansys.motorcad.core.geometry import (
    Arc,
    Coordinate,
    EntityList,
    Line,
    Region,
    rt_to_xy,
    xy_to_rt,
)


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

    r_A, th_A = xy_to_rt(x_A, y_A)
    r_B, th_B = xy_to_rt(x_B, y_B)
    r_C, th_C = xy_to_rt(x_C, y_C)
    r_D, th_D = xy_to_rt(x_D, y_D)

    # Check none cross lower boundary
    lower_angles = [th_D, th_C]
    shift_angle = 0
    for th in lower_angles:
        if th < 0:
            if abs(th) > shift_angle:
                shift_angle = abs(th)
    duplication_angle = 45
    # Check none cross upper boundary
    upper_angles = [th_A, th_B]
    for th in upper_angles:
        if th > duplication_angle:
            if (th - duplication_angle) > abs(shift_angle):
                shift_angle = -abs(th - duplication_angle)

    if shift_angle != 0:
        print(
            "Square coordinate not valid: square rotated by "
            + str(shift_angle)
            + " mechanical degrees."
        )
        th_O_new = th_O + shift_angle
        x_A, y_A, x_B, y_B, x_C, y_C, x_D, y_D = _square_coordinates(width, r_O, th_O_new)

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


def square_2(width, r_O, th_O):
    """NOT FINISHED - TRYING TO MODIFY square() to move points across rotor boundaries.

    Create a square of given width at a given set of coordinates.

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
    x_A, y_A, x_B, y_B, x_C, y_C, x_D, y_D = _square_coordinates(width, r_O, th_O)

    r_A, th_A = xy_to_rt(x_A, y_A)
    r_B, th_B = xy_to_rt(x_B, y_B)
    r_C, th_C = xy_to_rt(x_C, y_C)
    r_D, th_D = xy_to_rt(x_D, y_D)

    # Check none cross lower boundary
    coordinate_angles = [th_A, th_B, th_C, th_D]
    duplication_angle = 45
    change_coordinates = False
    n = 0
    for th in coordinate_angles:
        if th < 0:
            print("square coordinate crosses lower boundary")
            th_new = th + duplication_angle
            coordinate_angles[n] = th_new
            change_coordinates = True
        n = n + 1

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

    if change_coordinates:
        x_A, y_A = rt_to_xy(r_A, coordinate_angles[0])
        x_B, y_B = rt_to_xy(r_B, coordinate_angles[1])
        x_C, y_C = rt_to_xy(r_C, coordinate_angles[2])
        x_D, y_D = rt_to_xy(r_D, coordinate_angles[3])

        p_A = Coordinate(x_A, y_A)
        p_B = Coordinate(x_B, y_B)
        p_C = Coordinate(x_C, y_C)
        p_D = Coordinate(x_D, y_D)

        # Lower Boundary
        if coordinate_angles[3] != th_D:
            # if D is out of bounds but A is not
            if coordinate_angles[0] == th_A:
                # find the point on boundary
                c = line_AD.y_intercept
                m = line_AD.gradient
                # r = 2*c/(sqrt(2)*(1-m))
                r = c / (sin(radians(0)) - m * cos(radians(0)))
                x_L, y_L = rt_to_xy(r, 0)
                x_U, y_U = rt_to_xy(r, duplication_angle)
                p_DL = Coordinate(x_L, y_L)
                p_DU = Coordinate(x_U, y_U)
                line_AD_L = Line(p_DL, p_A)
                line_AD_U = Line(p_D, p_DU)
                this_square.add_entity(line_AD_L)
                # this_square.add_entity(line_AD_U)
            # if D and A are out of bounds
            else:
                line_AD = Line(p_D, p_A)
                # this_square.add_entity(line_AD)
        else:
            # if neither A or D are out of bounds
            this_square.add_entity(line_AD)
        if coordinate_angles[2] != th_C:
            # if C is out of bounds but B is not
            if coordinate_angles[1] == th_B:
                # find the point on boundary
                c = line_CB.y_intercept
                m = line_CB.gradient
                r = c / (sin(radians(0)) - m * cos(radians(0)))
                x_L, y_L = rt_to_xy(r, 0)
                x_U, y_U = rt_to_xy(r, duplication_angle)
                p_CL = Coordinate(x_L, y_L)
                p_CU = Coordinate(x_U, y_U)
                line_CB_L = Line(p_CL, p_B)
                line_CB_U = Line(p_C, p_CU)
                this_square.add_entity(line_CB_L)
                # this_square.add_entity(line_CB_U)
            # if B and C are out of bounds
            else:
                line_CB = Line(p_C, p_B)
                # this_square.add_entity(line_CB)
        else:
            # if neither B or C are out of bounds
            this_square.add_entity(line_CB)
        # if D and C are both out of bounds
        if coordinate_angles[3] != th_D:
            if coordinate_angles[2] != th_C:
                line_DCL = Line(p_DL, p_CL)
                line_DCU = Line(p_DU, p_CU)
                this_square.add_entity(line_DCL)
                # this_square.add_entity(line_DCU)
        line_BA = Line(p_B, p_A)
        line_DC = Line(p_D, p_C)
        # this_square.add_entity(line_DC)
        this_square.add_entity(line_BA)
    else:
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


def triangular_notch(
    rotor_radius,
    rotor_centre,
    epsilon,
    notch_start_angle,
    notch_centre_angle,
    notch_end_angle,
    notch_depth,
):
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
    # generate coordinates for triangular notch using start/mid/end
    # angles above converting from polar to cartesian
    x1, y1 = rt_to_xy(rotor_radius, notch_start_angle)
    x2, y2 = rt_to_xy(rotor_radius - notch_depth, notch_centre_angle)
    x3, y3 = rt_to_xy(rotor_radius, notch_end_angle)

    p1 = Coordinate(x1, y1)
    p2 = Coordinate(x2, y2)
    p3 = Coordinate(x3, y3)

    # using coordinate create entities making up notch region
    line_1 = Line(p3, p2)
    line_2 = Line(p2, p1)
    airgap_arc = Arc(p1, p3, rotor_centre, rotor_radius * epsilon)

    this_triangular_arc = Region()
    this_triangular_arc.entities = EntityList([line_1, line_2, airgap_arc])

    return this_triangular_arc


def triangular_notch2(rotor_radius, notch_sweep, notch_centre_angle, notch_depth):
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
    rotor_centre = Coordinate(0, 0)
    notch_start_angle = notch_centre_angle + notch_sweep / 2
    notch_end_angle = notch_centre_angle - notch_sweep / 2
    # generate coordinates for triangular notch using start/mid/end
    # angles above converting from polar to cartesian
    x1, y1 = rt_to_xy(rotor_radius, notch_start_angle)
    x2, y2 = rt_to_xy(rotor_radius - notch_depth, notch_centre_angle)
    x3, y3 = rt_to_xy(rotor_radius, notch_end_angle)

    p1 = Coordinate(x1, y1)
    p2 = Coordinate(x2, y2)
    p3 = Coordinate(x3, y3)

    # using coordinate create entities making up notch region
    line_1 = Line(p3, p2)
    line_2 = Line(p2, p1)

    # epsilon must equal -1 if
    airgap_arc = Arc(p1, p3, rotor_centre, rotor_radius * epsilon)

    this_triangular_arc = Region()
    this_triangular_arc.entities = EntityList([line_1, line_2, airgap_arc])

    return this_triangular_arc
