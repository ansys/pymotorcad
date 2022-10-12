from os import path


def get_dir_path():
    return path.dirname(path.realpath(__file__))


def almost_equal(a, b, decimal_places=1):
    # Rough check
    return round(a - b, decimal_places) == 0


def almost_equal_fixed(a, b, allowed_difference=0):
    return abs(a - b) < +allowed_difference
