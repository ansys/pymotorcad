"""RPC methods for graphs."""
from ansys.motorcad.core.rpc_client_core import MotorCADError


def _get_graph(graphing_func, *args):
    """Get an array from a Motor-CAD graph specific to input graph function name.

    Parameters
    ----------
    graphing_func : func
        graph function to use eg. get_magnetic_graph_point
    *args : str, int
        Name/id of graph to select. Graph name is preferred and can be found in
        Motor-CAD (help -> graph viewer) for eg. TorqueVW

    Returns
    -------
    x_array : array
        Values of x coordinates from the graph.
    y_array : array
        Values of y coordinates from the graph.
    """
    loop = 0
    x_array = []
    y_array = []
    while True:
        try:
            x, y = graphing_func(*args, loop)

            y_array.append(y)
            x_array.append(x)
            loop += 1

        except MotorCADError as e:
            break
            # Can't be used currently: Bug in Motor-CAD RPC server
            # if "Point requested is greater than number of points available" in str(e):
            #     break
            # else:
            #     raise

    return x_array, y_array


class _RpcMethodsGraphs:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def get_magnetic_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to retrieve the x and y coordinate values from.

        Returns
        -------
        xValue : float
             Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph(self, graph_name):
        """Get graph points from a Motor-CAD Magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : list
            value of x coordinates from graph
        y_array : list
            value of y coordinates from graph
        """
        loop = 0
        x_array = []
        y_array = []
        return _get_graph(self.get_magnetic_graph_point, graph_name)

    def get_temperature_graph(self, graph_name):
        """Get graph points from a Motor-CAD transient temperature graph.

        Parameters
        ----------
        graph_name : str, int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : list
            value of x coordinates from graph
        y_array : list
            value of y coordinates from graph
        """
        loop = 0
        x_array = []
        y_array = []
        return _get_graph(self.get_temperature_graph_point, graph_name)

    def get_power_graph(self, graph_name):
        """Get graph points from a Motor-CAD transient power loss graph.

        Parameters
        ----------
        graph_name : str, int
            Name/id of graph to select. Graph name is preferred and can be found in
            Motor-CAD (help -> graph viewer)
        Returns
        -------
        x_array : list
            value of x coordinates from graph
        y_array : list
            value of y coordinates from graph
        """
        return _get_graph(self.get_power_graph_point, graph_name)

    def get_temperature_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD thermal graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to get the x and y coordinate values from.

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_power_graph_point(self, graph_name, point_number):
        """Get a point from a Motor-CAD power graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        point_number : int
            Point number to get x and y coordinate values from.

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_3d_graph_point(self, graph_name, slice_number, point_number, time_step_number):
        """Get a point from a Motor-CAD magnetic 3D graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number

        point_number : int
            Point number to get x and y coordinate values from.
        time_step_number

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graph_name}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)

    def get_fea_graph_point(self, graph_id, slice_number, point_number, time_step_number):
        """Get a point from a Motor-CAD FEA graph.

        Parameters
        ----------
        graph_id : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.
        slice_number

        point_number : int
            Point number to get x and y coordinate values from.
        time_step_number

        Returns
        -------
        xValue : float
            Value of the x coordinate from the graph.
        yValue : float
            Value of the y coordinate from the graph.
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graph_id}, slice_number, point_number, time_step_number]
        return self.connection.send_and_receive(method, params)
