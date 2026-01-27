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

import builtins
from copy import copy, deepcopy
import math
from math import inf, isclose, pi, radians, sin, sqrt
import tempfile

import pytest

from RPC_Test_Common import get_dir_path
from ansys.motorcad.core import MotorCADError, geometry
from ansys.motorcad.core.geometry import (
    GEOM_TOLERANCE,
    Arc,
    Coordinate,
    EntityList,
    Line,
    MagnetisationDirection,
    Region,
    RegionMagnet,
    RegionType,
    _Orientation,
    _orientation_of_three_points,
    get_bezier_points,
    rt_to_xy,
)
from ansys.motorcad.core.geometry_shapes import eq_triangle_h, square, triangular_notch
import ansys.motorcad.core.rpc_client_core as rpc_client_core
from ansys.motorcad.core.rpc_client_core import DEFAULT_INSTANCE, set_default_instance


def generate_constant_region():
    region = geometry.Region(region_type=RegionType.stator_air)
    region.name = "testing_region"
    region.colour = (0, 0, 255)
    region.material = "Air"

    region.entities.append(geometry.Line(geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0)))
    region.entities.append(
        geometry.Arc(
            geometry.Coordinate(1, 0), geometry.Coordinate(0, 1), geometry.Coordinate(0, 0), 1
        )
    )
    region.entities.append(geometry.Line(geometry.Coordinate(0, 1), geometry.Coordinate(-1, 0)))

    return region


def create_square():
    points = [
        geometry.Coordinate(0, 0),
        geometry.Coordinate(0, 2),
        geometry.Coordinate(2, 2),
        geometry.Coordinate(2, 0),
    ]

    square = geometry.Region(region_type=RegionType.stator)

    for count, point in enumerate(points):
        if count == len(points) - 1:
            square.add_entity(geometry.Line(point, points[0]))
        else:
            square.add_entity(geometry.Line(point, points[count + 1]))

    return square


def create_triangle():
    points = [geometry.Coordinate(1, 2.2), geometry.Coordinate(2.2, 1), geometry.Coordinate(4, 4)]

    triangle = geometry.Region(region_type=RegionType.stator)

    for count, point in enumerate(points):
        if count == len(points) - 1:
            triangle.add_entity(geometry.Line(point, points[0]))
        else:
            triangle.add_entity(geometry.Line(point, points[count + 1]))

    return triangle


def create_lines_from_points(points):
    lines = []

    for count, point in enumerate(points):
        if count == len(points) - 1:
            lines.append(geometry.Line(point, points[0]))
        else:
            lines.append(geometry.Line(point, points[count + 1]))

    return lines


def test_set_get_winding_coil(mc):
    phase = 1
    path = 1
    coil = 1

    go_slot = 2
    go_position = "C"
    return_slot = 8
    return_position = "C"
    turns = 10

    mc.set_winding_coil(
        phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    )

    (
        go_slot_test,
        go_position_test,
        return_slot_test,
        return_position_test,
        turns_test,
    ) = mc.get_winding_coil(phase, path, coil)

    assert go_slot == go_slot_test
    assert go_position == go_position_test
    assert return_slot == return_slot_test
    assert return_position == return_position_test
    assert turns == turns_test


def test_check_if_geometry_is_valid(mc):
    # base_test_file should have valid geometry
    mc.check_if_geometry_is_valid(0)

    save_slot_depth = mc.get_variable("Slot_Depth")

    mc.set_variable("Slot_Depth", 50)
    with pytest.raises(MotorCADError):
        mc.check_if_geometry_is_valid(0)

    # Check resetting geometry works
    mc.check_if_geometry_is_valid(1)

    mc.set_variable("Slot_Depth", save_slot_depth)


def test_set_adaptive_parameter_value(mc):
    parameter_name = "test_parameter"
    parameter_value = 100

    mc.set_adaptive_parameter_value(parameter_name, parameter_value)
    assert mc.get_array_variable("AdaptiveTemplates_Parameters_Name", 0) == parameter_name
    assert mc.get_array_variable("AdaptiveTemplates_Parameters_Value", 0) == parameter_value

    parameter_value = 70
    # update existing parameter
    mc.set_adaptive_parameter_value(parameter_name, parameter_value)
    assert mc.get_array_variable("AdaptiveTemplates_Parameters_Name", 0) == parameter_name
    assert mc.get_array_variable("AdaptiveTemplates_Parameters_Value", 0) == parameter_value


def test_set_adaptive_parameter_value_incorrect_type(mc):
    with pytest.raises(MotorCADError):
        mc.set_adaptive_parameter_value("incorrect_type", "test_string")


def test_get_adaptive_parameter_value(mc):
    mc.set_adaptive_parameter_value("test_parameter_1", 100)

    value = mc.get_adaptive_parameter_value("test_parameter_1")
    assert value == 100


def test_get_adaptive_parameter_value_does_not_exist(mc):
    with pytest.raises(Exception) as e_info:
        mc.get_adaptive_parameter_value("testing_parameter")

    assert "No adaptive parameter found with name" in str(e_info.value)


def test_set_adaptive_parameter_default(mc):
    mc.set_adaptive_parameter_default("testing_parameter_default", 100)
    assert mc.get_adaptive_parameter_value("testing_parameter_default") == 100
    # As parameter already exists, this should not change the value
    mc.set_adaptive_parameter_default("testing_parameter_default", 200)
    assert mc.get_adaptive_parameter_value("testing_parameter_default") == 100


def test_get_region(mc):
    expected_region = generate_constant_region()
    mc.set_region(expected_region)

    region = mc.get_region(expected_region.name)
    assert region == expected_region

    with pytest.raises(Exception) as e_info:
        mc.get_region("Rotor_Magnet")

    assert ("region" in str(e_info.value)) and ("name" in str(e_info.value))


def test_get_region_dxf(mc):
    mc.load_dxf_file(get_dir_path() + r"\test_files\dxf_import.dxf")
    expected_region = geometry.Region(region_type=RegionType.dxf_import)
    expected_region.name = "DXFRegion_Rotor"
    expected_region.colour = (192, 192, 192)
    expected_region.duplications = 8
    expected_region.add_entity(
        geometry.Arc(
            geometry.Coordinate(27.5, 0),
            geometry.Coordinate(19.4454364826301, 19.4454364826301),
            geometry.Coordinate(0, 0),
            27.5,
        )
    )
    expected_region.add_entity(
        geometry.Line(
            geometry.Coordinate(19.4454364826301, 19.4454364826301), geometry.Coordinate(0, 0)
        )
    )
    expected_region.add_entity(
        geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(27.5, 0))
    )

    region = mc.get_region_dxf("DXFRegion_Rotor")
    assert region == expected_region

    with pytest.raises(Exception) as e_info:
        mc.get_region_dxf("Hello_World")

    assert ("region" in str(e_info.value)) and ("name" in str(e_info.value))


def test_set_region(mc):
    region = generate_constant_region()
    mc.set_region(region)
    returned_region = mc.get_region("testing_region")
    assert returned_region == region


def test_load_adaptive_script(mc):
    """Test loading adaptive template script into Motor-CAD from file."""
    filepath = get_dir_path() + r"\test_files\adaptive_templates_script.py"
    # load file into Motor-CAD
    mc.load_adaptive_script(filepath)

    num_lines = mc.get_variable("AdaptiveTemplates_ScriptLines")
    # open file and sum number of lines and check against number of lines from Motor-CAD
    with open(filepath, "r") as f:
        num_lines_file = sum(1 for _ in f)

    assert num_lines == num_lines_file


def test_save_adaptive_script(mc):
    """Test save adaptive template script from Motor-CAD to specified file path."""
    filepath = get_dir_path() + r"\test_files\adaptive_templates_script.py"
    mc.load_adaptive_script(filepath)
    num_lines = mc.get_variable("AdaptiveTemplates_ScriptLines")

    filepath = tempfile.gettempdir() + r"\adaptive_templates_script.py"
    mc.save_adaptive_script(filepath)
    # sum number of lines in saved file and check against number of lines from Motor-CAD
    with open(filepath, "r") as f:
        num_lines_file = sum(1 for _ in f)

    assert num_lines == num_lines_file


def test_region_add_entity_line():
    # generate entity to add to region
    entity = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))

    expected_region = generate_constant_region()
    expected_region.entities.append(entity)

    region = generate_constant_region()
    region.add_entity(entity)

    assert region == expected_region


def test_region_add_entity_arc():
    # generate entity to add to region
    entity = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    expected_region = generate_constant_region()
    expected_region.entities.append(entity)

    region = generate_constant_region()
    region.add_entity(entity)

    assert region == expected_region


def test_region_insert_entity():
    entity = geometry.Line(geometry.Coordinate(-2, 2), geometry.Coordinate(2, 3))

    expected_region = generate_constant_region()
    expected_region.entities.insert(1, entity)

    region = generate_constant_region()
    region.insert_entity(1, entity)

    assert region == expected_region


def test_region_insert_polyline():
    polyline = [
        geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1)),
        geometry.Arc(
            geometry.Coordinate(1, 1), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
        ),
        geometry.Line(geometry.Coordinate(1, 0), geometry.Coordinate(0, 0)),
    ]

    expected_region = generate_constant_region()
    expected_region.entities = polyline + expected_region.entities

    region = generate_constant_region()
    region.insert_polyline(0, polyline)

    assert region == expected_region


def test_region_remove_entity():
    expected_region = generate_constant_region()

    entity = expected_region.entities[1]
    expected_region.entities.remove(entity)

    region = generate_constant_region()
    region.remove_entity(entity)

    assert region == expected_region


