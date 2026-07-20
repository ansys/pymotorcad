.. _ref_optislang_py_integration:

PyMotorCAD scripts in optiSLang
===============================

PyMotorCAD can be used to couple Motor-CAD with optiSLang, to automate Motor-CAD simulations and
extract results for detailed analysis. The optiSLang export tool in Motor-CAD can be used to set up
an optimisation study, and generates a Python script and an optiSLang project. This workflow sets
up a sensitivity study in optiSLang, using a dedicated Motor-CAD integration node.

Alternatively, Motor-CAD and optiSLang can be coupled using the general Python integration node in
optiSLang, which allows the user to run any Python script.

optiSLang export tool in Motor-CAD
**********************************

To use the optiSLang export tool window in Motor-CAD, open the **Tools** menu from the main menu,
and select **Ansys optiSLang**. Set up the input parameters and ranges for the optimisation study on
the **Input Parameters** tab, and on the **Requirements** and **Objectives** tabs set up the outputs
that will be used to assess electric machine designs.

The export tool generates a Python script, using PyMotorCAD to control Motor-CAD. The script sets
the input parameters, initialises and runs the necessary Motor-CAD calculations, and gets the
required output parameters/results. The script can be viewed on the **Test Run** tab, and when the
**Setup Optimisation in Ansys optiSLang** button on the **Summary** tab is clicked, the optimisation
script is saved and the sensitivity wizard pops up. Clicking through the wizard, the optiSLang
project automatically opened, showing the sensitivity system with Motor-CAD integration node.

The Motor-CAD integration node in optiSLang is set up to run the optimisation script using the
Python interpreter that is installed with Motor-CAD.

Python node integration in optiSLang
************************************

Alternatively, Motor-CAD can be coupled with optiSLang using the general Python integration node in
optiSLang. The Python node uses a Python interpreter that is installed with optiSLang, which, by
default, does not have PyMotorCAD installed. If the PyMotorCAD package is not installed, a Python
error will be raised when the script is run in optiSLang, indicating that
:code:`ansys.motorcad.core` is not available. It is recommended to add some lines to the Python
script so that PyMotorCAD can be imported from the Motor-CAD Python installation folder:

.. code:: python

    import os
    import sys

    awp_root261 = os.getenv("AWP_ROOT261")
    pymotorcad_parent_dir = os.path.join(
        awp_root261, "motorcad", "Python", "Python", "Lib", "site-packages"
    )
    sys.path.append(pymotorcad_parent_dir)
    import ansys.motorcad.core as pymotorcad

This adds the Motor-CAD Python installation folder to the Python path, so that PyMotorCAD can be
imported and used in the script, without having to install PyMotorCAD to the optiSLang Python
interpreter.



