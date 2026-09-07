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

import functools
import os
import shutil

import pytest


def _find_mc_fixture(kwargs):
    """Locate the Motor-CAD fixture instance from the test's keyword arguments."""
    for name in ("mc", "mc_reset_to_default_on_teardown", "mc_fea_old"):
        if name in kwargs:
            return kwargs[name]
    raise RuntimeError(
        "requires_motorcad_feature/version decorator requires an mc fixture "
        "(mc, mc_reset_to_default_on_teardown, or mc_fea_old) on the test."
    )


def requires_motorcad_feature(feature_name):
    """Skip the decorated test if the connected Motor-CAD lacks ``feature_name``."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mc = _find_mc_fixture(kwargs)
            if not mc.connection.check_if_feature_exists(feature_name):
                pytest.skip(f"{feature_name} API not available in this version of Motor-CAD")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def requires_motorcad_version(required_version):
    """Skip the decorated test if the connected Motor-CAD is older than ``required_version``."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mc = _find_mc_fixture(kwargs)
            if not mc.connection.check_version_at_least(required_version):
                pytest.skip(f"Motor-CAD version {required_version} or later required for this test")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_test_files_dir_path():
    return os.path.join(get_dir_path(), "test_files")


def get_base_test_file_path():
    return os.path.join(get_test_files_dir_path(), "base_test_file.mot")


def get_temp_files_dir_path():
    return os.path.join(get_test_files_dir_path(), "temp_files")


def almost_equal(a, b, decimal_places=1):
    # Rough check
    return round(a - b, decimal_places) == 0


def almost_equal_percentage(a, b, percentage):
    return abs(a - b) < abs(a * (percentage / 100))


def almost_equal_fixed(a, b, allowed_difference=0):
    return abs(a - b) < +allowed_difference


def reset_to_default_file(motorcad_instance):
    motorcad_instance.load_from_file(get_base_test_file_path())

    # save to temp location to avoid editing base file
    motorcad_instance.save_to_file(os.path.join(get_temp_files_dir_path(), "temp_test_file.mot"))


def reset_temp_file_folder():
    dir_path = get_temp_files_dir_path()

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)
