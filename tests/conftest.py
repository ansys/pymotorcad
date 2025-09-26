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

from RPC_Test_Common import reset_temp_file_folder, reset_to_default_file
import ansys.motorcad.core
from ansys.motorcad.core import MotorCAD


def pytest_sessionstart(session):
    reset_temp_file_folder()
    ansys.motorcad.core.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = True


@pytest.fixture(scope="session")
def mc():
    """Set up test environment for whole unit of tests"""
    motorcad_instance = MotorCAD()
    # Disable messages if opened with UI
    motorcad_instance.set_variable("MessageDisplayState", 2)
    reset_to_default_file(motorcad_instance)

    return motorcad_instance


@pytest.fixture(scope="function")
def mc_reset_to_default_on_teardown(mc):
    """Set up test environment for whole unit of tests"""
    yield mc
    reset_to_default_file(mc)


@pytest.fixture(scope="session")
def mc_fea_old():
    """Old fea geometry tests cause lots of conflicts - use a new MotorCAD"""
    motorcad_instance_fea_old = MotorCAD()
    # Disable messages if opened with UI
    motorcad_instance_fea_old.set_variable("MessageDisplayState", 2)
    reset_to_default_file(motorcad_instance_fea_old)

    return motorcad_instance_fea_old
