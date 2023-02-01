"""RPC methods for FEA results."""


class _RpcMethodsFEAResults:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def load_fea_result(self, file_path, solution_number):
        """Load in an existing FEA solution to allow viewing of FEA results.

        Parameters
        ----------
        file_path : str
            Use r'filepath' syntax to force Python to ignore special characters.
        solution_number : int
        """
        method = "LoadFEAResult"
        params = [file_path, solution_number]
        return self.connection.send_and_receive(method, params)

    def save_fea_data(self, file, first_step, final_step, outputs, regions, separator):
        """Save raw data for open FEA solution.

        Parameters
        ----------
        file : string
            File path to store fea data.
            Use r'filepath' syntax to force Python to ignore special characters.
        first_step : integer
            first step desired from transient calculation
        final_step : integer
            final step desired from transient calculation
        outputs : string
            comma delimited string of desired outputs
        regions : string
            comma delimited string of desired regions
        separator : string
            separator used in output file
        """
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.connection.send_and_receive(method, params)

    def get_point_value(self, parameter, x, y):
        """Get a specified point from Motor-CAD FEA.

        Parameters
        ----------
        parameter : str|int
            Motor-CAD shading function
        x : float
            x value
        y : float
            y value

        Returns
        -------
        value : float
            value from FEA
        units : string
            units of parameter
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.connection.send_and_receive(method, params)

    def get_region_value(self, expression, region_name):
        """Calculate the integral value for given expression of the region.

        Parameters
        ----------
        expression : string
            selected parameter
        region_name : string
            region to calculate integral value
        """
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.connection.send_and_receive(method, params)

    def get_region_loss(self, expression, region_name, radius1, radius2, angle1, angle2):
        """Calculate the loss value for given expression of the region.

        Region bounded by radii and angles specified.
        Radii and angle values of 0 will give all region losses.
        Losses calculated are for per unit length and are only for the FEA areas modelled
        (for total losses require to multiply by symmetry factor).
        Valid for magnetic solution only.

        Parameters
        ----------
        expression : string
            selected parameter
        region_name : string
            region to calculate integral value
        radius1 : float
            boundary radius start
        radius2 : float
            boundary radius finish
        angle1 : float
            boundary angle start
        angle2 : float
            boundary angle finish
        """
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
        """Add/edit a point in the path editor."""
        method = "SetFEAPathPoint"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x,
            tor_y,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_arc(
        self,
        path_name,
        path_location,
        r,
        theta_start,
        theta_end,
        points,
        fea_method,
        calculation,
        expression,
    ):
        """Add/edit an arc in the path editor."""
        method = "SetFEAPathArc"
        params = [
            path_name,
            path_location,
            r,
            theta_start,
            theta_end,
            points,
            fea_method,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_line(
        self,
        path_name,
        path_location,
        coord_system,
        ror_x_start,
        tor_y_start,
        ror_x_end,
        tor_y_end,
        points,
        calculation,
        expression,
    ):
        """Add/edit a line in the path editor."""
        method = "SetFEAPathLine"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x_start,
            tor_y_start,
            ror_x_end,
            tor_y_end,
            points,
            calculation,
            expression,
        ]
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
