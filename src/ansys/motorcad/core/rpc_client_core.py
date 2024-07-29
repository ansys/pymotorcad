"""Contains the JSON-RPC client for connecting to an instance of Motor-CAD."""
import os
from os import environ, path
import re
import socket
import subprocess
import time
import warnings

from packaging import version
import psutil
import requests

try:
    import ansys.platform.instancemanagement as pypim

    _HAS_PIM = True
except ModuleNotFoundError:
    _HAS_PIM = False


DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

DEFAULT_INSTANCE = -1

LOCALHOST_ADDRESS = "http://localhost"
TRY_RESOLVE_LOCALHOST = True
SERVER_IP = LOCALHOST_ADDRESS

_METHOD_SUCCESS = 0

MOTORCAD_EXE_GLOBAL = ""

MOTORCAD_PROC_NAMES = ["MotorCAD", "Motor-CAD"]

# Useful for debugging new functions when using debug Motor-CAD
DONT_CHECK_MOTORCAD_VERSION = False


def is_running_in_internal_scripting():
    """Whether the script is running internally in Motor-CAD."""
    return DEFAULT_INSTANCE != -1


def set_server_ip(ip):
    """IP address of the machine that Motor-CAD is running on."""
    global SERVER_IP
    SERVER_IP = ip


def set_default_instance(port):
    """Set the Motor-CAD instance to use as the default when running scripts from MotorCAD.

    For Motor-CAD internal use only. Do not use this function.
    """
    global DEFAULT_INSTANCE
    DEFAULT_INSTANCE = port


def set_motorcad_exe(exe_location):
    """Set the directory with the Motor-CAD executable file to launch."""
    global MOTORCAD_EXE_GLOBAL
    MOTORCAD_EXE_GLOBAL = exe_location


class MotorCADError(Exception):
    """Provides the errors to display when issues are raised by the Motor-CAD executable file."""

    pass


class MotorCADWarning(Warning):
    """Provides the warnings to display when issues are raised by the Motor-CAD executable file."""

    pass


def _get_port_from_motorcad_process(process):
    connection_list = process.connections()
    if len(connection_list) > 0:
        for connect in connection_list:
            if connect.family == socket.AddressFamily.AF_INET6:
                port = connect.laddr.port
                return port
    # Failed to get port from process
    return -1


def _find_motor_cad_exe():
    if MOTORCAD_EXE_GLOBAL != "":
        motor_exe = MOTORCAD_EXE_GLOBAL
        return motor_exe

    str_alt_method = (
        "Try setting the Motor-CAD executable file manually before creating "
        "the MotorCAD() object with the MotorCAD_Methods.set_motorcad_exe(location) "
        "method. "
    )

    # Find Motor-CAD exe
    motor_batch_file_path = environ.get("MOTORCAD_ACTIVEX")

    if motor_batch_file_path is None:
        raise MotorCADError(
            "Failed to retrieve MOTORCAD_ACTIVEX environment variable. " + str_alt_method
        )

    try:
        motor_batch_file_path = path.normpath(motor_batch_file_path)
        # Get rid of quotations from environ.get
        motor_batch_file_path = motor_batch_file_path.replace('"', "")
    except Exception as e:
        raise MotorCADError("Failed to get file path. " + str(e) + str_alt_method)

    try:
        # Grab MotorCAD exe from activex batch file
        motor_batch_file = open(motor_batch_file_path, "r")

        motor_batch_file_lines = motor_batch_file.readlines()

        for MotorBatchFileLine in motor_batch_file_lines:
            motor_exe_list = re.split('"', MotorBatchFileLine)
            if "call" in motor_exe_list[0]:
                # Check we're on the right line
                motor_exe = motor_exe_list[1]
                if path.isfile(motor_exe):
                    return motor_exe
                else:
                    # Not a valid path
                    raise MotorCADError(
                        "File does not exist: "
                        + motor_exe
                        + "\nTry updating batch file location in "
                        + "Defaults->Automation->Update to Current Version."
                        + "\nAlternative Method: "
                        + str_alt_method
                    )
        else:
            # Couldn't find line containing call
            raise

    except MotorCADError:
        # Raise our custom Error Message
        raise
    except Exception:
        raise MotorCADError("Error reading Motor-CAD batch file. " + str_alt_method)


