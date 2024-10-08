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

"""Contains JSON-RPC API methods that are only for internal use.

DO NOT USE IN SCRIPTS.
"""


class _RpcMethodsTesting:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def run_regression_tests(self, test_categories, calculation_method, decimal_separator):
        """Run regression tests.

        Parameters
        ----------
        test_categories : str
            Regression test categories. If running specific sets of tests, the following format
            is used: "Test_Category1|Test_Category2|etc"
        calculation_method : int
            Type of calculation method. Options are "0" or "1" referring to "New Methods" or
            "Compatibility Methods" consecutively.
        decimal_separator : int
            Type of decimal separator. Options are "0", "1" or "2" referring to "Standard",
            "Alternate" or "Standard + Alternate" consecutively.

        Returns
        -------
        str
            Test results including name, test case, diff type, and major and minor differences.
        """
        method = "RunRegressionTests"
        params = [test_categories, calculation_method, decimal_separator]
        return self.connection.send_and_receive(method, params)
