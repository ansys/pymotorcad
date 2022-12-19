from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_model_build_lab():
    # base test file includes built model
    assert mc.get_model_built_lab() is True

    mc.clear_model_build_lab()
    assert mc.get_model_built_lab() is False

    mc.build_model_lab()
    assert mc.get_model_built_lab() is True
