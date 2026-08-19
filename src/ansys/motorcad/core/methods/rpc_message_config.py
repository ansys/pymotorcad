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

"""RPC methods for updating message config."""
from ansys.motorcad.core.enums import MotorCADPopupDisplayLevel


class _RpcMessageConfig:
    def __init__(self, mc_connection):
        self._connection = mc_connection

    def enable_popups(self):
        """Enable the display of popups in Motor-CAD."""
        method = "EnablePopups"
        return self._connection.send_and_receive(method)

    def disable_popups(self):
        """Disable the display of popups in Motor-CAD."""
        method = "DisablePopups"
        return self._connection.send_and_receive(method)

    def get_popups_enabled(self):
        """Get whether popups are enabled in Motor-CAD.

        Returns
        -------
        bool
            Whether popups are enabled. If ``True``, popups are enabled. If ``False``,
            popups are disabled.
        """
        method = "GetPopupsEnabled"
        return self._connection.send_and_receive(method)

    def set_popup_display_level(self, level):
        """Set the display level of popups in Motor-CAD.

        Parameters
        ----------
        level : MotorCADPopupDisplayLevel
            The display level for popups. Values, ``1`` = info, ``2`` = warning, ``3`` = error,
              ``4`` = query.
        """
        method = "SetPopupDisplayLevel"
        params = [level]
        return self._connection.send_and_receive(method, params)

    def get_popup_display_level(self):
        """Get the display level of popups in Motor-CAD.

        Returns
        -------
        int
            The display level for popups. Values, ``1`` = info, ``2`` = warning, ``3`` = error,
             ``4`` = query.
        """
        method = "GetPopupDisplayLevel"
        return MotorCADPopupDisplayLevel(self._connection.send_and_receive(method))

    def enable_verbose_messages(self):
        """Enable the display of verbose messages in Motor-CAD."""
        method = "EnableVerboseMessages"
        return self._connection.send_and_receive(method)

    def disable_verbose_messages(self):
        """Disable the display of verbose messages in Motor-CAD."""
        method = "DisableVerboseMessages"
        return self._connection.send_and_receive(method)

    def get_verbose_messages_enabled(self):
        """Get whether verbose messages are enabled in Motor-CAD.

        Returns
        -------
        bool
            Whether verbose messages are enabled. If ``True``, verbose messages are enabled.
            If ``False``, verbose messages are disabled.
        """
        method = "GetVerboseMessagesEnabled"
        return self._connection.send_and_receive(method)

    def enable_verbose_fea_messages(self):
        """Enable the display of verbose FEA messages in Motor-CAD."""
        method = "EnableVerboseFEAMessages"
        return self._connection.send_and_receive(method)

    def disable_verbose_fea_messages(self):
        """Disable the display of verbose FEA messages in Motor-CAD."""
        method = "DisableVerboseFEAMessages"
        return self._connection.send_and_receive(method)

    def get_verbose_fea_messages_enabled(self):
        """Get whether verbose FEA messages are enabled in Motor-CAD.

        Returns
        -------
        bool
            Whether verbose FEA messages are enabled. If ``True``, verbose FEA messages are
            enabled. If ``False``, verbose FEA messages are disabled.
        """
        method = "GetVerboseFEAMessagesEnabled"
        return self._connection.send_and_receive(method)
