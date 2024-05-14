from ansys.motorcad.core import MotorCADCompatibility
from ansys.motorcad.core.rpc_client_core import _MotorCADConnection

open_new_instance_flag = False


def set_instance_flag(*args, **kwargs):
    global open_new_instance_flag
    open_new_instance_flag = True


# Check MotorCADCompatibility object working as expected
def test_motorcadcompatibility(mc, monkeypatch):
    global open_new_instance_flag
    open_new_instance_flag = False

    monkeypatch.setattr(_MotorCADConnection, "_open_motor_cad_local", set_instance_flag)

    # Ensure Motor-CAD has opened successfully
    mc.connection._wait_for_response(30)

    mc2 = MotorCADCompatibility(port=mc.connection._port)

    # should have connected to open instance
    # Think this will actually just throw an exception if this fails
    assert open_new_instance_flag == False
    assert mc2.connection._port == mc.connection._port

    # Try simple method
    succ, var = mc2.GetVariable("Tooth_Width")
    assert succ == 0
    assert var is not None
    assert var != 0

    succ, var = mc2.GetVariable("not_a_var")
    assert succ != 0
