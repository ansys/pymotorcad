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

import pytest

from RPC_Test_Common import almost_equal, get_dir_path, reset_to_default_file
from ansys.motorcad.core.rpc_client_core import MotorCADError


def test_set_resistance_value(mc):
    mc.set_resistance_value("test res", 6, 27, 4444, "test resistance")

    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(6, 27)
    assert res == 4444


def test_set_resistance_multiplier(mc):
    mc.set_resistance_multiplier("test res mult", 7, 8, 5, "test resistance multiplier")

    # Value is being set correctly but
    # can't check value with get_node_to_node_resistance
    # -> Doesn't factor in multiplier (issue #39)

    # mc.do_steady_state_analysis()
    #
    # res = mc.get_node_to_node_resistance(7, 8)
    # assert res ==


def test_get_node_to_node_resistance(mc):
    reset_to_default_file(mc)
    mc.do_steady_state_analysis()
    res = mc.get_node_to_node_resistance(1, 9)
    assert almost_equal(res, 0.0043, 3)


def test_save_load_clear_external_circuit(mc):
    mc.set_resistance_value("test res", 3, 4, 150, "test resistance")

    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res == 150

    save_path = get_dir_path() + "\\test_files\\external_circuit.ecf"

    mc.save_external_circuit(save_path)

    mc.clear_external_circuit()
    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res != 150

    mc.load_external_circuit(save_path)
    mc.do_steady_state_analysis()

    res = mc.get_node_to_node_resistance(3, 4)
    assert res == 150


def test_set_get_node_capacitance(mc):
    mc.set_capacitance_value("test cap", 795, 35, "test capacitance value")
    mc.do_steady_state_analysis()

    cap = mc.get_node_capacitance(795)
    assert cap == 35


def test_get_node_power(mc):
    reset_to_default_file(mc)
    mc.do_steady_state_analysis()

    power = mc.get_node_power(397)
    assert almost_equal(power, 75.2)


def test_get_node_temperature(mc):
    mc.do_steady_state_analysis()
    # ambient
    temp = mc.get_node_temperature(0)
    assert temp == 40


def test_get_node_exists(mc):
    mc.do_steady_state_analysis()

    assert mc.get_node_exists(2) is True

    # doesn't exist for this model
    assert mc.get_node_exists(211) is False

    # outside of range
    assert mc.get_node_exists(5000) is False

    # non-integer value
    with pytest.raises(MotorCADError) as e_info:
        mc.get_node_exists(0.5)
    assert "nodeNumber: Integer" in str(e_info.value)
