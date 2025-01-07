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

# import pytest

from RPC_Test_Common import almost_equal, almost_equal_percentage, reset_to_default_file


def test_get_magnetic_graph_point(mc):
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_graph_point("TorqueVW", 3)
    assert almost_equal(x, 360)
    assert almost_equal_percentage(y, 182, 20)


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

    x, y = mc.get_heatflow_graph("TVent Airgap to Rotor Surface")
    # This should be the same grap series
    x1, y1 = mc.get_heatflow_graph(400524)

    assert len(x) == len(y) == 11
    assert len(x1) == len(y1) == 11
    assert almost_equal(y1[3], y[3])
    # Expect heat flow to increase with time for this model
    assert y[4] > y[3]


def test_get_fea_graph(mc):
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)
    mc.set_variable("ElectromagneticForcesCalc_Load", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_fea_graph_point("Bt Gap (on load)", 1, 16, 0)
    x1, y1 = mc.get_fea_graph("Bt Gap (on load)", 1)

    assert len(x1) == len(y1) == 181
    assert almost_equal(x1[16], x)
    assert almost_equal(y1[16], y)


def test_get_fea_graph_transient(mc):
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)
    mc.set_variable("ElectromagneticForcesCalc_Load", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_fea_graph_point("Br Gap (stator) (on load transient)", 1, 0, 1)
    x1, y1 = mc.get_fea_graph("Br Gap (stator) (on load transient)", 1, 0)
    assert len(x1) == len(y1) == 4
    assert almost_equal(x1[1], x)
    assert almost_equal(y1[1], y)


def test_get_magnetic_3d_graph(mc):
    reset_to_default_file(mc)

    mc.set_variable("TorqueCalculation", True)
    mc.set_variable("ElectromagneticForcesCalc_Load", True)

    mc.do_magnetic_calculation()

    x, y = mc.get_magnetic_3d_graph_point("Ft_Stator_OL", 1, 1, 1)
    graph_result = mc.get_magnetic_3d_graph("Ft_Stator_OL", 1)
    assert len(graph_result.x) == 481
    assert len(graph_result.y) == 4
    # Note that graph viewer shows in kN, result is in N
    assert almost_equal(graph_result.data[1][1], y)


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
