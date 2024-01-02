from ansys.motorcad.core.geometry import Coordinate
from ansys.motorcad.core.geometry_fitting import _orientation, Orientation


def test__orientation():
    c1 = Coordinate(0, 0)
    c2 = Coordinate(1, 1)
    c3 = Coordinate(2, 2)
    assert (_orientation(c1, c2, c3) == Orientation.collinear)

    c1 = Coordinate(0, 3)
    c2 = Coordinate(4, 2)
    c3 = Coordinate(3, 1)
    assert (_orientation(c1, c2, c3) == Orientation.clockwise)

    c1 = Coordinate(0, 3)
    c2 = Coordinate(1, 2)
    c3 = Coordinate(9, 5)
    assert (_orientation(c1, c2, c3) == Orientation.anticlockwise)
