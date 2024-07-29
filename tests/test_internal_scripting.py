import os

from RPC_Test_Common import get_dir_path, get_temp_files_dir_path


def test_load_run_script(mc):
    save_tooth_width = mc.get_variable("tooth_width")

    # script in test file changes tooth width
    mc.run_script()
    assert mc.get_variable("tooth_width") == 6.5

    mc.load_script(get_dir_path() + r"\test_files\internal_script.py")
    mc.run_script()
    assert mc.get_variable("tooth_width") == 7.5

    mc.set_variable("tooth_width", save_tooth_width)


def test_save_script(mc):
    file_path = get_temp_files_dir_path() + r"\test_internal_script.py"

    mc.save_script(file_path)
    assert os.path.exists(file_path)