def test_region_from_json():
    raw_region = {
        "name": "test_region",
        "name_base": "test_region_base",
        "material": "copper",
        "colour": {"r": 240, "g": 0, "b": 0},
        "area": 5.1,
        "centroid": {"x": 0.0, "y": 1.0},
        "region_coordinate": {"x": 0.0, "y": 1.1},
        "duplications": 10,
        "entities": [],
        "parent_name": "Insulation",
        "child_names": ["Duct", "Duct_1"],
        "region type": RegionType.stator_copper,
        "mesh_length": 0.035,
        "singular": False,
        "linked_regions": ["linked_region", "linked_region_1"],
        "on_boundary": True,
    }

    test_region = geometry.Region(region_type=RegionType.stator_copper)
    test_region.name = "test_region"
    test_region._base_name = "test_region_base"
    test_region.material = "copper"
    test_region.colour = (240, 0, 0)
    test_region._area = 5.1
    test_region._centroid = geometry.Coordinate(0.0, 1.0)
    test_region._region_coordinate = geometry.Coordinate(0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []
    test_region.parent_name = "Insulation"
    test_region._child_names = ["Duct", "Duct_1"]
    test_region.mesh_length = (0.035,)
    test_region.singular = False
    test_region._linked_region_names = ["linked_region", "linked_region_1"]
    test_region.singular = False
    linked_region = geometry.Region(region_type=RegionType.stator_copper)
    linked_region.name = "linked_region"
    linked_region_1 = geometry.Region(region_type=RegionType.stator_copper)
    linked_region.name = "linked_region_1"
    test_region.linked_regions = [linked_region, linked_region_1]

    region = geometry.Region._from_json(raw_region)

    assert region == test_region


def test_region_to_json():
    raw_region = {
        "name": "test_region",
        "name_base": "test_region_base",
        "material": "copper",
        "material_weight_component_type": 2,
        "material_weight_material_type": "Any",
        "colour": {"r": 240, "g": 0, "b": 0},
        "area": 5.1,
        "centroid": {"x": 0.0, "y": 1.0},
        "region_coordinate": {"x": 0.0, "y": 1.1},
        "duplications": 10,
        "entities": [],
        "lamination_type": "",
        "parent_name": "Insulation",
        "region_type": RegionType.stator_copper.value,
        "mesh_length": 0.035,
        "singular": True,
        "linked_regions": [],
        "extrusion_blocks": [],
    }

    test_region = geometry.Region(region_type=RegionType.stator_copper)
    test_region.name = "test_region"
    test_region._base_name = "test_region_base"
    test_region.material = "copper"
    test_region.colour = (240, 0, 0)
    test_region._area = 5.1
    test_region._centroid = geometry.Coordinate(0.0, 1.0)
    test_region._region_coordinate = geometry.Coordinate(0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []
    test_region.parent_name = "Insulation"
    test_region.mesh_length = 0.035
    test_region.singular = True
    test_region.linked_regions = []

    assert test_region._to_json() == raw_region

    # test no material specified
    raw_region["material"] = ""
    del test_region._raw_region["material"]
    test_region.material = ""

    assert test_region._to_json() == raw_region

    # test changing material with a previous material specified
    raw_region["material"] = "M350-35A"
    test_region.material = "M350-35A"

    assert test_region._to_json() == raw_region


def test_region_is_closed():
    region = generate_constant_region()
    assert region.is_closed()


def test_EntityList_is_closed():
    region = generate_constant_region()
    assert region.entities.is_closed

    # Check an empty list returns as False
    test_el1 = EntityList()
    assert test_el1.is_closed == False

    # Test an open polygon is not closed
    test_el1.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
    test_el1.append(Line(Coordinate(1, 1), Coordinate(1, 0)))
    test_el1.append(Line(Coordinate(1, 0), Coordinate(0.5, 0)))
    assert test_el1.is_closed == False


def test_EntityList_self_intersecting():
    # Test that intersection detection works properly on arcs
    test_el1 = EntityList()
    test_el1.append(Arc(Coordinate(0, 1), Coordinate(1, 0), centre=Coordinate(0.6, 0.6)))
    test_el1.append(Line(Coordinate(0.4, 0.4), Coordinate(0, 1)))
    test_el1.append(Line(Coordinate(1, 0), Coordinate(1, 1)))
    test_el1.append(Line(Coordinate(1, 1), Coordinate(0.4, 0.4)))
    assert test_el1.self_intersecting == False

    # Test convex polygons are not detected as intersecting
    test_el2 = EntityList()
    test_el2.append(Line(Coordinate(0, 3), Coordinate(0, 0)))
    test_el2.append(Line(Coordinate(0, 0), Coordinate(2, 0)))
    test_el2.append(Line(Coordinate(2, 0), Coordinate(2, 1)))
    test_el2.append(Line(Coordinate(2, 1), Coordinate(1, 1)))
    test_el2.append(Line(Coordinate(1, 1), Coordinate(1, 2)))
    test_el2.append(Line(Coordinate(1, 2), Coordinate(2, 2)))
    test_el2.append(Line(Coordinate(2, 2), Coordinate(2, 3)))
    test_el2.append(Line(Coordinate(2, 3), Coordinate(0, 3)))
    assert test_el2.self_intersecting == False

    # Test intersections are properly detected
    test_el3 = EntityList()
    test_el3.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
    test_el3.append(Line(Coordinate(1, 1), Coordinate(0, 1)))
    test_el3.append(Line(Coordinate(0, 1), Coordinate(1, 0)))
    test_el3.append(Line(Coordinate(1, 0), Coordinate(0, 0)))
    assert test_el3.self_intersecting == True


def test_EntityList_is_anticlockwise():
    assert generate_constant_region().entities.is_anticlockwise == True

    # Test opposite winding
    test_el2 = EntityList()
    test_el2.append(Line(Coordinate(0, 0), Coordinate(0, 1)))
    test_el2.append(Line(Coordinate(0, 1), Coordinate(1, 1)))
    test_el2.append(Line(Coordinate(1, 1), Coordinate(1, 0)))
    test_el2.append(Line(Coordinate(1, 0), Coordinate(0, 0)))
    assert test_el2.is_anticlockwise == False

    # Test that arcs with endpoints that would result in opposite ordering if connected with a line
    # are correctly accounted for
    test_el3 = EntityList()
    test_el3.append(Line(Coordinate(0, 0), Coordinate(0, 2)))
    test_el3.append(
        Arc.from_coordinates(Coordinate(0.2, 2.4), Coordinate(-0.3, 1), Coordinate(0, 0))
    )
    test_el3.append(Line(Coordinate(0, 2), Coordinate(0.2, 2.4)))
    assert test_el3.is_anticlockwise == True

    # Test error detection
    with pytest.raises(Exception, match="Entities must be closed and nonintersecting"):
        test_el4 = EntityList()
        test_el4.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
        test_el4.append(Line(Coordinate(1, 1), Coordinate(0, 1)))
        test_el4.append(Line(Coordinate(0, 1), Coordinate(1, 0)))
        test_el4.append(Line(Coordinate(1, 0), Coordinate(0, 0)))
        test_el4.is_anticlockwise


def test_EntityList_has_valid_geometry():
    assert generate_constant_region().entities.has_valid_geometry == True

    # Test self_intersecting
    test_el1 = EntityList()
    test_el1.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
    test_el1.append(Line(Coordinate(1, 1), Coordinate(0, 1)))
    test_el1.append(Line(Coordinate(0, 1), Coordinate(1, 0)))
    test_el1.append(Line(Coordinate(1, 0), Coordinate(0, 0)))
    assert test_el1.has_valid_geometry == False

    # Test is_anticlockwise
    test_el2 = EntityList()
    test_el2.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
    test_el2.append(Line(Coordinate(1, 1), Coordinate(1, 0)))
    test_el2.append(Line(Coordinate(1, 0), Coordinate(0, 0)))
    assert test_el2.has_valid_geometry == False

    # Test is_closed
    test_el3 = EntityList()
    test_el3.append(Line(Coordinate(0, 0), Coordinate(1, 1)))
    test_el3.append(Line(Coordinate(1, 1), Coordinate(1, 0)))
    test_el3.append(Line(Coordinate(1, 0), Coordinate(0.5, 0)))
    assert test_el3.has_valid_geometry == False


def test_set_linked_region():
    # depreciated functionality, here for backwards compatibility
    region = generate_constant_region()

    region_linked = Region(region_type=RegionType.stator)
    region_linked.name = "linked_region_test"
    # set linked region
    region.linked_region = region_linked
    region_linked.linked_region = region

    assert region_linked.name in region.linked_region_names
    assert region.name in region_linked.linked_region_names


def test_set_linked_regions():
    region = generate_constant_region()

    region_linked = Region()
    region_linked.name = "linked_region_test"
    # set linked region
    region.linked_regions = [region_linked]
    region_linked.linked_regions = [region]

    assert region_linked.name in region.linked_region_names
    assert region.name in region_linked.linked_region_names


def test_set_singular_region():
    region = generate_constant_region()
    region.singular = True

    assert region._singular is True
    assert region.singular is True


def test_region_contains_same_entities():
    region = generate_constant_region()

    expected_region = deepcopy(region)
    expected_region.entities.reverse()

    assert region == expected_region


def test_region_get_parent(mc):
    pocket = mc.get_region("rotor pocket")
    expected_region = mc.get_region("rotor")

    assert pocket.parent == expected_region


def test_region_set_parent(mc):
    shaft = mc.get_region("Shaft")
    square = create_square()
    square.name = "square"
    square.parent = shaft
    mc.set_region(square)

    shaft_expected = mc.get_region("Shaft")
    assert square.name in shaft_expected._child_names


def test_region_children(mc):
    rotor = mc.get_region("rotor")
    children = rotor.children

    assert len(children) == 16


def test_region_linked_regions(mc):
    duct = mc.get_region("RotorDuctFluidRegion_1", get_linked=True)
    assert len(duct.linked_regions) == 1


def test_reverse_entity():
    entity = geometry.Entity(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))
    expected_entity = geometry.Entity(geometry.Coordinate(1, 1), geometry.Coordinate(0, 0))

    entity.reverse()

    assert entity == expected_entity


def test_reverse_line():
    region = generate_constant_region()
    line = region.entities[0]
    expected_line = geometry.Line(line.end, line.start)
    line.reverse()

    assert line == expected_line


def test_reverse_arc():
    region = generate_constant_region()
    arc = region.entities[1]
    expected_line = geometry.Arc(arc.end, arc.start, arc.centre, -arc.radius)
    arc.reverse()

    assert arc == expected_line


def test_entities_same_subset():
    arc1 = Arc(Coordinate(1, 0), Coordinate(0, 1), radius=1)
    arc2 = Arc(Coordinate(0, 1), Coordinate(-1, 0), radius=1)
    ent1 = geometry.EntityList([arc1, arc2])
    ent2 = geometry.EntityList([arc1])

    assert ent1 != ent2


def test_entities_same():
    region = generate_constant_region()
    region_expected = generate_constant_region()

    assert region.entities == region_expected.entities


def test_entities_same_1():
    region_1 = generate_constant_region()

    entities_list_duplicate = deepcopy(region_1.entities)

    entities = [entities_list_duplicate[i] for i in range(1, len(entities_list_duplicate))] + [
        entities_list_duplicate[i] for i in range(0, 1)
    ]
    region_2 = geometry.Region(region_type=RegionType.stator)
    region_2.entities = entities

    assert region_1.entities == region_2.entities


def test_entities_same_reverse():
    region_1 = generate_constant_region()

    region_2 = geometry.Region(RegionType.stator_air)
    region_2.entities = deepcopy(region_1.entities)
    region_2.entities.reverse()

    assert region_1.entities == region_2.entities


def test_reverse_entities():
    region = generate_constant_region()

    duplicate_entities = deepcopy(region.entities)
    duplicate_entities = list(duplicate_entities)

    # Use list reverse function
    duplicate_entities.reverse()

    expected_entities = geometry.EntityList()

    for entity in duplicate_entities:
        if isinstance(entity, geometry.Line):
            expected_entities.append(geometry.Line(entity.end, entity.start))
        elif isinstance(entity, geometry.Arc):
            expected_entities.append(
                geometry.Arc(entity.end, entity.start, entity.centre, -entity.radius)
            )

    assert region.entities._entities_same(expected_entities) is False
    assert region.entities._entities_same(expected_entities, check_reverse=True) is True


def test_reverse_entities_2():
    region_1 = generate_constant_region()
    region_2 = geometry.Region(RegionType.stator_air)

    region_2.entities = deepcopy(region_1.entities)
    region_2.entities.reverse()
    assert region_1.entities._entities_same(region_2.entities, check_reverse=False) is False
    assert region_1.entities._entities_same(region_2.entities, check_reverse=True) is True

    region_2.entities.reverse()
    assert region_1.entities._entities_same(region_2.entities, check_reverse=False) is True


def test_line_get_coordinate_from_percentage_distance():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(2, 0))

    coord = line.get_coordinate_from_percentage_distance(geometry.Coordinate(0, 0), 0.5)
    assert coord == geometry.Coordinate(1, 0)


def test_line_get_coordinate_from_distance():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(2, 0))

    # test using the 'distance' argument
    assert line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1) == geometry.Coordinate(
        1, 0
    )
    # test using the 'fraction' argument
    assert line.get_coordinate_from_distance(
        geometry.Coordinate(0, 0), fraction=0.5
    ) == geometry.Coordinate(1, 0)
    # test using the 'percentage' argument
    assert line.get_coordinate_from_distance(
        geometry.Coordinate(0, 0), percentage=50
    ) == geometry.Coordinate(1, 0)

    # test that warnings are raised when multiple arguments are given
    # distance and fraction
    with pytest.warns(UserWarning) as record:
        coord = line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1, fraction=0.6)
    assert "Both distance and fraction provided" in record[0].message.args[0]
    # check that distance is used
    assert coord == line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1)

    # distance and percentage
    with pytest.warns(UserWarning) as record:
        coord = line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1, percentage=40)
    assert "Both distance and percentage provided" in record[0].message.args[0]
    # check that distance is used
    assert coord == line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1)

    # fraction and percentage
    with pytest.warns(UserWarning) as record:
        coord = line.get_coordinate_from_distance(
            geometry.Coordinate(0, 0), fraction=0.6, percentage=40
        )
    assert "Both fraction and percentage provided" in record[0].message.args[0]
    # check that fraction is used
    assert coord == line.get_coordinate_from_distance(geometry.Coordinate(0, 0), fraction=0.6)

    # distance, fraction and percentage
    with pytest.warns(UserWarning) as record:
        coord = line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1, 0.6, 40)
    assert "Both distance and fraction provided" in record[0].message.args[0]
    # check that both warnings are given
    assert "Both distance and percentage provided" in record[1].message.args[0]
    # check that distance is used
    assert coord == line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1)

    # neither distance, fraction or percentage are provided
    with pytest.raises(Exception) as e_info:
        coord = line.get_coordinate_from_distance(line.start)
    assert "provide either a distance, fraction or percentage" in str(e_info)

    # Test if reference coordinate isn't start or end (ref coordinate near start)
    assert line.get_coordinate_from_distance(geometry.Coordinate(0.5, 0), 1) == geometry.Coordinate(
        1.5, 0
    )

    # Test if reference coordinate isn't start or end (ref coordinate near end)
    assert line.get_coordinate_from_distance(geometry.Coordinate(1.5, 0), 1) == geometry.Coordinate(
        0.5, 0
    )

    # Test that reference coordinate not on the line raises an exception
    with pytest.raises(ValueError):
        line.get_coordinate_from_distance(geometry.Coordinate(0.5, 0.5), 1)


def test_line_length():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))

    assert line.length == sqrt(2)


def test_line_get_coordinate_distance():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(0, 2))
    point = Coordinate(1, 1)
    assert line.get_coordinate_distance(point) == 1


def test_coordinate_distance():
    coordinate_1 = geometry.Coordinate(0, 1)
    coordinate_2 = geometry.Coordinate(0, 2)
    assert coordinate_1.distance(coordinate_2) == 1

    # Make sure type error is raised if we try to find distance to something that isn't a coordinate
    with pytest.raises(TypeError):
        coordinate_1.distance(1)


def test_arc_get_coordinate_from_fractional_distance():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    coord_1 = arc.get_coordinate_from_percentage_distance(geometry.Coordinate(-1, 0), 0.5)
    assert isclose(coord_1.x, 0, abs_tol=1e-12)
    assert isclose(coord_1.y, -1, abs_tol=1e-12)

    # test an arc that failed with the old definition of get_coordinate_from_percentage_distance()
    arc_2 = geometry.Arc(geometry.Coordinate(62, 20), geometry.Coordinate(56, 33), radius=45)
    coord_2 = arc_2.get_coordinate_from_percentage_distance(arc_2.end, 1e-13)
    assert math.isclose(arc_2.end.x, coord_2.x, abs_tol=1e-12)
    assert math.isclose(arc_2.end.y, coord_2.y, abs_tol=1e-12)
    coord_3 = arc_2.get_coordinate_from_percentage_distance(arc_2.start, 1e-13)
    assert math.isclose(arc_2.start.x, coord_3.x, abs_tol=1e-12)
    assert math.isclose(arc_2.start.y, coord_3.y, abs_tol=1e-12)
    # test arc drawn clockwise
    arc_4 = geometry.Arc(geometry.Coordinate(56, 33), geometry.Coordinate(62, 20), radius=45)
    coord_4 = arc_4.get_coordinate_from_percentage_distance(arc_4.end, 1e-13)
    assert math.isclose(arc_4.end.x, coord_4.x, abs_tol=1e-12)
    assert math.isclose(arc_4.end.y, coord_4.y, abs_tol=1e-12)
    coord_5 = arc_4.get_coordinate_from_percentage_distance(arc_4.start, 1e-13)
    assert math.isclose(arc_4.start.x, coord_5.x, abs_tol=1e-12)
    assert math.isclose(arc_4.start.y, coord_5.y, abs_tol=1e-12)
    # test arc with negative radius
    arc_6 = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), -1
    )
    coord_6 = arc_6.get_coordinate_from_percentage_distance(Coordinate(-1, 0), 0.5)
    assert math.isclose(coord_6.x, 0, abs_tol=1e-12)
    assert math.isclose(coord_6.y, 1, abs_tol=1e-12)


def test_arc_get_coordinate_from_distance():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    # test using the 'distance' argument
    coord = arc.get_coordinate_from_distance(geometry.Coordinate(-1, 0), math.pi / 2)
    assert math.isclose(coord.x, 0, abs_tol=1e-12)
    assert math.isclose(coord.y, -1, abs_tol=1e-12)

    # test for an arc with negative radius using the 'distance' argument
    arc_1 = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), -1
    )
    coord_1 = arc_1.get_coordinate_from_distance(geometry.Coordinate(-1, 0), math.pi / 2)
    assert math.isclose(coord_1.x, 0, abs_tol=1e-12)
    assert math.isclose(coord_1.y, 1, abs_tol=1e-12)

    # test an arc that failed with the old definition of get_coordinate_from_distance() using the
    # 'distance' argument
    arc_2 = geometry.Arc(geometry.Coordinate(62, 20), geometry.Coordinate(56, 33), radius=45)
    coord_2 = arc_2.get_coordinate_from_distance(arc_2.end, 1e-15)
    assert math.isclose(arc_2.end.x, coord_2.x, abs_tol=1e-12)
    assert math.isclose(arc_2.end.y, coord_2.y, abs_tol=1e-12)
    coord_3 = arc_2.get_coordinate_from_distance(arc_2.start, 1e-15)
    assert math.isclose(arc_2.start.x, coord_3.x, abs_tol=1e-12)
    assert math.isclose(arc_2.start.y, coord_3.y, abs_tol=1e-12)
    # test arc drawn clockwise using the 'distance' argument
    arc_4 = geometry.Arc(geometry.Coordinate(56, 33), geometry.Coordinate(62, 20), radius=45)
    coord_4 = arc_4.get_coordinate_from_distance(arc_4.end, 1e-15)
    assert math.isclose(arc_4.end.x, coord_4.x, abs_tol=1e-12)
    assert math.isclose(arc_4.end.y, coord_4.y, abs_tol=1e-12)
    coord_5 = arc_4.get_coordinate_from_distance(arc_4.start, 1e-15)
    assert math.isclose(arc_4.start.x, coord_5.x, abs_tol=1e-12)
    assert math.isclose(arc_4.start.y, coord_5.y, abs_tol=1e-12)
    coord_6 = arc_2.get_coordinate_from_distance(arc_2.start, 5)
    assert math.isclose(60.389142028418, coord_6.x, abs_tol=1e-12)
    assert math.isclose(24.730689908764, coord_6.y, abs_tol=1e-12)

    # test using the 'fraction' argument
    coord_7 = arc.get_coordinate_from_distance(geometry.Coordinate(-1, 0), fraction=0.5)
    assert isclose(coord_7.x, 0, abs_tol=1e-12)
    assert isclose(coord_7.y, -1, abs_tol=1e-12)

    # test using the 'percentage' argument
    coord_8 = arc.get_coordinate_from_distance(geometry.Coordinate(-1, 0), percentage=50)
    assert isclose(coord_8.x, 0, abs_tol=1e-12)
    assert isclose(coord_8.y, -1, abs_tol=1e-12)

    # test that warnings are raised when multiple arguments are given
    # distance and fraction
    with pytest.warns(UserWarning) as record:
        coord = arc.get_coordinate_from_distance(arc.start, 1, fraction=0.6)
    assert "Both distance and fraction provided" in record[0].message.args[0]
    # check that distance is used
    assert coord == arc.get_coordinate_from_distance(arc.start, 1)
    # distance and percentage
    with pytest.warns(UserWarning) as record:
        coord = arc.get_coordinate_from_distance(arc.start, 1, percentage=40)
    assert "Both distance and percentage provided" in record[0].message.args[0]
    # check that distance is used
    assert coord == arc.get_coordinate_from_distance(arc.start, 1)
    # fraction and percentage
    with pytest.warns(UserWarning) as record:
        coord = arc.get_coordinate_from_distance(arc.start, fraction=0.6, percentage=40)
    assert "Both fraction and percentage provided" in record[0].message.args[0]
    # check that fraction is used
    assert coord == arc.get_coordinate_from_distance(arc.start, fraction=0.6)
    # distance, fraction and percentage
    with pytest.warns(UserWarning) as record:
        coord = arc.get_coordinate_from_distance(arc.start, 1, 0.6, 40)
    assert "Both distance and fraction provided" in record[0].message.args[0]
    # check that both warnings are given
    assert "Both distance and percentage provided" in record[1].message.args[0]
    # check that distance is used
    assert coord == arc.get_coordinate_from_distance(arc.start, 1)
    # neither distance, fraction or percentage are provided
    with pytest.raises(Exception) as e_info:
        coord = arc.get_coordinate_from_distance(arc.start)
    assert "provide either a distance, fraction or percentage" in str(e_info)


