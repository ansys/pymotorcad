"""Contains all the JSON-RPC API calls for Motor-CAD.

Not for direct use. Inherited by _MotorCADCore/_RpcMethodsCoreOld
"""

from ansys.motorcad.core.methods.rpc_methods_calculations import _RpcMethodsCalculations
from ansys.motorcad.core.methods.rpc_methods_fea_geometry import _RpcMethodsFEAGeometry
from ansys.motorcad.core.methods.rpc_methods_general import _RpcMethodsGeneral
from ansys.motorcad.core.methods.rpc_methods_geometry import _RpcMethodsGeometry
from ansys.motorcad.core.methods.rpc_methods_graphs import _RpcMethodsGraphs
from ansys.motorcad.core.methods.rpc_methods_internal_scripting import _RpcMethodsInternalScripting
from ansys.motorcad.core.methods.rpc_methods_lab import _RpcMethodsLab
from ansys.motorcad.core.methods.rpc_methods_materials import _RpcMethodsMaterials
from ansys.motorcad.core.methods.rpc_methods_thermal import _RpcMethodsThermal
from ansys.motorcad.core.methods.rpc_methods_ui import _RpcMethodsUI
from ansys.motorcad.core.methods.rpc_methods_variables import _RpcMethodsVariables


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
