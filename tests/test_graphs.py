# import pytest

from RPC_Test_Common import almost_equal, reset_to_default_file


def test_get_magnetic_graph_point(mc):
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_graph_point("TorqueVW", 3)
    assert almost_equal(x, 360)
    assert almost_equal(
        y,
        180.2760,
    )


def test_get_temperature_graph_point(mc):
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_temperature_graph_point("Housing [Active]", 4)

    assert almost_equal(x, 16)
    assert almost_equal(y, 47.66)


def test_get_temperature_graph(mc):
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_temperature_graph_point("Housing [Active]", 4)
    x1, y1 = mc.get_temperature_graph("Housing [Active]")

    assert almost_equal(x, x1[4])
    assert almost_equal(y, y1[4])


def test_get_power_graph_point(mc):
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_power_graph_point("Stator Back Iron", 4)

    assert almost_equal(x, 16)
    assert almost_equal(y, 341.3)


def test_get_power_graph(mc):
    reset_to_default_file(mc)
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)

    mc.do_transient_analysis()

    x, y = mc.get_power_graph_point("Stator Back Iron", 4)
    x1, y1 = mc.get_power_graph("Stator Back Iron")

    assert almost_equal(x, x1[4])
    assert almost_equal(y, y1[4])


def test_get_magnetic_graph(mc):
    reset_to_default_file(mc)
    mc.set_variable("TorqueCalculation", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_graph_point("TorqueVW", 3)
    x1, y1 = mc.get_magnetic_graph("TorqueVW")

    assert almost_equal(x, x1[3])
    assert almost_equal(y, y1[3])

    # Will be added later as Bug in MotorCAD-RPC
    # with pytest.raises(MotorCADError):
    #     x, y = mc.get_magnetic_graph("ediujhweioufbewkijbf")


def test_get_heatflow_graph(mc):
    reset_to_default_file(mc)
    # Simple transient
    mc.set_variable("TransientCalculationType", 0)
    mc.do_transient_analysis()

    x, y = mc.get_heatflow_graph("Housing OH [Rear] to Ambient")
    x1, y1 = mc.get_heatflow_graph(400524)

    assert len(x) == len(y) == 9
    assert len(x1) == len(y1) == 11
    assert almost_equal(y1[3], 11.68)


#   #Not fully ready submitted an issue
# def test_get_fea_graph_point():
#     reset_to_default_file(mc)
#     mc.show_magnetic_context()
#     mc.set_variable("SkewType", 2)
#     mc.set_variable("RotorSkewSlices", 3)
#     mc.set_variable("TorqueCalculation", True)
#     mc.set_variable("ElectromagneticForcesCalc_Load", True)
#
#
#     mc.do_magnetic_calculation()
#     x, y = mc.get_fea_graph_point("Br Gap (stator) (on load transient)", 1, 10, 1)
#     assert almost_equal(x, 120)
#     assert almost_equal(y, 1.0202)
#
#
# def test_get_fea_graph_point_no_slice():
#     reset_to_default_file(mc)
#     mc.show_magnetic_context()
#     mc.set_variable("TorqueCalculation", True)
#     mc.set_variable("ElectromagneticForcesCalc_Load", True)
#
#     mc.do_magnetic_calculation()
#     for i in range(0,6):
#         x, y = mc.get_fea_graph_point("Br Gap (stator) (on load transient)", 2, 0, i)
#         print(x,y)
#
#     # There is no slice now but if user chooses slice 2 ,
#     results shown are "Bt Gap (stator) (on load transient)
#     # instead of "Br Gap (stator) (on load transient) also
#     # slice = 0 does not work slice =1 works , i bug
#
#     assert almost_equal(x, 120)
#     assert almost_equal(y, 0.6111)
# # Get Motor-CAD exe
