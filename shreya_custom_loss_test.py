from os import remove
from tkinter.font import names

# from numpy import error_message

from ansys.motorcad.core import MotorCAD
from examples.links.ece_export_for_twinbuilder import index

# from examples.links.ece_export_for_twinbuilder import index

mc = MotorCAD(open_new_instance=False)

# Global variables
kNumCustomLossesInternal_Lab = "NumCustomLossesInternal_Lab"
kCustomLoss_name_internal_lab = "CustomLoss_name_internal_lab"
kCustomLoss_Function_Internal_Lab = "CustomLoss_Function_Internal_Lab"
kCustomLoss_Type_Internal_Lab = "CustomLoss_Type_Internal_Lab"
kCustomLoss_ThermalNode_Internal_Lab = "CustomLoss_ThermalNode_Internal_Lab"
kNumCustomLossesExternal_Lab = "NumCustomLossesExternal_Lab"
kCustomLoss_Name_External_Lab = "CustomLoss_Name_External_Lab"
kCustomLoss_PowerFunction_External_Lab = "CustomLoss_PowerFunction_External_Lab"
kCustomLoss_VoltageFunction_External_Lab = "CustomLoss_VoltageFunction_External_Lab"

def add_internal_custom_loss(name, function, type, thermal_node):
    type = type.capitalize()
    # Internal Custom Loss Type is case-sensitive in MotorCAD. Added a line to match the required format.
    if type not in ["Electrical", "Mechanical"]:
        raise ValueError("Thermal Loss Type must be Electrical or Mechanical")
    if mc.get_node_exists(thermal_node) == False:
        raise ValueError("Thermal node does not exist")
    else:
        # Find number of losses
        no_internal_losses = mc.get_variable(kNumCustomLossesInternal_Lab)
        # Increase array length by 1
        mc.set_variable(kNumCustomLossesInternal_Lab, no_internal_losses + 1)
        # Define properties
        mc.set_array_variable(kCustomLoss_name_internal_lab, no_internal_losses, name)
        mc.set_array_variable(kCustomLoss_Function_Internal_Lab, no_internal_losses, function)
        mc.set_array_variable(kCustomLoss_Type_Internal_Lab, no_internal_losses, type)
        mc.set_array_variable(kCustomLoss_ThermalNode_Internal_Lab, no_internal_losses, thermal_node)

def add_external_custom_loss(name, power_function, voltage_function):
    no_external_losses = mc.get_variable(kNumCustomLossesExternal_Lab)
    mc.set_variable(kNumCustomLossesExternal_Lab, no_external_losses + 1)
    mc.set_array_variable(kCustomLoss_Name_External_Lab, no_external_losses, name)
    mc.set_array_variable(kCustomLoss_PowerFunction_External_Lab, no_external_losses, power_function)
    mc.set_array_variable(kCustomLoss_VoltageFunction_External_Lab, no_external_losses, voltage_function)

def remove_internal_custom_loss(name):
    index = _get_index_from_name(name, kCustomLoss_name_internal_lab)
    _motorcad_array_pop(index, kNumCustomLossesInternal_Lab, [kCustomLoss_name_internal_lab, kCustomLoss_Function_Internal_Lab,
                                                                                kCustomLoss_Type_Internal_Lab, kCustomLoss_ThermalNode_Internal_Lab])

def remove_external_custom_loss(name):
    index = _get_index_from_name(name, kCustomLoss_Name_External_Lab)
    _motorcad_array_pop(index, kNumCustomLossesExternal_Lab,[kCustomLoss_Name_External_Lab, kCustomLoss_PowerFunction_External_Lab,
                                                                                 kCustomLoss_VoltageFunction_External_Lab])

def _motorcad_array_pop(index, var_length_array, list_of_var_names):
    array_length = mc.get_variable(var_length_array)

    for i in range(index+1, array_length):
        for j in range(len(list_of_var_names)):
            mc.set_array_variable(list_of_var_names[j], i-1, mc.get_array_variable(list_of_var_names[j], i))


    mc.set_variable(var_length_array, array_length - 1)

def _get_index_from_name(name, variable):
    for i in range(len(variable)):
        if name == mc.get_array_variable(variable, i):
            index = i
            return index








