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

"""Methods for building geometry trees."""

from ansys.motorcad.core.geometry import Arc, Coordinate, Line, Region, RegionMagnet, RegionType


class GeometryTree(dict):
    """Class used to build geometry trees."""

    def __init__(self, empty=False):
        """Initialise the geometry tree.

        Parameters
        ----------
        empty: bool
            Return an empty geometry tree, mostly used for the purposes of debugging and
            internal construction.
        """
        if empty:
            super().__init__()
        else:
            root = GeometryNode(region_type=RegionType.airgap)
            root.parent = None
            root.children = list()
            root.name = "root"
            root.key = "root"
            pair = [("root", root)]
            super().__init__(pair)

    def __iter__(self):
        """Define ordering according to tree structure."""
        well_ordered = []

        def dive(node=self.start):
            well_ordered.append(node)
            for child in node.children:
                dive(child)

        dive()
        return iter(well_ordered)

    def __str__(self):
        """Return string representation of the geometry tree."""
        string = ""
        starting_depth = list(self.values())[0].depth

        for node in self:
            relative_depth = node.depth - starting_depth
            string += "│   " * (relative_depth - 1)
            if relative_depth == 0:
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
        Also requires that each node with the same key is equal.
        """

        def dive(key):
            if len(self[key].children) != len(other[key].children):
                return False
            for child in self[key].children:
                # Making sure each child is in the other corresponding node's children
                if not child.key in other[key].child_keys:
                    return False
                if not dive(child.key):
                    return False
            # Actual equality check of nodes
            if self[key] != other[key]:
                return False
            return True

        return dive("root")

    def __ne__(self, other):
        """Define inequality."""
        return not self.__eq__(other)

    @classmethod
    def _from_json(cls, tree, mc):
        """Return a GeometryTree representation of the geometry defined within a JSON.

        Parameters
        ----------
        tree: dict
            JSON to create a tree from (generally, the output of get_geometry_tree()).
        Returns
        -------
        GeometryTree
        """
        self = cls(empty=True)
        """Initialize tree.

        Parameters
        ----------
        tree: dict
        """
        root = dict()
        root["name_unique"] = "root"
        root["parent_name"] = ""
        root["child_names"] = list()
        tree_json = tree["regions"]

        # properly connect the json file before tree is constructed
        for region in tree_json.values():
            if region["parent_name"] == "":
                region["parent_name"] = "root"
                root["child_names"].append(region["name_unique"])

        self._build_tree(tree_json, root)
        self.mc = mc
        return self

    def _to_json(self):
        """Return a dict object used to set geometry."""
        regions = dict()
        for node in self:
            if node.key != "root":
                if node.region_type == "Magnet":
                    regions[node.key] = RegionMagnet._to_json(node)
                else:
                    regions[node.key] = Region._to_json(node)
        return {"regions": regions}

    def get_node(self, key):
        """Get a region from the tree (case-insensitive)."""
        if isinstance(key, str):
            if key.lower() in self.lowercase_keys:
                lower_key = key.lower()
                return self[self.lowercase_keys[lower_key]]
            raise KeyError()
        elif isinstance(key, GeometryNode):
            return key
        else:
            raise TypeError("key must be a string or GeometryNode")

    def get_subtree(self, node):
        """Get all GeometryTree consisting of all nodes descended from the supplied one."""
        if node == self["root"]:
            return self
        subtree = GeometryTree(empty=True)

        def dive(node):
            subtree[node.key] = node
            for child in node.children:
                dive(child)

        dive(self.get_node(node))
        return subtree

    def _build_tree(self, tree_json, node, parent=None):
        """Recursively builds tree.

        Parameters
        ----------
        tree_json: dict
            Dictionary containing region dicts
        node: dict
            Information of current region
        parent: None or GeometryNode
        """
        # Convert current node to GeometryNode and add it to tree
        self[node["name_unique"]] = GeometryNode.from_json(self, node, parent)

        # Recur for each child.
        if node["child_names"] != []:
            for child_name in node["child_names"]:
                self._build_tree(tree_json, tree_json[child_name], self[node["name_unique"]])

    def fix_duct_geometry(self, node):
        """Fix geometry to work with FEA.

        Meant primarily for ducts; splitting apart magnet or other regions in this way can result
        in errors when solving.

        Parameters
        ----------
        node: node representing region to be fixed

        Returns
        -------
        None
        """
        # Splits regions apart, if necessary, to enforce valid geometry
        node = self.get_node(node)
        name_length = len(node.key)
        duplication_angle = 360 / node.duplications

        # brush1 used to find the valid portion just above angle 0
        brush1 = Region(region_type=RegionType.airgap)
        brush_length = self.mc.get_variable("Stator_Lam_Dia")
        p1 = Coordinate(0, 0)
        p2 = Coordinate(brush_length, 0)
        brush1.entities.append(Line(p2, p1))

        brush1.entities.append(Arc(p1, p2, centre=Coordinate(brush_length / 2, 1)))
        valid_regions_lower = self.mc.subtract_region(node, brush1)

        # Case where there is no lower intersection
        if (len(valid_regions_lower) == 1) and (valid_regions_lower[0].entities == node.entities):
            # now perform the upper check
            # brush3 used to find the valid portion just below duplication angle
            brush3 = Region(region_type=RegionType.airgap)
            p1 = Coordinate(0, 0)
            p2 = Coordinate.from_polar_coords(brush_length, duplication_angle)
            brush3.entities.append(Line(p1, p2))
            brush3.entities.append(Arc(p2, p1, radius=brush_length / 2))
            valid_regions_upper = self.mc.subtract_region(node, brush3)

            # Case where no slicing necessary
            if (len(valid_regions_upper) == 1) and (
                valid_regions_upper[0].entities == node.entities
            ):
                return False
            # Case where upper slicing necessary
            else:
                for new_valid_region in valid_regions_upper:
                    self.add_node(new_valid_region, parent=node.parent)
                # now perform the upper check
                # brush4 used to find the invalid portion just above duplication angle
                brush4 = Region(region_type=RegionType.airgap)
                p1 = Coordinate(0, 0)
                p2 = Coordinate.from_polar_coords(brush_length, duplication_angle)
                brush4.entities.append(Line(p2, p1))
                brush4.entities.append(Arc(p1, p2, radius=brush_length / 2))
                invalid_regions_upper = self.mc.subtract_region(node, brush4)
                for i, new_lower_valid_region in enumerate(invalid_regions_upper):
                    new_lower_valid_region.rotate(Coordinate(0, 0), -duplication_angle)
                    new_lower_valid_region.name = new_lower_valid_region.name[0 : name_length + 1]
                    new_lower_valid_region.name += str(i + len(valid_regions_upper) + 1)
                    # Linked regions currently only guaranteed to work if only one new region is
                    # formed at top and bottom; will change once regions can be multiply linked.
                    new_lower_valid_region.linked_region = valid_regions_upper[i]
                    valid_regions_upper[i].linked_region = new_lower_valid_region
                    self.add_node(new_lower_valid_region, parent=node.parent)
                self.remove_node(node)
                return True
        # Case where lower slicing necessary
        else:
            # first, handle the valid regions returned
            for new_valid_region in valid_regions_lower:
                self.add_node(new_valid_region, parent=node.parent)

            # brush2 used to find the invalid portion just below angle 0
            brush2 = Region(region_type=RegionType.airgap)
            p1 = Coordinate(0, 0)
            p2 = Coordinate(brush_length, 0)
            brush2.entities.append(Line(p1, p2))
            brush2.entities.append(Arc(p2, p1, centre=Coordinate(brush_length / 2, -1)))
            # Upper in this case referring to the fact that this region will
            # form the upper half of the ellipse.
            # It will be below the other half in terms of relative positioning
            invalid_regions_lower = self.mc.subtract_region(node, brush2)
            for i, new_upper_valid_region in enumerate(invalid_regions_lower):
                new_upper_valid_region.rotate(Coordinate(0, 0), duplication_angle)
                new_upper_valid_region.name = new_upper_valid_region.name[0 : name_length + 1]
                new_upper_valid_region.name += str(i + len(valid_regions_lower) + 1)
                # Linked regions currently only guaranteed to work if only one new region is
                # formed at top and bottom; will change once regions can be multiply linked.
                new_upper_valid_region.linked_region = valid_regions_lower[i]
                valid_regions_lower[i].linked_region = new_upper_valid_region
                self.add_node(new_upper_valid_region, parent=node.parent)
            self.remove_node(node)
            return True

    def add_node(self, region, key=None, parent=None, children=None):
        """Add node to tree.

        Note that any children specified will be 'reassigned' to the added node, with no
        connection to their previous parent.

        Parameters
        ----------
        region: ansys.motorcad.core.geometry.Region
            Region to convert and add to tree
        key: str
            Key to be used for dict
        parent: GeometryNode or str
            Parent object or parent key (must be already within tree)
        children: list of GeometryNode or str
            Children objects or children keys (must be already within tree)

        """
        if not isinstance(region, GeometryNode):
            region.__class__ = GeometryNode
        if children is None:
            region.children = list()
        else:
            if all(isinstance(child, Region) for child in children):
                region.children = children
            elif all(isinstance(child, str) for child in children):
                direct_children = list(self.get_node(child) for child in children)
                region.children = direct_children
            else:
                raise TypeError("Children must be a GeometryNode or str")
            # Essentially, slotting the given node in between the given parent and children
            # Children are removed from their old spot and placed in the new one
            # Children's children become assigned to child's old parent
            for child in region.children:
                self.remove_node(child)
                child.parent = region
                child.children = list()
                self[child.key] = child

        if parent is None:
            region.parent = self["root"]
            self["root"].children.append(region)
        else:
            if isinstance(parent, GeometryNode):
                region.parent = parent
                parent.children.append(region)
            elif isinstance(parent, str):
                region.parent = self.get_node(parent)
                self[parent].children.append(region)
            else:
                raise TypeError("Parent must be a GeometryNode or str")

        if key is None:
            self[region.name] = region
            region.key = region.name
        else:
            self[key] = region
            region.key = key

    def remove_node(self, node):
        """Remove Node from tree, attach children of removed node to parent."""
        if type(node) is str:
            node = self.get_node(node)
        for child in node.children:
            child.parent = node.parent
            node.parent.children.append(child)
        node.parent.children.remove(node)
        self.pop(node.key)

    def remove_branch(self, node):
        """Remove Node and all descendants from tree."""
        if type(node) == str:
            node = self.get_node(node)

        # Recursive inner function to find and remove all descendants
        def dive(node):
            for child in node.children:
                dive(child)
            self.pop(node.key)

        dive(node)
        node.parent.children.remove(node)

    @property
    def lowercase_keys(self):
        """Return a dict of lowercase keys and their corresponding real keys."""
        return dict((node.key.lower(), node.key) for node in self)

    @property
    def start(self):
        """Return the start of the tree."""
        # Find starting point
        for node in self.values():
            if node.parent is None:
                start = node
                break
            else:
                try:
                    self[node.parent.key]
                except KeyError:
                    start = node
        return start


class GeometryNode(Region):
    """Subclass of Region used for entries in GeometryTree.

    Nodes should not have a parent or children unless they are part of a tree.
    """

    def __init__(self, region_type=RegionType.adaptive):
        """Initialize the geometry node.

        Parent and children are defined when the node is added to a tree.

        Parameters
        ----------
        region_type: RegionType
        """
        super().__init__(region_type=region_type)
        self.children = list()
        self.parent = None
        self.key = None

    def __repr__(self):
        """Return string representation of GeometryNode."""
        try:
            return self.key
        except AttributeError:
            return self.name

    @classmethod
    def from_json(cls, tree, node_json, parent):
        """Create a GeometryNode from JSON data.

        Parameters
        ----------
        tree: dict
        node_json: dict
        parent: GeometryNode

        Returns
        -------
        GeometryNode
        """
        if node_json["name_unique"] == "root":
            new_region = GeometryNode(region_type=RegionType.airgap)
            new_region.name = "root"
            new_region.key = "root"

        else:
            new_region = Region._from_json(node_json)
            new_region.__class__ = GeometryNode
            new_region.parent = parent
            new_region.children = list()
            parent.children.append(new_region)
            new_region.key = node_json["name_unique"]
        return new_region

    @property
    def depth(self):
        """Depth of node."""
        depth = 0
        node = self

        while True:
            if node.key == "root":
                break
            depth += 1
            node = node.parent

        return depth

    @property
    def parent(self):
        """Get or set parent region.

        Returns
        -------
        ansys.motorcad.core.geometry.Region
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
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

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
        """Get key corresponding to parent node.

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
        """Get name corresponding to parent node.

        Returns
        -------
        str
        """
        if self.parent is None:
            return ""
        else:
            return self.parent.name
