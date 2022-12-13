"""Contains all the JSON-RPC API calls for Motor-CAD.

Not for direct use. Inherited by _MotorCADCore/_RpcMethodsCoreOld
"""

from ansys.motorcad.core.methods.rpc_methods_calculations import _RpcMethodsCalculations
from ansys.motorcad.core.methods.rpc_methods_files import _RpcMethodsFiles
from ansys.motorcad.core.methods.rpc_methods_geometry import _RpcMethodsGeometry
from ansys.motorcad.core.methods.rpc_methods_graphs import _RpcMethodsGraphs
from ansys.motorcad.core.methods.rpc_methods_lab import _RpcMethodsLab
from ansys.motorcad.core.methods.rpc_methods_thermal import _RpcMethodsThermal
from ansys.motorcad.core.methods.rpc_methods_ui import _RpcMethodsUI
from ansys.motorcad.core.methods.rpc_methods_variables import _RpcMethodsVariables


class _RpcMethodsCore(
    _RpcMethodsVariables,
    _RpcMethodsUI,
    _RpcMethodsFiles,
    _RpcMethodsCalculations,
    _RpcMethodsLab,
    _RpcMethodsGraphs,
    _RpcMethodsGeometry,
    _RpcMethodsThermal,
):
    def __init__(self, mc_connection):
        self.connection = mc_connection

        _RpcMethodsVariables.__init__(self, self.connection)
        _RpcMethodsUI.__init__(self, self.connection)
        _RpcMethodsFiles.__init__(self, self.connection)
        _RpcMethodsCalculations.__init__(self, self.connection)
        _RpcMethodsLab.__init__(self, self.connection)
        _RpcMethodsGraphs.__init__(self, self.connection)
        _RpcMethodsGeometry.__init__(self, self.connection)
        _RpcMethodsThermal.__init__(self, self.connection)
