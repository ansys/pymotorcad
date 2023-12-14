import os
import tempfile

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# Launch Motor-CAD
_mc = pymotorcad.MotorCAD(reuse_parallel_instances=True)

# Disable popup messages
_mc.set_variable("MessageDisplayState", 2)
_mc.set_visible(True)

# Open relevant file
working_folder = tempfile.gettempdir() + r"\adaptive_example"
_mc.load_template("i3")
mot_name = "Adaptive_Templates_Example_2"
_mc.save_to_file(os.path.join(working_folder, mot_name + ".mot"))

# Disable adaptive templates
_mc.set_variable("GeometryTemplateType", 0)

# Display screenshot
