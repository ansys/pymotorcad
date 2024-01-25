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
