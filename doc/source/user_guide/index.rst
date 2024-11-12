.. _ref_user_guide:

User guide
============
.. toctree::
   :maxdepth: 1
   :hidden:

   internal_scripting
   external_scripting
   matlab_scripting
   backwards_compatibility
   troubleshooting
   Motor-CAD_setup
   adaptive_templates
   virtual_env_motorcad


PyMotorCAD provides Python access to Motor-CAD. The RPC-based :ref:`ref_MotorCAD_object`
allows you to create a Motor-CAD instance on a local machine or connect to an existing
instance on a remote machine over HTTP. Using the many methods available in this API's
single class, you can create scripts for fully controlling and automating Motor-CAD
without using the GUI.

Additionally, Motor-CAD scripts can be used via the internal
**Scripting** tab within Ansys Motor-CAD or externally.


Using PyMotorCAD scripts internally 
-----------------------------------
Motor-CAD is installed with an internal Python interpreter that includes a stable version
of PyMotorCAD. This Python package is based around the ``MotorCAD()`` Python object.
Each individual ``MotorCAD()`` object represents an instance of Motor-CAD.

For more information on using PyMotorCAD via the internal Scripting tab in Motor-CAD, see :ref:`ref_internal_scripting`.

Using PyMotorCAD scripts externally
------------------------------------

PyMotorCAD can be added to any Python installation and used to control Motor-CAD from
the command line or via scripts from a Python IDE of your choice.
For more information on using PyMotorCAD with an external Python installation, see :ref:`ref_external_scripting`.

PyMotorCAD can also be used in MATLAB, for information on this, see :ref:`ref_matlab_scripting`.

Adaptive templates scripts
--------------------------
PyMotorCAD can be used to define Adaptive Templates Scripts
for designing models with geometries that cannot be modelled
using the standard Motor-CAD template geometries.
Adaptive Templates Scripts can be defined using the internal
Geometry -> Editor -> Adaptive Templates tab,
and are run whenever the Motor-CAD geometry is created.

For more information on Adaptive Templates Scripting, see :ref:`ref_adaptive_templates_UG`.

Backwards compatibility with old scripts
-----------------------------------------

Altering old scripts for use with PyMotorCAD is straightforward and allows the user to take advantage of the improvements
offered by PyMotorCAD over the previous Motor-CAD communication method (ActiveX).
For information on converting ActiveX scripts to use PyMotorCAD, see :ref:`ref_backwards_compatibility`.
