# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from time import sleep
from unittest.mock import create_autospec
import warnings

import ansys.platform.instancemanagement as pypim
import grpc
from psutil import pid_exists
import pytest

import ansys.motorcad.core as pym
import ansys.motorcad.core as pymotorcad
from ansys.motorcad.core import MotorCAD, MotorCADError, MotorCADWarning
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection


def test__find_free_motor_cad(mc):
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
def test_internal_connection(mc):
    port = mc.connection._port

    pymotorcad.rpc_client_core.set_default_instance(port)

    mc2 = MotorCAD()

    assert mc2.connection._port == port

    # reset default instance flag
    pymotorcad.rpc_client_core.DEFAULT_INSTANCE = -1


# Test opening Motor-CAD with port defined
def test_open_new_with_port():
    test_port = 36020

    try:
        mc2 = MotorCAD(open_new_instance=True, port=test_port)
    except:
        # This might not be able to connect if running tests in parallel.
        # Can't think of a way to test this on a server with multiple Motor-CADs without
        # race condition
        warnings.warn("unable to test opening with specific port. Port already in use")
        return

    try:
        assert mc2.connection._port == test_port
    except Exception as e:
        raise e
    finally:
        mc2.quit()


# Test connecting to known Motor-CAD instance
def test_connect_existing_with_port(mc):
    test_port = mc.connection._port

    mc2 = MotorCAD(open_new_instance=False, port=test_port)

    assert mc2.connection._port == test_port


def test_reusing_parallel_instances(mc, monkeypatch):
    # This should connect to mc test instance
    mc2 = MotorCAD(reuse_parallel_instances=True, port=mc.connection._port)
    try:
        original_port = mc2.connection._port

        # Force open another Motor-CAD to avoid hijacking existing instance
        mock_set_busy = create_autospec(_MotorCADConnection._set_busy, return_value=1)
        monkeypatch.setattr(_MotorCADConnection, "_set_busy", mock_set_busy)

        mc3 = MotorCAD(reuse_parallel_instances=True)
        try:
            # Ensure connected to different instances
            assert mc3.connection._port != original_port
        except Exception as e:
            raise e
        finally:
            # close second instance
            mc3.quit()
    except Exception as e:
        raise e
    finally:
        # close second instance
        mc2.set_free()

    # Check that original python object deleting doesn't close Motor-CAD
    del mc2

    assert mc.is_open()


def test_set_busy(mc):
    mc2 = MotorCAD(open_new_instance=False, port=mc.connection._port)
    mc2.set_free()
    mc2.connection._set_busy()

    mc3 = MotorCAD(open_new_instance=False, port=mc.connection._port)
    with pytest.raises(MotorCADError):
        mc3.connection._set_busy()


# test keeping an instance open
def test_keeping_instance_open(monkeypatch):
    # This should connect to mc test instance
    mc2 = MotorCAD(keep_instance_open=True)

    original_port = mc2.connection._port

    # finished with this instance
    del mc2

    # connect to the same instance (if it is still open)
    mc3 = pymotorcad.MotorCAD(open_new_instance=False, port=original_port)

    # check the instance is the same as before
    assert mc3.connection._port == original_port

    mc3.quit()

    del mc3

    # Check keep_instance_open ignored when building docs
    monkeypatch.setenv("PYMOTORCAD_DOCS_BUILD", "True")

    mc2 = MotorCAD(keep_instance_open=True)

    original_port = mc2.connection._port

    del mc2

    with pytest.raises(Exception):
        _ = pymotorcad.MotorCAD(open_new_instance=False, port=original_port)


# Check that Motor-CAD closes when Motor-CAD object is freed
def test_deleting_object():
    mc3 = MotorCAD(open_new_instance=True)

    proc_id = mc3.connection.pid

    del mc3

    # give process some time to fully close
    sleep(5)

    assert pid_exists(proc_id) is False


def test_rpc_communication_error(mc):
    # raise error by calling method with incorrect params
    with pytest.raises(Exception) as e_info:
        mc.connection.send_and_receive("GetVariable", ["var", "extra params", 1])
        assert "One or more parameter types were invalid" in str(e_info.value)


