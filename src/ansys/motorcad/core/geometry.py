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
from cmath import polar, rect
from copy import deepcopy
from enum import Enum
from math import acos, atan2, cos, degrees, fabs, floor, inf, isclose, radians, sin, sqrt
import warnings
from warnings import warn

GEOM_TOLERANCE = 1e-6


class RegionType(Enum):
    """Provides an enumeration for storing Motor-CAD region types."""

    stator = "Stator"
    rotor = "Rotor"
    slot_area_stator = "Stator Slot Area"
    slot_area_stator_deprecated = "Stator Slot"
    slot_area_rotor = "Rotor Slot Area"
    slot_split = "Split Slot"
    stator_liner = "Stator Liner"
    rotor_liner = "Rotor Liner"
    wedge = "Wedge"
    stator_duct = "Stator Duct"
    housing = "Housing"
    housing_magnetic = "Magnetic Housing"
    stator_impreg = "Stator Impreg"
    impreg_gap = "Impreg Gap"
    stator_copper = "Stator Copper"
    stator_copper_ins = "Stator Copper Insulation"
    stator_divider = "Stator Divider"
    stator_slot_spacer = "Stator Slot Spacer"
    stator_separator = "Stator slot separator"
    coil_insulation = "Coil Insulation"
    stator_air = "Stator Air"
    rotor_hub = "Rotor hub"
    rotor_air = "Rotor Air"
    rotor_air_exc_liner = "Rotor Air (excluding liner area)"
    rotor_pocket = "Rotor Pocket"
    pole_spacer = "Pole Spacer"
    rotor_slot = "Rotor Slot"
    rotor_bar_end_ring = "Rotor Bar End Ring"
    coil_separator = "Coil Separator"
    damper_bar = "Damper Bar"
    wedge_rotor = "Rotor Wedge"
    rotor_divider = "Rotor Divider"
    rotor_copper_ins = "Rotor Copper Insulation"
    rotor_copper = "Rotor Copper"
    rotor_impreg = "Rotor Impreg"
    shaft = "Shaft"
    axle = "Axle"
    rotor_duct = "Rotor Duct"
    magnet = "Magnet"
    barrier = "Barrier"
    mounting_base = "Base Mount"
    mounting_plate = "Plate Mount"
    endcap = "Endcap"
    banding = "Banding"
    sleeve = "Sleeve"
    rotor_cover = "Rotor Cover"
    slot_wj_insulation = "Slot Water Jacket Insulation"
    slot_wj_wall = "Slot Water Jacket Wall"
    slot_wj_duct = "Slot Water Jacket Duct"
    slot_wj_duct_no_detail = "Slot Water Jacket Duct (no detail)"
    cowling = "Cowling"
    cowling_gril = "Cowling Grill"
    cowling_grill_hole = "Cowling Grill Hole"
    brush = "Brush"
    bearings = "Bearings"
    commutator = "Commutator"
    airgap = "Airgap"
    dxf_import = "DXF Import"
    impreg_loss_lot_ac_loss = "Stator Proximity Loss Slot"
    adaptive = "Adaptive Region"


RegionType.slot_area_stator_deprecated.__doc__ = "Only for use with Motor-CAD 2025.1 and earlier"


