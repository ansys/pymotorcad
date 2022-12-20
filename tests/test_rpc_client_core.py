from time import sleep

from psutil import pid_exists
import pytest

import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core import MotorCAD
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test__find_free_motor_cad():
    # Test if we can find open Motor-CAD instance
    mc2 = MotorCAD(open_new_instance=False)


def test_set_server_ip():
    def_address = pymotorcad.rpc_client_core.SERVER_IP

    # Use loopback address
    test_ip = "http://127.0.0.1"

    pymotorcad.set_server_ip(test_ip)

    assert pymotorcad.rpc_client_core.SERVER_IP == test_ip

    # Reset address to default
    pymotorcad.set_server_ip(def_address)
    assert pymotorcad.rpc_client_core.SERVER_IP == def_address


def test_set_motorcad_exe():
    test_path = r"test_path/test"

    pymotorcad.set_motorcad_exe(test_path)

    assert pymotorcad.rpc_client_core._find_motor_cad_exe() == test_path

    # reset path
    pymotorcad.set_motorcad_exe("")
    pymotorcad.rpc_client_core._find_motor_cad_exe()


# Test the method used to connect to Motor-CAD from internal scripting
def test_internal_connection():

    port = mc.connection._port

    pymotorcad.rpc_client_core.DEFAULT_INSTANCE = port

    mc2 = MotorCAD()

    assert mc2.connection._port == port

    # reset default instance flag
    pymotorcad.rpc_client_core.DEFAULT_INSTANCE = -1


# Test opening Motor-CAD with port defined
def test_open_new_with_port():
    test_port = 5555

    mc2 = MotorCAD(open_new_instance=True, port=test_port)

    assert mc2.connection._port == test_port

    mc2.quit()


# Test connecting to known Motor-CAD instance
def test_connect_existing_with_port():
    test_port = mc.connection._port

    mc2 = MotorCAD(open_new_instance=False, port=test_port)

    assert mc2.connection._port == test_port


def test_reusing_parallel_instances():
    # This should connect to mc test instance
    mc2 = MotorCAD(reuse_parallel_instances=True)
    original_port = mc2.connection._port

    mc3 = MotorCAD(reuse_parallel_instances=True)

    # Ensure connected to different instances
    assert mc3.connection._port != original_port

    # close second instance
    mc3.quit()

    mc2.set_free()

    # Check that original python object deleting doesn't close Motor-CAD
    del mc2

    mc3 = MotorCAD(reuse_parallel_instances=True)

    assert mc3.connection._port == original_port

    mc3.set_free()


# Check that Motor-CAD closes when Motor-CAD object is freed
def test_deleting_object():
    mc3 = MotorCAD(open_new_instance=True)

    proc_id = mc3.connection.pid

    del mc3

    # give process some time to fully close
    sleep(5)

    assert pid_exists(proc_id) is False


def test_rpc_communication_error():
    # raise error by calling method with incorrect params
    with pytest.raises(Exception) as e_info:
        mc.connection.send_and_receive("GetVariable", ["var", "extra params", 1])
        assert "One or more parameter types were invalid" in str(e_info.value)
