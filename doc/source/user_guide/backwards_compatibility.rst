Backwards compatibility with old scripts
========================================

It's easy to convert old ActiveX scripts to use PyMotorCAD.

Change communication method
----------------------------

Old scripts connect to Motor-CAD using ActiveX:

.. code:: python

    import win32com.client
    mcApp = win32com.client.Dispatch("MotorCAD.AppAutomation")

To connect to Motor-CAD using PyMotorCAD replace these 2 lines with:

.. code:: python

    import ansys.motorcad.core as pymotorcad
    mcApp = pymotorcad.MotorCADCompatibility()

The script now runs using PyMotorCAD.
This method allows old scripts to be converted with minimal changes,
however some of the new features of PyMotorCAD are turned off to ensure compatibility with these scripts.

Full script conversion
--------------------------

To convert a script to use the new features you must do 2 steps:

Change function name
^^^^^^^^^^^^^^^^^^^^^^^^^^

All API calls in the script must be renamed to use the new syntax. The API calls have been renamed to match
Python code convention. The functions are now lower case with underscores (snake_case) e.g.

.. code:: python

   McApp.GetVariable()

Must be changed to:

.. code:: python

   mcApp.get_variable()

If you are using a modern Python IDE then this is straightforward as the IDE suggests functions from your input.
You can also search for the functions in the PyMotorCAD documentation:

.. image:: /_static/backwards_compatibility_1.png
    :width: 600

There is also documentation built into the Python package that explains what
functions do and what parameters they require:

.. image:: /_static/backwards_compatibility_2.png
    :width: 600

Update function syntax
Update function syntax
^^^^^^^^^^^^^^^^^^^^^^^^^^

Previously functions returned a “success” variable that would need to be checked to ensure an API
call had been successful:

.. code:: python

   success, VariableValue = mcApp.GetVariable("Not_A_Real_Var")

This meant that API calls could fail silently unless you checked the success variable every time.
This success variable has been removed as PyMotorCAD will raise an exception if a failure occurs:

.. code:: python

   variable_value = mcApp.get_variable("Not_A_Real_Var")

.. image:: /_static/backwards_compatibility_3.png
    :width: 600

For cases where you might expect the API call to fail you should wrap it in a try/except.
For example, the following script reads graph points until the end of the graph.
Note that the MotorCADError exception type is used so that only errors raised by MotorCAD are caught:

.. code:: python

   import ansys.motorcad.core as pymotorcad
   from ansys.motorcad.core import MotorCADError

   mcApp = pymotorcad.MotorCAD()

   mcApp.do_magnetic_calculation()

   i = 0
   torque = []

   reading_graph = True
   while reading_graph is True:
       try:
           x, y = mcApp.get_magnetic_graph_point("TorqueVW", i)
           torque.append(y)
           i = i + 1
       except MotorCADError:
           reading_graph = False
