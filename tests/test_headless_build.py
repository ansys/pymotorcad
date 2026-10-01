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

from unittest.mock import create_autospec
from warnings import catch_warnings, simplefilter

import pytest

from ansys.motorcad.core import MotorCAD
from ansys.motorcad.core.rpc_client_core import (
    MOTORCAD_EXE_GLOBAL,
    MotorCADWarning,
    _MotorCADConnection,
    set_motorcad_exe,
)


def test_full_headless_beta(mc):
    if not mc.connection.check_version_at_least("2027.0"):
        pytest.skip("full_headless requires Motor-CAD 2027.0 or later")

    with pytest.warns(UserWarning, match="full_headless is a beta setting"):
        mc1 = MotorCAD(full_headless=True)
    try:
        assert mc1.connection._full_headless is True
    finally:
        mc1.quit()

    with pytest.warns(UserWarning, match="full_headless has no effect"):
        MotorCAD(open_new_instance=False, port=mc.connection._port, full_headless=True)


def test_resolve_motor_cad_exe_ignores_full_headless_beta_when_exe_manually_set():
    save_global_exe = MOTORCAD_EXE_GLOBAL
    test_path = r"test_path/test"
    set_motorcad_exe(test_path)
    try:
        mock_conn = create_autospec(_MotorCADConnection, instance=True)
        mock_conn._full_headless_beta = True
        with pytest.warns(UserWarning, match="full_headless_beta is ignored"):
            result = _MotorCADConnection._resolve_motor_cad_exe(mock_conn)
        assert result == test_path
    finally:
        set_motorcad_exe(save_global_exe)


def test_unsupported_method_warning(mc_headless):
    # In fully headless Motor-CAD the server marks GUI-only methods as unsupported
    # and skips them. The client should emit a MotorCADWarning without raising.
    with pytest.warns(MotorCADWarning, match="only available in Motor-CAD with a GUI"):
        mc_headless.set_visible(False)


def test_supported_method_no_warning(mc_headless):
    with catch_warnings(record=True) as caught_warnings:
        simplefilter("always")
        result = mc_headless.get_variable("Tooth_Width")

    assert result is not None
    assert len(caught_warnings) == 0
