from os import remove
from tkinter.font import names

# from numpy import error_message

from ansys.motorcad.core import MotorCAD
# from examples.links.ece_export_for_twinbuilder import index

# from examples.links.ece_export_for_twinbuilder import index

mc = MotorCAD(open_new_instance=False)

# Global variables
k_num_custom_losses_internal_lab = "NumCustomLossesInternal_Lab"
k_custom_loss_name_internal_lab = "CustomLoss_name_internal_lab"
k_custom_loss_function_internal_lab = "CustomLoss_Function_Internal_Lab"
k_custom_loss_type_internal_lab = "CustomLoss_Type_Internal_Lab"
k_custom_loss_thermal_node_internal_lab = "CustomLoss_ThermalNode_Internal_Lab"
k_num_custom_losses_external_lab = "NumCustomLossesExternal_Lab"
k_custom_loss_name_external_lab = "CustomLoss_Name_External_Lab"
k_custom_loss_power_function_external_lab = "CustomLoss_PowerFunction_External_Lab"
k_custom_loss_voltage_function_external_lab = "CustomLoss_VoltageFunction_External_Lab"

def add_internal_custom_loss(name, function, type, thermal_node):
    type = type.capitalize()
    # Internal Custom Loss Type is case-sensitive in MotorCAD. Added a line to match the required format.
    if type not in ["Electrical", "Mechanical"]:
        raise ValueError("Thermal Loss Type must be Electrical or Mechanical")
    if not mc.get_node_exists(thermal_node):
        raise ValueError("Thermal node does not exist")
    else:
        # Find number of losses
        no_internal_losses = mc.get_variable(k_num_custom_losses_internal_lab)
        # Increase array length by 1
        mc.set_variable(k_num_custom_losses_internal_lab, no_internal_losses + 1)
        # Define properties
        mc.set_array_variable(k_custom_loss_name_internal_lab, no_internal_losses, name)
        mc.set_array_variable(k_custom_loss_function_internal_lab, no_internal_losses, function)
        mc.set_array_variable(k_custom_loss_type_internal_lab, no_internal_losses, type)
        mc.set_array_variable(k_custom_loss_thermal_node_internal_lab, no_internal_losses, thermal_node)

def add_external_custom_loss(name, power_function, voltage_function):
    no_external_losses = mc.get_variable(k_num_custom_losses_external_lab)
    mc.set_variable(k_num_custom_losses_external_lab, no_external_losses + 1)
    mc.set_array_variable(k_custom_loss_name_external_lab, no_external_losses, name)
    mc.set_array_variable(k_custom_loss_power_function_external_lab, no_external_losses, power_function)
    mc.set_array_variable(k_custom_loss_voltage_function_external_lab, no_external_losses, voltage_function)

def remove_internal_custom_loss(name):
    index = _get_index_from_name(name, k_num_custom_losses_internal_lab,  k_custom_loss_name_internal_lab)
    _motorcad_array_pop(index, k_num_custom_losses_internal_lab, [k_custom_loss_name_internal_lab, k_custom_loss_function_internal_lab,
                                                                  k_custom_loss_type_internal_lab, k_custom_loss_thermal_node_internal_lab])

def remove_external_custom_loss(name):
    index = _get_index_from_name(name,k_num_custom_losses_external_lab, k_custom_loss_name_external_lab)
    _motorcad_array_pop(index, k_num_custom_losses_external_lab, [k_custom_loss_name_external_lab, k_custom_loss_power_function_external_lab,
                                                                  k_custom_loss_voltage_function_external_lab])

def _motorcad_array_pop(index, var_length_array, list_of_var_names):
    array_length = mc.get_variable(var_length_array)

    for i in range(index+1, array_length):
        for j in range(len(list_of_var_names)):
            mc.set_array_variable(list_of_var_names[j], i-1, mc.get_array_variable(list_of_var_names[j], i))


    mc.set_variable(var_length_array, array_length - 1)

def _get_index_from_name(name, var_length_array, variable_name):
    array_length = mc.get_variable(var_length_array)
    for i in range(array_length):
        if name == mc.get_array_variable(variable_name, i):
            index = i
            break
    else:
        raise NameError("Provided name is not listed")
    return index

