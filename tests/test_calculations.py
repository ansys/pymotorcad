from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_do_weight_calculation():
    # not sure how to test this?
    mc.DoWeightCalculation()


def test_do_steady_state_analysis():
    assert False
