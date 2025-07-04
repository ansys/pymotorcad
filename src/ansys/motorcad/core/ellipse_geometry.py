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

"""Ellipse Class which approximates elliptical arcs using circular ones."""

from copy import deepcopy
from math import log, sqrt
import warnings

from ansys.motorcad.core.geometry import GEOM_TOLERANCE, Arc, Coordinate, EntityList, Line


class _BaseEllipse(EntityList):
    """Internal class to allow creation of Ellipses.

    Approximates an ellipse using circular arcs. the lengths of the major and minor axes must
    be provided, either by 2 points mirrored across an axis along with eccentricity, or by
    two points that are not mirrored. There exists only a single ellipse that satisfies
    passing through two points if they are not mirrored, so eccentricity will be ignored
    in that case.
    Begins by extracting the lengths of the major and minor axes from the given information,
    then approximates a single quadrant. It then mirrors that to create a full ellipse, and
    extracts the section of that full ellipse defined by the start and end coordinates.
    n defines the precision of the approximation of the single quadrant. As such, it is
    correlated with the number of arcs in the final returned elliptic arc, that final
    number will vary based on the location and length of the elliptic arc defined by the
     start and end coordinates.

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.

    n : integer, optional
        Number of arcs used to construct the ellipse in each quadrant

    eccentricity : float
        Ellipse eccentricity. Unused when specified points and centre define
        eccentricity, which is all cases where points are not mirrored across
        a major or minor axis.
    """

    def __init__(self, start, end, n=None, eccentricity=None):
        if (start is not None) and (end is not None):
            self.relative_start = deepcopy(start)
            self.relative_end = deepcopy(end)

        # initializing a and b
        if self.is_reflection():
            if eccentricity is None:
                raise Exception("Eccentricity must be given for mirrored points")
            else:
                self.eccentricity = eccentricity
                self.a = sqrt(
                    (
                        (-(eccentricity**2) + 1) * self.relative_start.x**2
                        + self.relative_start.y**2
                    )
                    / (-(eccentricity**2) + 1)
                )
                self.b = sqrt(self.a**2 * (1 - eccentricity**2))
        else:
            self.initialize_ab()

        # shortcut if ellipse is just circle:
        if self.eccentricity == 0:
            super().__init__([Arc(self.relative_start, self.relative_end, centre=Coordinate(0, 0))])
        else:
            # if n is not provided, n is generated based on the eccentricity
            if n is None:
                self.n = int(3 * log(1 / (1 - self.eccentricity)))
                if self.n < 2:
                    self.n = 2
            else:
                self.n = n

            quad1_points = self.get_quad1_interpolation_points()
            arcs = self.get_quad1_arcs(quad1_points)
            ellipse = self.get_whole_ellipse(arcs)
            spanning_arcs = self.get_spanning_arcs(ellipse)
            elliptic_arc = self.truncate_spanning_arcs(spanning_arcs)
            arc0 = elliptic_arc[0]
            # Implementation sometimes results in very short arcs at endpoints;
            # these are removed.
            if arc0.length < GEOM_TOLERANCE:
                elliptic_arc.pop(0)
            arcn = elliptic_arc[-1]
            if arcn.length < GEOM_TOLERANCE:
                elliptic_arc.pop()
            super().__init__(elliptic_arc)

            if self.get_min_length() < 0.1:
                warnings.warn("Curvature may be too extreme. Less detail or curvature recommended")

    def initialize_ab(self):
        """Initialize a, b, and eccentricity.

        Returns
        -------
        None
        """
        start = self.relative_start
        end = self.relative_end
        try:
            a = sqrt(
                (start.x**2 * end.y**2 - end.x**2 * start.y**2)
                / ((start.y + end.y) * (end.y - start.y))
            )
            # b might be defined by one of two equations,
            # depending on whether the x or y axis is the major one
            b = a * sqrt((end.y**2 - start.y**2) / (start.x**2 - end.x**2))
            if type(b) == complex:
                b = a * sqrt((start.y**2 - end.y**2) / (end.x**2 - start.x**2))

            self.b = b
            self.a = a

            top = min(a, b)
            bottom = max(a, b)
            self.eccentricity = sqrt(1 - top**2 / bottom**2)

        except ZeroDivisionError as e:
            raise ZeroDivisionError(
                "Invalid points: proposed shape must be an ellipse or elliptic arc"
            ) from e
        except ValueError as e:
            raise ValueError(
                "Invalid points: proposed shape must be an ellipse or elliptic arc"
            ) from e

    def get_a(self):
        start = self.relative_start
        end = self.relative_end
        try:
            a = sqrt(
                (start.x**2 * end.y**2 - end.x**2 * start.y**2)
                / ((start.y + end.y) * (end.y - start.y))
            )
        except:
            pass

    def get_quad1_interpolation_points(self):
        """Get the endpoints of arcs used within the first quadrant.

        Returns
        -------
        List
        """
        a = self.a
        b = self.b
        n = self.n

        if a == b:
            return list(Coordinate.from_polar_coords(a, i / n * 90) for i in range(0, n + 1))

        k_0 = a / b**2
        k_n = b / a**2

        points = [0] * (n + 1)
        points[0] = Coordinate(a, 0)
        points[n] = Coordinate(0, b)

        for i in range(1, n):
            k_i = (1 - i / n) * k_0 + (i / n) * k_n
            l_i = ((a * b) / k_i) ** (2 / 3)
            x_i = a * sqrt(abs((l_i - a**2) / (b**2 - a**2)))
            y_i = b * sqrt(abs((l_i - b**2) / (a**2 - b**2)))
            points[i] = Coordinate(x_i, y_i)
        return points

    def get_arc_section(self, arc, new_start, new_end):
        """Return an Arc with new start and end coordinates.

        Parameters
        ----------
        arc: Arc
            Arc to be truncated

        new_start: Coordinate

        new_end: Coordinate

        Returns
        -------
        Arc
        """
        return Arc(new_start, new_end, radius=arc.radius)

    def get_quad1_arcs(self, points):
        """Get a list of arcs defining the Ellipse in the first quadrant.

        Parameters
        ----------
        points: list of Coordinate

        Returns
        -------
        EntityList
        """
        # First arc chosen to pass through starting point, second point, and second point mirrored
        arcs = EntityList()
        full_arc_0 = Arc.from_coordinates(
            Coordinate(points[1].x, -points[1].y), points[0], points[1]
        )
        arcs.append((self.get_arc_section(full_arc_0, points[0], points[1])))

        if len(points) > 3:
            for i in range(1, len(points) - 2):
                # Each arc would pass through three points if extended
                # Just the half spanning the ith and i+1th point is appended
                full_arc_i = Arc.from_coordinates(points[i - 1], points[i], points[i + 1])
                arcs.append(self.get_arc_section(full_arc_i, points[i], points[i + 1]))
        full_arc_n = Arc.from_coordinates(
            points[-2], points[-1], Coordinate(-points[-2].x, points[-2].y)
        )
        arcs.append(self.get_arc_section(full_arc_n, points[-2], points[-1]))
        return arcs

    def get_whole_ellipse(self, arcs):
        """Extrapolate the whole ellipse from the first quadrant.

        Parameters
        ----------
        arcs: EntityList of Arcs
            Arcs within the first quadrant

        Returns
        -------
        EntityList
        """
        n = len(arcs)
        whole_ellipse = [0] * (n * 4)
        whole_ellipse[0:n] = arcs
        for i, arc in enumerate(arcs):
            # Each arc is mirrored to the other three quadrants
            whole_ellipse[2 * n - (i + 1)] = arc.mirror(Line(Coordinate(0, 0), Coordinate(0, 1)))
            whole_ellipse[2 * n - (i + 1)].reverse()

            whole_ellipse[2 * n + i] = whole_ellipse[2 * n - (i + 1)].mirror(
                Line(Coordinate(0, 0), Coordinate(1, 0))
            )
            whole_ellipse[2 * n + i].reverse()

            whole_ellipse[4 * n - (i + 1)] = arc.mirror(Line(Coordinate(0, 0), Coordinate(1, 0)))
            whole_ellipse[4 * n - (i + 1)].reverse()

        return EntityList(whole_ellipse)

    def get_spanning_arcs(self, whole_ellipse):
        """Get the section of the ellipse spanning between start and end.

        Parameters
        ----------
        whole_ellipse: EntityList

        Returns
        -------
        EntityList
        """
        spanning = False
        n = len(whole_ellipse)
        start_angle = self.relative_start.get_polar_coords_deg()[1]
        end_angle = self.relative_end.get_polar_coords_deg()[1]
        if abs(end_angle) < GEOM_TOLERANCE:
            end_angle = 0
        if abs(start_angle) < GEOM_TOLERANCE:
            start_angle = 0
        if end_angle == 180:
            end_angle = -180
        if start_angle == 180:
            start_angle = -180
        rev = (end_angle - start_angle) % 360 > 180
        spanning_arcs = EntityList()

        if rev:
            whole_ellipse.reverse()
            i = 0
            while True:
                arc = whole_ellipse[i % n]
                if arc.end.get_polar_coords_deg()[1] == 180:
                    lower_bound = -180
                else:
                    lower_bound = arc.end.get_polar_coords_deg()[1]
                upper_bound = arc.start.get_polar_coords_deg()[1]
                if lower_bound <= start_angle <= upper_bound:
                    spanning = True

                if spanning:
                    spanning_arcs.append(arc)
                if (lower_bound <= end_angle <= upper_bound) and spanning:
                    break
                i += 1
        else:
            i = 0
            while True:
                arc = whole_ellipse[i % n]
                if arc.start.get_polar_coords_deg()[1] == 180:
                    lower_bound = -180
                else:
                    lower_bound = arc.start.get_polar_coords_deg()[1]
                upper_bound = arc.end.get_polar_coords_deg()[1]
                if lower_bound <= start_angle < upper_bound:
                    spanning = True

                if spanning:
                    spanning_arcs.append(arc)
                if (lower_bound < end_angle <= upper_bound) and spanning:
                    break
                i += 1
        return spanning_arcs

    def truncate_spanning_arcs(self, spanning_arcs):
        """Truncate spanning arcs to match start and end.

        Parameters
        ----------
        spanning_arcs: EntityList

        Returns
        -------
        EntityList
        """
        # Due to the nature of the approximation, arcs will not precisely contain the given
        # start or end. Instead, the point with the same angular coordinate on the ellipse is used
        start_intersection_line = Line(Coordinate(0, 0), self.relative_start)
        end_intersection_line = Line(Coordinate(0, 0), self.relative_end)

        # get_line_intersection will return two intersection points; the nearer is used
        start_intersections = spanning_arcs[0].get_line_intersection(start_intersection_line)
        start_intersections.sort(
            key=lambda p: sqrt(
                (self.relative_start.x - p.x) ** 2 + (self.relative_start.y - p.y) ** 2
            )
        )
        spanning_arcs[0] = self.get_arc_section(
            spanning_arcs[0], start_intersections[0], spanning_arcs[0].end
        )

        end_intersections = spanning_arcs[-1].get_line_intersection(end_intersection_line)
        end_intersections.sort(
            key=lambda p: sqrt((self.relative_end.x - p.x) ** 2 + (self.relative_end.y - p.y) ** 2)
        )
        spanning_arcs[-1] = self.get_arc_section(
            spanning_arcs[-1], spanning_arcs[-1].start, end_intersections[0]
        )

        return spanning_arcs

    def get_min_length(self):
        """Get the length of the smallest arc.

        Returns
        -------
        int
        """
        lengths = list(arc.length for arc in self)
        return min(lengths)


