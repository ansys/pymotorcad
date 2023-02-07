.. _ref_getting_started:

Getting started
=======================
.. toctree::
   :maxdepth: 1
   :hidden:


PyMotorCAD provides pythonic access to Ansys Motor-CAD.

To run PyMotorCAD, there must be a licensed copy of Motor-CAD v2023R1 or later installed locally.

For more information on Motor-CAD, see the `Ansys Motor-CAD page <https://www.ansys.com/products/electronics/ansys-motor-cad>`_
on the Ansys website.

PyMotorCAD is installed with Motor-CAD v2023R1 and later for internal Motor-CAD Scripting tab use. To install PyMotorCAD
for use outside of Motor-CAD, it may be downloaded from GitHub. PyMotorCAD will be available for install via pip in the
near future.

Installation
*************

Python module
--------------
The ``ansys.motorcad.core`` package currently supports Python Python 3.7 through Python 3.10 on Windows.

Install the latest release from
`PyPi <pymotorcad_pypi_>`_ with:

.. code:: console

   pip install ansys-motorcad-core

Alternatively, install the latest from
`PyMotorCAD GitHub <pymotorcad_issues_>`_ via:

.. code:: console

   pip install git+https://github.com/pyansys/pymotorcad.git


For a local *development* version, install with:

.. code:: console

   git clone https://github.com/pyansys/pymotorcad.git
   cd pymotorcad
   pip install -e .

This allows you to install the ``ansys-motorcad-core`` module, modify it locally and have the changes reflected in your
setup after restarting the Python kernel.