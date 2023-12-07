from os import path


def get_dir_path():
    return path.dirname(path.realpath(__file__))


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
