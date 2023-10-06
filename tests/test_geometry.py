from copy import deepcopy
import math
from math import cos, isclose, radians, sin, sqrt

from matplotlib import pyplot as plt
import pytest

from RPC_Test_Common import get_dir_path
from ansys.motorcad.core import MotorCADError, geometry
from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from ansys.motorcad.core.geometry_drawing import draw_regions
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def generate_constant_region():
    region = geometry.Region()
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

    square = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            square.add_entity(geometry.Line(point, points[0]))
        else:
            square.add_entity(geometry.Line(point, points[count + 1]))

    return square


def create_triangle():
    points = [geometry.Coordinate(1, 2.2), geometry.Coordinate(2.2, 1), geometry.Coordinate(4, 4)]

    triangle = geometry.Region()

    for count, point in enumerate(points):
        if count == len(points) - 1:
            triangle.add_entity(geometry.Line(point, points[0]))
        else:
            triangle.add_entity(geometry.Line(point, points[count + 1]))

    return triangle


def test_set_get_winding_coil():
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


def test_check_if_geometry_is_valid():
    # base_test_file should have valid geometry
    mc.check_if_geometry_is_valid(0)

    save_slot_depth = mc.get_variable("Slot_Depth")

    mc.set_variable("Slot_Depth", 50)
    with pytest.raises(MotorCADError):
        mc.check_if_geometry_is_valid(0)

    # Check resetting geometry works
    mc.check_if_geometry_is_valid(1)

    mc.set_variable("Slot_Depth", save_slot_depth)


def test_set_adaptive_parameter_value():
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


def test_set_adaptive_parameter_value_incorrect_type():
    with pytest.raises(MotorCADError):
        mc.set_adaptive_parameter_value("incorrect_type", "test_string")


def test_get_adaptive_parameter_value():
    mc.set_adaptive_parameter_value("test_parameter_1", 100)

    value = mc.get_adaptive_parameter_value("test_parameter_1")
    assert value == 100


def test_get_adaptive_parameter_value_does_not_exist():
    with pytest.raises(Exception) as e_info:
        mc.get_adaptive_parameter_value("testing_parameter")

    assert "No adaptive parameter found with name" in str(e_info.value)


def test_get_region():
    expected_region = generate_constant_region()
    mc.set_region(expected_region)

    region = mc.get_region(expected_region.name)
    assert region == expected_region

    with pytest.raises(Exception) as e_info:
        mc.get_region("Rotor_Magnet")

    assert ("region" in str(e_info.value)) and ("name" in str(e_info.value))


def test_set_region():
    region = generate_constant_region()
    mc.set_region(region)
    returned_region = mc.get_region("testing_region")
    assert returned_region == region


