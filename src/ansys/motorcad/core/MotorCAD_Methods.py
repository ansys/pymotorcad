"""MotorCAD_Methods
version: """

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
    """IP of machine that MotorCAD is running on"""
    global SERVER_IP
    SERVER_IP = ip


def set_default_instance(port):
    """Used when running script from MotorCAD"""
    global DEFAULT_INSTANCE
    DEFAULT_INSTANCE = port


def set_motorcad_exe(exe_location):
    global MOTORCAD_EXE_GLOBAL
    MOTORCAD_EXE_GLOBAL = exe_location


class MotorCADError(Exception):
    pass


class MotorCADBase:
    """Each MotorCAD object has a Motor-CAD.exe instance attached to it"""

    def __init__(
        self,
        port,
        open_new_instance,
        enable_exceptions,
        enable_success_variable,
        reuse_parallel_instances=False,
        compatibility_mode=False,
    ):
        """Description of function
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
        """Close Motor-CAD when MotorCAD object leaves memory"""
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
        """Gets url for RPC communication"""
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
        """Returns the most recent error message

        Returns
        -------
        ErrorMessage : str
            Most recent error message
        """
        return self._last_error_message

    # Motor-CAD functions start here

    # ------------------------------------ Variables ------------------------------------

    def GetArrayVariable_2d(self, arrayName, arrayIndex1, arrayIndex2):
        method = "GetArrayVariable_2d"
        params = [arrayName, arrayIndex1, arrayIndex2]
        return self.__SendAndReceive(method, params)

    def SetArrayVariable_2d(self, arrayName, arrayIndex1, arrayIndex2, newValue):
        method = "SetArrayVariable_2d"
        params = [arrayName, arrayIndex1, arrayIndex2, {"variant": newValue}]
        return self.__SendAndReceive(method, params)

    def RestoreCompatibilitySettings(self):
        method = "RestoreCompatibilitySettings"
        return self.__SendAndReceive(method)

    def GetVariable(self, variableName):
        """Gets a MotorCAD variable

        Parameters
        ----------
        VariableName : str
            Name of variable

        Returns
        -------
        success : int
            0 indicates a successful result
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetVariable"
        params = [variableName]
        return self.__SendAndReceive(method, params)

    def GetArrayVariable(self, arrayName, arrayIndex):
        """Gets a MotorCAD array variable

        Parameters
        ----------
        arrayName : str
            Name of array
        arrayIndex : int
            Position variable in array

        Returns
        -------
        success : int
            0 indicates a successful result
        result: int|float|str|bool
            Value of MotorCAD variable
        """
        method = "GetArrayVariable"
        params = [arrayName, arrayIndex]
        return self.__SendAndReceive(method, params)

    def SetVariable(self, variableName, variableValue):
        """Sets a MotorCAD variable

        Parameters
        ----------
        variableName : str
            Name of variable
        variableValue : int|float|str|bool
            Sets the variable to this value

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "SetVariable"
        params = [variableName, {"variant": variableValue}]
        return self.__SendAndReceive(method, params)

    def SetArrayVariable(self, arrayName, arrayIndex, variableValue):
        """Sets a MotorCAD array variable

        Parameters
        ----------
        arrayName : str
            Name of array
        arrayIndex : int
            Position in array
        variableValue : int|float|str|bool
            Sets the variable to this value

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "SetArrayVariable"
        params = [arrayName, arrayIndex, {"variant": variableValue}]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ UI ------------------------------------

    def IsStopRequested(self):
        method = "IsStopRequested"
        return self.__SendAndReceive(method)

    def DisableErrorMessages(self, Active):
        method = "DisableErrorMessages"
        params = [Active]
        return self.__SendAndReceive(method, params)

    def GetMessages(self, numMessages):
        """Returns a list of the last N messages from the message history

        Parameters
        ----------
        numMessages : int
            The number of recent messages to be returned.
            If numMessages=0 all messages in history will be returned.

        Returns
        -------
        success : int
            0 indicates success
            -1 indicates failure
        messages : str
            List of messages (most recent first, separated by ;)
        """
        method = "GetMessages"
        params = [numMessages]
        return self.__SendAndReceive(method, params)

    def UpdateInterface(self):
        method = "UpdateInterface"
        return self.__SendAndReceive(method)

    def InitialiseTabNames(self):
        """Initialises the available tabs in the Motor-CAD UI.
        Call before using SaveMotorCADScreenToFile or DisplayScreen. Motor-CAD UI must be visible.

        Returns
        -------
        success : int
            0 indicates success
            -1 indicates failure
        """
        method = "InitialiseTabNames"
        return self.__SendAndReceive(method)

    def SaveMotorCADScreenToFile(self, screenName, fileName):
        """Save the whole Motor-CAD screen of the specified tab as a image file, (bmp, jpg, png).
        InitialiseTabNames must be called before using this function. Motor-CAD UI must be visible.

        Parameters
        ----------
        screenName : str
            Path of the screen to save,
            must be in the format of "tabName;tabName;tabName" e.g. "Geometry;Axial"
        fileName : str
            File where the image is to be saved (full path)

        Returns
        -------
        success : int
            0 indicates success
            -1 indicates failure
        """
        method = "SaveMotorCADScreenToFile"
        params = [screenName, fileName]
        return self.__SendAndReceive(method, params)

    def GetLicence(self):
        method = "GetLicence"
        return self.__SendAndReceive(method)

    def SetVisible(self, visible):
        """Sets the visibility of the Motor-CAD user interface

        Parameters
        ----------
        visible : bool
            When true, the Motor-CAD user interface is shown. When false, the UI is hidden.

        Returns
        -------
        success : int
            0 indicates a successful result
            -1 indicates failure
        """
        if version.parse(self._program_version) < version.parse("15.2.0"):
            # Backwards compatibility for v15.1.x
            method = "Set_Visible"
        else:  # v15.2 onwards
            method = "SetVisible"

        params = [visible]
        return self.__SendAndReceive(method, params)

    def AvoidImmediateUpdate(self, avoidUpdate):
        method = "AvoidImmediateUpdate"
        params = [{"variant": avoidUpdate}]
        return self.__SendAndReceive(method, params)

    def ClearMessageLog(self):
        method = "ClearMessageLog"
        return self.__SendAndReceive(method)

    def ShowMessage(self, message):
        """Display a message in the MotorCAD message window

        Parameters
        ----------
        message : str
            Message to display

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "ShowMessage"
        params = [message]
        return self.__SendAndReceive(method, params)

    def showmessage(self, message):
        """ "See ShowMessage. For backwards compatibility"""
        return self.ShowMessage(message)

    def ShowMagneticContext(self):
        """Show magnetic context in Motor-CAD

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "ShowMagneticContext"
        return self.__SendAndReceive(method)

    def ShowMechanicalContext(self):
        """Show mechanical context in Motor-CAD

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "ShowMechanicalContext"
        return self.__SendAndReceive(method)

    def ShowThermalContext(self):
        """Show thermal context in Motor-CAD

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "ShowThermalContext"
        return self.__SendAndReceive(method)

    def DisplayScreen(self, screenName):
        """Shows a screen within Motor-CAD

        Parameters
        ----------
        screenName : str
            Screen to display

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "DisplayScreen"
        params = [screenName]
        return self.__SendAndReceive(method, params)

    def Quit(self):
        """Quits MotorCAD"""
        method = "Quit"
        return self.__SendAndReceive(method)

    def SaveScreenToFile(self, screenName, fileName):
        """Saves a screen as an image

        Parameters
        ----------
        screenName : str
            Screen to save
        fileName : str
            File to save image full path

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "SaveScreenToFile"
        params = [screenName, fileName]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Files ------------------------------------

    def LoadDutyCycle(self, fileName):
        method = "LoadDutyCycle"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def SaveDutyCycle(self, fileName):
        method = "SaveDutyCycle"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def ExportMatrices(self, fileName):
        method = "ExportMatrices"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def LoadCustomDriveCycle(self, fileName):
        method = "LoadCustomDriveCycle"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def LoadFEAResult(self, fileName, solutionNumber):
        method = "LoadFEAResult"
        params = [fileName, solutionNumber]
        return self.__SendAndReceive(method, params)

    def ExportToAnsysElectronicsDesktop(self, fileName):
        method = "ExportToAnsysElectronicsDesktop"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def ExportResults(self, solutionType, fileName):
        method = "ExportResults"
        params = [solutionType, fileName]
        return self.__SendAndReceive(method, params)

    def LoadDXFFile(self, fileName):
        method = "LoadDXFFile"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def CreateReport(self, filePath, templatefilePath):
        method = "CreateReport"
        params = [filePath, templatefilePath]
        return self.__SendAndReceive(method, params)

    def LoadReportStructure(self, filePath):
        method = "LoadReportStructure"
        params = [filePath]
        return self.__SendAndReceive(method, params)

    def ExportForceAnimation(self, animation, fileName):
        method = "ExportForceAnimation"
        params = [animation, fileName]
        return self.__SendAndReceive(method, params)

    def LoadReportTree(self):
        method = "LoadReportTree"
        return self.__SendAndReceive(method)

    def LoadTemplate(self, templateName):
        method = "LoadTemplate"
        params = [templateName]
        return self.__SendAndReceive(method, params)

    def SaveTemplate(
        self,
        templateFileName,
        name,
        sector,
        machineType,
        application,
        windingType,
        maxSpeed,
        power,
        cooling,
        driveType,
        notes,
    ):
        method = "SaveTemplate"
        params = [
            templateFileName,
            name,
            sector,
            machineType,
            application,
            windingType,
            maxSpeed,
            power,
            cooling,
            driveType,
            notes,
        ]
        return self.__SendAndReceive(method, params)

    def LoadWindingPattern(self, fileName):
        method = "LoadWindingPattern"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def SaveWindingPattern(self, fileName):
        method = "SaveWindingPattern"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def ExportMultiForceData(self, fileName):
        method = "ExportMultiForceData"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def GeometryExport(self):
        method = "GeometryExport"
        return self.__SendAndReceive(method)

    def ExportToAnsysDiscovery(self, fileName):
        method = "ExportToAnsysDiscovery"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def ExportNVHResultsData(self, fileName):
        method = "ExportNVHResultsData"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def LoadFromFile(self, motFile):
        """Loads a .mot file into the MotorCAD instance

        Parameters
        ----------
        motFile : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "LoadFromFile"
        params = [motFile]
        return self.__SendAndReceive(method, params)

    def SaveToFile(self, motFile):
        """Saves the current .mot file

        Parameters
        ----------
        motFile : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "SaveToFile"
        params = [motFile]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Internal Scripting ------------------------------------

    def SaveScript(self, fileName):
        method = "SaveScript"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def LoadScript(self, scriptFile):
        """Loads a script file into Motor-CAD internal scripting

        Parameters
        ----------
        scriptFile : str
            Full path to file including file name. You can use r'filepath' syntax to force
            Python to ignore special characters.

        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "LoadScript"
        params = [scriptFile]
        return self.__SendAndReceive(method, params)

    def RunScript(self):
        """Runs script file in Motor-CAD internal scripting
        Returns
        -------
        success : int
            0 indicates a successful result
        """
        method = "RunScript"
        return self.__SendAndReceive(method)

    # ------------------------------------ Calculations ------------------------------------

    def ClearDutyCycle(self):
        method = "ClearDutyCycle"
        return self.__SendAndReceive(method)

    def DoMagneticThermalCalculation(self):
        method = "DoMagneticThermalCalculation"
        return self.__SendAndReceive(method)

    def GetIMSaturationFactor(self, iMag):
        """NO SUCCESS VARIABLE
        Returns
        -------
        satFactor : real
            Saturation Factor
        """
        method = "GetIMSaturationFactor"
        params = [iMag]
        satFactor = self.__SendAndReceive(method, params, aSuccessVar=False)
        return satFactor

    def GetIMIronLoss(self, slip, backEMF):
        method = "GetIMIronLoss"
        params = [slip, backEMF]
        return self.__SendAndReceive(method, params)

    def Set3DComponentVisibility(self, groupName, componentName, visibility):
        method = "Set3DComponentVisibility"
        params = [groupName, componentName, visibility]
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

    def SaveResults(self, solutionType):
        method = "SaveResults"
        params = [solutionType]
        return self.__SendAndReceive(method, params)

    def LoadResults(self, solutionType):
        method = "LoadResults"
        params = [solutionType]
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

    def GetForceFrequencyDomainAmplitude(self, row, column, loadpoint):
        method = "GetForceFrequencyDomainAmplitude"
        params = [row, column, loadpoint]
        return self.__SendAndReceive(method, params)

    def UpdateForceAnalysisResults(self, FFTDataType):
        method = "UpdateForceAnalysisResults"
        params = [FFTDataType]
        return self.__SendAndReceive(method, params)

    def DoMultiForceCalculation(self):
        method = "DoMultiForceCalculation"
        return self.__SendAndReceive(method)

    def DoSteadyStateAnalysis(self):
        """Do thermal steady state analysis

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "DoSteadyStateAnalysis"
        return self.__SendAndReceive(method)

    def DoTransientAnalysis(self):
        """Do thermal transient analysis

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "DoTransientAnalysis"
        return self.__SendAndReceive(method)

    def DoMagneticCalculation(self):
        """Run the Motor-CAD magnetic calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "DoMagneticCalculation"
        return self.__SendAndReceive(method)

    def DoWeightCalculation(self):
        """Run the Motor-CAD weight calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "DoWeightCalculation"
        return self.__SendAndReceive(method)

    def DoMechanicalCalculation(self):
        """Run the Motor-CAD mechanical calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
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

    def ShowResultsViewer_Lab(self, calculationType):
        method = "ShowResultsViewer_Lab"
        params = [calculationType]
        return self.__SendAndReceive(method, params)

    def ExportFigure_Lab(self, calculationType, variable, fileName):
        method = "ExportFigure_Lab"
        params = [calculationType, variable, fileName]
        return self.__SendAndReceive(method, params)

    def CalculateGenerator_Lab(self):
        method = "CalculateGenerator_Lab"
        return self.__SendAndReceive(method)

    def LoadExternalModel_Lab(self, fileName):
        method = "LoadExternalModel_Lab"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def ClearModelBuild_Lab(self):
        """Clears the Lab model build

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "ClearModelBuild_Lab"
        return self.__SendAndReceive(method)

    def SetMotorLABContext(self):
        """Changes Motor-CAD to Lab Context"""
        method = "SetMotorLABContext"
        return self.__SendAndReceive(method)

    def BuildModel_Lab(self):
        """Builds the Lab model

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "BuildModel_Lab"
        return self.__SendAndReceive(method)

    def CalculateOperatingPoint_Lab(self):
        """Calculates Lab operating point

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "CalculateOperatingPoint_Lab"
        return self.__SendAndReceive(method)

    def CalculateMagnetic_Lab(self):
        """Does Lab magnetic calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "CalculateMagnetic_Lab"
        return self.__SendAndReceive(method)

    def CalculateThermal_Lab(self):
        """Does Lab thermal calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "CalculateThermal_Lab"
        return self.__SendAndReceive(method)

    def CalculateDutyCycle_Lab(self):
        """Does Lab duty cycle calculation

        Returns
        -------
        success : int
            0 indicates a successful calculation
        """
        method = "CalculateDutyCycle_Lab"
        return self.__SendAndReceive(method)

    # ------------------------------------ Geometry ------------------------------------

    def SetWindingCoil(
        self, phase, path, coil, goSlot, goPosition, returnSlot, returnPosition, turns
    ):
        method = "SetWindingCoil"
        params = [
            phase,
            path,
            coil,
            goSlot,
            goPosition,
            returnSlot,
            returnPosition,
            turns,
        ]
        return self.__SendAndReceive(method, params)

    def GetWindingCoil(self, phase, path, coil):
        method = "GetWindingCoil"
        params = [phase, path, coil]
        return self.__SendAndReceive(method, params)

    def CheckIfGeometryIsValid(self, editGeometry):
        """Checks if Motor-CAD geometry is valid

        Returns
        -------
        success : int
            1 indicates valid geometry
            NOTE: This is different to the standard convention
        """
        method = "CheckIfGeometryIsValid"
        params = [editGeometry]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Graphs ------------------------------------

    def LoadMagnetisationCurves(self, fileName):
        method = "LoadMagnetisationCurves"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def SaveMagnetisationCurves(self, fileName):
        method = "SaveMagnetisationCurves"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def GetMagneticGraphPoint(self, graphName, pointNumber):
        """Gets a specified point from a MotorCAD Magnetic graph

        Parameters
        ----------
        graphName : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        pointNumber : int
            Point number to retrieve x and y values from

        Returns
        -------
        success : int
            0 indicates a successful result
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagneticGraphPoint"
        params = [{"variant": graphName}, pointNumber]
        return self.__SendAndReceive(method, params)

    def GetTemperatureGraphPoint(self, graphName, pointNumber):
        """Gets a specified point from a MotorCAD Thermal graph

        Parameters
        ----------
        graphName : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        pointNumber : int
            Point number to retrieve x and y values from

        Returns
        -------
        success : int
            0 indicates a successful result
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetTemperatureGraphPoint"
        params = [{"variant": graphName}, pointNumber]
        return self.__SendAndReceive(method, params)

    def GetPowerGraphPoint(self, graphName, pointNumber):
        """Gets a specified point from a MotorCAD graph

        Parameters
        ----------
        graphName : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        pointNumber : int
            Point number to retrieve x and y values from

        Returns
        -------
        success : int
            0 indicates a successful result
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetPowerGraphPoint"
        params = [{"variant": graphName}, pointNumber]
        return self.__SendAndReceive(method, params)

    def GetMagnetic3DGraphPoint(self, graphName, sliceNumber, pointNumber, timeStepNumber):
        """Gets a specified point from a MotorCAD graph

        Parameters
        ----------
        graphName : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        sliceNumber

        pointNumber : int
            Point number to retrieve x and y values from
        timeStepNumber

        Returns
        -------
        success : int
            0 indicates a successful result
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetMagnetic3DGraphPoint"
        params = [{"variant": graphName}, sliceNumber, pointNumber, timeStepNumber]
        return self.__SendAndReceive(method, params)

    def GetFEAGraphPoint(self, graphID, sliceNumber, pointNumber, timeStepNumber):
        """Gets a specified point from a MotorCAD graph

        Parameters
        ----------
        graphID : str|int
            Name/id of graph to select. Graph name is preferred and can be found in
            MotorCAD (help -> graph viewer)
        sliceNumber

        pointNumber : int
            Point number to retrieve x and y values from
        timeStepNumber

        Returns
        -------
        success : int
            0 indicates a successful result
        xValue : float
            value of x coordinate from graph
        yValue : float
            value of y coordinate from graph
        """
        method = "GetFEAGraphPoint"
        params = [{"variant": graphID}, sliceNumber, pointNumber, timeStepNumber]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ FEA ------------------------------------

    def SetPowerInjectionValue(self, name, node1, Value, RPM_Ref, RPM_Coef, description):
        method = "SetPowerInjectionValue"
        params = [name, node1, Value, RPM_Ref, RPM_Coef, description]
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

    def SetBndCond(self, dirCode, c1, c2, c3):
        method = "SetBndCond"
        params = [dirCode, c1, c2, c3]
        return self.__SendAndReceive(method, params)

    def StoreProblemData(self, PType, EqType, Symmode, SymmAxis, TimeMode, dt, tmax):
        method = "StoreProblemData"
        params = [PType, EqType, Symmode, SymmAxis, TimeMode, dt, tmax]
        return self.__SendAndReceive(method, params)

    def Add_Region_Thermal_A(
        self,
        regName,
        ThermalConductivity,
        Tcc,
        RefTemp,
        JVal,
        Sigma,
        Density,
        LossDensity,
    ):
        method = "Add_Region_Thermal_A"
        params = [
            regName,
            ThermalConductivity,
            Tcc,
            RefTemp,
            JVal,
            Sigma,
            Density,
            LossDensity,
        ]
        return self.__SendAndReceive(method, params)

    def AddPoint_XY(self, x, y, regName):
        method = "AddPoint_XY"
        params = [x, y, regName]
        return self.__SendAndReceive(method, params)

    def CreateOptimisedMesh(self):
        method = "CreateOptimisedMesh"
        return self.__SendAndReceive(method)

    def CreateOptimisedMesh_Thermal(self, copperRegion, insRegion, impregRegion):
        method = "CreateOptimisedMesh_Thermal"
        params = [copperRegion, insRegion, impregRegion]
        return self.__SendAndReceive(method, params)

    def SetMeshGeneratorParam(self, maxBndLength, BndFactor, maxAngle):
        method = "SetMeshGeneratorParam"
        params = [maxBndLength, BndFactor, maxAngle]
        return self.__SendAndReceive(method, params)

    def SolveProblem(self):
        method = "SolveProblem"
        return self.__SendAndReceive(method)

    def Add_Region_Thermal(self, RegName, ThermalConductivity, Tcc, RefTemp, JVal, Sigma, Density):
        method = "Add_Region_Thermal"
        params = [RegName, ThermalConductivity, Tcc, RefTemp, JVal, Sigma, Density]
        return self.__SendAndReceive(method, params)

    def AddCircularConductor_A(
        self,
        xc,
        yc,
        copperRadius,
        insRadius,
        angDegree,
        PointsNo,
        Mb,
        Line,
        Column,
        RegionName,
        JAux,
        LossDensity,
    ):
        method = "AddCircularConductor_A"
        params = [
            xc,
            yc,
            copperRadius,
            insRadius,
            angDegree,
            PointsNo,
            Mb,
            Line,
            Column,
            RegionName,
            JAux,
            LossDensity,
        ]
        return self.__SendAndReceive(method, params)

    def AddRectangularConductor_A(
        self,
        xc,
        yc,
        Width,
        Height,
        InsWidth,
        angDeg,
        PointsNo,
        Mb,
        line,
        column,
        regName,
        JAux,
        LossDensity,
    ):
        method = "AddRectangularConductor_A"
        params = [
            xc,
            yc,
            Width,
            Height,
            InsWidth,
            angDeg,
            PointsNo,
            Mb,
            line,
            column,
            regName,
            JAux,
            LossDensity,
        ]
        return self.__SendAndReceive(method, params)

    def AddArc_XY(self, xc, yc, Th1, Th2, R):
        method = "AddArc_XY"
        params = [xc, yc, Th1, Th2, R]
        return self.__SendAndReceive(method, params)

    def SetRegionColour(self, region, colour):
        method = "SetRegionColour"
        params = [region, colour]
        return self.__SendAndReceive(method, params)

    def AddPoint_RT(self, r, t, regName):
        method = "AddPoint_RT"
        params = [r, t, regName]
        return self.__SendAndReceive(method, params)

    def AddLine_RT(self, rs, ts, re, te):
        method = "AddLine_RT"
        params = [rs, ts, re, te]
        return self.__SendAndReceive(method, params)

    def AddArc_RT(self, rc, tc, Th1, Th2, R):
        method = "AddArc_RT"
        params = [rc, tc, Th1, Th2, R]
        return self.__SendAndReceive(method, params)

    def AddArc_Boundary_RT(
        self, direction, rc, tc, Th1, Th2, R, dircode, symmcode, virtcode, initcode
    ):
        method = "AddArc_Boundary_RT"
        params = [direction, rc, tc, Th1, Th2, R, dircode, symmcode, virtcode, initcode]
        return self.__SendAndReceive(method, params)

    def AddArc_Boundary_XY(
        self, direction, xc, yc, Th1, Th2, R, dircode, symmcode, virtcode, initcode
    ):
        method = "AddArc_Boundary_XY"
        params = [direction, xc, yc, Th1, Th2, R, dircode, symmcode, virtcode, initcode]
        return self.__SendAndReceive(method, params)

    def AddLine_Boundary_RT(self, rs, ts, re, te, dircode, symmcode, virtcode, initcode):
        method = "AddLine_Boundary_RT"
        params = [rs, ts, re, te, dircode, symmcode, virtcode, initcode]
        return self.__SendAndReceive(method, params)

    def AddLine_Boundary_XY(self, xs, ys, xe, ye, dircode, symmcode, virtcode, initcode):
        method = "AddLine_Boundary_XY"
        params = [xs, ys, xe, ye, dircode, symmcode, virtcode, initcode]
        return self.__SendAndReceive(method, params)

    def InitiateGeometryFromScript(self):
        method = "InitiateGeometryFromScript"
        return self.__SendAndReceive(method)

    def AddPoint_Magnetic_RT(self, r, t, magName, brAngle, brMult, polarity):
        method = "AddPoint_Magnetic_RT"
        params = [r, t, magName, brAngle, brMult, polarity]
        return self.__SendAndReceive(method, params)

    def AddPoint_Magnetic_XY(self, x, y, magName, brAngle, brMult, polarity):
        method = "AddPoint_Magnetic_XY"
        params = [x, y, magName, brAngle, brMult, polarity]
        return self.__SendAndReceive(method, params)

    def AddArc_CentreStartEnd_RT(self, rc, tc, rs, ts, re, te):
        method = "AddArc_CentreStartEnd_RT"
        params = [rc, tc, rs, ts, re, te]
        return self.__SendAndReceive(method, params)

    def AddArc_CentreStartEnd_XY(self, xc, yc, xs, ys, xe, ye):
        method = "AddArc_CentreStartEnd_XY"
        params = [xc, yc, xs, ys, xe, ye]
        return self.__SendAndReceive(method, params)

    def SetFEAPathPoint(
        self, pathName, pathLocation, coordSystem, rorx, tory, calculation, expression
    ):
        method = "SetFEAPathPoint"
        params = [
            pathName,
            pathLocation,
            coordSystem,
            rorx,
            tory,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SetFEAPathArc(
        self,
        pathName,
        pathLocation,
        r,
        thetaStart,
        thetaEnd,
        points,
        FEAmethod,
        calculation,
        expression,
    ):
        method = "SetFEAPathArc"
        params = [
            pathName,
            pathLocation,
            r,
            thetaStart,
            thetaEnd,
            points,
            FEAmethod,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SetFEAPathLine(
        self,
        pathName,
        pathLocation,
        coordSystem,
        rorXStart,
        torYStart,
        rorXEnd,
        torYEnd,
        points,
        calculation,
        expression,
    ):
        method = "SetFEAPathLine"
        params = [
            pathName,
            pathLocation,
            coordSystem,
            rorXStart,
            torYStart,
            rorXEnd,
            torYEnd,
            points,
            calculation,
            expression,
        ]
        return self.__SendAndReceive(method, params)

    def SaveFEAData(self, file, firstStep, finalStep, outputs, regions, separator):
        method = "SaveFEAData"
        params = [file, firstStep, finalStep, outputs, regions, separator]
        return self.__SendAndReceive(method, params)

    def AddPoint_CustomMaterial_XY(self, x, y, regName, matName, colour):
        method = "AddPoint_CustomMaterial_XY"
        params = [x, y, regName, matName, colour]
        return self.__SendAndReceive(method, params)

    def GetRegionValue(self, expression, regionName):
        method = "GetRegionValue"
        params = [expression, regionName]
        return self.__SendAndReceive(method, params)

    def GetRegionLoss(self, expression, regionName, radius1, radius2, angle1, angle2):
        method = "GetRegionLoss"
        params = [expression, regionName, radius1, radius2, angle1, angle2]
        return self.__SendAndReceive(method, params)

    def EditMagnetRegion(self, regionName, magnetMaterial, brAngle, brMultiplier):
        method = "EditMagnetRegion"
        params = [regionName, magnetMaterial, brAngle, brMultiplier]
        return self.__SendAndReceive(method, params)

    def AddRegion_XY(self, x, y, regionName):
        method = "AddRegion_XY"
        params = [x, y, regionName]
        return self.__SendAndReceive(method, params)

    def AddRegion_RT(self, r, t, regionName):
        method = "AddRegion_RT"
        params = [r, t, regionName]
        return self.__SendAndReceive(method, params)

    def DeleteRegions(self, regionName):
        method = "DeleteRegions"
        params = [regionName]
        return self.__SendAndReceive(method, params)

    def ResetRegions(self):
        method = "ResetRegions"
        return self.__SendAndReceive(method)

    def AddMagnetRegion_RT(
        self, r, theta, regionName, magnetMaterial, brAngle, brMultiplier, polarityCode
    ):
        method = "AddMagnetRegion_RT"
        params = [
            r,
            theta,
            regionName,
            magnetMaterial,
            brAngle,
            brMultiplier,
            polarityCode,
        ]
        return self.__SendAndReceive(method, params)

    def AddMagnetRegion_XY(
        self, x, y, regionName, magnetMaterial, brAngle, brMultiplier, polarityCode
    ):
        method = "AddMagnetRegion_XY"
        params = [x, y, regionName, magnetMaterial, brAngle, brMultiplier, polarityCode]
        return self.__SendAndReceive(method, params)

    def GetPointValue(self, parameter, x, y):
        """Gets a specified point from Motor-CAD FEA

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
        success : int
            0 indicates a successful result
        value : float
            value from FEA
        units : string
            units of parameter
        """
        method = "GetPointValue"
        params = [{"variant": parameter}, x, y]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Thermal ------------------------------------

    def SetResistanceValue(self, name, node1, node2, Value, description):
        method = "SetResistanceValue"
        params = [name, node1, node2, Value, description]
        return self.__SendAndReceive(method, params)

    def SetResistanceMultiplier(self, name, node1, node2, Value, description):
        method = "SetResistanceMultiplier"
        params = [name, node1, node2, Value, description]
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

    def SetCapacitanceValue(self, name, node1, Value, description):
        method = "SetCapacitanceValue"
        params = [name, node1, Value, description]
        return self.__SendAndReceive(method, params)

    def SetPowerSourceValue(self, name, node1, Value, RPM_Ref, RPM_Coef, description):
        method = "SetPowerSourceValue"
        params = [name, node1, Value, RPM_Ref, RPM_Coef, description]
        return self.__SendAndReceive(method, params)

    def LoadExternalCircuit(self, CircuitFileName):
        method = "LoadExternalCircuit"
        params = [CircuitFileName]
        return self.__SendAndReceive(method, params)

    def SaveExternalCircuit(self, CircuitFileName):
        method = "SaveExternalCircuit"
        params = [CircuitFileName]
        return self.__SendAndReceive(method, params)

    def SaveTransientPowerValues(self, fileName):
        method = "SaveTransientPowerValues"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def SaveTransientTemperatures(self, fileName):
        method = "SaveTransientTemperatures"
        params = [fileName]
        return self.__SendAndReceive(method, params)

    def RemoveExternalComponent(self, componentType, name, node1):
        method = "RemoveExternalComponent"
        params = [componentType, name, node1]
        return self.__SendAndReceive(method, params)

    def GetNodeTemperature(self, nodeNumber):
        """Gets the temperature of a thermal node

        Parameters
        ----------
        nodeNumber : int
            Thermal node number

        Returns
        -------
        success : int
            0 indicates a successful result
        value : float
            Temperature of thermal node
        """
        method = "GetNodeTemperature"
        params = [nodeNumber]
        return self.__SendAndReceive(method, params)

    def GetNodeCapacitance(self, nodeNumber):
        """Gets the capacitance of a thermal node

        Parameters
        ----------
        nodeNumber : int
            Thermal node number

        Returns
        -------
        success : int
            0 indicates a successful result
        value : float
            Capacitance of thermal node
        """
        method = "GetNodeCapacitance"
        params = [nodeNumber]
        return self.__SendAndReceive(method, params)

    def GetNodePower(self, nodeNumber):
        """Gets the power of a thermal node

        Parameters
        ----------
        nodeNumber : int
            Thermal node number

        Returns
        -------
        success : int
            0 indicates a successful result
        value : float
            Power of thermal node
        """
        method = "GetNodePower"
        params = [nodeNumber]
        return self.__SendAndReceive(method, params)

    def GetNodeToNodeResistance(self, node1, node2):
        """Gets node to node resistance

        Parameters
        ----------
        node1 : int
            Thermal node number
        node2 : int
            Thermal node number
        Returns
        -------
        success : int
            0 indicates a successful result
        value : float
            Resistance value
        """
        method = "GetNodeToNodeResistance"
        params = [node1, node2]
        return self.__SendAndReceive(method, params)

    def GetNodeExists(self, nodeNumber):
        """Checks if node exists

        Parameters
        ----------
        nodeNumber : int
            Thermal node number

        Returns
        -------
        nodeExists : boolean
            True if node exists
        """
        method = "GetNodeExists"
        params = [nodeNumber]
        nodeExists = self.__SendAndReceive(method, params, aSuccessVar=False)
        return nodeExists

    def GetOffsetNodeNumber(self, nodeNumber, sliceNumber, cuboidNumber):
        """Get offset node number

        Parameters
        ----------
        sliceNumber : int
            slice number
        cuboidNumber : int
            cuboid number

        Returns
        -------
        success : int
            0 indicates a successful result
        offsetNodeNumber : int
            offset node number
        """
        method = "GetOffsetNodeNumber"
        params = [nodeNumber, sliceNumber, cuboidNumber]
        return self.__SendAndReceive(method, params)

    # ------------------------------------ Materials ------------------------------------

    def SetFluid(self, coolingType, fluid):
        method = "SetFluid"
        params = [coolingType, fluid]
        return self.__SendAndReceive(method, params)

    def SetComponentMaterial(self, componentName, materialName):
        method = "SetComponentMaterial"
        params = [componentName, materialName]
        return self.__SendAndReceive(method, params)

    def GetComponentMaterial(self, componentName):
        method = "GetComponentMaterial"
        params = [componentName]
        return self.__SendAndReceive(method, params)

    def ImportSolidMaterial(self, fileName, materialName):
        method = "ImportSolidMaterial"
        params = [fileName, materialName]
        return self.__SendAndReceive(method, params)

    def ExportSolidMaterial(self, fileName, materialName):
        method = "ExportSolidMaterial"
        params = [fileName, materialName]
        return self.__SendAndReceive(method, params)

    def DeleteSolidMaterial(self, materialName):
        method = "DeleteSolidMaterial"
        params = [materialName]
        return self.__SendAndReceive(method, params)

    def CalculateIronLossCoefficients(self, materialName):
        method = "CalculateIronLossCoefficients"
        params = [materialName]
        return self.__SendAndReceive(method, params)

    def SaveIronLossCoefficients(self, materialName):
        method = "SaveIronLossCoefficients"
        params = [materialName]
        return self.__SendAndReceive(method, params)

    def CalculateMagnetParameters(self, materialName):
        method = "CalculateMagnetParameters"
        params = [materialName]
        return self.__SendAndReceive(method, params)

    def SaveMagnetParameters(self, materialName):
        method = "SaveMagnetParameters"
        params = [materialName]
        return self.__SendAndReceive(method, params)


class MotorCAD(MotorCADBase):
    """Standard MotorCAD object"""

    def __init__(
        self,
        port=-1,
        open_new_instance=True,
        enable_exceptions=True,
        enable_success_variable=False,
    ):
        """Connect to existing Motor-CAD instance or open a new one
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
    """Creates a MotorCAD object that behaves the same as old ActiveX methods.
    Can be used for old scripts that were written for ActiveX"""

    def __init__(self):
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
