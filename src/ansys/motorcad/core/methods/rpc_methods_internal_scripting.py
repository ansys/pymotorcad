"""RPC methods for Motor-CAD internal scripting."""


class _RpcMethodsInternalScripting:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def save_script(self, file_path):
        """Save the internal Python script to a Python file.

        Parameters
        ----------
        file_path : str
            Absolute filepath for the Python file, including the file
            name and a PY extension. The default filepath is the
            Windows directory on the C: drive. Use the ``r'filepath'``
            syntax to force Python to ignore special characters.
        """
        method = "SaveScript"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def load_script(self, script_file):
        """Load a script file into Motor-CAD's internal scripting.

        Parameters
        ----------
        script_file : str
            Full path to the script file, including the file name.
            Use the ``r'filepath'`` syntax to force Python to ignore
            special characters.
        """
        method = "LoadScript"
        params = [script_file]
        return self.connection.send_and_receive(method, params)

    def run_script(self):
        """Run the script file in Motor-CAD's internal scripting."""
        method = "RunScript"
        return self.connection.send_and_receive(method)
