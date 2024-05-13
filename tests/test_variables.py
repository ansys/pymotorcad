import pytest

from RPC_Test_Common import reset_to_default_file
from ansys.motorcad.core import MotorCADError


def test_get_variable(mc):
    # normal call and checks result isn't wild
    var = mc.get_variable("tooth_width")
    assert var > 0
    assert var < 10000

    # wrong var name
    with pytest.raises(MotorCADError):
        var = mc.get_variable("not_a_real_variable")

    # check int
    var = mc.get_variable("Duty_Cycle_Number_Points")
    assert isinstance(var, int)

    # check bool
    var = mc.get_variable("TorqueSpeedCalculation")
    assert isinstance(var, bool)

    # check string
    var = mc.get_variable("Discovery_FileName")
    assert isinstance(var, str)


def test_set_variable(mc):
    # Standard call and check var has been set
    # Might be better to move this to some longer test sequences
    # Can specify order of tests so can run sequences after short tests
    mc.set_variable("tooth_width", 10)
    tooth_width = mc.get_variable("tooth_width")
    assert tooth_width == 10

    # wrong variable name
    with pytest.raises(Exception):
        mc.set_variable("Not_a_real_variable", 10)

    # bool type
    mc.set_variable("TorqueSpeedCalculation", True)
    assert mc.get_variable("TorqueSpeedCalculation") == True

    mc.set_variable("Discovery_FileName", "test")
    assert mc.get_variable("Discovery_FileName") == "test"


def test_get_array_variable(mc):
    reset_to_default_file(mc)

    var = mc.get_array_variable("Duty_Cycle_Time", 2)
    assert isinstance(var, int)

    var = mc.get_array_variable("CustomOutputName_Python", 2)
    assert isinstance(var, str)

    var = mc.get_array_variable("CustomOutputEnabled_Python", 2)
    assert isinstance(var, bool)


def test_set_array_variable(mc):
    # Float
    mc.set_array_variable("Duty_Cycle_Time", 2, 30)
    var = mc.get_array_variable("Duty_Cycle_Time", 2)
    assert var == 30

    # String
    mc.set_array_variable("CustomOutputName_Python", 2, "test_name")
    var = mc.get_array_variable("CustomOutputName_Python", 2)
    assert var == "test_name"

    # Boolean
    mc.set_array_variable("CustomOutputEnabled_Python", 2, True)
    var = mc.get_array_variable("CustomOutputEnabled_Python", 2)
    assert var is True


def test_get_set_array_variable_2d(mc):
    test_value = 10

    save_value = mc.get_array_variable_2d("ConductorCentre_L_x", 2, 2)

    mc.set_array_variable_2d("ConductorCentre_L_x", 2, 2, test_value)

    var = mc.get_array_variable_2d("ConductorCentre_L_x", 2, 2)

    assert var == test_value

    mc.set_array_variable_2d("ConductorCentre_L_x", 2, 2, save_value)


def test_restore_compatibility_settings(mc):
    test_compatibility_setting = "EWdgAreaCalculation"
    original_method = 0
    improved_method = 1

    mc.set_variable(test_compatibility_setting, original_method)
    assert mc.get_variable(test_compatibility_setting) == original_method

    mc.restore_compatibility_settings()
    assert mc.get_variable(test_compatibility_setting) == improved_method
