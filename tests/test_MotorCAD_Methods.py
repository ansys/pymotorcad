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

from ansys.motorcad.core import MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection

open_new_instance_flag = False


def set_instance_flag(*args, **kwargs):
    global open_new_instance_flag
    open_new_instance_flag = True


# Check MotorCADCompatibility object working as expected
def test_motorcadcompatibility(mc, monkeypatch):
    global open_new_instance_flag
    open_new_instance_flag = False

    monkeypatch.setattr(_MotorCADConnection, "_open_motor_cad_local", set_instance_flag)

    # Ensure Motor-CAD has opened successfully
    mc.connection._wait_for_response(30)

    mc2 = MotorCADCompatibility(port=mc.connection._port)

    # should have connected to open instance
    # Think this will actually just throw an exception if this fails
    assert open_new_instance_flag == False
    assert mc2.connection._port == mc.connection._port

    # Try simple method
    succ, var = mc2.GetVariable("Tooth_Width")
    assert succ == 0
    assert var is not None
    assert var != 0

    succ, var = mc2.GetVariable("not_a_var")
    assert succ != 0
