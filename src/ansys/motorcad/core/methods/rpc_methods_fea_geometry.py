"""RPC methods for FEA geometry.

Advanced functions. See FEA_Geometry_Scripting tutorial for more information
"""


class _RpcMethodsFEAGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

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

    def do_slot_finite_element(self):
        """Run slot FEA."""
        method = "DoSlotFiniteElement"
        return self.connection.send_and_receive(method)

    def clear_all_data(self):
        """Clear data and initialize the FEA."""
        method = "ClearAllData"
        return self.connection.send_and_receive(method)

    def create_optimised_mesh(self):
        """Create the FEA geometry and an optimized mesh.

        Call this method at the end of creating a custom scripting geometry.
        """
        method = "CreateOptimisedMesh"
        return self.connection.send_and_receive(method)

    def add_arc_boundary_rt(
        self, direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add a boundary condition arc using r, t coordinates for the center."""
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_arc_boundary_xy(
        self, direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add a boundary condition arc using x, y coordinates for the center."""
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_rt(self, rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code):
        """Add a boundary condition line using r, t coordinates for the start and end points."""
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_xy(self, xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code):
        """Add a boundary condition line using x, y coordinates for the start and end points."""
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
        """Add or edit a point in the path editor."""
        method = "SetFEAPathPoint"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x,
            tor_y,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_arc(
        self,
        path_name,
        path_location,
        r,
        theta_start,
        theta_end,
        points,
        fea_method,
        calculation,
        expression,
    ):
        """Add or edit an arc in the path editor."""
        method = "SetFEAPathArc"
        params = [
            path_name,
            path_location,
            r,
            theta_start,
            theta_end,
            points,
            fea_method,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_line(
        self,
        path_name,
        path_location,
        coord_system,
        ror_x_start,
        tor_y_start,
        ror_x_end,
        tor_y_end,
        points,
        calculation,
        expression,
    ):
        """Add or edit a line in the path editor."""
        method = "SetFEAPathLine"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x_start,
            tor_y_start,
            ror_x_end,
            tor_y_end,
            points,
            calculation,
            expression,
        ]
        return self.connection.send_and_receive(method, params)

    def save_fea_data(self, file, first_step, final_step, outputs, regions, separator):
        """Save raw data for the open FEA solution."""
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.connection.send_and_receive(method, params)

    def get_region_value(self, expression, region_name):
        """Calculate the integral value for an expression of a region."""
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.connection.send_and_receive(method, params)

    def get_region_loss(self, expression, region_name, radius1, radius2, angle1, angle2):
        """Calculate the loss value for an expression of a region.

        This method is valid for a magnetic solution only.
        The region is bounded by the radii and angles that are specified in parameters.

        Radii and angle values of 0 give all region losses.
        Losses calculated are per unit length and are only for the FEA areas modeled.

        For total losses, you must multiply by the symmetry factor.
        """
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.connection.send_and_receive(method, params)

    def edit_magnet_region(self, region_name, magnet_material, br_angle, br_multiplier):
        """Edit a magnet region.

        Parameters
        ----------
        region_name : str
            Name of the magnet region.
        magnet_material : str
            Magnet material.
        br_angle : float
            Br angle of the magnet.
        br_multiplier : float
            Br multiplier for the magnet.
        """
        method = "EditMagnetRegion"
        params = [region_name, magnet_material, br_angle, br_multiplier]
        return self.connection.send_and_receive(method, params)

    def delete_regions(self, region_name):
        """Delete a comma-separated list of named regions or all regions.

        Parameters
        ----------
        region_name: list
           List of names for the regions to delete. If the list is empty,
           all regions are deleted. If the name of a region to delete contains
           a space, enclose the name in double quotation marks. For example,
           ``"Rotor Pocket"``.
        """
        method = "DeleteRegions"
        params = [region_name]
        return self.connection.send_and_receive(method, params)

    def reset_regions(self):
        """Reset custom FEA regions to standard regions from the Motor-CAD template geometry."""
        method = "ResetRegions"
        return self.connection.send_and_receive(method)

    def get_point_value(self, parameter, x, y):
        """Get a point value from the Motor-CAD FEA.

        Parameters
        ----------
        parameter : str|int
            Motor-CAD shading function.
        x : float
            Value for the x coordinate.
        y : float
            Value for the y coordinate.

        Returns
        -------
        value : float
            Value from the FEA.
        units : string
            Units for ``paramater``, which is the Motor-CAD shading function.
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.connection.send_and_receive(method, params)

    # ------------------------------------ Custom Geometry ------------------------------------
    def initiate_geometry_from_script(self):
        """Initiate the geometry from scripting so Motor-CAD knows how to use it.

        This method clears the current scripting geometry.
        The ``clear_all_data`` method must be called before this method is called.
        """
        method = "InitiateGeometryFromScript"
        return self.connection.send_and_receive(method)

    def add_line_xy(self, x_start, y_start, x_end, y_end):
        """Add a line to the Motor-CAD axial geometry with an x, y coordinate system.

        Parameters
        ----------
        x_start : float
            Start position for the x coordinate.
        y_start : float
            Start position for the y coordinate.
        x_end : float
            End position for the x coordinate.
        y_end : float
            End position for the y coordinate.
        """
        method = "AddLine_XY"
        params = [x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_line_rt(self, radius_start, theta_start, radius_end, theta_end):
        """Add a line to the Motor-CAD axial geometry with an r, t (polar) coordinate system.

        Use degrees for angles.

        Parameters
        ----------
        radius_start : float
            Start position for the radial coordinate.
        theta_start : float
            Start position for the angular coordinate in degrees.
        radius_end : float
            End position for the radial coordinate.
        theta_end : float
            End position for the angular coordinate in degrees.
        """
        method = "AddLine_RT"
        params = [radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_xy(self, x_centre, y_centre, theta_start, theta_end, radius):
        """Add an arc to the Motor-CAD axial geometry with an x, y coordinate system.

        This method uses the center point, radius, and angles. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            Center position for the x coordinate.
        y_centre : float
            Center position for the x coordinate.
        theta_start : float
            Angular coordinate of the arc start point in degrees.
        theta_end : float
            Angular coordinate of the arc end point in degrees.
        radius : float
            Radius of the arc from the center point.
        """
        method = "AddArc_XY"
        params = [x_centre, y_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_rt(self, radius_center, theta_centre, theta_start, theta_end, radius):
        """Add an arc to the Motor-CAD axial geometry with an r, t (polar) coordinate system.

        This method uses the center point, radius, and angles. Use degrees for angles.

        Parameters
        ----------
        radius_center : float
            Center position the radial coordinate.
        theta_centre : float
            Center position for the angular coordinate.
        theta_start : float
            Angular coordinate of the arc start point in degrees.
        theta_end : float
            Angular coordinate of the arc end point in degrees.
        radius : float
            Radius of the arc from the center point.
        """
        method = "AddArc_RT"
        params = [radius_center, theta_centre, theta_start, theta_end, radius]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_xy(self, x_centre, y_centre, x_start, y_start, x_end, y_end):
        """Add an arc to the Motor-CAD axial geometry with an r, t (polar) coordinate system.

        This method uses start, end, and center coordinates. Use degrees for angles.

        Parameters
        ----------
        x_centre : float
            Center position for the x coordinate.
        y_centre : float
            Center position for the y coordinate.
        x_start : float
            Start position for the x coordinate.
        y_start : float
            Start position for the y coordinate.
        x_end : float
            End position for the x coordinate.
        y_end : float
            End position for the y coordinate.
        """
        method = "AddArc_CentreStartEnd_XY"
        params = [x_centre, y_centre, x_start, y_start, x_end, y_end]
        return self.connection.send_and_receive(method, params)

    def add_arc_centre_start_end_rt(
        self, radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end
    ):
        """Add an arc to the Motor-CAD axial geometry with an r, t (polar) coordinate system.

        This method uses start, end, and center coordinates. Use degrees for angles.

        Parameters
        ----------
        radius_centre : float
            Center position for the radial coordinate.
        theta_centre : float
            Centre position for the angular coordinate in degrees.
        radius_start : float
            Start position for the radial coordinate.
        theta_start : float
            Start position for other angular coordinate in degrees.
        radius_end : float
            end position radial coordinate
        theta_end : float
            End position for the angular coordinate in degrees.
        """
        method = "AddArc_CentreStartEnd_RT"
        params = [radius_centre, theta_centre, radius_start, theta_start, radius_end, theta_end]
        return self.connection.send_and_receive(method, params)

    def add_region_xy(self, x, y, region_name):
        """Add a region to the Motor-CAD geometry with an x, y coordinate system.

        If a region already exists, this method overwrites the existing region.

        Parameters
        ----------
        x : float
            Region position for the x coordinate.
        y : float
            Region position for the y coordinate.
        region_name : string
            Name of the region.
        """
        method = "AddRegion_XY"
        params = [x, y, region_name]
        return self.connection.send_and_receive(method, params)

    def add_region_rt(self, radius, theta, region_name):
        """Add a region to the Motor-CAD geometry with an r, t (polar) coordinate system.

        If a region already exists, this method overwrites the existing region.

        Use degrees for angles.

        Parameters
        ----------
        radius : float
            Region position for the radial coordinate.
        theta : float
            Region position for the angular coordinate in degrees.
        region_name : string
            Name of the region.
        """
        method = "AddRegion_RT"
        params = [radius, theta, region_name]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_xy(
        self, x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add a magnet region to the Motor-CAD geometry with an x, y coordinate system.

        If a region already exists, this method overwrites the existing region.

        Use degrees for angles.

        Parameters
        ----------
        x : float
            Region position for the x coordinate.
        y : float
            Region position for the y coordinate.
        region_name : string
            Name of the region.
        magnet_material : string
            Magnet material.
        br_angle : float
            Magnet angle in degrees.
        br_multiplier : float, optional
            Magnet Br multiplier. The default is ``1``.
        polarity_code : integer
            Magnet polarity, where ``0`` is north and ``1`` is south.
        """
        method = "AddMagnetRegion_XY"
        params = [x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code]
        return self.connection.send_and_receive(method, params)

    def add_magnet_region_rt(
        self, radius, theta, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        """Add a magnet region to the Motor-CAD geometry with an r, t (polar) coordinate system.

        If a region already exists, this method overwrites the existing region.

        Use degrees for angles.

        Parameters
        ----------
        radius : float
            Region position for the radial coordinate.
        theta : float
            Region position for the angular coordinate in degrees.
        region_name : string
            Name of the region.
        magnet_material : string
            Magnet material.
        br_angle : float
            Magnet angle in degrees.
        br_multiplier : float, optional
            Magnet Br multiplier. The default is ``1``.
        polarity_code : integer
            Magnet polarity, where ``0`` is north and ``1`` is south.
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

    def _get_region_properties_xy(self, x, y):
        """Get properties of region from name and coordinates.

        Returns list of parameters. Currently only used for testing other geometry functions.
        EXPERIMENTAL FUNCTION - LIKELY TO CHANGE.
        """
        method = "GetRegionProperties_XY"
        params = [x, y]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_xy(self, x, y, region_name, material_name, colour):
        """Add a region to the geometry and specify the material.

        .. note::
           Do not use this method to add a magnet. Use the ``add_magnet_region_xy`` method.

        Parameters
        ----------
        x : float
            Region position for the x coordinate.
        y : float
            Region position for the y coordinate.
        region_name : string
            Name of the region.
        material_name : string
            Name of the material. In Motor-CAD, material names can be found in
            **Input Data -> materials**. The material type (``laminated``, ``solid``,
            or ``air``) is set automatically.
        colour : string
            VCL color. For more information, see https://wiki.freepascal.org/Colors.
            The color can be designaed as a hexadecimal value, such as ``"$008000"``
            or a color name such as ``"clGreen"``.
        """
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_custom_material_rt(self, radius, theta, region_name, material_name, colour):
        """Add a region to the geometry and specify the material.

        .. note::
           Do not use this method to add a magnet. Use the ``add_magnet_region_rt`` method.

        Use degrees for angles.

        Parameters
        ----------
        radius : float
            Region position for the radial coordinate.
        theta : float
            Region position for the angular coordinate in degrees.
        region_name : string
            Name of the region.
        material_name : string
            NName of the material. In Motor-CAD, material names can be found in
            **Input Data -> materials**. The material type (``laminated``, ``solid``,
            or ``air``) is set automatically.
        colour : string
            VCL color. For more information, see https://wiki.freepascal.org/Colors.
            The color can be designaed as a hexadecimal value, such as ``"$008000"``
            or a color name such as ``"clGreen"``.
        """
        method = "AddPoint_CustomMaterial_RT"
        params = [radius, theta, region_name, material_name, colour]
        return self.connection.send_and_receive(method, params)
