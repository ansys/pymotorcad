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

import builtins
from copy import deepcopy
import math
from math import inf, isclose, pi, radians, sin, sqrt
import tempfile

import pytest

from RPC_Test_Common import get_dir_path, reset_to_default_file
from ansys.motorcad.core import MotorCADError, geometry
from ansys.motorcad.core.geometry import (
    GEOM_TOLERANCE,
    Arc,
    Coordinate,
    Line,
    Region,
    RegionMagnet,
    RegionType,
    _Orientation,
    _orientation_of_three_points,
    rt_to_xy,
)
from ansys.motorcad.core.geometry_shapes import eq_triangle_h, triangular_notch
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
    expected_region.colour = (0, 0, 0)
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
    }

    test_region = geometry.Region(region_type=RegionType.stator_copper)
    test_region.name = "test_region"
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
    test_region.singular = (False,)

    region = geometry.Region._from_json(raw_region)

    assert region == test_region


def test_region_to_json():
    raw_region = {
        "name": "test_region",
        "material": "copper",
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
        "on_boundary": False,
    }

    test_region = geometry.Region(region_type=RegionType.stator_copper)
    test_region.name = "test_region"
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

    assert test_region._to_json() == raw_region


def test_region_is_closed():
    region = generate_constant_region()

    assert region.is_closed()


def test_set_linked_region():
    region = generate_constant_region()

    region_linked = Region(region_type=RegionType.stator)
    region_linked.name = "linked_region_test"
    # set linked region
    region.linked_region = region_linked

    assert region._linked_region.name == region_linked.name
    assert region_linked.linked_region.name == region.name


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


def test_line_length():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))

    assert line.length == sqrt(2)


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


def test_delete_region(mc):
    stator = mc.get_region("Stator")

    mc.delete_region(stator)

    with pytest.raises(Exception) as e_info:
        mc.get_region("Stator")

    assert "Failed to find region with name" in str(e_info.value)
    reset_to_default_file(mc)


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
        geom_import.draw_regions(region)


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

    # check exception is raised when a point that is not a corner is specified
    with pytest.raises(Exception):
        notch_1.round_corner(corners[0], corner_radius)
    with pytest.raises(Exception):
        notch_1.round_corner(notch_1.entities[0].midpoint, corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(Exception):
        notch_2.round_corner(notch_2.entities[0].end, 100 * corner_radius)


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

    # check exception is raised when a point that is not a corner is specified
    with pytest.raises(Exception):
        notch_1.round_corner(corners[0], corner_radius)
    with pytest.raises(Exception):
        notch_1.round_corner(notch_1.entities[0].midpoint, corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(Exception):
        notch_2.round_corner(notch_2.entities[0].end, 100 * corner_radius)


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

    # check exception is raised when a point that is not a corner is specified
    with pytest.raises(Exception):
        shape_1.round_corner(corners[0], corner_radius)
    with pytest.raises(Exception):
        shape_1.round_corner(shape_1.entities[0].midpoint, corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(Exception):
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

    # check exception is raised when a point that is not a corner is specified
    with pytest.raises(Exception):
        shape_1.round_corner(corners[0], corner_radius)
    with pytest.raises(Exception):
        shape_1.round_corner(shape_1.entities[0].midpoint, corner_radius)

    # check exception is raised when the corner radius is too large
    # this is the case when the distance by which an original entity is to be shortened is larger
    # than the entity's original length
    with pytest.raises(Exception):
        shape_2.round_corner(shape_2.entities[0].end, 100 * corner_radius)


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

    triangle_3.round_corner(triangle_3.points[3], radius_2)

    # check that the entities making up the triangle are unchanged
    assert triangle_3.is_closed()
    for i in range(2):
        assert triangle_3.entities[i] == triangle_2.entities[i]
    assert triangle_3.entities[2].start == triangle_2.entities[2].start
    assert triangle_3.entities[2].end == triangle_2.entities[2].midpoint
    assert triangle_3.entities[3].start == triangle_2.entities[2].midpoint
    assert triangle_3.entities[3].end == triangle_2.entities[2].end


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

    mc.set_region(magnet)
    magnet = mc.get_region("L1_1Magnet2")
    assert magnet.br_multiplier == 2
    assert magnet.magnet_angle == 0
    assert magnet.magnet_polarity == "N"
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


def test_set_lamination_type(mc):
    rotor = mc.get_region("Rotor")
    assert rotor.lamination_type == "Laminated"

    rotor._region_type = RegionType.adaptive
    # We don't get lamination type for normal regions yet
    rotor.lamination_type = "Solid"
    mc.set_region(rotor)

    rotor = mc.get_region("Rotor")
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
    mc.load_from_file(solid_rotor_section_file)
    mc.do_magnetic_calculation()
    mc.load_fea_result(solid_rotor_section_result, 1)
    # Check eddy current to make sure rotor is solid
    res, units = mc.get_point_value("Je", -9, -20)
    assert res != 0

    mc.load_from_file(lam_rotor_section_file)
    mc.do_magnetic_calculation()
    mc.load_fea_result(lam_rotor_section_result, 1)
    # Check eddy current to make sure rotor is laminated
    res, units = mc.get_point_value("Je", -9, -20)
    assert res == 0

    reset_to_default_file(mc)


def test_region_creation_warnings(mc):
    with pytest.warns():
        _ = Region()
    with pytest.warns():
        _ = Region(mc)
