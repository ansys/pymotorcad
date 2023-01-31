.. _ref_getting_started:

Getting started
=======================
.. toctree::
   :maxdepth: 1
   :hidden:

   backwards_compatibility
   external_scripting

PyMotorCAD provides Python access to Motor-CAD.

Using from internal Motor-CAD scripting
-----------------------------------------
Motor-CAD is installed with an internal Python interpreter.
This includes a stable version of PyMotorCAD.
To connect with Motor-CAD from your internal scripting:

.. code:: python

    import ansys.motorcad.core as pymotorcad
    mcApp = pymotorcad.MotorCAD()

PyMotorCAD API
===============

For the full list of methods, see :ref:`ref_MotorCAD_object`.
