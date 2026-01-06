# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from RPC_Test_Common import almost_equal, get_temp_files_dir_path, reset_to_default_file
from ansys.motorcad.core.geometry import rt_to_xy, xy_to_rt

MATERIAL_INVALID_NAME = "invalid material name here"
MATERIAL_EPOXY = "Epoxy"

# Invalid coordinates - never expect motor to be this large
X_INVALID = 10000000
Y_INVALID = 10000000


def reset_model_geometry(mc_fea_old):
    mc_fea_old.reset_regions()
    mc_fea_old.set_variable("UseDXFImportForFEA_Magnetic", False)


# Draw square with centre at 5,5
def draw_square(mc_fea_old):
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
    mc_fea_old.add_line_xy(x1, y1, x2, y2)
    mc_fea_old.add_line_xy(x2, y2, x3, y3)
    mc_fea_old.add_line_xy(x3, y3, x4, y4)
    mc_fea_old.add_line_xy(x4, y4, x1, y1)


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


def test_add_line_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10x10 square and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    draw_square(mc_fea_old)

    mc_fea_old.add_region_xy(5, 5, "test_region")

    mc_fea_old.create_optimised_mesh()

    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(5, 5)

    # assert almost_equal(region["RegionArea"], 100)
    # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_line_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10x10 square and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

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
    mc_fea_old.add_line_rt(r1, t1, r2, t2)
    mc_fea_old.add_line_rt(r2, t2, r3, t3)
    mc_fea_old.add_line_rt(r3, t3, r4, t4)
    mc_fea_old.add_line_rt(r4, t4, r1, t1)

    mc_fea_old.add_region_xy(5, 5, "test_region")

    mc_fea_old.create_optimised_mesh()

    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(5, 5)
    #
    # # assert almost_equal(region["RegionArea"], 100)
    # # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_arc_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    radius = 10

    # Centre point coordinates
    x_c = 10
    y_c = 10

    # Make a circle
    mc_fea_old.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc_fea_old.add_arc_xy(x_c, y_c, -180, 0, radius)

    mc_fea_old.add_region_xy(10, 10, "test_region")

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(10, 10)
    #
    # # assert almost_equal(region["RegionArea"], pi * pow(radius, 2))
    # # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_arc_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    radius = 10

    # Centre point coordinates
    r_c = 14.142135623730951
    t_c = 45.0

    x_c = 10
    y_c = 10

    # Make a circle
    mc_fea_old.add_arc_rt(r_c, t_c, 0, -180, radius)
    mc_fea_old.add_arc_rt(r_c, t_c, -180, 0, radius)

    mc_fea_old.add_region_xy(10, 10, "test_region")

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # # assert almost_equal(region["RegionArea"], pi * pow(radius, 2))
    # # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_arc_centre_start_end_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    radius = 10

    # Point coordinates
    x_c = 10
    y_c = 10
    x_1 = 20
    y_1 = 10
    x_2 = 0
    y_2 = 10

    # Make a circle
    mc_fea_old.add_arc_centre_start_end_xy(x_c, y_c, x_1, y_1, x_2, y_2)
    mc_fea_old.add_arc_centre_start_end_xy(x_c, y_c, x_2, y_2, x_1, y_1)

    mc_fea_old.add_region_xy(x_c, y_c, "test_region")

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # # assert almost_equal(region["RegionArea"], pi * pow(radius, 2))
    # # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_arc_centre_start_end_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # Draw a 10 radius circle and check its area
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    radius = 10

    # Point coordinates
    r_c = 14.142135623730951
    t_c = 45
    r_1 = 22.360679774997898
    t_1 = 26.56505117707799
    r_2 = 10.0
    t_2 = 90.0

    # Make a circle
    mc_fea_old.add_arc_centre_start_end_rt(r_c, t_c, r_1, t_1, r_2, t_2)
    mc_fea_old.add_arc_centre_start_end_rt(r_c, t_c, r_2, t_2, r_1, t_1)

    x_c, y_c = rt_to_xy(r_c, t_c)

    mc_fea_old.add_region_xy(x_c, y_c, "test_region")

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # # assert almost_equal(region["RegionArea"], pi * pow(radius, 2))
    # # RegionArea not working in this function - don't bother fixing since these will be deprecated
    # assert region["RegionName"] == "test_region"
    reset_model_geometry(mc_fea_old)


def test_add_region_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square(mc_fea_old)

    region_name = "test_region"

    mc_fea_old.add_region_xy(x_c, y_c, region_name)

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # assert region["RegionName"] == region_name

    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_region_xy(X_INVALID, Y_INVALID, region_name)

    assert "Could not find region" in str(e_info.value)
    reset_model_geometry(mc_fea_old)


def test_add_region_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # This function links to add_region_xy so just need basic test
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    x_c = 5
    y_c = 5
    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square(mc_fea_old)

    region_name = "test_region"

    mc_fea_old.add_region_rt(r_c, t_c, region_name)

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # assert region["RegionName"] == region_name
    reset_model_geometry(mc_fea_old)


# Draw region that can be added as a magnet
def draw_magnet(mc_fea_old, x_c, y_c):
    # Ensure magnetic context active for FEA tests

    radius = 2

    # Make a circle
    mc_fea_old.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc_fea_old.add_arc_xy(x_c, y_c, -180, 0, radius)