def test_ensure_version_later_than():
    mock_motorcad_connection = _MotorCADConnection.__new__(_MotorCADConnection)
    mock_motorcad_connection._connected = True

    save_DONT_CHECK_MOTORCAD_VERSION = pym.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION

    # Check global flag is working
    pym.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = True
    mock_motorcad_connection.program_version = "2023.1.2"
    mock_motorcad_connection.ensure_version_at_least("2023.2.0")

    pym.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = False

    # Tests will fail if ensure_version_at_least() raises MotorCADError
    mock_motorcad_connection.program_version = "2023.2.0"
    mock_motorcad_connection.ensure_version_at_least("2023.1.2")

    mock_motorcad_connection.program_version = "2023.2.0"
    mock_motorcad_connection.ensure_version_at_least("2022.1.2")

    mock_motorcad_connection.program_version = "2023.1.2"
    mock_motorcad_connection.ensure_version_at_least("2023.1.2")

    mock_motorcad_connection.program_version = "2023.1.2.0"
    mock_motorcad_connection.ensure_version_at_least("2023.1.2")

    mock_motorcad_connection.program_version = "2025.0.0.0"
    mock_motorcad_connection.ensure_version_at_least("2025")

    with pytest.raises(MotorCADError):
        mock_motorcad_connection.program_version = "2023.1.2"
        mock_motorcad_connection.ensure_version_at_least("2023.2.0")

    pym.rpc_client_core.DONT_CHECK_MOTORCAD_VERSION = save_DONT_CHECK_MOTORCAD_VERSION


def test_ansys_labs_connection(mc, monkeypatch):
    # Use existing Motor-CAD (mc.connection._port)
    mock_instance = pypim.Instance(
        definition_name="definitions/fake-motorcad",
        name="instances/fake-motorcad",
        ready=True,
        status_message="",
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


# Fake requests post class for testing functionality without involving Motor-CAD instance
class FakeRequestsPostWithWarning:
    def __init__(self, *args, **kwargs):
        pass

    def json(self):
        result = {"success": 0, "output": [], "errorMessage": "", "warningMessage": "test_warning"}
        response = {"jsonrpc": "2.0", "id": 347289, "result": result}
        return response


def test_warnings(mc, monkeypatch):
    # Create fake request result so we can test this before Motor-CAD 24R1
    # TODO - replace with actual call with warnings e.g. set_region
    monkeypatch.setattr("requests.post", FakeRequestsPostWithWarning)

    with pytest.warns(MotorCADWarning):
        # Call something which triggers send_and_receive
        mc.get_variable("n/a")


def test_using_url_to_connect(mc):
    port = mc.connection._port
    url = "http://localhost:" + str(port)
    full_url = url + "/jsonrpc"
    mc2 = MotorCAD(url=url)

    assert mc2.connection._get_url() == full_url


def test__resolve_localhost():
    mc2 = MotorCAD()
    try:
        # Reset SERVER_IP since this will have been resolved on initial Motor-CAD connection
        pymotorcad.set_server_ip(pymotorcad.rpc_client_core.LOCALHOST_ADDRESS)

        full_url = (
            pymotorcad.rpc_client_core.LOCALHOST_ADDRESS
            + ":"
            + str(mc2.connection._port)
            + "/jsonrpc"
        )

        assert mc2.connection._get_url() == full_url

        ipv6_localhost = "http://[::1]" + ":" + str(mc2.connection._port) + "/jsonrpc"
        ipv4_localhost = "http://127.0.0.1" + ":" + str(mc2.connection._port) + "/jsonrpc"

        mc2.connection._resolve_localhost()

        current_url = mc2.connection._get_url()
        assert current_url in [ipv4_localhost, ipv6_localhost]
    except Exception as e:
        raise e
    finally:
        mc2.quit()


def test_blackbox_licencing():
    mc2 = MotorCAD(use_blackbox_licence=True)
    # Not sure it's possible to assert that only a blackbox licence was consumed
    # Just check it works for now
    mc2.get_licence()
