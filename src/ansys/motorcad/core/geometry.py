"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from cmath import polar, rect
from copy import deepcopy
from enum import Enum
from math import atan2, cos, degrees, inf, isclose, radians, sin, sqrt


class Region(object):
    """Python representation of Motor-CAD geometry region."""

    def __init__(self, motorcad_instance=None):
        """Create geometry region and set parameters to defaults."""
        self.name = ""
        self.material = "air"
        self.colour = (0, 0, 0)
        self.area = 0.0
        self.centroid = Coordinate(0, 0)
        self.region_coordinate = Coordinate(0, 0)
        self.duplications = 1
        self.entities = EntityList()
        self._parent_name = ""
        self._child_names = []
        self._motorcad_instance = motorcad_instance
        self._region_type = RegionType.unknown

        # expect other properties to be implemented here including number duplications, material etc

    def __eq__(self, other):
        """Override the default equals implementation for Region."""
        return (
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
            and self.entities == other.entities
        )

    @classmethod
    def from_coordinate_list(cls):
        """Work in progress. Need to split up geometry first to avoid circular imports.

        Use geometry_fitting.return_entity_list for now
        """
        pass

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
        polyline : EntityList
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
    @classmethod
    def _from_json(cls, json, motorcad_instance=None):
        """Convert class from json object.

        Parameters
        ----------
        json: dict
            Represents geometry region
        motorcad_instance : ansys.motorcad.core.MotorCAD
            Motor-CAD instance that is connected
        """
        has_region_type = "region_type" in json
        is_magnet = has_region_type and (json["region_type"] == RegionType.magnet.value)

        if is_magnet:
            new_region = RegionMagnet(motorcad_instance)
            new_region._magnet_angle = json["_magnet_angle"]
            new_region._mag_factor = json["magnet_magfactor"]
            new_region._magnet_polarity = json["magnet_polarity"]
        else:
            new_region = cls(motorcad_instance)

        if has_region_type:
            new_region._region_type = RegionType(json["region_type"])

        # self.Entities = json.Entities
        new_region.name = json["name"]
        new_region.material = json["material"]

        new_region.colour = (json["colour"]["r"], json["colour"]["g"], json["colour"]["b"])
        new_region.area = json["area"]

        new_region.centroid = Coordinate(json["centroid"]["x"], json["centroid"]["y"])
        new_region.region_coordinate = Coordinate(
            json["region_coordinate"]["x"], json["region_coordinate"]["y"]
        )
        new_region.duplications = json["duplications"]
        new_region.entities = _convert_entities_from_json(json["entities"])
        new_region.parent_name = json["parent_name"]
        new_region._child_names = json["child_names"]

        return new_region

    # method to convert python object to send to Motor-CAD
    def _to_json(self):
        """Convert from Python class to Json object.

        Returns
        -------
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
            "parent_name": self.parent_name,
            "region_type": self._region_type.value,
        }

        return region_dict

    def is_closed(self):
        """Check whether region entities create a closed region.

        Returns
        -------
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

    @property
    def parent_name(self):
        """Get region parent name.

        Returns
        -------
        string
        """
        return self._parent_name

    @parent_name.setter
    def parent_name(self, name):
        """Set region parent name."""
        self._parent_name = name

    @property
    def child_names(self):
        """Property for child names list.

        Returns
        -------
        list of string
            list of child region names
        """
        return self._child_names

    @property
    def motorcad_instance(self):
        """Get linked Motor-CAD instance."""
        return self._motorcad_instance

    @motorcad_instance.setter
    def motorcad_instance(self, mc):
        """Set linked Motor-CAD instance."""
        # if isinstance(mc, _MotorCADConnection):
        #     raise Exception("Unable to set self.motorcad_instance,
        #                      mc is not a Motor-CAD connection")
        self._motorcad_instance = mc

    @property
    def children(self):
        """Return list of child regions from Motor-CAD.

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        self._check_connection()
        return [self.motorcad_instance.get_region(name) for name in self.child_names]

    @property
    def parent(self):
        """Return parent region from Motor-CAD.

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        self._check_connection()
        return self.motorcad_instance.get_region(self.parent_name)

    @parent.setter
    def parent(self, region):
        """Set parent region."""
        self._parent_name = region.name

    def subtract(self, region):
        """Subtract region from self, returning any additional regions.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        self._check_connection()
        regions = self.motorcad_instance.subtract_region(self, region)

        if len(regions) > 0:
            self.update(regions[0])
            return regions[1 : len(regions)]

    def unite(self, regions):
        """Unite one or more other regions with self.

        Parameters
        ----------
        regions : ansys.motorcad.core.geometry.Region or list of ansys.motorcad.core.geometry.Region
            Motor-CAD region object/list of objects
        """
        if type(regions) is not list:
            regions = [regions]

        self._check_connection()
        united_region = self.motorcad_instance.unite_regions(self, regions)
        self.update(united_region)

    def collides(self, regions):
        """Check whether any of the specified regions collide with self.

        Parameters
        ----------
        regions : ansys.motorcad.core.geometry.Region or list of ansys.motorcad.core.geometry.Region
            Motor-CAD region object/list of objects
        """
        if type(regions) is not list:
            regions = [regions]

        self._check_connection()
        collisions = self.motorcad_instance.check_collisions(self, regions)

        return len(collisions) > 0

    def mirror(self, mirror_line, unique_name=True):
        """Mirror region along entity.

        Parameters
        ----------
        mirror_line : ansys.motorcad.core.geometry.Line
            Line entity to mirror region about

        unique_name : boolean
            Whether to apply a unique name to returned region

        Returns
        -------
        ansys.motorcad.core.geometry.Region
        """
        if isinstance(mirror_line, Line):
            region = deepcopy(self)
            region.entities.clear()
            region.centroid = self.centroid.mirror(mirror_line)
            region.region_coordinate = self.region_coordinate.mirror(mirror_line)
            region._child_names = []

            if unique_name:
                region.name = region.name + "_mirrored"

            for entity in self.entities:
                region.add_entity(entity.mirror(mirror_line))

            return region
        else:
            raise Exception("Region can only be mirrored about Line()")

    def update(self, region):
        """Update class fields from another region.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object
        """
        self.name = region.name
        self.material = region.material
        self.colour = region.colour
        self.area = region.area
        self.centroid = deepcopy(region.centroid)
        self.region_coordinate = deepcopy(region.region_coordinate)
        self.duplications = region.duplications
        self.entities = deepcopy(region.entities)
        self.parent_name = region.parent_name
        self._child_names = region.child_names
        self._motorcad_instance = region._motorcad_instance

    def _check_connection(self):
        """Check mc connection for region."""
        if self.motorcad_instance is None:
            raise Exception(
                "A Motor-CAD connection is required for this function"
                + ", please set self.motorcad_instance to a valid Motor-CAD instance"
            )
        if self.motorcad_instance.connection._wait_for_response(1) is False:
            raise Exception(
                "Unable to connect to Motor-CAD using self.motorcad_instance,"
                + ", please set self.motorcad_instance to a valid Motor-CAD instance"
            )

    @property
    def points(self):
        """Get points that exist in region.

        Returns
        -------
        List of Coordinate
        """
        return self.entities.points

    def add_point(self, point):
        """Add a new point into region on an existing Line/Arc.

        The point must already exist on a Line/Arc belonging to the region. The entity will be split
        and 2 new entities created.

        Parameters
        ----------
        point : Coordinate
            Coordinate at which to add new point
        """
        for pos, entity in enumerate(self.entities):
            if entity.coordinate_on_entity(point):
                if isinstance(entity, Line):
                    new_entity_1 = Line(entity.start, point)
                    new_entity_2 = Line(point, entity.end)
                elif isinstance(entity, Arc):
                    new_entity_1 = Arc(entity.start, point, entity.centre, entity.radius)
                    new_entity_2 = Arc(point, entity.end, entity.centre, entity.radius)
                else:
                    raise Exception("Entity type is not Arc or Line")

                self.entities.pop(pos)
                self.entities.insert(pos, new_entity_1)
                self.entities.insert(pos + 1, new_entity_2)
                break

        else:
            raise Exception("Failed to find point on entity in region")

    def edit_point(self, old_coordinates, new_coordinates):
        """Edit a point in the region and update entities.

        Parameters
        ----------
        old_coordinates : Coordinate
            Position of point to edit
        new_coordinates : Coordinate
            Position to move the point to
        """
        for entity in self.entities:
            edited = False

            if entity.start == old_coordinates:
                entity.start = deepcopy(new_coordinates)
                edited = True
            if entity.end == old_coordinates:
                entity.end = deepcopy(new_coordinates)
                edited = True

            if edited and isinstance(entity, Arc):
                # Draw line between arc start/end
                # get centre point of that line
                p_centre = (entity.end + entity.start) / 2
                # Get vector of that line
                v_1 = entity.end - entity.start
                # Get length div 2
                d1 = abs(v_1) / 2

                # Draw perpendicular line from centre point
                radius, angle = v_1.get_polar_coords_deg()
                perpendicular_angle = angle + 90 * (entity.radius / abs(entity.radius))

                if entity.radius < d1:
                    raise Exception("It is not possible to draw an arc with this geometry")

                # Get vector from p_centre to centre point of arc
                d_adjacent = sqrt(entity.radius**2 - d1**2)
                l_x, l_y = rt_to_xy(d_adjacent, perpendicular_angle)

                # Apply vector to centre point of arc
                entity.centre = p_centre + Coordinate(l_x, l_y)

    def find_entity_from_coordinates(self, coordinate_1, coordinate_2):
        """Search through region to find an entity with start and end coordinates.

        Order of coordinates does not matter.

        Parameters
        ----------
        coordinate_1: ansys.motorcad.core.geometry.Coordinate
        coordinate_2: ansys.motorcad.core.geometry.Coordinate

        Returns
        -------
        Line or Arc entity
        """
        for entity in self.entities:
            if (coordinate_1 == entity.start) and (coordinate_2 == entity.end):
                return entity
            elif (coordinate_1 == entity.end) and (coordinate_2 == entity.start):
                return entity

        return None


class RegionMagnet(Region):
    """Python representation of Motor-CAD magnet geometry region."""

    def __init__(self, motorcad_instance=None):
        """Initialise RegionMagnet."""
        super().__init__(motorcad_instance)
        self._magnet_angle = 0.0
        self._mag_factor = 0.0
        self._br_magnet = 0.0
        self._magnet_polarity = ""

    def _to_json(self):
        """Convert from Python class to Json object.

        Returns
        -------
        dict
            Geometry region json representation
        """
        region_dict = super()._to_json()

        region_dict["magnet_magfactor"] = self._mag_factor
        region_dict["_magnet_angle"] = self._magnet_angle

        return region_dict

    @property
    def mag_factor(self):
        """Get mag_factor.

        Returns
        -------
        float
        """
        return self._mag_factor

    @mag_factor.setter
    def mag_factor(self, mag_factor):
        """Set mag_factor.

        Parameters
        ----------
        mag_factor : float
        """
        self._mag_factor = mag_factor

    @property
    def br_value(self):
        """Br value of magnet before mag factor applied.

        Returns
        -------
        float
        """
        return self._br_magnet

    @property
    def magnet_angle(self):
        """Get angle of magnet (degrees).

        Returns
        -------
        float
        """
        return self._magnet_angle

    @magnet_angle.setter
    def magnet_angle(self, magnet_angle):
        """Set magnet angle (degrees).

        Parameters
        ----------
        magnet_angle : float
        """
        self._magnet_angle = magnet_angle

    @property
    def br_x(self):
        """Get x axis component of br value.

        Returns
        -------
        float
        """
        return cos(radians(self.magnet_angle)) * self.br_value * self._mag_factor

    @property
    def br_y(self):
        """Get y axis component of br value.

        Returns
        -------
        float
        """
        return sin(radians(self.magnet_angle)) * self.br_value * self._mag_factor

    @property
    def br_used(self):
        """Br used after applying mag factor.

        Returns
        -------
        float
        """
        return self._br_magnet * self.mag_factor

    @property
    def magnet_polarity(self):
        """Get polarity of magnet.

        Returns
        -------
        string
        """
        return self._magnet_polarity


class Coordinate(object):
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
        return (
            isinstance(other, Coordinate)
            and isclose(self.x, other.x, abs_tol=1e-6)
            and isclose(self.y, other.y, abs_tol=1e-6)
        )

    def __sub__(self, other):
        """Override the default subtract implementation for Coordinate."""
        return Coordinate(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Override the default add implementation for Coordinate."""
        return Coordinate(self.x + other.x, self.y + other.y)

    def __abs__(self):
        """Override the default abs() implementation for Coordinate."""
        return sqrt(self.x**2 + self.y**2)

    def __mul__(self, other):
        """Override the default multiplication implementation for Coordinate."""
        return Coordinate(self.x * other, self.y * other)

    def __truediv__(self, other):
        """Override the default divide implementation for Coordinate."""
        return Coordinate(self.x / other, self.y / other)

    def __str__(self):
        """Override the default str() implementation for Coordinate."""
        return str([self.x, self.y])

    def get_polar_coords_deg(self):
        """Get coordinates as polar coordinates in degrees."""
        return xy_to_rt(self.x, self.y)

    def mirror(self, mirror_line):
        """Mirror Coordinate about a line entity.

        Parameters
        ----------
        mirror_line : ansys.motorcad.core.geometry.Line
            Line entity to mirror coordinate about

        Returns
        -------
        ansys.motorcad.core.geometry.Coordinate
        """
        if isinstance(mirror_line, Line):
            if mirror_line.is_vertical:
                d = self.x - mirror_line.start.x
                return Coordinate(mirror_line.start.x - d, self.y)
            else:
                d = (self.x + (self.y - mirror_line.y_intercept) * mirror_line.gradient) / (
                    1 + mirror_line.gradient**2
                )
                return Coordinate(
                    2 * d - self.x,
                    2 * d * mirror_line.gradient - self.y + 2 * mirror_line.y_intercept,
                )
        else:
            raise Exception("Coordinate can only be mirrored about Line")

    def rotate(self, centre_point, angle):
        """Rotate Coordinate around a point for a given angle.

        Parameters
        ----------
        centre_point : Coordinate
            point to rotate Coordinate around.
        angle : float
            Angle of rotation in degrees.

        Returns
        -------
        Coordinate
        """
        angle_r = radians(angle)
        x_new = centre_point.x + (
            (cos(angle_r) * (self.x - centre_point.x)) + (-sin(angle_r) * (self.y - centre_point.y))
        )
        y_new = centre_point.y + (
            (sin(angle_r) * (self.x - centre_point.x)) + (cos(angle_r) * (self.y - centre_point.y))
        )

        return Coordinate(x_new, y_new)

    @classmethod
    def from_polar_coords(cls, radius, theta):
        """Create Coordinate from polar coordinates.

        Parameters
        ----------
        radius : float
            Radial coordinate.
        theta : float
            Angular coordinate.
        Returns
        -------
        Coordinate
        """
        return cls(*rt_to_xy(radius, theta))


