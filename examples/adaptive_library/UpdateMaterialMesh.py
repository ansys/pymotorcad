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
Material and Mesh Properties
=================
This script applies the adaptive templates functionality to modify material and mesh properties
in a turbocharger machine.
"""
# %%
# .. note::
#    Adaptive Templates material and mesh properties described in this example require v2025.1.1
# (Motor-CAD 2025 R1 Update) or later


# %%
# Perform required imports
# ------------------------
# Import ``pymotorcad`` to access Motor-CAD.
# Import ``Arc``, ``EntityList``, ``Coordinate``, ``Line``, ``Line``, ``Region``, ``rt_to_xy``
# to define the adaptive template geometry.
# Import ``os``, ``shutil``, ``sys``, and ``tempfile``
# to open and save a temporary .mot file if none is open.

# sphinx_gallery_thumbnail_path = 'images/RotorBandMesh.png'

import os
import shutil
import sys
import tempfile

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core.geometry import Arc, Coordinate, EntityList, Line, Region, rt_to_xy

# %%
# Connect to Motor-CAD
# --------------------
# If this script is loaded into the Adaptive Templates file in Motor-CAD, the current Motor-CAD
# instance is used.
#
# If the script is run externally, these actions occur: a new Motor-CAD instance is opened,
# the e7 IPM motor template is loaded and  the file is saved to a temporary folder.
# To keep a new Motor-CAD instance open after executing the script, use
# the ``MotorCAD(keep_instance_open=True)`` option when opening the new instance.
# Alternatively, use the ``MotorCAD()`` method, which closes the Motor-CAD instance after the
# script is executed.

if pymotorcad.is_running_in_internal_scripting():
    # Use existing Motor-CAD instance if possible
    mc = pymotorcad.MotorCAD(open_new_instance=False)
else:
    mc = pymotorcad.MotorCAD(keep_instance_open=True)
    # Disable popup messages
    mc.set_variable("MessageDisplayState", 2)
    mc.set_visible(True)
    mc.load_template("e7")
    # Open relevant file
    working_folder = os.path.join(tempfile.gettempdir(), "adaptive_library")
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    os.mkdir(working_folder)
    mot_name = "E7"
    mc.save_to_file(working_folder + "/" + mot_name + ".mot")

# Reset geometry to default
mc.reset_adaptive_geometry()

# %%
# **Geometry -> Editor** tab contains Geometry Tree. Here user can select a region to
# visualaize relevant information such as entities, material type etc. For example, the Rotor
# material is defined as "Laminated" with material "N10 0.1 strip".
# From Motor-CAD version 2025 R1 onwards, a user can define different material as well as lamination
# type such as "Solid" or "Laminated" as will be demonstrated in this example.

# %%
# .. image:: ../../images/Material_E7.png
#

# %%
# Create the Adaptive Templates geometry
# --------------------------------------
# Set adaptive parameter if required
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mc.set_adaptive_parameter_default(
    "Rotor_band_thickness", 0.225
)  # Adaptive parameter of  rotor band thickness
mc.set_adaptive_parameter_default(
    "Rotor_band_mesh_length", 0.05
)  # Adaptive parameter for mesh density of rotor band

# %%
# Create points and entities for rotor band
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rt_region = mc.get_region("Rotor")  # get the rotor region
st_bore = mc.get_variable("Stator_Bore")  # Get the stator inner diameter
airgap = mc.get_variable("Airgap")  # Airgap
mag_thickness = mc.get_variable("Magnet_thickness")  # Magnet thickness
rt_radius = st_bore / 2 - airgap - mag_thickness  # Rotor lamination outer radius
rt_band_thickness = mc.get_adaptive_parameter_value("Rotor_band_thickness")  # Read the adaptive
# parameter for rotor band thickness
rt_band_radius = rt_radius - rt_band_thickness
symm_angle = 360 / rt_region.duplications
p1 = Coordinate(rt_to_xy(rt_radius, 0)[0], rt_to_xy(rt_radius, 0)[1])
p2 = Coordinate(rt_to_xy(rt_radius, symm_angle)[0], rt_to_xy(rt_radius, symm_angle)[1])
p3 = Coordinate(rt_to_xy(rt_band_radius, 0)[0], rt_to_xy(rt_band_radius, 0)[1])
p4 = Coordinate(rt_to_xy(rt_band_radius, symm_angle)[0], rt_to_xy(rt_band_radius, symm_angle)[1])
line_1 = Line(p3, p1)
line_2 = Line(p2, p4)
arc_mag = Arc(p1, p2, centre=None, radius=rt_radius)
arc_rt = Arc(p4, p3, centre=None, radius=-rt_band_radius)

# %%
# Create rotor band region with material and mesh properties
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

rt_band = Region()
rt_band.name = "rotor band"
rt_band.entities = EntityList([line_1, arc_mag, line_2, arc_rt])
rt_band.duplications = rt_region.duplications
rt_band.parent = rt_region
# %%
# Change the material using the ``Region.material`` method.
rt_band.material = "4340 Steel"
# %%
# Change the mesh length / density using the ``Region.mesh_length`` method.
rt_band.mesh_length = mc.get_adaptive_parameter_value("Rotor_band_mesh_length")
# %%
# Change the lamination type to Solid from Laminated using the ``Region.lamination_type`` method.
rt_band.lamination_type = "Solid"
mc.set_region(rt_band)

# %%
# Load in Adaptive Templates script if required
# ---------------------------------------------
# When this script is run externally, the script executes the following:
#
# * Set **Geometry type** to **Adaptive**.
#
# * Load the script into the **Adaptive Templates** tab.
#
# * Go to the **Geometry -> Radial** tab to run the Adaptive Templates script and display the new
#   geometry.

# %%
#  New rotor band region should be visible in Geometry tab. Also, notice the material and lamination
# type

# %%
# .. image:: ../../images/RotorBand.png

# %%
# Run the Emag (on Load > Torque) calculation
# ------------------------------------------
# Flux density distribution of rotor with rotor band will be visible as shown below

# %%
# .. image:: ../../images/FluxDensity_rotorband.png

# %%
# As the rotor band region is defined as "Solid" lamination type, eddy current losses can also be
# observed

# %%
# .. image:: ../../images/RotorBand_EddyLosses.png

# %%
# The eddy current losses are confined in narrow band as shown above. Hence by creating a band
# region and controlling the mesh length of specific regions user can make an computationally
# efficient model as presented in this example.
#
# Notice the different mesh density of rotor and rotor-band region. As rotor band density is an
# adaptive parameter user can change it accordingly.

# %%
# .. image:: ../../images/RotorBandMesh.png

# %%
# Eddy current losses of the rotor band region created by adaptive template will be reported under
# **Output Data -> Losses** tab as **Additional Custom Materials Loss**

# %%
# .. image:: ../../images/RotorBand_CustomLoss.png

# %%
# .. note::
#    When running in a Jupyter Notebook, you must provide the path for the Adaptive Templates script
#    (PY file) instead of ``sys.argv[0]`` when using the ``load_adaptive_script()`` method.
if not pymotorcad.is_running_in_internal_scripting():
    mc.set_variable("GeometryTemplateType", 1)
    mc.load_adaptive_script(sys.argv[0])
    mc.display_screen("Geometry;Radial")