class Region(object):
    """Create geometry region.

    Parameters
    ----------
    region_type: RegionType
        Type of region
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected
    """

    def __init__(self, region_type=RegionType.adaptive, motorcad_instance=None):
        """Initialise Region."""
        if not isinstance(region_type, RegionType):
            warnings.warn(
                "The first parameter of creating a new region has changed to region_type."
                " Please use named parameters ```Region(motorcad_instance=mc``` and add a"
                " region type"
            )
            # Try and catch case where user has added Motor-CAD instance without using named param
            motorcad_instance = region_type
            region_type = None

        elif region_type == RegionType.adaptive:
            warnings.warn(
                "It is strongly recommended to set a region_type when creating new regions."
                " Creating new regions with no type will be deprecated in a future release"
            )

        self._name = ""
        self._base_name = ""
        self._material = "air"
        self._colour = (0, 0, 0)
        self._area = 0.0
        self._centroid = Coordinate(0, 0)
        self._region_coordinate = Coordinate(0, 0)
        self._duplications = 1
        self._entities = EntityList()
        self._parent_name = ""
        self._child_names = []
        self._motorcad_instance = motorcad_instance
        self._region_type = region_type
        self._mesh_length = 0
        self._linked_region = None
        self._singular = False
        self._lamination_type = ""

    def __eq__(self, other):
        """Override the default equals implementation for Region."""
        return (
            isinstance(other, Region)
            and self._name == other._name
            # and self.area == other.area ->
            # Already check entities - can't expect user to calculate area
            # and self.centroid == other.centroid ->
            # Centroid calculated from entities - can't expect user to calculate
            # and self.region_coordinate == other.region_coordinate ->
            # Region coordinate is an output, cannot guarantee will be same for identical regions
            and self._duplications == other._duplications
            and self._entities == other._entities
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
        self._entities.append(entity)

    def insert_entity(self, index, entity):
        """Insert entity to list of region entities at given index.

        Parameters
        ----------
        index : int
            Index of which to insert at
        entity : Line or Arc
            Line/arc entity class instance
        """
        self._entities.insert(index, entity)

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
        for entity in self._entities:
            if (entity.start == entity_remove.start) & (entity.end == entity_remove.end):
                if type(entity) == Line:
                    self._entities.remove(entity)
                elif type(entity) == Arc:
                    if (entity.centre == entity_remove.centre) & (
                        entity.radius == entity_remove.radius
                    ):
                        self._entities.remove(entity)

    def replace(self, replacement_region):
        """Replace self with another region.

        This method replaces region entities with entities from the replacement region object,
        such as an imported DXF region.

        Parameters
        ----------
        replacement_region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object whose entities are to replace those of the
            existing region.
        """
        # Remove existing entities from the region object
        self._entities.clear()

        # Set the region object entities to be the list of replacement region entities
        self._entities = deepcopy(replacement_region.entities)

    # method to receive region from Motor-CAD and create python object
    @classmethod
    def _from_json(cls, json, motorcad_instance=None):
        """Convert the class from a JSON object.

        Parameters
        ----------
        json: dict
            Dictionary representing the geometry region.
        motorcad_instance : ansys.motorcad.core.MotorCAD
            Motor-CAD instance to connect to. The default is ``None``.
        """
        has_region_type = "region_type" in json
        is_magnet = has_region_type and (json["region_type"] == RegionType.magnet.value)

        if is_magnet:
            new_region = RegionMagnet(motorcad_instance)
            new_region._magnet_angle = json["magnet_angle"]
            new_region._br_multiplier = json["magnet_magfactor"]
            new_region._magnet_polarity = json["magnet_polarity"]
            new_region._br_magnet = json["magnet_br_value"]
        else:
            if has_region_type:
                new_region = cls(
                    motorcad_instance=motorcad_instance, region_type=RegionType(json["region_type"])
                )
            else:
                new_region = cls(motorcad_instance=motorcad_instance)

        # self.Entities = json.Entities

        if "name_unique" in json:
            new_region.name = json["name_unique"]
        else:
            new_region.name = json["name"]

        new_region._base_name = json["name"]
        new_region.material = json["material"]
        new_region._colour = (json["colour"]["r"], json["colour"]["g"], json["colour"]["b"])
        new_region._area = json["area"]

        new_region._centroid = Coordinate(json["centroid"]["x"], json["centroid"]["y"])
        new_region._region_coordinate = Coordinate(
            json["region_coordinate"]["x"], json["region_coordinate"]["y"]
        )
        new_region._duplications = json["duplications"]
        new_region._entities = _convert_entities_from_json(json["entities"])
        new_region._parent_name = json["parent_name"]
        new_region._child_names = json["child_names"]

        if "mesh_length" in json:
            new_region._mesh_length = json["mesh_length"]

        if "singular" in json:
            new_region._singular = json["singular"]

        if "lamination_type" in json:
            new_region._lamination_type = json["lamination_type"]

        return new_region

    # method to convert python object to send to Motor-CAD
    def _to_json(self):
        """Convert from Python class to Json object.

        Returns
        -------
        dict
            Geometry region json representation
        """
        if self._region_type == RegionType.adaptive:
            lamination_type = self._lamination_type
        else:
            lamination_type = ""

        region_dict = {
            "name": self._name,
            "name_base": self._base_name,
            "material": self._material,
            "colour": {"r": self._colour[0], "g": self._colour[1], "b": self._colour[2]},
            "area": self._area,
            "centroid": {"x": self._centroid.x, "y": self._centroid.y},
            "region_coordinate": {"x": self._region_coordinate.x, "y": self._region_coordinate.y},
            "duplications": self._duplications,
            "entities": _convert_entities_to_json(self.entities),
            "parent_name": self._parent_name,
            "region_type": self._region_type.value,
            "mesh_length": self._mesh_length,
            "on_boundary": False if self._linked_region is None else True,
            "singular": self._singular,
            "lamination_type": lamination_type,
        }

        return region_dict

    def is_closed(self):
        """Check whether region entities create a closed region.

        Returns
        -------
        Boolean
            Whether region is closed
        """
        if len(self._entities) > 0:
            entity_first = self._entities[0]
            entity_last = self._entities[-1]

            is_closed = get_entities_have_common_coordinate(entity_first, entity_last)

            for i in range(len(self._entities) - 1):
                is_closed = get_entities_have_common_coordinate(
                    self._entities[i], self._entities[i + 1]
                )

            return is_closed
        else:
            return False

    @property
    def parent_name(self):
        """Get or set the region parent name."""
        return self._parent_name

    @parent_name.setter
    def parent_name(self, name):
        self._parent_name = name

    @property
    def linked_region(self):
        """Get or set linked duplication/unite region."""
        return self._linked_region

    @linked_region.setter
    def linked_region(self, region):
        self._linked_region = region
        region._linked_region = self

    @property
    def singular(self):
        """Get or set if region is singular."""
        return self._singular

    @singular.setter
    def singular(self, singular):
        self._singular = singular

    @property
    def child_names(self):
        """Get child names list.

        Returns
        -------
        list of string
            list of child region names
        """
        return self._child_names

    @property
    def region_type(self):
        """Get region type.

        Returns
        -------
        RegionType
        """
        return self._region_type

    @region_type.setter
    def region_type(self, region_type):
        self._region_type = region_type

    @property
    def motorcad_instance(self):
        """Get or set the linked Motor-CAD instance."""
        return self._motorcad_instance

    @motorcad_instance.setter
    def motorcad_instance(self, mc):
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
        """Get or set parent region from Motor-CAD.

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        self._check_connection()
        return self.motorcad_instance.get_region(self.parent_name)

    @parent.setter
    def parent(self, region):
        self._parent_name = region.name

    @property
    def lamination_type(self):
        """Get or set lamination type of region from Motor-CAD.

        Returns
        -------
            string
        """
        return self._lamination_type

    @lamination_type.setter
    def lamination_type(self, lamination_type):
        if self.region_type == RegionType.adaptive:
            self._lamination_type = lamination_type
        else:
            raise Exception(
                "It is currently only possible to set lamination type for adaptive regions"
            )

    @property
    def name(self):
        """Get or set region name."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def material(self):
        """Get or set region material name."""
        return self._material

    @material.setter
    def material(self, material):
        self._material = material

    @property
    def colour(self):
        """Get or set region colour."""
        return self._colour

    @colour.setter
    def colour(self, colour):
        self._colour = colour

    @property
    def duplications(self):
        """Get or set number of region duplications for the full machine."""
        return self._duplications

    @duplications.setter
    def duplications(self, duplications):
        self._duplications = duplications

    @property
    def entities(self):
        """Get or set the list of entities in the region."""
        return self._entities

    @entities.setter
    def entities(self, entities):
        self._entities = entities

    @property
    def mesh_length(self):
        """Get or set the mesh length to use, or 0 for default."""
        return self._mesh_length

    @mesh_length.setter
    def mesh_length(self, mesh_length):
        self._mesh_length = mesh_length

    @property
    def area(self):
        """Get the region area."""
        return self._area

    @property
    def centroid(self):
        """Get the region centroid."""
        return self._centroid

    @property
    def region_coordinate(self):
        """Get the reference coordinate within the region."""
        return self._region_coordinate

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
            region._entities.clear()
            region._centroid = self._centroid.mirror(mirror_line)
            region._region_coordinate = self._region_coordinate.mirror(mirror_line)
            region._child_names = []

            if unique_name:
                region._name = region._name + "_mirrored"

            for entity in self._entities:
                region.add_entity(entity.mirror(mirror_line))

            return region
        else:
            raise Exception("Region can only be mirrored about Line()")

    def rotate(self, centre_point, angle):
        """Rotate Region around a point for a given angle.

        Parameters
        ----------
        centre_point : Coordinate
            point to rotate Coordinate around.
        angle : float
            Angle of rotation in degrees. Anticlockwise direction is positive.
        """
        for entity in self._entities:
            entity.rotate(centre_point, angle)

    def translate(self, x, y):
        """Translate Region by specified x,y distances.

        Parameters
        ----------
        x : float
            x distance.
        y : float
            y distance.
        """
        for entity in self._entities:
            entity.translate(x, y)

    def update(self, region):
        """Update class fields from another region.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object
        """
        self._name = region._name
        self._material = region._material
        self._colour = region._colour
        self._area = region._area
        self._centroid = deepcopy(region._centroid)
        self._region_coordinate = deepcopy(region._region_coordinate)
        self._duplications = region._duplications
        self._entities = deepcopy(region._entities)
        self._parent_name = region._parent_name
        self._child_names = region._child_names
        self._motorcad_instance = region._motorcad_instance

    def _check_connection(self):
        """Check mc connection for region."""
        if self._motorcad_instance is None:
            raise Exception(
                "A Motor-CAD connection is required for this function"
                + ", please set self.motorcad_instance to a valid Motor-CAD instance"
            )
        if self._motorcad_instance.connection._wait_for_response(1) is False:
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
        return self._entities.points

    def add_point(self, point):
        """Add a new point into region on an existing Line/Arc.

        The point must already exist on a Line/Arc belonging to the region. The entity will be split
        and 2 new entities created.

        Parameters
        ----------
        point : Coordinate
            Coordinate at which to add new point
        """
        for pos, entity in enumerate(self._entities):
            if entity.coordinate_on_entity(point):
                if isinstance(entity, Line):
                    new_entity_1 = Line(entity.start, point)
                    new_entity_2 = Line(point, entity.end)
                elif isinstance(entity, Arc):
                    new_entity_1 = Arc(entity.start, point, entity.centre, entity.radius)
                    new_entity_2 = Arc(point, entity.end, entity.centre, entity.radius)
                else:
                    raise Exception("Entity type is not Arc or Line")

                self._entities.pop(pos)
                self._entities.insert(pos, new_entity_1)
                self._entities.insert(pos + 1, new_entity_2)
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
        for entity in self._entities:
            if entity.start == old_coordinates:
                entity.start = deepcopy(new_coordinates)
            if entity.end == old_coordinates:
                entity.end = deepcopy(new_coordinates)
            if isinstance(entity, Arc):
                # Check Arc is still valid
                _ = entity.centre

    def consolidate_lines(self):
        """Consolidate separate Line objects into a single Line object where possible.

        If the current and previous entities are both Line entity types with the same angle, the
        current entity is removed and the previous entity is extended to the end point of the
        removed entity.

        """
        entities_to_remove = []
        # last entity of the region
        entity_n = self._entities[len(self._entities) - 1]
        # for each entity in the region
        for entity in self._entities:
            # if the entity is a line
            if isinstance(entity, Line) and isinstance(entity_n, Line):
                if (
                    isclose(entity.angle, entity_n.angle, abs_tol=1e-6)
                    or isclose(entity.angle, entity_n.angle - 180, abs_tol=1e-6)
                    or isclose(entity.angle, entity_n.angle + 180, abs_tol=1e-6)
                    or isclose(entity.angle, entity_n.angle - 360, abs_tol=1e-6)
                    or isclose(entity.angle, entity_n.angle + 360, abs_tol=1e-6)
                ):
                    entity_n.end = entity.end
                    entities_to_remove.append(entity)
                else:
                    entity_n = entity
            else:
                entity_n = entity

        for entity in entities_to_remove:
            self.remove_entity(entity)

    def _round_corner(self, corner_coordinate, radius, distance_limit):
        """Round the corner of a region.

        The corner coordinates must already exist on two entities belonging to the region.
        The two entities adjacent to the corner are shortened, and an arc is created between
        them.

        Parameters
        ----------
        corner_coordinate : ansys.motorcad.core.geometry.Coordinate
            Coordinate of the corner to round.
        radius : float
            Radius to round the corner by.
        distance_limit : float
            Maximum distance that the adjacent entities can be shortened by.
        adj_entity_lengths : list of float
            List of lengths of the original region entities that are adjacent to the corner to
            round.
        """
        # If radius is 0, do nothing
        if radius == 0:
            return

        # Find adjacent entities. There should be 2 entities adjacent to the corner. Going
        # anti-clockwise around the region, the entities before and after the corner will be
        # adj_entity[0] and adj_entity[1] respectively.
        adj_entities = []
        adj_entity_indices = []
        for index in range(len(self._entities)):
            entity = self._entities[index]
            if entity.coordinate_on_entity(corner_coordinate):
                adj_entities.append(entity)
                adj_entity_indices.append(index)
        # If no adjacent entities are found, the point provided is not a corner
        if not adj_entities:
            raise Exception(
                "Failed to find point on entity in region. "
                "You must specify a corner in this region."
            )
        # If only one adjacent entity is found, the point provided is not a corner
        if len(adj_entities) == 1:
            raise Exception(
                "Point found on only one entity in region. "
                "You must specify a corner in this region."
            )
        # If the adj_entities are the first and last entities of the region, then the entity after
        # the corner will be found first (entity 0). In this case, swap the entities around so that
        # adj_entity[0] is always the entity before the corner (corner is adj_entity[0].end).
        if corner_coordinate == self._entities[len(self._entities) - 1].end:
            adj_entities[0] = self._entities[len(self._entities) - 1]
            adj_entities[1] = self._entities[0]
            adj_entity_indices[0] = len(self._entities) - 1
            adj_entity_indices[1] = 0

        # If we have arc rounding, we need to find the angle at the intersection of the arc and the
        # rounding arc. We don't know this position in advance, so iterate up to 100 times to find
        # the correct distance.
        distance = 0
        converged = False
        for iteration in range(100):
            # get the angles of the adjacent entities. For a line, this is a property of the entity
            # object. For an arc, approximate the arc by a straight line from the arc start or end
            # (whichever is the corner coordinate) to a point 0.0001 mm along the arc.
            adj_entity_angles = []
            for entity in adj_entities:
                if isinstance(entity, Arc):
                    if corner_coordinate == entity.start:
                        point_on_arc1 = entity.get_coordinate_from_distance(entity.start, distance)
                        point_on_arc2 = entity.get_coordinate_from_distance(
                            entity.start, distance + 0.0001
                        )
                    else:
                        point_on_arc1 = entity.get_coordinate_from_distance(
                            entity.end, distance + 0.0001
                        )
                        point_on_arc2 = entity.get_coordinate_from_distance(entity.end, distance)
                    line_on_arc = Line(point_on_arc1, point_on_arc2)
                    adj_entity_angles.append(line_on_arc.angle)
                else:
                    adj_entity_angles.append(entity.angle)

            # calculate the internal angle of the corner.
            corner_internal_angle = 180 + (adj_entity_angles[0] - adj_entity_angles[1])
            # If this is more than 360, subtract 360.
            if corner_internal_angle > 360:
                corner_internal_angle = corner_internal_angle - 360
            # If it is less than zero, add 360.
            elif corner_internal_angle < 0:
                corner_internal_angle = corner_internal_angle + 360

            # calculate the arc angle
            corner_arc_angle = 180 - corner_internal_angle

            # If the arc angle is zero, the point provided is not a corner.
            if (
                isclose(corner_arc_angle, 0, abs_tol=1e-3)
                or isclose(corner_arc_angle, 360, abs_tol=1e-3)
                or isclose(corner_arc_angle, -360, abs_tol=1e-3)
            ):
                return

            # Calculate distances by which the adjacent entities are shortened
            previous_distance = distance
            half_chord = radius * sin(radians(corner_arc_angle) / 2)
            distance = abs(half_chord / (sin(radians(corner_internal_angle) / 2)))

            # Check if distance has converged, or if iterative convergence not needed
            if (isinstance(adj_entities[0], Line) and isinstance(adj_entities[1], Line)) or isclose(
                previous_distance, distance, abs_tol=1e-3
            ):
                converged = True
                break

        # Raise assertion if not converged, as radius probably not valid
        if converged == False:
            raise ValueError("Cannot find intersection. Check if radius is too large")

        # check that the  distances by which the adjacent entities are shortened are less than
        # the distance_limit.
        if distance_limit < distance:
            raise ValueError(
                "Corner radius is too large for these entities. "
                "You must specify a smaller radius."
            )
        # get and set the new start and end coordinates for the adjacent entities
        adj_entities[0].end = adj_entities[0].get_coordinate_from_distance(
            corner_coordinate, distance
        )
        adj_entities[1].start = adj_entities[1].get_coordinate_from_distance(
            corner_coordinate, distance
        )

        # if the internal angle of the corner is more than 180, a negative radius must be applied
        if corner_internal_angle > 180:
            e = -1
        else:
            e = 1

        # create the round corner arc and insert at the index after the first adjacent entity.
        corner_arc = Arc(adj_entities[0].end, adj_entities[1].start, radius=e * radius)
        self.insert_entity(adj_entity_indices[0] + 1, corner_arc)

    def round_corner(self, corner_coordinate, radius, maximise=True):
        """Round the corner of a region.

        The corner coordinates must already exist on two entities belonging to the region.
        The two entities adjacent to the corner are shortened, and an arc is created between
        them.

        Parameters
        ----------
        corner_coordinate : ansys.motorcad.core.geometry.Coordinate
            Coordinate of the corner to round.
        radius : float
            Radius to round the corner by.
        maximise : bool
            Whether to maximise the possible radius if the radius provided is too large.
        """
        # get the original entities before any corner rounding has been done
        entities_orig = deepcopy(self._entities)
        # get the lengths of the original adjacent entities before any corner rounding
        adj_entity_lengths = []
        for index in range(len(entities_orig)):
            entity = entities_orig[index]
            if entity.coordinate_on_entity(corner_coordinate):
                adj_entity_lengths.append(entity.length)
        # find the limit for how much an adjacent entity may be shortened by:
        distance_limit = 10000
        for index in range(len(adj_entity_lengths)):
            if adj_entity_lengths[index] < distance_limit:
                distance_limit = adj_entity_lengths[index]

        # if the corner radius is too large, an exception will be raised
        if not maximise:
            # round the corner
            self._round_corner(corner_coordinate, radius, distance_limit)
        # if the corner radius is too large, maximise the corner radius that is short enough for
        # the adjacent entities. The adjacent entities can only be shortened to half the original
        # entity length before any corner rounding
        else:
            try:
                # try to round the corner with the specified radius
                self._round_corner(corner_coordinate, radius, distance_limit)
            except ValueError as e:
                if "Corner radius is too large for these entities" in str(e):
                    new_corner_radius = round(radius, 1)
                    # iterate 100 times to find a maximum suitable corner radius
                    for iteration in range(100):
                        # subtract 0.1 mm from the previous corner radius that was tried
                        new_corner_radius -= 0.1
                        try:
                            # try to round the corner with the new shorter radius
                            self._round_corner(corner_coordinate, new_corner_radius, distance_limit)
                            break
                        except ValueError as e:
                            if "Corner radius is too large for these entities" in str(e):
                                # try 100 iterations
                                if iteration < 99:
                                    pass
                                # if the radius is still too large on the final iteration, raise
                                # the exception
                                else:
                                    raise e
                # if any other exception is raised by the corner rounding attempt, raise the
                # exception
                else:
                    raise e

    def round_corners(self, corner_coordinates, radius, maximise=True):
        """Round multiple corners of a region.

        Each corner coordinate must already exist on two entities belonging to the region.
        The two entities adjacent to each corner are shortened, and an arc is created
        between them.

        Parameters
        ----------
        corner_coordinates : list of ansys.motorcad.core.geometry.Coordinate
            List of coordinates of the corners to round.
        radius : float
            Radius to round the corners by.
        maximise : bool
            Whether to maximise the possible radius if the radius provided is too large.
        """
        # if the corner radius is too large, an exception will be raised
        if not maximise:
            # get the original entities before any corner rounding has been done
            entities_orig = deepcopy(self._entities)
            # apply the rounding to each corner in turn
            for corner in corner_coordinates:
                # get the lengths of the original adjacent entities before any corner rounding
                adj_entity_lengths = []
                for index in range(len(entities_orig)):
                    entity = entities_orig[index]
                    if entity.coordinate_on_entity(corner):
                        adj_entity_lengths.append(entity.length)

                # find the distance limit that the adjacent entities can be shortened by
                distance_limit = 10000
                for index in range(len(adj_entity_lengths)):
                    if adj_entity_lengths[index] < distance_limit:
                        distance_limit = adj_entity_lengths[index]

                # round the corner
                self._round_corner(corner, radius, distance_limit)
        # if the corner radius is too large, maximise the corner radius that is short enough for
        # the adjacent entities. The adjacent entities can only be shortened to half the original
        # entity length before any corner rounding
        else:
            # apply the rounding to each corner in turn
            for corner in corner_coordinates:
                # get the original entities before any corner rounding has been done
                entities_orig = deepcopy(self._entities)
                # get the lengths of the original adjacent entities before any corner rounding
                adj_entity_lengths = []
                for index in range(len(entities_orig)):
                    entity = entities_orig[index]
                    if entity.coordinate_on_entity(corner):
                        adj_entity_lengths.append(entity.length)
                # find the distance limit that the adjacent entities can be shortened by
                distance_limit = 10000
                for index in range(len(adj_entity_lengths)):
                    if adj_entity_lengths[index] < distance_limit:
                        distance_limit = adj_entity_lengths[index]
                try:
                    # try to round the corner with the specified radius
                    self._round_corner(corner, radius, distance_limit)
                except ValueError as e:
                    if "Corner radius is too large for these entities" in str(e):
                        new_corner_radius = round(radius, 1)
                        # iterate 100 times to find a maximum suitable corner radius
                        for iteration in range(100):
                            # subtract 0.1 mm from the previous corner radius that was tried
                            new_corner_radius -= 0.1
                            try:
                                # try to round the corner with the new shorter radius
                                self._round_corner(corner, new_corner_radius, distance_limit)
                                break
                            except ValueError as e:
                                if "Corner radius is too large for these entities" in str(e):
                                    # try 100 iterations
                                    if iteration < 99:
                                        pass
                                    # if the radius is still too large on the final iteration, raise
                                    # the exception
                                    else:
                                        raise e
                    # if any other exception is raised by the corner rounding attempt, raise the
                    # exception
                    else:
                        raise e

    def limit_arc_chord(self, max_chord_height):
        """Limit the chord height for arcs in a region.

        Subdivide arcs if required to ensure the arc's chord height (the distance between the arc
        midpoint and the midpoint of a line between the start and end) is lower than the specified
        value. This can be used to force a fine FEA mesh around entities with high curvature.

        Parameters:
            max_chord_height: float
                The maximum chord height allowed.
        """
        new_entity_list = []
        for entity in self.entities:
            if (
                isinstance(entity, Arc)
                and (entity.radius != 0)
                and (fabs(entity.radius * 2) > max_chord_height)
            ):
                # Find maximum arc angle so the chord height is equal to the required maximum error
                max_angle = degrees(2 * acos(1 - max_chord_height / fabs(entity.radius)))

                # Find how many segments are needed to achieve this
                if max_angle > 0:
                    segmentation = floor(entity.total_angle / max_angle)
                else:
                    segmentation = 1

                # If required, split the arc into segments
                if segmentation > 1:
                    segment_start = entity.start
                    for segment in range(1, segmentation + 1):
                        segment_end = entity.get_coordinate_from_distance(
                            entity.start, fraction=segment / segmentation
                        )
                        new_arc = Arc(segment_start, segment_end, entity.centre, entity.radius)
                        # Add to the list
                        new_entity_list.append(new_arc)
                        # Ready for next segment
                        segment_start = segment_end
                else:
                    # Arc already OK, just add to list as-is
                    new_entity_list.append(entity)
            else:
                # Add to list unchanged
                new_entity_list.append(entity)

        # Update the entity list
        self.entities = new_entity_list

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
        for entity in self._entities:
            if (coordinate_1 == entity.start) and (coordinate_2 == entity.end):
                return entity
            elif (coordinate_1 == entity.end) and (coordinate_2 == entity.start):
                return entity

        return None


class RegionMagnet(Region):
    """Create magnet geometry region.

    Parameters
    ----------
    motorcad_instance: ansys.motorcad.core.MotorCAD
        Motor-CAD instance currently connected
    """

    def __init__(self, motorcad_instance=None):
        """Initialise Magnet Region."""
        super().__init__(RegionType.magnet, motorcad_instance)
        self._magnet_angle = 0.0
        self._br_multiplier = 0.0
        self._br_magnet = 0.0
        self._magnet_polarity = ""

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        dict
            Dictionary of the geometry region represented as JSON.
        """
        region_dict = super()._to_json()

        region_dict["magnet_magfactor"] = self._br_multiplier
        region_dict["magnet_angle"] = self._magnet_angle
        region_dict["magnet_polarity"] = self._magnet_polarity

        return region_dict

    @property
    def br_multiplier(self):
        """Br multiplier.

        Returns
        -------
        float
        """
        return self._br_multiplier

    @br_multiplier.setter
    def br_multiplier(self, br_multiplier):
        self._br_multiplier = br_multiplier

    @property
    def br_value(self):
        """Br value of magnet before Br multiplier applied.

        Returns
        -------
        float
        """
        return self._br_magnet

    @property
    def magnet_angle(self):
        """Angle of the magnet in degrees.

        Returns
        -------
        float
        """
        return self._magnet_angle

    @magnet_angle.setter
    def magnet_angle(self, magnet_angle):
        self._magnet_angle = magnet_angle

    @property
    def br_x(self):
        """X-axis component of br value.

        Returns
        -------
        float
        """
        return cos(radians(self.magnet_angle)) * self.br_used

    @property
    def br_y(self):
        """Y-axis component of the br value.

        Returns
        -------
        float
        """
        return sin(radians(self.magnet_angle)) * self.br_used

    @property
    def br_used(self):
        """Br used after applying Br multiplier.

        Returns
        -------
        float
        """
        return self._br_magnet * self.br_multiplier

    @property
    def magnet_polarity(self):
        """Polarity of the magnet.

        Returns
        -------
        string
        """
        return self._magnet_polarity

    @magnet_polarity.setter
    def magnet_polarity(self, value):
        self._magnet_polarity = value


class Coordinate(object):
    """Provides the Python representation of a coordinate in two-dimensional space.

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
            and isclose(self.x, other.x, abs_tol=GEOM_TOLERANCE)
            and isclose(self.y, other.y, abs_tol=GEOM_TOLERANCE)
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
            Point to rotate Coordinate around.
        angle : float
            Angle of rotation in degrees. Anticlockwise direction is positive.
        """
        angle_r = radians(angle)
        x_new = centre_point.x + (
            (cos(angle_r) * (self.x - centre_point.x)) + (-sin(angle_r) * (self.y - centre_point.y))
        )
        y_new = centre_point.y + (
            (sin(angle_r) * (self.x - centre_point.x)) + (cos(angle_r) * (self.y - centre_point.y))
        )
        self.x = x_new
        self.y = y_new

    def translate(self, x, y):
        """Translate Coordinate by specified x,y distances.

        Parameters
        ----------
        x : float
            x distance.
        y : float
            y distance.
        """
        self.x += x
        self.y += y

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

    def rotate(self, centre_point, angle):
        """Rotate entity around a point for a given angle.

        Parameters
        ----------
        centre_point : Coordinate
            Coordinate to rotate line around.
        angle : float
            Angle of rotation in degrees. Anticlockwise direction is positive.
        """
        self.start.rotate(centre_point, angle)
        self.end.rotate(centre_point, angle)

    def translate(self, x, y):
        """Translate Entity by specified x,y distances.

        Parameters
        ----------
        x : float
            x distance.
        y : float
            y distance.
        """
        self.start.translate(x, y)
        self.end.translate(x, y)

    def get_intersection(self, entity):
        """Get intersection Coordinate of entity with another entity.

        Returns None if intersection not found.

        Parameters
        ----------
        entity : ansys.motorcad.core.geometry.Line or ansys.motorcad.core.geometry.Arc

        Returns
        -------
        ansys.motorcad.core.geometry.Coordinate or list of Coordinate or None
        """
        if isinstance(self, Line):
            if isinstance(entity, Line):
                points = self.get_line_intersection(entity)
            elif isinstance(entity, Arc):
                points = entity.get_line_intersection(self)
            else:
                raise Exception("Entity type is not Arc or Line")
        else:
            if isinstance(entity, Line):
                points = self.get_line_intersection(entity)
            elif isinstance(entity, Arc):
                points = self.get_arc_intersection(entity)
        if points:
            intersections = []
            if type(points) == list:
                for point in points:
                    if self.coordinate_on_entity(point):
                        intersections.append(point)
            else:
                if self.coordinate_on_entity(points):
                    intersections.append(points)
            if intersections:
                return intersections
            else:
                return None
        else:
            return None


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
        return isclose(self.end.x - self.start.x, 0, abs_tol=GEOM_TOLERANCE)

    @property
    def is_horizontal(self):
        """Check whether line is horizontal.

        Returns
        -------
            boolean
        """
        return isclose(self.end.y - self.start.y, 0, abs_tol=GEOM_TOLERANCE)

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

    def get_coordinate_from_percentage_distance(self, ref_coordinate, fraction):
        """Get the coordinate at a fractional distance along the line from the reference coord.

        .. note::
           This method is deprecated. Use the :func:`Line.get_coordinate_from_distance`
           method with the `fraction = ` or `percentage =` argument.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        fraction : float
            Fractional distance along Line.

        Returns
        -------
        Coordinate
            Coordinate at fractional distance along Line.
        """
        warn(
            "get_coordinate_from_percentage_distance() WILL BE DEPRECATED SOON - "
            "USE get_coordinate_from_distance instead with the `fraction = ` or `percentage = ` "
            "optional argument",
            DeprecationWarning,
        )
        return self.get_coordinate_from_distance(ref_coordinate, fraction=fraction)

    def get_coordinate_from_distance(
        self, ref_coordinate, distance=None, fraction=None, percentage=None
    ):
        """Get the coordinate at the specified distance along the line from the reference.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        distance : float, optional
            Distance along Line.

        fraction : float, optional
            Fractional distance along Line.

        percentage : float, optional
            Percentage distance along Line.

        Returns
        -------
        Coordinate
            Coordinate at distance along Line.
        """
        if (distance is None) and (fraction is None) and (percentage is None):
            raise Exception("You must provide either a distance, fraction or percentage.")

        if (distance is not None) and (fraction is not None):
            warn("Both distance and fraction provided. Using distance.", UserWarning)
        if (distance is not None) and (percentage is not None):
            warn("Both distance and percentage provided. Using distance.", UserWarning)

        if distance is None:
            if (fraction is not None) and (percentage is not None):
                warn("Both fraction and percentage provided. Using fraction.", UserWarning)
            if fraction is not None:
                distance = self.length * fraction
            elif percentage is not None:
                distance = self.length * (percentage / 100)

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

        return isclose(abs(v1) + abs(v2), self.length, abs_tol=GEOM_TOLERANCE)

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

    def get_arc_intersection(self, arc):
        """Get intersection Coordinates of line with an arc.

        Returns None if intersection not found.

        Parameters
        ----------
        arc : ansys.motorcad.core.geometry.Arc

        Returns
        -------
        ansys.motorcad.core.geometry.Coordinate or list of Coordinate or None
        """
        return arc.get_line_intersection(self)

    def get_coordinate_distance(self, coordinate):
        """Get distance of line with another coordinate."""
        normal_angle = self.angle - 90
        defining_point = Coordinate.from_polar_coords(1, normal_angle)
        normal = Line(Coordinate(0, 0), defining_point)
        normal.translate(coordinate.x, coordinate.y)
        nearest_point = self.get_line_intersection(normal)
        if nearest_point is None:
            return None
        return sqrt((coordinate.x - nearest_point.x) ** 2 + (coordinate.y - nearest_point.y) ** 2)


class _BaseArc(Entity):
    """Internal class to allow creation of Arcs."""

    def __init__(self, start, end, centre, radius):
        """Initialise base Arc object."""
        super().__init__(start, end)
        self.centre = deepcopy(centre)
        self.radius = radius

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

    def get_coordinate_from_percentage_distance(self, ref_coordinate, fraction):
        """Get the coordinate at a fractional distance along the arc from the reference coord.

        .. note::
           This method is deprecated. Use the :func:`Arc.get_coordinate_from_distance`
           method with the `fraction = ` or `percentage =` argument.

        Parameters
        ----------
        ref_coordinate : Coordinate
            Entity reference coordinate.

        fraction : float
            Fractional distance along Arc.

        Returns
        -------
        Coordinate
            Coordinate at fractional distance along Arc.
        """
        warn(
            "get_coordinate_from_percentage_distance() WILL BE DEPRECATED SOON - "
            "USE get_coordinate_from_distance instead with the `fraction = ` or `percentage = ` "
            "optional argument",
            DeprecationWarning,
        )
        return self.get_coordinate_from_distance(ref_coordinate, fraction=fraction)

    def get_coordinate_from_distance(
        self, ref_coordinate, distance=None, fraction=None, percentage=None
    ):
        """Get the coordinate at the specified distance along the arc from the reference coordinate.

        Parameters
        ----------
        ref_coordinate : Coordinate
           Entity reference coordinate.

        distance : float, optional
            Distance along arc.

        fraction : float, optional
            Fractional distance along Arc.

        percentage : float, optional
            Percentage distance along Arc.

        Returns
        -------
        Coordinate
            Coordinate at distance along Arc.
        """
        if (distance is None) and (fraction is None) and (percentage is None):
            raise Exception("You must provide either a distance, fraction or percentage.")

        if (distance is not None) and (fraction is not None):
            warn("Both distance and fraction provided. Using distance.", UserWarning)
        if (distance is not None) and (percentage is not None):
            warn("Both distance and percentage provided. Using distance.", UserWarning)

        if distance is None:
            if (fraction is not None) and (percentage is not None):
                warn("Both fraction and percentage provided. Using fraction.", UserWarning)
            if fraction is not None:
                distance = self.length * fraction
            elif percentage is not None:
                distance = self.length * (percentage / 100)

        ref_coordinate_angle = atan2(
            (ref_coordinate.y - self.centre.y), (ref_coordinate.x - self.centre.x)
        )
        if ref_coordinate == self.end:
            e = -1
        else:
            e = 1
        angle = ref_coordinate_angle + e * (
            distance / self.radius
        )  # sign of the radius accounts for clockwise/anticlockwise arcs
        return self.centre + Coordinate(*rt_to_xy(abs(self.radius), degrees(angle)))

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
        return abs(self.radius * radians(self.total_angle))

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
        return self.coordinate_within_arc_radius(coordinate) and isclose(
            abs(radius), abs(self.radius), abs_tol=GEOM_TOLERANCE
        )

    def get_line_intersection(self, line):
        """Get intersection Coordinates of arc with a line.

        Returns None if intersection not found.

        Parameters
        ----------
        line : ansys.motorcad.core.geometry.Line

        Returns
        -------
        ansys.motorcad.core.geometry.Coordinate or list of Coordinate or None
        """
        # circle of the arc
        a = self.centre.x
        b = self.centre.y
        r = self.radius

        if line.is_vertical:
            # line x coordinate is constant
            x = line.start.x

            A = 1
            B = -2 * b
            C = x**2 - 2 * x * a + a**2 + b**2 - r**2
            D = B**2 - 4 * A * C

            if D < 0:
                # line and circle do not intersect
                return None
            elif D == 0:
                # line and circle intersect at 1 point
                y = -B / (2 * A)
                return Coordinate(x, y)
            else:
                # line and circle intersect at 2 points
                y1 = (-B + sqrt(D)) / (2 * A)
                y2 = (-B - sqrt(D)) / (2 * A)
                return [Coordinate(x, y1), Coordinate(x, y2)]
        else:
            # Normal case, line y is a function of x
            m = line.gradient
            c = line.y_intercept

            A = 1 + m**2
            B = 2 * (m * (c - b) - a)
            C = a**2 + (c - b) ** 2 - r**2

            D = B**2 - 4 * A * C
            if D < 0:
                # line and circle do not intersect
                return None
            elif D == 0:
                # line and circle intersect at 1 point
                x = -B / (2 * A)
                y = m * x + c
                return Coordinate(x, y)
            else:
                # line and circle intersect at 2 points
                x1 = (-B + sqrt(D)) / (2 * A)
                x2 = (-B - sqrt(D)) / (2 * A)
                y1 = m * x1 + c
                y2 = m * x2 + c
                return [Coordinate(x1, y1), Coordinate(x2, y2)]

    def get_arc_intersection(self, arc):
        """Get intersection Coordinates of arc with another arc.

        Returns None if intersection not found.

        Parameters
        ----------
        arc : ansys.motorcad.core.geometry.Arc

        Returns
        -------
        list of Coordinate or None
        """
        # circle of self
        a1 = self.centre.x
        b1 = self.centre.y
        r1 = abs(self.radius)

        # circle of other arc
        a2 = arc.centre.x
        b2 = arc.centre.y
        r2 = abs(arc.radius)

        d = sqrt((a2 - a1) ** 2 + (b2 - b1) ** 2)

        if d > (r1 + r2):
            # if they don't intersect
            return None
        if d < abs(r1 - r2):
            # if one circle is inside the other
            return None
        if d == 0 and r1 == r2:
            # coincident circles
            return None
        else:
            a = (r1**2 - r2**2 + d**2) / (2 * d)
            h = sqrt(r1**2 - a**2)

            x = a1 + a * (a2 - a1) / d
            y = b1 + a * (b2 - b1) / d
            x1 = x + h * (b2 - b1) / d
            y1 = y - h * (a2 - a1) / d

            x2 = x - h * (b2 - b1) / d
            y2 = y + h * (a2 - a1) / d

            return [Coordinate(x1, y1), Coordinate(x2, y2)]

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

        if isclose(l1.gradient, l2.gradient, abs_tol=GEOM_TOLERANCE):
            # three points are on a straight line, no arc is possible
            return None

        # Trying to get the intersection of perpendicular lines:
        #  |
        #  |
        #  |              x
        #  |
        #  |___________________________

        # Work out perpendicular lines
        l1_p = deepcopy(l1)
        l1_p.rotate(l1.midpoint, 90)
        l2_p = deepcopy(l2)
        l2_p.rotate(l2.midpoint, 90)

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


class Arc(_BaseArc):
    """Python representation of Motor-CAD arc entity based upon start, end, (centre or radius).

    Parameters
    ----------
    start : Coordinate
        Start coordinate.

    end : Coordinate
        End coordinate.

    centre : Coordinate, optional
       Centre coordinate.

    radius : float, optional
        Arc radius
    """

    def __init__(self, start, end, centre=None, radius=None):
        """Initialise Arc."""
        self.start = deepcopy(start)
        self.end = deepcopy(end)

        # Centre point of arc is valid in 2 different locations depending on angle smaller or
        # greater than 180 deg
        # Assume angle is <180 deg unless centre and radius are specified and prove otherwise
        self._centre_point_pos = 1

        if radius and centre:
            # User has defined both radius and centre - normally assume angle is acute but need to
            # check for this case
            test_arc = _BaseArc(start, end, centre, radius)
            test = test_arc.total_angle
            if test > 180:
                # Use second location of arc centre point since arc defined as >180 deg
                self._centre_point_pos = 2

        if radius is not None:
            # Always calculate radius
            self.radius = radius
            # Check we can get a valid centre for this geometry
            _ = self.centre
        elif centre is not None:
            # Calc radius from centre point
            r1 = abs(self.start - centre)
            r2 = abs(self.end - centre)
            if not isclose(r1, r2, abs_tol=1e-6):
                raise Exception("It is not possible to draw an arc with this geometry")
            else:
                self.radius = r1

            if _orientation_of_three_points(centre, self.start, self.end) is _Orientation.clockwise:
                self.radius *= -1
        else:
            raise ValueError("You must specify either a centre point or radius for Arc object.")

    @property
    def centre(self):
        """Get centre point of circle defining arc.

        Returns
        -------
            Coordinate
        """
        # Draw line between arc start/end
        # get centre point of that line
        p_centre = (self.end + self.start) / 2
        # Get vector of that line
        v_1 = self.end - self.start
        # Get length div 2
        d1 = abs(v_1) / 2

        # Draw perpendicular line from centre point
        radius, angle = v_1.get_polar_coords_deg()
        perpendicular_angle = angle + 90 * (self.radius / abs(self.radius))

        if abs(self.radius) < d1:
            if (d1 - abs(self.radius)) < GEOM_TOLERANCE:
                # Radius is smaller than possible but within tolerance
                # Bump it to minimum viable radius and preserve sign
                self.radius = d1 * (self.radius / abs(self.radius))
            else:
                raise Exception("It is not possible to draw an arc with this geometry")

        # Get vector from p_centre to centre point of arc
        d_adjacent = sqrt(self.radius**2 - d1**2)
        l_x, l_y = rt_to_xy(d_adjacent, perpendicular_angle)

        # Apply vector to centre point of arc
        if self._centre_point_pos == 1:
            return p_centre + Coordinate(l_x, l_y)
        else:
            # Arc had an angle defined as greater than 180 deg
            return p_centre - Coordinate(l_x, l_y)


class EntityList(list):
    """Generic class for list of Entities."""

    def __eq__(self, other):
        """Compare equality of 2 EntityList objects."""
        return self._entities_same(other, check_reverse=True)

    def __ne__(self, other):
        """Compare difference of 2 EntityList objects."""
        return not self == other

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

        if len(self) != len(entities_to_compare):
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
