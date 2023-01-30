"""RPC methods for FEA geometry.

Advanced functions. See FEA_Geometry_Scripting tutorial for more information
"""


class _RpcMethodsFEAGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def do_slot_finite_element(self):
        """Carry out slot finite element analysis."""
        method = "DoSlotFiniteElement"
        return self.connection.send_and_receive(method)

    def clear_all_data(self):
        """Clear data and initialise FEA."""
        method = "ClearAllData"
        return self.connection.send_and_receive(method)

    def create_optimised_mesh(self):
        """Create FEA geometry and mesh.

        Call at the end of creating custom scripting geometry.
        """
        method = "CreateOptimisedMesh"
        return self.connection.send_and_receive(method)

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

    def edit_magnet_region(self, region_name, magnet_material, br_angle, br_multiplier):
        """Edit the specified magnet region.

        Parameters
        ----------
        region_name : str
            Name of magnet region to edit
        magnet_material : str
            Sets magnet material
        br_angle : float
            Sets Br angle of magnet
        br_multiplier : float
            Sets Br multiplier for magnet
        """
        method = "EditMagnetRegion"
        params = [region_name, magnet_material, br_angle, br_multiplier]
        return self.connection.send_and_receive(method, params)

    def delete_regions(self, region_name):
        """Delete a comma separated list of named regions or all regions if left empty.

        If region to be deleted contains a space, the region name should be enclosed in
        double quotation marks (e.g. "Rotor Pocket").

        Parameters
        ----------
        region_name : str
            Name of region to delete
        """
        method = "DeleteRegions"
        params = [region_name]
        return self.connection.send_and_receive(method, params)

    def reset_regions(self):
        """Reset custom FEA regions to standard regions from Motor-CAD template geometry."""
        method = "ResetRegions"
        return self.connection.send_and_receive(method)

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

    # ------------------------------------ Custom Geometry ------------------------------------
    def initiate_geometry_from_script(self):
        """Tells Motor-CAD to use geometry from scripting.

        Also clears current scripting geometry.
        Need to call clear_all_data before doing this.
        """
        method = "InitiateGeometryFromScript"
        return self.connection.send_and_receive(method)

    def add_line_xy(self, x_start, y_start, x_end, y_end):
        """Add line to Motor-CAD axial geometry with x and y coordinate system.

        Parameters
        ----------
        x_start : float
            start position x coordinate
        y_start : float
            start position y coordinate
        x_end : float
            end position x coordinate
        y_end : float
            end position y coordinate
        """
        method = "AddLine_XY"
        params = [x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_line_rt(self, radius_start, theta_start, radius_end, theta_end):
        """Add line to Motor-CAD axial geometry with rt (polar) coordinate system.

        Use degrees for angles.

        Parameters
        ----------
        radius_start : float
            start position radial coordinate
        theta_start : float
            start position angular coordinate (degrees)
        radius_end : float
            end position radial coordinate
        theta_end : float
            end position angular coordinate (degrees)
        """
        method = "AddLine_RT"
        params = [radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_xy(self, x_centre, y_centre, theta_start, theta_end, radius):
        """Add arc to Motor-CAD axial geometry with x and y coordinate system.

        Uses centre point, radius and angles. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            centre position x coordinate
        y_centre : float
            centre position x coordinate
        theta_start : float
            angular coordinate of arc start point (degrees)
        theta_end : float
            angular coordinate of arc end point (degrees)
        radius : float
            radius of arc from centre point
        """
        method = "AddArc_XY"
        params = [x_centre, y_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_rt(self, radius_center, theta_centre, theta_start, theta_end, radius):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses centre point, radius and angles. Use degrees for angles.

        Parameters
        ----------
        radius_center : float
            centre position radial coordinate
        theta_centre : float
            centre position angular coordinate
        theta_start : float
            angular coordinate of arc start point (degrees)
        theta_end : float
            angular coordinate of arc end point (degrees)
        radius : float
            radius of arc from centre point
        """
        method = "AddArc_RT"
        params = [radius_center, theta_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_xy(self, x_centre, y_centre, x_start, y_start, x_end, y_end):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses start, end, centre coordinates. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            centre position x coordinate
        y_centre : float
            centre position y coordinate
        x_start : float
            start position x coordinate
        y_start : float
            start position y coordinate
        x_end : float
            end position x coordinate
        y_end : float
            end position y coordinate
        """
        method = "AddArc_CentreStartEnd_XY"
        params = [x_centre, y_centre, x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_rt(
        self, radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end
    ):
        """Add arc to Motor-CAD axial geometry with rt (polar) coordinate system.

        Uses start, end, centre coordinates. Use degrees for angles.

        Parameters
        ----------
        radius_centre : float
            centre position radial coordinate
        theta_centre : float
            centre position angular coordinate (degrees)
        radius_start : float
            start position radial coordinate
        theta_start : float
            start position angular coordinate (degrees)
        radius_end : float
            end position radial coordinate
        theta_end : float
            end position angular coordinate (degrees)
        """
        method = "AddArc_CentreStartEnd_RT"
        params = [radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_region_xy(self, x, y, region_name):
        """Add region to Motor-CAD geometry - overwrites existing region if already exists.

        Use x,y coordinate system.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        """
        method = "AddRegion_XY"
        params = [x, y, region_name]
        return self.connection.send_and_receive(method, params)

    def add_region_rt(self, radius, theta, region_name):
        """Add region to Motor-CAD geometry - overwrites existing region if already exists.

        Use r,t coordinate system. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        """
        method = "AddRegion_RT"
        params = [radius, theta, region_name]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_xy(
        self, x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add magnet region to Motor-CAD geometry - overwrites existing region if already exists.

        Use x,y coordinate system. Use degrees for angles.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        magnet_material : string
            magnet material to use
        br_angle : float
            magnet angle  (degrees)
        br_multiplier : float
            magnet Br multiplier, default is 1
        polarity_code : integer
            magnet polarity. 0 is north, 1 is south
        """
        method = "AddMagnetRegion_XY"
        params = [x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_rt(
        self, radius, theta, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add magnet region to Motor-CAD geometry - overwrites existing region if already exists.

        Use r,t coordinate system. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        magnet_material : string
            magnet material to use
        br_angle : float
            magnet angle (degrees)
        br_multiplier : float
            magnet Br multiplier, default is 1
        polarity_code : integer
            magnet polarity. 0 is north, 1 is south
        """
        method = "AddMagnetRegion_RT"
        params = [
            radius,
            theta,
            region_name,
            magnet_material,
            br_angle,
            br_multiplier,
            polarity_code,
        ]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_xy(self, x, y, region_name, material_name, colour):
        """Add region to geometry and specify material.

        Not for adding magnets. Use add_magnet_region_xy for this.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        region_name : string
            name of region
        material_name : string
            name of material. Motor-CAD material names can be found in Input Data -> materials.
            Material type (laminated/solid/air) is set automatically.

        colour : string
            VCL colour as a string (see https://wiki.freepascal.org/Colors)
            This can be a hexadecimal value e.g. "$008000" or a colour name e.g. "clGreen"
        """
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_rt(self, radius, theta, region_name, material_name, colour):
        """Add region to geometry and specify material.

        Not for adding magnets. Use add_magnet_region_rt for this. Use degrees for angles.

        Parameters
        ----------
        radius : float
            region position radial coordinate
        theta : float
            region position angular coordinate (degrees)
        region_name : string
            name of region
        material_name : string
            name of material. Motor-CAD material names can be found in Input Data -> materials.
            Material type (laminated/solid/air) is set automatically.

        colour : string
            VCL colour as a string (see https://wiki.freepascal.org/Colors)
            This can be a hexadecimal value e.g. "$008000" or a colour name e.g. "clGreen"
        """
        method = "AddPoint_CustomMaterial_RT"
        params = [radius, theta, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)
