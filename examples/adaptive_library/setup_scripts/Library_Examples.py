import os
from pathlib import Path
import shutil
import tempfile

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import ansys.motorcad.core as pymotorcad

if "QT_API" in os.environ:
    os.environ["QT_API"] = "pyqt"


def example_setup(template, mot_name):
    """Setup Motor-CAD for adaptive templates library example.

    Parameters
    -------
    template: str
        Name of the template, which is given in the **Template** column when
        selecting **File -> Open Template** in Motor-CAD. For example, ``"a1"``
        or ``"e9"``.
    mot_name: str
        Filename of Motor-CAD file to be saved.
    """
    # Launch Motor-CAD
    _mc = pymotorcad.MotorCAD(reuse_parallel_instances=True)

    # Disable popup messages
    _mc.set_variable("MessageDisplayState", 2)
    _mc.set_visible(True)

    # Open relevant file
    working_folder = Path(tempfile.gettempdir()) / "adaptive_library"
    try:
        shutil.rmtree(working_folder)
    except:
        pass
    _mc.load_template(template)
    # mot_name = "Adaptive_Templates_Example_2"
    Path.mkdir(working_folder)
    _mc.save_to_file(working_folder / (mot_name + ".mot"))

    # Disable adaptive templates
    _mc.set_variable("GeometryTemplateType", 0)


def display_geometry(img_name):
    """Display an image for adaptive templates library example.

    Parameters
    -------
    img_name: str
        Filename of image to be displayed.
    """
    # Launch Motor-CAD
    _mc = pymotorcad.MotorCAD(open_new_instance=False)

    # Load the saved image
    images_folder = Path(__file__).parent.parent.parent.parent / "doc" / "source" / "images"
    img = mpimg.imread(images_folder / (img_name + ".png"))

    # Display the image

    imgplot = plt.imshow(img)
    plt.axis("off")
    plt.show()

    # Quit Motor-CAD
    _mc.quit()


def define_parameters(parameters, values):
    # Launch Motor-CAD
    _mc = pymotorcad.MotorCAD(open_new_instance=False)

    # Define the new adaptive parameters in the Motor-CAD file.
    for p in range(len(parameters)):
        _mc.set_adaptive_parameter_value(str(parameters[p]), float(values[p]))
