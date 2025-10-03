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

import os

import pytest

from RPC_Test_Common import (
    almost_equal,
    get_base_test_file_path,
    get_dir_path,
    get_temp_files_dir_path,
    get_test_files_dir_path,
    reset_to_default_file,
)
import ansys.motorcad.core
from ansys.motorcad.core import MotorCAD, MotorCADError

# Allows us to add a new api method to testing before the next Motor-CAD release is available
# Dev release will have a lower version number than actual release so don't want to check this
ansys.motorcad.core.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = True


def kh_to_ms(kh):
    return kh * 0.2777778


def test_save_load_clear_duty_cycle(mc):
    # thermal transient calc
    mc.set_variable("ThermalCalcType", 1)

    # transient calc type - duty cycle
    mc.set_variable("TransientCalculationType", 1)

    assert almost_equal(
        mc.get_array_variable("Duty_Cycle_Vehicle_Speed_Start", 20), kh_to_ms(64.21)
    )

    save_path = get_temp_files_dir_path() + r"\duty_cycle.dat"
    mc.save_duty_cycle(save_path)

    mc.clear_duty_cycle()
    assert mc.get_variable("Duty_Cycle_Num_Periods") < 2

    mc.load_duty_cycle(save_path)
    assert almost_equal(
        mc.get_array_variable("Duty_Cycle_Vehicle_Speed_Start", 20), kh_to_ms(64.21)
    )

    # reset model state
    reset_to_default_file(mc)


def test_export_matrices(mc):
    mc.do_steady_state_analysis()

    mc.export_matrices(get_temp_files_dir_path())

    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.nmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.pmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.rmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.tmf")


def test_load_fea_result(mc):
    mc.show_magnetic_context()

    mc.load_fea_result(get_dir_path() + r"\test_files\TorqueSpeed_result_1_5.mes", 0)

    value, unit = mc.get_point_value("B", 61, -16)
    assert almost_equal(value, 1.505, 3)
    assert unit == "T"


def test_export_results(mc):
    mc.do_steady_state_analysis()

    file_path = get_temp_files_dir_path() + r"\steady_state_result.csv"

    mc.export_results("SteadyState", file_path)

    assert os.path.exists(file_path)


def test_load_dxf_file():
    # Must currently open new Motor-CAD to ensure
    # this test will work
    # see issue #41
    mc2 = MotorCAD()
    try:
        mc2.set_variable("MessageDisplayState", 2)

        x = 53
        y = 19

        reset_to_default_file(mc2)
        mc2.show_magnetic_context()

        mc2.clear_all_data()
        mc2.initiate_geometry_from_script()

        mc2.load_dxf_file(get_dir_path() + r"\test_files\dxf_import.dxf")

        mc2.add_region_xy(x, y, "test_region")

        mc2.create_optimised_mesh()

        # Not currently working - needs fixing in Motor-CAD

        # region = mc2._get_region_properties_xy(x, y)
        #
        # # Can't currently access magnet properties except for material name
        # # This needs improving in the future
        # assert almost_equal(region["Area"], 129.3)

    except Exception as e:
        raise e
    finally:
        mc2.quit()


def test_export_force_animation(mc):
    mc.do_multi_force_calculation()

    file_path = get_temp_files_dir_path() + r"\test_animation.gif"
    mc.export_force_animation("Radial", file_path)


def test_load_template(mc):
    mc.load_template("e5")

    # Check we have loaded IM motor
    assert mc.get_variable("Motor_Type") == 1

    reset_to_default_file(mc)


def test_export_multi_force_data(mc):
    mc.do_multi_force_calculation()

    file_path = get_temp_files_dir_path() + r"\force_data.json"
    mc.export_multi_force_data(file_path)

    assert os.path.exists(file_path)


def test_geometry_export(mc):
    file_path = get_temp_files_dir_path() + r"\dxf_export_file.dxf"
    mc.set_variable("DXFFileName", file_path)
    mc.geometry_export()

    assert os.path.exists(file_path)


def test_save_load_magnetisation_curves(mc):
    mc.load_from_file(get_dir_path() + r"\test_files\SRM_test_file.mot")
    mc.do_magnetic_calculation()

    file_path = get_temp_files_dir_path() + r"\mag_curves.txt"

    mc.save_magnetisation_curves(file_path)
    assert os.path.exists(file_path)

    mc.set_variable("MaxCurrent_MagnetisationCurves", 20)
    mc.do_magnetic_calculation()
    assert mc.get_variable("MaxCurrent_Calculated_MagnetisationCurves") == 20

    mc.load_magnetisation_curves(file_path)
    assert mc.get_variable("MaxCurrent_Calculated_MagnetisationCurves") == 5

    reset_to_default_file(mc)


