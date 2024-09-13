from RPC_Test_Common import reset_to_default_file


def test_model_build_lab(mc):
    reset_to_default_file(mc)

    # base test file includes built model
    assert mc.get_model_built_lab() is True

    mc.clear_model_build_lab()
    assert mc.get_model_built_lab() is False

    mc.build_model_lab()
    assert mc.get_model_built_lab() is True


def test_calculate_test_performance_lab(mc):
    mc.calculate_test_performance_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_export_duty_cycle_lab(mc):
    # Automotive cycle
    mc.set_variable("DutyCycleType_Lab", 1)
    # EUDC cycle
    mc.set_variable("DrivCycle_MotorLab", 4)

    mc.calculate_duty_cycle_lab()

    mc.export_duty_cycle_lab()

    # Check losses transferred
    assert mc.get_array_variable("Duty_Cycle_Armature_Copper_Loss_DC", 50) != 0


def test_calculate_operating_point_lab(mc):
    mc.calculate_operating_point_lab()

    assert mc.get_variable("LabOpPoint_ShaftTorque") != 0


def test_calculate_magnetic_lab(mc):
    mc.calculate_magnetic_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_thermal_lab(mc):
    mc.calculate_thermal_lab()
    # Not sure how to test this has run successfully other than checking for exception

def test_add_internal_custom_loss(mc):
    name = "Stator iron Loss Connection"
    power_loss_function = "Speed**2 * (5.4E-9 * Iron_Loss_Stator - 1.7E-5 * Iron_Loss_Stator**2 + 1.43)"
    type = "Electrical"
    thermal_node = 2
    no_internal_losses = mc.get_variable("NumCustomLossesInternal_Lab")

    mc.add_internal_custom_loss(name,power_loss_function,type,thermal_node)

    assert mc.get_variable("NumCustomLossesInternal_Lab") == no_internal_losses + 1
    assert mc.get_array_variable("CustomLoss_name_internal_lab", no_internal_losses) == name
    assert mc.get_array_variable("CustomLoss_Function_Internal_Lab", no_internal_losses) == power_loss_function
    assert mc.get_array_variable("CustomLoss_Type_Internal_Lab", no_internal_losses) == type
    assert mc.get_array_variable("CustomLoss_ThermalNode_Internal_Lab", no_internal_losses) == thermal_node


def test_add_external_custom_loss(mc):
    name = "Battery Loss"
    power_loss_function = "(1E-2 * Mechanical_Loss**2) * Speed/10000 + min(5, Speed)"
    voltage_drop_function = "Idc * 2.5E-2"
    no_external_losses = mc.get_variable("NumCustomLossesExternal_Lab")

    mc.add_external_custom_loss(name, power_loss_function, voltage_drop_function)

    assert mc.get_variable("NumCustomLossesExternal_Lab") == no_external_losses + 1
    assert mc.get_array_variable("CustomLoss_Name_External_Lab", no_external_losses) == name
    assert mc.get_array_variable("CustomLoss_PowerFunction_External_Lab", no_external_losses) == power_loss_function
    assert mc.get_array_variable("CustomLoss_VoltageFunction_External_Lab", no_external_losses) == voltage_drop_function

def test_remove_internal_custom_loss(mc):
    pass

def test_remove_external_custom_loss(mc):
    pass

