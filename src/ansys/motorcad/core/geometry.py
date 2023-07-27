"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""
from cmath import polar, rect
from math import degrees, radians


def xy_to_rt(x, y):
    """Convert Motor-CAD Cartesian coordinates to polar coordinates in degrees.

    Parameters
    ----------
    x : float
        X coordinate value.
    y : float
        Y coordinate value.

    Returns
    -------
    radius : float
        Radial coordinate value.
    theta : float
        Angular coordinate value.
    """
    rect_coordinates = complex(x, y)

    radius, theta = polar(rect_coordinates)

    return radius, degrees(theta)


def rt_to_xy(radius, theta):
    """Convert Motor-CAD polar coordinates to Cartesian coordinates in degrees.

    Parameters
    ----------
    radius : float
        Radial coordinate.
    theta : float
        Angular coordinate.

    Returns
    -------
    x : float
        X coordinate value.
    y : float
        Y coordinate value.
    """
    coordinates_complex = rect(radius, radians(theta))

    x = coordinates_complex.real
    y = coordinates_complex.imag

    return x, y


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
    import os

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
