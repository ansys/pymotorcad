..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.

PyMotorCAD documentation |version|
===================================

.. toctree::
   :maxdepth: 2
   :hidden:

   getting_started/index
   user_guide/index
   methods/index
   examples/index
   samples/index
   contributing

Introduction
-------------

Ansys Motor-CAD is a dedicated design and analysis tool for electric motors.
It enables rapid and accurate multiphysics design and analysis of electric
machines across the full operating spectrum.

Today's electric motor design requires multiphysics analysis across wide
torque and speed operating ranges to accommodate rapid development cycles and
system integration. Motor-CAD facilitates this cutting-edge design approach
by providing:

- Intuitive, template-based setups for fast initial electric machine designs
- Built-in electromagnetic, thermal, and mechanical solvers for multiphysics insights
- Rapid analysis of efficiency maps, torque and speed characteristics, and drive cycles
- Quick evaluation of motor topologies and concepts to produce designs that are
  optimized for size, performance. and efficiency

What is PyMotorCAD?
--------------------

PyMotorCAD is part of the `PyAnsys <https://docs.pyansys.com/>`_ ecosystem
that facilitates the use of Motor-CAD within a Python environment in
conjunction with other PyAnsys libraries and external Python libraries.

PyMotorCAD uses a Python JSON-RPC (remote procedure call) interface for
Motor-CAD to launch or connect with a Motor-CAD instance, either locally or
from a remote machine via HTTP.

PyMotorCAD allows you to programmatically create, interact with,
and control a Motor-CAD model, with or without using the Motor-CAD GUI.
You can achieve Motor-CAD automation by running scripts, either internally
via the Motor-CAD **Scripting** tab or externally.

Features
---------

Features of PyMotorCAD include:

- The ability to launch Motor-CAD instances and connect to already-running
  instances of Motor-CAD.
- The ability to control Motor-CAD by automation using PyMotorCAD API methods
  to carry out Motor-CAD actions, such as setting and retrieving Motor-CAD
  parameters. For the list of API methods, see the :ref:`ref_MotorCAD_object`.
- The ability to automate workflows and methodologies within an instance of
  Motor-CAD via its internal **Scripting** tab. For information internal
  scripting in Motor-CAD see the :ref:`ref_user_guide`.
- Automation control of Motor-CAD via external scripts. Workflows and
  methodologies can be carried out with either a visible Motor-CAD GUI
  or via BlackBox mode. For adding PyMotorCAD to your own Python, see
  :ref:`ref_external_scripting`.
- The ability to control communication and couple or link Motor-CAD
  with other software such as Ansys optiSLang.
- The ability to run automated sensitivity analysis studies and/or select
  tolerance buildup to produce robust designs.
- Allowing users to introduce their own formulations into Motor-CAD.
- The running of multiple parallel Motor-CAD instances via an external script.
  Ansys optiSLang can be employed to carry out detailed optimizations by
  controlling multiple Motor-CAD instances in parallel.
- Example scripts for tutorials on Motor-CAD features and abilities.
- Customizable example scripts for common or advanced workflows, both within
  Motor-CAD and involving the coupling of Motor-CAD to other software.


Documentation and issues
------------------------
Documentation for the latest stable release of PyMotorCAD is hosted at
`PyMotorCAD documentation <https://motorcad.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation's title bar, there is an option for switching from
viewing the documentation for the latest stable release to viewing the documentation for the
development version or previously released versions.

You can also `view <https://cheatsheets.docs.pyansys.com/pymotorcad_cheat_sheet.png>`_ or
`download <https://cheatsheets.docs.pyansys.com/pymotorcad_cheat_sheet.pdf>`_ the
PyMotorCAD cheat sheet. This one-page reference provides syntax rules and commands
for using PyMotorCAD. 

On the `PyMotorCAD Issues <https://github.com/ansys/pymotorcad/issues>`_ page, you can create
issues to report bugs and request new features. On the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback. 

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

Project index
--------------

* :ref:`genindex`
