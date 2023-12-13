import os
import tempfile

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

mc = pymotorcad.MotorCAD(open_new_instance=False)
working_folder = tempfile.gettempdir() + r"\adaptive_example"

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

mc.quit()
