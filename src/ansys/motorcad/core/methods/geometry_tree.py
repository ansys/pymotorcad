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
from ansys.motorcad.core.geometry import Region, RegionType


class GeometryTree(dict):
    """."""

    def __init__(self, tree: dict):
        """Initialize tree.

        Parameters
        ----------
        tree
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

        self.build_tree(tree_json, root)

    def build_tree(self, tree_json, node, parent=None):
        """Recursively builds tree.

        Parameters
        ----------
        tree_json: dict
        node: dict
        parent: None or GeometryNode
        """
        # base case
        self[node["name_unique"]] = GeometryNode._from_json(self, node, parent)

        # recursive case
        if node["child_names"] != []:
            for child_name in node["child_names"]:
                self.build_tree(tree_json, tree_json[child_name], self[node["name_unique"]])

    def add_region(self, region, name=None, parent=None, children=[]):
        """."""
        region.__class__ = GeometryNode
        region.children = children
        if parent is None:
            region.parent = self["root"]
        else:
            region.parent = parent
        if name is None:
            self[region.name] = region
        else:
            self[name] = region

    def remove_region(self, region_name):
        """."""
        for child in self[region_name].children:
            child.parent = self[region_name].parent
            child.parent_name = self[region_name].parent.name
            self[region_name].parent.children.append(child)
        self.pop(region_name)


class GeometryNode(Region):
    """."""

    @classmethod
    def _from_json(cls, tree, node_json, parent):
        """Create node from dict."""
        if node_json["name_unique"] == "root":
            new_region = GeometryNode(region_type=RegionType.airgap)
            new_region.name = "root"
            new_region.key = "root"
            new_region.children = list()

        else:
            new_region = super()._from_json(node_json)
            new_region.__class__ = GeometryNode
            new_region.parent = parent
            new_region.children = list()
            parent.children.append(new_region)
            new_region.key = node_json["name_unique"]
        return new_region

    @property
    def parent(self):
        """Get or set parent region.

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
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
