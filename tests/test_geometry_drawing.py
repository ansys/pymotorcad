from matplotlib import pyplot as plt

from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from ansys.motorcad.core.geometry_drawing import draw_objects
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_draw_objects(monkeypatch):
    # Just check it runs for now
    # Stop plt.show() blocking tests
    monkeypatch.setattr(plt, "show", lambda: None)

    region = mc.get_region("Stator")
    region2 = mc.get_region("StatorWedge")
    region3 = mc.get_region("ArmatureSlotL1")

    draw_objects(region)
    draw_objects([region, region2, region3])

    # Test overflow of colours
    region4 = mc.get_region("StatorAir")
    region5 = mc.get_region("Shaft")
    draw_objects([region, region2, region3, region4, region5])

    # Test object drawing
    c1 = Coordinate(0, 0)
    c2 = Coordinate(4, 0)
    c3 = Coordinate(4, 4)

    l1 = Line(c1, c2)
    a1 = Arc(c1, c3, c2, -4)
    draw_objects(l1)
    draw_objects([l1, a1])

    draw_objects([c1, c2])
