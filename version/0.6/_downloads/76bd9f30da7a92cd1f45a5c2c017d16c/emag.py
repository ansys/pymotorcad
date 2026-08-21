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

"""
.. _ref_internal_scripting_emag:

E-magnetic
==========
This example demonstrates internal scripting E-Mag functionality
"""
import ansys.motorcad.core as pymotorcad

mc = pymotorcad.MotorCAD()

# %%
# Disable pop-up messages
mc.set_variable("MessageDisplayState", 2)


# This function is called when "Run" is pressed
def main():
    pass


class emagnetic:
    def initial(self):
        mc.display_screen("Scripting")
        shaft_speed = mc.get_variable("ShaftSpeed")
        if shaft_speed > 1000:
            print("Shaft speed is too high. Resetting to 500")
            mc.set_variable("ShaftSpeed", 500)

    def final(self):
        loss_total = mc.get_variable("loss_total")
        # display total loss rounded to 2dp if available
        print("total loss is: " + str(round(loss_total, 2)))
        mc.display_screen("Calculation")


# %%
# PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
try:
    from setup_scripts.setup_script import run_emag_demo
except ImportError:
    pass
else:
    run_emag_demo(mc)

mc.set_variable("MessageDisplayState", 0)
