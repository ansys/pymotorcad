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


from copy import copy, deepcopy

import pytest

from ansys.motorcad.core.geometry import Coordinate, Line, Region, RegionType
from ansys.motorcad.core.geometry_tree import GeometryTree, TreeRegion


@pytest.fixture(scope="session")
def sample_tree(mc):
    mc.reset_adaptive_geometry()
    return mc.get_geometry_tree()


@pytest.fixture(scope="function")
def basic_tree():
    """Return a simple GeometryTree for the purposes of testing"""
    p1 = Coordinate(25, 2.5)
    p2 = Coordinate(25, -2.5)
    p3 = Coordinate(29.330127018922, 0)
    line1 = Line(p1, p2)
    line2 = Line(p2, p3)
    line3 = Line(p3, p1)
    triangle = Region(region_type=RegionType.airgap)
    triangle.__class__ = TreeRegion
    triangle.entities.append(line1)
    triangle.entities.append(line2)
    triangle.entities.append(line3)
    triangle.name = "Triangle"
    triangle.key = "Triangle"
    triangle.children = []
    triangle.duplications = 8

    tree = GeometryTree()

    triangle.parent = tree["root"]
    tree["root"].children.append(triangle)
    tree["Triangle"] = triangle

    return tree


@pytest.fixture(scope="function")
def split_tree():
    """Return a tree with a duct split across a duplication angle"""
    p3 = Coordinate(25, 0)
    p2 = Coordinate(25, 2.5)
    p1 = Coordinate(29.330127018922, 0)

    line1 = Line(p1, p2)
    line2 = Line(p2, p3)
    line3 = Line(p3, p1)
    triangle1 = Region(region_type=RegionType.airgap)
    triangle1.__class__ = TreeRegion
    triangle1.entities.append(line1)
    triangle1.entities.append(line2)
    triangle1.entities.append(line3)
    triangle1.name = "Triangle_1"
    triangle1.key = "Triangle_1"
    triangle1.children = []
    triangle1.duplications = 8

    p4 = Coordinate(25, -2.5)
    line1 = Line(p1, p3)
    line2 = Line(p3, p4)
    line3 = Line(p4, p1)
    triangle2 = Region(region_type=RegionType.airgap)
    triangle2.__class__ = TreeRegion
    triangle2.entities.append(line1)
    triangle2.entities.append(line2)
    triangle2.entities.append(line3)
    triangle2.name = "Triangle_2"
    triangle2.key = "Triangle_2"
    triangle2.children = []
    triangle2.duplications = 8
    triangle2.rotate(Coordinate(0, 0), 360 / 8)

    test_tree = GeometryTree()

    triangle1.parent = test_tree["root"]
    test_tree["root"].children.append(triangle1)
    test_tree["Triangle_1"] = triangle1

    triangle2.parent = test_tree["root"]
    test_tree["root"].children.append(triangle2)
    test_tree["Triangle_2"] = triangle2

    return test_tree


def test_get_tree(sample_tree):
    node_keys = set(node.key for node in sample_tree)
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


def test_get_node(sample_tree):
    assert sample_tree.get_region("rotor") == sample_tree["Rotor"]

    with pytest.raises(TypeError) as e_info:
        sample_tree.get_region(5)

    assert "key must be a string or TreeRegion" in str(e_info.value)


def test_get_region_type(sample_tree):
    nodes = sample_tree.get_regions_of_type("Magnet")

    for node in nodes:
        assert node.region_type.value == "Magnet"


def test_tostring(sample_tree):
    # Test that all nodes are, at the least, present in the string representation
    string_repr = str(sample_tree)
    for node in sample_tree:
        assert node.key in string_repr


def test_add_node(basic_tree):
    # Tests the basic functionality of adding a region
    new_node = TreeRegion()
    new_node.parent = basic_tree["root"]
    new_node.name = "region"
    new_node.key = "region"
    basic_tree.get_region("root").children.append(new_node)
    basic_tree["region"] = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = TreeRegion()
    new_node2.name = "region"
    function_tree.add_region(new_node2, parent=function_tree["root"])

    assert basic_tree == function_tree


def test_get_subtree(basic_tree):
    # Test fetching subtrees
    test_tree = deepcopy(basic_tree)
    assert test_tree.get_subtree("root") == basic_tree

    test_tree.pop("root")
    function_tree = basic_tree.get_subtree("Triangle")
    assert test_tree == function_tree


