"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from cmath import polar, rect
from math import atan2, cos, degrees, pow, radians, sin, sqrt


class Region:
    """Python representation of Motor-CAD geometry region."""

    def __init__(self):
        """Create geometry region and set parameters to defaults."""
        self.name = ""
        self.material = "air"
        self.colour = (0, 0, 0)
        self.area = 0.0
        self.centroid = Coordinate(0, 0)
        self.region_coordinate = Coordinate(0, 0)
        self.duplications = 1
        self.entities = []

        # expect other properties to be implemented here including number duplications, material etc

    def __eq__(self, other):
        """Override the default equals implementation for Region."""
        if (
            isinstance(other, Region)
            and self.name == other.name
            and self.colour == other.colour
            # and self.area == other.area ->
            # Already check entities - can't expect user to calculate area
            # and self.centroid == other.centroid ->
            # Centroid calculated from entities - can't expect user to calculate
            # and self.region_coordinate == other.region_coordinate ->
            # Region coordinate is an output, cannot guarantee will be same for identical regions
            and self.duplications == other.duplications
            and self.contains_same_entities(other)
        ):
            return True
        else:
            return False

    def add_entity(self, entity):
        """Add entity to list of region entities.

        Parameters
        ----------
        entity : Line or Arc
            Line/arc entity class instance
        """
        self.entities.append(entity)

    def insert_entity(self, index, entity):
        """Insert entity to list of region entities at given index.

        Parameters
        ----------
        index : int
            Index of which to insert at
        entity : Line or Arc
            Line/arc entity class instance
        """
        self.entities.insert(index, entity)

    def insert_polyline(self, index, polyline):
        """Insert polyline at given index, polyline can be made up of line/arc entities.

        Parameters
        ----------
        index : int
            Index of which to insert at
        polyline : list of Line or list of Arc
            list of Line or list of Arc
        """
        for count, entity in enumerate(polyline):
            self.insert_entity(index + count, entity)

    def remove_entity(self, entity_remove):
        """Remove the entity from the region.

        Parameters
        ----------
        entity_remove : Line or Arc
            Line/arc entity class instance
        """
        for entity in self.entities:
            if (entity.start == entity_remove.start) & (entity.end == entity_remove.end):
                if type(entity) == Line:
                    self.entities.remove(entity)
                elif type(entity) == Arc:
                    if (entity.centre == entity_remove.centre) & (
                        entity.radius == entity_remove.radius
                    ):
                        self.entities.remove(entity)

    # method to receive region from Motor-CAD and create python object
    def _from_json(self, json):
        """Convert class from json object.

        Parameters
        ----------
        json: dict
            Represents geometry region
        """
        # self.Entities = json.Entities
        self.name = json["name"]
        self.material = json["material"]

        self.colour = (json["colour"]["r"], json["colour"]["g"], json["colour"]["b"])
        self.area = json["area"]

        self.centroid = Coordinate(json["centroid"]["x"], json["centroid"]["y"])
        self.region_coordinate = Coordinate(
            json["region_coordinate"]["x"], json["region_coordinate"]["y"]
        )
        self.duplications = json["duplications"]
        self.entities = _convert_entities_from_json(json["entities"])

    # method to convert python object to send to Motor-CAD
    def _to_json(self):
        """Convert from Python class to Json object.

        Returns
        ----------
        dict
            Geometry region json representation
        """
        region_dict = {
            "name": self.name,
            "material": self.material,
            "colour": {"r": self.colour[0], "g": self.colour[1], "b": self.colour[2]},
            "area": self.area,
            "centroid": {"x": self.centroid.x, "y": self.centroid.y},
            "region_coordinate": {"x": self.region_coordinate.x, "y": self.region_coordinate.y},
            "duplications": self.duplications,
            "entities": _convert_entities_to_json(self.entities),
        }

        return region_dict

    def is_closed(self):
        """Check whether region entities create a closed region.

        Returns
        ----------
        Boolean
            Whether region is closed
        """
        if len(self.entities) > 0:
            entity_first = self.entities[0]
            entity_last = self.entities[-1]

            is_closed = get_entities_have_common_coordinate(entity_first, entity_last)

            for i in range(len(self.entities) - 1):
                is_closed = get_entities_have_common_coordinate(
                    self.entities[i], self.entities[i + 1]
                )

            return is_closed
        else:
            return False

    def contains_same_entities(self, other):
        """Check whether entities in region are the same as entities a different region.

        Parameters
        ----------
        other : ansys.motorcad.core.geometry.Region
            Motor-CAD geometry region.
        """
        if entities_same(self.entities, other.entities) or entities_same(
            self.entities, reverse_entities(other.entities)
        ):
            return True
        else:
            return False


