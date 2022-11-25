.. _ref_getting_started:

Getting Started
=======================
.. toctree::
   :maxdepth: 1
   :hidden:

   backwards_compatibility
   external_scripting

pymotorcad provides Python access to Motor-CAD.

Using From Internal Motor-CAD Scripting
-----------------------------------------
Motor-CAD is installed with an internal Python interpreter.
This includes a stable version of Pymotorcad.
To connect with Motor-CAD from your internal scripting:

.. code:: python

    import ansys.motorcad.core as pymotorcad
    mcApp = pymotorcad.MotorCAD()


