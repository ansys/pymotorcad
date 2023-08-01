import pytest

from ansys.motorcad.core import MotorCADError
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()

def test_example():
    slot_width = mc.get_variable("slot_width")
    assert slot_width > 0
