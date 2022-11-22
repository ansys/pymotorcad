from math import pi

from ansys.motorcad.core.geometry import rt_to_xy, xy_to_rt
from tests.RPC_Test_Common import almost_equal
from tests.setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()

DXF_IMPORT_REGION = "DXF Import"


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


def test_initiate_geometry_from_script():
    # Tested in other geometry functions
    assert True


def test_add_line_xy():
    # Draw a 10x10 square and check its area
    mc.initiate_geometry_from_script()

    draw_square()

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(5, 5, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], 100)


def test_add_line_rt():
    # Draw a 10x10 square and check its area
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

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(5, 5, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], 100)


def test_add_arc_xy():
    # Draw a 10 radius circle and check its area
    mc.initiate_geometry_from_script()

    radius = 10

    # Centre point coordinates
    x_c = 10
    y_c = 10

    # Make a circle
    mc.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc.add_arc_xy(x_c, y_c, -180, 0, radius)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(10, 10, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], pi * pow(radius, 2))


def test_add_arc_rt():
    # Draw a 10 radius circle and check its area
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

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], pi * pow(radius, 2))


def test_add_arc_centre_start_end_xy():
    # Draw a 10 radius circle and check its area
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

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], pi * pow(radius, 2))


def test_add_arc_centre_start_end_rt():
    # Draw a 10 radius circle and check its area
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

    mc.create_optimised_mesh()

    x_c, y_c = rt_to_xy(r_c, t_c)

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert almost_equal(region["Area"], pi * pow(radius, 2))


def test_add_region_xy():
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square()

    region_name = "test_region"

    mc.add_region_xy(x_c, y_c, region_name)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == region_name


def test_add_region_rt():
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5
    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square()

    region_name = "test_region"

    mc.add_region_rt(r_c, t_c, region_name)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == region_name


# Draw region that can be added as a magnet
def draw_magnet(x_c, y_c):
    radius = 2

    # Make a circle
    mc.add_arc_xy(x_c, y_c, 0, -180, radius)
    mc.add_arc_xy(x_c, y_c, -180, 0, radius)


# Can be improved by adding to get_region_properties
# Currently magnet properties aren't available
def test_add_magnet_region_xy():
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
    mc.add_magnet_region_xy(
        x_c, y_c, magnet_name, magnet_material, br_angle, br_multiplier, polarity
    )

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == magnet_name


def test_add_magnet_region_rt():
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

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == magnet_name


def test_get_region_properties_xy():
    # Placeholder function so that we know this has been tested in other functions.
    # - could expand this in the future to have standalone test.

    # We already test this function in:
    # test_add_point_custom_material_rt/xy
    # test_add_magnet_region_rt/xy
    # test_add_region_rt/xy
    assert True


def test_add_point_custom_material_xy():
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    draw_square()

    region_name = "test_region"
    material_name = "Epoxy"
    colour = "0xff0000"
    mc.add_point_custom_material_xy(x_c, y_c, region_name, material_name, colour)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == region_name
    assert region["MaterialName"] == material_name
    assert hex(region["Colour"]) == colour


def test_add_point_custom_material_rt():
    mc.initiate_geometry_from_script()

    x_c = 5
    y_c = 5

    r_c, t_c = xy_to_rt(x_c, y_c)

    draw_square()

    region_name = "test_region"
    material_name = "M43"
    colour = "0xff00"
    mc.add_point_custom_material_rt(r_c, t_c, region_name, material_name, colour)

    mc.create_optimised_mesh()

    region = mc._get_region_properties_xy(x_c, y_c, DXF_IMPORT_REGION)

    assert region["RegionName"] == region_name
    assert region["MaterialName"] == material_name
    assert hex(region["Colour"]) == colour
