from tests.setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_do_weight_calculation():
    # not sure how to test this?
    mc.do_weight_calculation()
