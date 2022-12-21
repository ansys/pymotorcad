import os

from setup_test import get_dir_path, get_temp_files_dir_path, setup_test_env

# Get Motor-CAD exe
mc = setup_test_env()


def test_load_run_script():
    # script in test file changes tooth width
    mc.run_script()
    assert mc.get_variable("tooth_width") == 6.5

    mc.load_script(get_dir_path() + r"\test_files\internal_script.py")
    mc.run_script()
    assert mc.get_variable("tooth_width") == 7.5


def test_save_script():
    file_path = get_temp_files_dir_path() + r"\test_internal_script.py"

    mc.save_script(file_path)
    assert os.path.exists(file_path)