class _MotorCADConnection:
    """Provides the Motor-CAD instance attached to each MotorCAD object."""

    def __init__(
        self,
        port,
        open_new_instance,
        enable_exceptions,
        enable_success_variable,
        reuse_parallel_instances,
        keep_instance_open,
        url="",
        timeout=2,
        compatibility_mode=False,
    ):
        """Create a MotorCAD object for communication.

        Parameters
        ----------
        port : int
            Port to use for communication.
        open_new_instance: Boolean
            Open a new Motor-CAD instance or try to connect to an existing instance.
        enable_exceptions : Boolean
            Whether to show Motor-CAD communication errors as Python exceptions.
        enable_success_variable: Boolean
            Whether Motor-CAD methods are to return a success variable (first object in tuple).
        reuse_parallel_instances: Boolean
            Whether to reuse MotorCAD instances when running in parallel. You must free
            instances after use.
        keep_instance_open : Boolean, default: False
            Whether to keep the Motor-CAD instance open after the instance becomes free.
        compatibility_mode: Boolean, default: False
            Whether to try to run an old script written for ActiveX.
        url: string, default = ""
            Full url for Motor-CAD connection. Assumes we are connecting to existing instance.

        Returns
        -------
        MotorCAD object.
        """
        self._port = -1
        self._connected = False
        self._last_error_message = ""
        self.program_version = ""
        self.pid = -1

        self.enable_exceptions = enable_exceptions
        self.reuse_parallel_instances = reuse_parallel_instances

        self.keep_instance_open = keep_instance_open

        self._open_new_instance = open_new_instance

        self.enable_success_variable = enable_success_variable

        self._compatibility_mode = compatibility_mode

        self.pim_instance = None

        self._url = url
        self._timeout = timeout

        if DEFAULT_INSTANCE != -1:
            # Getting called from MotorCAD internal scripting so port is known
            port = DEFAULT_INSTANCE
            self._open_new_instance = False

        if self.reuse_parallel_instances is True:
            self._open_new_instance = False

        if self._url != "":
            # Don't want to start a Motor-CAD instance
            # Already have full url in _get_url()
            # Also don't want to exit Motor-CAD upon script ending
            self._open_new_instance = False
        elif _HAS_PIM and pypim.is_configured():
            # Start with PyPIM if the environment is configured for it
            self._launch_motorcad_remote()
        else:
            # run/connect to motor-cad on local machine
            self._launch_motorcad_local(port)

        if (SERVER_IP == LOCALHOST_ADDRESS) and TRY_RESOLVE_LOCALHOST:
            # Try to resolve localhost at same time as checking for connection
            # to decrease connection _start_times
            self._connected = self._try_resolve_wait_for_response(self._timeout)
        else:
            # Check for response
            self._connected = self._wait_for_response(self._timeout)

        if self._connected:
            # Store Motor-CAD version number for any required backwards compatibility
            self.program_version = self._get_program_version()

            self.pid = self.get_process_id()
        else:
            raise MotorCADError(
                "Failed to connect to Motor-CAD instance: port="
                + str(self._port)
                + ", Url="
                + str(self._get_url())
            )

    def _resolve_localhost(self):
        """Try to resolve localhost so that we don't have to do this for every api method.

        Replace the address http://localhost with the corresponding IP address.
        On some configurations this was increasing each api method time to 1/2 seconds.
        """
        global SERVER_IP

        ipv6_localhost = "http://[::1]"
        ipv4_localhost = "http://127.0.0.1"

        if self._check_address_for_response(ipv6_localhost):
            SERVER_IP = ipv6_localhost
            return True
        elif self._check_address_for_response(ipv4_localhost):
            SERVER_IP = ipv4_localhost
            return True
        else:
            return self._check_address_for_response(LOCALHOST_ADDRESS)

    def _check_address_for_response(self, address):
        """Try to communicate with Motor-CAD with specific url, returns True if response received.

        Uses handshake method. Used to resolve localhost.
        """
        # This function is only called from _resolve_localhost so SERVER_IP will be localhost
        # address
        # If connecting to remote machine then SERVER_IP is deprecated - should use url class
        # parameter instead
        global SERVER_IP

        save_SERVER_IP = SERVER_IP

        try:
            SERVER_IP = address
            address_responds = self._wait_for_response(1)
        finally:
            # Reset global SERVER_IP to original
            # Calling function can set SERVER_IP depending on address_responds return value
            SERVER_IP = save_SERVER_IP

        return address_responds

    def __del__(self):
        """Close Motor-CAD when MotorCAD object leaves memory."""
        if self._close_motorcad_on_exit():
            try:
                self._quit()
            except Exception:
                # Don't raise exception at this point
                # Motor-CAD might already have been closed by user
                pass

    def _close_motorcad_on_exit(self):
        """Check whether to close Motor-CAD when MotorCAD object __del__ is called."""
        if (
            (self.reuse_parallel_instances is False)
            and (self._open_new_instance is True)
            and (self._compatibility_mode is False)
        ):
            # Local Motor-CAD has been launched by Python
            if self.keep_instance_open:
                if "PYMOTORCAD_DOCS_BUILD" in os.environ:
                    # Building PyMotorCAD docs so don't keep open
                    return True
                else:
                    return False
            else:
                return True
                # keep the instance open if specified
        elif _HAS_PIM and pypim.is_configured():
            # Always try to close Ansys Lab instance
            return True
        else:
            return False

    # Close Motor-CAD if not asked to keep open
    def _launch_motorcad_local(self, port):
        """Launch local Motor-CAD instance."""
        if self._open_new_instance is True:
            if port != -1:
                self._port = int(port)

            self._open_motor_cad_local()

        else:  # (self._open_new_instance == False)
            if port != -1:
                self._port = int(port)

            else:  # port is not defined
                self._find_free_motor_cad()

    def _launch_motorcad_remote(self):
        """Launch Motor-CAD in Ansys Lab."""
        pim = pypim.connect()

        self.pim_instance = pim.create_instance(product_name="motorcad")
        self.pim_instance.wait_for_ready()
        # get ip and port for motorcad
        address = self.pim_instance.services["http"].uri

        ip = address.split(":")[0] + ":" + address.split(":")[1]
        set_server_ip(ip)

        self._port = address.split(":")[2]

        # Wait for Motor-CAD RPC server to start on remote machine - this might take a few minutes
        if self._wait_for_response(300) is False:
            raise MotorCADError("Failed to connect to Motor-CAD instance on: " + address)

    def _raise_if_allowed(self, error_message):
        if self.enable_exceptions is True:
            raise MotorCADError(error_message)

    def _get_url(self):
        """Get url for RPC communication."""
        if self._url != "":
            # Already have full url from launch params
            return self._url + "/jsonrpc"
        else:
            # Create url from server ip and port
            return SERVER_IP + ":" + str(self._port) + "/jsonrpc"

    def _open_motor_cad_local(self):
        self.__MotorExe = _find_motor_cad_exe()

        if self.__MotorExe == "":
            self._raise_if_allowed(
                "Failed to find instance of Motor-CAD to open."
                + str(self._port)
                + ", Url="
                + str(self._get_url())
            )

        motor_process = subprocess.Popen(
            [self.__MotorExe, "/PORT=" + str(self._port), "/SCRIPTING"]
        )

        pid = motor_process.pid

        motor_util = psutil.Process(pid)

        self._wait_for_server_to_start_local(motor_util)

    def _find_free_motor_cad(self):
        found_free_instance = False
        for proc in psutil.process_iter():
            proc_name = proc.name()
            if any(motor_proc_name in proc_name for motor_proc_name in MOTORCAD_PROC_NAMES):
                port = _get_port_from_motorcad_process(proc)

                # If Motor-CAD has RPC server running
                if port != -1:
                    self._port = port
                    if self.reuse_parallel_instances is True:
                        try:
                            success = self._set_busy()
                            if success == 0:
                                found_free_instance = True
                                break
                        except Exception:
                            pass
                            # SetBusy failed because thread was already busy
                            # Means other python exe is trying to connect to this instance
                            # Happens when you try to launch multiple at same time
                    else:
                        # If we are not reusing instances then no need to check if busy
                        found_free_instance = True

        if found_free_instance is False:
            if (self.reuse_parallel_instances is True) or (self._compatibility_mode is True):
                # reset port to default otherwise it will try to use port set in the above for loop
                self._port = -1
                self._open_motor_cad_local()
            else:
                raise MotorCADError(
                    "Could not find a Motor-CAD instance to connect to."
                    + "\n Ensure that Motor-CAD RPC server is enabled."
                )

    def ensure_version_at_least(self, required_version):
        """Ensure if the Motor-CAD version is later or equal to required version."""
        if not self.check_version_at_least(required_version):
            raise MotorCADError(
                "This function requires Motor-CAD version: " + required_version + " or later"
            )

    def check_version_at_least(self, required_version):
        """Check if the Motor-CAD version is later or equal to required version."""
        if DONT_CHECK_MOTORCAD_VERSION:
            return True
        else:
            return version.parse(self.program_version) >= version.parse(required_version)

    def _wait_for_server_to_start_local(self, process):
        number_of_tries = 0
        timeout = 300  # in seconds
        # Don't poll this too much
        pause_time = 0.5

        while pause_time * number_of_tries < timeout:
            port = _get_port_from_motorcad_process(process)

            if port != -1:
                self._port = port

                # Check port has active RPC connection
                if self._wait_for_response(1) is True:
                    break

            time.sleep(pause_time)
            number_of_tries = number_of_tries + 1
        else:
            raise MotorCADError("Failed to find Motor-CAD port.")

        self._wait_for_response(20)

    def send_and_receive(self, method, params=None, success_var=None):
        if params is None:
            params = []

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": self._port,  # Can be any number not just linked to port
        }

        try:
            # Special case as there won't be a response
            if method == "Quit":
                requests.post(self._get_url(), json=payload).json()
                return
            else:
                response = requests.post(self._get_url(), json=payload).json()

        except Exception as e:
            # This can occur when an assert fails in Motor-CAD debug
            success = -1
            self._raise_if_allowed("RPC Communication failed: " + str(e))

        else:  # No exceptions in RPC communication
            if "error" in response:
                error_string = "RPC Communication Error: " + response["error"]["message"]

                if "Invalid params" in error_string:
                    try:
                        # common error - give a better error message
                        new_error_string = error_string.split("hint")
                        # Get last part
                        new_error_string = new_error_string[-1]

                        new_error_string = (
                            method
                            + ": One or more parameter types were invalid. HINT ["
                            + new_error_string
                        )
                        error_string = new_error_string
                    except Exception:
                        # use old error string if that failed
                        pass

                success = -99
                self._last_error_message = error_string

                self._raise_if_allowed(error_string)
                return

            else:
                success = response["result"]["success"]

            if method == "CheckIfGeometryIsValid":
                # This doesn't have the normal success var
                success_value = 1
            else:
                success_value = _METHOD_SUCCESS

            if success != success_value:
                # This is an error caused by bad user code
                # Exception is enabled by default
                # Can get error message (get_last_error_message) instead
                if response["result"]["errorMessage"] != "":
                    error_message = response["result"]["errorMessage"]
                else:
                    error_message = (
                        "An error occurred in Motor-CAD."  # put some generic error message
                    )

                self._last_error_message = error_message

                self._raise_if_allowed(error_message)

            # Warning message only exists in response from Motor-CAD version >= 24R1
            if "warningMessage" in response["result"]:
                warning_message = response["result"]["warningMessage"]
                if warning_message != "":
                    # Code in Motor-CAD wants to raise a warning in Python
                    warnings.warn(response["result"]["warningMessage"], MotorCADWarning)

            result_list = []

            if success_var is None:
                success_var = self.enable_success_variable

            if success_var is True:
                result_list.append(success)

            if len(response["result"]["output"]) > 0:
                if len(response["result"]["output"]) == 1:
                    result_list.append(response["result"]["output"][0])
                else:
                    result_list.extend(list(response["result"]["output"]))

            if len(result_list) > 1:
                return tuple(result_list)
            elif len(result_list) == 1:
                return result_list[0]

    def _wait_for_response(self, max_retries):
        method = "Handshake"

        delay = 1

        for _ in range(max_retries):
            try:
                response = self.send_and_receive(method, success_var=True)
                if response != "":
                    return True
            except Exception:
                time.sleep(delay)

        return False

    def _try_resolve_wait_for_response(self, max_retries):
        delay = 1

        for _ in range(max_retries):
            try:
                response = self._resolve_localhost()
                if response:
                    return True
            except Exception:
                time.sleep(delay)

        return False

    def _get_program_version(self):
        method = "GetVariable"
        params = ["program_version"]
        return self.send_and_receive(method, params, success_var=False)

    def get_process_id(self):
        method = "GetVariable"
        params = ["MotorCADprocessID"]
        return int(self.send_and_receive(method, params, success_var=False))

    def _set_busy(self):
        method = "SetBusy"
        return self.send_and_receive(method, success_var=True)

    def _set_free(self):
        method = "SetFree"
        return self.send_and_receive(method)

    def get_last_error_message(self):
        """Get the most recent error message.

        Returns
        -------
        error_message : str
            Most recent error message.
        """
        return self._last_error_message

    def _quit(self):
        """Quit MotorCAD."""
        if self.pim_instance is not None:
            self.pim_instance.delete()
        else:
            # local machine
            method = "Quit"
            return self.send_and_receive(method)
