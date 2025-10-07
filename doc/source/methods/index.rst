.. _ref_API_Reference:
.. currentmodule:: ansys.motorcad

API reference
=============

Motor-CAD API
-------------

The ``MotorCAD`` object is used by default for PyMotorCAD scripting.
For descriptions of this object's single class and its many methods,
see :ref:`ref_MotorCAD_object`.

Motor-CAD compatibility API
---------------------------

The ``MotorCADCompatibility`` object is used for running old ActiveX
scripts. For information on backwards compatibility, see
:ref:`ref_backwards_compatibility`. For descriptions of this
object, its single class, and its many methods, see
:ref:`ref_MotorCADCompatibility_object`.

.. note::
   In addition to giving the available methods, their replacement functions
   have been commented.

Geometry objects and functions
------------------------------
The ``ansys.motorcad.core.geometry`` library contains geometry objects and functions
that provide geometry capability in Python.
Geometry objects and functions are used for
defining and modifying Adaptive Templates geometries in Python.
For descriptions of the objects and functions, see :ref:`ref_geometry_functions`.

Geometry drawing
------------------------------
The ``ansys.motorcad.core.geometry_drawing`` library contains functions for drawing
geometry objects as static visualisations in Python. Geometry drawing is used for plotting
objects such as regions, lines, arcs, and coordinates within the x-y plane. Drawing Motor-CAD
geometry objects can make it easier to test and create Adaptive Templates scripts.
For descriptions of the geometry drawing functions, see :ref:`ref_geometry_drawing`.

Geometry shapes
------------------------------
The ``ansys.motorcad.core.geometry_shapes`` library contains geometry functions
that provide geometry calculations in Python.
Geometry shapes functions are used for
defining and modifying Adaptive Templates geometries in Python.
For descriptions of the functions, see :ref:`ref_geometry_shapes`.

Geometry fitting
------------------------------
The ``ansys.motorcad.core.geometry_fitting`` library contains functions
used to find line and arc entities to fit a list of coordinates within a defined
tolerance.
For descriptions of the functions, see :ref:`ref_geometry_fitting`.

Utility functions
------------------

A number of utility functions are available.
For more information, see
:ref:`ref_utility_functions`.

Motor-CAD errors
----------------

A class/exception type is used to obtain and handle errors from Motor-CAD.
For more information, see
:ref:`MotorCAD_errors`.

.. toctree::
   :maxdepth: 1
   :hidden:

   MotorCAD_object
   MotorCADCompatibility_object
   geometry_functions
   geometry_drawing
   geometry_shapes
   geometry_fitting
   utility_functions
   MotorCAD_errors
