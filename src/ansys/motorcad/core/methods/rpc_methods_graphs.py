"""RPC methods for graphs."""
from ansys.motorcad.core.rpc_client_core import MotorCADError


class _RpcMethodsGraphs:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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

    def _get_graph(self, graphing_func, *args):
        """Get array from a Motor-CAD graph specific to  input graph function name.

        Parameters
        ----------
        graphing_func : str
            Name of graph function for eg. get_magnetic_graph_point
        *args : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer) for eg. TorqueVW

        Returns
        -------
        x_array : array
            value of x coordinates from graph
        y_array : array
            value of y coordinates from graph
        """
        loop = 0
        x_array = []
        y_array = []
        while True:
            try:
                x, y = graphing_func(*args, loop)

                y_array.append(y)
                x_array.append(x)
                loop = loop + 1

            except MotorCADError as e:
                if "Point requested is greater than number of points available" in str(e):
                    break
                else:
                    raise

        return x_array, y_array

    def get_magnetic_graph(self, graph_name):
        """Get array from a Motor-CAD Magnetic graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : array
            value of x coordinates from graph
        y_array : array
            value of y coordinates from graph
        """
        loop = 0
        x_array = []
        y_array = []
        return self._get_graph(self.get_magnetic_graph_point, graph_name)

    def get_temperature_graph(self, graph_name):
        """Get array from a Motor-CAD transient temperature  graph from thermal module of Motor-CAD.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : array
            value of x coordinates from graph
        y_array : array
            value of y coordinates from graph
        """
        loop = 0
        x_array = []
        y_array = []
        return self._get_graph(self.get_temperature_graph_point, graph_name)

    def get_power_graph(self, graph_name):
        """Get array from a Motor-CAD transient power loss graph from thermal module of Motor-CAD.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : array
            value of x coordinates from graph
        y_array : array
            value of y coordinates from graph
        """
        return self._get_graph(self.get_power_graph_point, graph_name)

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
