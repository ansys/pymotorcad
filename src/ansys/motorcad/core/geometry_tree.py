# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Methods for building geometry trees."""
from copy import deepcopy
import warnings

from ansys.motorcad.core.geometry import (
    Arc,
    Coordinate,
    EntityList,
    Line,
    Region,
    RegionMagnet,
    RegionType,
    rt_to_xy,
)
from ansys.motorcad.core.rpc_client_core import MotorCADError


class GeometryTree(dict):
    """Class used to build geometry trees."""

    def __init__(self, mc=None, create_root_node=True):
        """Initialise the geometry tree.

        Parameters
        ----------
        create_root_node: bool
            Create the root node of the geometry tree.
        """
        super().__init__()
        # increment every time we add a region so that we can automatically assign a
        # unique name to regions on creation
        self._motorcad_instance = mc
        self.unique_region_number = 0

        if create_root_node:
            root = self.create_region(RegionType.no_type)
            self["root"] = root
            root.tree = self
            root.parent = None

        # Reset back to 0 after initialising root node
        self.unique_region_number = 0

        # Tree has root node different to standard tree root
        self._custom_root_node = None

    def __setitem__(self, key, value):
        """Override __setitem___."""
        # Increment unique number if a new region has been added
        self.unique_region_number += 1
        super().__setitem__(key, value)

    def __iter__(self):
        """Define ordering according to tree structure."""
        well_ordered = []

        # Update hardcoded child names so we can add to list by recursively searching children

        for key in self.keys():
            region = self[key]
            region._child_names = []

        for key in self.keys():
            region = self[key]
            if region.parent is not None:
                region.parent._child_names += [region.name]

        for key in self.keys():
            region = self[key]
            region._child_names = sorted(region._child_names)

        def dive(list_to_append, current_region):
            list_to_append.append(current_region)
            for child_name in current_region._child_names:
                dive(list_to_append, self[child_name])

        dive(well_ordered, self.root_node)

        return iter(well_ordered)

    def __str__(self):
        """Return string representation of the geometry tree."""
        string = ""
        starting_level = list(self.values())[0].level

        for node in self:
            relative_level = node.level - starting_level
            string += "│   " * (relative_level - 1)
            if relative_level == 0:
                cap = ""
            elif node == node.parent.children[-1]:
                cap = "└── "
            else:
                cap = "├── "
            string += cap
            string += node.key
            string += "\n"
        return string

    def __eq__(self, other):
        """Define equality operator.

        Equality for trees requires both trees have the same structure.
        Also requires that each region with the same key is equal.
        """

        def dive(node):
            if len(node.children) != len(other[node.key].children):
                return False
            for child in node.children:
                # Making sure each child is in the other corresponding region's children
                if not child.key in other[node.key].child_keys:
                    return False
                if not dive(child):
                    return False
            # Actual equality check of nodes
            if node != other[node.key]:
                return False
            return True

        return dive(self.root_node)

    def __ne__(self, other):
        """Define inequality."""
        return not self.__eq__(other)

    @property
    def root_node(self):
        """Get the root node of the geometry tree."""
        if self._custom_root_node:
            return self._custom_root_node
        else:
            return self["root"]

    @root_node.setter
    def root_node(self, value):
        self._custom_root_node = value

    @classmethod
    def _from_json(cls, tree_json, mc):
        """Return a GeometryTree representation of the geometry defined within a JSON.

        Parameters
        ----------
        tree_json: dict
            JSON to create a tree from (generally, the output of get_geometry_tree()).
        Returns
        -------
        GeometryTree
        """
        geometry_tree = cls()
        """Initialize tree.

        Parameters
        ----------
        tree: dict
        """
        tree_json = tree_json["regions"]

        geometry_tree._motorcad_instance = mc

        for region_name in tree_json:
            # Add all regions as children of root node
            region = TreeRegion.from_json(geometry_tree, tree_json[region_name], mc)
            geometry_tree._add_region(region)

        # Don't use for x in y syntax yet as this uses __iter__
        # Not sure on this behaviour until parents are set

        # Establish linkages between linked regions
        for key in geometry_tree.keys():
            for linked_region_name in geometry_tree[key]._linked_region_names:
                geometry_tree[key].linked_regions.append(geometry_tree[linked_region_name])

        # Do parenting
        for key in geometry_tree.keys():
            if geometry_tree[key]._parent_name != "":
                geometry_tree[key].parent = geometry_tree[geometry_tree[key]._parent_name]

        return geometry_tree

    def _to_json(self):
        """Return a dict object used to set geometry."""
        regions = dict()
        for node in self:
            if node.key != "root":
                if node.region_type == RegionType.magnet:
                    regions[node.key] = TreeRegionMagnet._to_json(node)
                else:
                    regions[node.key] = TreeRegion._to_json(node)
        return {"regions": regions}

    def get_region(self, region_name):
        """Get a region from the tree (case-insensitive).

        Parameters
        ----------
        region_name: str
            Name of the region to get.
        """
        if isinstance(region_name, str):
            if region_name.lower() in self.lowercase_keys:
                lower_key = region_name.lower()
                return self[self.lowercase_keys[lower_key]]
            raise KeyError()
        elif isinstance(region_name, TreeRegion):
            return region_name
        else:
            raise TypeError("key must be a string or TreeRegion")

    def get_subtree(self, region):
        """Get all GeometryTree consisting of all nodes descended from the supplied one."""
        region = self.get_region(region)
        if region.key == "root":
            return self
        subtree = GeometryTree(create_root_node=False)

        def dive(node):
            subtree[node.key] = node
            for child in node.children:
                dive(child)

        dive(region)
        subtree.root_node = region
        return subtree

    def get_regions_of_type(self, region_type):
        """Return all regions in the tree of the supplied region type.

        Parameters
        ----------
        region_type: str or RegionType
            Region type to be fetched
        """
        if isinstance(region_type, RegionType):
            region_type = region_type.value
        nodes = []
        for node in self:
            if node.region_type.value == region_type and node.key != "root":
                nodes.append(node)
        return nodes

    # TODO: Revisit this at a later date
    # def fix_duct_geometry(self, node):
    #     """Fix geometry to work with FEA.
    #
    #     Check if a region crosses over its upper or lower duplication angle, and splits it
    #     apart into two regions within the valid sector. Meant primarily for ducts; splitting
    #     apart magnet or other regions in this way can result in errors when solving.
    #
    #     Parameters
    #     ----------
    #     node: region representing region to be fixed
    #
    #     Returns
    #     -------
    #     Bool: bool representing whether splitting occurred
    #     """
    #     # Splits regions apart, if necessary, to enforce valid geometry
    #     node = self.get_region(node)
    #     name = node.key
    #     duplication_angle = 360 / node.duplications
    #
    #     # brush1 used to find the valid portion just above angle 0
    #     brush1 = Region(region_type=RegionType.airgap)
    #     brush_length = self._motorcad_instance.get_variable("Stator_Lam_Dia")
    #     p1 = Coordinate(0, 0)
    #     p2 = Coordinate(brush_length, 0)
    #     brush1.entities.append(Line(p2, p1))
    #
    #     brush1.entities.append(Arc(p1, p2, centre=Coordinate(brush_length / 2, 1)))
    #     valid_regions_lower = self._motorcad_instance.subtract_region(node, brush1)
    #
    #     # Case where there is no lower intersection
    #     if (len(valid_regions_lower) == 1) and (valid_regions_lower[0].entities == node.entities):
    #         # now perform the upper check
    #         # brush3 used to find the valid portion just below duplication angle
    #         brush3 = Region(region_type=RegionType.airgap)
    #         p1 = Coordinate(0, 0)
    #         p2 = Coordinate.from_polar_coords(brush_length, duplication_angle)
    #         brush3.entities.append(Line(p1, p2))
    #         brush3.entities.append(Arc(p2, p1, radius=brush_length / 2))
    #         valid_regions_upper = self._motorcad_instance.subtract_region(node, brush3)
    #
    #         # Case where no slicing necessary
    #         if (len(valid_regions_upper) == 1) and (
    #             valid_regions_upper[0].entities == node.entities
    #         ):
    #             return False
    #         # Case where upper slicing necessary
    #         else:
    #             for i, new_valid_region in enumerate(valid_regions_upper):
    #                 new_valid_region.name = f"{name}_{i + 1}"
    #                 self._add_region(new_valid_region, parent=node.parent)
    #             # now perform the upper check
    #             # brush4 used to find the invalid portion just above duplication angle
    #             brush4 = Region(region_type=RegionType.airgap)
    #             p1 = Coordinate(0, 0)
    #             p2 = Coordinate.from_polar_coords(brush_length, duplication_angle)
    #             brush4.entities.append(Line(p2, p1))
    #             brush4.entities.append(Arc(p1, p2, radius=brush_length / 2))
    #             invalid_regions_upper = self._motorcad_instance.subtract_region(node, brush4)
    #             for i, new_lower_valid_region in enumerate(invalid_regions_upper):
    #                 new_lower_valid_region.rotate(Coordinate(0, 0), -duplication_angle)
    #                 new_lower_valid_region.name = f"{name}_{i + len(valid_regions_upper) + 1}"
    #                 # Make sure regions are appropriately linked
    #                 for valid_region_upper in valid_regions_upper:
    #                     new_lower_valid_region.linked_regions.append(valid_region_upper)
    #                     valid_region_upper.linked_regions.append(new_lower_valid_region)
    #                 self._add_region(new_lower_valid_region, parent=node.parent)
    #             self.remove_region(node)
    #             return True
    #     # Case where lower slicing necessary
    #     else:
    #         # first, handle the valid regions returned
    #         for i, new_valid_region in enumerate(valid_regions_lower):
    #             new_valid_region.name = f"{name}_{i+1}"
    #             self._add_region(new_valid_region, parent=node.parent)
    #
    #         # brush2 used to find the invalid portion just below angle 0
    #         brush2 = Region(region_type=RegionType.airgap)
    #         p1 = Coordinate(0, 0)
    #         p2 = Coordinate(brush_length, 0)
    #         brush2.entities.append(Line(p1, p2))
    #         brush2.entities.append(Arc(p2, p1, centre=Coordinate(brush_length / 2, -1)))
    #         # Upper in this case referring to the fact that this region will
    #         # form the upper half of the ellipse.
    #         # It will be below the other half in terms of relative positioning
    #         invalid_regions_lower = self._motorcad_instance.subtract_region(node, brush2)
    #         for i, new_upper_valid_region in enumerate(invalid_regions_lower):
    #             new_upper_valid_region.rotate(Coordinate(0, 0), duplication_angle)
    #             new_upper_valid_region.name = f"{name}_{i + len(valid_regions_lower) + 1}"
    #             # Make sure regions are appropriately linked
    #             for valid_region_lower in valid_regions_lower:
    #                 new_upper_valid_region.linked_regions.append(valid_region_lower)
    #                 valid_region_lower.linked_regions.append(new_upper_valid_region)
    #             self._add_region(new_upper_valid_region, parent=node.parent)
    #         self.remove_region(node)
    #         return True

    def _add_region(self, region, parent=None):
        """Add region to tree.

        Note that any children specified will be 'reassigned' to the added region, with no
        connection to their previous parent.

        Parameters
        ----------
        region: ansys.motorcad.core.geometry.TreeRegion|ansys.motorcad.core.geometry.TreeRegionMagnet # noqa: E501
            Region to convert and add to tree
        parent: TreeRegion or str
            Parent object or parent key (must be already within tree)
        """
        # Add some proper conversion here at some point. Using __class__ is unsatisfactory
        if not isinstance(region, TreeRegion):
            raise TypeError(
                "region must be of type ansys.motorcad.core.geometry.TreeRegion or "
                "ansys.motorcad.core.geometry.TreeRegionMagnet"
            )

        # Make certain any nodes being replaced are properly removed
        try:
            self.remove_region(self[region.key])
        except KeyError:
            pass

        if not "root" in self.keys():
            # Tree has no root - must be being created
            region._name = "root"
            self["root"] = region

        elif parent is None:
            region.parent = self["root"]
        else:
            if isinstance(parent, TreeRegion):
                region.parent = parent
            elif isinstance(parent, str):
                region.parent = self.get_region(parent)
            else:
                raise TypeError("Parent must be a TreeRegion or str")

        region._motorcad_instance = self._motorcad_instance
        self[region.key] = region

    def remove_region(self, node):
        """Remove Node from tree, attach children of removed region to parent."""
        if type(node) is str:
            node = self.get_region(node)
        for child in node.children:
            child.parent = node.parent

        self.pop(node.key)

    def create_region(self, region_type, parent=None):
        """Create a region in the tree.

        Parameters
        ----------
        region_type : ansys.motorcad.core.geometry.RegionType
            Type of region to create
        parent : TreeRegion|TreeRegionMagnet
            parent object (must be already within tree)
        Returns
        -------
        TreeRegion|TreeRegionMagnet
        """
        if region_type == RegionType.magnet:
            region = TreeRegionMagnet(self, motorcad_instance=self._motorcad_instance)
        else:
            region = TreeRegion(self, region_type, motorcad_instance=self._motorcad_instance)

        self._add_region(region, parent=parent)
        return region

    def remove_branch(self, node):
        """Remove Node and all descendants from tree."""
        if type(node) == str:
            node = self.get_region(node)

        # Recursive inner function to find and remove all descendants
        def dive(node):
            for child in node.children:
                dive(child)
            self.pop(node.key)

        dive(node)

    def unite_linked_regions(self, region):
        """Unite region with any linked regions when connected across the symmetry boundaries.

        Rotate linked regions and try to unite with region. Where the regions can be united, remove
        the linked regions from the geometry tree.

        If successful, region will be mutated into a full region that crosses the symmetry boundary.

        Parameters
        ----------
        region : TreeRegion|TreeRegionMagnet
            object (must be already within tree) to be united with its linked regions.
        Returns
        -------
        Bool
            If any regions were successfully united, return True
        """
        regions_united_bool = False

        # Iterate over a copy of the linked region names, since the list may be modified
        # during iteration when a successful unite removes a linked region.
        for name in deepcopy(region.linked_region_names):
            linked_region = self[name]

            # Only attempt to unite regions of the same type.
            if linked_region.region_type == region.region_type:
                # The linked region exists at a rotated position relative to region
                # (it lives one symmetry sector away). Rotate it back by one duplication
                # angle so it is positioned adjacent to region before uniting.
                region_j_rotated = deepcopy(linked_region.entities)
                region_j_rotated.rotate(Coordinate(0, 0), -360 / linked_region.duplications)
                region_j_rotated = region_j_rotated.get_region(
                    region_type=linked_region.region_type
                )

                try:
                    # Attempt to unite the regions. This will raise a MotorCADError if the two
                    # regions do not share a boundary (i.e. they don't physically touch).
                    regions_united = self._motorcad_instance.unite_regions(
                        region, [region_j_rotated]
                    )

                    # Unite succeeded: update region's geometry with the combined result,
                    # remove the linked reference from region, and delete the linked region
                    # from the tree, because its geometry is now included in region.
                    region.entities = regions_united.entities
                    region.linked_region_names.remove(name)
                    self.remove_region(self[name])
                    regions_united_bool = True

                except MotorCADError as e:
                    # Silently skip pairs that don't touch; any other MotorCADError is
                    # unexpected and will propagate up.
                    if "Unable to unite regions, regions do not touch" in str(e):
                        pass
            else:
                # raise a warning for cases when the region and linked region are not the same
                # RegionType.
                warnings.warn(
                    f"{region.name} and {linked_region.name} are regions of "
                    f"different RegionType. Cannot unite regions."
                )

        return regions_united_bool

    def separate_region_on_boundary(self, region, sector_rad=1000):
        """Separate/split a region into multiple regions connected across the symmetry boundaries.

        If a region collides with the symmetry boundary, split on the boundary and rotate any
        regions that are outside the symmetry sector around the origin by the duplication angle,
        so that these are within the symmetry sector. Link the separated regions together as linked
        regions so they can be recognised by Motor-CAD FEA solver as parts of the same region.

        If successful, region is mutated into the part of the region that is within the symmetry
        sector, and a list is returned of the new regions created for the parts of the region that
        were outside the symmetry sector.

        Parameters
        ----------
        region : TreeRegion|TreeRegionMagnet
            object (must be already within tree) to be separated based on the symmetry boundary.
        sector_rad : float
            Maximum radius of the symmetry sector used for separation. Default is 1000 mm.
        Returns
        -------
        list of TreeRegion|TreeRegionMagnet
            If the region was successfully separated, return a list of the new regions.
        """
        regions_separated = []

        # Build a wedge-shaped boundary region representing one duplication sector. The duplication
        # angle of the sector is determined by the region's parent region symmetry.
        boundary_line_0 = Line(Coordinate(0, 0), Coordinate(sector_rad, 0))
        boundary_point_x, boundary_point_y = rt_to_xy(sector_rad, 360 / region.parent.duplications)
        boundary_line_1 = Line(Coordinate(boundary_point_x, boundary_point_y), Coordinate(0, 0))
        boundary_arc_0 = Arc(boundary_line_0.end, boundary_line_1.start, centre=Coordinate(0, 0))
        boundaries = EntityList()
        boundaries.extend([boundary_line_0, boundary_arc_0, boundary_line_1])
        symmetry_sector = boundaries.get_region(RegionType.stator_air)

        # Only split when the region crosses the sector boundary.
        if region.collides(symmetry_sector):
            # Subtracting the sector wedge isolates parts of the region that are outside the
            # symmetry sector.
            out_of_bounds_regions = self._motorcad_instance.subtract_region(region, symmetry_sector)
            i = 1
            for new_region in out_of_bounds_regions:
                # Subtract the out-of-bounds regions from the original region, so that region is
                # mutated into only the part of the region that is within the symmetry sector.
                region.subtract(new_region)

                # Add each new region to the geometry tree, rotate it into the symmetry sector,
                # and set it as a linked region of the original region.
                tree_region = self.duplicate_region(region, f"{region.name}_{i}")
                tree_region.rotate(Coordinate(0, 0), 360 / region.duplications)
                region.linked_region_names.append(tree_region.name)
                regions_separated.append(tree_region)

                i += 1

        # Return the new separated regions. returns an empty list when no separation occurred.
        return regions_separated

    def duplicate_region(self, region, duplicate_name=None):
        """Create a copy of a region as a new tree region with all properties transferred.

        This method creates a new TreeRegion in the tree as a child of the same parent as the
        source region, then copies over all relevant properties (colour, duplications, material,
        and geometry entities) from the source region. The new region is given a unique name
        within the tree.

        Parameters
        ----------
        region : TreeRegion|TreeRegionMagnet|Region|RegionMagnet
            Source region whose properties will be copied. Can be a tree region (already in the
            tree) or a plain Region object.
        duplicate_name : str, optional
            Name to assign to the new duplicated region. If not provided, a default name is
            generated based on the original region name.

        Returns
        -------
        TreeRegion|TreeRegionMagnet
            The newly created tree region with all properties copied from the source region.
        """
        # Use a default name if none is provided.
        if duplicate_name is None:
            duplicate_name = f"{region.name}_duplicated"

        # Create a new tree region in the tree with the same type and parent as the source region.
        duplicate_region = self.create_region(region.region_type, region.parent)

        # Copy all visual and physical properties from the source region.
        duplicate_region.colour = region.colour
        duplicate_region.duplications = region.duplications
        duplicate_region.material = region.material

        # Copy the geometry entities from the source region.
        duplicate_region.entities = region.entities

        # Assign the requested name if it is not already present in the tree
        # (case-insensitive to avoid collisions like "Name" vs "name").
        if duplicate_name.lower() not in self.lowercase_keys:
            duplicate_region.name = duplicate_name
        else:
            # If the base name is taken, try suffixed variants until a unique
            # key is found or we hit a 100 attempts.
            max_iterations = 100
            for i in range(max_iterations):
                attempt_name = f"{duplicate_name}_{i}"
                if attempt_name.lower() not in self.lowercase_keys:
                    duplicate_region.name = attempt_name
                    # Stop at the first valid unique name.
                    break
            # raise an Exception if the duplicate name cannot be made unique within 100 attempts, to
            # avoid an infinite loop in edge cases where there are many similarly named regions in
            # the tree.
            if i == max_iterations - 1:
                raise Exception(
                    f"Could not find a unique name for the duplicated region in the "
                    f"geometry tree."
                )

        return duplicate_region

    @property
    def lowercase_keys(self):
        """Return a dict of lowercase keys and their corresponding real keys."""
        return dict((node.key.lower(), node.key) for node in self)


