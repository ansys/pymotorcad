"""RPC methods for files."""


class _RpcMethodsFiles:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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
