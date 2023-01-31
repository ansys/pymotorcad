import pytest

from RPC_Test_Common import almost_equal
from ansys.motorcad.core import MotorCADError
from setup_test import reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_get_magnetic_graph_point():
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_graph_point("TorqueVW", 3)
    assert almost_equal(x, 360)
    assert almost_equal(y, 180.14)


def test_get_magnetic_graph():
    reset_to_default_file(mc)
    mc.set_variable("TorqueCalculation", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_graph_point("TorqueVW", 3)
    x1, y1 = mc.get_magnetic_graph("TorqueVW")

    assert almost_equal(x, x1[3])
    assert almost_equal(y, y1[3])

    with pytest.raises(MotorCADError):
        x, y = mc.get_magnetic_graph("ediujhweioufbewkijbf")


# Get Motor-CAD exe