def test_arc_length():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    assert arc.length == math.pi

    radius = 45
    line_1 = Line(Coordinate(62, 20), Coordinate(56, 33))
    arc_2 = Arc(Coordinate(62, 20), Coordinate(56, 33), radius=radius)
    assert arc_2.length > line_1.length


def test_entities_polygon():
    expected_square = create_square()

    # test functionality without reordering
    reg1 = Region(region_type=RegionType.stator)
    reg1.entities = EntityList.polygon([(0, 0), (2, 0), (2, 2), (0, 2)])
    assert expected_square == reg1

    reg2 = Region(region_type=RegionType.stator)
    reg2.entities = EntityList.polygon(
        [Coordinate(0, 0), Coordinate(2, 0), Coordinate(2, 2), Coordinate(0, 2)]
    )
    assert expected_square == reg2

    # Test warnings given when order is incorrect
    with pytest.warns(UserWarning) as record:
        reg3 = Region(region_type=RegionType.stator)
        reg3.entities = EntityList.polygon([(0, 2), (2, 2), (2, 0), (0, 0)])
    assert "Entered point order may result in invalid geometry." == record[0].message.args[0]

    # test reordering
    reg4 = Region(region_type=RegionType.stator)
    reg4.entities = EntityList.polygon([(0, 0), (2, 2), (0, 2), (2, 0)], sort=True)
    assert expected_square == reg4


def test_convert_entities_to_json():
    raw_entities = [
        {"type": "line", "start": {"x": 0.0, "y": 0.0}, "end": {"x": -1.0, "y": 0}},
        {
            "type": "arc",
            "start": {"x": -1.0, "y": 0.0},
            "end": {"x": 1.0, "y": 0.0},
            "centre": {"x": 0, "y": 0},
            "radius": 1.0,
        },
    ]

    test_entities = [
        geometry.Line(geometry.Coordinate(0.0, 0.0), geometry.Coordinate(-1.0, 0)),
        geometry.Arc(
            geometry.Coordinate(-1.0, 0.0),
            geometry.Coordinate(1.0, 0.0),
            geometry.Coordinate(0.0, 0.0),
            1.0,
        ),
    ]

    assert geometry._convert_entities_to_json(test_entities) == raw_entities


def test_convert_entities_from_json():
    raw_entities = [
        {"type": "line", "start": {"x": 0.0, "y": 0.0}, "end": {"x": -1.0, "y": 0}},
        {
            "type": "arc",
            "start": {"x": -1.0, "y": 0.0},
            "end": {"x": 1.0, "y": 0.0},
            "centre": {"x": 0, "y": 0},
            "radius": 1.0,
        },
    ]

    test_entities = [
        geometry.Line(geometry.Coordinate(0.0, 0.0), geometry.Coordinate(-1.0, 0)),
        geometry.Arc(
            geometry.Coordinate(-1.0, 0.0),
            geometry.Coordinate(1.0, 0.0),
            geometry.Coordinate(0.0, 0.0),
            1.0,
        ),
    ]

    converted_entities = geometry._convert_entities_from_json(raw_entities)
    assert isinstance(converted_entities[0], type(test_entities[0]))
    assert converted_entities[0] == test_entities[0]

    assert isinstance(converted_entities[1], type(test_entities[1]))
    assert converted_entities[1] == test_entities[1]


def test_get_entities_have_common_coordinate():
    entity_1 = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))
    entity_2 = geometry.Line(geometry.Coordinate(1, 1), geometry.Coordinate(2, 2))

    assert geometry.get_entities_have_common_coordinate(entity_1, entity_2)


def test_unite_regions(mc):
    """Test unite two regions into a single region."""
    #   Before         After
    # |--------|    |--------|
    # |  |--|  |    |        |
    # |  |  |  | -> |        |
    # |--|--|--|    |--|  |--|
    #    |  |          |  |
    #    |--|          |--|
    region_a = geometry.Region(RegionType.stator_air)
    region_b = geometry.Region(RegionType.stator_air)
    expected_region = geometry.Region(RegionType.stator_air)

    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, -1), geometry.Coordinate(-1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, 1), geometry.Coordinate(1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, 1), geometry.Coordinate(1, -1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, -1), geometry.Coordinate(-1, -1)))

    points_b = [
        geometry.Coordinate(-0.5, -2),
        geometry.Coordinate(-0.5, -0.5),
        geometry.Coordinate(0.5, -0.5),
        geometry.Coordinate(0.5, -2),
    ]

    points_expected = [
        geometry.Coordinate(-1, 1),
        geometry.Coordinate(1, 1),
        geometry.Coordinate(1, -1),
        geometry.Coordinate(0.5, -1),
        geometry.Coordinate(0.5, -2),
        geometry.Coordinate(-0.5, -2),
        geometry.Coordinate(-0.5, -1),
        geometry.Coordinate(-1, -1),
    ]

    # create and add line entities to regions from their respective points
    region_b.entities += create_lines_from_points(points_b)
    expected_region.entities += create_lines_from_points(points_expected)

    expected_region._centroid = geometry.Coordinate(0, -0.3)
    expected_region._region_coordinate = geometry.Coordinate(0, -0.3)
    expected_region.duplications = 1

    united_region = mc.unite_regions(region_a, [region_b])

    assert united_region == expected_region


def test_unite_regions_1(mc):
    """Testing two regions not touching cannot be united."""
    #          Before                         After
    # |--------|
    # |        |    |---|
    # |        |    |   |     ->    RPC error: Unable to unite regions.
    # |        |    |---|           Regions have no mutual interceptions
    # |--------|

    region_a = geometry.Region(RegionType.stator_air)
    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, -1), geometry.Coordinate(-1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, 1), geometry.Coordinate(1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, 1), geometry.Coordinate(1, -1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, -1), geometry.Coordinate(-1, -1)))

    region_b = geometry.Region(RegionType.stator_air)
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5, 10)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, 10), geometry.Coordinate(10, 10)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 10), geometry.Coordinate(10, 5)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 5), geometry.Coordinate(5, 5)))

    with pytest.raises(Exception) as e_info:
        mc.unite_regions(region_a, [region_b])

    assert "Unable to unite regions" in str(e_info.value)


def test_unite_regions_2(mc):
    """Test unite two regions into a single region. No vertices from either region are within
    the other region."""
    #     Before                    After
    #
    #      \------|                \------|
    # |-----\-|   |           |-----\     |
    # |      \|   |           |           |
    # |       \   |    ->     |           |
    # |-------|\  |           |--------\  |
    #           \ |                     \ |
    #            \|                      \|
    #
    square = create_square()
    triangle = create_triangle()

    points = [
        geometry.Coordinate(0, 2),
        geometry.Coordinate(1.2, 2),
        geometry.Coordinate(1, 2.2),
        geometry.Coordinate(4, 4),
        geometry.Coordinate(2.2, 1),
        geometry.Coordinate(2, 1.2),
        geometry.Coordinate(2, 0),
        geometry.Coordinate(0, 0),
    ]

    expected_region = geometry.Region(RegionType.stator_air)
    expected_region._centroid = geometry.Coordinate(1.57886178861789, 1.57886178861789)
    expected_region._region_coordinate = geometry.Coordinate(1.57886178861789, 1.57886178861789)

    # create and add line entities to region from their respective points
    expected_region.entities += create_lines_from_points(points)

    union = mc.unite_regions(square, [triangle])

    assert expected_region == union


def test_replace_region(mc):
    """Test replace region entities with entities from another region."""
    region_a = geometry.Region(RegionType.stator_air)
    region_a.add_entity(geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5, 10)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(5, 10), geometry.Coordinate(10, 10)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(10, 10), geometry.Coordinate(10, 5)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(10, 5), geometry.Coordinate(5, 5)))

    region_b = geometry.Region(RegionType.stator_air)
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5, 8)))
    region_b.add_entity(
        geometry.Arc(
            geometry.Coordinate(5, 8), geometry.Coordinate(7, 10), geometry.Coordinate(7, 8), -2
        )
    )
    region_b.add_entity(geometry.Line(geometry.Coordinate(7, 10), geometry.Coordinate(7.5, 10)))
    region_b.add_entity(
        geometry.Arc(
            geometry.Coordinate(7.5, 10),
            geometry.Coordinate(8.5, 10),
            geometry.Coordinate(8, 10),
            -0.5,
        )
    )
    region_b.add_entity(geometry.Line(geometry.Coordinate(8.5, 10), geometry.Coordinate(9, 10)))
    region_b.add_entity(
        geometry.Arc(
            geometry.Coordinate(9, 10), geometry.Coordinate(10, 9), geometry.Coordinate(9, 9), -1
        )
    )
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 9), geometry.Coordinate(10, 5)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 5), geometry.Coordinate(5, 5)))

    region_a.replace(region_b)

    assert region_a.entities == region_b.entities


def test_check_collisions(mc):
    """Collision Type : Collision detected.
    No vertices from the other region within the other region."""
    #      Before                          After
    #
    #      |---|
    #      |   |
    #   |--|---|--|
    #   |  |   |  |     ->      Collision detected between regions
    #   |  |   |  |
    #   |--|---|--|
    #      |   |
    #      |---|
    #
    region_a = generate_constant_region()

    region_b = geometry.Region(RegionType.stator_air)
    region_b.add_entity(geometry.Line(geometry.Coordinate(0, -2), geometry.Coordinate(1, 2)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(1, 2), geometry.Coordinate(5, -3)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, -3), geometry.Coordinate(0, -2)))

    collisions = mc.check_collisions(region_a, [region_b, mc.get_region("Stator")])
    num_collisions = len(collisions)

    assert num_collisions == 1
    assert collisions[0] == region_b


def test_check_collisions_1(mc):
    """Collision Type : Collision Detected.
    Two vertices from the other region within the other region."""
    #      Before                          After
    #
    #   |---------|
    #   |         |     ->      Collision detected between regions
    #   |  |---|  |
    #   |--|---|--|
    #      |   |
    #      |---|
    #
    region_a = generate_constant_region()

    region_b = geometry.Region(RegionType.stator_air)
    region_b.add_entity(
        geometry.Line(geometry.Coordinate(-0.2, -2), geometry.Coordinate(-0.2, 0.2))
    )
    region_b.add_entity(
        geometry.Line(geometry.Coordinate(-0.2, 0.2), geometry.Coordinate(0.2, 0.2))
    )
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, 0.2), geometry.Coordinate(0.2, -2)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, -2), geometry.Coordinate(-0.2, -2)))

    collisions = mc.check_collisions(region_a, [region_b, mc.get_region("Stator")])
    num_collisions = len(collisions)

    assert num_collisions == 1
    assert collisions[0] == region_b


def test_check_collisions_2(mc):
    """Collision Type : No collision.
    Regions touching on single entity"""
    #      Before                          After
    #
    #   |---------|
    #   |         |     ->      No collision detected between regions
    #   |         |
    #   |--|---|--|
    #      |   |
    #      |---|
    #
    region_a = generate_constant_region()

    region_b = geometry.Region(RegionType.stator_air)
    region_b.add_entity(geometry.Line(geometry.Coordinate(-0.2, -2), geometry.Coordinate(-0.2, 0)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(-0.2, 0), geometry.Coordinate(0.2, 0)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, 0), geometry.Coordinate(0.2, -2)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, -2), geometry.Coordinate(-0.2, -2)))

    collisions = mc.check_collisions(region_a, [region_b, mc.get_region("Stator")])
    num_collisions = len(collisions)

    assert num_collisions == 0


def test_check_collisions_3(mc):
    """Collision Type : Collision detected.
    No vertices from the other region within the other region.
    Square region drawn clockwise."""
    #      Before                          After
    #
    #      |---|
    #      |   |
    #   |--|---|--|
    #   |  |   |  |     ->      Collision detected between regions
    #   |  |   |  |
    #   |--|---|--|
    #      |   |
    #      |---|
    #

    points_square = [
        geometry.Coordinate(0, 0),
        geometry.Coordinate(0, 2),
        geometry.Coordinate(2, 2),
        geometry.Coordinate(2, 0),
    ]

    square = geometry.Region(RegionType.stator_air)
    # create and add line entities to region from their respective points
    square.entities += create_lines_from_points(points_square)

    points_triangle = [
        geometry.Coordinate(1, 2.2),
        geometry.Coordinate(2.2, 1),
        geometry.Coordinate(4, 4),
    ]

    triangle = geometry.Region(RegionType.stator_air)
    # create and add line entities to region from their respective points
    triangle.entities += create_lines_from_points(points_triangle)

    collisions = mc.check_collisions(triangle, [square])
    assert len(collisions) == 1
    assert collisions[0] == square

    collisions = mc.check_collisions(square, [triangle])
    assert len(collisions) == 1
    assert collisions[0] == triangle


def test_delete_region(mc_reset_to_default_on_teardown):
    stator = mc_reset_to_default_on_teardown.get_region("Stator")

    mc_reset_to_default_on_teardown.delete_region(stator)

    with pytest.raises(Exception) as e_info:
        mc_reset_to_default_on_teardown.get_region("Stator")

    assert "Failed to find region with name" in str(e_info.value)


def test_coordinate_operators():
    c1 = Coordinate(5, 5)
    c2 = Coordinate(1, 1)
    c_res_exp = Coordinate(4, 4)
    assert (c1 - c2) == c_res_exp

    c1 = Coordinate(-5, -5)
    c2 = Coordinate(1, 1)
    c_res_exp = Coordinate(-6, -6)
    assert (c1 - c2) == c_res_exp

    c1 = Coordinate(5, 5)
    c2 = Coordinate(1, 1)
    c_res_exp = Coordinate(6, 6)
    assert (c1 + c2) == c_res_exp

    c1 = Coordinate(5, 4)
    assert abs(c1) == sqrt(41)


def test_line_coordinate_on_entity():
    p0 = Coordinate(0, 0)
    p1 = Coordinate(10, 0)
    l0 = Line(p0, p1)

    p_2 = Coordinate(5, 0)
    p_3 = Coordinate(11, 0)
    p_4 = Coordinate(5, 0.1)
    assert l0.coordinate_on_entity(p_2) is True
    assert l0.coordinate_on_entity(p_4) is False
    assert l0.coordinate_on_entity(p_3) is False


def test_arc_start_end_angle():
    p_centre = Coordinate(2, 2)
    p_end = Coordinate(4, 2)
    p_start = Coordinate(2, 0)
    radius = -2

    a0 = Arc(p_start, p_end, p_centre, radius)

    assert a0.start_angle == -90
    assert a0.end_angle == 0


def test_arc_coordinate_on_entity():
    pc = Coordinate(0, 0)
    p0 = Coordinate(0, -4)
    p1 = Coordinate(0, 4)
    radius = abs(p0 - pc)

    a1 = Arc(p0, p1, pc, radius)

    p2 = Coordinate(4, 0)
    p3 = p2 / 2
    p4 = Coordinate(-4, 0)

    assert a1.coordinate_on_entity(p2)
    assert a1.coordinate_on_entity(p3) is False
    assert a1.coordinate_on_entity(p4) is False

    a1 = Arc(p0, p1, pc, -radius)

    assert a1.coordinate_on_entity(p2) is False
    assert a1.coordinate_on_entity(p3) is False
    assert a1.coordinate_on_entity(p4) is True

    p_c = Coordinate(0, 0)

    p0 = Coordinate(1, 1)
    p1 = Coordinate(1, -1)
    radius = sqrt(2)

    a1 = Arc(p0, p1, p_c, -radius)

    p_test1 = Coordinate(radius, 0)
    p_test2 = Coordinate(-radius, 0)
    assert a1.coordinate_on_entity(p_test1) is True
    assert a1.coordinate_on_entity(p_test2) is False

    a2 = Arc(p0, p1, p_c, radius)
    assert a2.coordinate_on_entity(p_test1) is False
    assert a2.coordinate_on_entity(p_test2) is True


