from ansys.motorcad.core import MotorCAD

mc = MotorCAD(open_new_instance=False)

# mc.do_magnetic_calculation()

# (print(mc.get_array_variable("CustomLoss_name_internal_lab", 0))
mc.set_variable("NumCustomLossesInternal_Lab", 1)
mc.set_array_variable("CustomLoss_name_internal_lab", 0, "new name")
mc.set_array_variable("CustomLoss_Function_Internal_Lab", 0, "Idc")
mc.set_array_variable("CustomLoss_Type_Internal_Lab", 0, "Mechanical")
mc.set_array_variable("CustomLoss_ThermalNode_Internal_Lab", 0, -1)


def add_internal_custom_loss(name, function, type, thermal_node):
    pass


def remove_internal_custom_loss(index):
    pass


def remove_internal_custom_loss(name):
    pass
