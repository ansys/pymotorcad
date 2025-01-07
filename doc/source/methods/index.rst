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

.. toctree::
   :maxdepth: 1
   :hidden:

   MotorCAD_object
   MotorCADCompatibility_object
   geometry_functions
   geometry_drawing
   geometry_shapes
