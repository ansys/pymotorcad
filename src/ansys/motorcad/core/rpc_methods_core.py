"""Contains all the JSON-RPC API calls for Motor-CAD.

Not for direct use. Inherited by _MotorCADCore/_RpcMethodsCoreOld
"""

from packaging import version


class _RpcMethodsCore:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    # ------------------------------------ Variables ------------------------------------
    def get_array_variable_2d(self, array_name, array_index1, array_index2):
        method = "GetArrayVariable_2d"
        params = [array_name, array_index1, array_index2]
        return self.connection.send_and_receive(method, params)

    def set_array_variable_2d(self, array_name, array_index1, array_index2, new_value):
        method = "SetArrayVariable_2d"
        params = [array_name, array_index1, array_index2, {"variant": new_value}]
        return self.connection.send_and_receive(method, params)

    def restore_compatibility_settings(self):
        method = "RestoreCompatibilitySettings"
        return self.connection.send_and_receive(method)

    def get_variable(self, variable_name):
        """Get a MotorCAD variable.

        Parameters
        ----------
        variable_name : str
            Name of variable

        Returns
        -------
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetVariable"
        params = [variable_name]
        return self.connection.send_and_receive(method, params)

    def get_array_variable(self, array_name, array_index):
        """Get a MotorCAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
        array_index : int
            Position variable in array

        Returns
        -------
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetArrayVariable"
        params = [array_name, array_index]
        return self.connection.send_and_receive(method, params)

    def set_variable(self, variable_name, variable_value):
        """Set a MotorCAD variable.

        Parameters
        ----------
        variable_name : str
            Name of variable
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetVariable"
        params = [variable_name, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    def set_array_variable(self, array_name, array_index, variable_value):
        """Set a MotorCAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
        array_index : int
            Position in array
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetArrayVariable"
        params = [array_name, array_index, {"variant": variable_value}]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ UI ------------------------------------

    def is_stop_requested(self):
        method = "IsStopRequested"
        return self.connection.send_and_receive(method)

    def disable_error_messages(self, active):
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
        messages : str
            List of messages (most recent first, separated by ;)
        """
        method = "GetMessages"
        params = [num_messages]
        return self.connection.send_and_receive(method, params)

    def update_interface(self):
        method = "UpdateInterface"
        return self.connection.send_and_receive(method)

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

    def avoid_immediate_update(self, avoid_update):
        method = "AvoidImmediateUpdate"
        params = [{"variant": avoid_update}]
        return self.connection.send_and_receive(method, params)

    def clear_message_log(self):
        method = "ClearMessageLog"
        return self.connection.send_and_receive(method)

    def show_message(self, message):
        """Display a message in the MotorCAD message window.

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
        """Quit MotorCAD."""
        method = "Quit"
        return self.connection.send_and_receive(method)

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
        method = "LoadDutyCycle"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_duty_cycle(self, file_name):
        method = "SaveDutyCycle"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def export_matrices(self, file_name):
        method = "ExportMatrices"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def load_custom_drive_cycle(self, file_name):
        method = "LoadCustomDriveCycle"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def load_fea_result(self, file_name, solution_number):
        method = "LoadFEAResult"
        params = [file_name, solution_number]
        return self.connection.send_and_receive(method, params)

    def export_to_ansys_electronics_desktop(self, file_name):
        method = "ExportToAnsysElectronicsDesktop"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def export_results(self, solution_type, file_name):
        method = "ExportResults"
        params = [solution_type, file_name]
        return self.connection.send_and_receive(method, params)

    def load_dxf_file(self, file_name):
        method = "LoadDXFFile"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def create_report(self, file_path, template_file_path):
        method = "CreateReport"
        params = [file_path, template_file_path]
        return self.connection.send_and_receive(method, params)

    def load_report_structure(self, file_path):
        method = "LoadReportStructure"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_force_animation(self, animation, file_name):
        method = "ExportForceAnimation"
        params = [animation, file_name]
        return self.connection.send_and_receive(method, params)

    def load_report_tree(self):
        method = "LoadReportTree"
        return self.connection.send_and_receive(method)

    def load_template(self, template_name):
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

    def load_winding_pattern(self, file_name):
        method = "LoadWindingPattern"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_winding_pattern(self, file_name):
        method = "SaveWindingPattern"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def export_multi_force_data(self, file_name):
        method = "ExportMultiForceData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def geometry_export(self):
        method = "GeometryExport"
        return self.connection.send_and_receive(method)

    def export_to_ansys_discovery(self, file_name):
        method = "ExportToAnsysDiscovery"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def export_nvh_results_data(self, file_name):
        method = "ExportNVHResultsData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def load_from_file(self, mot_file):
        """Load a .mot file into the MotorCAD instance.

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

    def save_script(self, file_name):
        method = "SaveScript"
        params = [file_name]
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
        method = "ClearDutyCycle"
        return self.connection.send_and_receive(method)

    def do_magnetic_thermal_calculation(self):
        method = "DoMagneticThermalCalculation"
        return self.connection.send_and_receive(method)

    def get_im_sat_factor(self, i_mag):
        """NO SUCCESS VARIABLE.

        Returns
        -------
        satFactor : real
            Saturation Factor
        """
        method = "GetIMSaturationFactor"
        params = [i_mag]
        return self.connection.send_and_receive(method, params, success_var=False)

    def get_im_iron_loss(self, slip, back_emf):
        method = "GetIMIronLoss"
        params = [slip, back_emf]
        return self.connection.send_and_receive(method, params)

    def set_3d_component_visibility(self, group_name, component_name, visibility):
        method = "Set3DComponentVisibility"
        params = [group_name, component_name, visibility]
        return self.connection.send_and_receive(method, params)

    def set_all_emag_calculations(self, state):
        method = "SetAllEmagCalculations"
        params = [state]
        return self.connection.send_and_receive(method, params)

    def calculate_saturation_map(self):
        method = "CalculateSaturationMap"
        return self.connection.send_and_receive(method)

    def calculate_torque_envelope(self):
        method = "CalculateTorqueEnvelope"
        return self.connection.send_and_receive(method)

    def save_results(self, solution_type):
        method = "SaveResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def load_results(self, solution_type):
        method = "LoadResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def calculate_im_saturation_model(self):
        method = "CalculateIMSaturationModel"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_spatial(self):
        method = "CalculateForceHarmonics_Spatial"
        return self.connection.send_and_receive(method)

    def calculate_force_harmonics_temporal(self):
        method = "CalculateForceHarmonics_Temporal"
        return self.connection.send_and_receive(method)

    def get_force_frequency_domain_amplitude(self, row, column, load_point):
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, load_point]
        return self.connection.send_and_receive(method, params)

    def update_force_analysis_results(self, fft_data_type):
        method = "UpdateForceAnalysisResults"
        params = [fft_data_type]
        return self.connection.send_and_receive(method, params)

    def do_multi_force_calculation(self):
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
        method = "CalculateTestPerformance_Lab"
        return self.connection.send_and_receive(method)

    def export_duty_cycle_lab(self):
        method = "ExportDutyCycle_Lab"
        return self.connection.send_and_receive(method)

    def get_model_built_lab(self):
        method = "GetModelBuilt_Lab"
        return self.connection.send_and_receive(method)

    def show_results_viewer_lab(self, calculation_type):
        method = "ShowResultsViewer_Lab"
        params = [calculation_type]
        return self.connection.send_and_receive(method, params)

    def export_figure_lab(self, calculation_type, variable, file_name):
        method = "ExportFigure_Lab"
        params = [calculation_type, variable, file_name]
        return self.connection.send_and_receive(method, params)

    def calculate_generator_lab(self):
        method = "CalculateGenerator_Lab"
        return self.connection.send_and_receive(method)

    def load_external_model_lab(self, file_name):
        method = "LoadExternalModel_Lab"
        params = [file_name]
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
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.connection.send_and_receive(method, params)

    def check_if_geometry_is_valid(self, edit_geometry):
        """Check if Motor-CAD geometry is valid.

        Returns
        -------
        success : int
            1 indicates valid geometry
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Graphs ------------------------------------

    def load_magnetisation_curves(self, file_name):
        method = "LoadMagnetisationCurves"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_magnetisation_curves(self, file_name):
        method = "SaveMagnetisationCurves"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph_point(self, graph_name, point_number):
        """Get a specified point from a MotorCAD Magnetic graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
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
        """Get a specified point from a MotorCAD Thermal graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
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
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
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
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
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
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_id : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
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
        method = "SetPowerInjectionValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def set_fixed_temperature_value(self, name, node1, value, description):
        method = "SetFixedTemperatureValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_fixed_temperature_value(self, node1):
        method = "ClearFixedTemperatureValue"
        params = [node1]
        return self.connection.send_and_receive(method, params)

    def do_slot_finite_element(self):
        method = "DoSlotFiniteElement"
        return self.connection.send_and_receive(method)

    def clear_all_data(self):
        method = "ClearAllData"
        return self.connection.send_and_receive(method)

    def add_line_xy(self, xs, ys, xe, ye):
        method = "AddLine_XY"
        params = [xs, ys, xe, ye]
        return self.connection.send_and_receive(method, params)

    def set_bnd_cnd(self, dir_code, c1, c2, c3):
        method = "SetBndCond"
        params = [dir_code, c1, c2, c3]
        return self.connection.send_and_receive(method, params)

    def store_problem_data(self, p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max):
        method = "StoreProblemData"
        params = [p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max]
        return self.connection.send_and_receive(method, params)

    def add_region_thermal_a(
        self,
        reg_name,
        thermal_conductivity,
        tcc,
        ref_temp,
        j_val,
        sigma,
        density,
        loss_density,
    ):
        method = "Add_Region_Thermal_A"
        params = [
            reg_name,
            thermal_conductivity,
            tcc,
            ref_temp,
            j_val,
            sigma,
            density,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def add_point_xy(self, x, y, reg_name):
        method = "AddPoint_XY"
        params = [x, y, reg_name]
        return self.connection.send_and_receive(method, params)

    def create_optimised_mesh(self):
        method = "CreateOptimisedMesh"
        return self.connection.send_and_receive(method)

    def create_optimised_mesh_thermal(self, copper_region, ins_region, impreg_region):
        method = "CreateOptimisedMesh_Thermal"
        params = [copper_region, ins_region, impreg_region]
        return self.connection.send_and_receive(method, params)

    def set_mesh_generator_param(self, max_bnd_length, bnd_factor, max_angle):
        method = "SetMeshGeneratorParam"
        params = [max_bnd_length, bnd_factor, max_angle]
        return self.connection.send_and_receive(method, params)

    def solve_problem(self):
        method = "SolveProblem"
        return self.connection.send_and_receive(method)

    def add_region_thermal(
        self, reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density
    ):
        method = "Add_Region_Thermal"
        params = [reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density]
        return self.connection.send_and_receive(method, params)

    def add_circular_conductor_a(
        self,
        xc,
        yc,
        copper_radius,
        ins_radius,
        ang_degree,
        points_no,
        mb,
        line,
        column,
        region_name,
        j_aux,
        loss_density,
    ):
        method = "AddCircularConductor_A"
        params = [
            xc,
            yc,
            copper_radius,
            ins_radius,
            ang_degree,
            points_no,
            mb,
            line,
            column,
            region_name,
            j_aux,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def add_rectangular_conductor_a(
        self,
        xc,
        yc,
        width,
        height,
        ins_width,
        ang_deg,
        points_no,
        mb,
        line,
        column,
        reg_name,
        j_aux,
        loss_density,
    ):
        method = "AddRectangularConductor_A"
        params = [
            xc,
            yc,
            width,
            height,
            ins_width,
            ang_deg,
            points_no,
            mb,
            line,
            column,
            reg_name,
            j_aux,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def add_arc_xy(self, xc, yc, th1, th2, r):
        method = "AddArc_XY"
        params = [xc, yc, th1, th2, r]
        return self.connection.send_and_receive(method, params)

    def set_region_colour(self, region, colour):
        method = "SetRegionColour"
        params = [region, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_rt(self, r, t, reg_name):
        method = "AddPoint_RT"
        params = [r, t, reg_name]
        return self.connection.send_and_receive(method, params)

    def add_line_rt(self, rs, ts, re, t_e):
        method = "AddLine_RT"
        params = [rs, ts, re, t_e]
        return self.connection.send_and_receive(method, params)

    def add_arc_rt(self, rc, tc, th1, th2, r):
        method = "AddArc_RT"
        params = [rc, tc, th1, th2, r]
        return self.connection.send_and_receive(method, params)

    def add_arc_boundary_rt(
        self, direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_arc_boundary_xy(
        self, direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_rt(self, rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code):
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_xy(self, xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code):
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def initiate_geometry_from_script(self):
        method = "InitiateGeometryFromScript"
        return self.connection.send_and_receive(method)

    def add_point_magnetic_rt(self, r, t, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_RT"
        params = [r, t, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)

    def add_point_magnetic_xy(self, x, y, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_XY"
        params = [x, y, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_rt(self, rc, tc, rs, ts, re, t_e):
        method = "AddArc_CentreStartEnd_RT"
        params = [rc, tc, rs, ts, re, t_e]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_xy(self, xc, yc, xs, ys, xe, ye):
        method = "AddArc_CentreStartEnd_XY"
        params = [xc, yc, xs, ys, xe, ye]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
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
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_xy(self, x, y, reg_name, mat_name, colour):
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, reg_name, mat_name, colour]
        return self.connection.send_and_receive(method, params)

    def get_region_value(self, expression, region_name):
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.connection.send_and_receive(method, params)

    def get_region_loss(self, expression, region_name, radius1, radius2, angle1, angle2):
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.connection.send_and_receive(method, params)

    def edit_magnet_region(self, region_name, magnet_material, br_angle, br_multiplier):
        method = "EditMagnetRegion"
        params = [region_name, magnet_material, br_angle, br_multiplier]
        return self.connection.send_and_receive(method, params)

    def add_region_xy(self, x, y, region_name):
        method = "AddRegion_XY"
        params = [x, y, region_name]
        return self.connection.send_and_receive(method, params)

    def add_region_rt(self, r, t, region_name):
        method = "AddRegion_RT"
        params = [r, t, region_name]
        return self.connection.send_and_receive(method, params)

    def delete_regions(self, region_name):
        method = "DeleteRegions"
        params = [region_name]
        return self.connection.send_and_receive(method, params)

    def reset_regions(self):
        method = "ResetRegions"
        return self.connection.send_and_receive(method)

    def add_magnet_region_rt(
        self, r, theta, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        method = "AddMagnetRegion_RT"
        params = [
            r,
            theta,
            region_name,
            magnet_material,
            br_angle,
            br_multiplier,
            polarity_code,
        ]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_xy(
        self, x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        method = "AddMagnetRegion_XY"
        params = [x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code]
        return self.connection.send_and_receive(method, params)

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

    # ------------------------------------ Thermal ------------------------------------

    def set_resistance_value(self, name, node1, node2, value, description):
        method = "SetResistanceValue"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def set_resistance_multiplier(self, name, node1, node2, value, description):
        method = "SetResistanceMultiplier"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_external_circuit(self):
        method = "ClearExternalCircuit"
        return self.connection.send_and_receive(method)

    def create_new_node(self, name, node1, row, column, colour, description):
        method = "CreateNewNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def modify_node(self, name, node1, row, column, colour, description):
        method = "ModifyNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def set_capacitance_value(self, name, node1, value, description):
        method = "SetCapacitanceValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def set_power_source_value(self, name, node1, value, rpm_ref, rpm_coef, description):
        method = "SetPowerSourceValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def load_external_circuit(self, circuit_file_name):
        method = "LoadExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_external_circuit(self, circuit_file_name):
        method = "SaveExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_power_values(self, file_name):
        method = "SaveTransientPowerValues"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_temperatures(self, file_name):
        method = "SaveTransientTemperatures"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def remove_external_component(self, component_type, name, node1):
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
        value : float
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
        value : float
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
        value : float
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
        value : float
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
        nodeExists : boolean
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
        offsetNodeNumber : int
            offset node number
        """
        method = "GetOffsetNodeNumber"
        params = [node_number, slice_number, cuboid_number]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Materials ------------------------------------

    def set_fluid(self, cooling_type, fluid):
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.connection.send_and_receive(method, params)

    def set_component_material(self, component_name, material_name):
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.connection.send_and_receive(method, params)

    def get_component_material(self, component_name):
        method = "GetComponentMaterial"
        params = [component_name]
        return self.connection.send_and_receive(method, params)

    def import_solid_material(self, file_name, material_name):
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def export_solid_material(self, file_name, material_name):
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.connection.send_and_receive(method, params)

    def delete_solid_material(self, material_name):
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_iron_loss_coefficients(self, material_name):
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_iron_loss_coefficients(self, material_name):
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def calculate_magnet_parameters(self, material_name):
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)

    def save_magnet_parameters(self, material_name):
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.connection.send_and_receive(method, params)