def test_midpoints():
    p0 = Coordinate(-2, 4)
    p1 = Coordinate(10, -8)
    p01 = p1 - p0
    l0 = Line(p0, p1)
    assert l0.midpoint == (p0 + p01 / 2)

    pc = Coordinate(0, 0)
    p0 = Coordinate(3, 3)
    p1 = Coordinate(3, -3)
    a0 = Arc(p0, p1, pc, -abs(p1 - pc))
    assert a0.midpoint == Coordinate(abs(p1 - pc), 0)

    pc = Coordinate(0, 0)
    p0 = Coordinate(3, 0)
    p1 = Coordinate(0, 3)

    radius = 3 * sin(radians(45))
    a0 = Arc(p0, p1, pc, -abs(p1 - pc))
    assert a0.midpoint == Coordinate(-radius, -radius)

    a0 = Arc(p0, p1, pc, abs(p1 - pc))
    assert a0.midpoint == Coordinate(radius, radius)

    a0 = Arc(p1, p0, pc, -abs(p1 - pc))
    assert a0.midpoint == Coordinate(radius, radius)

    a0 = Arc(p1, p0, pc, abs(p1 - pc))
    assert a0.midpoint == Coordinate(-radius, -radius)


def test_total_angle():
    pc = Coordinate(0, 0)
    p0 = Coordinate(0, 5)
    p1 = Coordinate(-5, 0)
    a1 = Arc(p0, p1, pc, abs(p0 - pc))
    assert a1.total_angle == 90

    pc = Coordinate(-3, -1)
    p0 = Coordinate(-7, -1)
    p1 = Coordinate(-3, -5)
    a1 = Arc(p0, p1, pc, abs(p0 - pc))
    assert a1.total_angle == 90

    p0 = Coordinate(*rt_to_xy(1, 60))
    p1 = Coordinate(*rt_to_xy(1, 120))
    pc = Coordinate(0, 0)
    a1 = Arc(p0, p1, pc, 1)
    assert isclose(a1.total_angle, 60, abs_tol=1e-6)
    a1 = Arc(p0, p1, pc, -1)
    assert isclose(a1.total_angle, 300, abs_tol=1e-6)
    a1 = Arc(p1, p0, pc, 1)
    assert isclose(a1.total_angle, 300, abs_tol=1e-6)
    a1 = Arc(p1, p0, pc, -1)
    assert isclose(a1.total_angle, 60, abs_tol=1e-6)


def test_is_matplotlib_installed(monkeypatch):
    original_import = builtins.__import__

    def fail_import(name, *args, **kwargs):
        if name == "matplotlib":
            raise ImportError
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_import)

    region = generate_constant_region()
    import ansys.motorcad.core.geometry_drawing as geom_import

    with pytest.raises(ImportError):
        geom_import.draw_objects(region)


def test_strings(capsys):
    c = Coordinate(7, -10)
    print(c)
    output = capsys.readouterr()
    assert output.out.strip() == "[7, -10]"


def test_add_point():
    region = generate_constant_region()

    points = region.points
    new_point = region.entities[0].midpoint
    region.add_point(new_point)

    # Expected result
    points.insert(1, new_point)
    assert points == region.points

    region = generate_constant_region()
    with pytest.raises(Exception):
        region.add_point(Coordinate(100, 100))

    points = region.points
    new_point = region.entities[1].midpoint
    region.add_point(new_point)

    # Expected result
    points.insert(2, new_point)
    assert points == region.points


def test_edit_point():
    region = generate_constant_region()
    points = region.points
    new_coord = Coordinate(0, 0)
    region.edit_point(points[0], new_coord)
    assert region.entities[0].start == new_coord
    assert region.entities[2].end == new_coord

    region = generate_constant_region()
    points = region.points

    # Move arc point too far
    translate = Coordinate(2, 2)
    with pytest.raises(Exception):
        region.edit_point(points[2], points[2] + translate)

    ref_region = generate_constant_region()
    region = generate_constant_region()
    points = region.points

    translate = Coordinate(0.2, 0.2)
    region.edit_point(points[2], points[2] + translate)
    region.edit_point(points[1], points[1] + translate)

    assert region.entities[0].end == ref_region.entities[0].end + translate
    assert region.entities[1].start == ref_region.entities[1].start + translate
    assert region.entities[1].end == ref_region.entities[1].end + translate  #
    assert region.entities[2].start == ref_region.entities[2].start + translate


def test_consolidate_lines_1():
    # test for consolidating lines

    # create 4 lists of 11 colinear points. Together the 44 points form a square with width = 10 mm.
    # . . . . . . . . . . .
    # .                   .
    # .                   .
    # .                   .
    # .                   .
    # .                   .
    # .                   .
    # .                   .
    # .                   .
    # . . . . . . . . . . .
    line_a = []
    line_b = []
    line_c = []
    line_d = []
    for i in range(-5, 6):
        line_a.append(Coordinate(i, -5))
        line_b.append(Coordinate(5, i))
        line_c.append(Coordinate(-i, 5))
        line_d.append(Coordinate(-5, -i))

    # create a new region
    square_region = Region(region_type=RegionType.rotor)

    # Use the lists of points to create (4*10=)40 lines that form a closed square.
    for line in [line_a, line_b, line_c, line_d]:
        for i in range(len(line) - 1):
            square_region.add_entity(Line(line[i], line[i + 1]))

    # check the original region has 40 lines
    assert square_region.is_closed()
    assert len(square_region.entities) == 40
    for line in square_region.entities:
        assert line.length == 1

    # use the consolidate_lines method to replace the 40 lines (each 1 mm) with 4 lines (each 10 mm)
    square_region.consolidate_lines()

    # check the modified region has 4 lines
    assert square_region.is_closed()
    assert len(square_region.entities) == 4
    for line in square_region.entities:
        assert line.length == 10


def test_consolidate_lines_2():
    # test for consolidating lines when region entity list contains an Arc

    # create 4 lists of 11 colinear points. Together the 44 points form a square with width = 10 mm.
    line_a = []
    line_b = []
    line_c = []
    line_d = []
    for i in range(-5, 6):
        line_a.append(Coordinate(i, -5))
        line_b.append(Coordinate(5, i))
        line_c.append(Coordinate(-i, 5))
        line_d.append(Coordinate(-5, -i))

    # Use lists a-c to create a new region with 3 square sides and add an arc to form the 4th side.
    #    _______
    #   /       |
    #  /        |
    # |         |
    #  \        |
    #   \_______|
    new_region = Region(region_type=RegionType.rotor)
    for line in [line_a, line_b, line_c]:
        for i in range(len(line) - 1):
            new_region.add_entity(Line(line[i], line[i + 1]))
    new_region.add_entity(Arc(line_c[-1], line_a[0], radius=15))

    # check the original region has 31 entities (30 lines, 1 Arc)
    assert new_region.is_closed()
    assert len(new_region.entities) == 31
    for entity in new_region.entities:
        if isinstance(entity, Line):
            assert entity.length == 1
    assert isinstance(new_region.entities[-1], Arc)
    original_arc = deepcopy(new_region.entities[-1])

    # use the consolidate_lines method to replace the 30 lines (each 1 mm) with 4 lines (each 10 mm)
    new_region.consolidate_lines()

    # check the modified region has 3 lines and that the final entity is the same Arc as the
    # original region's last entity.
    assert new_region.is_closed()
    assert len(new_region.entities) == 4
    for entity in new_region.entities:
        if isinstance(entity, Line):
            assert entity.length == 10
    assert new_region.entities[-1] == original_arc


def test_consolidate_lines_3():
    # test for consolidating lines when region entity list contains an Arc and first entity is not
    # at the start of a full line.

    # create 4 lists of 11 colinear points. Together the 44 points form a square with width = 10 mm.
    line_a = []
    line_b = []
    line_c = []
    line_d = []
    for i in range(-5, 6):
        line_a.append(Coordinate(i, -5))
        line_b.append(Coordinate(5, i))
        line_c.append(Coordinate(-i, 5))
        line_d.append(Coordinate(-5, -i))

    # Use lists a-c to create a list of entities with 3 square sides made up of 30 lines and a
    # curved 4th side made up of an arc.
    entities = []
    for line in [line_a, line_b, line_c]:
        for i in range(len(line) - 1):
            entities.append(Line(line[i], line[i + 1]))
    entities.append(Arc(line_c[-1], line_a[0], radius=15))

    # create a new region to add the entities to
    new_region = Region(region_type=RegionType.rotor)

    # add the entities to the new region, but shift the ordering of entities by 5 indices.
    # The first 5 entities will be the 2nd half of the horizontal base of the shape, the last five
    # entities will be the 1st half of the horizontal base of the shape.
    #
    #           15-24
    #          _______
    #         /       |
    #        /        |
    #    25 |         | 5-14
    #        \        |
    #         \___|___|
    #        26-30  0-4
    offset = 5
    for i in range(len(entities) - offset):
        new_region.add_entity(entities[offset + i])
    for i in range(offset):
        new_region.add_entity(entities[i])

    # check the original region has 31 entities (30 lines, 1 Arc)
    assert new_region.is_closed()
    assert len(new_region.entities) == 31
    for entity in new_region.entities:
        if isinstance(entity, Line):
            assert entity.length == 1
        elif isinstance(entity, Arc):
            original_arc = deepcopy(entity)

    # use the consolidate_lines method to replace the 30 lines (each 1 mm) with 4 lines (each 10 mm)
    new_region.consolidate_lines()

    # check the modified region has 3 lines and that the final entity is the same Arc as the
    # original region's last entity.
    assert new_region.is_closed()
    assert len(new_region.entities) == 4
    for entity in new_region.entities:
        if isinstance(entity, Line):
            assert entity.length == 10
        elif isinstance(entity, Arc):
            assert entity == original_arc


