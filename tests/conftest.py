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

from RPC_Test_Common import reset_temp_file_folder, reset_to_default_file
from ansys.motorcad.core import MotorCAD
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection


def pytest_addoption(parser):
    """Register the headless command line argument with pytest."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Use the fully headless Motor-CAD build for all local test launches.",
    )


def pytest_collection_modifyitems(config, items):
    """On test collection find tests marked headless_incompatible and skip if --headless is set."""
    if config.getoption("--headless"):
        skip_headless = pytest.mark.skip(reason="Test is incompatible with --headless")
        for item in items:
            if item.get_closest_marker("headless_incompatible") is not None:
                item.add_marker(skip_headless)


def pytest_sessionstart(session):
    reset_temp_file_folder()


@pytest.fixture(scope="session", autouse=True)
def enforce_headless(pytestconfig):
    """Enforce headless executable selection for local launches throughout the session."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        if pytestconfig.getoption("--headless"):
            resolve_motor_cad_exe = _MotorCADConnection._resolve_motor_cad_exe

            def resolve_headless_exe(connection):
                connection._full_headless = True
                executable = resolve_motor_cad_exe(connection)
                return executable

            monkeypatch.setattr(_MotorCADConnection, "_resolve_motor_cad_exe", resolve_headless_exe)
        yield


@pytest.fixture(scope="session")
def mc():
    """Set up test environment for whole unit of tests"""
    motorcad_instance = MotorCAD()
    # Disable messages if opened with UI
    if motorcad_instance.connection.check_if_feature_exists("motor_cad_messager"):
        motorcad_instance.messageconfig.disable_popups()
    else:
        motorcad_instance.set_variable("MessageDisplayState", 2)
    reset_to_default_file(motorcad_instance)

    yield motorcad_instance

    motorcad_instance.quit()


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
    if motorcad_instance_fea_old.connection.check_if_feature_exists("motor_cad_messager"):
        motorcad_instance_fea_old.messageconfig.disable_popups()
    else:
        motorcad_instance_fea_old.set_variable("MessageDisplayState", 2)
    reset_to_default_file(motorcad_instance_fea_old)

    yield motorcad_instance_fea_old

    motorcad_instance_fea_old.quit()


@pytest.fixture(scope="session")
def mc_headless(mc):
    """Launch a fully headless Motor-CAD instance for testing GUI-only method warnings."""
    if not mc.connection.check_version_at_least("2027.0"):
        pytest.skip("full_headless requires Motor-CAD 2027.0 or later")

    mc_headless = MotorCAD(full_headless=True)
    reset_to_default_file(mc_headless)

    yield mc_headless
    mc_headless.quit()
