from ansys.motorcad.core import MotorCAD
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test__find_free_motor_cad():
    # Test if we can find open Motor-CAD instance
    mc2 = MotorCAD(open_new_instance=False)


# trigger actions
