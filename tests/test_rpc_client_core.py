from time import sleep
from unittest.mock import create_autospec

import ansys.platform.instancemanagement as pypim
import grpc
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

    pymotorcad.rpc_client_core.set_default_instance(port)

    mc2 = MotorCAD()

    assert mc2.connection._port == port

    # reset default instance flag
    pymotorcad.rpc_client_core.DEFAULT_INSTANCE = -1


# Test opening Motor-CAD with port defined
def test_open_new_with_port():
    test_port = 36020

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


def test_ansys_labs_connection(monkeypatch):
    # Use existing Motor-CAD (mc.connection._port)
    mock_instance = pypim.Instance(
        definition_name="definitions/fake-motorcad",
        name="instances/fake-motorcad",
        ready=True,
        status_message=None,
        services={
            "http": pypim.Service(uri="http://localhost:" + str(mc.connection._port), headers={})
        },
    )

    mock_instance.wait_for_ready = create_autospec(mock_instance.wait_for_ready)

    mock_instance.delete = create_autospec(mock_instance.delete)

    mock_client = pypim.Client(channel=grpc.insecure_channel("localhost:12345"))

    mock_client.create_instance = create_autospec(
        mock_client.create_instance, return_value=mock_instance
    )

    mock_connect = create_autospec(pypim.connect, return_value=mock_client)

    mock_is_configured = create_autospec(pypim.is_configured, return_value=True)
    monkeypatch.setattr(pypim, "connect", mock_connect)
    monkeypatch.setattr(pypim, "is_configured", mock_is_configured)

    # Try to connect to Motor-CAD
    mc2 = MotorCAD()

    # Check that PIM workflow was followed when creating mc2
    assert mc2.connection.pim_instance is not None
    assert mock_is_configured.called
    assert mock_connect.called
    assert mock_instance.wait_for_ready.called


def test_using_url_to_connect():
    port = mc.connection._port
    url = "http://localhost:" + str(port)
    full_url = url + "/jsonrpc"
    mc2 = MotorCAD(url=url)

    assert mc2.connection._get_url() == full_url


def test__resolve_localhost():
    # Reset SERVER_IP since this will have been resolved on initial Motor-CAD connection
    pymotorcad.set_server_ip(pymotorcad.rpc_client_core.LOCALHOST_ADDRESS)

    full_url = (
        pymotorcad.rpc_client_core.LOCALHOST_ADDRESS + ":" + str(mc.connection._port) + "/jsonrpc"
    )

    assert mc.connection._get_url() == full_url

    ipv6_localhost = "http://[::1]" + ":" + str(mc.connection._port) + "/jsonrpc"
    ipv4_localhost = "http://127.0.0.1" + ":" + str(mc.connection._port) + "/jsonrpc"

    mc.connection._resolve_localhost()

    current_url = mc.connection._get_url()
    assert current_url in [ipv4_localhost, ipv6_localhost]
