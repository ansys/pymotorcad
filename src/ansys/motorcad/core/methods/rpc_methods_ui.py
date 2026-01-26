# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""RPC methods for UI."""
from packaging import version


class _RpcMethodsUI:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def disable_error_messages(self, active):
        """Disable the display of error messages.

        Parameters
        ----------
        active : bool
            Whether to disable the display of error message. If ``True``,
            error messages are hidden. If ``False``, error messages are
            shown.
        """
        method = "DisableErrorMessages"
        params = [active]
        return self.connection.send_and_receive(method, params)

    def initialise_tab_names(self):
        """Initialize the available tabs in the Motor-CAD UI.

        Call this method prior to using the ``save_motorcad_screen_to_file`` or
        ``display_screen`` method. The Motor-CAD UI must be visible.
        """
        method = "InitialiseTabNames"
        return self.connection.send_and_receive(method)

    def save_motorcad_screen_to_file(self, screen_name, file_name):
        """Save the entire Motor-CAD screen of a tab to an image file.

        Call the ``initialise_tab_names`` method before you call this method. The
        Motor-CAD UI must be visible.

        Parameters
        ----------
        screen_name : str
            Path of the screen to save. The path must be in this format:
            ``"tabName;tabName;tabName"``. For example,
            ``"Geometry;Axial"``.
        file_name : str
            Full path for the image file, including the file name and file extension. The
            extensions supported are BMP, JPG, and PNG.
        """
        method = "SaveMotorCADScreenToFile"
        params = [screen_name, file_name]
        return self.connection.send_and_receive(method, params)

    def set_visible(self, visible):
        """Set the visibility of the Motor-CAD UI.

        Parameters
        ----------
        visible : bool
            Whether to show the Motor-CAD UI. When ``True``,
            the UI is shown. When ``False``, the UI is hidden.
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
            Message to display.
        """
        method = "ShowMessage"
        params = [message]
        return self.connection.send_and_receive(method, params)

    def show_magnetic_context(self):
        """Show the magnetic context in Motor-CAD."""
        method = "ShowMagneticContext"
        return self.connection.send_and_receive(method)

    def show_mechanical_context(self):
        """Show the mechanical context in Motor-CAD."""
        method = "ShowMechanicalContext"
        return self.connection.send_and_receive(method)

    def show_thermal_context(self):
        """Show the thermal context in Motor-CAD."""
        method = "ShowThermalContext"
        return self.connection.send_and_receive(method)

    def set_motorlab_context(self):
        """Change Motor-CAD to the lab context."""
        method = "SetMotorLABContext"
        return self.connection.send_and_receive(method)

    def display_screen(self, screen_name):
        """Display a screen within Motor-CAD.

        Parameters
        ----------
        screen_name : str
            Path of the screen to display. The path must be in this format:
            ``"tabName;tabName;tabName"``. For example,
            ``"Geometry;Axial"``.
        """
        method = "DisplayScreen"
        params = [screen_name]
        return self.connection.send_and_receive(method, params)

    def save_screen_to_file(self, screen_name, file_name):
        """Save the image from a Motor-CAD tab to an image file.

        This method is only available for select tabs (such as Geometry Radial and Axial tabs).

        Parameters
        ----------
        screen_name : str
            Name of the screen with the image to save. The name must be in this format:
            ``"tabName"``. For example, ``"Axial"``.
        file_name : string or pathlib.Path
            Full path for the image file, including the file name and file extension. The
            extensions supported are BMP, JPG, and PNG.
        """
        method = "SaveScreenToFile"
        params = [screen_name, str(file_name)]
        return self.connection.send_and_receive(method, params)

    def set_3d_component_visibility(self, group_name, component_name, visibility):
        """Set the visibility of a component by group name and component name.

        Parameters
        ----------
        group_name : str
            Name of the group. Options are ``"Machine"``, ``"Stator"``, ``"Rotor"``,
            and ``"Shaft Components"``. If the component is in the thermal context,
            ``"Mounting"`` and ``"Outer Casing"`` are also options.
        component_name : str
            Name of the component. The component names that are available depend
            on which model is used. Options include ``"All"``, ``"Lamination"``,
            and ``"Wedge"``.
        visibility : int
            Visibility level. Values range from ``0`` (invisible) to ``100`` (solid).
        """
        method = "Set3DComponentVisibility"
        params = [group_name, component_name, visibility]
        return self.connection.send_and_receive(method, params)

    def clear_messages(self):
        """Clear messages in the message display window."""
        self.connection.ensure_version_at_least("2024.2")
        method = "ClearMessages"
        params = []
        return self.connection.send_and_receive(method, params)
