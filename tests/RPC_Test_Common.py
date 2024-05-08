import os
import shutil


def get_dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_test_files_dir_path():
    return get_dir_path() + r"\test_files"


def get_base_test_file_path():
    return get_test_files_dir_path() + r"\base_test_file.mot"


def get_temp_files_dir_path():
    return get_test_files_dir_path() + r"\temp_files"


def almost_equal(a, b, decimal_places=1):
    # Rough check
    return round(a - b, decimal_places) == 0


def almost_equal_fixed(a, b, allowed_difference=0):
    return abs(a - b) < +allowed_difference


def reset_to_default_file(mc):
    mc.load_from_file(get_base_test_file_path())

    # save to temp location to avoid editing base file
    mc.save_to_file(get_temp_files_dir_path() + r"\temp_test_file.mot")


def reset_temp_file_folder():
    dir_path = get_temp_files_dir_path()

    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

    os.mkdir(dir_path)
