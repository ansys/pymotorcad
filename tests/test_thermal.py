import pytest

from RPC_Test_Common import almost_equal, get_dir_path
from ansys.motorcad.core.rpc_client_core import MotorCADError
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_set_resistance_value():
    mc.set_resistance_value("test res", 6, 27, 4444, "test resistance")

    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(6, 27)
    assert res == 4444


def test_set_resistance_multiplier():
    mc.set_resistance_multiplier("test res mult", 7, 8, 5, "test resistance multiplier")

    # Value is being set correctly but
    # can't check value with get_node_to_node_resistance
    # -> Doesn't factor in multiplier (issue #39)

    # mc.do_steady_state_analysis()
    #
    # res = mc.get_node_to_node_resistance(7, 8)
    # assert res ==


def test_get_node_to_node_resistance():
    mc.do_steady_state_analysis()
    res = mc.get_node_to_node_resistance(1, 9)
    assert almost_equal(res, 0.0043, 3)


def test_save_load_clear_external_circuit():
    mc.set_resistance_value("test res", 3, 4, 150, "test resistance")

    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res == 150

    save_path = get_dir_path() + "\\test_files\\external_circuit.ecf"

    mc.save_external_circuit(save_path)

    mc.clear_external_circuit()
    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res != 150

    mc.load_external_circuit(save_path)
    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res == 150


def test_set_get_node_capacitance():
    mc.set_capacitance_value("test cap", 795, 35, "test capacitance value")
    mc.do_steady_state_analysis()

    cap = mc.get_node_capacitance(795)
    assert cap == 35


def test_get_node_power():
    mc.do_steady_state_analysis()

    power = mc.get_node_power(397)
    assert almost_equal(power, 75.2)


def test_get_node_temperature():
    mc.do_steady_state_analysis()
    # ambient
    temp = mc.get_node_temperature(0)
    assert temp == 40


def test_get_node_exists():
    mc.do_steady_state_analysis()

    assert mc.get_node_exists(2) is True

    # doesn't exist for this model
    assert mc.get_node_exists(211) is False

    # outside of range
    assert mc.get_node_exists(5000) is False

    # non-integer value
    with pytest.raises(MotorCADError) as e_info:
        mc.get_node_exists(0.5)
    assert "nodeNumber: Integer" in str(e_info.value)
