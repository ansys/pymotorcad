import math
from math import isclose, sqrt

import pytest

from RPC_Test_Common import get_dir_path
from ansys.motorcad.core import MotorCADError, geometry
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


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
    with pytest.raises(MotorCADError):
        mc.geometry.set_adaptive_parameter_value("test_parameter", 100)


def test_get_adaptive_parameter_value():
    mc.geometry.set_adaptive_parameter_value("test_parameter_1", 100)

    with pytest.raises(MotorCADError):
        value = mc.geometry.get_adaptive_parameter_value("test_parameter_1")

    assert value == 100


def test_get_region():
    with pytest.raises(MotorCADError):
        region = mc.geometry.get_region("Stator")

    assert region.name == "Stator"


def test_set_region():
    region = geometry.Region()
    region.name = "testing_region"
    region.colour = (0, 0, 255)
    region.material = "Air"

    with pytest.raises(MotorCADError):
        mc.geometry.set_region(region)


def test_get_entities_between_poly_start_end():
    region = mc.geometry.get_region("Stator")
    poly = [geometry.Line(region.entities[4].end, region.entities[7].end)]

    entities_to_remove, start_index = mc.geometry.get_entities_between_poly_start_end(region, poly)

    assert entities_to_remove == region.entities[4:7:1]
    assert start_index == 4


def test_save_adaptive_script():
    with pytest.raises(MotorCADError):
        mc.geometry.save_adaptive_script(
            get_dir_path() + r"\test_files\adaptive_templates_script.py"
        )


def test_region_add_entity():
    region = geometry.Region()
    region.add_entity(geometry.Line((0, 0), (1, 1)))

    assert len(region.entities) == 1


def test_region_insert_entity():
    region = geometry.Region()
    region.add_entity(geometry.Line((0, 0), (1, 1)))

    entity = geometry.Line((-2, 2), (2, 3))
    region.insert_entity(0, entity)

    assert (len(region.entities) == 2) & (region.entities[0] == entity)


def test_region_insert_polyline():
    region = geometry.Region()
    region.insert_polyline(
        0,
        [
            geometry.Line((0, 0), (1, 1)),
            geometry.Line((1, 1), (1, 0)),
            geometry.Line((1, 0), (0, 0)),
        ],
    )

    assert len(region.entities) == 3


def test_region_remove_entity():
    region = geometry.Region()
    region.insert_polyline(
        0,
        [
            geometry.Line((0, 0), (1, 1)),
            geometry.Line((1, 1), (1, 0)),
            geometry.Line((1, 0), (0, 0)),
        ],
    )
    region.remove_entity(region.entities[1])

    assert len(region.entities) == 2


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
    test_region.centroid = (0.0, 1.0)
    test_region.region_coordinate = (0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []

    region = geometry.Region()
    region._from_json(raw_region)

    assert region.name == test_region.name
    assert region.material == test_region.material
    assert region.colour == test_region.colour
    assert region.area == test_region.area
    assert region.centroid == test_region.centroid
    assert region.region_coordinate == test_region.region_coordinate
    assert region.duplications == test_region.duplications
    assert region.entities == test_region.entities


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
    test_region.centroid = (0.0, 1.0)
    test_region.region_coordinate = (0.0, 1.1)
    test_region.duplications = 10
    test_region.entities = []

    assert test_region._to_json() == raw_region


def test_line_get_coordinate_from_percentage_distance():
    line = geometry.Line((0, 0), (1, 1))

    x, y = line.get_coordinate_from_percentage_distance(0, 0, 0.5)
    assert (x, y) == (0.5, 0.5)


def test_line_get_coordinate_from_distance():
    line = geometry.Line((0, 0), (1, 1))

    assert line.get_coordinate_from_distance(0, 0, sqrt(2) / 2) == (0.5, 0.5)


def test_line_get_length():
    line = geometry.Line((0, 0), (1, 1))

    assert line.get_length() == sqrt(2)


def test_arc_get_coordinate_from_percentage_distance():
    arc = geometry.Arc((-1, 0), (1, 0), (0, 0), 1)

    x, y = arc.get_coordinate_from_percentage_distance(-1, 0, 0.5)
    assert isclose(x, 0, abs_tol=1e-12)
    assert isclose(y, -1, abs_tol=1e-12)


def test_arc_get_coordinate_from_distance():
    arc = geometry.Arc((-1, 0), (1, 0), (0, 0), 1)

    x, y = arc.get_coordinate_from_distance(-1, 0, math.pi / 2)
    assert math.isclose(x, 0, abs_tol=1e-12)
    assert math.isclose(y, -1, abs_tol=1e-12)


def test_arc_get_length():
    arc = geometry.Arc((-1, 0), (1, 0), (0, 0), 1)

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
        geometry.Line((0.0, 0.0), (-1.0, 0)),
        geometry.Arc((-1.0, 0.0), (1.0, 0.0), (0.0, 0.0), 1.0),
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
        geometry.Line((0.0, 0.0), (-1.0, 0)),
        geometry.Arc((-1.0, 0.0), (1.0, 0.0), (0.0, 0.0), 1.0),
    ]

    converted_entities = geometry._convert_entities_from_json(raw_entities)
    assert isinstance(converted_entities[0], type(test_entities[0]))
    assert converted_entities[0].start == test_entities[0].start
    assert converted_entities[0].end == test_entities[0].end

    assert isinstance(converted_entities[1], type(test_entities[1]))
    assert converted_entities[1].start == test_entities[1].start
    assert converted_entities[1].end == test_entities[1].end
    assert converted_entities[1].centre == test_entities[1].centre
    assert converted_entities[1].radius == test_entities[1].radius
