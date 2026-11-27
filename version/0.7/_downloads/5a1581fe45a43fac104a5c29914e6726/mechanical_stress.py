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

"""
.. _ref_internal_scripting_mechanical_stress:

Mechanical stress
=================
This example demonstrates internal scripting mechanical stress functionality
"""

# %%
# Perform required imports
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()


# This function is called when "Run" is pressed
def main():
    pass


class mechanical_stress:
    def initial(self):
        # %%
        # Disable pop-up messages
        mc.set_variable("MessageDisplayState", 2)
        # Called before calculation
        mc.set_variable("ShaftSpeed", 1500)

    def final(self):
        # Called after calculation
        yield_stress = mc.get_variable("YieldStress_RotorLam")
        max_stress = mc.get_variable("MaxStress_RotorLam")

        print("Max Stress: " + str(max_stress))

        safety_factor = yield_stress / max_stress

        print("Safety factor is: " + str(round(safety_factor, 3)))

        mc.set_variable("MessageDisplayState", 0)


# %%
# PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
try:
    from setup_scripts.setup_script import run_mech_stress_demo
except ImportError:
    pass
else:
    run_mech_stress_demo(mc)