class Ellipse(_BaseEllipse):
    """Implementation of an ellipse constructed from Arc entities based upon start, end.

    Expected inputs:
        Ellipse(start, end, depth)
        Ellipse(start, end, eccentricity)
    Angle and centre may also be provided in either case.
    Default angle is equal to the angle of the normal of the line connecting start
    and end. If no centre point is given, the centre will be defined as the average
    position of the start and end.

    Angle and centre may be provided manually, though care should be taken when
    doing so, as if angle is provided and start and end points are not mirrored
    across a relative major or minor axis, *neither* eccentricity nor depth will be
    used, as the points already uniquely determine a single ellipse.

    Centre may be provided without angle, but doing so in such a way that points
    are no longer mirrored across an axis will result in an error, as the default
    angle results in points with identical x or y coordinates that are not mirrored,
    which do not form valid ellipses.

    A graphic helpful in showing valid start and endpoints for manually supplied
    centre and angle is shown below.
    Valid (relative) start and endpoints: the ** symbols show an example placement
    of start or end. All other symbols give information about the resulting ellipse
    if the other point were to be placed in that location. The ++ symbols show where
    eccentricity would be required, the == symbols show (relative) x and y axes.
    Whitespace results in no ellipse, while - results in an ellipse defined
    without need for eccentricity.


                        ------=------
                        ------=------
                        ------=------
                        ------=------
                       ++-----=-----**
    --------------------      =      --------------------
    --------------------      =      --------------------
    =====================================================
    --------------------      =      --------------------
    --------------------      =      --------------------
    --------------------      =      --------------------
                       ++-----=-----++
                        ------=------
                        ------=------
                        ------=------
                        ------=------
                        ------=------

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.

    n : integer, optional
        Number of arcs used to construct the ellipse in each quadrant

    depth: integer, optional
        distance between midpoint and average between start and end.

    centre : Coordinate, optional
       Centre coordinate.

    eccentricity : float, optional
        Ellipse eccentricity. Used only when points do not implicitly
        determine eccentricity, which is when they are mirrored across a major or minor axis

    angle: float (degrees), optional
        Angle of the relative x-axis (usually the major axis of the ellipse).
        When providing angle and eccentricity, switching whether the major or
        minor axis is used may be accomplished by leading supplied angle by 90 degrees.

    """

    def __init__(self, start, end, n=None, depth=None, eccentricity=None, angle=None, centre=None):
        """Initialize Ellipse."""
        origin = Coordinate(0, 0)
        midpoint = start - (start - end) / 2
        if centre is None:
            centre = midpoint

        angle_given = True
        if angle is None:
            angle_given = False
            tangent_line = Line(start, midpoint)
            angle = tangent_line.angle - 90

        self.n = n
        self.relative_start = start.to_relative_coords(centre)
        self.relative_end = end.to_relative_coords(centre)
        self.relative_start.rotate(Coordinate(0, 0), -angle)
        self.relative_end.rotate(Coordinate(0, 0), -angle)
        self.centre = centre

        radius = Line(centre, start).length

        mirror = False
        # An eccentricity that gives the proper depth is found even if centre is provided,
        # so long as the centre also results in required eccentricity
        if (depth is not None) and (eccentricity is None) and (self.is_reflection()):
            if depth < 0:
                mirror = True
                depth = -depth

            threshold_radius = Line(centre, start).length
            axis_length = depth + Line(centre, midpoint).length

            # Case when an arc section with depth greater than that of an arc is required
            if axis_length > threshold_radius:
                eccentricity = sqrt(
                    (axis_length**2 - self.relative_start.x**2 - self.relative_start.y**2)
                    / (axis_length**2 - self.relative_start.x**2)
                )

            if axis_length < threshold_radius:
                angle += 90
                self.relative_start.rotate(origin, -90)
                self.relative_end.rotate(origin, -90)
                eccentricity = sqrt(
                    1
                    - axis_length**2
                    * (axis_length**2 - self.relative_start.y**2)
                    / (axis_length**2 * self.relative_start.x**2)
                )

            if abs(axis_length - threshold_radius) < GEOM_TOLERANCE:
                eccentricity = 0

        # Approximation is always done on an ellipse centred at the origin
        # With an axis of symmetry aligned with the x-axis

        super().__init__(self.relative_start, self.relative_end, n, eccentricity)
        self.start = deepcopy(start)
        self.end = deepcopy(end)

        # Transforming relative Ellipse back to proper location and orientation
        for arc in self:
            arc.rotate(Coordinate(0, 0), angle)
            arc.translate(centre.x, centre.y)

        # Correcting inaccuracies inherent to ellipse approximation at start and end
        self[0] = Arc(start, self[0].end, radius=self[0].radius)
        self[-1] = Arc(self[-1].start, end, radius=self[-1].radius)

        if mirror:
            reflection_line = Line(start, end)
            for i, section in enumerate(self):
                self[i] = section.mirror(reflection_line)

    def is_reflection(self):
        """Determine whether start and end are reflections across an axis.

        Returns
        -------
        boolean
        """
        x_axis = Line(Coordinate(0, 0), Coordinate(1, 0))
        y_axis = Line(Coordinate(0, 0), Coordinate(0, 1))
        if self.relative_start.mirror(y_axis) == self.relative_end:
            return True
        if self.relative_start.mirror(x_axis) == self.relative_end:
            return True
        if Coordinate(-self.relative_start.x, -self.relative_start.y) == self.relative_end:
            return True
        return False
