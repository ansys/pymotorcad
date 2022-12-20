import os

from setup_test import get_temp_files_dir_path, setup_test_env

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


def test_set_motorlab_context():
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
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
    # Difficult to check this has actually worked
    # These might raise an exception if they fail
    mc.set_3d_component_visibility("stator", "winding", 0)