class TreeRegion(Region):
    """Subclass of Region used for entries in GeometryTree.

    Nodes should not have a parent or children unless they are part of a tree.
    """

    def __init__(self, tree, region_type, motorcad_instance=None):
        """Initialize the geometry region.

        Parent and children are defined when the region is added to a tree.

        Parameters
        ----------
        tree : GeometryTree
            Tree which region belongs to
        region_type: RegionType
            Type of region to create
        motorcad_instance: ansys.motorcad.core.geometry.MotorCAD
            MotorCAD instance
        """
        super().__init__(region_type=region_type, motorcad_instance=motorcad_instance)

        self._init_treeregion_properties(tree)
        self._name = "region_" + str(self.tree.unique_region_number)

    def _init_treeregion_properties(self, tree):
        """Initialise params for TreeRegion.

        Parameters
        ----------
        tree : GeometryTree
            Tree which region belongs to
        """
        self._parent = None
        self.tree = tree
        self._linked_region_names = []

    def __repr__(self):
        """Return string representation of TreeRegion."""
        return self.key

    def _get_new_object_of_type_self(self):
        """Return self object."""
        return type(self)(self.tree, self.region_type, motorcad_instance=self._motorcad_instance)

    @property
    def name(self):
        """Name of Region."""
        return self._name

    @name.setter
    def name(self, value):
        self.tree[value] = self.tree.pop(self.key)
        self._name = value

    @property
    def key(self):
        """Get key of Region in dict."""
        return self._name

    @classmethod
    def from_json(cls, geometry_tree, region_json, mc):
        """Create a RegionTree from JSON data, must link parent once whole tree is available.

        Parameters
        ----------
        geometry_tree : GeometryTree
            Geometry tree that region belongs to.
        region_json: dict
            JSON representation of region.
        mc: ansys.motorcad.core.geometry.MotorCAD
            Motor-CAD instance.

        Returns
        -------
        TreeRegion
        """
        is_magnet = region_json["region_type"] == RegionType.magnet.value

        if is_magnet:
            new_region = TreeRegionMagnet(geometry_tree, motorcad_instance=mc)
        else:
            new_region = cls(
                geometry_tree, RegionType(region_json["region_type"]), motorcad_instance=mc
            )

        new_region._add_parameters_from_json(region_json)

        # Protected linked_region_names attribute used only when first initializing the tree
        new_region._linked_region_names = region_json["linked_regions"]

        return new_region

    @property
    def level(self):
        """Level of region in tree."""
        level = 0
        node = self

        while True:
            if node.key == "root":
                break
            level += 1
            node = node.parent

        return level

    @property
    def parent(self):
        """Get or set parent region.

        Returns
        -------
        ansys.motorcad.core.geometry_tree.TreeRegion
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def children(self):
        """Get or set parent region.

        Returns
        -------
        list of ansys.motorcad.core.geometry_tree.TreeRegion
            list of Motor-CAD region object
        """
        children = []

        for region in self.tree:
            if region.parent == self:
                children += [region]

        return children

    @children.setter
    def children(self, value):
        raise NotImplementedError

    @property
    def child_keys(self):
        """Get list of keys corresponding to child nodes.

        Returns
        -------
        list of str
        """
        return list(child.key for child in self.children)

    @property
    def parent_key(self):
        """Get key corresponding to parent region.

        Returns
        -------
        str
        """
        if self.parent is None:
            return ""
        else:
            return self.parent.key

    @property
    def child_names(self):
        """Get list of names corresponding to child nodes.

        Returns
        -------
        list of str
        """
        return list(child.name for child in self.children)

    @property
    def parent_name(self):
        """Get name corresponding to parent region.

        Returns
        -------
        str
        """
        if self.parent is None:
            return ""
        else:
            return self.parent.name

    @Region.linked_regions.getter
    def linked_regions(self):
        """Get linked region objects for duplication/unite operations."""
        return [self.tree[name] for name in self._linked_region_names]


class TreeRegionMagnet(TreeRegion, RegionMagnet):
    """Class for magnets in tree.

    Inherit behaviour from both TreeRegions and RegionMagnet.
    """

    def __init__(self, tree, motorcad_instance=None):
        """Initialize the geometry region.

        Parent and children are defined when the region is added to a tree.

        Parameters
        ----------
        region_type: RegionType
        """
        RegionMagnet.__init__(self, motorcad_instance=motorcad_instance)
        self._init_treeregion_properties(tree)

        self._name = "magnet_region_" + str(self.tree.unique_region_number)

    def _get_new_object_of_type_self(self):
        """Return self object."""
        return type(self)(self.tree, motorcad_instance=self._motorcad_instance)
