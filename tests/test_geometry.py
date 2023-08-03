import pytest

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


def test_get_region():
    with pytest.raises(MotorCADError):
        mc.geometry.get_region("Stator")


def test_set_region():
    region = geometry.Region()
    region.name = "testing_region"
    region.colour = (0, 0, 255)
    region.material = "Air"

    with pytest.raises(MotorCADError):
        mc.geometry.set_region(region)


def test_region_add_entity():
    region = geometry.Region()
    region.add_entity(geometry.Line((0, 0), (1, 1)))

    assert region.entities.count() == 1


def test_region_add_polyline():
    region = geometry.Region()
    region.add_polyline(
        [
            geometry.Line((0, 0), (1, 1)),
            geometry.Line((1, 1), (1, 0)),
            geometry.Line((1, 0), (0, 0)),
        ]
    )

    assert region.entities.count() == 3


def test_region_remove_entity():
    region = geometry.Region()
    region.add_polyline(
        [
            geometry.Line((0, 0), (1, 1)),
            geometry.Line((1, 1), (1, 0)),
            geometry.Line((1, 0), (0, 0)),
        ]
    )
    region.remove_entity(region.entities[1])

    assert region.entities.count() == 2
