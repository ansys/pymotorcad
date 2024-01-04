import pytest

from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from ansys.motorcad.core.geometry_fitting import _TestEntity, return_entity_list


def test_return_entity_list():
    c = []

    c.append(Coordinate(7, 11))
    c.append(Coordinate(20, 10))
    c.append(Coordinate(24, 7))
    c.append(Coordinate(24, 0))
    c.append(Coordinate(18, 0))
    c.append(Coordinate(15, 3))
    c.append(Coordinate(14, 5))
    c.append(Coordinate(6, 6))
    c.append(Coordinate(1, 6))
    c.append(Coordinate(1, 7))
    c.append(Coordinate(2, 7))

    # Duplicate coordinates
    c.append(Coordinate(3, 7))
    c.append(Coordinate(3, 7))
    c.append(Coordinate(3, 7))

    c.append(Coordinate(3.2, 7))
    c.append(Coordinate(3.4, 7))
    c.append(Coordinate(3.6, 7))
    c.append(Coordinate(4, 7))
    c.append(Coordinate(7, 11))

    e = return_entity_list(c, 0.001, 0.001)
    expected_points = [
        Coordinate(7, 11),
        Coordinate(24, 7),
        Coordinate(18, 0),
        Coordinate(14, 5),
        Coordinate(1, 6),
        Coordinate(2, 7),
        Coordinate(4, 7),
    ]
    assert e.points == expected_points
    assert isinstance(e[0], Arc)
    assert isinstance(e[1], Arc)
    assert isinstance(e[2], Arc)
    assert isinstance(e[3], Arc)
    assert isinstance(e[4], Arc)
    assert isinstance(e[5], Line)
    assert isinstance(e[6], Line)


def test__TestEntity():
    # Cover any lines of code missed by other tests
    c1 = Coordinate(0, 0)
    c2 = Coordinate(10, 0)

    points = [c1, c2]
    tolerance = 2

    test_entity = _TestEntity("string", points, tolerance)
    with pytest.raises(TypeError):
        test_entity.is_in_tolerance()


def test__TestEntity_is_line_in_tolerance():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(5, 1)
    c3 = Coordinate(10, 0)

    points = [c1, c2, c3]
    l1 = Line(c1, c3)
    tolerance = 2

    test_entity = _TestEntity(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    tolerance = 1
    test_entity = _TestEntity(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    tolerance = 0.9
    test_entity = _TestEntity(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()


def test__TestEntity_is_arc_in_tolerance():
    centre = Coordinate(0, 0)
    c1 = Coordinate(5, 0)
    c2 = Coordinate(0, 5)
    l1 = Arc(c1, c2, centre, 5)

    tolerance = 1

    # Within angle and tolerance
    t1 = Coordinate.from_polar_coords(5.5, 45)
    points = [c1, t1, c2]
    test_entity = _TestEntity(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    # Within angle and at max tolerance
    t1 = Coordinate(6, 0)
    points = [c1, t1, c2]
    test_entity = _TestEntity(l1, points, tolerance)
    assert test_entity.is_in_tolerance()

    # Within angle and outside tolerance
    t1 = Coordinate.from_polar_coords(6.1, 45)
    points = [c1, t1, c2]
    test_entity = _TestEntity(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()

    # Not within angle and in radial tolerance
    t1 = Coordinate.from_polar_coords(5, -45)
    points = [c1, t1, c2]
    test_entity = _TestEntity(l1, points, tolerance)
    assert not test_entity.is_in_tolerance()

    # Not within angle and in tolerance
    t1 = c1 - Coordinate(0.5, 0.5)
    assert not l1.coordinate_within_arc_radius(t1)
    points = [c1, t1, c2]
    test_entity = _TestEntity(l1, points, tolerance)
    assert test_entity.is_in_tolerance()