class Coordinate:
    """Python representation of coordinate in two-dimensional space.

    Parameters
    ----------
    x : float
        X value.

    y : float
        Y value.
    """

    def __init__(self, x, y):
        """Initialise Coordinate."""
        self.x = x
        self.y = y

    def __eq__(self, other):
        """Override the default equals implementation for Coordinate."""
        if isinstance(other, Coordinate) and self.x == other.x and self.y == other.y:
            return True
        else:
            return False


class Entity:
    """Generic parent class for geometric entities based upon a start and end coordinate.

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.
    """

    def __init__(self, start, end):
        """Initialise Entity."""
        self.start = start
        self.end = end

    def __eq__(self, other):
        """Override the default equals implementation for Entity."""
        if isinstance(other, Entity) and self.start == other.start and self.end == other.end:
            return True
        else:
            return False

    def reverse(self):
        """Reverse Entity class."""
        return Entity(self.end, self.start)


class Line(Entity):
    """Python representation of Motor-CAD line entity based upon start and end coordinates.

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.
    """

    def __init__(self, start, end):
        """Initialise Line."""
        super().__init__(start, end)

    def __eq__(self, other):
        """Override the default equals implementation for Line."""
        if isinstance(other, Line) and self.start == other.start and self.end == other.end:
            return True
        else:
            return False

    def get_coordinate_from_percentage_distance(self, ref_coordinate, percentage):
        """Get the coordinate at the percentage distance along the line from the reference.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        percentage : float
            Percentage distance along Line.

        Returns
        -------
        Coordinate
            Coordinate at percentage distance along Line.
        """
        if ref_coordinate == self.end:
            coordinate_1 = self.end
            coordinate_2 = self.start
        else:
            coordinate_1 = self.start
            coordinate_2 = self.end

        length = self.get_length()

        t = (length * percentage) / length
        x = ((1 - t) * coordinate_1.x) + (t * coordinate_2.x)
        y = ((1 - t) * coordinate_1.y) + (t * coordinate_2.y)

        return Coordinate(x, y)

    def get_coordinate_from_distance(self, ref_coordinate, distance):
        """Get the coordinate at the specified distance along the line from the reference.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        distance : float
            Distance along Line.

        Returns
        -------
        Coordinate
            Coordinate at distance along Line.
        """
        if ref_coordinate == self.end:
            coordinate_1 = self.end
            coordinate_2 = self.start
        else:
            coordinate_1 = self.start
            coordinate_2 = self.end

        t = distance / self.get_length()
        x = ((1 - t) * coordinate_1.x) + (t * coordinate_2.x)
        y = ((1 - t) * coordinate_1.y) + (t * coordinate_2.y)

        return Coordinate(x, y)

    def get_length(self):
        """Get length of line.

        Returns
        -------
        float
            Length of line
        """
        return sqrt(pow(self.start.x - self.end.x, 2) + pow(self.start.y - self.end.y, 2))

    def reverse(self):
        """Reverse Line entity."""
        return Line(self.end, self.start)


class Arc(Entity):
    """Python representation of Motor-CAD arc entity based upon start, end, centre and radius.

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.

    centre :Coordinate
       Centre coordinate.

    radius : float
        Arc radius
    """

    def __init__(self, start, end, centre, radius):
        """Initialise Arc."""
        super().__init__(start, end)
        self.radius = radius
        self.centre = centre

    def __eq__(self, other):
        """Override the default equals implementation for Arc."""
        if (
            isinstance(other, Arc)
            and self.start == other.start
            and self.end == other.end
            and self.centre == other.centre
            and self.radius == other.radius
        ):
            return True
        else:
            return False

    def get_coordinate_from_percentage_distance(self, ref_coordinate, percentage):
        """Get the coordinate at the percentage distance along the arc from the reference coord.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        percentage : float
            Percentage distance along Arc.

        Returns
        -------
        Coordinate
            Coordinate at percentage distance along Arc.
        """
        length = self.get_length() * percentage

        return self.get_coordinate_from_distance(ref_coordinate, length)

    def get_coordinate_from_distance(self, ref_coordinate, distance):
        """Get the coordinate at the specified distance along the arc from the reference coordinate.

        Parameters
        ----------
        ref_coordinate : Coordinate
           Entity reference coordinate.

        distance : float
            Distance along arc.

        Returns
        -------
        Coordinate
            Coordinate at distance along Arc.
        """
        if ref_coordinate == self.end:
            if self.radius >= 0:
                # anticlockwise
                angle = atan2(ref_coordinate.y, ref_coordinate.x) - (distance / self.radius)
            else:
                angle = atan2(ref_coordinate.y, ref_coordinate.x) + (distance / self.radius)
        else:
            if self.radius >= 0:
                # anticlockwise
                angle = atan2(ref_coordinate.y, ref_coordinate.x) + (distance / self.radius)
            else:
                angle = atan2(ref_coordinate.y, ref_coordinate.x) - (distance / self.radius)

        return Coordinate(
            self.centre.x + self.radius * cos(angle), self.centre.y + self.radius * sin(angle)
        )

    def get_length(self):
        """Get length of arc from start to end along circumference.

        Returns
        -------
        float
            Length of arc
        """
        radius, angle_1 = xy_to_rt(self.start.x, self.start.y)
        radius, angle_2 = xy_to_rt(self.end.x, self.end.y)

        if self.radius == 0:
            arc_angle = 0
        elif ((self.radius > 0) and (angle_1 > angle_2)) or (
            (self.radius < 0) and angle_2 < angle_1
        ):
            arc_angle = angle_2 - (angle_1 - 360)
        else:
            arc_angle = angle_2 - angle_1

        return self.radius * radians(arc_angle)

    def reverse(self):
        """Reverse Arc entity."""
        return Arc(self.end, self.start, self.centre, -self.radius)


