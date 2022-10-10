import os

import ansys.motorcad.core as pymotorcad
from RPC_Test_Common import get_dir_path


def reset_to_default_file(mc):
    mc.load_from_file(get_dir_path() + r"\test_files\base_test_file.mot")


def setup_test_env():
    """Set up test environment for whole unit of tests"""
    global mc

    try:
        mc
    except NameError:
        mc = pymotorcad.MotorCAD()

    if mc.is_open() is False:
        mc = pymotorcad.MotorCAD()

    # Disable messages if opened with UI
    mc.SetVariable("MessageDisplayState", 2)

    return mc
