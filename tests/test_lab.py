# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

from RPC_Test_Common import reset_to_default_file


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
