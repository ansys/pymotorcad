"""Contains JSON-RPC API methods which are just for internal use.

DO NOT USE IN SCRIPTS.
These can be for internal testing or might be unfinished/undocumented/deprecated functions.
"""


class _RpcMethodsInternal:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def is_stop_requested(self):
        """Intercept button clicks in python since it does not use a separate thread."""
        method = "IsStopRequested"
        return self.connection.send_and_receive(method)

    def update_interface(self):
        method = "UpdateInterface"
        return self.connection.send_and_receive(method)

    def avoid_immediate_update(self, avoid_update):
        """Set to true to speed up the setting of inputs.

        The steady state calc will only now be calculated when DoSteadyStateAnalysis is called.

        Parameters
        ----------
        avoid_update: bool
        """
        method = "AvoidImmediateUpdate"
        params = [{"variant": avoid_update}]
        return self.connection.send_and_receive(method, params)

    def get_im_iron_loss(self, slip, back_emf):
        """Get analytic iron loss using data from FEA solution.

        The E-magnetic model must be solved prior to method call.

        Parameters
        ----------
        slip : float
            The induction motor slip.
        back_emf : float

        Returns
        -------
        EddyLoss : float
            Summation of stator tooth, stator back iron, rotor tooth and rotor back iron eddy
            current losses
        HysLoss : float
            Summation of stator tooth, stator back iron, rotor tooth and rotor back iron
            hysteresis losses
        """
        method = "GetIMIronLoss"
        params = [slip, back_emf]
        return self.connection.send_and_receive(method, params)

    def set_all_emag_calculations(self, state):
        """Control whether all or none of the performance tests are enabled.

        Parameters
        ----------
        state : bool
            True enables all performance tests.
        """
        method = "SetAllEmagCalculations"
        params = [state]
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
        method = "SetBndCond"
        params = [dir_code, c1, c2, c3]
        return self.connection.send_and_receive(method, params)

    def store_problem_data(self, p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max):
        method = "StoreProblemData"
        params = [p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max]
        return self.connection.send_and_receive(method, params)

    def add_point_xy(self, x, y, reg_name):
        method = "AddPoint_XY"
        params = [x, y, reg_name]
        return self.connection.send_and_receive(method, params)

    def create_optimised_mesh_thermal(self, copper_region, ins_region, impreg_region):
        method = "CreateOptimisedMesh_Thermal"
        params = [copper_region, ins_region, impreg_region]
        return self.connection.send_and_receive(method, params)

    def set_mesh_generator_param(self, max_bnd_length, bnd_factor, max_angle):
        method = "SetMeshGeneratorParam"
        params = [max_bnd_length, bnd_factor, max_angle]
        return self.connection.send_and_receive(method, params)

    def solve_problem(self):
        method = "SolveProblem"
        return self.connection.send_and_receive(method)

    def add_region_thermal(
        self, reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density
    ):
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
        method = "SetRegionColour"
        params = [region, colour]
        return self.connection.send_and_receive(method, params)

    def add_point_rt(self, r, t, reg_name):
        method = "AddPoint_RT"
        params = [r, t, reg_name]
        return self.connection.send_and_receive(method, params)

    def add_point_magnetic_rt(self, r, t, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_RT"
        params = [r, t, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)

    def add_point_magnetic_xy(self, x, y, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_XY"
        params = [x, y, mag_name, br_angle, br_mult, polarity]
        return self.connection.send_and_receive(method, params)

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

    def _get_region_properties_xy(self, x, y):
        """Get properties of region from name and coordinates.

        Returns list of parameters. Currently only used for testing other geometry functions.
        EXPERIMENTAL FUNCTION - LIKELY TO CHANGE.

        Parameters
        ----------
        x : float
            region position x coordinate
        y : float
            region position y coordinate
        """
        method = "GetRegionProperties_XY"
        params = [x, y]
        return self.connection.send_and_receive(method, params)
