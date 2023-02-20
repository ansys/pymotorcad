"""RPC methods for geometry."""


class _RpcMethodsGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_winding_coil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        """Set go and return slots, positions, and turns for a winding coil.

        Parameters
        ----------
        phase : int
        path : int
        coil : int
        go_slot : int
        go_position : str
            Position values for the upper and lower paths of a go slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a go
            slot are ``"L"`` and ``"R"``.
        return_slot : int
        return_position : str
            Position values for the upper and lower paths of a return slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a return
            slot are ``"L"`` and ``"R"``.
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
        """Get the go and return slots, positions, and turns for the winding coil.

        In Motor-CAD, you can select **Winding -> Pattern** to see how phases, paths,
        and coils are indexed.

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
        """Check if the Motor-CAD geometry is valid.

        Parameters
        ----------
        edit_geometry : int
            Indicates if Motor-CAD can try to reset the geometry
            within constraints if the geometry is invalid. Options are:
            - 1: Yes. Try and reset the geometry
            - 0: No. Do not try to reset the geometry.
        
        Returns
        -------
        int
            ``1`` if an attempt to reset the geometry has been made, ``O`` otherwise.
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)