def _convert_entities_to_json(entities):
    """Get entities list as a json object.

    Parameters
    ----------
    entities : list of Line or list of Arc
        List of Line/Arc class objects representing entities.

    Returns
    -------
    dict
        entities in json format
    """
    json_entities = []

    for entity in entities:
        if isinstance(entity, Line):
            json_entities.append(
                {
                    "type": "line",
                    "start": {"x": entity.start.x, "y": entity.start.y},
                    "end": {"x": entity.end.x, "y": entity.end.y},
                }
            )
        elif isinstance(entity, Arc):
            json_entities.append(
                {
                    "type": "arc",
                    "start": {"x": entity.start.x, "y": entity.start.y},
                    "end": {"x": entity.end.x, "y": entity.end.y},
                    "centre": {"x": entity.centre.x, "y": entity.centre.y},
                    "radius": entity.radius,
                }
            )

    return json_entities


def _convert_entities_from_json(json_array):
    """Convert entities from json object to list of Arc/Line class.

    Parameters
    ----------
    json_array : Json object
        Array of Json objects representing lines/arcs.

    Returns
    -------
    list of Line or list of Arc
        list of Line and Arc objects
    """
    entities = []

    for entity in json_array:
        if entity["type"] == "line":
            entities.append(
                Line(
                    Coordinate(entity["start"]["x"], entity["start"]["y"]),
                    Coordinate(entity["end"]["x"], entity["end"]["y"]),
                )
            )
        elif entity["type"] == "arc":
            entities.append(
                Arc(
                    Coordinate(entity["start"]["x"], entity["start"]["y"]),
                    Coordinate(entity["end"]["x"], entity["end"]["y"]),
                    Coordinate(entity["centre"]["x"], entity["centre"]["y"]),
                    entity["radius"],
                )
            )

    return entities


def get_entities_have_common_coordinate(entity_1, entity_2):
    """Check whether region entities create a closed region.

    Parameters
    ----------
    entity_1 : Line or Arc
        Line or Arc object to check for common coordinate

    entity_2 : Line or Arc
        Line or Arc object to check for common coordinate

    Returns
    ----------
        Boolean
    """
    if (
        (entity_1.end == entity_2.start)
        or (entity_1.end == entity_2.end)
        or (entity_1.start == entity_2.start)
        or (entity_1.start == entity_2.end)
    ):
        # found common coordinate between first and last entities
        return True
    else:
        return False


def entities_same(entities_a, entities_b):
    """Check whether entities in region are the same as entities a different region.

    Parameters
    ----------
    entities_a : list of Line or list of Arc
        list of Line and Arc objects.

    entities_b : list of Line or list of Arc
        list of Line and Arc objects.

    Returns
    ----------
    boolean
    """
    start_index = 0

    for count, entity in enumerate(entities_b):
        if entity == entities_a[0]:
            # start entity found
            start_index = count
            break

    # regenerate entities_b from start index found from entities_a
    entities = [entities_b[i] for i in range(start_index, len(entities_a))] + [
        entities_b[i] for i in range(0, start_index)
    ]

    if entities == entities_a:
        return True
    else:
        return False


def reverse_entities(entities):
    """Reverse list of line/arc entities, including entity start end coordinates.

    Parameters
    ----------
    entities : list of Line or list of Arc
        list of Line and Arc objects.

    Returns
    ----------
    list of Line or list of Arc
        list of Line and Arc objects.
    """
    entities.reverse()
    return [entity.reverse() for entity in entities]


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
