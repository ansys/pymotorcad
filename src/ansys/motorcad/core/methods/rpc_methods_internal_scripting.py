"""RPC methods for Motor-CAD internal scripting."""


class _RpcMethodsInternalScripting:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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
