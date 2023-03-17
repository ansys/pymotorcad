import os
import os.path
import shutil

from RPC_Test_Common import get_dir_path, get_temp_files_dir_path
import ansys.motorcad.core as pymotorcad


USE_CONTAINER = True


def reset_to_default_file(mc):
    mc.load_from_file(get_dir_path() + r"\test_files\base_test_file.mot")

    # save to temp location to avoid editing base file
    mc.save_to_file(get_temp_files_dir_path() + r"\temp_test_file.mot")


def reset_temp_file_folder():
    dir_path = get_temp_files_dir_path()

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)

def launch_motorcad():
    mc = pymotorcad.MotorCAD()
    # Disable messages if opened with UI
    mc.set_variable("MessageDisplayState", 2)
    reset_to_default_file(mc)
    return(mc)


def launch_container():
    mc = pymotorcad.MotorCADContainer()
    reset_to_default_file(mc)
    return(mc)

def setup_test_env():
    """Set up test environment for whole unit of tests"""
    global mc

    reset_temp_file_folder()

    launch_new_motorcad = False

    try:
        mc
    except NameError:
        launch_new_motorcad = True
    else:
        if mc.connection._wait_for_response(1) is False:
            launch_new_motorcad = True

    if launch_new_motorcad is True:
        if USE_CONTAINER is True:
            mc = launch_container()
        else:
            mc = launch_new_motorcad





    # Disable messages if opened with UI
    mc.set_variable("MessageDisplayState", 2)

    return mc
