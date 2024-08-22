from os import remove
from tkinter.font import names

from ansys.motorcad.core import MotorCAD

mc = MotorCAD(open_new_instance=False)

# mc.do_magnetic_calculation()

# (print(mc.get_array_variable("CustomLoss_name_internal_lab", 0))
# mc.set_variable("NumCustomLossesInternal_Lab", 1)
# mc.set_array_variable("CustomLoss_name_internal_lab", 0, "new name")
# mc.set_array_variable("CustomLoss_Function_Internal_Lab", 0, "Idc")
# mc.set_array_variable("CustomLoss_Type_Internal_Lab", 0, "Mechanical")
# mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", 0, -1)


def add_internal_custom_loss(name, function, type, thermal_node):
    # Find number of losses
    no_losses = mc.get_variable("NumCustomLossesInternal_Lab")
    # Increase array length by 1
    mc.set_variable("NumCustomLossesInternal_Lab", no_losses+1)
    # Define properties
    mc.set_array_variable("CustomLoss_name_internal_lab", no_losses, name)
    mc.set_array_variable("CustomLoss_Function_Internal_Lab", no_losses, function)
    mc.set_array_variable("CustomLoss_Type_Internal_Lab", no_losses, type)
    mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_losses, thermal_node)
    pass

def remove_internal_custom_loss(index):
    # Find number of losses
    no_losses = mc.get_variable("NumCustomLossesInternal_Lab")
    if index == no_losses:
        mc.set_variable("NumCustomLossesInternal_Lab", no_losses - 1)
    # Decrease array length by 1
    mc.set_variable("NumCustomLossesInternal_Lab", no_losses - 1)
    pass


# def remove_internal_custom_loss(name):
#     for i in mc.CustomLoss_name_internal_lab:
#         if mc.CustomLoss_name_internal_lab[i] == name:
#
#         else:
#             pass
#     pass
