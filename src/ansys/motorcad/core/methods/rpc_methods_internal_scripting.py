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

"""RPC methods for Motor-CAD internal scripting."""


class _RpcMethodsInternalScripting:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def save_script(self, file_path):
        """Save the internal Python script to a Python file.

        Parameters
        ----------
        file_path : str
            Absolute filepath for the Python file, including the file
            name and a PY extension. The default filepath is the
            Windows directory on the C: drive. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "SaveScript"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_script(self, script_file):
        """Load a script file into Motor-CAD's internal scripting.

        Parameters
        ----------
        script_file : str
            Full path to the script file, including the file name.
            Use the ``r'filepath'`` syntax to force Python to ignore
            special characters.
        """
        method = "LoadScript"
        params = [script_file]
        return self.connection.send_and_receive(method, params)

    def run_script(self):
        """Run the script file in Motor-CAD's internal scripting."""
        method = "RunScript"
        return self.connection.send_and_receive(method)