def test_round_corner():
    # test for rounding corners of a triangle (3 lines)
    radius = 0.5
    triangle_1 = eq_triangle_h(5, 15, 45)
    triangle_2 = eq_triangle_h(5, 15, 45)
    for index in reversed(range(3)):
        triangle_1.round_corner(triangle_1.entities[index].end, radius)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the rounded triangle are of the expected types
        assert type(triangle_1.entities[2 * i]) == Line
        assert type(triangle_1.entities[2 * i + 1]) == Arc
        # check that the midpoints of the shortened lines are the same as the original lines
        assert isclose(
            triangle_1.entities[2 * i].midpoint.x, triangle_2.entities[i].midpoint.x, abs_tol=1e-6
        )
        assert isclose(
            triangle_1.entities[2 * i].midpoint.y, triangle_2.entities[i].midpoint.y, abs_tol=1e-6
        )

    # check that the original corner coordinates are not on any of the rounded triangle's entities
    corners = []
    for i in range(3):
        corners.append(triangle_2.entities[i].end)
    for entity in triangle_1.entities:
        for i in range(3):
            assert not entity.coordinate_on_entity(corners[i])

    # check exception is raised when a point that is not a corner is specified
    with pytest.raises(Exception):
        triangle_1.round_corner(corners[0], radius)
    with pytest.raises(Exception):
        triangle_1.round_corner(triangle_1.entities[0].midpoint, radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(Exception):
        triangle_2.round_corner(triangle_2.entities[0].end, 100 * radius)

    # check the case when corner internal angle is negative
    corner_1 = Coordinate(0, 0)
    corner_2 = Coordinate(-3, 2)
    corner_3 = Coordinate(-3, 0)
    line_1 = Line(corner_1, corner_3)
    line_2 = Line(corner_3, corner_2)
    line_3 = Line(corner_2, corner_1)
    region = Region(RegionType.stator_air)
    region.add_entity(line_1)
    region.add_entity(line_2)
    region.add_entity(line_3)
    region_rounded = deepcopy(region)
    region_rounded.round_corner(corner_1, 0.1)
    # draw_objects_debug([region, region_rounded])
    assert corner_1 not in region_rounded.points
    assert len(region_rounded.entities) == 4
    assert type(region_rounded.entities[3]) == Arc
    print(region_rounded.entities[3].midpoint.x)
    assert region_rounded.entities[3].midpoint.x < corner_1.x

    # test the case when corner internal angle is more than 180 degrees
    radius = 5
    centre = Coordinate(0, 0)
    start_angle = -15
    end_angle = 195
    coord_1 = Coordinate(*rt_to_xy(radius, start_angle))
    coord_2 = Coordinate(*rt_to_xy(radius, start_angle + 180))
    arc_1 = Arc(coord_1, coord_2, centre=centre)
    arc_2 = Arc(arc_1.end, Coordinate(*rt_to_xy(radius, end_angle)), centre=centre)
    line_1 = Line(arc_2.end, centre)
    line_2 = Line(centre, arc_1.start)
    region = Region(RegionType.stator_air)
    region.add_entity(arc_1)
    region.add_entity(arc_2)
    region.add_entity(line_1)
    region.add_entity(line_2)
    region_rounded = deepcopy(region)
    region_rounded.round_corner(centre, 2)
    # draw_objects_debug([region, region_rounded])
    assert centre not in region_rounded.points
    assert len(region_rounded.entities) == len(region.entities) + 1
    assert type(region_rounded.entities[3]) == Arc
    # print(region_rounded.entities[3].midpoint.y)
    assert region_rounded.entities[3].midpoint.y < centre.y


def test_round_corners():
    # test for rounding corners of a triangle (3 lines)
    corner_radius = 0.5
    triangle_1 = eq_triangle_h(5, 15, 45)
    triangle_2 = eq_triangle_h(5, 15, 45)
    triangle_1.round_corners(triangle_1.points, corner_radius)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the rounded triangle are of the expected types
        assert type(triangle_1.entities[2 * i]) == Line
        assert type(triangle_1.entities[2 * i + 1]) == Arc
        # check that the midpoints of the shortened lines are the same as the original lines
        assert isclose(
            triangle_1.entities[2 * i].midpoint.x, triangle_2.entities[i].midpoint.x, abs_tol=1e-6
        )
        assert isclose(
            triangle_1.entities[2 * i].midpoint.y, triangle_2.entities[i].midpoint.y, abs_tol=1e-6
        )

    # check that the original corner coordinates are not on any of the rounded triangle's entities
    corners = []
    for i in range(3):
        corners.append(triangle_2.entities[i].end)
    for entity in triangle_1.entities:
        for i in range(3):
            assert not entity.coordinate_on_entity(corners[i])

    # check value error is raised when a point that is not a corner is specified
    with pytest.raises(ValueError):
        triangle_1.round_corners(corners, corner_radius)
    with pytest.raises(ValueError):
        triangle_1.round_corners(
            [
                triangle_1.entities[0].midpoint,
                triangle_1.entities[1].midpoint,
                triangle_1.entities[2].midpoint,
            ],
            corner_radius,
        )

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    # * Check this using the maximise = False option
    large_radius = 1.7
    with pytest.raises(ValueError):
        triangle_2.round_corners(triangle_2.points, large_radius, maximise=False)
    # * Check again with a suitably large radius that will not converge
    with pytest.raises(ValueError):
        triangle_2.round_corners(triangle_2.points, 100 * corner_radius)

    # Check that maximise option works
    # When a radius that is too large is given, iterate up to 100 times to find smaller radius
    # Check that the new arc radius after rounding is less than the specified radius
    triangle_2.round_corners(triangle_2.points, large_radius)  # by default, maximise = True
    assert triangle_2.entities[1].radius < large_radius


def test_round_corner_2():
    # test for rounding corner between an arc and a line

    corner_radius = 0.5
    notch_radius = 50
    notch_sweep = 22.5
    notch_depth = 20
    notch_angle = 45
    notch_1 = triangular_notch(notch_radius, notch_sweep, notch_angle, notch_depth)
    notch_2 = triangular_notch(notch_radius, notch_sweep, notch_angle, notch_depth)

    for index in reversed(range(3)):
        notch_1.round_corner(notch_1.entities[index].end, corner_radius)
    # draw_objects([notch_1, notch_2])

    assert notch_1.is_closed()
    # check that the entities making up the rounded notch are of the expected types
    assert type(notch_1.entities[0]) == Line
    assert type(notch_1.entities[1]) == Arc
    assert type(notch_1.entities[2]) == Line
    assert type(notch_1.entities[3]) == Arc
    assert type(notch_1.entities[4]) == Arc
    assert type(notch_1.entities[5]) == Arc
    # check that the gradients of the shortened lines are the same as the original lines
    assert isclose(notch_1.entities[0].gradient, notch_2.entities[0].gradient, abs_tol=1e-6)
    assert isclose(notch_1.entities[2].gradient, notch_2.entities[1].gradient, abs_tol=1e-6)
    # check that the centre of the shortened arc is the same as that of the original arc
    assert isclose(notch_1.entities[4].centre.x, notch_2.entities[2].centre.x, abs_tol=1e-6)
    assert isclose(notch_1.entities[4].centre.y, notch_2.entities[2].centre.y, abs_tol=1e-6)

    # check that the original corner coordinates are not on any of the rounded notch's entities
    corners = []
    for i in range(3):
        corners.append(notch_2.entities[i].end)
    for entity in notch_1.entities:
        for i in range(3):
            assert not entity.coordinate_on_entity(corners[i])

    # check ValueError is raised when a point that is not a corner is specified
    with pytest.raises(ValueError):
        notch_1.round_corner(corners[0], corner_radius)
    with pytest.raises(ValueError):
        notch_1.round_corner(notch_1.entities[0].midpoint, corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    # * Check this using the maximise = False option
    large_radius = 11
    with pytest.raises(ValueError):
        notch_2.round_corner(notch_2.entities[0].end, large_radius, maximise=False)
    # * Check again with a suitably large radius that will not converge
    with pytest.raises(ValueError):
        notch_2.round_corner(notch_2.entities[0].end, 100 * corner_radius)

    # Check that maximise option works
    # When a radius that is too large is given, iterate up to 100 times to find smaller radius
    # Check that the new arc radius after rounding is less than the specified radius
    notch_2.round_corner(notch_2.entities[0].end, large_radius)  # by default, maximise = True
    assert notch_2.entities[1].radius < large_radius


def test_round_corners_2():
    # test for rounding corner between an arc and a line

    corner_radius = 0.5
    notch_radius = 50
    notch_sweep = 22.5
    notch_depth = 20
    notch_angle = 45
    notch_1 = triangular_notch(notch_radius, notch_sweep, notch_angle, notch_depth)
    notch_2 = triangular_notch(notch_radius, notch_sweep, notch_angle, notch_depth)

    notch_1.round_corners(notch_1.points, corner_radius)
    # draw_objects([notch_1, notch_2])

    assert notch_1.is_closed()
    # check that the entities making up the rounded notch are of the expected types
    assert type(notch_1.entities[0]) == Line
    assert type(notch_1.entities[1]) == Arc
    assert type(notch_1.entities[2]) == Line
    assert type(notch_1.entities[3]) == Arc
    assert type(notch_1.entities[4]) == Arc
    assert type(notch_1.entities[5]) == Arc
    # check that the gradients of the shortened lines are the same as the original lines
    assert isclose(notch_1.entities[0].gradient, notch_2.entities[0].gradient, abs_tol=1e-6)
    assert isclose(notch_1.entities[2].gradient, notch_2.entities[1].gradient, abs_tol=1e-6)
    # check that the centre of the shortened arc is the same as that of the original arc
    assert isclose(notch_1.entities[4].centre.x, notch_2.entities[2].centre.x, abs_tol=1e-6)
    assert isclose(notch_1.entities[4].centre.y, notch_2.entities[2].centre.y, abs_tol=1e-6)

    # check that the original corner coordinates are not on any of the rounded notch's entities
    corners = []
    for i in range(3):
        corners.append(notch_2.entities[i].end)
    for entity in notch_1.entities:
        for i in range(3):
            assert not entity.coordinate_on_entity(corners[i])

    # check ValueError is raised when a point that is not a corner is specified
    with pytest.raises(ValueError):
        notch_1.round_corners(corners, corner_radius)
    with pytest.raises(ValueError):
        notch_1.round_corners(
            [
                notch_1.entities[0].midpoint,
                notch_1.entities[1].midpoint,
                notch_1.entities[2].midpoint,
            ],
            corner_radius,
        )

    # check ValueError is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(ValueError):
        notch_2.round_corner(notch_2.entities[0].end, 100 * corner_radius)
    # check ValueError is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    # * Check this using the maximise = False option
    large_radius = 6
    with pytest.raises(ValueError):
        notch_2.round_corners(notch_2.points, large_radius, maximise=False)
    # * Check again with a suitably large radius that will not converge
    with pytest.raises(ValueError):
        notch_2.round_corners(notch_2.points, 100 * corner_radius)

    # Check that maximise option works
    # When a radius that is too large is given, iterate up to 100 times to find smaller radius
    # Check that the new arc radius after rounding is less than the specified radius
    notch_2.round_corners(notch_2.points, large_radius)  # by default, maximise = True
    assert notch_2.entities[1].radius < large_radius


def test_round_corner_3():
    # test for rounding corners between two arcs

    corner_radius = 0.5
    point_1 = Coordinate(0, 15)
    point_2 = Coordinate(0, 0)
    shape_radius = 10
    arc_1 = Arc(point_1, point_2, radius=shape_radius)
    arc_2 = Arc(point_2, point_1, radius=shape_radius)
    shape_1 = Region(RegionType.stator_air)
    shape_1.add_entity(arc_1)
    shape_1.add_entity(arc_2)

    shape_2 = deepcopy(shape_1)

    for index in reversed(range(2)):
        shape_1.round_corner(shape_1.entities[index].end, corner_radius)
    # draw_objects([shape_1, shape_2])

    assert shape_1.is_closed()
    # check that the entities making up the rounded shape are of the expected types
    assert type(shape_1.entities[0]) == Arc
    assert type(shape_1.entities[1]) == Arc
    assert type(shape_1.entities[2]) == Arc
    assert type(shape_1.entities[3]) == Arc
    # check that the centres of the shortened arcs are the same as those of the original arcs
    assert isclose(shape_1.entities[0].centre.x, shape_2.entities[0].centre.x, abs_tol=1e-6)
    assert isclose(shape_1.entities[0].centre.y, shape_2.entities[0].centre.y, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].centre.x, shape_2.entities[1].centre.x, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].centre.y, shape_2.entities[1].centre.y, abs_tol=1e-6)

    # check that the arc radii are correct for each arc
    assert isclose(shape_1.entities[0].radius, shape_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[1].radius, corner_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].radius, shape_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[3].radius, corner_radius, abs_tol=1e-6)

    # check that the original corner coordinates are not on any of the rounded shape's entities
    corners = []
    for i in range(2):
        corners.append(shape_2.entities[i].end)
    for entity in shape_1.entities:
        for i in range(2):
            assert not entity.coordinate_on_entity(corners[i])

    # check ValueError is raised when a point that is not a corner is specified
    with pytest.raises(ValueError):
        shape_1.round_corner(corners[0], corner_radius)
    with pytest.raises(ValueError):
        shape_1.round_corner(shape_1.entities[0].midpoint, corner_radius)

    # check ValueError is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(ValueError):
        shape_2.round_corner(shape_2.entities[0].end, 100 * corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    # * Check this using the maximise = False option
    large_radius = 2
    with pytest.raises(ValueError):
        shape_2.round_corner(shape_2.entities[0].end, large_radius, maximise=False)
    # * Check again with a suitably large radius that will not converge
    with pytest.raises(ValueError):
        shape_2.round_corner(shape_2.entities[0].end, 100 * corner_radius)

    # check that the corners are rounded correctly when the original entity start coordinates are
    # set as the corners, instead of the end coordinates
    for index in reversed(range(2)):
        shape_2.round_corner(shape_2.entities[index].start, corner_radius)

    assert shape_2.entities[0] == shape_1.entities[0]
    assert shape_1.entities[1] == shape_2.entities[1]
    assert shape_1.entities[2] == shape_2.entities[2]
    assert shape_1.entities[3] == shape_2.entities[3]


def test_round_corners_3():
    # test for rounding corners between two arcs

    corner_radius = 0.5
    point_1 = Coordinate(0, 15)
    point_2 = Coordinate(0, 0)
    shape_radius = 10
    arc_1 = Arc(point_1, point_2, radius=shape_radius)
    arc_2 = Arc(point_2, point_1, radius=shape_radius)
    shape_1 = Region(RegionType.stator_air)
    shape_1.add_entity(arc_1)
    shape_1.add_entity(arc_2)

    shape_2 = deepcopy(shape_1)

    shape_1.round_corners(shape_1.points, corner_radius)
    # draw_objects([shape_1, shape_2])

    assert shape_1.is_closed()
    # check that the entities making up the rounded shape are of the expected types
    assert type(shape_1.entities[0]) == Arc
    assert type(shape_1.entities[1]) == Arc
    assert type(shape_1.entities[2]) == Arc
    assert type(shape_1.entities[3]) == Arc
    # check that the centres of the shortened arcs are the same as those of the original arcs
    assert isclose(shape_1.entities[0].centre.x, shape_2.entities[0].centre.x, abs_tol=1e-6)
    assert isclose(shape_1.entities[0].centre.y, shape_2.entities[0].centre.y, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].centre.x, shape_2.entities[1].centre.x, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].centre.y, shape_2.entities[1].centre.y, abs_tol=1e-6)

    # check that the arc radii are correct for each arc
    assert isclose(shape_1.entities[0].radius, shape_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[1].radius, corner_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[2].radius, shape_radius, abs_tol=1e-6)
    assert isclose(shape_1.entities[3].radius, corner_radius, abs_tol=1e-6)

    # check that the original corner coordinates are not on any of the rounded shape's entities
    corners = []
    for i in range(2):
        corners.append(shape_2.entities[i].end)
    for entity in shape_1.entities:
        for i in range(2):
            assert not entity.coordinate_on_entity(corners[i])

    # check ValueError is raised when a point that is not a corner is specified
    with pytest.raises(ValueError):
        shape_1.round_corner(corners[0], corner_radius)
    with pytest.raises(ValueError):
        shape_1.round_corner(shape_1.entities[0].midpoint, corner_radius)

    # check ValueError is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    # * Check this using the maximise = False option
    large_radius = 2
    with pytest.raises(ValueError):
        shape_2.round_corners(shape_2.points, large_radius, maximise=False)
    # * Check again with a suitably large radius that will not converge
    with pytest.raises(ValueError):
        shape_2.round_corners(shape_2.points, 100 * corner_radius)


def test_do_not_round_corner():
    # test for when round_corner method is given a radius of zero
    radius = 0
    triangle_1 = eq_triangle_h(5, 15, 45)
    triangle_2 = eq_triangle_h(5, 15, 45)
    for index in reversed(range(3)):
        triangle_1.round_corner(triangle_1.entities[index].end, radius)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the triangle are unchanged
        assert triangle_1.entities[i] == triangle_2.entities[i]

    # Repeat the test using the maximise = False option
    for index in reversed(range(3)):
        triangle_1.round_corner(triangle_1.entities[index].end, radius, maximise=False)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the triangle are unchanged
        assert triangle_1.entities[i] == triangle_2.entities[i]

    # draw a new triangle where the 3rd side is made up of 2 parallel lines. The region will have a
    # point here, but it is not a corner because the two lines are parallel and have an angle of
    # zero between them.
    triangle_3 = deepcopy(triangle_2)
    new_line_1 = Line(triangle_3.entities[2].start, triangle_3.entities[2].midpoint)
    new_line_2 = Line(triangle_3.entities[2].midpoint, triangle_3.entities[2].end)

    triangle_3.remove_entity(triangle_3.entities[2])
    triangle_3.add_entity(new_line_1)
    triangle_3.add_entity(new_line_2)
    # draw_objects([triangle_3, triangle_3.points[3]])
    radius_2 = 0.5

    triangle_3.round_corner(triangle_3.points[3], radius_2, maximise=False)

    # check that the entities making up the triangle are unchanged
    assert triangle_3.is_closed()
    for i in range(2):
        assert triangle_3.entities[i] == triangle_2.entities[i]
    assert triangle_3.entities[2].start == triangle_2.entities[2].start
    assert triangle_3.entities[2].end == triangle_2.entities[2].midpoint
    assert triangle_3.entities[3].start == triangle_2.entities[2].midpoint
    assert triangle_3.entities[3].end == triangle_2.entities[2].end


def test_do_not_round_corners():
    # test for when round_corners method is given a radius of zero
    radius = 0
    triangle_1 = eq_triangle_h(5, 15, 45)
    triangle_2 = eq_triangle_h(5, 15, 45)
    triangle_1.round_corners(triangle_1.points, radius)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the triangle are unchanged
        assert triangle_1.entities[i] == triangle_2.entities[i]

    # Repeat the test using the maximise = False option
    triangle_1.round_corners(triangle_1.points, radius, maximise=False)
    # draw_objects([triangle_1, triangle_2])

    assert triangle_1.is_closed()
    for i in range(3):
        # check that the entities making up the triangle are unchanged
        assert triangle_1.entities[i] == triangle_2.entities[i]


def test_round_corners_4_extra_points():
    # draw a triangle where the 3rd side is made up of 2 parallel lines. The region will have a
    # point here, but it is not a corner because the two lines are parallel and have an angle of
    # zero between them.
    triangle_1 = eq_triangle_h(5, 15, 45)
    triangle_2 = deepcopy(triangle_1)
    new_line_1 = Line(triangle_2.entities[2].start, triangle_2.entities[2].midpoint)
    new_line_2 = Line(triangle_2.entities[2].midpoint, triangle_2.entities[2].end)

    triangle_2.remove_entity(triangle_2.entities[2])
    triangle_2.add_entity(new_line_1)
    triangle_2.add_entity(new_line_2)
    # draw_objects([triangle_3, triangle_3.points[3]])
    radius_2 = 0.5

    # check that rounding the triangle's points leaves the point between the two parallel lines
    # unchanged
    triangle_2.round_corners(triangle_2.points, radius_2, maximise=False)

    # check that the triangle has been correctly rounded
    assert triangle_2.is_closed()
    # Check that triangle 3 has 4 more entities than triangle 2 (1 extra line + the 3 new arcs)
    assert len(triangle_2.entities) == len(triangle_1.entities) + 4

    # check that the triangle entities are the expected types
    assert isinstance(triangle_2.entities[0], Line)
    assert isinstance(triangle_2.entities[1], Arc)
    assert isinstance(triangle_2.entities[2], Line)
    assert isinstance(triangle_2.entities[3], Arc)
    assert isinstance(triangle_2.entities[4], Line)
    assert isinstance(triangle_2.entities[5], Line)
    assert isinstance(triangle_2.entities[6], Arc)

    # check that the point between the two parallel lines is unchanged.
    assert triangle_2.entities[4].end == triangle_1.entities[2].midpoint
    assert triangle_2.entities[5].start == triangle_1.entities[2].midpoint


