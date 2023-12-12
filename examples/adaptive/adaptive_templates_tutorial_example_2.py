"""
.. _ref_adaptive_templates_example_2:

Curved Rotor Flux Barriers for SYNCREL U-Shape
==============================================
This example describes a workflow using Adaptive Templates to
create a Synchronous Reluctance machine geometry with curved flux barriers.
This is done using a Motor-CAD Adaptive Templates script, which is provided.
This script works by altering a SYNCREL U-Shape rotor template.
More information on this example can be found in the Motor-CAD Adaptive Templates
tutorial (Example 2), provided with a Motor-CAD installation.
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

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

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
mc.load_template("i3")
mot_name = "Adaptive_Templates_Example_2"
mc.save_to_file(os.path.join(working_folder, mot_name + ".mot"))

# %%
# Enable adaptive templates
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set the relevant parameter to enable Adaptive Templates in the Motor-CAD file.

mc.set_variable("GeometryTemplateType", 1)

# %%
# Load and run adaptive templates script file
# --------------------------------------------
# Load the adaptive templates script file into Motor-CAD.
# The script will run automatically once loaded.
#
# Load adaptive templates script file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mc.load_adaptive_script(
    os.path.join(
        working_folder, "adaptive_template_script_files/UShapeSYNCRELCurvedFluxBarriers.py"
    )
)

# %%
# The script that was loaded in is shown below:
#
# UShapeSYNCRELCurvedFluxBarriers.py script file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# .. literalinclude:: /../../examples/adaptive/adaptive_template_script_files/UShapeSYNCRELCurvedFluxBarriers.py    # noqa: E501

# %%
# Improve model performance with adaptive template
# -------------------------------------------------
# The Adaptive Script that was loaded and run has changed
# the geometry of the rotor pocket regions to become curved.
#
# Alter the model to improve the model performance using the Adaptive
# Templates script. Ratio-based parameterisation will be used.
#
# Set geometry parameterisation to ratio-based
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mc.set_variable("GeometryParameterisation", 1)

# %%
# Set rotor geometry parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Units for the Bridge Thickness, Inner Thickness and Outer Thickness are in mm.
# U Magnet Web Thickness, U Magnet Diameter are ratios.
#
# Set geometry parameters for layer 1:

mc.set_array_variable("UShape_BridgeThickness_Array", 0, 0.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 0, 3.5)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 0, 0.14)
mc.set_array_variable("RatioArray_UMagnetDiameter", 0, 0.3)

# %%
# Set geometry parameters for layer 2:

mc.set_array_variable("UShape_BridgeThickness_Array", 1, 0.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 1, 3.0)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 1, 0.15)
mc.set_array_variable("RatioArray_UMagnetDiameter", 1, 0.35)

# %%
# Set geometry parameters for layer 3:

mc.set_array_variable("UShape_BridgeThickness_Array", 2, 0.5)
mc.set_array_variable("UShape_Thickness_Outer_Array", 2, 1.5)
mc.set_array_variable("UShape_Thickness_Inner_Array", 2, 2.5)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 2, 0.2)
mc.set_array_variable("RatioArray_UMagnetDiameter", 2, 0.5)

# %%
# Set geometry parameters for layer 4:

mc.set_array_variable("UShape_BridgeThickness_Array", 3, 0.5)
mc.set_array_variable("UShape_Thickness_Outer_Array", 3, 1.0)

mc.set_array_variable("RatioArray_UMagnetWebThickness", 3, 0.35)
mc.set_array_variable("RatioArray_UMagnetDiameter", 3, 0.8)

# %%
# Set corner rounding for rotor pockets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Enable the option to include corner rounding
# by setting the following to 'Single definition for all':

mc.set_variable("CornerRounding_Rotor", 1)

# %%
# Set the Rotor Lamination Corner Radius (units are mm):

mc.set_variable("CornerRoundingRadius_Rotor", 0.8)

# %%
# The curved flux barriers have now been set up
# for this Synchronous Reluctance Machine example.

# %%
# Display the example design geometry
# ------------------------------------
# Take a screenshot of the geometry that was set up using
# adaptive templates and save to the working directory.
#
# Screenshot the geometry
# ~~~~~~~~~~~~~~~~~~~~~~~

mc.initialise_tab_names()
mc.save_screen_to_file("Radial", os.path.join(working_folder, "Radial_Geometry_Screenshot.png"))

# %%
# Load, process and display the image
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Load the saved image

img = mpimg.imread(os.path.join(working_folder, "Radial_Geometry_Screenshot.png"))

# %%
# Crop the image to focus on the rotor geometry that was customised using
# adaptive templates

img_cropped = img[56:341, 250:535, :]

# %%
# Display the cropped image

imgplot = plt.imshow(img_cropped)
plt.axis("off")
plt.show()

# %%
# The customised rotor geometry is shown for this Synchronous Reluctance Machine
# example. The flux barriers have been curved using the imported script,
# and the rotor pocket parameters were adjusted to improve the model.
