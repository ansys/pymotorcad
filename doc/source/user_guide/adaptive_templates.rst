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
***************

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
*************************

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

``ansys.motorcad.core`` provides access to the Motor-CAD geometry,
such as the existing regions in the model.
It can be used to get an existing region from the Motor-CAD model
(such as the **Rotor**) as an object in Python (``rotor = mc.get_region("Rotor")``).
It can also be used to set a Motor-CAD region object in the Motor-CAD model
(``mc.set_region(rotor)``).

For a Motor-CAD region object that has been obtained using PyMotorCAD,
the region properties are accessible via Python.
The region object created in Python contains all of the region properties
shown in the Motor-CAD UI and all of the geometry entities that make up the region.

Properties such as the material and colour can be edited with an Adaptive Templates Script:

.. code:: python

     # Connect to Motor-CAD
     mc = pymotorcad.MotorCAD()

     # Get rotor region from Motor-CAD
     rotor = mc.get_region("Rotor")

     # Edit region properties
     rotor.colour = (186, 85, 211)
     rotor.material = "M470-50A"
     mc.set_region(rotor)

.. figure:: ../images/Adaptive_Geometry_GUI_Screenshot_UG_Modified.png
    :width: 500pt

    Rotor geometry with modified colour and material shown in the Geometry -> Editor -> Geometry tab

Details on the Adaptive Geometry functions within ``ansys.motorcad.core``
that provide access to the Motor-CAD geometry are available
in the :ref:`ref_MotorCAD_object` under :ref:`ref_Adaptive Geometry_API`.

Using the Geometry objects and functions library
------------------------------------------------

Adaptive scripts also require the ``ansys.motorcad.core.geometry`` library
to modify the model geometry.
This provides geometry functionality in Python, such as regions and entities.
It is required so that Lines and Arcs can be defined or modified by the script,
and so that regions can be created from these entities.

The geometry package can be imported:

.. code:: python

    import ansys.motorcad.core.geometry as geometry

Alternatively, specific functions (for example Line and Arc) can be imported from the package:

.. code:: python

    from ansys.motorcad.core.geometry import Line, Arc

``ansys.motorcad.core.geometry`` is required to edit the entities that belong to a region,
such as changing the Lines or Arcs that define the region geometry.

Details on the full list of Geometry objects and functions are available
in the :ref:`ref_API_Reference` under :ref:`ref_geometry_functions`.
For examples on modifying a Motor-CAD model geometry,
see :ref:`ref_examples_adaptive_templates_library`.

Adaptive Parameters
*******************

An Adaptive Templates script can be set
based on the Standard Template parameters
or based on custom Adaptive Parameters.
Adaptive Parameters are shown in the
Geometry -> Editor -> Adaptive Parameters tab.

.. figure:: ../images/Adaptive_Parameters_GUI_Screenshot.png
    :width: 500pt

    Geometry -> Editor -> Adaptive Parameters tab in Ansys Motor-CAD 2024 R1

Any parameter can be defined, with a Name, Value and Description.
Parameters can be added within the Motor-CAD interface,
or via Python script by using the PyMotorCAD function ``mc.set_adaptive_parameter_value()``:

.. code:: python

    mc.set_adaptive_parameter_value("Notches per Pole", 2)

Adaptive Parameters also appear in the Geometry -> Radial tab,
alongside the Standard Template parameters.

.. figure:: ../images/Adaptive_Parameters_GUI_Screenshot_2.png
    :width: 500pt

    Adaptive Parameters shown in the Geometry -> Radial tab

Adaptive Parameters can be accessed via the Adaptive Templates Script
using ``mc.get_adaptive_parameter_value()``,
so that the geometry can be defined by these Adaptive Parameters:

.. code:: python

    number_notches = int(mc.get_adaptive_parameter_value("Notches per Pole"))

Scripting workflow
*******************

As well as the defined Adaptive Parameters,
any parameter from Motor-CAD
can be used in the Adaptive Templates Script
by using ``mc.get_variable()`` from PyMotorCAD.
Any Motor-CAD API accessible by PyMotorCAD is available.

For example, when modifying the rotor geometry,
it is often necessary to retrieve the rotor radius:

.. code:: python

    rotor_radius = mc.get_variable("RotorDiameter") / 2

Adding a region to the geometry
-------------------------------
To add a new geometry feature to the Motor-CAD model,
such as a notch, the workflow is as follows:

* A new region is created to represent the notch

* The region properties are defined (material, colour etc.)

* Entities are added to the region
  to define the geometry (shape and position)

* The parent region is defined for the new region.
  For a rotor duct, the parent would be set to the rotor region.

* The new region is set in Motor-CAD

Creating a region
~~~~~~~~~~~~~~~~~

To create a new region to represent the notch,
use the Region object from ``ansys.motorcad.core.geometry``:

.. code:: python

    notch = Region()

Defining region properties and parent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Region properties can be set using the appropriate field/property:

.. code:: python

    notch.name = "Rotor_Notch_1"
    notch.colour = (255, 255, 255)
    notch.material = "Air"

This is how you set the region parent

If the region object of the rotor has been created in Python (``rotor = mc.get_region("Rotor")``)
The rotor region object's properties can be obtained and set for the rotor notch.

The ``duplications`` property represents the symmetry of the region.
In the example shown using the e9 IPM template, ``duplications = 8``
because there are 8 rotor poles of 45 ° symmetry.
In this example, the notch would have the same symmetry as the rotor.

The parent region of the notch can be set to the rotor region,
so that the notch will appear as a sub-region of the rotor
in the Geometry -> Editor tab in Motor-CAD.

.. code:: python

    notch.duplications = rotor_region.duplications
    notch.parent = rotor_region

Adding entities to a region
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add two Lines (line_1, line_2) and an Arc (airgap_arc) to the notch region,
use the ``.add_entity()`` function from ``ansys.motorcad.core``:

.. code:: python

    notch.add_entity(line_1)
    notch.add_entity(line_2)
    notch.add_entity(airgap_arc)

Setting a region in Motor-CAD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is how you set the new region in Motor-CAD







