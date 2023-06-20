"""Methods for adaptive geometry."""
from ansys.motorcad.core.geometry import Region


class _RpcMethodsAdaptiveGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_adaptive_parameter_value(self, name, value):
        """Sets adaptive parameter.

        If parameter does not exist then create it.

        Parameters
        ----------
        name : string
            name of parameter.
        value : float
            value of parameter.
        """
        method = "SetAdaptiveParameterValue"
        params = [name]
        return self.connection.send_and_receive(method, params)

    def get_adaptive_parameter_value(self, name):
        """Get adaptive parameter.

        Parameters
        ----------
        name : string
            name of parameter.

        Returns
        -------
        float
            value of parameter.
        """
        method = "GetAdaptiveParameterValue"
        params = [name]
        return self.connection.send_and_receive(method, params)

    def get_region(self, name):
        """Get Motor-CAD geometry region.

        Parameters
        ----------
        name : string
            name of region.

        Returns
        -------
        ansys.motorcad.core.geometry.Region
            Motor-CAD region object.

        """
        method = "GetRegion"
        params = [name]
        raw_region = self.connection.send_and_receive(method, params)

        region = Region()
        region._from_json(raw_region)

        return region

    def set_region(self, region):
        """Set Motor-CAD geometry region.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.
        """

        raw_region = region._to_json()

        method = "SetRegion"
        params = [raw_region]
        return self.connection.send_and_receive(method, params)

    def get_entities_between_poly_start_end(self, region, polyline):
        """

        Parameters
        ----------
        region
        polyline

        Returns
        -------

        """
        pass

    def check_closed_region(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def check_collisions(self, region):
        """

        Parameters
        ----------
        region

        Returns
        -------

        """
        pass

    def save_adaptive_script(self, filepath):
        """

        Parameters
        ----------
        filepath

        Returns
        -------

        """
        pass