def test_extend_entity_region_method():
    # Draw a square and extend its vertical lines to form a rectangle
    square_1 = square(4, 0, 0)

    # extend the lines using the fraction option
    rectangle_1 = deepcopy(square_1)
    rectangle_1.extend_entity(0, fraction=1, extend_from_end=False)
    rectangle_1.extend_entity(2, fraction=1)

    # check that the vertical lines have been doubled in length and the horizontal lines remain the
    # same lengths
    assert rectangle_1.is_closed()
    assert rectangle_1.entities[0].length == square_1.entities[0].length * 2
    assert rectangle_1.entities[2].length == square_1.entities[2].length * 2
    assert rectangle_1.entities[1].length == square_1.entities[1].length
    assert rectangle_1.entities[3].length == square_1.entities[3].length

    # Extend all 4 lines using the absolute distance option. Extend both ends of each line to form
    # a square with width larger than square_1 by the extension value and centred on the same point.
    square_2 = deepcopy(square_1)
    extension = 2.2
    square_2.extend_entity(0, distance=extension / 2, extend_from_end=False)
    square_2.extend_entity(2, distance=extension / 2)
    square_2.extend_entity(0, distance=extension / 2)
    square_2.extend_entity(2, distance=extension / 2, extend_from_end=False)
    square_2.extend_entity(1, distance=extension / 2, extend_from_end=False)
    square_2.extend_entity(3, distance=extension / 2)
    square_2.extend_entity(1, distance=extension / 2)
    square_2.extend_entity(3, distance=extension / 2, extend_from_end=False)

    # check that all lines have been increased in length by the extension value
    assert square_2.is_closed()
    assert isclose(
        square_2.entities[0].length, square_1.entities[0].length + extension, abs_tol=GEOM_TOLERANCE
    )
    assert isclose(
        square_2.entities[2].length, square_1.entities[2].length + extension, abs_tol=GEOM_TOLERANCE
    )
    assert isclose(
        square_2.entities[1].length, square_1.entities[1].length + extension, abs_tol=GEOM_TOLERANCE
    )
    assert isclose(
        square_2.entities[3].length, square_1.entities[3].length + extension, abs_tol=GEOM_TOLERANCE
    )

    # check the factor definition with a <1 factor that shortens two lines to form a parallelogram:
    parallelogram_1 = deepcopy(square_1)
    extension_factor = 0.8

    parallelogram_1.extend_entity(1, factor=extension_factor)
    parallelogram_1.extend_entity(3, factor=extension_factor)
    # check that the parallelogram is closed
    assert parallelogram_1.is_closed()
    # check that the unchanged points are unchanged
    assert parallelogram_1.entities[0].end == square_1.entities[0].end
    assert parallelogram_1.entities[2].end == square_1.entities[2].end
    # check that the horizontal lines are still horizontal
    assert isclose(
        parallelogram_1.entities[1].angle, square_1.entities[1].angle, abs_tol=GEOM_TOLERANCE
    )
    assert isclose(
        parallelogram_1.entities[3].angle, square_1.entities[3].angle, abs_tol=GEOM_TOLERANCE
    )
    # check that the horizontal lines have been shortened by the correct amount
    assert isclose(
        parallelogram_1.entities[1].length,
        square_1.entities[1].length * extension_factor,
        abs_tol=GEOM_TOLERANCE,
    )
    assert isclose(
        parallelogram_1.entities[1].length,
        parallelogram_1.entities[3].length,
        abs_tol=GEOM_TOLERANCE,
    )
    # check that the diagonal (previously vertical) lines are still equal lengths
    assert isclose(
        parallelogram_1.entities[0].length,
        parallelogram_1.entities[2].length,
        abs_tol=GEOM_TOLERANCE,
    )
    # check that the diagonal lines are still parallel
    assert isclose(
        parallelogram_1.entities[0].angle,
        parallelogram_1.entities[2].angle - 180,
        abs_tol=GEOM_TOLERANCE,
    )

    # check that negative factor gives same result
    parallelogram_2 = deepcopy(square_1)
    extension_factor = -0.8

    parallelogram_2.extend_entity(1, factor=extension_factor)
    parallelogram_2.extend_entity(3, factor=extension_factor)

    # check that the parallelogram is closed and that the lines are the same as for the positive
    # factor
    assert parallelogram_2.is_closed()
    for i in range(len(parallelogram_2.entities)):
        assert parallelogram_2.entities[i] == parallelogram_1.entities[i]

    # check that the correct warnings appear when multiple arguments are provided
    parallelogram_3 = deepcopy(square_1)
    extension_distance = 2
    extension_fractional_distance = 0.6
    extension_factor = 1.7

    # test that ValueError is raised when no optional argument is given
    with pytest.raises(ValueError) as e_info:
        parallelogram_3.extend_entity(0)
    assert "provide either a distance, fraction or factor" in str(e_info.value)

    # test that warnings are raised when multiple arguments are given
    # distance and fraction
    with pytest.warns(UserWarning) as record:
        parallelogram_3.extend_entity(
            0, distance=extension_distance, fraction=extension_fractional_distance
        )
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that distance is used
    assert isclose(
        parallelogram_3.entities[0].length,
        square_1.entities[0].length + extension_distance,
        abs_tol=GEOM_TOLERANCE,
    )

    # distance and factor
    with pytest.warns(UserWarning) as record:
        parallelogram_3.extend_entity(2, distance=extension_distance, factor=extension_factor)
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that distance is used
    assert isclose(
        parallelogram_3.entities[2].length,
        square_1.entities[2].length + extension_distance,
        abs_tol=GEOM_TOLERANCE,
    )

    # fraction and factor
    with pytest.warns(UserWarning) as record:
        parallelogram_3.extend_entity(
            0, fraction=extension_fractional_distance, factor=extension_factor
        )
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that fraction is used
    assert isclose(
        parallelogram_3.entities[0].length,
        (square_1.entities[0].length + extension_distance) * (1 + extension_fractional_distance),
        abs_tol=GEOM_TOLERANCE,
    )

    # test invalid arguments
    # Check ValueError is raised when asked to shorten an entity by more than its original length
    # distance definition
    square_3 = deepcopy(square_1)  # square of width = 4 mm
    extension = -5
    with pytest.raises(ValueError) as e_info:
        square_3.extend_entity(0, distance=extension)
    assert "Invalid distance provided" in str(e_info.value)
    # fraction definition
    extension_fractional_distance = -1.5
    with pytest.raises(ValueError) as e_info:
        square_3.extend_entity(0, fraction=extension_fractional_distance)
    assert "Invalid fraction provided" in str(e_info.value)
    # check TypeError raised when invalid argument is provided for extend_from_end
    with pytest.raises(TypeError) as e_info:
        square_3.extend_entity(0, distance=1, extend_from_end="no")
    assert "'extend_from_end' must be a boolean" in str(e_info.value)


def test_extend_entity_method():
    # test extending a line using the distance definition
    line_1 = Line(Coordinate(0, 0), Coordinate(5, 0))
    line_2 = deepcopy(line_1)

    extension = 2
    line_2.extend(distance=extension)

    # check that the line has been extended by the correct amount and the end has been moved to the
    # expected coordinate
    assert isclose(line_2.length, line_1.length + extension, abs_tol=GEOM_TOLERANCE)
    assert line_2.end == Coordinate(line_1.end.x + extension, line_1.end.y)
    # check that the start of the line is unchanged
    assert line_2.start == line_1.start

    # test extending a line using the fraction definition
    line_3 = deepcopy(line_1)
    extension_fractional_distance = 0.5
    line_3.extend(fraction=extension_fractional_distance, extend_from_end=False)

    # check that the line has been extended by the correct amount and that the start point has been
    # moved as expected
    assert isclose(
        line_3.length, line_1.length * (1 + extension_fractional_distance), abs_tol=GEOM_TOLERANCE
    )
    assert line_3.start == Coordinate(
        line_1.start.x - line_1.length * extension_fractional_distance, line_1.start.y
    )
    # check that the end point is unchanged
    assert line_3.end == line_1.end

    # test extending an arc with the distance definition
    arc_1 = Arc(Coordinate(-4, 0), Coordinate(4, 0), radius=-8)
    arc_2 = deepcopy(arc_1)
    extension = 0.75

    arc_2.extend(distance=extension)
    # check that the arc has been extended by the correct amount
    assert isclose(arc_2.length, arc_1.length + extension, abs_tol=GEOM_TOLERANCE)
    # check that the start point is unchanged
    assert arc_2.start == arc_1.start
    # check that the extended arc still has the same radius and centre
    assert isclose(arc_2.radius, arc_1.radius, abs_tol=GEOM_TOLERANCE)
    assert arc_2.centre == arc_1.centre

    # test extending an arc with the fraction definition
    arc_3 = deepcopy(arc_1)
    extension_fractional_distance = 2
    arc_3.extend(fraction=extension_fractional_distance, extend_from_end=False)

    # check that the arc has been extended by the correct amount
    assert isclose(
        arc_3.length, arc_1.length * (1 + extension_fractional_distance), abs_tol=GEOM_TOLERANCE
    )
    # check that the end point is unchanged
    assert arc_3.end == arc_1.end
    # check that the extended arc still has the same radius and centre
    assert isclose(arc_3.radius, arc_1.radius, abs_tol=GEOM_TOLERANCE)
    assert arc_3.centre == arc_1.centre

    # test extending an arc with the factor definition
    arc_4 = deepcopy(arc_1)
    extension_factor = 1.5
    arc_4.extend(factor=extension_factor)

    # check that the arc has been extended by the correct amount
    assert isclose(arc_4.length, arc_1.length * extension_factor, abs_tol=GEOM_TOLERANCE)
    # check that the start point is unchanged
    assert arc_4.start == arc_1.start
    # check that the extended arc still has the same radius and centre
    assert isclose(arc_4.radius, arc_1.radius, abs_tol=GEOM_TOLERANCE)
    assert arc_4.centre == arc_1.centre

    # test that extending an arc with a negative factor gives the same result
    arc_5 = deepcopy(arc_1)
    extension_factor = -1.5
    arc_5.extend(factor=extension_factor)
    assert arc_5 == arc_4

    # test that ValueError is raised when no optional argument is given
    line_4 = deepcopy(line_1)
    with pytest.raises(ValueError) as e_info:
        line_4.extend()
    assert "provide either a distance, fraction or factor" in str(e_info.value)

    # check that the correct warnings appear when multiple arguments are provided
    extension_distance = 2
    extension_fractional_distance = 0.6
    extension_factor = 1.7
    # test that warnings are raised when multiple arguments are given
    # distance and fraction
    with pytest.warns(UserWarning) as record:
        line_4.extend(distance=extension_distance, fraction=extension_fractional_distance)
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that distance is used
    assert isclose(line_4.length, line_1.length + extension_distance, abs_tol=GEOM_TOLERANCE)

    # distance and factor
    with pytest.warns(UserWarning) as record:
        line_4.extend(distance=extension_distance, factor=extension_factor)
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that distance is used
    assert isclose(line_4.length, line_1.length + 2 * extension_distance, abs_tol=GEOM_TOLERANCE)

    line_5 = deepcopy(line_1)
    # fraction and factor
    with pytest.warns(UserWarning) as record:
        line_5.extend(fraction=extension_fractional_distance, factor=extension_factor)
    assert "More than one optional argument provided" in record[0].message.args[0]
    # check that distance is used
    assert isclose(
        line_5.length, line_1.length * (1 + extension_fractional_distance), abs_tol=GEOM_TOLERANCE
    )

    # test invalid arguments
    # Check ValueError is raised when asked to shorten an entity by more than its original length
    # distance definition
    arc_5 = deepcopy(arc_1)  # arc length 8.4 mm
    extension = -9
    with pytest.raises(ValueError) as e_info:
        arc_5.extend(distance=extension)
    assert "Invalid distance provided" in str(e_info.value)
    # fraction definition
    extension_fractional_distance = -1.5
    with pytest.raises(ValueError) as e_info:
        arc_5.extend(fraction=extension_fractional_distance)
    assert "Invalid fraction provided" in str(e_info.value)
    # check TypeError raised when invalid argument is provided for extend_from_end
    with pytest.raises(TypeError) as e_info:
        arc_5.extend(distance=1, extend_from_end=None)
    assert "'extend_from_end' must be a boolean" in str(e_info.value)


def test_limit_arc_chord():
    # Draw a square, round its corners, and then limit the radii,
    # and check we have the right number of entities
    square_1 = square(20, 0, 0)
    square_2 = square(20, 0, 0)
    square_3 = square(20, 0, 0)
    assert len(square_1.entities) == 4
    assert len(square_2.entities) == 4
    assert len(square_3.entities) == 4
    corner_radius = 5
    square_1.round_corners(square_1.points, corner_radius)
    square_2.round_corners(square_2.points, corner_radius)
    square_3.round_corners(square_3.points, corner_radius)
    assert len(square_1.entities) == 8
    assert len(square_2.entities) == 8
    assert len(square_3.entities) == 8

    # This should split the corners into three
    chord_tolerance = 0.1
    square_1.limit_arc_chord(chord_tolerance)
    assert len(square_1.entities) == 16

    # This should not split the corners
    chord_tolerance = 8
    square_2.limit_arc_chord(chord_tolerance)
    assert len(square_2.entities) == 8

    # This should not split the corners (invalid input)
    chord_tolerance = 0
    square_3.limit_arc_chord(chord_tolerance)
    assert len(square_3.entities) == 8


def test_subtract_regions(mc):
    """Test subtract rectangle from square to create cut out in square as shown below"""
    #   Before         After
    # |--------|    |--------|
    # |  |--|  |    |  |--|  |
    # |  |  |  | -> |  |  |  |
    # |--|--|--|    |--|  |--|
    #    |  |
    #    |--|
    region_a = geometry.Region(RegionType.stator_air)
    region_b = geometry.Region(RegionType.stator_air)
    expected_region = geometry.Region(RegionType.stator_air)

    points_a = [
        geometry.Coordinate(-1, -1),
        geometry.Coordinate(-1, 1),
        geometry.Coordinate(1, 1),
        geometry.Coordinate(1, -1),
    ]
    # create and add line entities to region from their respective points
    region_a.entities += create_lines_from_points(points_a)

    points_b = [
        geometry.Coordinate(-0.5, -2),
        geometry.Coordinate(-0.5, -0.5),
        geometry.Coordinate(0.5, -0.5),
        geometry.Coordinate(0.5, -2),
    ]
    # create and add line entities to region from their respective points
    region_b.entities += create_lines_from_points(points_b)

    points_expected = [
        geometry.Coordinate(-1, 1),
        geometry.Coordinate(-1, -1),
        geometry.Coordinate(-0.5, -1),
        geometry.Coordinate(-0.5, -0.5),
        geometry.Coordinate(0.5, -0.5),
        geometry.Coordinate(0.5, -1),
        geometry.Coordinate(1, -1),
        geometry.Coordinate(1, 1),
    ]
    # create and add line entities to region from their respective points
    expected_region.entities += create_lines_from_points(points_expected)

    subtracted_regions = mc.subtract_region(region_a, region_b)

    assert len(subtracted_regions) == 1
    assert subtracted_regions[0] == expected_region


def test_subtract_region_1(mc):
    """Test subtracting long rectangle from square to generate two rectangles as shown below."""
    #      Before           After
    #      |---|
    #      |   |
    #   |--|---|--|      |--|   |--|
    #   |  |   |  |  ->  |  |   |  |
    #   |  |   |  |      |  |   |  |
    #   |--|---|--|      |--|   |--|
    #      |   |
    #      |---|
    #
    square = create_square()
    rectangle = geometry.Region(RegionType.stator_air)
    expected_region_1 = geometry.Region(RegionType.stator_air)
    expected_region_2 = geometry.Region(RegionType.stator_air)

    points_rectangle = [
        geometry.Coordinate(0.5, -1),
        geometry.Coordinate(1.5, -1),
        geometry.Coordinate(1.5, 3),
        geometry.Coordinate(0.5, 3),
    ]
    # create and add line entities to region from their respective points
    rectangle.entities += create_lines_from_points(points_rectangle)

    points_expected_1 = [
        geometry.Coordinate(0, 2),
        geometry.Coordinate(0, 0),
        geometry.Coordinate(0.5, 0),
        geometry.Coordinate(0.5, 2),
    ]
    # create and add line entities to region from their respective points
    expected_region_1.entities += create_lines_from_points(points_expected_1)

    points_expected_2 = [
        geometry.Coordinate(1.5, 2),
        geometry.Coordinate(1.5, 0),
        geometry.Coordinate(2, 0),
        geometry.Coordinate(2, 2),
    ]
    # create and add line entities to region from their respective points
    expected_region_2.entities += create_lines_from_points(points_expected_2)
    square.motorcad_instance = mc
    regions = square.subtract(rectangle)

    assert square == expected_region_1
    assert len(regions) == 1
    assert regions[0] == expected_region_2


