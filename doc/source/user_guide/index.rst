.. _ref_user_guide:

User guide
============
.. toctree::
   :maxdepth: 1
   :hidden:

   backwards_compatibility
   internal_scripting
   external_scripting

PyMotorCAD provides Python access to Motor-CAD. The RPC-based :ref:`ref_MotorCAD_object`
allows you to create a Motor-CAD instance on a local machine or connect to an existing
instance on a remote machine over HTTP. Using the many methods available in this API's
single class, you can create scripts for fully controlling and automating Motor-CAD
without using the GUI. Additionally, you can use Motor-CAD scripts via the internal
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