class Entity(object):
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
        self.start = deepcopy(start)
        self.end = deepcopy(end)

    def __eq__(self, other):
        """Override the default equals implementation for Entity."""
        return isinstance(other, Entity) and self.start == other.start and self.end == other.end

    def reverse(self):
        """Reverse Entity class."""
        start = self.start
        end = self.end
        self.start = end
        self.end = start

    def mirror(self, mirror_line):
        """Mirror entity about a line.

        Parameters
        ----------
        mirror_line : ansys.motorcad.core.geometry.Line
            Line entity to mirror entity about

        Returns
        -------
        ansys.motorcad.core.geometry.Entity
        """
        if isinstance(mirror_line, Line):
            return Entity(self.start.mirror(mirror_line), self.end.mirror(mirror_line))
        else:
            raise Exception("Entity can only be mirrored about Line()")


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
        return isinstance(other, Line) and self.start == other.start and self.end == other.end

    @property
    def midpoint(self):
        """Get midpoint of Line.

        Returns
        -------
            Coordinate
        """
        return (self.start + self.end) / 2

    @property
    def gradient(self):
        """Get gradient of line - A in equation (y = Ax + B).

        Undefined for vertical lines.

        Returns
        -------
            float
        """
        if self.is_vertical:
            return float(inf)
        else:
            return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    @property
    def y_intercept(self):
        """Get y intercept of line - B in equation (y = Ax + B).

        Returns
        -------
            float
        """
        if self.is_vertical:
            raise Exception("Vertical line, no y interception")
        else:
            return ((self.end.x * self.start.y) - (self.start.x * self.end.y)) / (
                self.end.x - self.start.x
            )

    @property
    def is_vertical(self):
        """Check whether line is vertical.

        Returns
        -------
            boolean
        """
        return self.end.x - self.start.x == 0

    @property
    def is_horizontal(self):
        """Check whether line is horizontal.

        Returns
        -------
            boolean
        """
        return self.end.y - self.start.y == 0

    def mirror(self, mirror_line):
        """Mirror line about a line.

        Parameters
        ----------
        mirror_line : ansys.motorcad.core.geometry.Line
            Line entity to mirror Line about

        Returns
        -------
        ansys.motorcad.core.geometry.Line
        """
        if isinstance(mirror_line, Line):
            return Line(self.start.mirror(mirror_line), self.end.mirror(mirror_line))
        else:
            raise Exception("Line can only be mirrored about Line()")

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

        t = (self.length * percentage) / self.length
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

        t = distance / self.length
        x = ((1 - t) * coordinate_1.x) + (t * coordinate_2.x)
        y = ((1 - t) * coordinate_1.y) + (t * coordinate_2.y)

        return Coordinate(x, y)

    @property
    def length(self):
        """Get length of line.

        Returns
        -------
        float
            Length of line
        """
        return abs(self.end - self.start)

    def __abs__(self):
        """Override the default abs() implementation for Line."""
        return self.length

    @property
    def angle(self):
        """Get angle of line vector."""
        _, angle = (self.end - self.start).get_polar_coords_deg()
        return angle

    def coordinate_on_entity(self, coordinate):
        """Get if a coordinate exists on this line.

        Parameters
        ----------
        coordinate : Coordinate
            Check if this coordinate is on the line
        Returns
        -------
        bool
        """
        v1 = self.end - coordinate
        v2 = coordinate - self.start

        return abs(v1) + abs(v2) == self.length

    def rotate(self, centre_point, angle):
        """Rotate line around a point for a given angle.

        Parameters
        ----------
        centre_point : Coordinate
            Coordinate to rotate line around.
        angle : float
            Angle of rotation in degrees.

        Returns
        -------
        Line
        """
        return Line(self.start.rotate(centre_point, angle), self.end.rotate(centre_point, angle))

    def _line_equation(self):
        """Get value of coefficients of line in format A*x + B*y = C."""
        a = self.start.y - self.end.y
        b = self.end.x - self.start.x
        c = a * self.start.x + b * self.start.y

        return a, b, c

    def get_line_intersection(self, line):
        """Get intersection Coordinate of line with another line.

        Returns None if intersection not found.

        Parameters
        ----------
        line : ansys.motorcad.core.geometry.Line

        Returns
        -------
        ansys.motorcad.core.geometry.Coordinate or None
        """
        a_self, b_self, c_self = self._line_equation()
        a_line, b_line, c_line = line._line_equation()

        d_main = (a_self * b_line) - (b_self * a_line)
        d_x = (c_self * b_line) - (b_self * c_line)
        d_y = (a_self * c_line) - (c_self * a_line)

        if d_main != 0:
            x = d_x / d_main
            y = d_y / d_main
            return Coordinate(x, y)
        else:
            # Lines don't intersect
            return None


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
        self.radius = deepcopy(radius)
        self.centre = deepcopy(centre)

    def __eq__(self, other):
        """Override the default equals implementation for Arc."""
        return (
            isinstance(other, Arc)
            and self.start == other.start
            and self.end == other.end
            and self.centre == other.centre
            and self.radius == other.radius
        )

    @property
    def midpoint(self):
        """Get midpoint of arc.

        Returns
        -------
            Coordinate
        """
        angle_to_rotate = (self.total_angle / 2) * (self.radius / abs(self.radius))
        angle = self.start_angle + angle_to_rotate
        x_shift, y_shift = rt_to_xy(abs(self.radius), angle)
        return Coordinate(self.centre.x + x_shift, self.centre.y + y_shift)

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
        length = self.length * percentage

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

        return self.centre + Coordinate(*rt_to_xy(self.radius, degrees(angle)))

    def mirror(self, mirror_line):
        """Mirror arc about a line.

        Parameters
        ----------
        mirror_line : ansys.motorcad.core.geometry.Line
            Line entity to mirror Line about

        Returns
        -------
        ansys.motorcad.core.geometry.Arc
        """
        if isinstance(mirror_line, Line):
            return Arc(
                self.start.mirror(mirror_line),
                self.end.mirror(mirror_line),
                self.centre.mirror(mirror_line),
                -1 * self.radius,
            )
        else:
            raise Exception("Arc can only be mirrored about Line()")

    @property
    def length(self):
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
        super().reverse()

        self.radius *= -1

    def coordinate_within_arc_radius(self, coordinate):
        """Check if coordinate exists within arc radius.

        Parameters
        ----------
        coordinate : Coordinate
            Check if this coordinate is on the Arc
        Returns
        -------
        bool
        """
        v_from_centre = coordinate - self.centre
        radius, angle_to_check = v_from_centre.get_polar_coords_deg()

        if self.radius > 0:
            theta1 = (angle_to_check - self.start_angle) % 360
        else:
            theta1 = (angle_to_check - self.end_angle) % 360

        return theta1 <= self.total_angle

    def coordinate_on_entity(self, coordinate):
        """Get if a coordinate exists on this Arc.

        Parameters
        ----------
        coordinate : Coordinate
            Check if this coordinate is on the Arc
        Returns
        -------
        bool
        """
        v_from_centre = coordinate - self.centre
        radius, _ = v_from_centre.get_polar_coords_deg()
        return self.coordinate_within_arc_radius(coordinate) and (abs(radius) == abs(self.radius))

    @property
    def start_angle(self):
        """Get angle of start point from centre point coordinates.

        Returns
        -------
        real
        """
        _, ang = (self.start - self.centre).get_polar_coords_deg()
        return ang

    @property
    def end_angle(self):
        """Get angle of end point from centre point coordinates.

        Returns
        -------
        real
        """
        _, ang = (self.end - self.centre).get_polar_coords_deg()
        return ang

    @property
    def total_angle(self):
        """Get arc sweep angle.

        Returns
        -------
        real
        """
        if self.radius > 0:
            return (self.end_angle - self.start_angle) % 360
        else:
            return (self.start_angle - self.end_angle) % 360

    @classmethod
    def from_coordinates(cls, start_point, intersection_point, end_point):
        """Take three coordinates and converts to an arc.

        Parameters
        ----------
        start_point: ansys.motorcad.core.geometry.Coordinate
            Start coordinate of Arc.
        intersection_point: ansys.motorcad.core.geometry.Coordinate
            Coordinate which arc will intersect.
        end_point: ansys.motorcad.core.geometry.Coordinate
            End coordinate of Arc.
        Returns
        -------
        ansys.motorcad.core.geometry.Arc
        """
        l1 = Line(start_point, intersection_point)
        l2 = Line(intersection_point, end_point)

        if isclose(l1.gradient, l2.gradient, abs_tol=1e-6):
            # three points are on a straight line, no arc is possible
            return None

        # Trying to get the intersection of perpendicular lines:
        #  |
        #  |
        #  |              x
        #  |
        #  |___________________________

        # Work out perpendicular lines
        l1_p = l1.rotate(l1.midpoint, 90)
        l2_p = l2.rotate(l2.midpoint, 90)

        # Get intersection of perpendicular lines
        intersection = l1_p.get_line_intersection(l2_p)

        # Get appropriate sign for radius
        if (
            _orientation_of_three_points(start_point, intersection_point, end_point)
            == _Orientation.anticlockwise
        ):
            radius = Line(start_point, intersection).length
        else:
            radius = -Line(start_point, intersection).length

        arc_centre = Coordinate(intersection.x, intersection.y)

        return cls(start_point, end_point, arc_centre, radius)


