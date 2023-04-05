"""Funtions for running MotorCAD in container"""
import subprocess
import ansys.motorcad.core as pymotorcad
from pathlib import PurePosixPath, PureWindowsPath, Path
import os


def _run_command_local(command_args):
    local_process = subprocess.run(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if local_process.stderr:
        error_message = local_process.stderr.decode("utf-8").strip()
        raise Exception(error_message)

    return local_process.stdout.decode("utf-8").strip()

def _create_container_path_from_windows_path(windows_path):

    new_path = os.path.splitdrive(windows_path)[1].strip("\\")

    new_path = os.path.join("home", "motorcaduser", ".wine", "drive_c", new_path)
    return PurePosixPath(PureWindowsPath(new_path))

class _MotorCADContainerLocal:
    def __init__(self, port):
        self.id = _run_command_local(
            [
                "docker",
                "run",
                "-it",
                "--init",
                "-d",
                "--rm",
                "--env",
                "ANSYSLMD_LICENSE_FILE=1055@host.docker.internal",
                "-p",
                "127.0.0.1:34000:34000/tcp",
                "motor-cad_container"
            ],
        )
        pass

    def __del__(self):
        _run_command_local(
            [
                "docker",
                "stop",
                self.id
            ]
        )
    pass


    def copy_files_to(self, local_windows_path):
        unix_path = str(_create_container_path_from_windows_path(local_windows_path))

        self.mkdir(local_windows_path)

        _run_command_local(
            [
                "docker",
                "cp",
                local_windows_path,
                self.id + ":" + unix_path
            ]
        )

    def get_files_from(self, local_windows_path):
        unix_path = str(_create_container_path_from_windows_path(local_windows_path))
        _run_command_local(
            [
                "docker",
                "cp",
                self.id + ":" + unix_path,
                local_windows_path
            ]
        )

    def get_path(self, local_windows_path):
        self.copy_files_to(local_windows_path)
        return local_windows_path

    def mkdir(self, local_windows_path):
        unix_path_parent = str(_create_container_path_from_windows_path(local_windows_path).parents[0])

        _run_command_local(
            [
                "docker",
                "exec",
                #"-it",
                self.id,
                "mkdir",
                "-p",
                unix_path_parent
            ]
        )