def test_save_adaptive_script():
    filepath = get_dir_path() + r"\test_files\adaptive_templates_script.py"
    mc.save_adaptive_script(filepath)

    num_lines = mc.get_variable("AdaptiveTemplates_ScriptLines")

    with open(filepath, "rbU") as f:
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
    }

    test_region = geometry.Region()
    test_region.name = "test_region"
    test_region.material = "copper"
    test_region.colour = (240, 0, 0)
    test_region.area = 5.1
    test_region.centroid = geometry.Coordinate(0.0, 1.0)
    test_region.region_coordinate = geometry.Coordinate(0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []

    region = geometry.Region()
    region._from_json(raw_region)

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
    }

    test_region = geometry.Region()
    test_region.name = "test_region"
    test_region.material = "copper"
    test_region.colour = (240, 0, 0)
    test_region.area = 5.1
    test_region.centroid = geometry.Coordinate(0.0, 1.0)
    test_region.region_coordinate = geometry.Coordinate(0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []

    assert test_region._to_json() == raw_region


def test_region_is_closed():
    region = generate_constant_region()

    assert region.is_closed()


def test_region_contains_same_entities():
    region = generate_constant_region()

    expected_region = deepcopy(region)
    expected_region.entities.reverse()

    assert region == expected_region


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
    region_2 = geometry.Region()
    region_2.entities = entities

    assert region_1.entities == region_2.entities


def test_entities_same_reverse():
    region_1 = generate_constant_region()

    region_2 = geometry.Region()
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
    region_2 = geometry.Region()

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

    assert line.get_coordinate_from_distance(geometry.Coordinate(0, 0), 1) == geometry.Coordinate(
        1, 0
    )


def test_line_get_length():
    line = geometry.Line(geometry.Coordinate(0, 0), geometry.Coordinate(1, 1))

    assert line.get_length() == sqrt(2)


def test_arc_get_coordinate_from_percentage_distance():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    coord = arc.get_coordinate_from_percentage_distance(geometry.Coordinate(-1, 0), 0.5)
    assert isclose(coord.x, 0, abs_tol=1e-12)
    assert isclose(coord.y, -1, abs_tol=1e-12)


def test_arc_get_coordinate_from_distance():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    coord = arc.get_coordinate_from_distance(geometry.Coordinate(-1, 0), math.pi / 2)
    assert math.isclose(coord.x, 0, abs_tol=1e-12)
    assert math.isclose(coord.y, -1, abs_tol=1e-12)


def test_arc_get_length():
    arc = geometry.Arc(
        geometry.Coordinate(-1, 0), geometry.Coordinate(1, 0), geometry.Coordinate(0, 0), 1
    )

    assert arc.get_length() == math.pi


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


def test_unite_regions():
    """Test unite two regions into a single region."""
    #   Before         After
    # |--------|    |--------|
    # |  |--|  |    |        |
    # |  |  |  | -> |        |
    # |--|--|--|    |--|  |--|
    #    |  |          |  |
    #    |--|          |--|
    region_a = geometry.Region()
    region_b = geometry.Region()
    expected_region = geometry.Region()

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

    for count, point in enumerate(points_b):
        if count == len(points_b) - 1:
            region_b.add_entity(geometry.Line(point, points_b[0]))
        else:
            region_b.add_entity(geometry.Line(point, points_b[count + 1]))

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

    for count, point in enumerate(points_expected):
        if count == len(points_expected) - 1:
            expected_region.add_entity(geometry.Line(point, points_expected[0]))
        else:
            expected_region.add_entity(geometry.Line(point, points_expected[count + 1]))

    expected_region.centroid = geometry.Coordinate(0, -0.3)
    expected_region.region_coordinate = geometry.Coordinate(0, -0.3)
    expected_region.duplications = 1

    united_region = mc.unite_regions(region_a, [region_b])

    assert united_region == expected_region


def test_unite_regions_1():
    """Testing two regions not touching cannot be united."""
    #          Before                         After
    # |--------|
    # |        |    |---|
    # |        |    |   |     ->    RPC error: Unable to unite regions.
    # |        |    |---|           Regions have no mutual interceptions
    # |--------|

    region_a = geometry.Region()
    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, -1), geometry.Coordinate(-1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(-1, 1), geometry.Coordinate(1, 1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, 1), geometry.Coordinate(1, -1)))
    region_a.add_entity(geometry.Line(geometry.Coordinate(1, -1), geometry.Coordinate(-1, -1)))

    region_b = geometry.Region()
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, 5), geometry.Coordinate(5, 10)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, 10), geometry.Coordinate(10, 10)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 10), geometry.Coordinate(10, 5)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(10, 5), geometry.Coordinate(5, 5)))

    with pytest.raises(Exception) as e_info:
        mc.unite_regions(region_a, [region_b])

    assert "Unable to unite regions" in str(e_info.value)


