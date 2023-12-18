"""
.. _ref_adaptive_templates_example_1:

Tutorial Example 1
==================
This example describes a workflow using Adaptive Templates to
create a BPM machine geometry with rotor notches.
This is done using a Motor-CAD Adaptive Templates script, which is provided.
This script works by altering a BPM template.
More information on this example can be found in the Motor-CAD Adaptive Templates
tutorial (Example 1), provided with a Motor-CAD installation.
"""

# %%
# Set up example
# --------------
# Setting up this example consists of performing imports,
# specifying the working directory, launching Motor-CAD,
# and disabling all popup messages from Motor-CAD.
#
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~

import os

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"

# %%
# Launch Motor-CAD
# ~~~~~~~~~~~~~~~~~~~~~~~~~

mc = pymotorcad.MotorCAD()

# %%
# Disable popup messages
# ~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("MessageDisplayState", 2)
mc.set_visible(True)

# %%
# Open relevant file
# ~~~~~~~~~~~~~~~~~~
# Specify the working directory and open the relevant Synchronous Reluctance machine
# template file for this example (i3).

working_folder = os.getcwd()
mc.load_template("e9")
mot_name = "Adaptive_Templates_Example_1"
mc.save_to_file(os.path.join(working_folder, mot_name + ".mot"))

# %%
# Enable adaptive templates
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the relevant parameter to enable Adaptive Templates in the Motor-CAD file.

mc.set_variable("GeometryTemplateType", 1)

# %%
# Add new parameters
# ~~~~~~~~~~~~~~~~~~~
# Set the relevant parameter to enable Adaptive Templates in the Motor-CAD file.

mc.set_adaptive_parameter_value("Notch Centre Angle", 5)
mc.set_adaptive_parameter_value("Notch Sweep", 2)
mc.set_adaptive_parameter_value("Notch Depth", 1)
mc.set_adaptive_parameter_value("Notches per Pole", 2)
