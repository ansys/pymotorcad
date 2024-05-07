from matplotlib import pyplot as plt
import pytest

from ansys.motorcad.core.geometry import Arc, Coordinate, Line
from ansys.motorcad.core.geometry_drawing import draw_objects, draw_objects_debug
from ansys.motorcad.core.rpc_client_core import DEFAULT_INSTANCE, set_default_instance
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()
drawing_flag = False


def set_drawing_flag(*args, **kwargs):
    global drawing_flag
    drawing_flag = True


def test_draw_objects_debug(monkeypatch):
    # Just check it runs for now
    # Stop plt.show() blocking tests
    global drawing_flag
    drawing_flag = False
    monkeypatch.setattr(plt, "show", set_drawing_flag)

    region = mc.get_region("Stator")

    draw_objects_debug(region)
    assert drawing_flag is True

    drawing_flag = False
    save_def_instance = DEFAULT_INSTANCE
    set_default_instance(mc.connection._port)

    draw_objects_debug(region)
    assert drawing_flag is False

    set_default_instance(save_def_instance)


def test_draw_objects(monkeypatch):
    # Just check it runs for now
    # Stop plt.show() blocking tests
    global drawing_flag
    drawing_flag = False

    monkeypatch.setattr(plt, "show", set_drawing_flag)

    region = mc.get_region("Stator")
    region2 = mc.get_region("StatorWedge")
    region3 = mc.get_region("ArmatureSlotL1")

    draw_objects(region)
    assert drawing_flag is True
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

    # Test missing object doesn't break function
    draw_objects([c1, c2, None])

    with pytest.raises(TypeError):
        draw_objects([int(10)])
