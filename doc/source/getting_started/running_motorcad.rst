.. _using_standard_install:

*********************
Standard installation
*********************

The PyAnsys ``ansys-motorcad-core`` package requires either a local or
remote instance of Motor-CAD to communicate with it. This section covers
launching and interfacing with Motor-CAD from a local instance by
launching it from Python.


.. _install_MotorCAD:

Install Motor-CAD
-----------------

The Motor-CAD installer can be downloaded from the Ansys Customer Portal.
A valid Motor-CAD licence is required to run the software.
Once the Windows setup file is downloaded, run this as administrator.
It may take up to around 5 minutes to prepare the installation wizard.
Then follow the steps, reading and accepting the license agreement, to proceed with installing Motor-CAD.
The installation may take several minutes to complete.

Launch Motor-CAD
-----------------

Launch Motor-CAD locally
~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the ``MotorCAD`` method to have Python start a new instance of Motor-CAD and
automatically connect to it:

.. code:: pycon

    >>> import ansys.motorcad.core as pymotorcad
    >>> mcApp = pymotorcad.MotorCAD()


This is the easiest and fastest way to get PyMotorCAD up and running.
But you need to have an Ansys license server installed locally.