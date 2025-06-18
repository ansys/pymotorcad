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

import os

import pytest

from RPC_Test_Common import get_temp_files_dir_path, reset_to_default_file
from ansys.motorcad.core import MotorCAD


@pytest.fixture(scope="module")
def mc_ui():
    """Set up test environment for whole unit of tests"""

    os.environ["MOTORCAD_FORCE_SHOW_GUI"] = "1"
    try:
        motorcad_instance_ui = MotorCAD()
    finally:
        os.environ.pop("MOTORCAD_FORCE_SHOW_GUI")

    # Disable messages if opened with UI
    motorcad_instance_ui.set_variable("MessageDisplayState", 2)
    reset_to_default_file(motorcad_instance_ui)

    return motorcad_instance_ui


def test_show_message(mc_ui):
    test_message = "test 1"
    mc_ui.show_message(test_message)
    messages = mc_ui.get_messages(1)
    assert (test_message in message for message in messages)


# Difficult to check these tests have actually worked
# These might raise an exception if they fail


def test_show_magnetic_context(mc_ui):
    mc_ui.show_magnetic_context()


def test_show_mechanical_context(mc_ui):
    mc_ui.show_mechanical_context()


def test_show_thermal_context(mc_ui):
    mc_ui.show_thermal_context()


def test_set_motorlab_context(mc_ui):
    mc_ui.set_motorlab_context()


def test_save_screen_to_file(mc_ui):
    file_path = get_temp_files_dir_path() + r"\screen.png"

    mc_ui.save_screen_to_file("Radial", file_path)

    assert os.path.exists(file_path)


def test_display_screen(mc_ui):
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc_ui.initialise_tab_names()
    mc_ui.display_screen("Calculation")


def test_set_3d_component_visibility(mc_ui):
    mc_ui.set_3d_component_visibility("stator", "winding", 0)


def test_set_visible(mc_ui):
    mc_ui.set_visible(False)
    mc_ui.set_visible(True)


def test_clear_messages(mc_ui):
    test_message = "test_message_to_clear"
    mc_ui.show_message(test_message)
    assert (test_message in message for message in mc_ui.get_messages(0))

    mc_ui.clear_messages()
    assert mc_ui.get_messages(0) == [""]
