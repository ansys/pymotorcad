"""RPC methods (general)."""


class _RpcMethodsGeneral:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def load_duty_cycle(self, file_name):
        """Load a duty cycle from a DAT file.

        Parameters
        ----------
        file_name : str
            Name of the DAT file with the duty cycle to load. The default
            directory is the one with the MOT file. To use a different
            directory, specify the absolute filepath to the DAT file.
            Use the ``r'filepath'`` syntax to force Python to ignore
            special characters.
        """
        method = "LoadDutyCycle"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_duty_cycle(self, file_path):
        """Save the duty cycle to a DAT file.

        The duty cycle should be saved to a file with a DAT extension to ensure
        that it can be correctly loaded into a MOT file.

        Parameters
        ----------
        file_path : str
            Filepath for saving the DAT file. The default directory is
            the one with the MOT file. To use a different directory,
            specify the absolute filepath. Use the ``r'filepath'`` syntax
            to force Python to ignore special characters.
        """
        method = "SaveDutyCycle"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def clear_duty_cycle(self):
        """Clear the duty cycle in both the lab and thermal contexts."""
        method = "ClearDutyCycle"
        return self.connection.send_and_receive(method)

    def export_matrices(self, directory_path):
        """Export the resistance, power, and capacitance matrices to files.

        The files are given the same name as the MOT model, with different
        file extensions.

        Parameters
        ----------
        directory_path : str
            Directory for exporting the files. The default is the root
            directory. To use a different directory, specify the absolute
            filepath. Use the ``r'filepath'`` syntax to force Python to
            ignore special characters.
        """
        method = "ExportMatrices"
        params = [directory_path]
        return self.connection.send_and_receive(method, params)

    def load_custom_drive_cycle(self, file_path):
        """Load a custom waveform from a file.

        Parameters
        ----------
        file_path : str
            Filepath for loading the file with the custom waveform.
            Use the ``r'filepath'`` syntax to force Python to ignore
            special characters.
        """
        method = "LoadCustomDriveCycle"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_fea_result(self, file_path, solution_number):
        """Load an existing FEA solution to allow viewing of FEA results.

        Parameters
        ----------
        file_path : str
            Filepath for loading the file with the existing FEA solution.
            Use the ``r'filepath'`` syntax to force Python to ignore
            special characters.
        solution_number : int
        """
        method = "LoadFEAResult"
        params = [file_path, solution_number]
        return self.connection.send_and_receive(method, params)

    def export_to_ansys_electronics_desktop(self, file_path):
        """Export the model to a VBS script file that can run in Ansys Electronics Desktop.

        Parameters
        ----------
        file_path : str
            Absolute filepath for the VSB script file. The default filepath
            is the Windows directory on the C: drive. The filepath must include
            the name of the file. To specify a different filepath, use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "ExportToAnsysElectronicsDesktop"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_results(self, solution_type, file_path):
        """Export results from a solution to a CSV file.

        Parameters
        ----------
        solution_type : str
            Type of the solution. Options are ``'SteadyState'`` (Steady State Thermal Solution),
            ``'Transient'`` (Transient Thermal Solution), ``'EMagnetic'`` (E-Magnetic Solution), and
            ``'Lab'`` (Lab Operating Point Solution).
        file_path : str
            Absolute filepath for the CSV file. The default is the Windows
            directory on the C: drive. The filepath must include the name
            of the file, with a CSV extension. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "ExportResults"
        params = [solution_type, file_path]
        return self.connection.send_and_receive(method, params)

    def load_dxf_file(self, file_name):
        """Load a DXF geometry file.

        Parameters
        ----------
        file_name : str
            Name of the DXF file. Use r'filepath' syntax to force Python
            to ignore special characters.
        """
        method = "LoadDXFFile"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def create_report(self, file_path, template_file_path):
        """Create a Word report of the report tree structure.

        Parameters
        ----------
        file_path : str
            Filepath for the Word report. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        template_file_path : str
            Filepath for the template file. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "CreateReport"
        params = [file_path, template_file_path]
        return self.connection.send_and_receive(method, params)

    def load_report_structure(self, file_path):
        """Load the tree structure of the report from a file.

        Parameters
        ----------
        file_path : str
            Filepath for the file with the tree structure of the
            report. Use the ``r'filepath'`` syntax to force Python
            to ignore special characters.
        """
        method = "LoadReportStructure"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_force_animation(self, animation, file_name):
        """Export a force animation to a GIF file.

        Animation is exported from the caption name. For example,
        ``"Radial OL"`` or ``"Radial OL (12th harmonic)"``.

        Parameters
        ----------
        animation : str
            Animation name.
        file_name : str
            Name for the GIF file. Use the ``r'filepath'`` syntax
            to force Python to ignore special characters.
        """
        method = "ExportForceAnimation"
        params = [animation, file_name]
        return self.connection.send_and_receive(method, params)

    def load_report_tree(self):
        """Load the report with the tree structure of the modules and components."""
        method = "LoadReportTree"
        return self.connection.send_and_receive(method)

    def load_template(self, template_name):
        """Load a motor template.

        Parameters
        ----------
        template_name : str
            Name of the template, which is given in the **Template** column when
            selecting **File -> Open Template** in Motor-CAD. For example, ``"a1"``
            or ``"e9"``.
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
        """Save the template to an MTT template file.

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
            Absolute filepath of the text file to load. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "LoadWindingPattern"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def save_winding_pattern(self, file_path):
        """Save the winding pattern to a file.

        Parameters
        ----------
        file_path : str
            Absolute filepath for the file. The default filepath is the
            Windows directory on the C: drive. The filepath must include
            the name of the file. If the file is to be re-loaded into
            Motor-CAD, the file extension must be TXT. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "SaveWindingPattern"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_multi_force_data(self, file_name):
        """Export calculated multiforce data to a file.

        Parameters
        ----------
        file_name : str
            Name of the file. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "ExportMultiForceData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def geometry_export(self):
        """Export the geometry to the file specified in the ``DXFFileName`` parameter."""
        method = "GeometryExport"
        return self.connection.send_and_receive(method)

    def export_to_ansys_discovery(self, file_path):
        """Export the model to a Python script file that can be run in Ansys Discovery.

        Parameters
        ----------
        file_path : str
            Absolute filepath for the Python script file. The default
            filepath is the Windows directory on the C: drive. The
            filepath must include the name of the file. The extension
            does not need to be specified. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "ExportToAnsysDiscovery"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def export_nvh_results_data(self, file_name):
        """Export NVH results data to a file.

        Parameters
        ----------
        file_name : str
            Name of the file. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "ExportNVHResultsData"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def load_from_file(self, mot_file):
        """Load a MOT file into the Motor-CAD instance.

        Parameters
        ----------
        mot_file : str
            Full path to the MOT file, including the file name.
            Use the ``r'filepath'`` syntax to force Python to ignore special characters.
        """
        method = "LoadFromFile"
        params = [mot_file]
        return self.connection.send_and_receive(method, params)

    def save_to_file(self, mot_file):
        """Save the MOT file.

        Parameters
        ----------
        mot_file : str
            Full path to file, including file name. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "SaveToFile"
        if not isinstance(mot_file, str):
            mot_file = str(mot_file)
        params = [mot_file]
        return self.connection.send_and_receive(method, params)

    def save_results(self, solution_type):
        """Save the output results from an ``"EMagnetic"`` solution.

        This method supports only ``"EMagnetic"`` solutions.

        Parameters
        ----------
        solution_type : str
            Soultion type, which must be ``"EMagnetic"``.
        """
        method = "SaveResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def load_results(self, solution_type):
        """Load the output results from an ``"EMagnetic"`` solution.

        This method supports only ``"EMagnetic"`` solution.

        Parameters
        ----------
        solution_type : str
            Soultion type, which must be ``"EMagnetic"``.
        """
        method = "LoadResults"
        params = [solution_type]
        return self.connection.send_and_receive(method, params)

    def load_magnetisation_curves(self, file_path):
        """Load the magnetization curves from a text file.

        This method is for switched reluctance machines (SRMs) only.

        Parameters
        ----------
        file_path : str
            Full path to the text file, including the file name. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "LoadMagnetisationCurves"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def save_magnetisation_curves(self, file_name):
        """Save the magnetisation curves to a text file.

        This method is for switched reluctance machines (SRMs) only.

        Parameters
        ----------
        file_name : str
            Full path to the text file, including file name. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "SaveMagnetisationCurves"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def get_messages(self, num_messages):
        """Get a list of the last *N* messages from the message history.

        Parameters
        ----------
        num_messages : int
            Number of last messages to get. If is parameter is set to
            ``0``, all messages in the history are returned.

        Returns
        -------
        List
            List of messages.
        """
        method = "GetMessages"
        params = [num_messages]
        messages = self.connection.send_and_receive(method, params)
        return messages.split(";")

    def get_licence(self):
        """Check if a license is available for the current context and machine type.

        If such a license is available, it is checked out.
        """
        method = "GetLicence"
        return self.connection.send_and_receive(method)

    def get_license(self):
        """Check if a license is available for the current context and machine type.

        .. note::
           This method is deprecated. Use the :func:`MotorCAD.get_licence` method.
        """
        method = "GetLicence"
        return self.get_licence()

    def clear_message_log(self):
        """Clear the message log file for the model."""
        method = "ClearMessageLog"
        return self.connection.send_and_receive(method)

    def quit(self):
        """Quit Motor-CAD."""
        self.connection._quit()

    def set_free(self):
        """Free the Motor-CAD instance."""
        return self.connection._set_free()

    def download_mot_file(self, file_path):
        """Download the current .mot file from Motor-CAD and write it to a local directory.

        This allows users to download .mot files to a local directory from a Motor-CAD instance
        on a remote machine. Equivalent of :func:`save_file` for remote machines.

        Parameters
        ----------
        file_path : str
            Full path to the mot file, including the file name and .mot extension.
            Use the ``r'filepath'`` syntax to force Python to ignore special characters.
        """
        self.connection.ensure_version_at_least("2023.2")
        method = "GetCurrentFileJSON"
        file_contents = self.connection.send_and_receive(method)

        with open(file_path, "w") as mot_file:
            for line in file_contents:
                mot_file.write(line + "\n")

    def upload_mot_file(self, file_path):
        """Upload a .mot file to Motor-CAD instance from local directory.

        This allows users to send .mot files from a local directory to a Motor-CAD instance
        on a remote machine. Equivalent of :func:`load_file` for remote machines.

        Parameters
        ----------
        file_path : str
            Full path to the mot file, including the file name and .mot extension.
            Use the ``r'filepath'`` syntax to force Python to ignore special characters.
        """
        self.connection.ensure_version_at_least("2023.2")
        file_contents = []
        with open(file_path, "r") as mot_file:
            for line in mot_file:
                file_contents += [line.replace("\n", "")]

        method = "SetCurrentFileJSON"
        params = [file_contents]
        self.connection.send_and_receive(method, params)
