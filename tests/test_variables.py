import pytest

from ansys.motorcad.core import MotorCADError
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_get_variable():
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


def test_set_variable():
    # Standard call and check var has been set
    # Might be better to move this to some longer test sequences
    # Can specify order of tests so can run sequences after short tests
    mc.SetVariable("tooth_width", 10)
    tooth_width = mc.get_variable("tooth_width")
    assert tooth_width == 10

    # wrong variable name
    with pytest.raises(Exception):
        mc.SetVariable("Not_a_real_variable", 10)

    # bool type
    mc.SetVariable("TorqueSpeedCalculation", True)
    assert mc.get_variable("TorqueSpeedCalculation") == True

    mc.SetVariable("Discovery_FileName", "test")
    assert mc.get_variable("Discovery_FileName") == "test"


def test_get_array_variable():
    var = mc.GetArrayVariable("Duty_Cycle_Time", 2)
    assert isinstance(var, int)

    var = mc.GetArrayVariable("CustomOutputName_Python", 2)
    assert isinstance(var, str)

    var = mc.GetArrayVariable("CustomOutputEnabled_Python", 2)
    assert isinstance(var, bool)


def test_set_array_variable():
    # Float
    mc.SetArrayVariable("Duty_Cycle_Time", 2, 30)
    var = mc.GetArrayVariable("Duty_Cycle_Time", 2)
    assert var == 30

    # String
    mc.SetArrayVariable("CustomOutputName_Python", 2, "test_name")
    var = mc.GetArrayVariable("CustomOutputName_Python", 2)
    assert var == "test_name"

    # Boolean
    mc.SetArrayVariable("CustomOutputEnabled_Python", 2, True)
    var = mc.GetArrayVariable("CustomOutputEnabled_Python", 2)
    assert var is True
