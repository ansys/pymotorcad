from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_show_message():
    test_message = "test 1"
    mc.show_message(test_message)
    message = mc.get_messages(1)
    assert test_message in message


def test_show_magnetic_context():
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc.show_magnetic_context()


def test_show_mechanical_context():
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc.show_mechanical_context()


def test_show_thermal_context():
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc.show_thermal_context()