class EntityList(list):
    """Generic class for list of Entities."""

    def __eq__(self, other):
        """Compare equality of 2 EntityList objects."""
        return self._entities_same(other, check_reverse=True)

    def reverse(self):
        """Reverse EntityList, including entity start end coordinates."""
        super().reverse()

        # Also reverse entity start/end points so the EntityList is continuous
        for entity in self:
            entity.reverse()

    @property
    def points(self):
        """Get points of shape/region from Entity list.

        Returns
        -------
        List of Coordinate
        """
        points = []
        for entity in self:
            points += [deepcopy(entity.start)]
        return points

    def _entities_same(self, entities_to_compare, check_reverse=False):
        """Check whether entities in region are the same as entities a different region.

        Parameters
        ----------
        entities_to_compare : EntityList
            entities to test against

        check_reverse : Boolean
            Whether to reverse entities when checking entity equivalency.

        Returns
        -------
        boolean
        """

        def _entities_same_with_direction(entities_1, entities_2):
            start_index = 0

            for count, entity in enumerate(entities_2):
                if entity == entities_1[0]:
                    # start entity found
                    start_index = count
                    break

            # regenerate entities_b from start index found from entities_a
            entities_same_order = [entities_2[i] for i in range(start_index, len(entities_1))] + [
                entities_2[i] for i in range(0, start_index)
            ]

            if list(entities_1) == list(entities_same_order):
                return True
            else:
                return False

        if check_reverse:
            if _entities_same_with_direction(self, entities_to_compare):
                return True
            else:
                # Copy list of entities
                entities_copy = deepcopy(entities_to_compare)
                entities_copy.reverse()

                return _entities_same_with_direction(self, entities_copy)

        else:
            return _entities_same_with_direction(self, entities_to_compare)