def test_unite_regions_2():
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

    entities = []
    for count, point in enumerate(points):
        if count == len(points) - 1:
            entities.append(geometry.Line(point, points[0]))
        else:
            entities.append(geometry.Line(point, points[count + 1]))

    expected_region = geometry.Region()
    expected_region.centroid = geometry.Coordinate(1.57886178861789, 1.57886178861789)
    expected_region.region_coordinate = geometry.Coordinate(1.57886178861789, 1.57886178861789)

    for entity in entities:
        expected_region.add_entity(entity)

    union = mc.unite_regions(square, [triangle])

    assert expected_region == union


def test_check_collisions():
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

    region_b = geometry.Region()
    region_b.add_entity(geometry.Line(geometry.Coordinate(0, -2), geometry.Coordinate(1, 2)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(1, 2), geometry.Coordinate(5, -3)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(5, -3), geometry.Coordinate(0, -2)))

    collisions = mc.check_collisions(region_a, [region_b, mc.get_region("Stator")])
    num_collisions = len(collisions)

    assert num_collisions == 1
    assert collisions[0] == region_b


def test_check_collisions_1():
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

    region_b = geometry.Region()
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


def test_check_collisions_2():
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

    region_b = geometry.Region()
    region_b.add_entity(geometry.Line(geometry.Coordinate(-0.2, -2), geometry.Coordinate(-0.2, 0)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(-0.2, 0), geometry.Coordinate(0.2, 0)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, 0), geometry.Coordinate(0.2, -2)))
    region_b.add_entity(geometry.Line(geometry.Coordinate(0.2, -2), geometry.Coordinate(-0.2, -2)))

    collisions = mc.check_collisions(region_a, [region_b, mc.get_region("Stator")])
    num_collisions = len(collisions)

    assert num_collisions == 0


def test_check_collisions_3():
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
    s_p = []
    s_l = []

    s_p.append(geometry.Coordinate(0, 0))
    s_p.append(geometry.Coordinate(0, 2))
    s_p.append(geometry.Coordinate(2, 2))
    s_p.append(geometry.Coordinate(2, 0))

    s_l.append(geometry.Line(s_p[0], s_p[1]))
    s_l.append(geometry.Line(s_p[1], s_p[2]))
    s_l.append(geometry.Line(s_p[2], s_p[3]))
    s_l.append(geometry.Line(s_p[3], s_p[0]))

    square = geometry.Region()
    for entity in s_l:
        square.add_entity(entity)

    t_p = []
    t_l = []

    t_p.append(geometry.Coordinate(1, 2.2))
    t_p.append(geometry.Coordinate(2.2, 1))
    t_p.append(geometry.Coordinate(4, 4))

    t_l.append(geometry.Line(t_p[0], t_p[1]))
    t_l.append(geometry.Line(t_p[1], t_p[2]))
    t_l.append(geometry.Line(t_p[2], t_p[0]))

    triangle = geometry.Region()
    for entity in t_l:
        triangle.add_entity(entity)

    collisions = mc.check_collisions(triangle, [square])
    assert len(collisions) == 1
    assert collisions[0] == square

    collisions = mc.check_collisions(square, [triangle])
    assert len(collisions) == 1
    assert collisions[0] == triangle


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


def test_line_coordinate_exists():
    p0 = Coordinate(0, 0)
    p1 = Coordinate(10, 0)
    l0 = Line(p0, p1)

    p_2 = Coordinate(5, 0)
    p_3 = Coordinate(11, 0)
    p_4 = Coordinate(5, 0.1)
    assert l0.coordinate_exists(p_2) is True
    assert l0.coordinate_exists(p_4) is False
    assert l0.coordinate_exists(p_3) is False


def test_arc_start_end_angle():
    p_centre = Coordinate(2, 2)
    p_end = Coordinate(4, 2)
    p_start = Coordinate(2, 0)
    radius = -2

    a0 = Arc(p_start, p_end, p_centre, radius)
    assert a0.start_angle() == -90
    assert a0.end_angle() == 0