def test_add_node_with_children(basic_tree):
    # Tests the parent and child reassignment performed when including those values
    test_tree = deepcopy(basic_tree)
    new_node = TreeRegion()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "region"
    new_node.key = "region"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["region"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = Region()
    new_node2.name = "region"
    function_tree.add_region(new_node2, parent="root", children=["Triangle"])

    assert test_tree == function_tree


def test_add_node_with_children_2(basic_tree):
    # Same test as above, but testing different mode of function input
    test_tree = deepcopy(basic_tree)
    new_node = TreeRegion()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "region"
    new_node.key = "node1"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["node1"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(basic_tree)
    new_node2 = Region()
    new_node2.name = "region"
    function_tree.add_region(
        new_node2, parent=function_tree["root"], children=[function_tree["Triangle"]], key="node1"
    )

    assert test_tree == function_tree


def test_add_node_errors(basic_tree):
    new_node2 = Region()
    new_node2.name = "region"

    with pytest.raises(TypeError, match="Parent must be a TreeRegion or str"):
        basic_tree.add_region(new_node2, parent=0)

    with pytest.raises(TypeError, match="Children must be a TreeRegion or str"):
        basic_tree.add_region(new_node2, children=[0, "root"])


def test_remove_node(basic_tree):
    # Test the basic functionality of removing a region
    test_tree = deepcopy(basic_tree)

    function_tree = deepcopy(basic_tree)
    new_node2 = TreeRegion()
    new_node2.name = "region"
    function_tree.add_region(new_node2, children=["Triangle"])
    function_tree.remove_region(new_node2)
    assert test_tree == function_tree


def test_equality_1(basic_tree):
    # Test trees with different sizes are detected
    test_tree = deepcopy(basic_tree)
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree.pop("Triangle")
    assert test_tree != basic_tree


def test_equality_2(basic_tree):
    # Test trees with the same nodes that only differ in structure are detected
    test_tree1 = deepcopy(basic_tree)
    new_node1 = TreeRegion()
    new_node1.name = "region"
    test_tree1.add_region(new_node1, parent="root", children=["Triangle"])

    test_tree2 = deepcopy(basic_tree)
    new_node2 = TreeRegion()
    new_node2.name = "region"
    test_tree2.add_region(new_node2, parent=test_tree2["Triangle"])

    assert test_tree2 != test_tree1


def test_equality_3(basic_tree):
    # Further test that similar but distinct structures are detected
    test_tree1 = deepcopy(basic_tree)
    new_node1 = TreeRegion()
    new_node1.name = "node1"
    test_tree1.add_region(new_node1, parent="root")
    new_node2 = TreeRegion()
    new_node2.name = "node2"
    test_tree1.add_region(new_node2, parent="node1", children=["Triangle"])

    test_tree2 = deepcopy(basic_tree)
    new_node3 = TreeRegion()
    new_node3.name = "node1"
    test_tree2.add_region(new_node3, parent="root", children=["Triangle"])
    new_node4 = TreeRegion()
    new_node4.name = "node2"
    test_tree2.add_region(new_node4, parent="Triangle")

    assert test_tree1 != test_tree2


def test_equality_4(basic_tree):
    # Test that trees with the same structure and names, but different geometries are detected
    test_tree = deepcopy(basic_tree)
    test_tree["Triangle"].entities.append(Line(Coordinate(0, 0), Coordinate(-1, 0)))
    assert test_tree != basic_tree


def test_remove_branch(basic_tree):
    # Tests the basic functionality of removing a branch
    test_tree = deepcopy(basic_tree)
    test_tree.remove_region("Triangle")

    function_tree1 = deepcopy(basic_tree)
    new_node1 = TreeRegion()
    new_node1.name = "region"
    function_tree1.add_region(new_node1, parent=function_tree1["root"], children=["Triangle"])
    function_tree1.remove_branch(new_node1)

    function_tree2 = deepcopy(basic_tree)
    new_node2 = TreeRegion()
    new_node2.name = "region"
    function_tree2.add_region(new_node2, parent=function_tree2["root"], children=["Triangle"])
    function_tree2.remove_branch("region")

    assert test_tree == function_tree1
    assert test_tree == function_tree2


def test_remove_branch2(basic_tree):
    # Same test, slightly different function input
    test_tree = deepcopy(basic_tree)
    test_tree.remove_region(test_tree["Triangle"])

    function_tree = deepcopy(basic_tree)
    new_node = TreeRegion()
    new_node.name = "region"
    function_tree.add_region(new_node, children=["Triangle"])
    function_tree.remove_branch(function_tree["region"])
    assert test_tree == function_tree


def test_get_parent(basic_tree):
    assert basic_tree["root"] == basic_tree["Triangle"].parent

    assert basic_tree["root"].key == basic_tree["Triangle"].parent_key

    assert basic_tree["root"].name == basic_tree["Triangle"].parent_name

    assert basic_tree["root"].parent_name == ""
    assert basic_tree["root"].parent_key == ""


def test_get_children(basic_tree):
    assert basic_tree["root"].children == [basic_tree["Triangle"]]

    assert basic_tree["root"].child_names == ["Triangle"]

    assert basic_tree["root"].child_keys == ["Triangle"]


def test_fix_region1(split_tree, basic_tree, mc):
    # Test that a region is correctly fixed when it crosses the lower boundary

    basic_tree._motorcad_instance = mc
    basic_tree.fix_duct_geometry("Triangle")

    assert split_tree == basic_tree


def test_fix_region2(basic_tree, split_tree, mc):
    # Test that a region is correctly fixed when it crosses the upper boundary

    basic_tree._motorcad_instance = mc

    basic_tree["Triangle"].rotate(Coordinate(0, 0), 45)
    basic_tree.fix_duct_geometry("Triangle")

    # Labeling is slightly different, so the split tree must be updated
    node1 = copy(split_tree["Triangle_1"])
    node2 = copy(split_tree["Triangle_2"])

    node1.name = "Triangle_2"
    node1.key = "Triangle_2"
    split_tree.add_region(node1)

    node2.name = "Triangle_1"
    node2.key = "Triangle_1"
    split_tree.add_region(node2)

    assert split_tree == basic_tree


def test_fix_region3(basic_tree, mc):
    # Test that a region is unaffected when already valid

    basic_tree["Triangle"].rotate(Coordinate(0, 0), 22.5)

    function_tree = deepcopy(basic_tree)
    function_tree._motorcad_instance = mc
    function_tree.fix_duct_geometry("Triangle")

    assert basic_tree == function_tree


def test_linked_regions(sample_tree):
    # Make certain connections, if present, are mutual
    for node in sample_tree:
        for linked in node.linked_regions:
            assert node in linked.linked_regions
