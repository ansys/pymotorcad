"""Methods for adaptive geometry."""
from ansys.motorcad.core.geometry import Region


class _RpcMethodsAdaptiveGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_adaptive_parameter_value(self, name, value):
        """Set adaptive parameter, if parameter does not exist then add it.

        Parameters
        ----------
        name : string
            name of parameter.
        value : float
            value of parameter.
        """
        self.connection.ensure_version_at_least("2024.0")
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
        self.connection.ensure_version_at_least("2024.0")
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
        self.connection.ensure_version_at_least("2024.0")
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
        self.connection.ensure_version_at_least("2024.0")
        raw_region = region._to_json()

        method = "SetRegion"
        params = [raw_region]
        return self.connection.send_and_receive(method, params)

    def check_closed_region(self, region):
        """Check region is closed using region detection.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.
        """
        self.connection.ensure_version_at_least("2024.0")
        pass

    def check_collisions(self, region, regions_to_check):
        """Check region does not collide with other geometry regions.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object.

        regions_to_check : list of ansys.motorcad.core.geometry.Region
            list of Motor-CAD region object
        """
        self.connection.ensure_version_at_least("2024.0")
        raw_region = region._to_json()
        raw_regions = [region_to_Check._to_json() for region_to_Check in regions_to_check]

        method = "Check_Collisions"
        params = [raw_region, raw_regions]

        raw_collision_regions = self.connection.send_and_receive(method, params)

        collision_regions = []

        for raw_collision_region in raw_collision_regions:
            collision_region = Region()
            collision_region._from_json(raw_collision_region)
            collision_regions.append(collision_region)

        return collision_regions

    def save_adaptive_script(self, filepath):
        """Save adaptive templates script file to Motor-CAD.

        Parameters
        ----------
        filepath : string
            full file path of script
        """
        self.connection.ensure_version_at_least("2024.0")
        method = "SaveAdaptiveScript"
        params = [filepath]
        return self.connection.send_and_receive(method, params)

    def unite_regions(self, region, regions):
        """Unite region with two or more other regions.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object

        regions : list of ansys.motorcad.core.geometry.Region
            Motor-CAD region objects to united with region

        Returns
        -------
        ansys.motorcad.core.geometry.Region
            United Motor-CAD region object.
        """
        self.connection.ensure_version_at_least("2024.0")

        raw_region = region._to_json()
        raw_regions = [region_internal._to_json() for region_internal in regions]

        method = "UniteRegions"
        params = [raw_region, raw_regions]
        united_raw = self.connection.send_and_receive(method, params)

        region = Region()
        region._from_json(united_raw)

        return region

    def delete_region(self, region, remove_children=False):
        """Delete region from Motor-CAd geometry engine.

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object

        remove_children : boolean
            Whether to remove regions children
        """
        self.connection.ensure_version_at_least("2024.0")

        raw_region = region._to_json()

        method = "DeleteRegion"
        params = [raw_region, remove_children]
        self.connection.send_and_receive(method, params)
