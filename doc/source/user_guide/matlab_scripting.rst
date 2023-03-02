.. _ref_matlab_scripting:

PyMotorCAD scripting in MATLAB
===============================

PyMotorCAD is available to use in MATLAB in the same way as other Python modules.
If the :code:`ansys.motorcad.core` package is installed for a version of Python,
this version of Python can be used in MATLAB and the PyMotorCAD API can be called.
This means that MATLAB scripts can make use of PyMotorCAD for controlling Motor-CAD and automation.

Using Python modules in MATLAB
*******************************

Python modules can be called in MATLAB as long as Python is installed on the system.

Please refer to the Mathworks website for detailed information on `configuring your system to use Python <https://uk.mathworks.com/help/matlab/matlab_external/install-supported-python-implementation.html>`_
and `accessing Python Modules from MATLAB <https://uk.mathworks.com/help/matlab/matlab_external/create-object-from-python-class.html>`_.

By default, MATLAB selects the version of Python based on the system path.
To view the system path in MATLAB, use the :code:`getenv('path')` command.
To check which version of Python MATLAB is using, call the :code:`pyenv` function in MATLAB.

.. code:: matlab

    pe = pyenv;
    pe.Version

For example, if version Python version 3.10 is installed and added to path, MATLAB will output:

.. code:: text

    ans =

    "3.10"

Using PyMotorCAD in MATLAB
***************************

If the Python version that MATLAB is using has the :code:`ansys.motorcad.core` package installed, PyMotorCAD will be available to use in MATLAB.
See :ref:`ref_getting_started` for details on installing :code:`ansys.motorcad.core`.

To import the :code:`ansys.motorcad.core` module as :code:`pymotorcad` for use in scripts, use:

.. code:: matlab

    pymotorcad = py.importlib.import_module('ansys.motorcad.core');

Then pymotorcad API commands can be used in MATLAB in the same way as in Python.
To start and connect to a Motor-CAD instance, access the :code:`MotorCAD()` object:

.. code:: matlab

    mcApp = pymotorcad.MotorCAD();

Example: Motor-CAD E-magnetic scripting in MATLAB
*************************************************

An example of a MATLAB script using PyMotorCAD to change the motor geometry and materials,
run magnetic calculations and extract results for further analysis is presented.
This example is also included in the Automation tutorial supplied with Motor-CAD.

.. code:: matlab

    % Use pymotorcad as an alias to access functionality in ansys.motorcad.core
    pymotorcad = py.importlib.import_module('ansys.motorcad.core');

    % Launch an instance of Motor-CAD
    mcApp = pymotorcad.MotorCAD();

    % Turn off popups
    mcApp.set_variable('MessageDisplayState', 2)
    % Change tab to scripting so that there are no conflicts when changing
    % variables
    mcApp.show_magnetic_context()
    mcApp.display_screen('scripting')
    % change to default BPM motor
    mcApp.set_variable('Motor_Type', 0)
    % Geometry changes
    mcApp.set_variable('Slot_Number', 24)
    mcApp.set_variable('Tooth_Width', 6)
    mcApp.set_variable('Magnet_Thickness', 4.5)
    % Coil changes
    mcApp.set_variable('MagPhases',3);
    mcApp.set_variable('ParallelPaths',1);
    mcApp.set_variable('WindingLayers',2);
    mcApp.set_variable('MagWindingType',1);
    mcApp.set_variable('MagPathType',1);
    mcApp.set_winding_coil(int64(2), int64(1), int64(3), int64(4), 'b', int64(18), 'a', int64(60));
    % Material changes
    mcApp.set_component_material('Stator Lam (Back Iron)', 'M250-35A')
    mcApp.set_component_material('Rotor Lam (Back Iron)', 'M250-35A')
    % Set calculation preferences
    PointsPerCycle = 30;
    NumberCycles = 1;
    mcApp.set_variable('TorquePointsPerCycle', PointsPerCycle);
    mcApp.set_variable('TorqueNumberCycles', NumberCycles);
    % Turn off performance tests
    mcApp.set_variable('BackEMFCalculation', false);
    mcApp.set_variable('CoggingTorqueCalculation', false);
    mcApp.set_variable('ElectromagneticForcesCalc_OC', false);
    mcApp.set_variable('TorqueSpeedCalculation', false);
    mcApp.set_variable('DemagnetizationCalc', false);
    mcApp.set_variable('ElectromagneticForcesCalc_Load', false);
    mcApp.set_variable('InductanceCalc', false);
    mcApp.set_variable('BPMShortCircuitCalc', false);
    % Enable transient torque
    mcApp.set_variable('TorqueCalculation', true);
    % Emangetic calculation settings
    mcApp.set_variable('Shaft_Speed_[RPM]', 1000);
    mcApp.set_variable('CurrentDefinition', 0);
    mcApp.set_variable('PeakCurrent', 3);
    mcApp.set_variable('DCBusVoltage', 350);
    mcApp.set_variable('PhaseAdvance', 45);

    % Save file and calculate
    mcApp.save_to_file('C:\ANSYS_Motor-CAD\2023_1_1\Motor-CAD Data\MATLAB_Tutorial\automation_scripting_MATLAB_EMagnetic.mot');
    mcApp.do_magnetic_calculation()

    % data retrieval and export
    mcApp.export_results('EMagnetic','C:\ANSYS_Motor-CAD\2023_1_1\Motor-CAD Data\MATLAB_Tutorial\automation_scripting_MATLAB_EMagnetic\Export EMag Results.csv');

    ShaftTorque = mcApp.get_variable('ShaftTorque');
    LineVoltage = mcApp.get_variable('PeakLineLineVoltage');

    NumTorquePoints = (PointsPerCycle * NumberCycles) + 1;

    for loop = 0:NumTorquePoints-1
        params = mcApp.get_magnetic_graph_point('TorqueVW', int64(loop));
        params = double(params);
        x = params(1);
        y = params(2);
        RotorPosition(loop+1) = x;
        TorqueVW(loop+1) = y;
    end


    loop = 0;
    success = 0;
    while true
        try
            params = mcApp.get_fea_graph_point('B Gap (on load)', int64(1), int64(loop), int64(0));
            params = double(params);
            x = params(1);
            y = params(2);
            MechAngle(loop+1) = x;
            AirgapFluxDensity(loop+1) = y;
            loop = loop + 1;
        catch
            break
        end
    end

    mcApp.initialise_tab_names();
    mcApp.display_screen('Graphs;Harmonics;Torque');

    NumHarmonicPoints = (PointsPerCycle * NumberCycles)+1 ;
    for loop = 0:NumHarmonicPoints - 1
        params = mcApp.get_magnetic_graph_point('HarmonicDataCycle',int64(loop));
        params = double(params);
        x = params(1);
        y = params(2);
        Datapoint(loop+1) = x;
        Torque(loop+1) = y;
    end

    mcApp.quit();


