# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

from RPC_Test_Common import almost_equal, get_dir_path
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


def test_get_solid_database(mc):
    solid_db = mc._get_solid_database()
    assert len(solid_db) > 0

    if len(solid_db) > 0:
        assert solid_db[0]["Name"] != ""


def test_select_material_database(mc_reset_to_default_on_teardown):
    mc_reset_to_default_on_teardown.select_material_database(
        get_dir_path() + r"\test_files\Arnold_Neodymium.mdb", False
    )

    solid_db = mc_reset_to_default_on_teardown._get_solid_database()
    assert solid_db[0]["Name"] == "N28AH"
