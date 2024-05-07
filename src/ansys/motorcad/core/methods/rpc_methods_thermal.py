"""RPC methods for Motor-CAD Thermal."""
from ansys.motorcad.core.rpc_client_core import MotorCADError


class _RpcMethodsThermal:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_resistance_value(self, name, node1, node2, value, description):
        """Set or create a resistance."""
        method = "SetResistanceValue"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def set_resistance_multiplier(self, name, node1, node2, value, description):
        """Set or create a resistance multiplication factor."""
        method = "SetResistanceMultiplier"
        params = [name, node1, node2, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_external_circuit(self):
        """Clear the external circuit."""
        method = "ClearExternalCircuit"
        return self.connection.send_and_receive(method)

    def create_new_node(self, name, node1, row, column, colour, description):
        """Create a node."""
        method = "CreateNewNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def modify_node(self, name, node1, row, column, colour, description):
        """Modify an existing node."""
        method = "ModifyNode"
        params = [name, node1, row, column, colour, description]
        return self.connection.send_and_receive(method, params)

    def set_capacitance_value(self, name, node1, value, description):
        """Set or create a capacitance."""
        method = "SetCapacitanceValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def set_power_source_value(self, name, node1, value, rpm_ref, rpm_coef, description):
        """Set or create a power source."""
        method = "SetPowerSourceValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def load_external_circuit(self, circuit_file_name):
        """Load an external circuit from a file."""
        method = "LoadExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_external_circuit(self, circuit_file_name):
        """Save the external circuit to a file."""
        method = "SaveExternalCircuit"
        params = [circuit_file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_power_values(self, file_name):
        """Save transient power results to a CSV file."""
        method = "SaveTransientPowerValues"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def save_transient_temperatures(self, file_name):
        """Save transient temperature results to a CSV file."""
        method = "SaveTransientTemperatures"
        params = [file_name]
        return self.connection.send_and_receive(method, params)

    def remove_external_component(self, component_type, name, node1):
        """Remove an external circuit component.

        Parameters
        ----------
        component_type: str
            Type of the external circuit components. Options are ``"Resistance"``,
            ``"Power Source"``, and ``"Power Injection"``).
        name: str

        node1: int
            Number of the thermal node.
        """
        method = "RemoveExternalComponent"
        params = [component_type, name, node1]
        return self.connection.send_and_receive(method, params)

    def get_node_temperature(self, node_number):
        """Get the temperature of a thermal node.

        Parameters
        ----------
        node_number : int
            Number of the thermal node.

        Returns
        -------
        float
            Temperature of the thermal node.
        """
        method = "GetNodeTemperature"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_capacitance(self, node_number):
        """Get the capacitance of a thermal node.

        Parameters
        ----------
        node_number : int
            Number of the thermal node.

        Returns
        -------
        float
            Capacitance of the thermal node.
        """
        method = "GetNodeCapacitance"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_power(self, node_number):
        """Get the power of a thermal node.

        Parameters
        ----------
        node_number : int
            Number of the thermal node.

        Returns
        -------
        float
            Power of the thermal node.
        """
        method = "GetNodePower"
        params = [node_number]
        return self.connection.send_and_receive(method, params)

    def get_node_to_node_resistance(self, node1, node2):
        """Get the node-to-node resistance.

        Parameters
        ----------
        node1 : int
            Number of the first thermal node.
        node2 : int
            Number of the second thermal node.

        Returns
        -------
        float
            Resistance value.
        """
        method = "GetNodeToNodeResistance"
        params = [node1, node2]
        return self.connection.send_and_receive(method, params)

    def get_node_exists(self, node_number):
        """Check if a node exists.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        bool
            ``True`` if node exists, ``False`` otherwise.
        """
        method = "GetNodeExists"
        params = [node_number]
        try:
            node_exists = self.connection.send_and_receive(method, params, success_var=False)
        except MotorCADError as e:
            if "Range check error" in str(e):
                node_exists = False
            else:
                raise

        return node_exists

    def get_offset_node_number(self, node_number, slice_number, cuboid_number):
        """Get the offset node number.

        Parameters
        ----------
        node_number : int
            Number of the node.
        slice_number : int
            Number of the slice.
        cuboid_number : int
            Number of the cuboid.

        Returns
        -------
        int
            Offset node number.
        """
        method = "GetOffsetNodeNumber"
        params = [node_number, slice_number, cuboid_number]
        return self.connection.send_and_receive(method, params)

    def set_power_injection_value(self, name, node1, value, rpm_ref, rpm_coef, description):
        """Set or create a power injection.

        Parameters
        ----------
        name : str
            Name of the power injection.
        node1 :
        value :
        rpm_ref :
        rpm_coef :
        description : str

        """
        method = "SetPowerInjectionValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.connection.send_and_receive(method, params)

    def set_fixed_temperature_value(self, name, node1, value, description):
        """Set or create a fixed temperature on a node."""
        method = "SetFixedTemperatureValue"
        params = [name, node1, value, description]
        return self.connection.send_and_receive(method, params)

    def clear_fixed_temperature_value(self, node1):
        """Remove a fixed temperature from a node."""
        method = "ClearFixedTemperatureValue"
        params = [node1]
        return self.connection.send_and_receive(method, params)
