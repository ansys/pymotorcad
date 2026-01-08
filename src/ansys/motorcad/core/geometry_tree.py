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
from ansys.motorcad.core.geometry import Region, RegionMagnet, RegionType


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

    def get_magnet_segment_regions(self):
        """Return all magnet regions in the tree with magnet segment regions grouped into lists.

        If a magnet has more than one segment, the magnet segment regions will be
        returned as a list of lists of magnet segment regions.

        For example, if there are 2 full magnets, each with 2 segments, return a list with two
        indices, where each index is a list of two regions (the individual magnet segment regions).

        Returns
        -------
        magnet_segments: list of lists of TreeRegionObject
            List of lists that represent full magnets. Full magnet lists contain magnet segment
            regions.
        """
        # get all magnet regions (these can be full magnets or magnet segments)
        magnets = self.get_regions_of_type(RegionType.magnet)

        all_magnet_segments_ungrouped = []
        all_magnet_segments_grouped = []

        # loop through all magnet regions
        for magnet in magnets:
            # check whether the magnet has already been found and identified as a magnet segment.
            if magnet not in all_magnet_segments_ungrouped:
                # create a copy of the magnet to be united with other magnet segments.
                magnet_copy = Region(region_type=RegionType.magnet)
                magnet_copy.replace(magnet)
                magnet_copy.motorcad_instance = self._motorcad_instance
                # create list of magnet segments with the magnet as first element.
                magnet_segments = [magnet]
                # loop through other magnets from 1 -> n
                for other_magnet in magnets:
                    # check that other magnet is not the same as magnet.
                    if other_magnet != magnet:
                        # create a copy of the other magnet to be united with magnet
                        other_magnet_copy = Region(region_type=RegionType.magnet)
                        other_magnet_copy.replace(other_magnet)
                        other_magnet_copy.motorcad_instance = self._motorcad_instance
                        # Identify corresponding magnet segments from the same full magnet by
                        # attempting to unite. If magnets can be united, then they are segments of
                        # the same full magnet.
                        try:
                            magnet_copy.unite(other_magnet_copy)
                            # if uniting the regions is successful, append other magnet to the list.
                            magnet_segments.append(other_magnet)
                        except:
                            # if the magnets cannot be united, then do nothing.
                            pass
                # loop through magnets from n -> 1
                # Try looping through magnets in the other direction to account for the list being
                # in a different order.
                for other_magnet in reversed(magnets):
                    # check that other magnet is not the same as magnet.
                    # check whether the magnet has already been found and identified as a magnet
                    # segment.
                    if other_magnet != magnet and other_magnet not in magnet_segments:
                        # create a copy of the other magnet to be united with magnet
                        other_magnet_copy = Region(region_type=RegionType.magnet)
                        other_magnet_copy.replace(other_magnet)
                        other_magnet_copy.motorcad_instance = self._motorcad_instance
                        # Identify corresponding magnet segments from the same full magnet by
                        # attempting to unite. If magnets can be united, then they are segments of
                        # the same full magnet.
                        try:
                            magnet_copy.unite(other_magnet_copy)
                            # if uniting the regions is successful, append other magnet to the list.
                            magnet_segments.append(other_magnet)
                        except:
                            # if the magnets cannot be united, then do nothing.
                            pass
                # add the list of corresponding magnet segments to a list
                all_magnet_segments_grouped.append(magnet_segments)
                # add all magnet segments that have been identified so far to a list
                all_magnet_segments_ungrouped.extend(magnet_segments)

        # return the all_magnet_segments_grouped list. Corresponding magnet segments that make up a
        # full magnet are stored in lists. all_magnet_segments_grouped is a list of these lists.
        return all_magnet_segments_grouped

    def get_full_magnet_regions(self):
        """Return magnets in the tree as a list of full magnet regions.

        If a magnet has more than one segment, unite the magnet segment regions to form a full
        magnet region. Returns a list of magnet regions.

        For example, if there are 2 full magnets, each with 2 segments, return a list of two full
        magnet regions, where each full magnet region is the result of uniting the magnet's two
        individual magnet segment regions.

        Returns
        -------
        full_magnets: list of TreeRegionObject
            List of full magnet regions.
        """
        # get the magnet segments from the geometry tree. These are grouped so that magnet_segments
        # is a list of full magnets and each full magnet is a list of magnet segments.
        magnet_segments = self.get_magnet_segment_regions()

        # create a list to add the full magnets to.
        full_magnets = []

        # loop through the magnet_segments list where each element is a list of one or more magnets.
        for magnet_list in magnet_segments:
            # if this magnet_list contains more than 1 magnet region, it is a segmented magnet.
            if len(magnet_list) > 1:
                # take the first magnet segment region in the list
                full_magnet = magnet_list[0]
                # loop through the remaining magnet segment regions in the list
                for i in range(len(magnet_list) - 1):
                    segment = magnet_list[i + 1]
                    # unite the magnet segments to form the full magnet
                    full_magnet.unite(segment)
                # when all segments have been united, append the full_magnet to the list
                full_magnets.append(full_magnet)
            # if this magnet_list contains only 1 magnet region, it is not segmented.
            else:
                # append the full (not segmented) magnet to the list
                full_magnets.append(magnet_list[0])
        # return the list of full magnet regions, where any segmented magnets have been united.
        return full_magnets

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
