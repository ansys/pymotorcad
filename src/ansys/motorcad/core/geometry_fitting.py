"""Unit containing functions for drawing geometry from a list of points."""

from copy import copy
from enum import Enum

from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line


class _EntityType(Enum):
    line = 0
    arc = 1


class _TestEntity:
    def __init__(self, entity, points_array, tolerance):
        self.entity = entity
        self.points_array = points_array
        self.tolerance = tolerance

    def is_in_tolerance(self):
        if self.entity is None:
            # Failed to create entity in previous step.
            # could be caused by trying to create an arc on collinear points
            return False
        if isinstance(self.entity, Line):
            return self._is_line_in_tolerance()
        elif isinstance(self.entity, Arc):
            return self._is_arc_in_tolerance()
        else:
            raise TypeError("Entity type must be arc or line")

    def _is_line_in_tolerance(self):
        for xy in self.points_array:
            # Try to find the closest point on the line
            angle = self.entity.rotate(self.entity.midpoint, 90).angle

            p2 = xy + Coordinate.from_polar_coords(1, angle)
            line_t = Line(xy, p2)

            p_intercept = line_t.get_line_intersection(self.entity)

            difference = abs(p_intercept - xy)

            if difference > self.tolerance:
                return False
        else:
            return True

    def _is_arc_in_tolerance(self):
        for point in self.points_array:
            if self.entity.coordinate_within_arc_radius(point):
                radius_calculated = abs(point - self.entity.centre)
                distance = abs(abs(self.entity.radius) - radius_calculated)
            else:
                # If not within arc then closest point will be arc start/end
                d_point_start = abs(point - self.entity.start)
                d_point_end = abs(point - self.entity.end)
                distance = min(d_point_start, d_point_end)

            if distance > self.tolerance:
                return False
        else:
            return True


def return_entity_list(coordinates, line_tolerance, arc_tolerance):
    """Get list of entities from a list of coordinates.

    Parameters
    ----------
    coordinates : List of ansys.motorcad.core.geometry.Coordinate
        coordinates from which to generate the geometry
    line_tolerance : float
        maximum allowed distance of point away from generated line
    arc_tolerance : float
        maximum allowed distance of point away from generated arc

    Returns
    -------
    ansys.motorcad.core.geometry.EntityList

    """
    p = _PointFitting()
    return p.return_entity_list(coordinates, line_tolerance, arc_tolerance)


class _PointFitting:
    def __init__(self):
        self.xy_dynamic_list = []
        self.line_tolerance = 0
        self.arc_tolerance = 0
        # Maximum distance searched along a list of point to generate next line or arc
        self.max_search_depth = 100

    def get_next_entity(self, entity_type):
        """Get next valid line or arc entity from list of xy points."""
        last_valid_entity = None

        # Arcs will always be able to fit 3 points
        # No point searching for less than this since a 3 point arc is preferred to 2 point line
        for segments in range(2, self.max_search_depth):
            if segments >= len(self.xy_dynamic_list):
                # Reached end of list for searching
                break

            if entity_type == _EntityType.line:
                # loops through extending line until the tolerance is reached
                line_to_check = Line(self.xy_dynamic_list[0], self.xy_dynamic_list[segments])

                test_entity = _TestEntity(
                    line_to_check, self.xy_dynamic_list[0 : segments + 1], self.line_tolerance
                )

            elif entity_type == _EntityType.arc:
                # Pick the middle value in the array to use for the middle of the arc
                # Could be improved in future
                arc_master = Arc.from_coordinates(
                    self.xy_dynamic_list[0],
                    self.xy_dynamic_list[round(segments / 2)],
                    self.xy_dynamic_list[segments],
                )

                test_entity = _TestEntity(
                    arc_master, self.xy_dynamic_list[0 : segments + 1], self.arc_tolerance
                )
            else:
                raise Exception("invalid entity type")

            if test_entity.is_in_tolerance():
                last_valid_entity = test_entity
            else:
                break

        return last_valid_entity

    def return_entity_list(self, coordinates, line_tolerance, arc_tolerance):
        """Create a list of entities from a list of points within a given tolerance.

        Parameters
        ----------
        coordinates: List of ansys.motorcad.core.geometry.Coordinate
            Coordinates to fit entities to
        line_tolerance: float
            Maximum allowed variation of line entity from original points.
        arc_tolerance: float
            Maximum allowed variation of arc entities from original points.
        Returns
        -------
        ansys.motorcad.core.geometry.EntityList
            List of Line/Arc class objects.
        """
        # coordinates is a list of ordered coordinates
        entities = EntityList()
        current_index = 0
        self.line_tolerance = line_tolerance
        self.arc_tolerance = arc_tolerance

        # Working list. Coordinates will be popped from the front of this list when used to create
        # entities
        self.xy_dynamic_list = copy(coordinates)

        # Pop duplicate coordinates from list
        for i in range(len(self.xy_dynamic_list) - 1, 0, -1):
            if self.xy_dynamic_list[i] == self.xy_dynamic_list[i - 1]:
                self.xy_dynamic_list.pop(i)

        while len(self.xy_dynamic_list) > 2:
            # future work need to consider sharp angle case where two separate line entities
            # are required to represent 3 points this could potentially be handled by a maximum
            # arc angle limit

            next_line = self.get_next_entity(_EntityType.line)
            next_arc = self.get_next_entity(_EntityType.arc)

            if (next_arc is None) and (next_line is None):
                raise Exception("failed to create next entity")
            elif (next_arc is None) or (next_line is None):
                if next_line is None:
                    next_object = next_arc
                else:
                    next_object = next_line
            else:
                if len(next_line.points_array) >= len(next_arc.points_array):
                    next_object = next_line
                else:
                    next_object = next_arc

            entities.append(next_object.entity)
            self.xy_dynamic_list = self.xy_dynamic_list[len(next_object.points_array) - 1 :]

        # Handling end of list where remaining items less than 3 coordinates
        if len(self.xy_dynamic_list) == 2:
            entities.append(Line(self.xy_dynamic_list[0], self.xy_dynamic_list[1]))
            self.xy_dynamic_list = []

        elif len(self.xy_dynamic_list) == 1:
            # Floating final coordinate - do nothing
            pass

        return entities
