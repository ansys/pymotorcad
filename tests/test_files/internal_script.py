# ---------- DEMO SCRIPT ----------

# Need to import pymotorcad to access Motor-CAD
import ansys.motorcad.core as pymotorcad

# Connect to Motor-CAD
mcApp = pymotorcad.MotorCAD()


# This function is called when "Run" is pressed
def main():
    # We can use main to test functions before running a calculation
    # e.g. running thermal steady initial function
    mcApp.set_variable("tooth_width", 7.5)


# demo function which sets tooth_width and runs thermal calculations
def demo_func():
    array_tooth_widths = [1, 1.5, 2.0]

    # set all messages to display in a separate window
    # Warning: this will disable crucial popups e.g. prompts to save files, overwrite data etc
    # Please ensure this is the behaviour you want
    mcApp.set_variable("MessageDisplayState", 2)

    for toothWidth in array_tooth_widths:
        mcApp.show_message("Tooth width = " + str(toothWidth))
        mcApp.set_variable("Tooth_Width", toothWidth)
        mcApp.do_steady_state_analysis()
        temperature = mcApp.get_variable(
            "T_[WINDING_AVERAGE]",
        )
        mcApp.show_message("Winding temperature = " + str(temperature))

        # restore the message dialogs
    mcApp.set_variable("MessageDisplayState", 0)


# ---------- FUNCTIONS RUN DURING CALCULATIONS ----------
# These will only run if using "Run During Analysis" selected
# (Scripting -> Settings -> Run During Analysis)

# If "Run During Analysis" is selected then this script will be imported.
# This means that anything other than setting up the MotorCAD object should
# be moved to a function/class to avoid unexpected behaviour

# This class contains functions for steady-state thermal calculations
class thermal_steady:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Steady State - Initial")

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Steady State - Main")

    def final(self):
        # Called after calculation
        print("Thermal Steady State - Final")

    # This class contains functions for trasient thermal calculations


class thermal_transient:
    def initial(self):
        # Called before calculation
        self.step = 0
        print("Thermal Transient - Initial")

    def main(self):
        # Called before each time step in calculation
        self.step = self.step + 1
        print("Step: " + str(self.step) + ". Thermal Transient State - Main")

    def final(self):
        # Called after calculation
        print("Thermal Transient - Final")

    # This class contains functions for E-Magnetic calculations


class emagnetic:
    def initial(self):
        # Called before calculation
        print("E-Magnetic - Initial")

    def final(self):
        # Called after calculation
        print("E-Magnetic - Final")


# This class contains functions for Mechanical Stress calculations
class mechanical_stress:
    def initial(self):
        # Called before calculation
        print("Mech Stress - Initial")

    def final(self):
        # Called after calculation
        print("Mech Stress - Final")


# This class contains functions for Mechanical Forces calculations
class mechanical_forces:
    def initial(self):
        # Called before calculation
        print("Mech Forces - Initial")

    def final(self):
        # Called after calculation
        print("Mech Forces - Final")
