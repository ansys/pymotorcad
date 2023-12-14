import ansys.motorcad.core as pymotorcad

_mc = pymotorcad.MotorCAD(open_new_instance=False)

# Quit Motor-CAD
_mc.quit()
