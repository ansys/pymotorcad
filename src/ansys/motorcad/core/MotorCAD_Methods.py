"""Module containing MotorCAD class for connecting to Motor-CAD exe."""

from os import environ, path
import re
import socket
import subprocess
import time

from packaging import version
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


class MotorCADBase:
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
                + str(self.__GetUrl())
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

    def __RaiseIfAllowed(self, aErrorMessage):
        if self.enable_exceptions is True:
            raise MotorCADError(aErrorMessage)

    def __GetUrl(self):
        """Get url for RPC communication."""
        url = SERVER_IP + ":" + str(self._port) + "/jsonrpc"
        return url

    def __OpenMotorCADLocal(self):
        self.__MotorExe = self.__FindMotorCADExe()

        if self.__MotorExe == "":
            self.__RaiseIfAllowed(
                "Failed to find instance of Motor-CAD to open"
                + str(self._port)
                + ", Url="
                + str(self.__GetUrl())
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

    def is_open(self):
        """Check if Motor-CAD exe is still running.

        Returns
        -------
        boolean
            True if Motor-CAD exe is running.
        """
        if self._pid != -1:
            return psutil.pid_exists(self._pid)
        else:
            raise MotorCADError("Motor-CAD process not created")

    def __GetPortFromProcess(self, aProcess):
        connectionList = aProcess.connections()
        if len(connectionList) > 0:
            for connect in connectionList:
                if connect.family == socket.AddressFamily.AF_INET6:
                    port = connect.laddr.port
                    return port
        # Failed to get port from process
        return -1

    def __SendAndReceive(self, aMethod, aParams=[], aSuccessVar=None):
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
                requests.post(self.__GetUrl(), json=payload).json()
                return
            else:
                response = requests.post(self.__GetUrl(), json=payload).json()

        except Exception as e:
            # This can occur when an assert fails in Motor-CAD debug
            success = -1
            self.__RaiseIfAllowed("RPC Communication failed: " + str(e))

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

                self.__RaiseIfAllowed(errorString)
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

                self.__RaiseIfAllowed(errorMessage)

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
                response = self.__SendAndReceive(method, aSuccessVar=True)
                if response != "":
                    return True
            except Exception:
                time.sleep(delay)

        return False

    def _GetProgramVersion(self):
        method = "GetVariable"
        params = ["program_version"]
        return self.__SendAndReceive(method, params, aSuccessVar=False)

    def get_process_id(self):
        method = "GetVariable"
        params = ["MotorCADprocessID"]
        return int(self.__SendAndReceive(method, params, aSuccessVar=False))

    def __SetBusy(self):
        method = "SetBusy"
        return self.__SendAndReceive(method)

    def set_free(self):
        method = "set_free"
        return self.__SendAndReceive(method)

    def get_last_error_message(self):
        """Return the most recent error message.

        Returns
        -------
        ErrorMessage : str
            Most recent error message
        """
        return self._last_error_message

    # Motor-CAD functions start here

    # ------------------------------------ Variables ------------------------------------

    def GetArrayVariable_2d(self, array_name, array_index1, array_index2):
        method = "GetArrayVariable_2d"
        params = [array_name, array_index1, array_index2]
        return self.__SendAndReceive(method, params)

    def SetArrayVariable_2d(self, array_name, array_index1, array_index2, new_value):
        method = "SetArrayVariable_2d"
        params = [array_name, array_index1, array_index2, {"variant": new_value}]
        return self.__SendAndReceive(method, params)

    def RestoreCompatibilitySettings(self):
        method = "RestoreCompatibilitySettings"
        return self.__SendAndReceive(method)

    def GetVariable(self, variable_name):
        """Get a MotorCAD variable.

        Parameters
        ----------
        VariableName : str
            Name of variable

        Returns
        -------
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetVariable"
        params = [variable_name]
        return self.__SendAndReceive(method, params)

    def GetArrayVariable(self, array_name, array_index):
        """Get a MotorCAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
        array_index : int
            Position variable in array

        Returns
        -------
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetArrayVariable"
        params = [array_name, array_index]
        return self.__SendAndReceive(method, params)

    def SetVariable(self, variable_name, variable_value):
        """Set a MotorCAD variable.

        Parameters
        ----------
        variable_name : str
            Name of variable
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetVariable"
        params = [variable_name, {"variant": variable_value}]
        return self.__SendAndReceive(method, params)

    def SetArrayVariable(self, array_name, array_index, variable_value):
        """Set a MotorCAD array variable.

        Parameters
        ----------
        array_name : str
            Name of array
        array_index : int
            Position in array
        variable_value : int|float|str|bool
            Sets the variable to this value
        """
        method = "SetArrayVariable"
        params = [array_name, array_index, {"variant": variable_value}]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ UI ------------------------------------

    def IsStopRequested(self):
        method = "IsStopRequested"
        return self.__SendAndReceive(method)

    def DisableErrorMessages(self, active):
        method = "DisableErrorMessages"
        params = [active]
        return self.__SendAndReceive(method, params)

    def GetMessages(self, num_messages):
        """Return a list of the last N messages from the message history.

        Parameters
        ----------
        num_messages : int
            The number of recent messages to be returned.
            If numMessages=0 all messages in history will be returned.

        Returns
        -------
        messages : str
            List of messages (most recent first, separated by ;)
        """
        method = "GetMessages"
        params = [num_messages]
        return self.__SendAndReceive(method, params)

    def UpdateInterface(self):
        method = "UpdateInterface"
        return self.__SendAndReceive(method)

    def InitialiseTabNames(self):
        """Initialise the available tabs in the Motor-CAD UI.

        Call before using SaveMotorCADScreenToFile or DisplayScreen. Motor-CAD UI must be visible.
        """
        method = "InitialiseTabNames"
        return self.__SendAndReceive(method)

    def SaveMotorCADScreenToFile(self, screen_name, file_name):
        """Save the whole Motor-CAD screen of the specified tab as a image file, (bmp, jpg, png).

        InitialiseTabNames must be called before using this function. Motor-CAD UI must be visible.

        Parameters
        ----------
        screen_name : str
            Path of the screen to save,
            must be in the format of "tabName;tabName;tabName" e.g. "Geometry;Axial"
        file_name : str
            File where the image is to be saved (full path)
        """
        method = "SaveMotorCADScreenToFile"
        params = [screen_name, file_name]
        return self.__SendAndReceive(method, params)

    def GetLicence(self):
        method = "GetLicence"
        return self.__SendAndReceive(method)

    def SetVisible(self, visible):
        """Set the visibility of the Motor-CAD user interface.

        Parameters
        ----------
        visible : bool
            When true, the Motor-CAD user interface is shown. When false, the UI is hidden.
        """
        if version.parse(self._program_version) < version.parse("15.2.0"):
            # Backwards compatibility for v15.1.x
            method = "Set_Visible"
        else:  # v15.2 onwards
            method = "SetVisible"

        params = [visible]
        return self.__SendAndReceive(method, params)

    def AvoidImmediateUpdate(self, avoid_update):
        method = "AvoidImmediateUpdate"
        params = [{"variant": avoid_update}]
        return self.__SendAndReceive(method, params)

    def ClearMessageLog(self):
        method = "ClearMessageLog"
        return self.__SendAndReceive(method)

    def ShowMessage(self, message):
        """Display a message in the MotorCAD message window.

        Parameters
        ----------
        message : str
            Message to display
        """
        method = "ShowMessage"
        params = [message]
        return self.__SendAndReceive(method, params)

    def showmessage(self, message):
        """See ShowMessage - for backwards compatibility."""
        return self.ShowMessage(message)

    def ShowMagneticContext(self):
        """Show magnetic context in Motor-CAD."""
        method = "ShowMagneticContext"
        return self.__SendAndReceive(method)

    def ShowMechanicalContext(self):
        """Show mechanical context in Motor-CAD."""
        method = "ShowMechanicalContext"
        return self.__SendAndReceive(method)

    def ShowThermalContext(self):
        """Show thermal context in Motor-CAD."""
        method = "ShowThermalContext"
        return self.__SendAndReceive(method)

    def DisplayScreen(self, screen_name):
        """Show a screen within Motor-CAD.

        Parameters
        ----------
        screen_name : str
            Screen to display
        """
        method = "DisplayScreen"
        params = [screen_name]
        return self.__SendAndReceive(method, params)

    def Quit(self):
        """Quit MotorCAD."""
        method = "Quit"
        return self.__SendAndReceive(method)

    def SaveScreenToFile(self, screen_name, file_name):
        """Save a screen as an image.

        Parameters
        ----------
        screen_name : str
            Screen to save
        file_name : str
            File to save image full path
        """
        method = "SaveScreenToFile"
        params = [screen_name, file_name]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Files ------------------------------------

    def LoadDutyCycle(self, file_name):
        method = "LoadDutyCycle"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def SaveDutyCycle(self, file_name):
        method = "SaveDutyCycle"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def ExportMatrices(self, file_name):
        method = "ExportMatrices"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def LoadCustomDriveCycle(self, file_name):
        method = "LoadCustomDriveCycle"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def LoadFEAResult(self, file_name, solution_number):
        method = "LoadFEAResult"
        params = [file_name, solution_number]
        return self.__SendAndReceive(method, params)

    def ExportToAnsysElectronicsDesktop(self, file_name):
        method = "ExportToAnsysElectronicsDesktop"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def ExportResults(self, solution_type, file_name):
        method = "ExportResults"
        params = [solution_type, file_name]
        return self.__SendAndReceive(method, params)

    def LoadDXFFile(self, file_name):
        method = "LoadDXFFile"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def CreateReport(self, file_path, template_file_path):
        method = "CreateReport"
        params = [file_path, template_file_path]
        return self.__SendAndReceive(method, params)

    def LoadReportStructure(self, file_path):
        method = "LoadReportStructure"
        params = [file_path]
        return self.__SendAndReceive(method, params)

    def ExportForceAnimation(self, animation, file_name):
        method = "ExportForceAnimation"
        params = [animation, file_name]
        return self.__SendAndReceive(method, params)

    def LoadReportTree(self):
        method = "LoadReportTree"
        return self.__SendAndReceive(method)

    def LoadTemplate(self, template_name):
        method = "LoadTemplate"
        params = [template_name]
        return self.__SendAndReceive(method, params)

    def SaveTemplate(
        self,
        template_file_name,
        name,
        sector,
        machine_type,
        application,
        winding_type,
        max_speed,
        power,
        cooling,
        drive_type,
        notes,
    ):
        method = "SaveTemplate"
        params = [
            template_file_name,
            name,
            sector,
            machine_type,
            application,
            winding_type,
            max_speed,
            power,
            cooling,
            drive_type,
            notes,
        ]
        return self.__SendAndReceive(method, params)

    def LoadWindingPattern(self, file_name):
        method = "LoadWindingPattern"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def SaveWindingPattern(self, file_name):
        method = "SaveWindingPattern"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def ExportMultiForceData(self, file_name):
        method = "ExportMultiForceData"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def GeometryExport(self):
        method = "GeometryExport"
        return self.__SendAndReceive(method)

    def ExportToAnsysDiscovery(self, file_name):
        method = "ExportToAnsysDiscovery"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def ExportNVHResultsData(self, file_name):
        method = "ExportNVHResultsData"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def LoadFromFile(self, mot_file):
        """Load a .mot file into the MotorCAD instance.

        Parameters
        ----------
        mot_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadFromFile"
        params = [mot_file]
        return self.__SendAndReceive(method, params)

    def SaveToFile(self, mot_file):
        """Save the current .mot file.

        Parameters
        ----------
        mot_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "SaveToFile"
        params = [mot_file]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Internal Scripting ------------------------------------

    def SaveScript(self, file_name):
        method = "SaveScript"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def LoadScript(self, script_file):
        """Load a script file into Motor-CAD internal scripting.

        Parameters
        ----------
        script_file : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.
        """
        method = "LoadScript"
        params = [script_file]
        return self.__SendAndReceive(method, params)

    def RunScript(self):
        """Run script file in Motor-CAD internal scripting."""
        method = "RunScript"
        return self.__SendAndReceive(method)

    # ------------------------------------ Calculations ------------------------------------

    def ClearDutyCycle(self):
        method = "ClearDutyCycle"
        return self.__SendAndReceive(method)

    def DoMagneticThermalCalculation(self):
        method = "DoMagneticThermalCalculation"
        return self.__SendAndReceive(method)

    def GetIMSaturationFactor(self, i_mag):
        """NO SUCCESS VARIABLE.

        Returns
        -------
        satFactor : real
            Saturation Factor
        """
        method = "GetIMSaturationFactor"
        params = [i_mag]
        satFactor = self.__SendAndReceive(method, params, aSuccessVar=False)
        return satFactor

    def GetIMIronLoss(self, slip, back_emf):
        method = "GetIMIronLoss"
        params = [slip, back_emf]
        return self.__SendAndReceive(method, params)

    def Set3DComponentVisibility(self, group_name, component_name, visibility):
        method = "Set3DComponentVisibility"
        params = [group_name, component_name, visibility]
        return self.__SendAndReceive(method, params)

    def SetAllEmagCalculations(self, state):
        method = "SetAllEmagCalculations"
        params = [state]
        return self.__SendAndReceive(method, params)

    def CalculateSaturationMap(self):
        method = "CalculateSaturationMap"
        return self.__SendAndReceive(method)

    def CalculateTorqueEnvelope(self):
        method = "CalculateTorqueEnvelope"
        return self.__SendAndReceive(method)

    def SaveResults(self, solution_type):
        method = "SaveResults"
        params = [solution_type]
        return self.__SendAndReceive(method, params)

    def LoadResults(self, solution_type):
        method = "LoadResults"
        params = [solution_type]
        return self.__SendAndReceive(method, params)

    def CalculateIMSaturationModel(self):
        method = "CalculateIMSaturationModel"
        return self.__SendAndReceive(method)

    def CalculateForceHarmonics_Spatial(self):
        method = "CalculateForceHarmonics_Spatial"
        return self.__SendAndReceive(method)

    def CalculateForceHarmonics_Temporal(self):
        method = "CalculateForceHarmonics_Temporal"
        return self.__SendAndReceive(method)

    def GetForceFrequencyDomainAmplitude(self, row, column, load_point):
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, load_point]
        return self.__SendAndReceive(method, params)

    def UpdateForceAnalysisResults(self, fft_data_type):
        method = "UpdateForceAnalysisResults"
        params = [fft_data_type]
        return self.__SendAndReceive(method, params)

    def DoMultiForceCalculation(self):
        method = "DoMultiForceCalculation"
        return self.__SendAndReceive(method)

    def DoSteadyStateAnalysis(self):
        """Do thermal steady state analysis."""
        method = "DoSteadyStateAnalysis"
        return self.__SendAndReceive(method)

    def DoTransientAnalysis(self):
        """Do thermal transient analysis."""
        method = "DoTransientAnalysis"
        return self.__SendAndReceive(method)

    def DoMagneticCalculation(self):
        """Run the Motor-CAD magnetic calculation."""
        method = "DoMagneticCalculation"
        return self.__SendAndReceive(method)

    def DoWeightCalculation(self):
        """Run the Motor-CAD weight calculation."""
        method = "DoWeightCalculation"
        return self.__SendAndReceive(method)

    def DoMechanicalCalculation(self):
        """Run the Motor-CAD mechanical calculation."""
        method = "DoMechanicalCalculation"
        return self.__SendAndReceive(method)

    # ------------------------------------ Lab ------------------------------------

    def CalculateTestPerformance_Lab(self):
        method = "CalculateTestPerformance_Lab"
        return self.__SendAndReceive(method)

    def ExportDutyCycle_Lab(self):
        method = "ExportDutyCycle_Lab"
        return self.__SendAndReceive(method)

    def GetModelBuilt_Lab(self):
        method = "GetModelBuilt_Lab"
        return self.__SendAndReceive(method)

    def ShowResultsViewer_Lab(self, calculation_type):
        method = "ShowResultsViewer_Lab"
        params = [calculation_type]
        return self.__SendAndReceive(method, params)

    def ExportFigure_Lab(self, calculation_type, variable, file_name):
        method = "ExportFigure_Lab"
        params = [calculation_type, variable, file_name]
        return self.__SendAndReceive(method, params)

    def CalculateGenerator_Lab(self):
        method = "CalculateGenerator_Lab"
        return self.__SendAndReceive(method)

    def LoadExternalModel_Lab(self, file_name):
        method = "LoadExternalModel_Lab"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def ClearModelBuild_Lab(self):
        """Clear the Lab model build."""
        method = "ClearModelBuild_Lab"
        return self.__SendAndReceive(method)

    def SetMotorLABContext(self):
        """Change Motor-CAD to Lab Context."""
        method = "SetMotorLABContext"
        return self.__SendAndReceive(method)

    def BuildModel_Lab(self):
        """Build the Lab model."""
        method = "BuildModel_Lab"
        return self.__SendAndReceive(method)

    def CalculateOperatingPoint_Lab(self):
        """Calculate Lab operating point."""
        method = "CalculateOperatingPoint_Lab"
        return self.__SendAndReceive(method)

    def CalculateMagnetic_Lab(self):
        """Do Lab magnetic calculation."""
        method = "CalculateMagnetic_Lab"
        return self.__SendAndReceive(method)

    def CalculateThermal_Lab(self):
        """Do Lab thermal calculation."""
        method = "CalculateThermal_Lab"
        return self.__SendAndReceive(method)

    def CalculateDutyCycle_Lab(self):
        """Calculate Lab duty cycle."""
        method = "CalculateDutyCycle_Lab"
        return self.__SendAndReceive(method)

    # ------------------------------------ Geometry ------------------------------------

    def SetWindingCoil(
        self, phase, path, coil, go_slot, go_position, return_slot, return_position, turns
    ):
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            go_slot,
            go_position,
            return_slot,
            return_position,
            turns,
        ]
        return self.__SendAndReceive(method, params)

    def GetWindingCoil(self, phase, path, coil):
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.__SendAndReceive(method, params)

    def CheckIfGeometryIsValid(self, edit_geometry):
        """Check if Motor-CAD geometry is valid.

        Returns
        -------
        success : int
            1 indicates valid geometry
        """
        method = "CheckIfGeometryIsValid"
        params = [edit_geometry]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Graphs ------------------------------------

    def LoadMagnetisationCurves(self, file_name):
        method = "LoadMagnetisationCurves"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def SaveMagnetisationCurves(self, file_name):
        method = "SaveMagnetisationCurves"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def GetMagneticGraphPoint(self, graph_name, point_number):
        """Get a specified point from a MotorCAD Magnetic graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.__SendAndReceive(method, params)

    def GetTemperatureGraphPoint(self, graph_name, point_number):
        """Get a specified point from a MotorCAD Thermal graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.__SendAndReceive(method, params)

    def GetPowerGraphPoint(self, graph_name, point_number):
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        point_number : int
            Point number to retrieve x and y values from

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graph_name}, point_number]
        return self.__SendAndReceive(method, params)

    def GetMagnetic3DGraphPoint(self, graph_name, slice_number, point_number, time_step_number):
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_name : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graph_name}, slice_number, point_number, time_step_number]
        return self.__SendAndReceive(method, params)

    def GetFEAGraphPoint(self, graph_id, slice_number, point_number, time_step_number):
        """Get a specified point from a MotorCAD graph.

        Parameters
        ----------
        graph_id : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        slice_number

        point_number : int
            Point number to retrieve x and y values from
        time_step_number

        Returns
        -------
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graph_id}, slice_number, point_number, time_step_number]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ FEA ------------------------------------

    def SetPowerInjectionValue(self, name, node1, value, rpm_ref, rpm_coef, description):
        method = "SetPowerInjectionValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.__SendAndReceive(method, params)

    def SetFixedTemperatureValue(self, name, node1, value, description):
        method = "SetFixedTemperatureValue"
        params = [name, node1, value, description]
        return self.__SendAndReceive(method, params)

    def ClearFixedTemperatureValue(self, node1):
        method = "ClearFixedTemperatureValue"
        params = [node1]
        return self.__SendAndReceive(method, params)

    def DoSlotFiniteElement(self):
        method = "DoSlotFiniteElement"
        return self.__SendAndReceive(method)

    def ClearAllData(self):
        method = "ClearAllData"
        return self.__SendAndReceive(method)

    def AddLine_XY(self, xs, ys, xe, ye):
        method = "AddLine_XY"
        params = [xs, ys, xe, ye]
        return self.__SendAndReceive(method, params)

    def SetBndCond(self, dir_code, c1, c2, c3):
        method = "SetBndCond"
        params = [dir_code, c1, c2, c3]
        return self.__SendAndReceive(method, params)

    def StoreProblemData(self, p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max):
        method = "StoreProblemData"
        params = [p_type, eq_type, sym_mode, sym_axis, time_mode, dt, t_max]
        return self.__SendAndReceive(method, params)

    def Add_Region_Thermal_A(
        self,
        reg_name,
        thermal_conductivity,
        tcc,
        ref_temp,
        j_val,
        sigma,
        density,
        loss_density,
    ):
        method = "Add_Region_Thermal_A"
        params = [
            reg_name,
            thermal_conductivity,
            tcc,
            ref_temp,
            j_val,
            sigma,
            density,
            loss_density,
        ]
        return self.__SendAndReceive(method, params)

    def AddPoint_XY(self, x, y, reg_name):
        method = "AddPoint_XY"
        params = [x, y, reg_name]
        return self.__SendAndReceive(method, params)

    def CreateOptimisedMesh(self):
        method = "CreateOptimisedMesh"
        return self.__SendAndReceive(method)

    def CreateOptimisedMesh_Thermal(self, copper_region, ins_region, impreg_region):
        method = "CreateOptimisedMesh_Thermal"
        params = [copper_region, ins_region, impreg_region]
        return self.__SendAndReceive(method, params)

    def SetMeshGeneratorParam(self, max_bnd_length, bnd_factor, max_angle):
        method = "SetMeshGeneratorParam"
        params = [max_bnd_length, bnd_factor, max_angle]
        return self.__SendAndReceive(method, params)

    def SolveProblem(self):
        method = "SolveProblem"
        return self.__SendAndReceive(method)

    def Add_Region_Thermal(
        self, reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density
    ):
        method = "Add_Region_Thermal"
        params = [reg_name, thermal_conductivity, tcc, ref_temp, j_val, sigma, density]
        return self.__SendAndReceive(method, params)

    def AddCircularConductor_A(
        self,
        xc,
        yc,
        copper_radius,
        ins_radius,
        ang_degree,
        points_no,
        mb,
        line,
        column,
        region_name,
        j_aux,
        loss_density,
    ):
        method = "AddCircularConductor_A"
        params = [
            xc,
            yc,
            copper_radius,
            ins_radius,
            ang_degree,
            points_no,
            mb,
            line,
            column,
            region_name,
            j_aux,
            loss_density,
        ]
        return self.__SendAndReceive(method, params)

    def AddRectangularConductor_A(
        self,
        xc,
        yc,
        width,
        height,
        ins_width,
        ang_deg,
        points_no,
        mb,
        line,
        column,
        reg_name,
        j_aux,
        loss_density,
    ):
        method = "AddRectangularConductor_A"
        params = [
            xc,
            yc,
            width,
            height,
            ins_width,
            ang_deg,
            points_no,
            mb,
            line,
            column,
            reg_name,
            j_aux,
            loss_density,
        ]
        return self.__SendAndReceive(method, params)

    def AddArc_XY(self, xc, yc, th1, th2, r):
        method = "AddArc_XY"
        params = [xc, yc, th1, th2, r]
        return self.__SendAndReceive(method, params)

    def SetRegionColour(self, region, colour):
        method = "SetRegionColour"
        params = [region, colour]
        return self.__SendAndReceive(method, params)

    def AddPoint_RT(self, r, t, reg_name):
        method = "AddPoint_RT"
        params = [r, t, reg_name]
        return self.__SendAndReceive(method, params)

    def AddLine_RT(self, rs, ts, re, t_e):
        method = "AddLine_RT"
        params = [rs, ts, re, t_e]
        return self.__SendAndReceive(method, params)

    def AddArc_RT(self, rc, tc, th1, th2, r):
        method = "AddArc_RT"
        params = [rc, tc, th1, th2, r]
        return self.__SendAndReceive(method, params)

    def AddArc_Boundary_RT(
        self, direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code
    ):
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, th1, th2, r, dir_code, sym_code, virt_code, init_code]
        return self.__SendAndReceive(method, params)

    def AddArc_Boundary_XY(
        self, direction, xc, yc, th1, th2, R, dir_code, sym_code, virt_code, init_code
    ):
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, th1, th2, R, dir_code, sym_code, virt_code, init_code]
        return self.__SendAndReceive(method, params)

    def AddLine_Boundary_RT(self, rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code):
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, t_e, dir_code, sym_code, virt_code, init_code]
        return self.__SendAndReceive(method, params)

    def AddLine_Boundary_XY(self, xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code):
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dir_code, sym_code, virt_code, init_code]
        return self.__SendAndReceive(method, params)

    def InitiateGeometryFromScript(self):
        method = "InitiateGeometryFromScript"
        return self.__SendAndReceive(method)

    def AddPoint_Magnetic_RT(self, r, t, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_RT"
        params = [r, t, mag_name, br_angle, br_mult, polarity]
        return self.__SendAndReceive(method, params)

    def AddPoint_Magnetic_XY(self, x, y, mag_name, br_angle, br_mult, polarity):
        method = "AddPoint_Magnetic_XY"
        params = [x, y, mag_name, br_angle, br_mult, polarity]
        return self.__SendAndReceive(method, params)

    def AddArc_CentreStartEnd_RT(self, rc, tc, rs, ts, re, t_e):
        method = "AddArc_CentreStartEnd_RT"
        params = [rc, tc, rs, ts, re, t_e]
        return self.__SendAndReceive(method, params)

    def AddArc_CentreStartEnd_XY(self, xc, yc, xs, ys, xe, ye):
        method = "AddArc_CentreStartEnd_XY"
        params = [xc, yc, xs, ys, xe, ye]
        return self.__SendAndReceive(method, params)

    def SetFEAPathPoint(
        self, path_name, path_location, coord_system, ror_x, tor_y, calculation, expression
    ):
        method = "SetFEAPathPoint"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x,
            tor_y,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SetFEAPathArc(
        self,
        path_name,
        path_location,
        r,
        theta_start,
        theta_end,
        points,
        fea_method,
        calculation,
        expression,
    ):
        method = "SetFEAPathArc"
        params = [
            path_name,
            path_location,
            r,
            theta_start,
            theta_end,
            points,
            fea_method,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SetFEAPathLine(
        self,
        path_name,
        path_location,
        coord_system,
        ror_x_start,
        tor_y_start,
        ror_x_end,
        tor_y_end,
        points,
        calculation,
        expression,
    ):
        method = "SetFEAPathLine"
        params = [
            path_name,
            path_location,
            coord_system,
            ror_x_start,
            tor_y_start,
            ror_x_end,
            tor_y_end,
            points,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SaveFEAData(self, file, first_step, final_step, outputs, regions, separator):
        method = "SaveFEAData"
        params = [file, first_step, final_step, outputs, regions, separator]
        return self.__SendAndReceive(method, params)

    def AddPoint_CustomMaterial_XY(self, x, y, reg_name, mat_name, colour):
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, reg_name, mat_name, colour]
        return self.__SendAndReceive(method, params)

    def GetRegionValue(self, expression, region_name):
        method = "GetRegionValue"
        params = [expression, region_name]
        return self.__SendAndReceive(method, params)

    def GetRegionLoss(self, expression, region_name, radius1, radius2, angle1, angle2):
        method = "GetRegionLoss"
        params = [expression, region_name, radius1, radius2, angle1, angle2]
        return self.__SendAndReceive(method, params)

    def EditMagnetRegion(self, region_name, magnet_material, br_angle, br_multiplier):
        method = "EditMagnetRegion"
        params = [region_name, magnet_material, br_angle, br_multiplier]
        return self.__SendAndReceive(method, params)

    def AddRegion_XY(self, x, y, region_name):
        method = "AddRegion_XY"
        params = [x, y, region_name]
        return self.__SendAndReceive(method, params)

    def AddRegion_RT(self, r, t, region_name):
        method = "AddRegion_RT"
        params = [r, t, region_name]
        return self.__SendAndReceive(method, params)

    def DeleteRegions(self, region_name):
        method = "DeleteRegions"
        params = [region_name]
        return self.__SendAndReceive(method, params)

    def ResetRegions(self):
        method = "ResetRegions"
        return self.__SendAndReceive(method)

    def AddMagnetRegion_RT(
        self, r, theta, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        method = "AddMagnetRegion_RT"
        params = [
            r,
            theta,
            region_name,
            magnet_material,
            br_angle,
            br_multiplier,
            polarity_code,
        ]
        return self.__SendAndReceive(method, params)

    def AddMagnetRegion_XY(
        self, x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code
    ):
        method = "AddMagnetRegion_XY"
        params = [x, y, region_name, magnet_material, br_angle, br_multiplier, polarity_code]
        return self.__SendAndReceive(method, params)

    def GetPointValue(self, parameter, x, y):
        """Get a specified point from Motor-CAD FEA.

        Parameters
        ----------
        parameter : str|int
            Motor-CAD shading function
        x : float
            x value
        y : float
            y value

        Returns
        -------
        value : float
            value from FEA
        units : string
            units of parameter
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Thermal ------------------------------------

    def SetResistanceValue(self, name, node1, node2, value, description):
        method = "SetResistanceValue"
        params = [name, node1, node2, value, description]
        return self.__SendAndReceive(method, params)

    def SetResistanceMultiplier(self, name, node1, node2, value, description):
        method = "SetResistanceMultiplier"
        params = [name, node1, node2, value, description]
        return self.__SendAndReceive(method, params)

    def ClearExternalCircuit(self):
        method = "ClearExternalCircuit"
        return self.__SendAndReceive(method)

    def CreateNewNode(self, name, node1, row, column, colour, description):
        method = "CreateNewNode"
        params = [name, node1, row, column, colour, description]
        return self.__SendAndReceive(method, params)

    def ModifyNode(self, name, node1, row, column, colour, description):
        method = "ModifyNode"
        params = [name, node1, row, column, colour, description]
        return self.__SendAndReceive(method, params)

    def SetCapacitanceValue(self, name, node1, value, description):
        method = "SetCapacitanceValue"
        params = [name, node1, value, description]
        return self.__SendAndReceive(method, params)

    def SetPowerSourceValue(self, name, node1, value, rpm_ref, rpm_coef, description):
        method = "SetPowerSourceValue"
        params = [name, node1, value, rpm_ref, rpm_coef, description]
        return self.__SendAndReceive(method, params)

    def LoadExternalCircuit(self, circuit_file_name):
        method = "LoadExternalCircuit"
        params = [circuit_file_name]
        return self.__SendAndReceive(method, params)

    def SaveExternalCircuit(self, circuit_file_name):
        method = "SaveExternalCircuit"
        params = [circuit_file_name]
        return self.__SendAndReceive(method, params)

    def SaveTransientPowerValues(self, file_name):
        method = "SaveTransientPowerValues"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def SaveTransientTemperatures(self, file_name):
        method = "SaveTransientTemperatures"
        params = [file_name]
        return self.__SendAndReceive(method, params)

    def RemoveExternalComponent(self, component_type, name, node1):
        method = "RemoveExternalComponent"
        params = [component_type, name, node1]
        return self.__SendAndReceive(method, params)

    def GetNodeTemperature(self, node_number):
        """Get the temperature of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        value : float
            Temperature of thermal node
        """
        method = "GetNodeTemperature"
        params = [node_number]
        return self.__SendAndReceive(method, params)

    def GetNodeCapacitance(self, node_number):
        """Get the capacitance of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        value : float
            Capacitance of thermal node
        """
        method = "GetNodeCapacitance"
        params = [node_number]
        return self.__SendAndReceive(method, params)

    def GetNodePower(self, node_number):
        """Get the power of a thermal node.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        value : float
            Power of thermal node
        """
        method = "GetNodePower"
        params = [node_number]
        return self.__SendAndReceive(method, params)

    def GetNodeToNodeResistance(self, node1, node2):
        """Get node to node resistance.

        Parameters
        ----------
        node1 : int
            Thermal node number
        node2 : int
            Thermal node number
        Returns
        -------
        value : float
            Resistance value
        """
        method = "GetNodeToNodeResistance"
        params = [node1, node2]
        return self.__SendAndReceive(method, params)

    def GetNodeExists(self, node_number):
        """Check if node exists.

        Parameters
        ----------
        node_number : int
            Thermal node number

        Returns
        -------
        nodeExists : boolean
            True if node exists
        """
        method = "GetNodeExists"
        params = [node_number]
        nodeExists = self.__SendAndReceive(method, params, aSuccessVar=False)
        return nodeExists

    def GetOffsetNodeNumber(self, node_number, slice_number, cuboid_number):
        """Get offset node number.

        Parameters
        ----------
        node_number  : int
            node number
        slice_number : int
            slice number
        cuboid_number : int
            cuboid number

        Returns
        -------
        offsetNodeNumber : int
            offset node number
        """
        method = "GetOffsetNodeNumber"
        params = [node_number, slice_number, cuboid_number]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Materials ------------------------------------

    def SetFluid(self, cooling_type, fluid):
        method = "SetFluid"
        params = [cooling_type, fluid]
        return self.__SendAndReceive(method, params)

    def SetComponentMaterial(self, component_name, material_name):
        method = "SetComponentMaterial"
        params = [component_name, material_name]
        return self.__SendAndReceive(method, params)

    def GetComponentMaterial(self, component_name):
        method = "GetComponentMaterial"
        params = [component_name]
        return self.__SendAndReceive(method, params)

    def ImportSolidMaterial(self, file_name, material_name):
        method = "ImportSolidMaterial"
        params = [file_name, material_name]
        return self.__SendAndReceive(method, params)

    def ExportSolidMaterial(self, file_name, material_name):
        method = "ExportSolidMaterial"
        params = [file_name, material_name]
        return self.__SendAndReceive(method, params)

    def DeleteSolidMaterial(self, material_name):
        method = "DeleteSolidMaterial"
        params = [material_name]
        return self.__SendAndReceive(method, params)

    def CalculateIronLossCoefficients(self, material_name):
        method = "CalculateIronLossCoefficients"
        params = [material_name]
        return self.__SendAndReceive(method, params)

    def SaveIronLossCoefficients(self, material_name):
        method = "SaveIronLossCoefficients"
        params = [material_name]
        return self.__SendAndReceive(method, params)

    def CalculateMagnetParameters(self, material_name):
        method = "CalculateMagnetParameters"
        params = [material_name]
        return self.__SendAndReceive(method, params)

    def SaveMagnetParameters(self, material_name):
        method = "SaveMagnetParameters"
        params = [material_name]
        return self.__SendAndReceive(method, params)


class MotorCAD(MotorCADBase):
    """Standard MotorCAD object."""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
    ):
        """Connect to existing Motor-CAD instance or open a new one.

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

        Returns
        -------
        MotorCAD object
        """
        super().__init__(port, open_new_instance, enable_exceptions, enable_success_variable)

    # This gives an area to add functions to without touching MotorCADBase
    # Move these classes to another file?


class MotorCADCompatibility(MotorCADBase):
    """Create a MotorCAD object that behaves the same as old ActiveX methods.

    Can be used for old scripts that were written for ActiveX
    """

    def __init__(self):
        """Create MotorCADCompatibility object."""
        port = -1
        open_new_instance = False
        enable_exceptions = False
        enable_success_variable = True
        super().__init__(
            port,
            open_new_instance,
            enable_exceptions,
            enable_success_variable,
            compatibility_mode=True,
        )