def _convert_entities_to_json(entities):
    """Get entities list as a json object.

    Parameters
    ----------
    entities : EntityList
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
    EntityList
        list of Line and Arc objects
    """
    entities = EntityList()

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
    -------
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


class _Orientation(Enum):
    clockwise = 1
    anticlockwise = 2
    collinear = 0


def _orientation_of_three_points(c1, c2, c3):
    """Find the orientation of three coordinates, this can be clockwise, anticlockwise or collinear.

    Parameters
    ----------
    coordinate_1 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 1
    c2 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 2
    c3 : ansys.motorcad.core.geometry.Coordinate
        Coordinate 3
    Returns
    -------
        _Orientation
    """
    # To find the orientation of three coordinates
    val = (float(c2.y - c1.y) * (c3.x - c2.x)) - (float(c2.x - c1.x) * (c3.y - c2.y))
    if val > 0:
        # Clockwise orientation
        return _Orientation.clockwise
    elif val < 0:
        # Anticlockwise orientation
        return _Orientation.anticlockwise
    else:
        # Collinear orientation
        return _Orientation.collinear


class RegionType(Enum):
    """Class to store region types for Motor-CAD regions."""

    stator = "Stator"
    rotor = "Rotor"
    slotarea_stator = "Stator Slot"
    slotarea_rotor = "Rotor Slot"
    slot_split = "Split Slot"
    statorliner = "Stator Liner"
    rotorliner = "Rotor Liner"
    wedge = "Wedge"
    statorduct = "Stator Duct"
    housing = "Housing"
    housing_magnetic = "Magnetic Housing"
    statorimpreg = "Stator Impreg"
    impreggap = "Impreg Gap"
    statorcopper = "Stator Copper"
    statorcopperins = "Stator Copper Insulation"
    statordivider = "Stator Divider"
    statorslotspacer = "Stator Slot Spacer"
    statorseparator = "Stator slot separator"
    coilinsulation = "Coil Insulation"
    statorair = "Stator Air"
    rotorhub = "Rotor hub"
    rotorair = "Rotor Air"
    rotorair_excliner = "Rotor Air (excluding liner area)"
    rotorpocket = "Rotor Pocket"
    polespacer = "Pole Spacer"
    rotorslot = "Rotor Slot"
    coilseparator = "Coil Separator"
    damperbar = "Damper Bar"
    wedge_rotor = "Rotor Wedge"
    rotordivider = "Rotor Divider"
    rotorcopperins = "Rotor Copper Insulation"
    rotorcopper = "Rotor Copper"
    rotorimpreg = "Rotor Impreg"
    shaft = "Shaft"
    axle = "Axle"
    rotorduct = "Rotor Duct"
    magnet = "Magnet"
    barrier = "Barrier"
    mounting_base = "Base Mount"
    mounting_plate = "Plate Mount"
    banding = "Banding"
    sleeve = "Sleeve"
    rotorcover = "Rotor Cover"
    slotwjinsulation = "Slot Water Jacket Insulation"
    slotwjwall = "Slot Water Jacket Wall"
    slotwjduct = "Slot Water Jacket Duct"
    slotwjduct_nodetail = "Slot Water Jacket Duct (no detail)"
    cowling = "Cowling"
    cowling_gril = "Cowling Grill"
    brush = "Brush"
    commutator = "Commutator"
    airgap = "Airgap"
    dxfimpo = "DXF Impo"
    useradded = "User added"
    notype = "No type"
    background = "Background"
    invalidduct = "Invalid Duct"
    impreglossslot_acloss = "Stator Proximity Loss Slot"
    adaptive = "Adaptive Region"
    unknown = "Unknown"
