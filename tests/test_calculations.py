# import os

from RPC_Test_Common import (  # get_temp_files_dir_path
    almost_equal,
    get_dir_path,
    reset_to_default_file,
)


def test_do_magnetic_thermal_calculation(mc):
    mc.do_magnetic_thermal_calculation()

    assert almost_equal(mc.get_variable("ArmatureConductor_Temperature"), 133.367)


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
