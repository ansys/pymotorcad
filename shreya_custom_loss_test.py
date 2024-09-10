from os import remove
from tkinter.font import names

# from numpy import error_message

from ansys.motorcad.core import MotorCAD

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
    if type not in ["Electrical", "Mechanical"]:
        raise ValueError("Thermal Loss Type must be Electrical or Mechanical")
    elif mc.get_node_exists(thermal_node) == False:
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

def remove_internal_custom_loss(index):
    # Find number of losses
    no_internal_losses = mc.get_variable(kNumCustomLossesInternal_Lab)

    # Collapse variables upwards at location of index
    for i in range(index+1,no_internal_losses):
        mc.set_array_variable(kCustomLoss_name_internal_lab,i-1,mc.get_array_variable(kCustomLoss_name_internal_lab, i))
        mc.set_array_variable(kCustomLoss_Function_Internal_Lab,i-1,mc.get_array_variable(kCustomLoss_Function_Internal_Lab, i))
        mc.set_array_variable(kCustomLoss_Type_Internal_Lab,i-1,mc.get_array_variable(kCustomLoss_Type_Internal_Lab, i))
        mc.set_array_variable(kCustomLoss_ThermalNode_Internal_Lab,i-1,mc.get_array_variable(kCustomLoss_ThermalNode_Internal_Lab, i))

        # Decrease array length by 1
    mc.set_variable(kNumCustomLossesInternal_Lab, no_internal_losses - 1)

def remove_internal_custom_loss_name(name):
    no_internal_losses = mc.get_variable(kNumCustomLossesInternal_Lab)
    for i in range(no_internal_losses):
        if name == mc.get_array_variable(kCustomLoss_name_internal_lab, i):
            remove_internal_custom_loss(i)
            break

def remove_external_custom_loss(index):
    no_external_losses = mc.get_variable(kNumCustomLossesExternal_Lab)
    for i in range(index+1, no_external_losses):
        mc.set_array_variable(kCustomLoss_Name_External_Lab,i-1,mc.get_array_variable(kCustomLoss_Name_External_Lab, i))
        mc.set_array_variable(kCustomLoss_PowerFunction_External_Lab,i-1,mc.get_array_variable(kCustomLoss_PowerFunction_External_Lab, i))
        mc.set_array_variable(kCustomLoss_VoltageFunction_External_Lab,i-1,mc.get_array_variable(kCustomLoss_VoltageFunction_External_Lab, i))

    mc.set_variable(kNumCustomLossesExternal_Lab, no_external_losses - 1)


def remove_external_custom_loss_name(name):
    no_external_losses = mc.get_variable(kNumCustomLossesExternal_Lab)
    for i in range(no_external_losses):
        if name == mc.get_array_variable(kCustomLoss_Name_External_Lab, i):
            remove_external_custom_loss(i)
            break
    pass

# Code repetition:
# Finding Number of External/Internal Losses
