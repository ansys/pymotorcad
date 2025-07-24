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

from os import path, remove

import pytest

from RPC_Test_Common import get_dir_path, reset_to_default_file
from ansys.motorcad.core import MotorCAD, MotorCADError, rpc_client_core


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


def test_get_file_name():
    mc = MotorCAD()

    file_path = get_dir_path() + r"\test_files\temp_files\Get_File_Name.mot"

    if path.exists(file_path):
        remove(file_path)

    assert path.exists(file_path) is False

    with pytest.warns():
        mc.get_file_name()

    mc.save_to_file(file_path)
    assert mc.get_file_name() == file_path
    remove(file_path)


def test_get_file_name_fallback():
    mc = MotorCAD()
    # Pretend to be an older version
    mc.connection.program_version = "2024.2.3.1"
    save_DONT_CHECK_MOTORCAD_VERSION = rpc_client_core.DONT_CHECK_MOTORCAD_VERSION
    rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = False

    try:
        file_path = get_dir_path() + r"\test_files\temp_files\Get_File_Name.mot"

        if path.exists(file_path):
            remove(file_path)

        assert path.exists(file_path) is False

        with pytest.warns():
            mc.get_file_name()

        mc.save_to_file(file_path)
        assert mc.get_file_name() == file_path
        remove(file_path)
    finally:
        rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = save_DONT_CHECK_MOTORCAD_VERSION


def test_get_datastore(mc):
    """Incomplete testing"""
    datastore = mc.get_datastore()

    test = datastore.get_variable("slot_width")
    test_rec = datastore.get_variable_record("test_int")

    test_array = datastore.get_variable("IMInductance_CurrentProp")
    test_array_2d = datastore.get_variable("ConductorCentre_L_x")

    test_array_ref = datastore.get_variable_record("IMInductance_CurrentProp").array_length_ref
    test_array_2d_ref = datastore.get_variable_record("ConductorCentre_L_x").array_length_ref_2d

    arrays = [
        datastore[item]
        for item in datastore
        if (datastore[item].is_array) and (datastore[item].dynamic)
    ]
    arrays_2d = [datastore[item] for item in datastore if datastore[item].is_array_2d]

    datastore.pop("slot_width")
    datastore.pop("test_int")
    filtered_output = datastore.filter_variables(file_sections=["SaturationMap"], inout_types=[0])
    datastore_json = datastore.to_json()
    datastore_dict = datastore.to_dict()
