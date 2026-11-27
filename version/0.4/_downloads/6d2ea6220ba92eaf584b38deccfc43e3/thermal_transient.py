"""
.. _ref_internal_scripting_thermal_transient:

Thermal transient
=================
This example demonstrates internal scripting thermal transient functionality
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


class thermal_transient:
    def initial(self):
        # %%
        # Disable pop-up messages
        mc.set_variable("MessageDisplayState", 2)
        mc.display_screen("Scripting")
        # initialise water jacket and rotor cooling flow rate
        mc.set_variable("Wet_Rotor_Fluid_Volume_Flow_Rate", 0.1)
        mc.set_variable("WJ_Fluid_Volume_Flow_Rate", 0.1)

    def main(self):
        current_time = mc.get_variable("CurrentTime")
        if 1000 <= current_time < 1500:
            # if between 1000 and 1500 s, stop water jacket coolant flow
            mc.set_variable("WJ_Fluid_Volume_Flow_Rate", 0)
        else:
            # if between 1000 and 1500 s, rotor coolant flow
            mc.set_variable("Wet_Rotor_Fluid_Volume_Flow_Rate", 0)

    def final(self):
        # Called after calculation
        print("Thermal Transient - Final")
        mc.set_variable("MessageDisplayState", 0)


# %%
# Note
# ----
# For more information about transient thermal analysis, see the Scripting Control In
# Duty Cycle tutorial, installed under
# C:\ANSYS_Motor-CAD\VersionNumber\Tutorials\Scripting_Control_In_Duty_Cycle.

# %%
# PyMotorCAD Documentation Example
# --------------------------------------
# (Used for the PyMotorCAD Documentation Examples only)
try:
    from setup_scripts.setup_script import run_thermal_transient_demo
except ImportError:
    pass
else:
    run_thermal_transient_demo(mc)

mc.set_variable("MessageDisplayState", 0)
