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

# import os

from RPC_Test_Common import almost_equal, almost_equal_fixed, get_dir_path


def test_do_magnetic_thermal_calculation(mc):
    mc.do_magnetic_thermal_calculation()

    assert almost_equal_fixed(mc.get_variable("ArmatureConductor_Temperature"), 134, 10)


# def test_calculate_saturation_map():
#     file_path = get_temp_files_dir_path() + r"\SaturationLossMap.mat"
#     mc.set_variable("SaturationMap_ExportFile", file_path)
#     mc.calculate_saturation_map()
#
#     assert os.path.exists(file_path)


def test_do_transient_analysis(mc):
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_temperature_graph_point("Housing [Active]", 4)

    assert almost_equal(x, 16)
    assert almost_equal(y, 47.7438)

    # Duty cycle
    mc.set_variable("TransientCalculationType", 1)


# Not sure how to fully test these functions
# Check for exceptions for now


def test_do_mechanical_calculation(mc):
    mc.do_mechanical_calculation()


def test_calculate_im_saturation_model(mc):
    mc.load_from_file(get_dir_path() + r"\test_files\IM_test_file.mot")

    mc.calculate_im_saturation_model()

    reset_to_default_file(mc)


def test_calculate_force_harmonics_spatial(mc):
    mc.calculate_force_harmonics_spatial()


def test_calculate_force_harmonics_temporal(mc):
    mc.calculate_force_harmonics_temporal()


def test_do_weight_calculation(mc):
    mc.do_weight_calculation()


def test_create_winding_pattern(mc):
    # Copper solot fill definition so changing strands in hand will change wire diameter
    wire_diameter = mc.get_variable("Wire_Diameter")
    strands = mc.get_variable("NumberStrandsHand")

    mc.set_variable("NumberStrandsHand", strands - 1)
    # winding not updated yet
    assert mc.get_variable("Wire_Diameter") == wire_diameter

    mc.create_winding_pattern()
    # less strands in hand -> larger wire diameter
    assert mc.get_variable("Wire_Diameter") > wire_diameter

    # Reset model
    mc.set_variable("NumberStrandsHand", strands)
    mc.create_winding_pattern()
