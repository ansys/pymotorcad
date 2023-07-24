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

def template_list():
    """ Returns List of templates avaialbe with Motor-CAD
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
    list=[{'Template': 'a1',
            'Sector': 'Aerospace',
            'Machine_Type': ' Surface PM',
            'Application': ' Generator',
            'Winding_Type': ' Concentrated',
            'Max_Speed(rpm)': ' 10,000',
            'Power(kW)': ' 14',
            'Cooling': 'Oil cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'a2',
            'Sector': 'Aerospace',
            'Machine_Type': ' Surface PM',
            'Application': ' Motor',
            'Winding_Type': ' Concentrated',
            'Max_Speed(rpm)': ' 1,500',
            'Power(kW)': ' 195',
            'Cooling': 'Air cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'a3',
            'Sector': 'Aerospace',
            'Machine_Type': 'SPM outer rotor',
            'Application': 'UAV Motor',
            'Winding_Type': 'Concentrated',
            'Max_Speed(rpm)': ' 3,000',
            'Power(kW)': '0.120',
            'Cooling': 'Air cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'e10',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'Automotive',
            'Winding_Type': 'Hairpin',
            'Max_Speed(rpm)': '15000',
            'Power(kW)': '200',
            'Cooling': 'Oil Cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'e1_eMobility_IPM_150kW',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'P4-Automotive',
            'Winding_Type': 'Stranded distributed',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '150',
            'Cooling': 'Water Jacket + Internal Air',
            'Drive_Type': 'Sine'},
            {'Template': 'e2_eMobility_IPM_hairpin_150kW',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'P4-Automotive',
            'Winding_Type': 'Hairpin distributed',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '150',
            'Cooling': 'Water Jacket + Oil Spray',
            'Drive_Type': 'Sine'},
            {'Template': 'e3_eMobility_WFSM_150kW',
            'Sector': 'eMobility',
            'Machine_Type': 'SYNC',
            'Application': 'P4-Automotive',
            'Winding_Type': 'Stranded distributed',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '150',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Sine'},
            {'Template': 'e4a_EMobility_IPM',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'Automotive',
            'Winding_Type': 'Hairpin',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '150',
            'Cooling': 'Water Jacket + Shaft cooling',
            'Drive_Type': 'Sine'},
            {'Template': 'e4_eMobility_BPMOR_hairpin',
            'Sector': 'eMobility',
            'Machine_Type': 'BPMOR',
            'Application': 'P4-Automotive',
            'Winding_Type': 'Hairpin',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '200',
            'Cooling': 'Axle water jacket',
            'Drive_Type': 'Sine'},
            {'Template': 'e5_eMobility_IM_150kW',
            'Sector': 'eMobility',
            'Machine_Type': 'IM',
            'Application': 'P4-Automotive',
            'Winding_Type': 'Stranded distributed',
            'Max_Speed(rpm)': '12,000',
            'Power(kW)': '150',
            'Cooling': 'Water Jacket + Rotor cooling',
            'Drive_Type': 'Sine'},
            {'Template': 'e6_emobility_SRM_100kW',
            'Sector': 'eMobility',
            'Machine_Type': 'SRM',
            'Application': 'Automotive',
            'Winding_Type': 'Stranded Distributed',
            'Max_Speed(rpm)': '10,000',
            'Power(kW)': '18',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Square'},
            {'Template': 'e7_eMobility_SPM_20kW',
            'Sector': 'eMobility',
            'Machine_Type': 'SPM',
            'Application': 'Turbocharger',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '150,000',
            'Power(kW)': '20',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Sine'},
            {'Template': 'e8_eMobility_IPM',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'Automotive',
            'Winding_Type': 'Stranded Distributed',
            'Max_Speed(rpm)': '10,000',
            'Power(kW)': '80',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Sine'},
            {'Template': 'e9_eMobility_IPM',
            'Sector': 'eMobility',
            'Machine_Type': 'IPM',
            'Application': 'Automotive',
            'Winding_Type': 'Stranded Distributed',
            'Max_Speed(rpm)': '10,000',
            'Power(kW)': '120',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Sine'},
            {'Template': 'i1_Industrial_SPM_square',
            'Sector': 'Industrial',
            'Machine_Type': 'SPM',
            'Application': 'Pump/Fan',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': '3.5',
            'Cooling': 'Fan cooled',
            'Drive_Type': 'Square'},
            {'Template': 'i2_Industrial_SPM_sine',
            'Sector': 'Industrial',
            'Machine_Type': 'SPM',
            'Application': 'Pump/Fan',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': '5',
            'Cooling': 'Fan cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'i3_Industrial_SyncRel',
            'Sector': 'Industrial',
            'Machine_Type': 'SyncRel',
            'Application': 'Pump/Fan',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': ' ',
            'Cooling': 'Fan cooled',
            'Drive_Type': 'Sine'},
            {'Template': 'i4_Industrial_IM',
            'Sector': 'Industrial',
            'Machine_Type': 'IM',
            'Application': 'Pump/Fan',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': '',
            'Cooling': 'Fan cooled',
            'Drive_Type': 'Direct online'},
            {'Template': 'i5_Industrial_SPM_Servo_Tooth_Wound',
            'Sector': 'Industrial',
            'Machine_Type': 'SPM',
            'Application': 'Servo',
            'Winding_Type': 'Concentrated',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': '1.1',
            'Cooling': 'Totally Enclosed Non Ventilated (TENV)',
            'Drive_Type': 'Sine'},
            {'Template': 'i6a_HV_1MW_FOC',
            'Sector': 'Industrial',
            'Machine_Type': 'IM',
            'Application': 'Oil/Gas',
            'Winding_Type': 'Round wire',
            'Max_Speed(rpm)': '',
            'Power(kW)': '1,000',
            'Cooling': 'Axial through vent',
            'Drive_Type': 'FOC'},
            {'Template': 'i6b_HV_IM_oilgas',
            'Sector': 'Industrial',
            'Machine_Type': 'IM',
            'Application': 'Oil/Gas',
            'Winding_Type': 'Form Wound',
            'Max_Speed(rpm)': '1,500',
            'Power(kW)': '650',
            'Cooling': 'Axial through vent',
            'Drive_Type': 'Direct online'},
            {'Template': 'i7_IM_1MW_Generator',
            'Sector': 'Industrial',
            'Machine_Type': 'IM',
            'Application': 'Power Generation',
            'Winding_Type': 'Form Wound',
            'Max_Speed(rpm)': '3,000',
            'Power(kW)': '1,000',
            'Cooling': 'Radial through vent',
            'Drive_Type': 'Direct online generator'},
            {'Template': 'i8_IEEJ_IPM_D-Model',
            'Sector': 'Industrial',
            'Machine_Type': 'IPM',
            'Application': 'Benchmark Motor',
            'Winding_Type': 'Distributed',
            'Max_Speed(rpm)': '2,000',
            'Power(kW)': '0.7',
            'Cooling': 'Axial through vent',
            'Drive_Type': 'Sine'},
            {'Template': 'i9_SYNC_HV_325kW_Generator',
            'Sector': 'Industrial',
            'Machine_Type': ' SYNC',
            'Application': ' Power Generation',
            'Winding_Type': ' Form Wound',
            'Max_Speed(rpm)': ' 1,000',
            'Power(kW)': ' 325',
            'Cooling': 'Water Jacket',
            'Drive_Type': 'Passive Gen'},
            {'Template': 'r1',
            'Sector': 'Renewable',
            'Machine_Type': 'Surface PM',
            'Application': 'Direct Drive Wind Turbine',
            'Winding_Type': ' Concentrated',
            'Max_Speed(rpm)': '150',
            'Power(kW)': '6',
            'Cooling': 'Air cooled',
            'Drive_Type': ' Rectifier'}]
    return list 