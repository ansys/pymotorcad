.. _ref_geometry_functions:
.. currentmodule:: ansys.motorcad.core.geometry
Geometry objects and functions
==============================
Geometry functions are used to define and modify
the Motor-CAD Adaptive Templates geometry using PyMotorCAD.

More information on Adaptive Templates is available
in the :ref:`ref_user_guide` under :ref:`ref_adaptive_templates_UG`.

API reference for the Motor-CAD methods for getting and setting geometry
regions is available under :ref:`ref_Adaptive Geometry_API`.

Geometry objects
----------------
.. autosummary::
   :toctree: _autosummary_geometry_methods

   Region
   RegionMagnet
   RegionType
   Coordinate
   Entity
   EntityList
   Line
   Arc

Geometry functions
------------------
.. autosummary::
   :toctree: _autosummary_geometry_functions

   get_entities_have_common_coordinate
   xy_to_rt
   rt_to_xy
   get_bezier_points
