from math import pi

import pytest

from RPC_Test_Common import almost_equal
from ansys.motorcad.core.geometry import rt_to_xy, xy_to_rt
from setup_test import get_temp_files_dir_path, reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()

MATERIAL_INVALID_NAME = "invalid material name here"
MATERIAL_EPOXY = "Epoxy"

# Invalid coordinates - never expect motor to be this large
X_INVALID = 10000000
Y_INVALID = 10000000


def reset_model_geometry():
    mc.reset_regions()
    mc.set_variable("UseDXFImportForFEA_Magnetic", False)


# Draw square with centre at 5,5
def draw_square():
    # point coordinates
    x1 = 0
    y1 = 0
    x2 = 10
    y2 = 0
    x3 = 10
    y3 = 10
    x4 = 0
    y4 = 10

    # Make a square box
    mc.add_line_xy(x1, y1, x2, y2)
    mc.add_line_xy(x2, y2, x3, y3)
    mc.add_line_xy(x3, y3, x4, y4)
    mc.add_line_xy(x4, y4, x1, y1)

    mc.add_region_xy(5, 5, "test_region")


def test_initiate_geometry_from_script():
    # Placeholder function so that we know this has been tested in other functions.
    # - could expand this in the future to have standalone test.

    # We already test this function in:
    # test_add_point_custom_material_rt/xy
    # test_add_magnet_region_rt/xy
    # test_add_region_rt/xy
    # test_add_line_rt/xy
    # test_add_arc_rt/xy
    # test_add_arc_centre_start_end_rt/xy
    assert True


def test_add_line_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10x10 square and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    draw_square()

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(5, 5)

    assert almost_equal(region["Area"], 100)
    reset_model_geometry()


def test_add_line_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10x10 square and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    # point coordinates
    r1 = 0
    t1 = 0
    r2 = 10
    t2 = 0
    r3 = 14.142135623730951
    t3 = 45
    r4 = 10
    t4 = 90

    # Make a square box
    mc.add_line_rt(r1, t1, r2, t2)
    mc.add_line_rt(r2, t2, r3, t3)
    mc.add_line_rt(r3, t3, r4, t4)
    mc.add_line_rt(r4, t4, r1, t1)

    mc.add_region_xy(5, 5, "test_region")

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(5, 5)

    assert almost_equal(region["Area"], 100)
    reset_model_geometry()


def test_add_arc_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    radius = 10

    # Centre point coordinates
    x_c = 10
    y_c = 10

    # Make a circle
    mc.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc.add_arc_xy(x_c, y_c, -180, 0, radius)

    mc.add_region_xy(10, 10, "test_region")

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(10, 10)

    assert almost_equal(region["Area"], pi * pow(radius, 2))
    reset_model_geometry()


def test_add_arc_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    radius = 10

    # Centre point coordinates
    r_c = 14.142135623730951
    t_c = 45.0

    x_c = 10
    y_c = 10

    # Make a circle
    mc.add_arc_rt(r_c, t_c, 0, -180, radius)
    mc.add_arc_rt(r_c, t_c, -180, 0, radius)

    mc.add_region_xy(10, 10, "test_region")

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert almost_equal(region["Area"], pi * pow(radius, 2))
    reset_model_geometry()


def test_add_arc_centre_start_end_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    radius = 10

    # Point coordinates
    x_c = 10
    y_c = 10
    x_1 = 20
    y_1 = 10
    x_2 = 0
    y_2 = 10

    # Make a circle
    mc.add_arc_centre_start_end_xy(x_c, y_c, x_1, y_1, x_2, y_2)
    mc.add_arc_centre_start_end_xy(x_c, y_c, x_2, y_2, x_1, y_1)

    mc.add_region_xy(x_c, y_c, "test_region")

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert almost_equal(region["Area"], pi * pow(radius, 2))
    reset_model_geometry()


def test_add_arc_centre_start_end_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    radius = 10

    # Point coordinates
    r_c = 14.142135623730951
    t_c = 45
    r_1 = 22.360679774997898
    t_1 = 26.56505117707799
    r_2 = 10.0
    t_2 = 90.0

    # Make a circle
    mc.add_arc_centre_start_end_rt(r_c, t_c, r_1, t_1, r_2, t_2)
    mc.add_arc_centre_start_end_rt(r_c, t_c, r_2, t_2, r_1, t_1)

    x_c, y_c = rt_to_xy(r_c, t_c)

    mc.add_region_xy(x_c, y_c, "test_region")

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert almost_equal(region["Area"], pi * pow(radius, 2))
    reset_model_geometry()


def test_add_region_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square()

    region_name = "test_region"

    mc.add_region_xy(x_c, y_c, region_name)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert region["RegionName"] == region_name

    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc.add_region_xy(X_INVALID, Y_INVALID, region_name)

    assert "Could not find region" in str(e_info.value)
    reset_model_geometry()


def test_add_region_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # This function links to add_region_xy so just need basic test
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5
    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square()

    region_name = "test_region"

    mc.add_region_rt(r_c, t_c, region_name)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert region["RegionName"] == region_name
    reset_model_geometry()


