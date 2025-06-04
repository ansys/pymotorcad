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
.. _ref_internal_scripting_thermal_steady_state:

Thermal steady-state
====================
This example demonstrates internal scripting thermal steady-state functionality
"""
# %%
# Perform required imports
import ansys.motorcad.core as pymotorcad

# %%
# Launch Motor-CAD
mc = pymotorcad.MotorCAD()


# %%
# We will update the resistance between nodes with the following equation:
# resistance = (0.01 × ambient_temp) + 1
# This function is called when "Run" is pressed
def main():
    pass


class thermal_steady:
    # Select nodes to update
    housing_node = 1
    ambient_node = 0

    def initial(self):
        # %%
        # Disable pop-up messages
        mc.set_variable("MessageDisplayState", 2)

        # Adjust Losses
        mc.display_screen("Scripting")
        mc.set_variable("Armature_Copper_Loss_@Ref_Speed", 200)

    def main(self):
        ambient_temp = mc.get_variable("T_Ambient")
        resistance = (ambient_temp * 0.01) + 1
        mc.set_resistance_value(
            "Custom Resistance", self.ambient_node, self.housing_node, resistance, ""
        )
        print(str(resistance))

    def final(self):
        # Get temperature from node
        housing_temp = mc.get_node_temperature(self.housing_node)
        print("Housing Temperature: " + str(round(housing_temp, 1)))

        mc.set_variable("MessageDisplayState", 0)


# %%
# PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
try:
    from setup_scripts.setup_script import run_thermal_steady_demo
except ImportError:
    pass
else:
    run_thermal_steady_demo(mc)
