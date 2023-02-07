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


def test_get_temperature_graph_point():
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_temperature_graph_point("Housing [Active]", 4)

    assert almost_equal(x, 16)
    assert almost_equal(y, 47.66)

def test_get_temperature_graph():
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_temperature_graph_point("Housing [Active]", 4)
    x1, y1 = mc.get_temperature_graph("Housing [Active]")

    assert almost_equal(x, x1[4])
    assert almost_equal(y, y1[4])

def test_get_power_graph_point():
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_power_graph_point("Stator Back Iron", 4)

    assert almost_equal(x, 16)
    assert almost_equal(y, 341.3)

def test_get_power_graph():
    reset_to_default_file(mc)
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_power_graph_point("Stator Back Iron", 4)
    x1, y1 = mc.get_power_graph("Stator Back Iron")

    assert almost_equal(x, x1[4])
    assert almost_equal(y, y1[4])

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
