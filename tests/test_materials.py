import pytest

from RPC_Test_Common import almost_equal
from ansys.motorcad.core import MotorCADError


def test_set_get_component_material(mc):
    mc.set_component_material("Shaft [Active]", "Stainless Steel 302")
    material = mc.get_component_material("Shaft [Active]")
    assert material == "Stainless Steel 302"

    with pytest.raises(MotorCADError):
        material = mc.get_component_material("Not a component")

    # This test currently fails - need to check if materials are real
    # issue #43
    # with pytest.raises(MotorCADError):
    #     mc.set_component_material("Shaft [Active]", "Not a material")


def test_set_fluid(mc):
    mc.set_fluid("WetRotorFluid", "Engine Oil (Unused)")
    assert almost_equal(mc.get_variable("Wet_Rotor_Fluid_Dynamic_Viscosity"), 0.2103, 4)
