"""Contains JSON-RPC API methods which are just for internal use.

DO NOT USE IN SCRIPTS.
These can be for internal testing or might be unfinished/undocumented/deprecated functions.
"""


class _RpcMethodsInternal:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def is_stop_requested(self):
        """Intercept button clicks in python since it does not use a separate thread."""
        method = "IsStopRequested"
        return self.connection.send_and_receive(method)

    def update_interface(self):
        method = "UpdateInterface"
        return self.connection.send_and_receive(method)

    def avoid_immediate_update(self, avoid_update):
        """Set to true to speed up the setting of inputs.

        The steady state calc will only now be calculated when DoSteadyStateAnalysis is called.

        Parameters
        ----------
        avoid_update: bool
        """
        method = "AvoidImmediateUpdate"
        params = [{"variant": avoid_update}]
        return self.connection.send_and_receive(method, params)

    def get_im_iron_loss(self, slip, back_emf):
        """Get analytic iron loss using data from FEA solution.

        The E-magnetic model must be solved prior to method call.

        Parameters
        ----------
        slip : float
            The induction motor slip.
        back_emf : float

        Returns
        -------
        EddyLoss : float
            Summation of stator tooth, stator back iron, rotor tooth and rotor back iron eddy
            current losses
        HysLoss : float
            Summation of stator tooth, stator back iron, rotor tooth and rotor back iron
            hysteresis losses
        """
        method = "GetIMIronLoss"
        params = [slip, back_emf]
        return self.connection.send_and_receive(method, params)

    def set_all_emag_calculations(self, state):
        """Control whether all or none of the performance tests are enabled.

        Parameters
        ----------
        state : bool
            True enables all performance tests.
        """
        method = "SetAllEmagCalculations"
        params = [state]
        return self.connection.send_and_receive(method, params)

    def _get_region_properties_xy(self, x, y):
        """Get properties of region from name and coordinates.

        Returns list of parameters. Currently only used for testing other geometry functions.
        EXPERIMENTAL FUNCTION - LIKELY TO CHANGE.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        """
        method = "GetRegionProperties_XY"
        params = [x, y]
        return self.connection.send_and_receive(method, params)
