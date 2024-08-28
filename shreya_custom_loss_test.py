from os import remove
from tkinter.font import names

from ansys.motorcad.core import MotorCAD

mc = MotorCAD(open_new_instance=False)

# mc.do_magnetic_calculation()

# print(mc.get_array_variable("CustomLoss_name_internal_lab", 0))
# mc.set_variable("NumCustomLossesInternal_Lab", 5)
# for i in range(5):
#     mc.set_array_variable("CustomLoss_name_internal_lab", i, "new name" + str(i))
#     mc.set_array_variable("CustomLoss_Function_Internal_Lab", i, "Idc")
#     mc.set_array_variable("CustomLoss_Type_Internal_Lab", i, "Mechanical")
#     mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", i, -1)



def add_internal_custom_loss(name, function, type, thermal_node):
    # Find number of losses
    no_internal_losses = mc.get_variable("NumCustomLossesInternal_Lab")
    # Increase array length by 1
    mc.set_variable("NumCustomLossesInternal_Lab", no_internal_losses+1)
    # Define properties
    mc.set_array_variable("CustomLoss_name_internal_lab", no_internal_losses, name)
    mc.set_array_variable("CustomLoss_Function_Internal_Lab", no_internal_losses, function)
    mc.set_array_variable("CustomLoss_Type_Internal_Lab", no_internal_losses, type)
    mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_internal_losses, thermal_node)

def add_external_custom_loss(name, power_function, voltage_function):
    no_external_losses = mc.get_variable("NumCustomLossesExternal_Lab")
    mc.set_variable("NumCustomLossesExternal_Lab", no_external_losses + 1)
    mc.set_array_variable('CustomLoss_Name_External_Lab', no_external_losses, name)
    mc.set_array_variable('CustomLoss_PowerFunction_External_Lab', no_external_losses, power_function)
    mc.set_array_variable('CustomLoss_VoltageFunction_External_Lab', no_external_losses, voltage_function)

def remove_internal_custom_loss(index):
    # Find number of losses
    no_internal_losses = mc.get_variable("NumCustomLossesInternal_Lab")

    # Collapse variables upwards at location of index
    for i in range(index+1,no_internal_losses):
        mc.set_array_variable("CustomLoss_name_internal_lab",i-1,mc.get_array_variable("CustomLoss_name_internal_lab", i))
        mc.set_array_variable("CustomLoss_Function_Internal_Lab",i-1,mc.get_array_variable("CustomLoss_Function_internal_lab", i))
        mc.set_array_variable("CustomLoss_Type_Internal_Lab",i-1,mc.get_array_variable("CustomLoss_Type_internal_lab", i))
        mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab",i-1,mc.get_array_variable("CustomLoss_ThermalNode_internal_lab", i))

        # Decrease array length by 1
    mc.set_variable("NumCustomLossesInternal_Lab", no_internal_losses - 1)

def remove_internal_custom_loss_name(name):
    no_internal_losses = mc.get_variable("NumCustomLossesInternal_Lab")
    for i in range(no_internal_losses):
        if name == mc.get_array_variable("CustomLoss_name_internal_lab", i):
            remove_internal_custom_loss(i)
            break


