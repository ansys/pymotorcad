"""RPC methods for graphs."""


class _RpcMethodsGraphs:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def load_magnetisation_curves(self, file_path):
        """Load the magnetisation curves from a text file.

        Parameters
        ----------
        file_path : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadMagnetisationCurves"
        params = [file_path]
        return self.connection.send_and_receive(method, params)

    def save_magnetisation_curves(self, file_name):
        """Save the magnetisation curves to a text file.

        Parameters
        ----------
        file_name : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "SaveMagnetisationCurves"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD Magnetic graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_temperature_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD Thermal graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_power_graph_point(self, graph_name, point_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_3d_graph_point(self, graph_name, slice_number, point_number, time_step_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graph_name}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    def get_fea_graph_point(self, graph_id, slice_number, point_number, time_step_number):
        """Get a specified point from a Motor-CAD graph.

        Parameters
        ----------
        graph_id : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graph_id}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)
