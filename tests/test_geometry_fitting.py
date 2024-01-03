from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from ansys.motorcad.core.geometry_fitting import return_entity_list


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
        Coordinate(3.6, 7),
    ]
    assert e.points == expected_points
    assert isinstance(e[0], Arc)
    assert isinstance(e[1], Arc)
    assert isinstance(e[2], Arc)
    assert isinstance(e[3], Arc)
    assert isinstance(e[4], Arc)
    assert isinstance(e[5], Line)
    assert isinstance(e[6], Arc)
