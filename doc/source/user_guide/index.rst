.. _ref_user_guide:

User guide
============
.. toctree::
   :maxdepth: 1
   :hidden:

   backwards_compatibility
   internal_scripting
   external_scripting

PyMotorCAD provides Python access to Motor-CAD.
The PyMotorCAD RPC API allows Motor-CAD to be controlled on a local machine or over HTTP from a remote machine.

For the full list of PyMotorCAD API methods, which can be used to create a script for Motor-CAD control/automation,
see :ref:`ref_MotorCAD_object`.

Through automation, Motor-CAD can be fully controlled by scripts, without using the GUI. Motor-CAD scripts can be
utilised via the internal scripting tab within Ansys Motor-CAD or externally.


Using internal PyMotorCAD scripts
----------------------------------
Motor-CAD is installed with an internal Python interpreter.
This includes a stable version of PyMotorCAD.
The PyMotorCAD Python package is based around the ``MotorCAD()`` Python object.
Each individual ``MotorCAD()`` object represents an instance of Motor-CAD.

Within the Motor-CAD GUI, there is a Scripting tab (available in the E-Magnetic, Thermal and Mechanical contexts).
This tab facilitates the creating, editing, loading, and saving of internal scripts in Motor-CAD.

For more information on using PyMotorCAD via the internal Scripting tab in Motor-CAD, see :ref:`ref_internal_scripting`.

Using PyMotorCAD scripts externally
------------------------------------

PyMotorCAD can be added to any Python installation and used to control Motor-CAD from the command line or via scripts
via the users' Python IDE of choice.
