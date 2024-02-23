import os

from RPC_Test_Common import get_temp_files_dir_path
from setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_show_message():
    test_message = "test 1"
    mc.show_message(test_message)
    messages = mc.get_messages(1)
    assert (test_message in message for message in messages)


# Difficult to check these tests have actually worked
# These might raise an exception if they fail


def test_show_magnetic_context():
    mc.show_magnetic_context()


def test_show_mechanical_context():
    mc.show_mechanical_context()


def test_show_thermal_context():
    mc.show_thermal_context()


def test_set_motorlab_context():
    mc.set_motorlab_context()


def test_save_screen_to_file():
    file_path = get_temp_files_dir_path() + r"\screen.png"

    mc.save_screen_to_file("Radial", file_path)

    assert os.path.exists(file_path)


def test_display_screen():
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc.initialise_tab_names()
    mc.display_screen("Calculation")


def test_set_3d_component_visibility():
    mc.set_3d_component_visibility("stator", "winding", 0)


def test_set_visible():
    mc.set_visible(False)
    mc.set_visible(True)


def test_clear_messages():
    test_message = "test_message_to_clear"
    mc.show_message(test_message)
    assert (test_message in message for message in mc.get_messages(0))

    mc.clear_messages()
    assert mc.get_messages(0) == ""
