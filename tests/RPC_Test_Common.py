# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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
import shutil


def get_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_test_files_dir_path():
    return get_dir_path() + r"\test_files"


def get_base_test_file_path():
    return get_test_files_dir_path() + r"\base_test_file.mot"


def get_temp_files_dir_path():
    return get_test_files_dir_path() + r"\temp_files"


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
    motorcad_instance.save_to_file(get_temp_files_dir_path() + r"\temp_test_file.mot")


def reset_temp_file_folder():
    dir_path = get_temp_files_dir_path()

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)
