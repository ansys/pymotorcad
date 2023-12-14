import os

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

_mc = pymotorcad.MotorCAD(open_new_instance=False)

# Load the saved image
this_folder = os.getcwd()
pymotorcad_folder = os.path.dirname(os.path.dirname(this_folder))
images_folder = pymotorcad_folder + r"\doc\source\images"
img = mpimg.imread(os.path.join(images_folder, "UShapeSYNCRELCurvedFluxBarriers.png"))

# %%
# Crop the image to focus on the rotor geometry that was customised using
# adaptive templates

# %%
# Display the cropped image

imgplot = plt.imshow(img)
plt.axis("off")
plt.show()

# Quit Motor-CAD
_mc.quit()
