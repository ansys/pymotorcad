.. _ref_adaptive_templates_UG:

Motor-CAD Adaptive Templates Scripting
======================================


This guide describes the Adaptive Templates functionality.
Motor-CAD provides the Adaptive Templates functionality
for the design of models with geometries that cannot be modelled
using the standard template geometries.
By using the Adaptive Templates functionality,
users can generate their own geometric parameterisations
from scratch or based on the Standard Templates.

Using Adaptive Templates, custom geometric parameterisations
are set up using a Python script.

Geometry Editor
---------------

The Geometry -> Editor tab in Ansys Motor-CAD
shows each geometry region currently in use in the model.

.. figure:: ../images/Adaptive_Geometry_GUI_Screenshot.png
    :width: 500pt

    Geometry -> Editor -> Geometry tab in Ansys Motor-CAD 2024 R1

The interface is fully interactive.
Individual geometry regions can be selected
from the region tree or the diagram.

Motor geometry components are grouped by Armature and Field
and represented by regions.
The Editor displays the geometry regions based on their spatial locations,
such that a region's sub-regions are shown as a descendant/child
of their parent region.

The e9 IPM template in Motor-CAD is shown.
In this example, the Magnet and Rotor Pocket regions
(**L1_1Magnet1**, **L2_1Magnet2**, **Rotor Pocket** and **Rotor Pocket_1**)
are shown in a branch underneath the **Rotor** region.
When a region is selected,
region properties are displayed at the bottom-left of the screen
and region entities at the bottom-right.

Region properties include the Name, Type, Material, Area (base and actual),
Position (Centroid, Region Coordinate) and Symmetry of the region.
Region entities include all the Lines and Arcs that define the region.
The **Rotor** region in the e9 IPM template is defined by two lines and two arcs.
If an individual entity is selected from the table,
it will be highlighted in the diagram.

Either Cartesian or Polar coordinate systems can be used.
The coordinate system can be be changed by going to
Input Data -> Settings -> Geometry.

.. figure:: ../images/Geometry_Coordinate_System_GUI_Screenshot.png
    :width: 500pt

    Input Data -> Settings -> Geometry tab in Ansys Motor-CAD 2024 R1

Adaptive Templates Script
-------------------------

Adaptive Templates can be enabled by going to the
Geometry -> Editor -> Adaptive Templates tab
and setting the Geometry Templates Type from **Standard** to **Adaptive**.
This means that the Adaptive Templates Script will be run
every time the Motor-CAD geometry is created,
and the scripting interface enabled, which allows editing of the script.

.. figure:: ../images/Adaptive_Templates_GUI_Screenshot.png
    :width: 500pt

    Geometry -> Editor -> Adaptive Templates tab in Ansys Motor-CAD 2024 R1

Adaptive Templates Scripts require PyMotorCAD to be imported.
This Python package provides access to Motor-CAD.

.. code:: python

    import ansys.motorcad.core as pymotorcad

Adaptive scripts also require the ``ansys.motorcad.core.geometry`` library.
This provides geometry functionality in Python, such as regions and entities.
It is required so that Lines and Arcs can be defined or modified by the script,
and so that regions can be created from these entities.

The geometry package can be imported:

.. code:: python

    import ansys.motorcad.core.geometry as geometry

Alternatively, specific functions (for example Line and Arc) can be imported from the package:

.. code:: python

    from ansys.motorcad.core.geometry import Line, Arc

Details on the full list of Adaptive Geometry functions are available in the :ref:`ref_MotorCAD_object`
under :ref:`ref_geometry_functions`.

Adaptive Parameters
-------------------

An Adaptive Templates script can be set
based on the Standard Template parameters
or based on custom Adaptive Parameters.
Adaptive Parameters are shown in the
Geometry -> Editor -> Adaptive Parameters tab.





