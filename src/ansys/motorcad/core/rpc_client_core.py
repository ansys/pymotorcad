"""rpc_client_core."""

from os import environ, path
import re
import socket
import subprocess
import time

import psutil
import requests

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

DEFAULT_INSTANCE = -1

SERVER_IP = "http://localhost"

_METHOD_SUCCESS = 0

MOTORCAD_EXE_GLOBAL = ""

MOTORCAD_PROC_NAMES = ["MotorCAD", "Motor-CAD"]


def set_server_ip(ip):
    """IP of machine that MotorCAD is running on."""
    global SERVER_IP
    SERVER_IP = ip


def set_default_instance(port):
    """Use when running script from MotorCAD."""
    global DEFAULT_INSTANCE
    DEFAULT_INSTANCE = port


def set_motorcad_exe(exe_location):
    """Set location of Motor-CAD.exe to launch."""
    global MOTORCAD_EXE_GLOBAL
    MOTORCAD_EXE_GLOBAL = exe_location


class MotorCADError(Exception):
    """Error raised when an issue is raised by Motor-CAD exe."""

    pass


class MotorCADCore:
    """Each MotorCAD object has a Motor-CAD.exe instance attached to it."""

    def __init__(
        self,
        port,
        open_new_instance,
        enable_exceptions,
        enable_success_variable,
        reuse_parallel_instances=False,
        compatibility_mode=False,
    ):
        """Create MotorCAD object for communication.

        Parameters
        ----------
        port : int
            Port to use for communication
        open_new_instance: Boolean
            Open a new instance or try to connect to existing instance
        enable_exceptions : Boolean
            Show Motor-CAD communication errors as Python exceptions
        enable_success_variable: Boolean
                Motor-CAD methods return a success variable (first object in tuple)
        reuse_parallel_instances: Boolean, optional
            Reuse MotorCAD instances when running in parallel. Need to free instances after use.
        compatibility_mode: Boolean, optional
            Try to run an old script written for ActiveX
        Returns
        -------
        MotorCAD object
        """
        self._port = -1
        self._connected = False
        self._last_error_message = ""
        self._program_version = ""
        self._pid = -1

        self.enable_exceptions = enable_exceptions
        self.reuse_parallel_instances = reuse_parallel_instances

        self._open_new_instance = open_new_instance

        self.enable_success_variable = enable_success_variable

        self._compatibility_mode = compatibility_mode

        if DEFAULT_INSTANCE != -1:
            # Getting called from MotorCAD internal scripting so port is known
            port = DEFAULT_INSTANCE
            self._open_new_instance = False

        if self.reuse_parallel_instances is True:
            self._open_new_instance = False

        if self._open_new_instance is True:
            if port != -1:
                self._port = int(port)

            self.__OpenMotorCADLocal()

        else:  # (self._open_new_instance == False)
            if port != -1:
                self._port = int(port)

            else:  # port is not defined
                self.__FindFreeMotorCAD()

        self._pid = self.get_process_id()

        # Check for response
        if self.__WaitForResponse(2) is True:
            self._connected = True
            # Store Motor-CAD version number for any required backwards compatibility

            self._program_version = self._GetProgramVersion()

        else:
            raise MotorCADError(
                "Failed to connect to Motor-CAD instance: port="
                + str(self._port)
                + ", Url="
                + str(self._GetUrl())
            )

    def __del__(self):
        """Close Motor-CAD when MotorCAD object leaves memory."""
        if self._connected is True:
            if (
                (self.reuse_parallel_instances is False)
                and (self._open_new_instance is True)
                and (self._compatibility_mode is False)
            ):
                # Close Motor-CAD if not asked to keep open
                try:
                    self.Quit()
                except Exception:
                    # Don't raise exception at this point
                    # Motor-CAD might already have been closed by user
                    pass

    def _RaiseIfAllowed(self, aErrorMessage):
        if self.enable_exceptions is True:
            raise MotorCADError(aErrorMessage)

    def _GetUrl(self):
        """Get url for RPC communication."""
        url = SERVER_IP + ":" + str(self._port) + "/jsonrpc"
        return url

    def __OpenMotorCADLocal(self):
        self.__MotorExe = self.__FindMotorCADExe()

        if self.__MotorExe == "":
            self._RaiseIfAllowed(
                "Failed to find instance of Motor-CAD to open"
                + str(self._port)
                + ", Url="
                + str(self._GetUrl())
            )

        MotorProcess = subprocess.Popen([self.__MotorExe, "/PORT=" + str(self._port), "/SCRIPTING"])

        PID = MotorProcess.pid

        MotorUtil = psutil.Process(PID)

        self.__WaitForServerToStart(MotorUtil)

    def __FindMotorCADExe(self):
        if MOTORCAD_EXE_GLOBAL != "":
            MotorExe = MOTORCAD_EXE_GLOBAL
            return MotorExe

        strAltMethod = (
            "Try setting Motor-CAD exe manually before creating MotorCAD() "
            "object with MotorCAD_Methods.set_motorcad_exe(location)"
        )

        # Find Motor-CAD exe
        MotorBatchFilePath = environ.get("MOTORCAD_ACTIVEX")

        if MotorBatchFilePath is None:
            raise MotorCADError(
                "Failed to retrieve MOTORCAD_ACTIVEX environment variable. " + strAltMethod
            )

        try:
            MotorBatchFilePath = path.normpath(MotorBatchFilePath)
            # Get rid of quotations from environ.get
            MotorBatchFilePath = MotorBatchFilePath.replace('"', "")
        except Exception as e:
            raise MotorCADError("Failed to get file path. " + str(e) + strAltMethod)

        try:
            # Grab MotorCAD exe from activex batch file
            MotorBatchFile = open(MotorBatchFilePath, "r")

            MotorBatchFileLines = MotorBatchFile.readlines()

            for MotorBatchFileLine in MotorBatchFileLines:
                MotorExeList = re.split('"', MotorBatchFileLine)
                if "call" in MotorExeList[0]:
                    # Check we're on the right line
                    MotorExe = MotorExeList[1]
                    if path.isfile(MotorExe):
                        return MotorExe
                    else:
                        # Not a valid path
                        raise MotorCADError(
                            "File  does not exist: "
                            + MotorExe
                            + "\nTry updating batch file location in "
                            + "Defaults->Automation->Update to Current Version."
                            + "\nAlternative Method: "
                            + strAltMethod
                        )
            else:
                # Couldn't find line containing call
                raise

        except MotorCADError:
            # Raise our custom Error Message
            raise
        except Exception:
            raise MotorCADError("Error reading Motor-CAD batch file. " + strAltMethod)

    def __FindFreeMotorCAD(self):
        foundFreeInstance = False
        for proc in psutil.process_iter():
            procName = proc.name()
            if any(motor_proc_name in procName for motor_proc_name in MOTORCAD_PROC_NAMES):
                port = self.__GetPortFromProcess(proc)

                # If Motor-CAD has RPC server running
                if port != -1:
                    self._port = port
                    if self.reuse_parallel_instances is True:
                        try:
                            success = self.__SetBusy()
                            if success == 0:
                                foundFreeInstance = True
                                break
                        except Exception:
                            pass
                            # SetBusy failed because thread was already busy
                            # Means other python exe is trying to connect to this instance
                            # Happens when you try to launch multiple at same time
                    else:
                        # If we are not reusing instances then no need to check if busy
                        foundFreeInstance = True

        if foundFreeInstance is False:
            if (self.reuse_parallel_instances is True) or (self._compatibility_mode is True):
                self.__OpenMotorCADLocal()
            else:
                raise MotorCADError(
                    "Could not find a Motor-CAD instance to connect to."
                    + "\n Ensure that Motor-CAD RPC server is enabled"
                )

    def __WaitForServerToStart(self, aProcess):
        numberOfTries = 0
        timeout = 300  # in seconds
        # Don't poll this too much
        pause_time = 0.5

        while pause_time * numberOfTries < timeout:
            port = self.__GetPortFromProcess(aProcess)

            if port != -1:
                self._port = port

                # Check port has active RPC connection
                if self.__WaitForResponse(1) is True:
                    break

            time.sleep(pause_time)
            numberOfTries = numberOfTries + 1
        else:
            raise MotorCADError("Failed to find Motor-CAD port")

        self.__WaitForResponse(20)

    def __GetPortFromProcess(self, aProcess):
        connectionList = aProcess.connections()
        if len(connectionList) > 0:
            for connect in connectionList:
                if connect.family == socket.AddressFamily.AF_INET6:
                    port = connect.laddr.port
                    return port
        # Failed to get port from process
        return -1

    def _SendAndReceive(self, aMethod, aParams=[], aSuccessVar=None):
        errorMessage = ""

        payload = {
            "method": aMethod,
            "params": aParams,
            "jsonrpc": "2.0",
            "id": self._port,  # Can be any number not just linked to port
        }

        try:
            # Special case as there won't be a response
            if aMethod == "Quit":
                requests.post(self._GetUrl(), json=payload).json()
                return
            else:
                response = requests.post(self._GetUrl(), json=payload).json()

        except Exception as e:
            # This can occur when an assert fails in Motor-CAD debug
            success = -1
            self._RaiseIfAllowed("RPC Communication failed: " + str(e))

        else:  # No exceptions in RPC communication
            if "error" in response:
                errorString = "RPC Communication Error: " + response["error"]["message"]

                if "Invalid params" in errorString:
                    try:
                        # common error - give a better error message
                        newErrorString = errorString.split("hint")
                        # Get last part
                        newErrorString = newErrorString[-1]

                        newErrorString = (
                            aMethod
                            + ": One or more parameter types were invalid. HINT ["
                            + newErrorString
                        )
                        errorString = newErrorString
                    except Exception:
                        # use old error string if that failed
                        pass

                success = -99
                self._last_error_message = errorString

                self._RaiseIfAllowed(errorString)
                return

            else:
                success = response["result"]["success"]

            if aMethod == "CheckIfGeometryIsValid":
                # This doesn't have the normal success var
                successValue = 1
            else:
                successValue = _METHOD_SUCCESS

            if success != successValue:
                # This is an error caused by bad user code
                # Exception is enabled by default
                # Can get error message (get_last_error_message) instead
                if response["result"]["errorMessage"] != "":
                    errorMessage = response["result"]["errorMessage"]
                else:
                    errorMessage = (
                        "An error occurred in Motor-CAD"  # put some generic error message
                    )

                self._last_error_message = errorMessage

                self._RaiseIfAllowed(errorMessage)

            resultList = []

            if aSuccessVar is None:
                aSuccessVar = self.enable_success_variable

            if aSuccessVar is True:
                resultList.append(success)

            if len(response["result"]["output"]) > 0:
                if len(response["result"]["output"]) == 1:
                    resultList.append(response["result"]["output"][0])
                else:
                    resultList.extend(list(response["result"]["output"]))

            if len(resultList) > 1:
                return tuple(resultList)
            elif len(resultList) == 1:
                return resultList[0]

    def __WaitForResponse(self, aMaxRetries):
        method = "Handshake"

        delay = 1

        for _ in range(aMaxRetries):
            try:
                response = self._SendAndReceive(method, aSuccessVar=True)
                if response != "":
                    return True
            except Exception:
                time.sleep(delay)

        return False

    def _GetProgramVersion(self):
        method = "GetVariable"
        params = ["program_version"]
        return self._SendAndReceive(method, params, aSuccessVar=False)

    def get_process_id(self):
        method = "GetVariable"
        params = ["MotorCADprocessID"]
        return int(self._SendAndReceive(method, params, aSuccessVar=False))

    def __SetBusy(self):
        method = "SetBusy"
        return self._SendAndReceive(method)

    def set_free(self):
        method = "set_free"
        return self._SendAndReceive(method)

    def get_last_error_message(self):
        """Return the most recent error message.

        Returns
        -------
        ErrorMessage : str
            Most recent error message
        """
        return self._last_error_message
