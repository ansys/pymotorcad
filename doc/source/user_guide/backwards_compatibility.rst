Backwards compatibility with Old Scripts
========================================

It's easy to convert old ActiveX script to use pymotorcad.

Change Communication Method
----------------------------

Old scripts connect to Motor-CAD using ActiveX:

.. code:: python

    import win32com.client
    mcApp = win32com.client.Dispatch("MotorCAD.AppAutomation")

To connect to Motor-CAD using Pymotorcad replace these 2 lines with:

.. code:: python

    import ansys.motorcad.core as pymotorcad
    mcApp = pymotorcad.MotorCADCompatibility()

The script will now run using pymotorcad.
This method allows old scripts to be converted with minimal changes,
however some of the new features of pymotorcad as disabled to ensure compatibility with these scripts.
There are extra steps that can be taken to take advantage of some of these improvements:

(document that here)

