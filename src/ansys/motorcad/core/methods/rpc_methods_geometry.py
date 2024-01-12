"""RPC methods for geometry."""
import os

class _RpcMethodsGeometry:
    def __init__(self, mc_connection):
        self.connection = mc_connection

    def set_winding_coil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        """Set go and return slots, positions, and turns for the winding coil.

        Parameters
        ----------
        phase : int
        path : int
        coil : int
        go_slot : int
        go_position : str
            Position values for the upper and lower paths of a go slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a go
            slot are ``"L"`` and ``"R"``.
        return_slot : int
        return_position : str
            Position values for the upper and lower paths of a return slot can
            be lowercase alphabetic characters, such as ``"a"``, ``"b"``,
            and ``"c"``. Position values for left and right paths of a return
            slot are ``"L"`` and ``"R"``.
        turns : int
        """
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            go_slot,
            go_position,
            return_slot,
            return_position,
            turns,
        ]
        return self.connection.send_and_receive(method, params)

    def get_winding_coil(self, phase, path, coil):
        """Get the go and return slots, positions, and turns for the winding coil.

        In Motor-CAD, you can select **Winding -> Pattern** to see how phases, paths,
        and coils are indexed.

        Parameters
        ----------
        phase : int
        path : int
        coil : int

        Returns
        -------
        GoSlot : int
        GoPosition : str
        ReturnSlot : int
        ReturnPosition : str
        Turns : int
        """
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.connection.send_and_receive(method, params)

    def check_if_geometry_is_valid(self, edit_geometry):
        """Check if the Motor-CAD geometry is valid.

        Parameters
        ----------
        edit_geometry : int
            Indicates if Motor-CAD can try to reset the geometry
            within constraints if the geometry is invalid. Options are:

            - ``1``: Yes. Try and reset the geometry
            - ``0``: No. Do not try to reset the geometry.

        Returns
        -------
        int
            ``1`` if an attempt to reset the geometry has been made, ``O`` otherwise.
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.connection.send_and_receive(method, params)
    

    def template_list(self):
        """Return List of templates available in Motor-CAD.

            Individual template information is in dictionary format
            for example
            [{'Template': 'a1',
            'Sector': 'Aerospace',
        '     Machine_Type': ' Surface PM',
            'Application': ' Generator',
            'Winding_Type': ' Concentrated',
            'Max_Speed(rpm)': ' 10,000',
            'Power(kW)': ' 14',
        '     Cooling': 'Oil cooled',
        '     Drive_Type': 'Sine'},]
        """
    

        # Motor-CAD installation directory in PC
        mcad_install_dir = self.get_variable("CurrentExeDir_MotorLAB")
        directory = mcad_install_dir + r"Motor-CAD Data\templates"
        template_list1 = []
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if filename.endswith(".mtt"):
                with open(f, "r") as file:
                    print(filename)
                    for l_no, line in enumerate(file):
                        # search string
                        if "Data_File_Notes[1]" in line:
                            print("string found in a file")
                            print("Line Number:", l_no)
                            print("Line:", line)
                            # don't look for next lines
                            list1 = line.split(";")
                            list1[0] = list1[0][19:]
                            dict1 = {
                                "Template": filename.split(".")[0],
                                "Sector": list1[0],
                                "Machine_Type": list1[1],
                                "Application": list1[2],
                                "Winding_Type": list1[3],
                                "Max_Speed(rpm)": list1[4],
                                "Power(kW)": list1[5],
                                "Cooling": list1[6],
                                "Drive_Type": list1[7],
                            }
                            template_list1.append(dict1)
                            break

        return template_list1

