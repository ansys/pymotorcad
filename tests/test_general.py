import os

from RPC_Test_Common import almost_equal, get_dir_path, get_temp_files_dir_path
from ansys.motorcad.core import MotorCAD
from setup_test import reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def kh_to_ms(kh):
    return kh * 0.2777778


def test_save_load_clear_duty_cycle():
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


def test_export_matrices():
    mc.do_steady_state_analysis()

    mc.export_matrices(get_temp_files_dir_path())

    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.nmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.pmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.rmf")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file.tmf")


def test_load_fea_result():
    mc.show_magnetic_context()

    mc.load_fea_result(get_dir_path() + r"\test_files\TorqueSpeed_result_1_5.mes", 0)

    value, unit = mc.get_point_value("B", 61, -16)
    assert almost_equal(value, 1.505, 3)
    assert unit == "T"


def test_export_results():
    mc.do_steady_state_analysis()

    file_path = get_temp_files_dir_path() + r"\steady_state_result.csv"

    mc.export_results("SteadyState", file_path)

    assert os.path.exists(file_path)


def test_load_dxf_file():
    # Must currently open new Motor-CAD to ensure
    # this test will work
    # see issue #41
    mc2 = MotorCAD()

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

    region = mc2._get_region_properties_xy(x, y)

    # Can't currently access magnet properties except for material name
    # This needs improving in the future
    assert almost_equal(region["Area"], 129.3)

    mc2.quit()


def test_export_force_animation():
    mc.do_multi_force_calculation()

    file_path = get_temp_files_dir_path() + r"\test_animation.gif"
    mc.export_force_animation("Radial", file_path)


def test_load_template():
    mc.load_template("e5")

    # Check we have loaded IM motor
    assert mc.get_variable("Motor_Type") == 1

    reset_to_default_file(mc)


def test_export_multi_force_data():
    mc.do_multi_force_calculation()

    file_path = get_temp_files_dir_path() + r"\force_data.json"
    mc.export_multi_force_data(file_path)

    assert os.path.exists(file_path)


def test_geometry_export():
    file_path = get_temp_files_dir_path() + r"\dxf_export_file.dxf"
    mc.set_variable("DXFFileName", file_path)
    mc.geometry_export()

    assert os.path.exists(file_path)


def test_save_load_magnetisation_curves():
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


def test_save_load_results():
    mc.do_magnetic_calculation()
    mc.save_results("EMagnetic")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file\EMag\outputResults.mot")
    assert os.path.exists(get_temp_files_dir_path() + r"\temp_test_file\EMag\GraphResults.ini")

    mc.load_from_file(get_temp_files_dir_path() + r"\temp_test_file.mot")

    mc.load_results("EMagnetic")
    assert mc.get_variable("MaxTorque") != 0

    reset_to_default_file(mc)


def test_get_message():
    mc.show_message("test1")
    mc.show_message("test2")
    mc.show_message("test3")

    messages = mc.get_messages(3)
    assert "test1" in messages
    assert "test3" in messages
