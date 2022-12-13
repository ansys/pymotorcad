"""RPC methods for UI."""
from packaging import version


class _RpcMethodsUI:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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
        """Save the whole Motor-CAD screen of the specified tab as an image file, (bmp, jpg, png).

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
