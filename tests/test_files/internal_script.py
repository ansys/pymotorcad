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
