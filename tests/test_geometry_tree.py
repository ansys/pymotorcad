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


from copy import deepcopy

import pytest

from ansys.motorcad.core.geometry import Coordinate, Line, Region, RegionType
from ansys.motorcad.core.methods.geometry_tree import GeometryNode, GeometryTree


@pytest.fixture(scope="session")
def sample_tree(mc):
    mc.display_screen("Geometry;Radial")
    return mc.get_geometry_tree()


@pytest.fixture(scope="function")
def basic_tree():
    """Return a simple GeometryTree for the purposes of testing"""
    p1 = Coordinate(0, 0)
    p2 = Coordinate(1, 0)
    p3 = Coordinate(0, 1)
    line1 = Line(p1, p2)
    line2 = Line(p2, p3)
    line3 = Line(p3, p1)
    triangle = Region(region_type=RegionType.airgap)
    triangle.__class__ = GeometryNode
    triangle.entities.append(line1)
    triangle.entities.append(line2)
    triangle.entities.append(line3)
    triangle.name = "Triangle"
    triangle.key = "Triangle"
    triangle.children = []

    tree = GeometryTree()

    triangle.parent = tree["root"]
    tree["root"].children.append(triangle)
    tree["Triangle"] = triangle

    return tree


def test_get_tree(sample_tree):
    node_keys = set(sample_tree)
    # Check each item is listed only once among all children
    # Check also that each item is the child of something, except root
    valid = True
    for node in sample_tree.values():
        for child in node.children:
            try:
                node_keys.remove(child.key)
            except KeyError:
                valid = False
            assert node == child.parent
    assert node_keys == {"root"}
    assert valid


# def test_to_json(sample_tree):
#    test_json = sample_tree.to_json()
#    assert test_json == sample_json2


def test_get_node(sample_tree):
    assert sample_tree.get_node("rotor") == sample_tree["Rotor"]


def test_add_node(basic_tree):
    # Tests the basic functionality of adding a node
    test_tree = deepcopy(basic_tree)
    new_node = GeometryNode(parent=test_tree["root"])
    new_node.name = "node"
    new_node.key = "node"
    test_tree["node"] = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = GeometryNode(parent=function_tree["root"])
    new_node2.name = "node"
    function_tree.add_node(new_node2)

    assert test_tree == function_tree


def test_add_node_with_children(basic_tree):
    # Tests the parent and child reassignment performed when including those values
    test_tree = deepcopy(basic_tree)
    new_node = GeometryNode()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "node"
    new_node.key = "node"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["node"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = Region()
    new_node2.name = "node"
    function_tree.add_node(new_node2, parent="root", children=["Triangle"])

    assert test_tree == function_tree


def test_add_node_with_children_2(basic_tree):
    # Same test as above, but testing different mode of function input
    test_tree = deepcopy(basic_tree)
    new_node = GeometryNode()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "node"
    new_node.key = "node1"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["node1"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = Region()
    new_node2.name = "node"
    function_tree.add_node(
        new_node2, parent=function_tree["root"], children=[function_tree["Triangle"]], key="node1"
    )

    assert test_tree == function_tree


def test_add_node_errors(basic_tree):
    new_node2 = Region()
    new_node2.name = "node"

    with pytest.raises(TypeError, match="Parent must be a GeometryNode or str"):
        basic_tree.add_node(new_node2, parent=0)

    with pytest.raises(TypeError, match="Children must be a GeometryNode or str"):
        basic_tree.add_node(new_node2, children=[0, "root"])


def test_remove_node(basic_tree):
    # Tests the basic functionality of removing a node
    test_tree = deepcopy(basic_tree)

    function_tree = deepcopy(basic_tree)
    new_node2 = GeometryNode(parent=function_tree["root"])
    new_node2.name = "node"
    function_tree.add_node(new_node2, children=["Triangle"])
    function_tree.remove_node(new_node2)
    assert test_tree == function_tree


def test_remove_branch(basic_tree):
    # Tests the basic functionality of removing a branch
    test_tree = deepcopy(basic_tree)
    test_tree.remove_node("Triangle")

    function_tree = deepcopy(basic_tree)
    new_node = GeometryNode(parent=function_tree["root"])
    new_node.name = "node"
    function_tree.add_node(new_node, children=["Triangle"])
    function_tree.remove_branch(new_node)
    assert test_tree == function_tree


def test_remove_branch2(basic_tree):
    # Same test, slightly different function input
    test_tree = deepcopy(basic_tree)
    test_tree.remove_node(test_tree["Triangle"])

    function_tree = deepcopy(basic_tree)
    new_node = GeometryNode(parent=function_tree["root"])
    new_node.name = "node"
    function_tree.add_node(new_node, children=["Triangle"])
    function_tree.remove_branch(function_tree["node"])
    assert test_tree == function_tree


def test_get_parent(basic_tree):
    assert basic_tree["root"] == basic_tree["Triangle"].parent

    assert basic_tree["root"].key == basic_tree["Triangle"].parent_key

    assert basic_tree["root"].name == basic_tree["Triangle"].parent_name


def test_get_children(basic_tree):
    assert basic_tree["root"].children == [basic_tree["Triangle"]]

    assert basic_tree["root"].child_names == ["Triangle"]

    assert basic_tree["root"].child_keys == ["Triangle"]
