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

    def add_arc_boundary_rt(
        self, direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add boundary condition arc using RT coordinates for centre."""
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_arc_boundary_xy(
        self, direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        """Add boundary condition arc using XY coordinates for centre."""
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_rt(self, rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code):
        """Add boundary condition line using RT coordinates for start and end points."""
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def add_line_boundary_xy(self, xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code):
        """Add boundary condition line using XY coordinates for start and end points."""
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code]
        return self.connection.send_and_receive(method, params)

    def set_fea_path_point(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
        """Add/edit a point in the path editor."""
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
        """Add/edit an arc in the path editor."""
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
        """Add/edit a line in the path editor."""
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

    # ------------------------------- Undocumented FEA Functions ------------------------------
    # Need to check if these are actually used and remove/move as required

    def add_region_thermal_a(
        self,
        reg_name,
        thermal_conductivity,
        tcc,
        ref_temp,
        j_val,
        sigma,
        density,
        loss_density,
    ):
        """Add thermal region."""
        method = "Add_Region_Thermal_A"
        params = [
            reg_name,
            thermal_conductivity,
            tcc,
            ref_temp,
            j_val,
            sigma,
            density,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def set_bnd_cond(self, dir_code, c1, c2, c3):
        """Set boundary condition."""
        method = "SetBndCond"
        params = [dir_code, c1, c2, c3]
        return self.connection.send_and_receive(method, params)

    def store_problem_data(self, p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max):
        """Store problem data."""
        method = "StoreProblemData"
        params = [p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max]
        return self.connection.send_and_receive(method, params)

    def add_point_xy(self, x, y, reg_name):
        """Add point (x, y coordinates)."""
        method = "AddPoint_XY"
        params = [x, y, reg_name]
        return self.connection.send_and_receive(method, params)

    def create_optimised_mesh_thermal(self, copper_region, ins_region, impreg_region):
        """Create optimised mesh for thermal FEA."""
        method = "CreateOptimisedMesh_Thermal"
        params = [copper_region, ins_region, impreg_region]
        return self.connection.send_and_receive(method, params)

    def set_mesh_generator_param(self, max_bnd_length, bnd_factor, max_angle):
        """Set mesh generator parameter."""
        method = "SetMeshGeneratorParam"
        params = [max_bnd_length, bnd_factor, max_angle]
        return self.connection.send_and_receive(method, params)

    def solve_problem(self):
        """Solve FEA problem."""
        method = "SolveProblem"
        return self.connection.send_and_receive(method)

    def add_region_thermal(
        self, reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density
    ):
        """Add thermal region."""
        method = "Add_Region_Thermal"
        params = [reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density]
        return self.connection.send_and_receive(method, params)

    def add_circular_conductor_a(
        self,
        xc,
        yc,
        copper_radius,
        ins_radius,
        ang_degree,
        points_no,
        mb,
        line,
        column,
        region_name,
        j_aux,
        loss_density,
    ):
        """Add circular conductor."""
        method = "AddCircularConductor_A"
        params = [
            xc,
            yc,
            copper_radius,
            ins_radius,
            ang_degree,
            points_no,
            mb,
            line,
            column,
            region_name,
            j_aux,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def add_rectangular_conductor_a(
        self,
        xc,
        yc,
        width,
        height,
        ins_width,
        ang_deg,
        points_no,
        mb,
        line,
        column,
        reg_name,
        j_aux,
        loss_density,
    ):
        """Add rectangular conductor."""
        method = "AddRectangularConductor_A"
        params = [
            xc,
            yc,
            width,
            height,
            ins_width,
            ang_deg,
            points_no,
            mb,
            line,
            column,
            reg_name,
            j_aux,
            loss_density,
        ]
        return self.connection.send_and_receive(method, params)

    def set_region_colour(self, region, colour):
        """Set region colour."""
        method = "SetRegionColour"
        params = [region, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_rt(self, r, t, reg_name):
        """Add point (r, t coordinates)."""
        method = "AddPoint_RT"
        params = [r, t, reg_name]
        return self.connection.send_and_receive(method, params)

    def add_point_magnetic_rt(self, r, t, mag_name, br_angle, br_mult, polarity):
        """Add magnetic point (r, t coordinates)."""
        method = "AddPoint_Magnetic_RT"
        params = [r, t, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)

    def add_point_magnetic_xy(self, x, y, mag_name, br_angle, br_mult, polarity):
        """Add magnetic point (x, y coordinates)."""
        method = "AddPoint_Magnetic_XY"
        params = [x, y, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)
