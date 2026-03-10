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

import os

from RPC_Test_Common import get_dir_path, get_temp_files_dir_path


def test_load_run_script(mc):
    save_tooth_width = mc.get_variable("tooth_width")

    # script in test file changes tooth width
    mc.run_script()
    assert mc.get_variable("tooth_width") == 6.5

    mc.load_script(get_dir_path() + r"\test_files\internal_script.py")
    mc.run_script()
    assert mc.get_variable("tooth_width") == 7.5

    mc.set_variable("tooth_width", save_tooth_width)


def test_save_script(mc):
    file_path = get_temp_files_dir_path() + r"\test_internal_script.py"

    mc.save_script(file_path)
    assert os.path.exists(file_path)
