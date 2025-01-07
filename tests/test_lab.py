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
import time

import pytest

from RPC_Test_Common import get_dir_path, reset_to_default_file


def test_model_build_lab(mc):
    reset_to_default_file(mc)

    # base test file includes built model
    assert mc.get_model_built_lab() is True

    mc.clear_model_build_lab()
    assert mc.get_model_built_lab() is False

    mc.build_model_lab()
    assert mc.get_model_built_lab() is True


def test_calculate_test_performance_lab(mc):
    mc.calculate_test_performance_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_export_duty_cycle_lab(mc):
    # Automotive cycle
    mc.set_variable("DutyCycleType_Lab", 1)
    # EUDC cycle
    mc.set_variable("DrivCycle_MotorLab", 4)

    mc.calculate_duty_cycle_lab()

    mc.export_duty_cycle_lab()

    # Check losses transferred
    assert mc.get_array_variable("Duty_Cycle_Armature_Copper_Loss_DC", 50) != 0


def test_calculate_operating_point_lab(mc):
    mc.calculate_operating_point_lab()

    assert mc.get_variable("LabOpPoint_ShaftTorque") != 0


def test_calculate_magnetic_lab(mc):
    mc.calculate_magnetic_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_thermal_lab(mc):
    mc.calculate_thermal_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_internal_custom_loss_functions(mc):
    no_internal_losses = mc.get_variable("NumCustomLossesInternal_Lab")
    name = "Stator iron Loss Connection"
    power_loss_function = (
        "Speed**2 * (5.4E-9 * Iron_Loss_Stator - 1.7E-5 * Iron_Loss_Stator**2 + 1.43)"
    )
    type = "Electrical"
    incorrect_type = "Type"
    thermal_node = 2
    incorrect_thermal_node = -2
    removed_name = "Bearing Connection"
    removed_power_loss_function = "1E-2 * Mechanical_Loss **2) * Speed / 10000 + min(5, Speed)"
    removed_type = "Mechanical"
    removed_thermal_node = 4

    mc.add_internal_custom_loss(name, power_loss_function, type, thermal_node)
    mc.add_internal_custom_loss(
        removed_name, removed_power_loss_function, removed_type, removed_thermal_node
    )

    assert mc.get_variable("NumCustomLossesInternal_Lab") == no_internal_losses + 2
    assert mc.get_array_variable("CustomLoss_name_internal_lab", no_internal_losses) == name
    assert (
        mc.get_array_variable("CustomLoss_Function_Internal_Lab", no_internal_losses)
        == power_loss_function
    )
    assert mc.get_array_variable("CustomLoss_Type_Internal_Lab", no_internal_losses) == type
    assert (
        mc.get_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_internal_losses)
        == thermal_node
    )
    assert (
        mc.get_array_variable("CustomLoss_name_internal_lab", no_internal_losses + 1)
        == removed_name
    )
    assert (
        mc.get_array_variable("CustomLoss_Function_Internal_Lab", no_internal_losses + 1)
        == removed_power_loss_function
    )
    assert (
        mc.get_array_variable("CustomLoss_Type_Internal_Lab", no_internal_losses + 1)
        == removed_type
    )
    assert (
        mc.get_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_internal_losses + 1)
        == removed_thermal_node
    )

    mc.remove_internal_custom_loss(removed_name)
    assert mc.get_variable("NumCustomLossesInternal_Lab") == no_internal_losses + 1

    with pytest.raises(ValueError):
        mc.add_internal_custom_loss(name, power_loss_function, incorrect_type, thermal_node)

    with pytest.raises(ValueError):
        mc.add_internal_custom_loss(name, power_loss_function, type, incorrect_thermal_node)


def test_external_custom_loss_functions(mc):
    no_external_losses = mc.get_variable("NumCustomLossesExternal_Lab")
    name = "Battery Loss"
    power_loss_function = "(1E-2 * Mechanical_Loss**2) * Speed/10000 + min(5, Speed)"
    voltage_drop_function = "Idc * 2.5E-2"
    removed_name = "DC Harness Loss"
    removed_power_loss_function = "Idc**2 * 1E-2"
    removed_voltage_drop_function = "Idc * 2.5E-2"

    mc.add_external_custom_loss(
        removed_name, removed_power_loss_function, removed_voltage_drop_function
    )
    mc.add_external_custom_loss(name, power_loss_function, voltage_drop_function)

    assert mc.get_variable("NumCustomLossesExternal_Lab") == no_external_losses + 2
    assert mc.get_array_variable("CustomLoss_Name_External_Lab", no_external_losses) == removed_name
    assert (
        mc.get_array_variable("CustomLoss_PowerFunction_External_Lab", no_external_losses)
        == removed_power_loss_function
    )
    assert (
        mc.get_array_variable("CustomLoss_VoltageFunction_External_Lab", no_external_losses)
        == removed_voltage_drop_function
    )
    assert mc.get_array_variable("CustomLoss_Name_External_Lab", no_external_losses + 1) == name
    assert (
        mc.get_array_variable("CustomLoss_PowerFunction_External_Lab", no_external_losses + 1)
        == power_loss_function
    )
    assert (
        mc.get_array_variable("CustomLoss_VoltageFunction_External_Lab", no_external_losses + 1)
        == voltage_drop_function
    )

    mc.remove_external_custom_loss(removed_name)
    assert mc.get_variable("NumCustomLossesExternal_Lab") == no_external_losses + 1


def test_lab_model_export(mc):
    mc.set_variable("MessageDisplayState", 2)
    file_path = get_dir_path() + r"\test_files\temp_files\lab_model_export.lab"

    mc.load_template("e3")

    if path.exists(file_path):
        remove(file_path)

    assert path.exists(file_path) is False

    mc.export_lab_model(file_path)

    # Exporting the lab model takes a few seconds and so a delay is required before
    # asserting the .lab file is present.
    checks = 0

    while checks < 60:
        time.sleep(1)
        if path.exists(file_path) is False:
            checks += 1
        else:
            break

    assert path.exists(file_path) is True

    remove(file_path)

    # Checks that a warning is raised if the model build speed has changed
    mc.set_variable("LabModel_Saturation_StatorCurrent_Peak", 750)

    with pytest.raises(Exception) as stator_current_changed_error:
        mc.export_lab_model(file_path)

    assert "maximum current has changed" in str(stator_current_changed_error)

    # Clears lab model and checks a warning has been raised
    mc.clear_model_build_lab()

    with pytest.raises(Exception) as model_not_built_error:
        mc.export_lab_model(file_path)

    assert "model has not been built" in str(model_not_built_error)

    reset_to_default_file(mc)
