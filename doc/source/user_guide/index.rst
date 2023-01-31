.. _ref_getting_started:

Getting started
=======================
.. toctree::
   :maxdepth: 1
   :hidden:

   backwards_compatibility
   external_scripting

PyMotorCAD provides Python access to Motor-CAD. The PyMotorCAD RPC API allows Motor-CAD to be controlled on a local machine or over HTTP from a remote machine.

Through automation, Motor-CAD can be fully controlled by scripts, without using the GUI. Motor-CAD scripts can be utilised via the internal scripting tab within Ansys Motor-CAD or externally.

Using internal PyMotorCAD scripts
----------------------------------
Motor-CAD is installed with an internal Python interpreter.
This includes a stable version of PyMotorCAD. The PyMotorCAD Python package is based around the ``MotorCAD()`` Python object. Each individual ``MotorCAD()`` object represents an instance of Motor-CAD.

Within the Motor-CAD GUI, there is a Scripting tab (available in the E-Magnetic, Thermal and Mechanical contexts). This tab facilitates the creating, editing, loading and saving of internal scripts in Motor-CAD.

To connect with Motor-CAD from an internal script on the Scripting tab, access the ``MotorCAD()`` object as follows:

.. code:: python

    import ansys.motorcad.core as pymotorcad
    mcApp = pymotorcad.MotorCAD()

PyMotorCAD methods can then be used to send commands to the current Motor-CAD instance with the object ``mcApp``. This can be used to set and get values before, during and after calculations, and to create a script for Motor-CAD automation.

PyMotorCAD API
===============

For the full list of methods, which can be used to create a script for Motor-CAD control/automation, see :ref:`ref_MotorCAD_object`.
