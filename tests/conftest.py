import pytest

from RPC_Test_Common import reset_temp_file_folder, reset_to_default_file
import ansys.motorcad.core
from ansys.motorcad.core import MotorCAD

motorcad_instance = None


def pytest_sessionstart(session):
    global motorcad_instance

    reset_temp_file_folder()
    ansys.motorcad.core.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = True


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    ...  # Your code goes here
    global motorcad_instance
    if hasattr(motorcad_instance, "quit"):
        motorcad_instance.quit()


@pytest.fixture
def mc():
    """Set up test environment for whole unit of tests"""
    global motorcad_instance

    if not (hasattr(motorcad_instance, "is_open") and motorcad_instance.is_open()):
        motorcad_instance = MotorCAD()
        # Disable messages if opened with UI
        motorcad_instance.set_variable("MessageDisplayState", 2)
        reset_to_default_file(motorcad_instance)

        # Disable messages if opened with UI
        motorcad_instance.set_variable("MessageDisplayState", 2)

    return motorcad_instance