def test_subtract_region_2(mc):
    """Test subtracting triangle from square. No vertices from either region are within
    the other region."""
    #     Before             After
    #      \------|
    # |-----\-|   |         |-----\
    # |      \|   |         |      \
    # |       \   |  ->     |       \
    # |-------|\  |         |--------|
    #           \ |
    #            \|
    #
    square = create_square()
    triangle = create_triangle()
    expected_region = geometry.Region(RegionType.stator_air)

    points = [
        geometry.Coordinate(0, 2),
        geometry.Coordinate(0, 0),
        geometry.Coordinate(2, 0),
        geometry.Coordinate(2, 1.2),
        geometry.Coordinate(1.2, 2),
    ]
    # create and add line entities to region from their respective points
    expected_region.entities += create_lines_from_points(points)
    square.motorcad_instance = mc
    square.subtract(triangle)

    assert square == expected_region


def test_subtract_region_3(mc):
    """Test subtract rectangle from square to create cut out in square as shown below"""
    #   Before         After
    # |--------|    |--------|
    # |   |----|    |   |----|
    # |   |    | -> |   |
    # |---|----|    |---|
    #
    square = create_square()
    inner_square = geometry.Region(RegionType.stator_air)
    expected_region = geometry.Region(RegionType.stator_air)

    points = [
        geometry.Coordinate(2, 0),
        geometry.Coordinate(2, 1.5),
        geometry.Coordinate(0.5, 1.5),
        geometry.Coordinate(0.5, 0),
    ]
    # create and add line entities to region from their respective points
    inner_square.entities += create_lines_from_points(points)

    expected_points = [
        geometry.Coordinate(0.5, 0),
        geometry.Coordinate(0.5, 1.5),
        geometry.Coordinate(2, 1.5),
        geometry.Coordinate(2, 2),
        geometry.Coordinate(0, 2),
        geometry.Coordinate(0, 0),
    ]
    # create and add line entities to region from their respective points
    expected_region.entities += create_lines_from_points(expected_points)

    subtracted_regions = mc.subtract_region(square, inner_square)

    assert len(subtracted_regions) == 1
    assert subtracted_regions[0] == expected_region


def test_subtract_region_4(mc):
    """Test subtract rectangle from rectangle, where one rectangle is a sub region of the other."""
    #   Before         After
    # |--------|    |--------|
    # | |----| |    | |----| |
    # | |    | | -> | |    | |
    # | |----| |    | |----| |
    # |--------|    |--------|
    #
    square = create_square()
    inner_square = geometry.Region(RegionType.stator_air)
    inner_square.name = "Subtraction Region"
    expected_region = deepcopy(square)

    points = [
        geometry.Coordinate(0.5, 0.5),
        geometry.Coordinate(0.5, 1.5),
        geometry.Coordinate(1.5, 1.5),
        geometry.Coordinate(0.5, 1.5),
    ]
    # create and add line entities to region from their respective points
    inner_square.entities += create_lines_from_points(points)

    subtracted_regions = mc.subtract_region(square, inner_square)

    assert len(subtracted_regions) == 1
    assert subtracted_regions[0] == expected_region

    assert len(subtracted_regions[0].child_names) == 1
    assert subtracted_regions[0].child_names[0] == inner_square.name


def test_region_mirror():
    square = create_square()
    square.name = "square"
    mirror_line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(5, 0))

    expected_region = deepcopy(square)
    expected_region.entities.clear()

    points = [
        geometry.Coordinate(0, 0),
        geometry.Coordinate(2, 0),
        geometry.Coordinate(2, -2),
        geometry.Coordinate(0, -2),
    ]
    expected_region.entities += create_lines_from_points(points)
    assert square.mirror(mirror_line, unique_name=False) == expected_region

    expected_region.name = expected_region.name + "_mirrored"
    assert square.mirror(mirror_line, unique_name=True) == expected_region


def test_region_mirror_1():
    square = create_square()
    mirror_line = geometry.Arc(
        geometry.Coordinate(0, 0), geometry.Coordinate(5, 0), geometry.Coordinate(2.5, 0), 2.5
    )

    with pytest.raises(Exception) as e_info:
        square.mirror(mirror_line, unique_name=False)  # noqa

    assert "Region can only be mirrored about Line()" in str(e_info.value)


def test_entity_mirror():
    #
    #   ---------- entity
    #  ------------------------------------------ mirror line
    #   ---------- mirrored
    #
    entity = geometry.Entity(geometry.Coordinate(0, 1), geometry.Coordinate(5, 1))
    mirror_line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(0, 10))
    expected_entity = geometry.Entity(geometry.Coordinate(0, 1), geometry.Coordinate(-5, 1))

    assert entity.mirror(mirror_line) == expected_entity


def test_entity_mirror_1():
    entity = geometry.Entity(geometry.Coordinate(0, 1), geometry.Coordinate(5, 1))
    mirror_line = geometry.Arc(
        geometry.Coordinate(0, 0), geometry.Coordinate(5, 0), geometry.Coordinate(2.5, 0), 2.5
    )

    with pytest.raises(Exception) as e_info:
        entity.mirror(mirror_line)  # noqa

    assert "Entity can only be mirrored about Line()" in str(e_info.value)


def test_line_mirror():
    #
    #        mirror line
    #           \
    #      |     \     --------- line
    #      |      \
    #      |       \
    #      |        \
    #   mirrored
    #
    line = geometry.Line(geometry.Coordinate(0, 5), geometry.Coordinate(5, 5))
    mirror_line = geometry.Line(geometry.Coordinate(-10, 10), geometry.Coordinate(10, -10))
    expected_line = geometry.Line(geometry.Coordinate(-5, 0), geometry.Coordinate(-5, -5))

    assert line.mirror(mirror_line) == expected_line


def test_line_mirror_1():
    entity = geometry.Line(geometry.Coordinate(0, 1), geometry.Coordinate(5, 1))
    mirror_line = geometry.Arc(
        geometry.Coordinate(0, 0), geometry.Coordinate(5, 0), geometry.Coordinate(2.5, 0), 2.5
    )

    with pytest.raises(Exception) as e_info:
        entity.mirror(mirror_line)  # noqa

    assert "Line can only be mirrored about Line()" in str(e_info.value)


def test_line_is_vertical():
    line = geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5, 10))
    assert line.is_vertical == True

    line = geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5.1, 10))
    assert line.is_vertical == False


def test_line_gradient():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(10, 10))
    assert line.gradient == 1

    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(10, -10))
    assert line.gradient == -1

    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(20, 10))
    assert line.gradient == 0.5

    line = geometry.Line(geometry.Coordinate(-5, 0), geometry.Coordinate(10, -10))
    assert line.gradient == -2 / 3

    line = geometry.Line(geometry.Coordinate(20, 0), geometry.Coordinate(20, 10))
    assert line.gradient == float(inf)


def test_line_y_intercept():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(10, 10))
    assert line.y_intercept == 0

    line = geometry.Line(geometry.Coordinate(-5, 0), geometry.Coordinate(10, -10))
    assert line.y_intercept == -10 / 3

    line = geometry.Line(geometry.Coordinate(20, 0), geometry.Coordinate(20, 10))
    with pytest.raises(Exception) as e_info:
        y_intercept = line.y_intercept

    assert "Vertical line, no y interception" in str(e_info.value)


def test_arc_mirror():
    #
    #   ---------- arc
    #  ------------------------------------------ mirror line
    #   ---------- mirrored
    #
    arc = geometry.Arc(
        geometry.Coordinate(0, 0), geometry.Coordinate(5, 0), geometry.Coordinate(2.5, 0), -2.5
    )
    mirror_line = geometry.Line(geometry.Coordinate(0, -1), geometry.Coordinate(10, -1))
    expected_arc = geometry.Arc(
        geometry.Coordinate(0, -2), geometry.Coordinate(5, -2), geometry.Coordinate(2.5, -2), 2.5
    )

    assert arc.mirror(mirror_line) == expected_arc


def test_arc_mirror_1():
    arc = geometry.Arc(
        geometry.Coordinate(0, 0), geometry.Coordinate(5, 0), geometry.Coordinate(2.5, 0), -2.5
    )
    mirror_line = geometry.Entity(geometry.Coordinate(0, -1), geometry.Coordinate(10, -1))

    with pytest.raises(Exception) as e_info:
        arc.mirror(mirror_line)  # noqa

    assert "Arc can only be mirrored about Line()" in str(e_info.value)


def test_coordinate_mirror():
    #
    #       mirrored coordinate       mirror line         coordinate
    #                                      |
    #              .                       |                   .
    #                                      |
    #
    coord = geometry.Coordinate(5, 5)
    mirror_line = geometry.Line(geometry.Coordinate(-2, -2), geometry.Coordinate(-2, 10))
    expected_coord = geometry.Coordinate(-9, 5)

    assert coord.mirror(mirror_line) == expected_coord


def test_coordinate_mirror_1():
    coord = geometry.Coordinate(5, 5)
    mirror_line = geometry.Entity(geometry.Coordinate(-2, -2), geometry.Coordinate(-2, 10))

    with pytest.raises(Exception) as e_info:
        coord.mirror(mirror_line)  # noqa

    assert "Coordinate can only be mirrored about Line" in str(e_info.value)


def test_coordinate_rotation():
    centre = Coordinate(0, 0)

    c1 = Coordinate(10, 0)
    c1.rotate(centre, 90)
    assert c1 == Coordinate(0, 10)

    c1 = Coordinate(10, 0)
    c1.rotate(centre, -90)
    assert c1 == Coordinate(0, -10)

    centre = Coordinate(9, 0)
    c1 = Coordinate(10, 0)
    c1.rotate(centre, 90)
    assert c1 == Coordinate(9, 1)


def test_line_rotation():
    centre = Coordinate(0, 0)

    c1 = Coordinate(0, 0)
    c2 = Coordinate(10, 0)

    l1 = Line(c1, c2)
    l1.rotate(centre, 90)
    assert l1 == Line(Coordinate(0, 0), Coordinate(0, 10))

    l1 = Line(c1, c2)
    old_mid = l1.midpoint
    l1.rotate(l1.midpoint, 90)
    assert l1 == Line(Coordinate(5, -5), Coordinate(5, 5))
    assert l1.midpoint == old_mid


def test_arc_rotation():
    centre = Coordinate(0, 0)
    radius = 10
    c1 = Coordinate(radius, 0)
    c2 = Coordinate(0, 10)

    a1 = Arc(c1, c2, centre, radius)

    c3 = Coordinate(-radius, 0)
    a2 = Arc(c2, c3, centre, radius)

    a1.rotate(centre, 90)

    assert a1 == a2


def test_get_line_intersection():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(10, 10)
    l1 = Line(c1, c2)

    c3 = Coordinate(0, 10)
    c4 = Coordinate(10, 0)
    l2 = Line(c3, c4)

    assert l1.get_line_intersection(l2) == Coordinate(5, 5)

    c1 = Coordinate(0, 0)
    c2 = Coordinate(10, 0)
    l1 = Line(c1, c2)

    c3 = Coordinate(0, 5)
    c4 = Coordinate(10, 5)
    l2 = Line(c3, c4)

    assert l1.get_line_intersection(l2) is None


def test_get_intersection():
    arc_1 = Arc(Coordinate(0, 0), Coordinate(5, 5), radius=15)
    arc_2 = Arc(Coordinate(0, 6), Coordinate(5, 1), radius=-21)

    coordinate = Coordinate(0, 0)

    # test get_intersection

    # 2 arcs, 1 intersection
    intersection_1_2 = arc_1.get_intersection(arc_2)
    intersection_2_1 = arc_2.get_intersection(arc_1)
    assert len(intersection_1_2) == 1
    assert len(intersection_2_1) == 1
    assert intersection_1_2[0] == intersection_2_1[0]
    assert arc_1.coordinate_on_entity(intersection_1_2[0])
    assert arc_2.coordinate_on_entity(intersection_1_2[0])
    # draw_objects_debug([arc_1, arc_2, intersection_1_2[0]])

    # 2 arcs, 2 intersections
    arc_3 = Arc(Coordinate(1, 0), Coordinate(5, 4), radius=-5)
    intersection_1_3 = arc_1.get_arc_intersection(arc_3)
    intersection_3_1 = arc_3.get_arc_intersection(arc_1)
    assert len(intersection_1_3) == 2
    assert len(intersection_3_1) == 2
    for point in intersection_1_3:
        assert arc_1.coordinate_on_entity(point)
        assert arc_3.coordinate_on_entity(point)
        assert point in intersection_3_1
    # draw_objects_debug([arc_1, arc_3, intersection_1_3[0], intersection_1_3[1]])

    # 2 arcs, 0 intersection
    arc_4 = Arc(Coordinate(0, -1), Coordinate(0, 1), radius=1)
    arc_5 = Arc(Coordinate(0, -0.5), Coordinate(0, 0.5), radius=0.5)
    intersection_4_5 = arc_4.get_intersection(arc_5)
    intersection_5_4 = arc_5.get_intersection(arc_4)
    assert intersection_4_5 is None
    assert intersection_5_4 is None
    # draw_objects_debug([arc_4, arc_5])

    # 2 arcs, same radius, 0 intersection
    intersection_4_4 = arc_4.get_intersection(arc_4)
    assert intersection_4_4 is None
    # draw_objects_debug([arc_4])

    # 1 arc, 1 line, 1 intersection
    line_4 = Line(Coordinate(0, 6), Coordinate(5, 1))
    intersection_1_4 = arc_1.get_intersection(line_4)
    intersection_4_1 = line_4.get_intersection(arc_1)
    intersection_4_1_alt = line_4.get_arc_intersection(arc_1)
    assert len(intersection_1_4) == 1
    assert len(intersection_4_1) == 1
    assert len(intersection_4_1_alt) >= len(intersection_4_1)
    assert intersection_1_4[0] == intersection_4_1[0]
    assert intersection_4_1[0] in intersection_4_1_alt
    assert arc_1.coordinate_on_entity(intersection_1_4[0])
    assert line_4.coordinate_on_entity(intersection_1_4[0])
    # draw_objects_debug([arc_1, line_4, intersection_1_4[0]])

    # 1 arc, 1 line, 2 intersections
    line_5 = Line(Coordinate(1, 0), Coordinate(5, 4))
    arc_6 = Arc(Coordinate(0, 0), Coordinate(5, 5), radius=8)
    intersection_5_6 = line_5.get_intersection(arc_6)
    intersection_6_5 = arc_6.get_intersection(line_5)
    assert len(intersection_5_6) == 2
    assert len(intersection_6_5) == 2
    for point in intersection_5_6:
        assert line_5.coordinate_on_entity(point)
        assert arc_6.coordinate_on_entity(point)
        assert point in intersection_6_5
    # draw_objects_debug([arc_6, line_5, intersection_5_6[0], intersection_5_6[1]])

    # 1 arc, 1 line, 1 intersection (vertical tangent line)
    arc_7 = Arc(Coordinate(0, 0), Coordinate(0, 2), radius=1)
    line_6 = Line(Coordinate(1, 2), Coordinate(1, 0))
    intersection_7_6 = arc_7.get_intersection(line_6)
    intersection_6_7 = line_6.get_intersection(arc_7)
    assert len(intersection_7_6) == 1
    assert len(intersection_6_7) == 1
    assert intersection_7_6[0] == intersection_6_7[0]
    assert arc_7.coordinate_on_entity(intersection_7_6[0])
    assert line_6.coordinate_on_entity(intersection_7_6[0])
    # draw_objects_debug([arc_7, line_6, intersection_7_6[0]])

    # 1 arc, 1 line, 2 intersections (vertical line)
    line_7 = Line(Coordinate(0.5, 2), Coordinate(0.5, 0))
    intersection_7a_7l = arc_7.get_intersection(line_7)
    intersection_7l_7a = line_7.get_intersection(arc_7)
    assert len(intersection_7a_7l) == 2
    assert len(intersection_7l_7a) == 2
    assert intersection_7a_7l[0] == intersection_7l_7a[0]
    assert arc_7.coordinate_on_entity(intersection_7l_7a[0])
    assert line_7.coordinate_on_entity(intersection_7l_7a[0])
    # draw_objects_debug([arc_7, line_7, intersection_7a_7l[0], intersection_7a_7l[1]])

    # 1 arc, 1 line, 1 intersection (horizontal tangent line)
    line_8 = Line(Coordinate(-1, 2), Coordinate(1, 2))
    intersection_7_8 = arc_7.get_intersection(line_8)
    intersection_8_7 = line_8.get_intersection(arc_7)
    assert len(intersection_7_8) == 1
    assert len(intersection_8_7) == 1
    assert intersection_7_8[0] == intersection_8_7[0]
    assert arc_7.coordinate_on_entity(intersection_7_8[0])
    assert line_8.coordinate_on_entity(intersection_7_8[0])
    # draw_objects_debug([arc_7, line_8, intersection_7_8[0]])

    # 2 lines, 1 intersection
    intersection_4_5 = line_4.get_intersection(line_5)
    intersection_5_4 = line_5.get_intersection(line_4)
    assert len(intersection_4_5) == 1
    assert len(intersection_5_4) == 1
    assert intersection_4_5[0] == intersection_5_4[0]
    assert line_4.coordinate_on_entity(intersection_4_5[0])
    assert line_5.coordinate_on_entity(intersection_4_5[0])
    # draw_objects_debug([line_4, line_5, intersection_4_5[0]])

    # Arc intersection with point, not valid, should raise exception
    with pytest.raises(Exception) as e_info:
        arc_1.get_intersection(coordinate)  # noqa

    # Line intersection with point, not valid, should raise exception
    with pytest.raises(Exception) as e_info:
        line_1.get_intersection(coordinate)  # noqa