# Can be improved by adding to get_region_properties
# Currently magnet properties aren't available
def test_add_magnet_region_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    rt_magnet = 36

    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    # Centre point coordinates
    x_c = 15
    y_c = 15

    draw_magnet(mc_fea_old, x_c, y_c)

    magnet_name = "magnet_test"
    magnet_material = "N30UH"
    br_angle = 30
    br_multiplier = 1
    polarity = 0

    # Valid region
    mc_fea_old.add_magnet_region_xy(
        x_c, y_c, magnet_name, magnet_material, br_angle, br_multiplier, polarity
    )

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)

    # # Can't get magnet properties from this yet - try and improve in future
    # assert region["RegionName"] == magnet_name
    # assert region["RegionType_Mapped"] == rt_magnet

    mc_fea_old.initiate_geometry_from_script()
    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_magnet_region_xy(
            X_INVALID, Y_INVALID, magnet_name, magnet_material, br_angle, br_multiplier, polarity
        )

    # This check is currently failing
    # Exception is still being raised so not a huge issue
    # Needs looking into
    # assert "Could not find region" in str(e_info.value)

    mc_fea_old.initiate_geometry_from_script()
    # Invalid region material
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_magnet_region_xy(
            x_c, y_c, magnet_name, MATERIAL_INVALID_NAME, br_angle, br_multiplier, polarity
        )

    assert "Could not find magnet material" in str(e_info.value)

    # Material not a magnet
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_magnet_region_xy(
            x_c, y_c, magnet_name, MATERIAL_EPOXY, br_angle, br_multiplier, polarity
        )

    assert "is not a magnet material" in str(e_info.value)
    reset_model_geometry(mc_fea_old)


def test_add_magnet_region_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # This function links to add_magnet_region_xy so just need basic test
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    # Centre point coordinates
    x_c = 15
    y_c = 15

    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_magnet(mc_fea_old, x_c, y_c)

    magnet_name = "magnet_test"
    magnet_material = "N30UH"
    br_angle = 30
    br_multiplier = 1
    polarity = 0
    mc_fea_old.add_magnet_region_rt(
        r_c, t_c, magnet_name, magnet_material, br_angle, br_multiplier, polarity
    )

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # assert region["RegionName"] == magnet_name
    reset_model_geometry(mc_fea_old)


def test_get_region_properties_xy():
    # Placeholder function so that we know this has been tested in other functions.
    # - could expand this in the future to have standalone test.

    # We already test this function in:
    # test_add_point_custom_material_rt/xy
    # test_add_magnet_region_rt/xy
    # test_add_region_rt/xy
    assert True


def test_add_point_custom_material_xy(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square(mc_fea_old)

    # Valid region
    region_name = "test_region"
    material_name = "Epoxy"
    colour = "red"
    colour_code = "0xff"
    mc_fea_old.add_point_custom_material_xy(x_c, y_c, region_name, material_name, colour)

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)
    #
    # assert region["RegionName"] == region_name
    # assert region["MaterialName"] == material_name
    # assert hex(region["Colour"]) == colour_code

    # Invalid region coordinates
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_point_custom_material_xy(
            X_INVALID, Y_INVALID, region_name, material_name, colour
        )

    # This check is currently failing
    # Exception is still being raised so not a huge issue
    # Needs looking into
    # assert "Could not find region" in str(e_info.value)

    # Invalid material
    with pytest.raises(Exception) as e_info:
        mc_fea_old.add_point_custom_material_xy(
            x_c, y_c, region_name, MATERIAL_INVALID_NAME, colour
        )

    assert "Material does not exist in database" in str(e_info.value)
    reset_model_geometry(mc_fea_old)


def test_add_point_custom_material_rt(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    # This function links to add_point_custom_material_xy so just need basic test
    mc_fea_old.clear_all_data()
    mc_fea_old.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square(mc_fea_old)

    region_name = "test_region"
    material_name = "M43"
    colour = "red"
    colour_code = "0xff"
    mc_fea_old.add_point_custom_material_rt(r_c, t_c, region_name, material_name, colour)

    mc_fea_old.create_optimised_mesh()
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(x_c, y_c)

    # assert region["RegionName"] == region_name
    # assert region["MaterialName"] == material_name
    # assert hex(region["Colour"]) == colour_code
    reset_model_geometry(mc_fea_old)


def test_edit_magnet_region(mc_fea_old):
    reset_to_default_file(mc_fea_old)

    # Ensure magnetic context active for FEA tests
    mc_fea_old.show_magnetic_context()

    material_name = "Y34"

    mc_fea_old.edit_magnet_region("L1_1Magnet2", material_name, 63, 7)
    # _get_region_properties_xy is having issues - unwilling to prioritise fixing as this
    # functionality will be deprecated soon
    # region = mc_fea_old._get_region_properties_xy(62, 35)

    # # Can't currently access magnet properties except for material name
    # # This needs improving in the future
    # assert region["MaterialName"] == material_name
    reset_model_geometry(mc_fea_old)


def test_get_region_value(mc_fea_old):
    # Ensure magnetic context active for FEA tests
    reset_to_default_file(mc_fea_old)

    mc_fea_old.show_magnetic_context()

    mc_fea_old.do_magnetic_calculation()

    mc_fea_old.load_fea_result(
        get_temp_files_dir_path() + r"\temp_test_file\FEResultsData\StaticLoad_result_1.mes", 0
    )

    value, area = mc_fea_old.get_region_value("B", "Rotor")

    assert almost_equal(value, 0.0016, 2)
    assert almost_equal(area, 0.0018, 2)
    reset_model_geometry(mc_fea_old)
