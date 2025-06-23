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
from ansys.motorcad.core.geometry import Region


class GeometryTree(dict):
    """."""

    def __init__(self, tree: dict):
        """Initialize tree.

        Parameters
        ----------
        tree
        """
        self.root = GeometryNode()
        self.tree_json = tree["regions"]

    def build_tree(self, region: dict, parent):
        """Recursively builds tree.

        Parameters
        ----------
        region
        parent
        """
        # base case
        if region["parent_name"]:
            pass


class GeometryNode(Region):
    """."""

    @classmethod
    def _from_json(cls, json, parent):
        new_region = super()._from_json(json, cls_to_create=cls)
        new_region.parent = parent
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
