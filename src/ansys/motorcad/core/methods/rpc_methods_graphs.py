"""RPC methods for graphs."""
from ansys.motorcad.core.rpc_client_core import MotorCADError


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
            Value of x coordinate from the graph.
        yValue : float
            Value of y coordinate from the graph.
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.connection.send_and_receive(method, params)

    def get_magnetic_graph(self, graph_name):
        """Get an array  from a Motor-CAD magnetic graph.

        Parameters
        ----------
        graph_name : str, int
            Name (preferred) or ID of the graph. In Motor-CAD, you can
            select **Help -> Graph Viewer** to see the graph name.

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
                x, y = self.get_magnetic_graph_point(graph_name, loop)

                y_array.append(y)
                x_array.append(x)
                loop = loop + 1

            except MotorCADError as e:
                if (
                    "Number of points requested is greater than the number of points available."
                    in str(e)
                ):
                    break
                else:
                    raise

        return x_array, y_array

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
            Vlue of the x coordinate from the graph.
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
