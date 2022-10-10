from RPC_Test_Common import almost_equal
from setup_test import reset_to_default_file, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_get_magnetic_graph_point():
    reset_to_default_file(mc)

    mc.DoMagneticCalculation()

    x, y = mc.GetMagneticGraphPoint("TorqueVW", 3)
    assert almost_equal(x, 180)
    assert almost_equal(y, 78.436)


def test_get_fea_graph_point():
    reset_to_default_file(mc)

    mc.DoMagneticCalculation()

    x, y = mc.GetMagneticGraphPoint("TorqueVW", 3)
    assert almost_equal(x, 180)
    assert almost_equal(y, 78.436)