def test_arc_from_coordinates():
    c1 = Coordinate(1, 0)
    c2 = Coordinate(sin(pi / 4), sin(pi / 4))
    c3 = Coordinate(0, 1)

    a1 = Arc.from_coordinates(c1, c2, c3)
    assert a1 == Arc(c1, c3, Coordinate(0, 0), 1)

    c1 = Coordinate(7, 11)
    c2 = Coordinate(20, 10)
    c3 = Coordinate(24, 7)

    a1 = Arc.from_coordinates(c1, c2, c3)
    assert a1 == Arc(
        Coordinate(7, 11),
        Coordinate(24, 7),
        Coordinate(12.357142857142858, -4.357142857142857),
        -16.264710766765287,
    )


def test_coordinate_from_polar_coords():
    c1 = Coordinate.from_polar_coords(2 ** (1 / 2), 45)
    assert c1 == Coordinate(1, 1)


def test_line_angle():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(1, 1)
    l1 = Line(c1, c2)
    assert l1.angle == 45

    # negative
    c1 = Coordinate(0, 0)
    c2 = Coordinate(-1, -1)
    l1 = Line(c1, c2)
    assert l1.angle == -135

    # vertical
    c1 = Coordinate(0, 0)
    c2 = Coordinate(0, 1)
    l1 = Line(c1, c2)
    assert l1.angle == 90

    # vertical
    c1 = Coordinate(0, 0)
    c2 = Coordinate(1, 0)
    l1 = Line(c1, c2)
    assert l1.angle == 0


def test__orientation():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(1, 1)
    c3 = Coordinate(2, 2)
    assert _orientation_of_three_points(c1, c2, c3) == _Orientation.collinear

    c1 = Coordinate(0, 3)
    c2 = Coordinate(4, 2)
    c3 = Coordinate(3, 1)
    assert _orientation_of_three_points(c1, c2, c3) == _Orientation.clockwise

    c1 = Coordinate(0, 3)
    c2 = Coordinate(1, 2)
    c3 = Coordinate(9, 5)
    assert _orientation_of_three_points(c1, c2, c3) == _Orientation.anticlockwise


def test_line_is_horizontal():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(5, 0)
    l1 = Line(c1, c2)
    assert l1.is_horizontal

    c1 = Coordinate(0, 0)
    c2 = Coordinate(5, 1)
    l1 = Line(c1, c2)
    assert not l1.is_horizontal


def test_line_overrides():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(5, 0)
    l1 = Line(c1, c2)
    assert abs(l1) == 5


def test_region_find_entity_from_coordinates():
    c1 = create_square()

    assert c1.find_entity_from_coordinates(Coordinate(99, 99), Coordinate(99, 99)) is None

    assert (
        c1.find_entity_from_coordinates(c1.entities[0].start, c1.entities[0].end) == c1.entities[0]
    )


def test_reset_geometry(mc):
    stator = mc.get_region("stator")

    # When the new regions go out of scope they close Motor-CAD
    # Do we need to fix this?
    stator.motorcad_instance = None

    stator_copy = deepcopy(stator)
    stator_edited = deepcopy(stator)

    stator_edited.edit_point(stator_edited.points[1], stator_edited.points[1] + Coordinate(5, 5))
    assert stator_edited.entities != stator_copy.entities

    mc.set_region(stator_edited)
    stator = mc.get_region("stator")
    assert stator.entities != stator_copy.entities

    mc.reset_adaptive_geometry()
    stator = mc.get_region("stator")
    assert stator.entities == stator_copy.entities

    save_default_instance = DEFAULT_INSTANCE
    set_default_instance(mc.connection._port)

    mc.set_region(stator_edited)
    stator = mc.get_region("stator")
    assert stator.entities != stator_copy.entities

    mc.reset_adaptive_geometry()
    stator = mc.get_region("stator")
    assert stator.entities != stator_copy.entities

    set_default_instance(save_default_instance)


def test_translation_coord():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(2, 2)
    c1.translate(2, 2)
    assert c1 == c2

    c1 = Coordinate(1, 2)
    c2 = Coordinate(-1.5, 1)
    c1.translate(-2.5, -1)
    assert c1 == c2


def test_arc_new_init():
    a1 = Arc(Coordinate(10, 0), Coordinate(0, 10), radius=10)
    assert a1.centre == Coordinate(0, 0)

    with pytest.raises(Exception):
        _ = Arc(Coordinate(10, 0), Coordinate(0, 10), radius=6)

    a1 = Arc(Coordinate(10, 0), Coordinate(0, 10), centre=Coordinate(0, 0))
    assert a1.radius == 10

    a2 = Arc(Coordinate(0, 10), Coordinate(10, 0), centre=Coordinate(10, 10))
    assert a2.radius == 10

    a3 = Arc(Coordinate(0, 10), Coordinate(10, 0), centre=Coordinate(0, 0))
    assert a3.radius == -10
    assert a3.centre == Coordinate(0, 0)

    # Check tolerances
    with pytest.raises(Exception):
        _ = Arc(Coordinate(0, 0), Coordinate(10, 0), radius=4)

    original_radius = -5 + (GEOM_TOLERANCE * 0.95)
    a5 = Arc(Coordinate(0, 0), Coordinate(10, 0), radius=original_radius)
    # Arc creation will bump radius to a value that is physically possible since within tolerance
    # check sign is preserved
    assert (a5.radius - original_radius) < GEOM_TOLERANCE


def test_region_rotate():
    p1 = Coordinate(0, 0)
    p2 = Coordinate(5, 0)
    p3 = Coordinate(0, 5)

    r1 = Region(RegionType.stator_air)
    r1.add_entity(Line(p1, p2))
    r1.add_entity(Arc(p2, p3, radius=10))
    r1.add_entity(Line(p3, p1))

    p4 = Coordinate(10, 5)
    p5 = Coordinate(5, 5)
    r2 = Region(RegionType.stator_air)
    r2.add_entity(Arc(p2, p4, radius=10))
    r2.add_entity(Line(p4, p5))
    r2.add_entity(Line(p5, p2))

    assert r1 != r2

    r1.rotate(p2, -90)
    assert r1 == r2


def test_region_translate():
    p1 = Coordinate(0, 0)
    p2 = Coordinate(5, 0)
    p3 = Coordinate(0, 5)
    r1 = Region(RegionType.stator_air)
    r1.add_entity(Line(p1, p2))
    r1.add_entity(Arc(p2, p3, radius=10))
    r1.add_entity(Line(p3, p1))

    p4 = Coordinate(3, -2)
    p5 = Coordinate(8, -2)
    p6 = Coordinate(3, 3)
    r2 = Region(RegionType.stator_air)
    r2.add_entity(Line(p4, p5))
    r2.add_entity(Arc(p5, p6, radius=10))
    r2.add_entity(Line(p6, p4))

    assert r1 != r2

    r1.translate(3, -2)
    assert r1 == r2


def test_get_set_region_magnet(mc):
    mc.set_variable("GeometryTemplateType", 1)
    mc.reset_adaptive_geometry()
    magnet = mc.get_region("L1_1Magnet2")
    assert isinstance(magnet, RegionMagnet)

    assert magnet.br_multiplier == 1
    assert magnet.br_value == 1.31
    assert magnet.br_used == 1.31
    assert magnet.magnet_angle == 22.5
    assert magnet.magnet_polarity == "N"
    assert magnet.region_type == RegionType.magnet

    assert isclose(magnet.br_x, 1.21028, abs_tol=1e-3)
    assert isclose(magnet.br_y, 0.50131, abs_tol=1e-3)

    magnet.magnet_angle = 0
    assert isclose(magnet.br_x, 1.31, abs_tol=1e-3)
    assert isclose(magnet.br_y, 0, abs_tol=1e-3)

    magnet.br_multiplier = 2
    assert magnet.br_value == 1.31
    assert magnet.br_used == 1.31 * 2

    magnet.magnet_polarity = "S"

    mc.set_region(magnet)
    magnet = mc.get_region("L1_1Magnet2")
    assert magnet.br_multiplier == 2
    assert magnet.magnet_angle == 0
    assert magnet.magnet_polarity == "S"
    assert isclose(magnet.br_x, 1.31 * 2, abs_tol=1e-3)
    assert isclose(magnet.br_y, 0, abs_tol=1e-3)
    assert magnet.br_value == 1.31
    assert magnet.br_used == 1.31 * 2
    assert magnet.region_type == RegionType.magnet


def test_get_set_region_compatibility(mc, monkeypatch):
    monkeypatch.setattr(mc.connection, "program_version", "2024.1")
    monkeypatch.setattr(rpc_client_core, "DONT_CHECK_MOTORCAD_VERSION", False)
    test_region = RegionMagnet()
    test_region.br_multiplier = 2
    with pytest.warns(UserWarning):
        mc.set_region(test_region)

    test_region = Region(RegionType.stator_air)
    test_region.mesh_length = 0.1

    with pytest.warns(UserWarning):
        mc.set_region(test_region)


def test_region_material_assignment(mc):
    rotor = mc.get_region("Rotor")
    rotor.material = "M470-50A"

    mc.set_region(rotor)

    assert rotor == mc.get_region("Rotor")


def test_set_lamination_type(mc_reset_to_default_on_teardown):
    rotor = mc_reset_to_default_on_teardown.get_region("Rotor")
    assert rotor.lamination_type == "Laminated"

    rotor._region_type = RegionType.adaptive
    # We don't get lamination type for normal regions yet
    rotor.lamination_type = "Solid"
    mc_reset_to_default_on_teardown.set_region(rotor)

    rotor = mc_reset_to_default_on_teardown.get_region("Rotor")
    assert rotor.lamination_type == "Solid"

    solid_rotor_section_file = (
        get_dir_path() + r"\test_files\adaptive_template_testing_solid_rotor_region.mot"
    )
    lam_rotor_section_file = (
        get_dir_path() + r"\test_files\adaptive_template_testing_lam_rotor_region.mot"
    )

    solid_rotor_section_result = (
        get_dir_path() + r"\test_files\adaptive_template_testing_solid_rotor_region"
        r"\FEResultsData\StaticLoadInductance_result_1.mes"
    )
    lam_rotor_section_result = (
        get_dir_path() + r"\test_files\adaptive_template_testing_lam_rotor_region"
        r"\FEResultsData\StaticLoadInductance_result_1.mes"
    )

    # load file into Motor-CAD
    mc_reset_to_default_on_teardown.load_from_file(solid_rotor_section_file)
    mc_reset_to_default_on_teardown.do_magnetic_calculation()
    mc_reset_to_default_on_teardown.load_fea_result(solid_rotor_section_result, 1)
    # Check eddy current to make sure rotor is solid
    res, units = mc_reset_to_default_on_teardown.get_point_value("Je", -9, -20)
    assert res != 0

    mc_reset_to_default_on_teardown.load_from_file(lam_rotor_section_file)
    mc_reset_to_default_on_teardown.do_magnetic_calculation()
    mc_reset_to_default_on_teardown.load_fea_result(lam_rotor_section_result, 1)
    # Check eddy current to make sure rotor is laminated
    res, units = mc_reset_to_default_on_teardown.get_point_value("Je", -9, -20)
    assert res == 0


def test_region_creation_warnings(mc):
    with pytest.warns():
        _ = Region()
    with pytest.warns():
        _ = Region(mc)


def test_set_get_magnetisation_directions(mc):
    magnet_region = mc.get_region("L1_1Magnet2")

    # test case 1
    magnet_region.magnetisation_direction = MagnetisationDirection.radial
    mc.set_region(magnet_region)
    magnet_region = mc.get_region("L1_1Magnet2")
    assert magnet_region.magnetisation_direction.value == MagnetisationDirection.radial.value

    # test case 2
    magnet_region.magnetisation_direction = MagnetisationDirection.parallel
    mc.set_region(magnet_region)
    magnet_region = mc.get_region("L1_1Magnet2")
    assert magnet_region.magnetisation_direction.value == MagnetisationDirection.parallel.value

    # test case 3
    magnet_region.magnetisation_direction = MagnetisationDirection.function
    magnet_region.magnetisation_function_amplitude = "1.125"
    magnet_region.magnetisation_function_angle = "(1-Pole_Number / 2) * theta + 180"

    mc.set_region(magnet_region)
    magnet_region = mc.get_region("L1_1Magnet2")
    assert magnet_region.magnetisation_direction.value == MagnetisationDirection.function.value
    assert magnet_region.magnetisation_function_amplitude == "1.125"
    assert magnet_region.magnetisation_function_angle == "(1-Pole_Number / 2) * theta + 180"


def test_copying(mc):
    stator = mc.get_region("stator")

    copy_region = copy(stator)

    assert copy_region == stator
    assert copy_region._raw_region == dict()
    deepcopy_region = deepcopy(stator)

    assert deepcopy_region == stator
    assert deepcopy_region._raw_region == dict()


def test_get_bezier_points():
    # Control points make a triangle with a height of 1
    control_points = [Coordinate(0, 0), Coordinate(0.5, 1), Coordinate(1, 0)]
    result_points = get_bezier_points(control_points, 3)

    # End points should match control points
    assert isclose(result_points[0].x, control_points[0].x)
    assert isclose(result_points[0].y, control_points[0].y)

    assert isclose(result_points[2].x, control_points[2].x)
    assert isclose(result_points[2].y, control_points[2].y)

    # Mid point should be half the height of the triangle
    assert isclose(result_points[1].x, 0.5)
    assert isclose(result_points[1].y, 0.5)


def test_region_creation_type(mc):
    new_region_1 = Region("rotor_air")
    assert new_region_1.region_type == RegionType.rotor_air

    with pytest.warns():
        # This should give us a warning that the region type is the first argument
        new_region_2 = Region(mc)

    with pytest.raises(Exception):
        # This should give us an exception that the region name isn't valid
        new_region_2 = Region("not_a_motorcad_region")

    with pytest.raises(Exception):
        # Passing in something that's not a string or motorcad object should give an exception
        new_region_3 = Region(1)
