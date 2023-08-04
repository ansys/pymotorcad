from setup_test import reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_model_build_lab():
    reset_to_default_file(mc)

    # base test file includes built model
    assert mc.get_model_built_lab() is True

    mc.clear_model_build_lab()
    assert mc.get_model_built_lab() is False

    mc.build_model_lab()
    assert mc.get_model_built_lab() is True


def test_calculate_test_performance_lab():
    mc.calculate_test_performance_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_export_duty_cycle_lab():
    # Automotive cycle
    mc.set_variable("DutyCycleType_Lab", 1)
    # EUDC cycle
    mc.set_variable("DrivCycle_MotorLab", 4)

    mc.calculate_duty_cycle_lab()

    mc.export_duty_cycle_lab()

    # Check losses transferred
    assert mc.get_array_variable("Duty_Cycle_Armature_Copper_Loss_DC", 50) != 0


def test_calculate_operating_point_lab():
    mc.calculate_operating_point_lab()

    assert mc.get_variable("LabOpPoint_ShaftTorque") != 0


def test_calculate_magnetic_lab():
    mc.calculate_magnetic_lab()
    # Not sure how to test this has run successfully other than checking for exception


def test_calculate_thermal_lab():
    mc.calculate_thermal_lab()
    # Not sure how to test this has run successfully other than checking for exception
