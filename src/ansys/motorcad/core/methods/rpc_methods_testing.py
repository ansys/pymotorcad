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

"""Contains JSON-RPC API methods that are only for internal use.

DO NOT USE IN SCRIPTS.
"""


class _RpcMethodsTesting:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def run_regression_tests(
        self,
        test_categories: str,
        decimal_separator: int,
        calculation_method: int,
        model_file_dir: str = "",
        comparison_file_dir: str = "",
    ):
        """Run regression tests.

        Parameters
        ----------
        test_categories : str
            If running specific sets of tests, the following format
            is used: "Test_Category1|Test_Category2|etc"
            Test category options are: "RT_EMag_Full",
            "RT_EMag_NoFEA", "RT_FEA_Emag", "RT_Mech_Stress",
            "RT_Mech_NVH", "RT_Thermal_Steady", "RT_Thermal_Trans",
            "RT_Lab_OpPoints", "RT_Lab_ModelBuild",
            "RT_Lab_Emag", "RT_Lab_Thermal",
            "RT_Lab_DutyCycle", "RT_Lab_GenOrCal",
            and "RT_Geometry"

        decimal_separator : int
            Type of decimal separator. Options are "0", "1" or "2" referring to "Standard",
            "Alternate" or "Standard + Alternate" consecutively.

        calculation_method : int
            Type of calculation method. Options are "0" or "1" referring to "New Methods" or
            "Compatibility Methods" consecutively.

        model_file_dir : str
            Model files directory relative to the Motor-CAD executable. Use "" if using default
            location.

        comparison_file_dir : str
            Comparison files directory relative to the Motor-CAD executable's parent. Use ""
            if using default location. Include slash at the end.


        Returns
        -------
        dict
            Test results including name, test case, diff type, and major and minor differences.
        """
        method = "RunRegressionTests"

        # Remove trailing None values

        params = params = [
            test_categories,
            calculation_method,
            decimal_separator,
            model_file_dir,
            comparison_file_dir,
        ]
        while params and params[-1] is None:
            params.pop()

        return self.connection.send_and_receive(method, params)
