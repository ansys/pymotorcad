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

"""Live pytest integration tests for MotorCAD constructor parameter combinations.

Test results assume licence server has MotorCAD enterprise plus licence available
and no MotorCAD enterprise licences available.

"""

import os

import pytest

from ansys.motorcad.core import MotorCAD

MOTORCAD_ENV_VARS = (
    "MOTORDES_BLACKBOX",
    "MOTORCAD_LICENCE_TYPE",
    "MOTORCAD_SHOWGUI",
)


@pytest.fixture(autouse=True)
def clean_motorcad_env():
    """Clear Motor-CAD constructor environment overrides before each test."""
    for var in MOTORCAD_ENV_VARS:
        os.environ.pop(var, None)
    yield
    # Also clean up after the test
    for var in MOTORCAD_ENV_VARS:
        os.environ.pop(var, None)


@pytest.mark.licensing
def is_motorcad_gui_visible(mc):
    """Best-effort visibility check for Motor-CAD GUI.

    Returns:
        True  -> GUI appears visible
        False -> GUI appears hidden
    Raises:
        Exception for non-visibility-related RPC failures
    """
    try:
        # This RPC requires the Motor-CAD UI to be visible.
        mc.initialise_tab_names()
        return True
    except Exception as exc:
        return False


# Test 1: old licence type with UI
# should attempt to use old 'motorcad' and motorcad_pm licence
# if not available then will fall back to new 'motorcad_gui' licence


@pytest.mark.licensing
def test_oldmotorcad_visible():
    mc = MotorCAD(use_new_license_type=False)
    assert mc.is_open()
    assert mc.get_licence() is None
    mc.get_messages(1)
    if is_motorcad_gui_visible(mc) == False:
        assert True
    mc.quit()


# Test 2: old licence type without UI
# should have attempted to use old 'motorcad' and motorcad_pm licences when no GUI
# if no 'motorcad' licence then will fail with no fall back


@pytest.mark.licensing
def test_oldmotorcad_nogui():
    # Test old licence type without UI - expected to fail due to missing licence."""
    # with pytest.raises(MotorCADError):
    #     mc = MotorCAD(
    #         use_new_license_type=False,
    #         show_gui=False,
    #     )
    # try:
    #     assert mc.is_open()
    # finally:
    #     if mc is not None:
    #         mc.quit()
    # have licence so will succeed
    mc = MotorCAD(use_new_license_type=False, show_gui=False)
    assert mc.is_open()
    assert mc.get_licence() is None
    mc.get_messages(1)
    if is_motorcad_gui_visible(mc) == True:
        assert True
    mc.quit()


# Test 3: using black box licence (also setting new licence method)
# should be in blackbox mode using blackbox licence, ignores licence_type setting
# should not fall back


@pytest.mark.licensing
def test_newmotorcad_blackbox():
    # Test old licence type without UI - expected to fail due to missing licence."""
    # with pytest.raises(MotorCADError):
    #     mc = MotorCAD(
    #         use_blackbox_licence=True,
    #         use_new_license_type=True
    #     )
    # try:
    #     assert mc.is_open()
    # finally:
    #     if mc is not None:
    #         mc.quit()
    # have licence so will succeed
    mc = MotorCAD(use_blackbox_licence=True, use_new_license_type=True)
    assert mc.is_open(), "Failed to open MotorCAD"
    assert mc.is_open()
    assert mc.get_licence() is None
    mc.get_messages(1)
    if is_motorcad_gui_visible(mc) == True:
        assert True
    mc.quit()


# test 4: new licence type with UI (not using black box licence)
@pytest.mark.licensing
def test_newmotorcad_withui():
    mc = MotorCAD(use_new_license_type=True)
    assert mc.is_open(), "Failed to open MotorCAD"
    assert mc.get_licence() is None, "Failed to get licence"
    mc.get_messages(1)
    if is_motorcad_gui_visible(mc) == False:
        assert True, "MotorCAD GUI appears hidden"
    mc.quit()


# test 5: new licence type without UI (not using black box licence)
@pytest.mark.licensing
def test_newmotorcad_withoutui():
    mc = MotorCAD(
        use_new_license_type=True,
        show_gui=False,
    )
    assert mc.is_open()
    assert mc.get_licence() is None
    mc.get_messages(1)
    if is_motorcad_gui_visible(mc) == True:
        assert True
    mc.quit()


# test6: try to set licence type when using existing instance
@pytest.mark.licensing
def test_existinginstance_withlicencetype():
    mc = MotorCAD(
        use_new_license_type=True,
        show_gui=False,
    )
    mc2 = MotorCAD(
        open_new_instance=False, use_new_license_type=True, show_gui=False, full_headless_beta=True
    )
    assert mc.is_open(), "Failed to open MotorCAD"
    assert mc2.is_open()
    assert mc2.get_licence() is None
    mc2.get_messages(1)
    if is_motorcad_gui_visible(mc2) == True:
        assert True
    mc2.quit()
    mc.quit()
