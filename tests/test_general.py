import pathlib

from RPC_Test_Common import almost_equal
from setup_test import reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def kh_to_ms(kh):
    return kh * 0.2777778


def test_save_load_clear_duty_cycle():
    # thermal transient calc
    mc.set_variable("ThermalCalcType", 1)

    # transient calc type - duty cycle
    mc.set_variable("TransientCalculationType", 1)

    assert almost_equal(mc.get_array_variable("Duty_Cycle_Vehicle_Speed_Start", 20), kh_to_ms(27.5))

    save_path = str(pathlib.Path(__file__).parent.resolve()) + "\\test_files\\duty_cycle.dat"
    mc.save_duty_cycle(save_path)

    mc.clear_duty_cycle()
    assert mc.get_variable("Duty_Cycle_Num_Periods") < 2

    mc.load_duty_cycle(save_path)
    assert almost_equal(mc.get_array_variable("Duty_Cycle_Vehicle_Speed_Start", 20), kh_to_ms(27.5))

    # reset model state
    reset_to_default_file(mc)
