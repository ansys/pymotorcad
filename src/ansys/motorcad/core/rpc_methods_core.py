# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Contains all the ``JSON-RPC`` API calls for Motor-CAD.

Not for direct use. Inherited by _MotorCADCore/_RpcMethodsCoreOld
"""

from ansys.motorcad.core.methods.adaptive_geometry import _RpcMethodsAdaptiveGeometry
from ansys.motorcad.core.methods.rpc_methods_calculations import _RpcMethodsCalculations
from ansys.motorcad.core.methods.rpc_methods_fea_geometry import _RpcMethodsFEAGeometry
from ansys.motorcad.core.methods.rpc_methods_general import _RpcMethodsGeneral
from ansys.motorcad.core.methods.rpc_methods_geometry import _RpcMethodsGeometry
from ansys.motorcad.core.methods.rpc_methods_graphs import _RpcMethodsGraphs
from ansys.motorcad.core.methods.rpc_methods_internal_scripting import _RpcMethodsInternalScripting
from ansys.motorcad.core.methods.rpc_methods_lab import _RpcMethodsLab
from ansys.motorcad.core.methods.rpc_methods_materials import _RpcMethodsMaterials
from ansys.motorcad.core.methods.rpc_methods_testing import _RpcMethodsTesting
from ansys.motorcad.core.methods.rpc_methods_thermal import _RpcMethodsThermal
from ansys.motorcad.core.methods.rpc_methods_ui import _RpcMethodsUI
from ansys.motorcad.core.methods.rpc_methods_variables import _RpcMethodsVariables
from ansys.motorcad.core.methods.maxwell_udm_geometry import _RpcMethodsMaxwellUDM


class _RpcMethodsCore(
    _RpcMethodsVariables,
    _RpcMethodsUI,
    _RpcMethodsGeneral,
    _RpcMethodsCalculations,
    _RpcMethodsLab,
    _RpcMethodsGraphs,
    _RpcMethodsGeometry,
    _RpcMethodsThermal,
    _RpcMethodsInternalScripting,
    _RpcMethodsFEAGeometry,
    _RpcMethodsMaterials,
    _RpcMethodsAdaptiveGeometry,
    _RpcMethodsMaxwellUDM,
    _RpcMethodsTesting,
):
    def __init__(self, mc_connection):
        self.connection = mc_connection

        _RpcMethodsVariables.__init__(self, self.connection)
        _RpcMethodsUI.__init__(self, self.connection)
        _RpcMethodsGeneral.__init__(self, self.connection)
        _RpcMethodsCalculations.__init__(self, self.connection)
        _RpcMethodsLab.__init__(self, self.connection)
        _RpcMethodsGraphs.__init__(self, self.connection)
        _RpcMethodsGeometry.__init__(self, self.connection)
        _RpcMethodsThermal.__init__(self, self.connection)
        _RpcMethodsInternalScripting.__init__(self, self.connection)
        _RpcMethodsFEAGeometry.__init__(self, self.connection)
        _RpcMethodsMaterials.__init__(self, self.connection)
        _RpcMethodsAdaptiveGeometry.__init__(self, self.connection)
        _RpcMethodsMaxwellUDM.__init__(self, self.connection)
        _RpcMethodsTesting.__init__(self, self.connection)
