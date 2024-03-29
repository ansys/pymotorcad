.. _ref_getting_started:

Getting started
=======================
.. toctree::
   :hidden:
   :maxdepth: 2

   running_motorcad


PyMotorCAD provides access to Ansys Motor-CAD via Python.

To run PyMotorCAD, there must be a licensed copy of Motor-CAD v2023R1 or later installed locally.

For more information on Motor-CAD, see the `Ansys Motor-CAD page <https://www.ansys.com/products/electronics/ansys-motor-cad>`_
on the Ansys website.

PyMotorCAD is installed with Motor-CAD v2023R1 and later for internal Motor-CAD Scripting tab use. To install PyMotorCAD
for use outside of Motor-CAD, it may be downloaded from GitHub. PyMotorCAD is available for install via pip in the
near future.

Installation
*************

Python module
--------------
The ``ansys.motorcad.core`` package currently supports Python 3.7 through Python 3.10 on Windows.

Install the latest release from
`PyPi <https://pypi.org/project/ansys-motorcad-core/>`_ with:

.. code:: console

   pip install ansys-motorcad-core

Alternatively, install the latest from
`PyMotorCAD GitHub <https://github.com/ansys/pymotorcad>`_ via:

.. code:: console

   pip install git+https://github.com/ansys/pymotorcad.git


For a local *development* version, install with:

.. code:: console

   git clone https://github.com/ansys/pymotorcad.git
   cd pymotorcad
   pip install -e .

This allows you to install the ``ansys-motorcad-core`` module, modify it locally and have the changes reflected in your
setup after restarting the Python kernel.

Ansys software requirements
----------------------------
For the latest features, you must have a copy of Ansys Motor-CAD v2023R1
installed locally.

For more information, see :ref:`install_MotorCAD`.

Verify your installation
----------------------------
Check that Motor-CAD can be started from Python by running:

.. code:: pycon

    >>> import ansys.motorcad.core as pymotorcad
    >>> mcApp = pymotorcad.MotorCAD()

If successful, a Motor-CAD instance is launched, appearing on the taskbar. You are now ready to start using
Motor-CAD with PyMotorCAD. For more information on the PyMotorCAD interface, see the :ref:`ref_user_guide`.
