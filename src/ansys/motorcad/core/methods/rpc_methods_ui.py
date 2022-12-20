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

    def set_motorlab_context(self):
        """Change Motor-CAD to Lab Context."""
        method = "SetMotorLABContext"
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