def test_arc_coordinate_exists():
    pc = Coordinate(0, 0)
    p0 = Coordinate(0, -4)
    p1 = Coordinate(0, 4)
    radius = abs(p0 - pc)

    a1 = Arc(p0, p1, pc, radius)

    p2 = Coordinate(4, 0)
    p3 = p2 / 2
    p4 = Coordinate(-4, 0)

    assert a1.coordinate_exists(p2)
    assert a1.coordinate_exists(p3) is False
    assert a1.coordinate_exists(p4) is False

    radius = -1 * abs(p0 - pc)
    a1 = Arc(p0, p1, pc, radius)

    assert a1.coordinate_exists(p2) is False
    assert a1.coordinate_exists(p3) is False
    assert a1.coordinate_exists(p4) is True


def test_midpoints():
    p0 = Coordinate(-2, 4)
    p1 = Coordinate(10, -8)
    p01 = p1 - p0
    l0 = Line(p0, p1)
    assert l0.midpoint() == (p0 + p01 / 2)

    pc = Coordinate(-2, -6)
    p0 = Coordinate(1, -3)
    p1 = Coordinate(1, -9)
    a0 = Arc(p0, p1, pc, abs(p1 - pc))
    assert a0.midpoint() == Coordinate(-2, abs(p1 - pc) - 6)

    pc = Coordinate(0, 0)
    p0 = Coordinate(0, 3)
    p1 = Coordinate(3, 0)
    a0 = Arc(p0, p1, pc, -abs(p1 - pc))
    assert a0.midpoint() == Coordinate(3 * sin(radians(45)), 3 * cos(radians(45)))


def test_total_angle():
    pc = Coordinate(0, 0)
    p0 = Coordinate(0, 5)
    p1 = Coordinate(-5, 0)
    a1 = Arc(p0, p1, pc, abs(p0 - pc))
    assert a1.total_angle() == 90

    pc = Coordinate(-3, -1)
    p0 = Coordinate(-7, -1)
    p1 = Coordinate(-3, -5)
    a1 = Arc(p0, p1, pc, abs(p0 - pc))
    assert a1.total_angle() == 90


def test_draw_regions(monkeypatch):
    # Just check it runs for now
    # Stop plt.show() blocking tests
    monkeypatch.setattr(plt, "show", lambda: None)

    region = mc.get_region("Stator")
    region2 = mc.get_region("StatorWedge")
    region3 = mc.get_region("ArmatureSlotL1")
    draw_regions(region)
    draw_regions([region, region2, region3])


def test_add_point():
    region = generate_constant_region()
    points = region.get_points()
    new_point = region.entities[0].midpoint()
    region.add_point(new_point)

    # Expected result
    points.insert(1, new_point)
    assert points == region.get_points()

    region = generate_constant_region()
    with pytest.raises(Exception):
        region.add_point(Coordinate(100, 100))

    points = region.get_points()
    new_point = region.entities[1].midpoint()
    region.add_point(new_point)

    # Expected result
    points.insert(2, new_point)
    assert points == region.get_points()


def test_edit_point():
    region = generate_constant_region()
    points = region.get_points()
    new_coord = Coordinate(0, 0)
    region.edit_point(points[0], new_coord)
    assert region.entities[0].start == new_coord
    assert region.entities[2].end == new_coord

    region = generate_constant_region()
    points = region.get_points()

    # Move arc point too far
    translate = Coordinate(2, 2)
    with pytest.raises(Exception):
        region.edit_point(points[2], points[2] + translate)

    ref_region = generate_constant_region()
    region = generate_constant_region()
    points = region.get_points()
    draw_regions(region)
    translate = Coordinate(0.2, 0.2)
    region.edit_point(points[2], points[2] + translate)
    region.edit_point(points[1], points[1] + translate)

    assert region.entities[0].end == ref_region.entities[0].end + translate
    assert region.entities[1].start == ref_region.entities[1].start + translate
    assert region.entities[1].end == ref_region.entities[1].end + translate  #
    assert region.entities[2].start == ref_region.entities[2].start + translate