def test_save_load_results(mc):
    # Currently not working as part of full tests
    # Works individually - need to look into this

    # EMag test
    mc.do_magnetic_calculation()
    mc.save_results("EMagnetic")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file\EMag\outputResults.mot")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file\EMag\GraphResults.ini")

    mc.load_from_file(get_temp_files_dir_path() + r"\temp_test_file.mot")

    mc.load_results("EMagnetic")
    assert mc.get_variable("MaxTorque") != 0

    reset_to_default_file(mc)

    # Thermal test - transient graphs only
    mc.do_transient_analysis()
    mc.save_results("Thermal")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file\Thermal\GraphResults.ini")

    mc.load_from_file(get_temp_files_dir_path() + r"\temp_test_file.mot")

    mc.load_results("TheRmal")
    assert mc.get_power_graph_point("Armature Copper(Total)", 5) != 0

    with pytest.raises(MotorCADError):
        mc.load_results("wrong_type")

    with pytest.raises(MotorCADError):
        mc.save_results("wrong_type")
    reset_to_default_file(mc)


def test_get_message(mc):
    mc.show_message("test1")
    mc.show_message("test2")
    mc.show_message("test3")

    messages = mc.get_messages(3)
    assert ("test1" in message for message in messages)
    assert ("test3" in message for message in messages)


def file_contents_equal(file_1, file_2):
    with open(file_1) as f1:
        with open(file_2) as f2:
            return f1.read() == f2.read()


def file_line_differences(file_1, file_2):
    number_differences = 0
    with open(file_1) as f1:
        with open(file_2) as f2:
            f1_contents = f1.readlines()
            f2_contents = f2.readlines()

            max_line = min(len(f1_contents), len(f2_contents))

            for line_number in range(max_line):
                if f1_contents[line_number] != f2_contents[line_number]:
                    number_differences += 1

    return number_differences


def test_download_mot_file(mc):
    # Load and save base file so that contents are updated for this version of Motor-CAD
    mc.load_from_file(get_base_test_file_path())
    save_file_path = get_temp_files_dir_path() + r"\base_test_file_copy.mot"
    mc.save_to_file(save_file_path)

    download_mot_file_path = get_temp_files_dir_path() + r"\download_test_file.mot"
    mc.download_mot_file(download_mot_file_path)

    # File contents should be identical since downloading file without modifying
    assert file_contents_equal(save_file_path, download_mot_file_path)
    reset_to_default_file(mc)


def test_upload_mot_file(mc):
    # Load and save base file so that contents are updated for this version of Motor-CAD
    mc.load_from_file(get_test_files_dir_path() + r"\IM_test_file.mot")
    save_file_path = get_temp_files_dir_path() + r"\IM_test_file_copy.mot"
    mc.save_to_file(save_file_path)

    IM_test_file_path = get_test_files_dir_path() + r"\IM_test_file.mot"
    mc.upload_mot_file(IM_test_file_path)

    upload_mot_file_path = get_temp_files_dir_path() + r"\upload_test_file.mot"
    mc.save_to_file(upload_mot_file_path)

    # File might have slight differences (paths etc.) since we are uploading and
    # saving as a new file
    assert file_line_differences(upload_mot_file_path, save_file_path) < 30
    reset_to_default_file(mc)


def test_save_load_custom_response(mc):
    # reset model state
    reset_to_default_file(mc)

    # set data
    mc.set_variable("CustomNVHFRFOrders", 2)
    mc.set_variable("CustomNVHFRFPoints", 3)

    mc.set_array_variable("CustomNVHFRFModeShape", 0, 0)
    mc.set_array_variable("CustomNVHFRFModeExcitation", 0, "R")

    mc.set_array_variable("CustomNVHFRFModeShape", 1, 0)
    mc.set_array_variable("CustomNVHFRFModeExcitation", 1, "T")

    # Frequencies
    mc.set_array_variable("CustomNVHFRFFrequencies", 0, 20)
    mc.set_array_variable("CustomNVHFRFFrequencies", 1, 100)
    mc.set_array_variable("CustomNVHFRFFrequencies", 2, 500)

    # FRF 0 Radial
    mc.set_array_variable_2d("CustomNVHFRFResponse", 0, 0, 0)
    mc.set_array_variable_2d("CustomNVHFRFResponse", 1, 0, 10)
    mc.set_array_variable_2d("CustomNVHFRFResponse", 2, 0, 20)

    # FRF 0 Tangential
    mc.set_array_variable_2d("CustomNVHFRFResponse", 0, 1, 40)
    mc.set_array_variable_2d("CustomNVHFRFResponse", 1, 1, 60)
    mc.set_array_variable_2d("CustomNVHFRFResponse", 2, 1, 80)

    file_path = get_dir_path() + r"\test_files\SaveLoadNVHResponse.txt"
    if os.path.exists(file_path):
        os.remove(file_path)

    # save to file, clear and re-load
    mc.save_nvh_custom_response(file_path)
    reset_to_default_file(mc)
    mc.load_nvh_custom_response(file_path)

    assert mc.get_array_variable_2d("CustomNVHFRFResponse", 2, 1) == 80
    assert mc.get_array_variable("CustomNVHFRFModeShape", 1) == 0
    assert mc.get_array_variable("CustomNVHFRFModeExcitation", 1) == "T"
