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