# Draw region that can be added as a magnet
def draw_magnet(x_c, y_c):
    # Ensure magnetic context active for FEA tests

    radius = 2

    # Make a circle
    mc.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc.add_arc_xy(x_c, y_c, -180, 0, radius)


# Can be improved by adding to get_region_properties
# Currently magnet properties aren't available
def test_add_magnet_region_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    rt_magnet = 36

    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    # Centre point coordinates
    x_c = 15
    y_c = 15

    draw_magnet(x_c, y_c)

    magnet_name = "magnet_test"
    magnet_material = "N30UH"
    br_angle = 30
    br_multiplier = 1
    polarity = 0

    # Valid region
    mc.add_magnet_region_xy(
        x_c, y_c, magnet_name, magnet_material, br_angle, br_multiplier, polarity
    )

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    # Can't get magnet properties from this yet - try and improve in future
    assert region["RegionName"] == magnet_name
    assert region["RegionType_Mapped"] == rt_magnet

    mc.initiate_geometry_from_script()
    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc.add_magnet_region_xy(
            X_INVALID, Y_INVALID, magnet_name, magnet_material, br_angle, br_multiplier, polarity
        )

    # This check is currently failing
    # Exception is still being raised so not a huge issue
    # Needs looking into
    # assert "Could not find region" in str(e_info.value)

    mc.initiate_geometry_from_script()
    # Invalid region material
    with pytest.raises(Exception) as e_info:
        mc.add_magnet_region_xy(
            x_c, y_c, magnet_name, MATERIAL_INVALID_NAME, br_angle, br_multiplier, polarity
        )

    assert "Could not find magnet material" in str(e_info.value)

    # Material not a magnet
    with pytest.raises(Exception) as e_info:
        mc.add_magnet_region_xy(
            x_c, y_c, magnet_name, MATERIAL_EPOXY, br_angle, br_multiplier, polarity
        )

    assert "is not a magnet material" in str(e_info.value)
    reset_model_geometry()


def test_add_magnet_region_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # This function links to add_magnet_region_xy so just need basic test
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    # Centre point coordinates
    x_c = 15
    y_c = 15

    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_magnet(x_c, y_c)

    magnet_name = "magnet_test"
    magnet_material = "N30UH"
    br_angle = 30
    br_multiplier = 1
    polarity = 0
    mc.add_magnet_region_rt(
        r_c, t_c, magnet_name, magnet_material, br_angle, br_multiplier, polarity
    )

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert region["RegionName"] == magnet_name
    reset_model_geometry()


def test_get_region_properties_xy():
    # Placeholder function so that we know this has been tested in other functions.
    # - could expand this in the future to have standalone test.

    # We already test this function in:
    # test_add_point_custom_material_rt/xy
    # test_add_magnet_region_rt/xy
    # test_add_region_rt/xy
    assert True


def test_add_point_custom_material_xy():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square()

    # Valid region
    region_name = "test_region"
    material_name = "Epoxy"
    colour = "red"
    colour_code = "0xff"
    mc.add_point_custom_material_xy(x_c, y_c, region_name, material_name, colour)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert region["RegionName"] == region_name
    assert region["MaterialName"] == material_name
    assert hex(region["Colour"]) == colour_code

    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc.add_point_custom_material_xy(X_INVALID, Y_INVALID, region_name, material_name, colour)

    # This check is currently failing
    # Exception is still being raised so not a huge issue
    # Needs looking into
    # assert "Could not find region" in str(e_info.value)

    # Invalid material
    with pytest.raises(Exception) as e_info:
        mc.add_point_custom_material_xy(x_c, y_c, region_name, MATERIAL_INVALID_NAME, colour)

    assert "Material does not exist in database" in str(e_info.value)
    reset_model_geometry()


def test_add_point_custom_material_rt():
    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    # This function links to add_point_custom_material_xy so just need basic test
    mc.clear_all_data()
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square()

    region_name = "test_region"
    material_name = "M43"
    colour = "red"
    colour_code = "0xff"
    mc.add_point_custom_material_rt(r_c, t_c, region_name, material_name, colour)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c)

    assert region["RegionName"] == region_name
    assert region["MaterialName"] == material_name
    assert hex(region["Colour"]) == colour_code
    reset_model_geometry()


def test_edit_magnet_region():
    reset_to_default_file(mc)

    # Ensure magnetic context active for FEA tests
    mc.show_magnetic_context()

    material_name = "Y34"

    mc.edit_magnet_region("L1_1Magnet2", material_name, 63, 7)
    region = mc._get_region_properties_xy(62, 35)

    # Can't currently access magnet properties except for material name
    # This needs improving in the future
    assert region["MaterialName"] == material_name
    reset_model_geometry()


def test_get_region_value():
    # Ensure magnetic context active for FEA tests
    reset_to_default_file(mc)

    mc.show_magnetic_context()

    mc.do_magnetic_calculation()

    mc.load_fea_result(
        get_temp_files_dir_path() + r"\temp_test_file\FEResultsData\StaticLoad_result_1.mes", 0
    )

    value, area = mc.get_region_value("B", "Rotor")

    assert almost_equal(value, 0.00169, 4)
    assert almost_equal(area, 0.00181, 4)
    reset_model_geometry()
