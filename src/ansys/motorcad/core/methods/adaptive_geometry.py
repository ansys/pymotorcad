"""Methods for adaptive geometry."""
from ansys.motorcad.core.geometry import Region, _convert_entities_to_json, _set_json_entities


class _RpcMethodsAdaptiveGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    # def add_adaptive_parameter(self, name):
    #     """Adds new adaptive parameter.
    #
    #             If parameter does not exist then create it.
    #
    #             Parameters
    #             ----------
    #             name : string
    #                 name of parameter.
    #             """
    #     method = "AddAdaptiveParameter"
    #     params = [name]
    #    return self.connection.send_and_receive(method, params)

    def set_adaptive_parameter_value(self, name, value):
        """Set adaptive parameter, if parameter does not exist then add it.

        Parameters
        ----------
        name : string
            name of parameter.
        value : float
            value of parameter.
        """
        method = "SetAdaptiveParameterValue"
        params = [name, value]
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
        """Return entities from region which are between start/end of polyline.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.
        polyline : List of Line/Arc objects
            Polyline using lines/arcs

        Returns
            List of Line/Arc objects
        -------

        """
        raw_region = region._to_json()
        raw_entities = _convert_entities_to_json(polyline)

        method = "GetEntities_Between_PolyStartEnd"
        params = [raw_region, raw_entities]

        raw_output_entities, start_index = self.connection.send_and_receive(method, params)

        return _set_json_entities(raw_output_entities), start_index

    def check_closed_region(self, region):
        """Check region is closed using region detection.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.

        -------

        """
        pass

    def check_collisions(self, region):
        """Check region does not collide with other geometry regions.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.

        -------

        """
        pass

    def save_adaptive_script(self, filepath):
        """Save adaptive templates script file to Motor-CAD.

        Parameters
        ----------
        filepath : string
            full file path of script
        """
        method = "SaveAdaptiveScript"
        params = [filepath]
        return self.connection.send_and_receive(method, params)
