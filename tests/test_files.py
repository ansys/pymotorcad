from os import path, remove

from tests.RPC_Test_Common import get_dir_path
from tests.setup_test import setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_load_from_file():
    # This has some differences to the default file so can test it's loaded correctly
    file_path = get_dir_path() + r"\test_files\SaveLoadFiles.mot"
    mc.set_variable("slot_number", 21)
    mc.save_to_file(file_path)

    mc.set_variable("slot_number", 9)
    # make sure slot number has definitely changed
    value = mc.get_variable("slot_number")
    assert value == 9

    # go back to saved file
    mc.load_from_file(file_path)

    # make sure slot number has definitely changed
    value = mc.get_variable("slot_number")
    assert value == 21


def test_save_to_file():
    file_path = get_dir_path() + r"\test_files\SaveLoadFiles.mot"

    if path.exists(file_path):
        remove(file_path)

    assert path.exists(file_path) is False

    mc.save_to_file(file_path)

    assert path.exists(file_path) is True
