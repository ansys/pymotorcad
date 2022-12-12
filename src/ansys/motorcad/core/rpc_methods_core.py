"""Contains all the JSON-RPC API calls for Motor-CAD.

Not for direct use. Inherited by _MotorCADCore/_RpcMethodsCoreOld
"""

from packaging import version

from ansys.motorcad.core.methods.rpc_methods_variables import _RpcMethodsVariables


class _RpcMethodsCore(_RpcMethodsVariables):
    def __init__(self, mc_connection):
        self.connection = mc_connection

        _RpcMethodsVariables.__init__(self, self.connection)

    # ------------------------------------ UI ------------------------------------

    def disable_error_messages(self, active):
        """Disable or enable message display.

        Parameters
        ----------
        active : bool
            If true, then disable messages
        """
        method = "DisableErrorMessages"
        params = [active]
        return self.connection.send_and_receive(method, params)

    def get_messages(self, num_messages):
        """Return a list of the last N messages from the message history.

        Parameters
        ----------
        num_messages : int
            The number of recent messages to be returned.
            If numMessages=0 all messages in history will be returned.

        Returns
        -------
        str
            List of messages (most recent first, separated by ;)
        """
        method = "GetMessages"
        params = [num_messages]
        return self.connection.send_and_receive(method, params)

    def initialise_tab_names(self):
        """Initialise the available tabs in the Motor-CAD UI.

        Call before using SaveMotorCADScreenToFile or DisplayScreen. Motor-CAD UI must be visible.
        """
        method = "InitialiseTabNames"
        return self.connection.send_and_receive(method)

    def save_motorcad_screen_to_file(self, screen_name, file_name):
        """Save the whole Motor-CAD screen of the specified tab as a image file, (bmp, jpg, png).

        InitialiseTabNames must be called before using this function. Motor-CAD UI must be visible.

        Parameters
        ----------
        screen_name : str
            Path of the screen to save,
            must be in the format of "tabName;tabName;tabName" e.g. "Geometry;Axial"
        file_name : str
            File where the image is to be saved (full path)
        """
        method = "SaveMotorCADScreenToFile"
        params = [screen_name, file_name]
        return self.connection.send_and_receive(method, params)

    def get_license(self):
        """Check if there is a licence available for the current context and machine type.

        The licence is checked out if available.
        """
        method = "GetLicence"
        return self.connection.send_and_receive(method)

    def set_visible(self, visible):
        """Set the visibility of the Motor-CAD user interface.

        Parameters
        ----------
        visible : bool
            When true, the Motor-CAD user interface is shown. When false, the UI is hidden.
        """
        if version.parse(self.connection.program_version) < version.parse("15.2.0"):
            # Backwards compatibility for v15.1.x
            method = "Set_Visible"
        else:  # v15.2 onwards
            method = "SetVisible"

        params = [visible]
        return self.connection.send_and_receive(method, params)

    def clear_message_log(self):
        """Clear the message log file for the current model."""
        method = "ClearMessageLog"
        return self.connection.send_and_receive(method)

    def show_message(self, message):
        """Display a message in the Motor-CAD message window.

        Parameters
        ----------
        message : str
            Message to display
        """
        method = "ShowMessage"
        params = [message]
        return self.connection.send_and_receive(method, params)

    def show_magnetic_context(self):
        """Show magnetic context in Motor-CAD."""
        method = "ShowMagneticContext"
        return self.connection.send_and_receive(method)

    def show_mechanical_context(self):
        """Show mechanical context in Motor-CAD."""
        method = "ShowMechanicalContext"
        return self.connection.send_and_receive(method)

    def show_thermal_context(self):
        """Show thermal context in Motor-CAD."""
        method = "ShowThermalContext"
        return self.connection.send_and_receive(method)

    def display_screen(self, screen_name):
        """Show a screen within Motor-CAD.

        Parameters
        ----------
        screen_name : str
            Screen to display
        """
        method = "DisplayScreen"
        params = [screen_name]
        return self.connection.send_and_receive(method, params)

    def quit(self):
        """Quit Motor-CAD."""
        method = "Quit"
        return self.connection.send_and_receive(method)

    def set_free(self):
        """Free Motor-CAD instance."""
        return self.connection._set_free()

    def save_screen_to_file(self, screen_name, file_name):
        """Save a screen as an image.

        Parameters
        ----------
        screen_name : str
            Screen to save
        file_name : str
            File to save image full path
        """
        method = "SaveScreenToFile"
        params = [screen_name, file_name]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Files ------------------------------------

    def load_duty_cycle(self, file_name):
        """Load a duty cycle from a .dat file.

        Parameters
        ----------
        file_name : str
            The default is the directory of the .mot file. Alternatively, use a custom location
            by specifying the absolute filepath of the duty cycle to be saved. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "LoadDutyCycle"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_duty_cycle(self, file_path):
        """Save the duty cycle to a file.

        The file should be saved with a .dat file extension to ensure it can be correctly loaded
        into a .mot file

        Parameters
        ----------
        file_path : str
            The default is the directory of the .mot file. Alternatively, use a custom location
            by specifying the absolute filepath of the duty cycle to be saved. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "SaveDutyCycle"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_matrices(self, directory_path):
        """Save the resistance, power and capacitance matrices to files in the file path.

        The files are given the name of the .mot model, with different file extensions.

        Parameters
        ----------
        directory_path : str
            The default is the root directory. Alternatively, use a custom location
            by specifying the absolute filepath of the data to be saved. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "ExportMatrices"
        params = [directory_path]
        return self.connection.send_and_receive(method, params)

    def load_custom_drive_cycle(self, file_path):
        """Load a custom current waveform from a file.

        Parameters
        ----------
        file_path : str
            Use r'filepath' syntax to force Python to ignore special characters.
        """
        method = "LoadCustomDriveCycle"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_fea_result(self, file_path, solution_number):
        """Load in an existing FEA solution to allow viewing of FEA results.

        Parameters
        ----------
        file_path : str
            Use r'filepath' syntax to force Python to ignore special characters.
        solution_number : int
        """
        method = "LoadFEAResult"
        params = [file_path, solution_number]
        return self.connection.send_and_receive(method, params)

    def export_to_ansys_electronics_desktop(self, file_path):
        """Export the model to a vbs script file to be run in Ansys Electronics Desktop.

        The filepath must include the name of the file. The default
        filepath is the Windows directory in the C: drive

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be saved. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "ExportToAnsysElectronicsDesktop"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_results(self, solution_type, file_path):
        """Export results from the selected solution to a csv file.

        The filepath must include the name of the file, with the .CSV extension.

        Parameters
        ----------
        solution_type : str
            solution_type can be 'SteadyState', 'Transient', 'EMagnetic' or 'Lab'
        file_path : str
            The absolute filepath of the data to be saved. The default
            filepath is the Windows directory in the C: drive. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "ExportResults"
        params = [solution_type, file_path]
        return self.connection.send_and_receive(method, params)

    def load_dxf_file(self, file_name):
        """Load a .dxf geometry file.

        Parameters
        ----------
        file_name : str
            DXF file. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadDXFFile"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def create_report(self, file_path, template_file_path):
        """Create Word report of report tree structure.

        Parameters
        ----------
        file_path : str
            You can use r'filepath' syntax to force
            Python to ignore special characters.
        template_file_path : str
            You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "CreateReport"
        params = [file_path, template_file_path]
        return self.connection.send_and_receive(method, params)

    def load_report_structure(self, file_path):
        """Load tree structure of report from file.

        Parameters
        ----------
        file_path : str
            You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadReportStructure"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_force_animation(self, animation, file_name):
        """Export chosen force animation to file as a GIF.

        Animation is exported from caption name e.g. "Radial OL" or "Radial OL (12th harmonic)"

        Parameters
        ----------
        animation : str
            animation name
        file_name : str
            You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "ExportForceAnimation"
        params = [animation, file_name]
        return self.connection.send_and_receive(method, params)

    def load_report_tree(self):
        """Create tree structure of selected modules and components."""
        method = "LoadReportTree"
        return self.connection.send_and_receive(method)

    def load_template(self, template_name):
        """Load a motor template.

        Parameters
        ----------
        template_name : str
            The template name is given in the Template column from File
            -> Open Template e.g. a1, e9
        """
        method = "LoadTemplate"
        params = [template_name]
        return self.connection.send_and_receive(method, params)

    def save_template(
        self,
        template_file_name,
        name,
        sector,
        machine_type,
        application,
        winding_type,
        max_speed,
        power,
        cooling,
        drive_type,
        notes,
    ):
        """Save to a .mtt template file.

        Parameters
        ----------
        template_file_name : str
        name : str
        sector : str
        machine_type : str
        application : str
        winding_type : str
        max_speed : str
        power : str
        cooling : str
        drive_type : str
        notes : str
        """
        method = "SaveTemplate"
        params = [
            template_file_name,
            name,
            sector,
            machine_type,
            application,
            winding_type,
            max_speed,
            power,
            cooling,
            drive_type,
            notes,
        ]
        return self.connection.send_and_receive(method, params)

    def load_winding_pattern(self, file_path):
        """Load the winding pattern from a text file.

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be loaded. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "LoadWindingPattern"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def save_winding_pattern(self, file_path):
        """Save the winding pattern to a file.

        The filepath must include the name of the file. If the file is to be re-loaded
        into Motor-CAD, then the file extension must be specified as .txt. The default
        filepath is the Windows directory in the C: drive

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be saved. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "SaveWindingPattern"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_multi_force_data(self, file_name):
        """Export multiforce data calculated to file.

        Parameters
        ----------
        file_name : str
            Use r'filepath' syntax to force Python to ignore special characters.
        """
        method = "ExportMultiForceData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def geometry_export(self):
        """Export the geometry to file specified in DXFFileName parameter."""
        method = "GeometryExport"
        return self.connection.send_and_receive(method)

    def export_to_ansys_discovery(self, file_path):
        """Export the model to a python script file which can be run in Ansys Discovery.

        The filepath must include the name of the file. The
        extension does not need to be specified.

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be saved. The default
            filepath is the Windows directory in the C: drive. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "ExportToAnsysDiscovery"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_nvh_results_data(self, file_name):
        """Export NVH results data to file.

        Parameters
        ----------
        file_name : str
            Use r'filepath' syntax to force Python to ignore special characters.
        """
        method = "ExportNVHResultsData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def load_from_file(self, mot_file):
        """Load a .mot file into the Motor-CAD instance.

        Parameters
        ----------
        mot_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadFromFile"
        params = [mot_file]
        return self.connection.send_and_receive(method, params)

    def save_to_file(self, mot_file):
        """Save the current .mot file.

        Parameters
        ----------
        mot_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "SaveToFile"
        params = [mot_file]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Internal Scripting ------------------------------------

    def save_script(self, file_path):
        """Save the internal python script to a file.

        The .py extension should be included in the file name.

        Parameters
        ----------
        file_path : str
            The absolute filepath of the data to be saved. The default
            filepath is the Windows directory in the C: drive. Use r'filepath'
            syntax to force Python to ignore special characters.
        """
        method = "SaveScript"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_script(self, script_file):
        """Load a script file into Motor-CAD internal scripting.

        Parameters
        ----------
        script_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadScript"
        params = [script_file]
        return self.connection.send_and_receive(method, params)

    def run_script(self):
        """Run script file in Motor-CAD internal scripting."""
        method = "RunScript"
        return self.connection.send_and_receive(method)

    # ------------------------------------ Calculations ------------------------------------

    def clear_duty_cycle(self):
        """Clear the duty cycle in both the lab and thermal contexts."""
        method = "ClearDutyCycle"
        return self.connection.send_and_receive(method)

    def do_magnetic_thermal_calculation(self):
        """Carry out coupled e-magnetic and thermal calculation."""
        method = "DoMagneticThermalCalculation"
        return self.connection.send_and_receive(method)

    def set_3d_component_visibility(self, group_name, component_name, visibility):
        """Set the visibility of a component specified by group name, and component name.

        Parameters
        ----------
        group_name : str
            "Machine", "Stator", "Rotor", "Shaft Components". If in the thermal context then
            "Mounting"
            and "Outer Casing" are available too.
        component_name : str
            "All", "Lamination", "Wedge". The available component names depends on which model
            is used.
        visibility : int
            0=Invisible to 100=Solid
        """
        method = "Set3DComponentVisibility"
        params = [group_name, component_name, visibility]
        return self.connection.send_and_receive(method, params)

    def calculate_saturation_map(self):
        """Generate electromagnetic saturation and loss data.

        Saturation (flux linkages and inductances) and loss data for use in other
        analysis and modelling tools. The default file extension is .mat and is saved in
        the lab folder in the .mot directory.
        """
        method = "CalculateSaturationMap"
        return self.connection.send_and_receive(method)

    def calculate_torque_envelope(self):
        """Calculate torque envelope for machine."""
        method = "CalculateTorqueEnvelope"
        return self.connection.send_and_receive(method)

    def save_results(self, solution_type):
        """Save the output results from the selected solution (EMagnetic).

        Parameters
        ----------
        solution_type : str
            Only 'EMagnetic' solution type currently available.
        """
        method = "SaveResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def load_results(self, solution_type):
        """Load the output results from the selected solution (EMagnetic).

        Parameters
        ----------
        solution_type : str
            Only 'EMagnetic' solution type currently available.
        """
        method = "LoadResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def calculate_im_saturation_model(self):
        """Calculate saturation lookup tables for IM machines."""
        method = "CalculateIMSaturationModel"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_spatial(self):
        """Calculate 1D force harmonics in Space axis."""
        method = "CalculateForceHarmonics_Spatial"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_temporal(self):
        """Calculate 1D force harmonics in Time axis."""
        method = "CalculateForceHarmonics_Temporal"
        return self.connection.send_and_receive(method)

    def get_force_frequency_domain_amplitude(self, row, column, load_point):
        """Export matrix value from Force Space Time Harmonics matrix from 2D FFT.

        Parameters
        ----------
        row : int
            row index of FFT matrix
        column : int
            column index of FFT matrix
        load_point : int
        """
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, load_point]
        return self.connection.send_and_receive(method, params)

    def update_force_analysis_results(self, fft_data_type):
        """Update force analysis results for selected multiforce operating point.

        Parameters
        ----------
        fft_data_type : int
            0 : 1D Temporal Harmonics, 1 : 1D Spatial Harmonics
        """
        method = "UpdateForceAnalysisResults"
        params = [fft_data_type]
        return self.connection.send_and_receive(method, params)

    def do_multi_force_calculation(self):
        """Calculate forces for multiple operating points."""
        method = "DoMultiForceCalculation"
        return self.connection.send_and_receive(method)

    def do_steady_state_analysis(self):
        """Do thermal steady state analysis."""
        method = "DoSteadyStateAnalysis"
        return self.connection.send_and_receive(method)

    def do_transient_analysis(self):
        """Do thermal transient analysis."""
        method = "DoTransientAnalysis"
        return self.connection.send_and_receive(method)

    def do_magnetic_calculation(self):
        """Run the Motor-CAD magnetic calculation."""
        method = "DoMagneticCalculation"
        return self.connection.send_and_receive(method)

    def do_weight_calculation(self):
        """Run the Motor-CAD weight calculation."""
        method = "DoWeightCalculation"
        return self.connection.send_and_receive(method)

    def do_mechanical_calculation(self):
        """Run the Motor-CAD mechanical calculation."""
        method = "DoMechanicalCalculation"
        return self.connection.send_and_receive(method)

    # ------------------------------------ Lab ------------------------------------

    def calculate_test_performance_lab(self):
        """Calculate the test performance.

        Results will be saved in the .mot file results folder as MotorLAB_caldata.mat
        """
        method = "CalculateTestPerformance_Lab"
        return self.connection.send_and_receive(method)

    def export_duty_cycle_lab(self):
        """Export the calculated duty cycle data to the thermal model."""
        method = "ExportDutyCycle_Lab"
        return self.connection.send_and_receive(method)

    def get_model_built_lab(self):
        """Test if the Lab model needs to be built or rebuilt before running calculations.

        Returns
        -------
        bool
            Return true if the Lab model has been built and is valid for the current settings.
        """
        method = "GetModelBuilt_Lab"
        return self.connection.send_and_receive(method)

    def show_results_viewer_lab(self, calculation_type):
        """Load the results viewer for the specified Lab calculation type.

        Parameters
        ----------
        calculation_type : str
            Choose from "Electromagnetic", "Thermal","Generator", "Duty Cycle" or "Calibration"
        """
        method = "ShowResultsViewer_Lab"
        params = [calculation_type]
        return self.connection.send_and_receive(method, params)

    def export_figure_lab(self, calculation_type, variable, file_name):
        """Export an image of the Lab results graph.

        Parameters
        ----------
        calculation_type : str
            Choose from "Electromagnetic", "Thermal","Generator", "Duty Cycle" or "Calibration"
        variable : str
            The given variable will be plotted on the Y axis (2d graphs) or Z axis (3d graphs),
            e.g. "Shaft Torque"
        file_name : str
        """
        method = "ExportFigure_Lab"
        params = [calculation_type, variable, file_name]
        return self.connection.send_and_receive(method, params)

    def calculate_generator_lab(self):
        """Calculate generator performance.

        Results will be saved in the .mot file results folder as LabResults_Generator.mat
        """
        method = "CalculateGenerator_Lab"
        return self.connection.send_and_receive(method)

    def load_external_model_lab(self, file_path):
        """Load the specified external model data file.

        For when the Lab link type is set to Custom or ANSYS Maxwell.

        Parameters
        ----------
        file_path : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadExternalModel_Lab"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def clear_model_build_lab(self):
        """Clear the Lab model build."""
        method = "ClearModelBuild_Lab"
        return self.connection.send_and_receive(method)

    def set_motorlab_context(self):
        """Change Motor-CAD to Lab Context."""
        method = "SetMotorLABContext"
        return self.connection.send_and_receive(method)

    def build_model_lab(self):
        """Build the Lab model."""
        method = "BuildModel_Lab"
        return self.connection.send_and_receive(method)

    def calculate_operating_point_lab(self):
        """Calculate Lab operating point."""
        method = "CalculateOperatingPoint_Lab"
        return self.connection.send_and_receive(method)

    def calculate_magnetic_lab(self):
        """Do Lab magnetic calculation."""
        method = "CalculateMagnetic_Lab"
        return self.connection.send_and_receive(method)

    def calculate_thermal_lab(self):
        """Do Lab thermal calculation."""
        method = "CalculateThermal_Lab"
        return self.connection.send_and_receive(method)

    def calculate_duty_cycle_lab(self):
        """Calculate Lab duty cycle."""
        method = "CalculateDutyCycle_Lab"
        return self.connection.send_and_receive(method)

    # ------------------------------------ Geometry ------------------------------------

    def set_winding_coil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        """Set Go and Return slots, positions and turns for a winding coil.

        Parameters
        ----------
        phase : int
        path : int
        coil : int
        go_slot : int
        go_position : str
            Position parameters can be "a", "b", "c" etc. for Upper/Lower paths and "L"
            or "R" for Left/Right paths
        return_slot : int
        return_position : str
            Position parameters can be "a", "b", "c" etc. for Upper/Lower paths and "L"
            or "R" for Left/Right paths
        turns : int
        """
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            go_slot,
            go_position,
            return_slot,
            return_position,
            turns,
        ]
        return self.connection.send_and_receive(method, params)

    def get_winding_coil(self, phase, path, coil):
        """Get Go and Return slots, positions and turns for a winding coil.

        Phases, paths and coils indexed as on Winding -> Pattern tab.

        Parameters
        ----------
        phase : int
        path : int
        coil : int

        Returns
        -------
        GoSlot : int
        GoPosition : str
        ReturnSlot : int
        ReturnPosition : str
        Turns : int
        """
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.connection.send_and_receive(method, params)

    def check_if_geometry_is_valid(self, edit_geometry):
        """Check if Motor-CAD geometry is valid.

        Returns
        -------
        int
            1 indicates valid geometry
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Graphs ------------------------------------

    def load_magnetisation_curves(self, file_path):
        """Load the magnetisation curves from a text file.

        Parameters
        ----------
        file_path : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadMagnetisationCurves"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def save_magnetisation_curves(self, file_name):
        """Save the magnetisation curves to a text file.

        Parameters
        ----------
        file_name : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "SaveMagnetisationCurves"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD Magnetic graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_temperature_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD Thermal graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_power_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_3d_graph_point(self, graph_name, slice_number, point_number, time_step_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graph_name}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    def get_fea_graph_point(self, graph_id, slice_number, point_number, time_step_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_id : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graph_id}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ FEA ------------------------------------

    def set_power_injection_value(self, name, node1, value, rpm_ref, rpm_coef, description):
        """Set or creates a power injection."""
        method = "SetPowerInjectionValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def set_fixed_temperature_value(self, name, node1, value, description):
        """Set or creates a fixed temperature on a node."""
        method = "SetFixedTemperatureValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_fixed_temperature_value(self, node1):
        """Remove a fixed temperature from a node."""
        method = "ClearFixedTemperatureValue"
        params = [node1]
        return self.connection.send_and_receive(method, params)

    def do_slot_finite_element(self):
        """Carry out slot finite element analysis."""
        method = "DoSlotFiniteElement"
        return self.connection.send_and_receive(method)

    def clear_all_data(self):
        """Clear data and initialise FEA."""
        method = "ClearAllData"
        return self.connection.send_and_receive(method)

    def create_optimised_mesh(self):
        """Create FEA geometry and mesh.

        Call at the end of creating custom scripting geometry.
        """
        method = "CreateOptimisedMesh"
        return self.connection.send_and_receive(method)

    def add_arc_boundary_rt(
        self, direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add boundary condition arc using RT coordinates for centre."""
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_arc_boundary_xy(
        self, direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add boundary condition arc using XY coordinates for centre."""
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_rt(self, rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code):
        """Add boundary condition line using RT coordinates for start and end points."""
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_xy(self, xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code):
        """Add boundary condition line using XY coordinates for start and end points."""
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
        """Add/edit a point in the path editor."""
        method = "SetFEAPathPoint"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x,
            tor_y,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_arc(
        self,
        path_name,
        path_location,
        r,
        theta_start,
        theta_end,
        points,
        fea_method,
        calculation,
        expression,
    ):
        """Add/edit an arc in the path editor."""
        method = "SetFEAPathArc"
        params = [
            path_name,
            path_location,
            r,
            theta_start,
            theta_end,
            points,
            fea_method,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_line(
        self,
        path_name,
        path_location,
        coord_system,
        ror_x_start,
        tor_y_start,
        ror_x_end,
        tor_y_end,
        points,
        calculation,
        expression,
    ):
        """Add/edit a line in the path editor."""
        method = "SetFEAPathLine"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x_start,
            tor_y_start,
            ror_x_end,
            tor_y_end,
            points,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def save_fea_data(self, file, first_step, final_step, outputs, regions, separator):
        """Save raw data for open FEA solution."""
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.connection.send_and_receive(method, params)

    def get_region_value(self, expression, region_name):
        """Calculate the integral value for given expression of the region."""
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.connection.send_and_receive(method, params)

    def get_region_loss(self, expression, region_name, radius1, radius2, angle1, angle2):
        """Calculate the loss value for given expression of the region.

        Region bounded by radii and angles specified.
        Radii and angle values of 0 will give all region losses.
        Losses calculated are for per unit length and are only for the FEA areas modelled
        (for total losses require to multiply by symmetry factor).
        Valid for magnetic solution only.
        """
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.connection.send_and_receive(method, params)

    def edit_magnet_region(self, region_name, magnet_material, br_angle, br_multiplier):
        """Edit the specified magnet region.

        Parameters
        ----------
        region_name : str
            Name of magnet region to edit
        magnet_material : str
            Sets magnet material
        br_angle : float
            Sets Br angle of magnet
        br_multiplier : float
            Sets Br multiplier for magnet
        """
        method = "EditMagnetRegion"
        params = [region_name, magnet_material, br_angle, br_multiplier]
        return self.connection.send_and_receive(method, params)

    def delete_regions(self, region_name):
        """Delete a comma separated list of named regions or all regions if left empty.

        If region to be deleted contains a space, the region name should be enclosed in
        double quotation marks (e.g. "Rotor Pocket").
        """
        method = "DeleteRegions"
        params = [region_name]
        return self.connection.send_and_receive(method, params)

    def reset_regions(self):
        """Reset custom FEA regions to standard regions from Motor-CAD template geometry."""
        method = "ResetRegions"
        return self.connection.send_and_receive(method)

    def get_point_value(self, parameter, x, y):
        """Get a specified point from Motor-CAD FEA.

        Parameters
        ----------
        parameter : str|int
            Motor-CAD shading function
        x : float
            x value
        y : float
            y value

        Returns
        -------
        value : float
            value from FEA
        units : string
            units of parameter
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Custom Geometry ------------------------------------
    def initiate_geometry_from_script(self):
        """Tells Motor-CAD to use geometry from scripting.

        Also clears current scripting geometry.
        Need to call clear_all_data before doing this.
        """
        method = "InitiateGeometryFromScript"
        return self.connection.send_and_receive(method)

    def add_line_xy(self, x_start, y_start, x_end, y_end):
        """Add line to Motor-CAD axial geometry with x and y coordinate system.

        Parameters
        ----------
        x_start : float
            start position x coordinate
        y_start : float
            start position y coordinate
        x_end : float
            end position x coordinate
        y_end : float
            end position y coordinate
        """
        method = "AddLine_XY"
        params = [x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_line_rt(self, radius_start, theta_start, radius_end, theta_end):
        """Add line to Motor-CAD axial geometry with rt (polar) coordinate system.

        Use degrees for angles.

        Parameters
        ----------
        radius_start : float
            start position radial coordinate
        theta_start : float
            start position angular coordinate (degrees)
        radius_end : float
            end position radial coordinate
        theta_end : float
            end position angular coordinate (degrees)
        """
        method = "AddLine_RT"
        params = [radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_xy(self, x_centre, y_centre, theta_start, theta_end, radius):
        """Add arc to Motor-CAD axial geometry with x and y coordinate system.

        Uses centre point, radius and angles. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            centre position x coordinate
        y_centre : float
            centre position x coordinate
        theta_start : float
            angular coordinate of arc start point (degrees)
        theta_end : float
            angular coordinate of arc end point (degrees)
        radius : float
            radius of arc from centre point
        """
        method = "AddArc_XY"
        params = [x_centre, y_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_rt(self, radius_center, theta_centre, theta_start, theta_end, radius):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses centre point, radius and angles. Use degrees for angles.

        Parameters
        ----------
        radius_center : float
            centre position radial coordinate
        theta_centre : float
            centre position angular coordinate
        theta_start : float
            angular coordinate of arc start point (degrees)
        theta_end : float
            angular coordinate of arc end point (degrees)
        radius : float
            radius of arc from centre point
        """
        method = "AddArc_RT"
        params = [radius_center, theta_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_xy(self, x_centre, y_centre, x_start, y_start, x_end, y_end):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses start, end, centre coordinates. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            centre position x coordinate
        y_centre : float
            centre position y coordinate
        x_start : float
            start position x coordinate
        y_start : float
            start position y coordinate
        x_end : float
            end position x coordinate
        y_end : float
            end position y coordinate
        """
        method = "AddArc_CentreStartEnd_XY"
        params = [x_centre, y_centre, x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_rt(
        self, radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end
    ):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses start, end, centre coordinates. Use degrees for angles.

        Parameters
        ----------
        radius_centre : float
            centre position radial coordinate
        theta_centre : float
            centre position angular coordinate (degrees)
        radius_start : float
            start position radial coordinate
        theta_start : float
            start position angular coordinate (degrees)
        radius_end : float
            end position radial coordinate
        theta_end : float
            end position angular coordinate (degrees)
        """
        method = "AddArc_CentreStartEnd_RT"
        params = [radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_region_xy(self, x, y, region_name):
        """Add region to Motor-CAD geometry - overwrites existing region if already exists.

        Use x,y coordinate system.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        """
        method = "AddRegion_XY"
        params = [x, y, region_name]
        return self.connection.send_and_receive(method, params)

    def add_region_rt(self, radius, theta, region_name):
        """Add region to Motor-CAD geometry - overwrites existing region if already exists.

        Use r,t coordinate system. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        """
        method = "AddRegion_RT"
        params = [radius, theta, region_name]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_xy(
        self, x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add magnet region to Motor-CAD geometry - overwrites existing region if already exists.

        Use x,y coordinate system. Use degrees for angles.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        magnet_material : string
            magnet material to use
        br_angle : float
            magnet angle  (degrees)
        br_multiplier : float
            magnet Br multiplier, default is 1
        polarity_code : integer
            magnet polarity. 0 is north, 1 is south
        """
        method = "AddMagnetRegion_XY"
        params = [x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_rt(
        self, radius, theta, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add magnet region to Motor-CAD geometry - overwrites existing region if already exists.

        Use r,t coordinate system. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        magnet_material : string
            magnet material to use
        br_angle : float
            magnet angle (degrees)
        br_multiplier : float
            magnet Br multiplier, default is 1
        polarity_code : integer
            magnet polarity. 0 is north, 1 is south
        """
        method = "AddMagnetRegion_RT"
        params = [
            radius,
            theta,
            region_name,
            magnet_material,
            br_angle,
            br_multiplier,
            polarity_code,
        ]
        return self.connection.send_and_receive(method, params)

    def _get_region_properties_xy(self, x, y):
        """Get properties of region from name and coordinates.

        Returns list of parameters. Currently only used for testing other geometry functions.
        EXPERIMENTAL FUNCTION - LIKELY TO CHANGE.
        """
        method = "GetRegionProperties_XY"
        params = [x, y]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_xy(self, x, y, region_name, material_name, colour):
        """Add region to geometry and specify material.

        Not for adding magnets. Use add_magnet_region_xy for this.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        material_name : string
            name of material. Motor-CAD material names can be found in Input Data -> materials.
            Material type (laminated/solid/air) is set automatically.

        colour : string
            VCL colour as a string (see https://wiki.freepascal.org/Colors)
            This can be a hexadecimal value e.g. "$008000" or a colour name e.g. "clGreen"
        """
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_rt(self, radius, theta, region_name, material_name, colour):
        """Add region to geometry and specify material.

        Not for adding magnets. Use add_magnet_region_rt for this. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        material_name : string
            name of material. Motor-CAD material names can be found in Input Data -> materials.
            Material type (laminated/solid/air) is set automatically.

        colour : string
            VCL colour as a string (see https://wiki.freepascal.org/Colors)
            This can be a hexadecimal value e.g. "$008000" or a colour name e.g. "clGreen"
        """
        method = "AddPoint_CustomMaterial_RT"
        params = [radius, theta, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Thermal ------------------------------------

    def set_resistance_value(self, name, node1, node2, value, description):
        """Set or create a resistance."""
        method = "SetResistanceValue"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def set_resistance_multiplier(self, name, node1, node2, value, description):
        """Set or create a resistance muliplication factor."""
        method = "SetResistanceMultiplier"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_external_circuit(self):
        """Clear the external circuit."""
        method = "ClearExternalCircuit"
        return self.connection.send_and_receive(method)

    def create_new_node(self, name, node1, row, column, colour, description):
        """Create a new node."""
        method = "CreateNewNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def modify_node(self, name, node1, row, column, colour, description):
        """Modify an existing node."""
        method = "ModifyNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def set_capacitance_value(self, name, node1, value, description):
        """Set or create a capacitance."""
        method = "SetCapacitanceValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def set_power_source_value(self, name, node1, value, rpm_ref, rpm_coef, description):
        """Set or create a power source."""
        method = "SetPowerSourceValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def load_external_circuit(self, circuit_file_name):
        """Load an external circuit from a file."""
        method = "LoadExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_external_circuit(self, circuit_file_name):
        """Save the external circuit to a file."""
        method = "SaveExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_power_values(self, file_name):
        """Save transient power results in a csv file."""
        method = "SaveTransientPowerValues"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_temperatures(self, file_name):
        """Save transient temperature results in a csv file."""
        method = "SaveTransientTemperatures"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def remove_external_component(self, component_type, name, node1):
        """Remove an external circuit component (e.g. Resistance, Power Source, Power Injection)."""
        method = "RemoveExternalComponent"
        params = [component_type, name, node1]
        return self.connection.send_and_receive(method, params)

    def get_node_temperature(self, node_number):
        """Get the temperature of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        float
            Temperature of thermal node
        """
        method = "GetNodeTemperature"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_capacitance(self, node_number):
        """Get the capacitance of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        float
            Capacitance of thermal node
        """
        method = "GetNodeCapacitance"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_power(self, node_number):
        """Get the power of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        float
            Power of thermal node
        """
        method = "GetNodePower"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_to_node_resistance(self, node1, node2):
        """Get node to node resistance.

        Parameters
        ----------
        node1 : int
            Thermal node number
        node2 : int
            Thermal node number
        Returns
        -------
        float
            Resistance value
        """
        method = "GetNodeToNodeResistance"
        params = [node1, node2]
        return self.connection.send_and_receive(method, params)

    def get_node_exists(self, node_number):
        """Check if node exists.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        boolean
            True if node exists
        """
        method = "GetNodeExists"
        params = [node_number]
        node_exists = self.connection.send_and_receive(method, params, success_var=False)
        return node_exists

    def get_offset_node_number(self, node_number, slice_number, cuboid_number):
        """Get offset node number.

        Parameters
        ----------
        node_number  : int
            node number
        slice_number : int
            slice number
        cuboid_number : int
            cuboid number

        Returns
        -------
        int
            offset node number
        """
        method = "GetOffsetNodeNumber"
        params = [node_number, slice_number, cuboid_number]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Materials ------------------------------------

    def set_fluid(self, cooling_type, fluid):
        """Set fluid for specified cooling type.

        Cooling types: InternalFluid, ExternalFluid, ShaftSGFluid, RotorWJFluid, SlotWJFluid,
        HousingWJFluid, WetRotorFluid, SprayCoolingFluid, Spray_RadialHousing_Fluid, TVentFluid.
        """
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.connection.send_and_receive(method, params)

    def set_component_material(self, component_name, material_name):
        """Set the solid material properties of the named component from the materials database.

        Component names are found under Input Data -> Materials (Component column).
        """
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.connection.send_and_receive(method, params)

    def get_component_material(self, component_name):
        """Get the current solid material name of the named component.

        Component names are found under Input Data -> Materials (Component column).
        """
        method = "GetComponentMaterial"
        params = [component_name]
        return self.connection.send_and_receive(method, params)

    def import_solid_material(self, file_name, material_name):
        """Import the solid material from the materials database."""
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def export_solid_material(self, file_name, material_name):
        """Export the solid material to the materials database."""
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def delete_solid_material(self, material_name):
        """Delete the solid material from the materials database."""
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_iron_loss_coefficients(self, material_name):
        """Calculate and return iron loss coefficients for the specified material."""
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_iron_loss_coefficients(self, material_name):
        """Save the calculated iron loss coefficients to the solids database."""
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_magnet_parameters(self, material_name):
        """Calculate parameters for nonlinear demagnetisation model."""
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_magnet_parameters(self, material_name):
        """Save the calculated magnet parameters of the selected material to the solids database."""
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)
