"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from cmath import polar, rect
from math import atan2, cos, degrees, pow, radians, sin, sqrt


class GeometryRegion:
    def __init__(self):
        """Create geometry region and set parameters to defaults"""
        self.entities = []
        self.number_duplications = 1
        self.colour = "(0,0,0)"
        self.material = "air"

        # expect other properties to be implemented here including number duplications, material etc

    def add_entity(self, entity):
        """Add entity to list of region entities

        Parameters
        ----------
        entity : Line/Arc class
            Line/arc entity class instance
        """
        self.entities.append(entity)

    def add_polyline(self, polyline):
        """Add polyline to list of region entities, polyline can be made up of line/arc entities

        Parameters
        ----------
        polyline : List of line/Arc class
            List of line/arc entity class instances
        """
        for entity in polyline:
            self.add_entity(entity)

    def remove_entity(self, entity):
        """Remove the entity from the region

        Parameters
        ----------
        entity : Line/Arc class
            Line/arc entity class instance
        """
        self.entities.remove(entity)

    # method to receive region from Motor-CAD and create python object
    def _from_json(self, json):
        """

        :param json:
        """
        self.Entities = json.Entities
        self.number_duplications = json.number_duplications
        self.colour = json.colour
        self.material = json.material

    # method to convert python object to send to Motor-CAD
    def _to_json(self):
        """

        :return:
        """
        return [self.entities]

    # def check_geometry():
    #     # call Motor-CAD API


class Line:
    def __init__(self, start, end):
        """Create line entity based upon start and end coordinates

        Parameters
        ----------
        start : (float, float)
            (x,y) values for start coordinate.

        end : (float, float)
            (x,y) values for end coordinate.
        """
        self.start = start
        self.end = end

    def get_coordinate_form_percentage_distance(self, x, y, percentage):
        """Get the coordinate at the percentage distance along the line from the reference coord.

        Parameters
        ----------
        x : float
            X coordinate value for entity reference.

        y : float
            y coordinate value for entity reference.
            .
        percentage : float
            Y coordinate value.

        Returns
        -------
        x : float
            X coordinate value.
        y : float
            Y coordinate value.
        """
        if (x, y) == self.end:
            coordinate_1 = self.end
            coordinate_2 = self.start
        else:
            coordinate_1 = self.start
            coordinate_2 = self.end

        length = sqrt(pow(self.start[1] - self.end[1], 2) + pow(self.start[2] - self.end[2], 2))

        t = (length * percentage) / length
        x = ((1 - t) * coordinate_1[1]) + (t * coordinate_2[1])
        y = ((1 - t) * coordinate_1[2]) + (t * coordinate_2[2])

        return x, y

    def get_coordinate_from_distance(self, x, y, distance):
        """Get the coordinate at the specified distance along the line from the reference coord.

        Parameters
        ----------
        x : float
            X coordinate value for entity reference.

        y : float
            y coordinate value for entity reference.
            .
        distance : float
            Y coordinate value.

        Returns
        -------
        x : float
            X coordinate value.
        y : float
            Y coordinate value.
        """

        if (x, y) == self.end:
            coordinate_1 = self.end
            coordinate_2 = self.start
        else:
            coordinate_1 = self.start
            coordinate_2 = self.end

        length = sqrt(pow(self.start[1] - self.end[1], 2) + pow(self.start[2] - self.end[2], 2))

        t = distance / length
        x = ((1 - t) * coordinate_1[1]) + (t * coordinate_2[1])
        y = ((1 - t) * coordinate_1[2]) + (t * coordinate_2[2])

        return x, y


class Arc:
    def __init__(self, start, end, centre, radius):
        """Create arc entity based upon start, end, centre and radius

        Parameters
        ----------
        start : (float, float)
            (x,y) values for start coordinate.

        end : (float, float)
            (x,y) values for end coordinate.

        centre : (float, float)
            (x,y) values for centre coordinate.

        radius : float
            Arc radius
        """
        self.start = start
        self.end = end
        self.radius = radius
        self.centre = centre

    def get_coordinate_from_percentage_distance(self, x, y, percentage):
        """Get the coordinate at the percentage distance along the arc from the reference coord.

        Parameters
        ----------
        x : float
            X coordinate value for entity reference.

        y : float
            y coordinate value for entity reference.
            .
        percentage : float
            Y coordinate value.

        Returns
        -------
        x : float
            X coordinate value.
        y : float
            Y coordinate value.
        """
        radius, angle_1 = xy_to_rt(self.start[1], self.start[2])
        radius, angle_2 = xy_to_rt(self.end[1], self.end[2])

        if self.radius == 0:
            arc_angle = 0
        elif ((self.radius > 0) and (angle_1 < angle_2)) or (
            (self.radius < 0) and angle_2 > angle_1
        ):
            arc_angle = 360 - angle_2 + angle_1
        else:
            arc_angle = angle_2 - angle_1

        length = self.radius * arc_angle * percentage

        return self.get_coordinate_from_distance(x, y, length, 0)

    def get_coordinate_from_distance(self, x, y, distance):
        """Get the coordinate at the specified distance along the arc from the reference coordinate.

        Parameters
        ----------
        x : float
            X coordinate value for entity reference.

        y : float
            y coordinate value for entity reference.
            .
        distance : float
            Y coordinate value.

        Returns
        -------
        x : float
            X coordinate value.
        y : float
            Y coordinate value.
        """
        if (x, y) == self.end:
            if self.radius >= 0:
                # anticlockwise
                angle = atan2(y, x) - (distance / self.radius)
            else:
                angle = atan2(y, x) + (distance / self.radius)
        else:
            if self.radius >= 0:
                # anticlockwise
                angle = atan2(y, x) + (distance / self.radius)
            else:
                angle = atan2(y, x) - (distance / self.radius)

        return self.centre[1] + self.radius * cos(angle), self.centre[2] + self.radius * sin(angle)


def xy_to_rt(x, y):
    """Convert Motor-CAD Cartesian coordinates to polar coordinates in degrees.

    Parameters
    ----------
    x : float
        X coordinate value.
    y : float
        Y coordinate value.

    Returns
    -------
    radius : float
        Radial coordinate value.
    theta : float
        Angular coordinate value.
    """
    rect_coordinates = complex(x, y)

    radius, theta = polar(rect_coordinates)

    return radius, degrees(theta)


def rt_to_xy(radius, theta):
    """Convert Motor-CAD polar coordinates to Cartesian coordinates in degrees.

    Parameters
    ----------
    radius : float
        Radial coordinate.
    theta : float
        Angular coordinate.

    Returns
    -------
    x : float
        X coordinate value.
    y : float
        Y coordinate value.
    """
    coordinates_complex = rect(radius, radians(theta))

    x = coordinates_complex.real
    y = coordinates_complex.imag

    return x, y
