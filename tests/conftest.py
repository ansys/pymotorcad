import pytest

from RPC_Test_Common import reset_temp_file_folder, reset_to_default_file
import ansys.motorcad.core
from ansys.motorcad.core import MotorCAD

motorcad_instance = None
motorcad_instance_fea_old = None


def pytest_sessionstart(session):
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

    return motorcad_instance


@pytest.fixture
def mc_fea_old():
    """Old fea geometry tests cause lots of conflicts - use a new MotorCAD"""
    global motorcad_instance_fea_old

    if not (hasattr(motorcad_instance_fea_old, "is_open") and motorcad_instance_fea_old.is_open()):
        motorcad_instance_fea_old = MotorCAD()
        # Disable messages if opened with UI
        motorcad_instance_fea_old.set_variable("MessageDisplayState", 2)
        reset_to_default_file(motorcad_instance_fea_old)

    return motorcad_instance_fea_old
