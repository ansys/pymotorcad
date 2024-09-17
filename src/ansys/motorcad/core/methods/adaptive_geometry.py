# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Methods for adaptive geometry."""
from ansys.motorcad.core.geometry import Region
from ansys.motorcad.core.rpc_client_core import is_running_in_internal_scripting


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
        ansys.motorcad.core.geometry.Region or ansys.motorcad.core.geometry.RegionMagnet
            Motor-CAD region object.

        """
        self.connection.ensure_version_at_least("2024.0")
        method = "GetRegion"
        params = [name]
        raw_region = self.connection.send_and_receive(method, params)

        region = Region._from_json(raw_region, motorcad_instance=self)

        return region

    def get_region_dxf(self, name):
        """Get Motor-CAD dxf geometry region.

        Parameters
        ----------
        name : string
            Name of the region.

        Returns
        -------
        ansys.motorcad.core.geometry.Region or ansys.motorcad.core.geometry.RegionMagnet
            Motor-CAD region object.

        """
        self.connection.ensure_version_at_least("2024.2.0")
        method = "GetRegion_DXF"
        params = [name]
        raw_region = self.connection.send_and_receive(method, params)

        region = Region._from_json(raw_region)
        region.motorcad_instance = self

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
        raw_regions = [region_to_check._to_json() for region_to_check in regions_to_check]

        method = "Check_Collisions"
        params = [raw_region, raw_regions]

        raw_collision_regions = self.connection.send_and_receive(method, params)

        collision_regions = []

        for raw_collision_region in raw_collision_regions:
            collision_region = Region._from_json(raw_collision_region, motorcad_instance=self)
            collision_regions.append(collision_region)

        return collision_regions

    def save_adaptive_script(self, filepath):
        """Save adaptive templates script from Motor-CAD to file.

        Parameters
        ----------
        filepath : string
            full file path of script
        """
        self.connection.ensure_version_at_least("2024.0")
        method = "SaveAdaptiveScript"
        params = [filepath]
        return self.connection.send_and_receive(method, params)

    def load_adaptive_script(self, filepath):
        """Load adaptive templates script file to Motor-CAD.

        Parameters
        ----------
        filepath : string or pathlib.Path
            full file path of script
        """
        self.connection.ensure_version_at_least("2024.0")
        method = "LoadAdaptiveScript"
        params = [str(filepath)]
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

        region = Region._from_json(united_raw, motorcad_instance=self)

        return region

    def delete_region(self, region, remove_children=False):
        """Delete region from Motor-CAD geometry engine.

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

    def subtract_region(self, region, region_subtract):
        """Subtract Motor-CAD region (region_subtract) from another Motor-CAD region (region).

        Parameters
        ----------
        region : ansys.motorcad.core.geometry.Region
            Motor-CAD region object

        region_subtract : ansys.motorcad.core.geometry.Region
            Motor-CAD region object

        Returns
        -------
        list of ansys.motorcad.core.geometry.Region
            Motor-CAD region objects
        """
        self.connection.ensure_version_at_least("2024.0")

        raw_region = region._to_json()
        raw_region_subtract = region_subtract._to_json()

        method = "SubtractRegion"
        params = [raw_region, raw_region_subtract]
        subtracted_raw_regions = self.connection.send_and_receive(method, params)

        regions = []
        for subtracted_raw in subtracted_raw_regions:
            returned_region = Region._from_json(subtracted_raw, motorcad_instance=self)
            regions.append(returned_region)

        return regions

    def reset_adaptive_geometry(self):
        """Reset geometry to default."""
        method = "ResetGeometry"
        # No need to do this if running internally
        if not is_running_in_internal_scripting():
            return self.connection.send_and_receive(method)
