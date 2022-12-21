"""RPC methods for geometry."""


class _RpcMethodsGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_winding_coil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        """Set Go and Return slots, positions and turns for a winding coil.

        Parameters
        ----------
        phase : int
        path : int
        coil : int
        go_slot : int
        go_position : str
            Position parameters can be "a", "b", "c" etc. for Upper/Lower paths and "L"
            or "R" for Left/Right paths
        return_slot : int
        return_position : str
            Position parameters can be "a", "b", "c" etc. for Upper/Lower paths and "L"
            or "R" for Left/Right paths
        turns : int
        """
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            go_slot,
            go_position,
            return_slot,
            return_position,
            turns,
        ]
        return self.connection.send_and_receive(method, params)

    def get_winding_coil(self, phase, path, coil):
        """Get Go and Return slots, positions and turns for a winding coil.

        Phases, paths and coils indexed as on Winding -> Pattern tab.

        Parameters
        ----------
        phase : int
        path : int
        coil : int

        Returns
        -------
        GoSlot : int
        GoPosition : str
        ReturnSlot : int
        ReturnPosition : str
        Turns : int
        """
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.connection.send_and_receive(method, params)

    def check_if_geometry_is_valid(self, edit_geometry):
        """Check if Motor-CAD geometry is valid.

        Parameters
        ----------
        edit_geometry : int
            Allow Motor-CAD to try and reset geometry within constraints is geometry is not valid
            1 - True
            0 - False
        Returns
        -------
        int
            1 indicates valid geometry
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)
