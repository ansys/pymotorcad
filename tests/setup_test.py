import os
import os.path
import shutil

from RPC_Test_Common import get_dir_path, get_temp_files_dir_path
import ansys.motorcad.core as pymotorcad


def reset_to_default_file(mc):
    mc.load_from_file(get_dir_path() + r"\test_files\base_test_file.mot")

    # save to temp location to avoid editing base file
    mc.save_to_file(get_temp_files_dir_path() + r"\temp_test_file.mot")


def reset_temp_file_folder():
    dir_path = get_temp_files_dir_path()

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)


def setup_test_env():
    """Set up test environment for whole unit of tests"""
    global mc

    reset_temp_file_folder()

    try:
        mc
    except NameError:
        mc = pymotorcad.MotorCAD()
        reset_to_default_file(mc)

    if mc.is_open() is False:
        mc = pymotorcad.MotorCAD()
        reset_to_default_file(mc)

    # Disable messages if opened with UI
    mc.set_variable("MessageDisplayState", 2)

    return mc
