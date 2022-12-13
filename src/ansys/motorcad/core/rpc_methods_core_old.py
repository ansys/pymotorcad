"""Contains all the JSON-RPC API calls for Motor-CAD with the old CamelCase function names.

For backwards compatibility.
Not for direct use. Inherited by
"""
from sys import _getframe
from warnings import warn

from ansys.motorcad.core.rpc_methods_core import _RpcMethodsCore
from ansys.motorcad.core.rpc_methods_internal import _RpcMethodsInternal


def deprecation_warning(old_name, new_name):
    """Output deprecation warning for old method names."""
    warn(
        "Function: " + old_name + " is deprecated and has been replaced by: " + new_name + "."
        "\nThis function will be removed in version.....",
        DeprecationWarning,
    )


class _RpcMethodsCoreOld:
    def __init__(self, mc_connection):
        self.new_methods = _RpcMethodsCore(mc_connection)
        self.internal_methods = _RpcMethodsInternal(mc_connection)

    # ------------------------------------ Variables ------------------------------------
    def GetArrayVariable_2d(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_array_variable_2d`."""
        replacement_function = self.new_methods.get_array_variable_2d
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetArrayVariable_2d(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_array_variable_2d`."""
        replacement_function = self.new_methods.set_array_variable_2d
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def RestoreCompatibilitySettings(self):
        """Deprecated function. Replaced by :func:`MotorCAD.restore_compatibility_settings`."""
        replacement_function = self.new_methods.restore_compatibility_settings
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def GetVariable(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_variable`."""
        replacement_function = self.new_methods.get_variable
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetArrayVariable(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_array_variable`."""
        replacement_function = self.new_methods.get_array_variable
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetVariable(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_variable`."""
        replacement_function = self.new_methods.set_variable
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetArrayVariable(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_array_variable`."""
        replacement_function = self.new_methods.set_array_variable
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ UI ------------------------------------

    def IsStopRequested(self):
        """Deprecated function."""
        replacement_function = self.internal_methods.is_stop_requested
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DisableErrorMessages(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.disable_error_messages`."""
        replacement_function = self.new_methods.disable_error_messages
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetMessages(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_messages`."""
        replacement_function = self.new_methods.get_messages
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def UpdateInterface(self):
        """Deprecated function."""
        replacement_function = self.internal_methods.update_interface
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def InitialiseTabNames(self):
        """Deprecated function. Replaced by :func:`MotorCAD.initialise_tab_names`."""
        replacement_function = self.new_methods.initialise_tab_names
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def SaveMotorCADScreenToFile(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_motorcad_screen_to_file`."""
        replacement_function = self.new_methods.save_motorcad_screen_to_file
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetLicence(self):
        """Deprecated function. Replaced by :func:`MotorCAD.get_license`."""
        replacement_function = self.new_methods.get_license
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def SetVisible(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_visible`."""
        replacement_function = self.new_methods.set_visible
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AvoidImmediateUpdate(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.avoid_immediate_update
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ClearMessageLog(self):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_message_log`."""
        replacement_function = self.new_methods.clear_message_log
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ShowMessage(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.show_message`."""
        replacement_function = self.new_methods.show_message
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ShowMagneticContext(self):
        """Deprecated function. Replaced by :func:`MotorCAD.show_magnetic_context`."""
        replacement_function = self.new_methods.show_magnetic_context
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ShowMechanicalContext(self):
        """Deprecated function. Replaced by :func:`MotorCAD.show_mechanical_context`."""
        replacement_function = self.new_methods.show_mechanical_context
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ShowThermalContext(self):
        """Deprecated function. Replaced by :func:`MotorCAD.show_thermal_context`."""
        replacement_function = self.new_methods.show_thermal_context
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DisplayScreen(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.display_screen`."""
        replacement_function = self.new_methods.display_screen
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def Quit(self):
        """Deprecated function. Replaced by :func:`MotorCAD.quit`."""
        replacement_function = self.new_methods.quit
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def set_free(self):
        """Deprecated function. Replaced by :func:`MotorCAD.set_free`."""
        replacement_function = self.new_methods.set_free
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def SaveScreenToFile(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_screen_to_file`."""
        replacement_function = self.new_methods.save_screen_to_file
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ Files ------------------------------------

    def LoadDutyCycle(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_duty_cycle`."""
        replacement_function = self.new_methods.load_duty_cycle
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveDutyCycle(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_duty_cycle`."""
        replacement_function = self.new_methods.save_duty_cycle
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportMatrices(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_matrices`."""
        replacement_function = self.new_methods.export_matrices
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadCustomDriveCycle(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_custom_drive_cycle`."""
        replacement_function = self.new_methods.load_custom_drive_cycle
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadFEAResult(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_fea_result`."""
        replacement_function = self.new_methods.load_fea_result
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportToAnsysElectronicsDesktop(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_to_ansys_electronics_desktop`."""
        replacement_function = self.new_methods.export_to_ansys_electronics_desktop
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportResults(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_results`."""
        replacement_function = self.new_methods.export_results
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadDXFFile(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_dxf_file`."""
        replacement_function = self.new_methods.load_dxf_file
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CreateReport(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.create_report`."""
        replacement_function = self.new_methods.create_report
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadReportStructure(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_report_structure`."""
        replacement_function = self.new_methods.load_report_structure
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportForceAnimation(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_force_animation`."""
        replacement_function = self.new_methods.export_force_animation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadReportTree(self):
        """Deprecated function. Replaced by :func:`MotorCAD.load_report_tree`."""
        replacement_function = self.new_methods.load_report_tree
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def LoadTemplate(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_template`."""
        replacement_function = self.new_methods.load_template
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveTemplate(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_template`."""
        replacement_function = self.new_methods.save_template
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadWindingPattern(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_winding_pattern`."""
        replacement_function = self.new_methods.load_winding_pattern
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveWindingPattern(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_winding_pattern`."""
        replacement_function = self.new_methods.save_winding_pattern
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportMultiForceData(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_multi_force_data`."""
        replacement_function = self.new_methods.export_multi_force_data
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GeometryExport(self):
        """Deprecated function. Replaced by :func:`MotorCAD.geometry_export`."""
        replacement_function = self.new_methods.geometry_export
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ExportToAnsysDiscovery(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_to_ansys_discovery`."""
        replacement_function = self.new_methods.export_to_ansys_discovery
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportNVHResultsData(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_nvh_results_data`."""
        replacement_function = self.new_methods.export_nvh_results_data
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadFromFile(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_from_file`."""
        replacement_function = self.new_methods.load_from_file
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveToFile(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_to_file`."""
        replacement_function = self.new_methods.save_to_file
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ Internal Scripting ------------------------------------

    def SaveScript(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_script`."""
        replacement_function = self.new_methods.save_script
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadScript(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_script`."""
        replacement_function = self.new_methods.load_script
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def RunScript(self):
        """Deprecated function. Replaced by :func:`MotorCAD.run_script`."""
        replacement_function = self.new_methods.run_script
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    # ------------------------------------ Calculations ------------------------------------

    def ClearDutyCycle(self):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_duty_cycle`."""
        replacement_function = self.new_methods.clear_duty_cycle
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoMagneticThermalCalculation(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_magnetic_thermal_calculation`."""
        replacement_function = self.new_methods.do_magnetic_thermal_calculation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def GetIMIronLoss(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.get_im_iron_loss
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def Set3DComponentVisibility(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_3d_component_visibility`."""
        replacement_function = self.new_methods.set_3d_component_visibility
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetAllEmagCalculations(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.set_all_emag_calculations
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CalculateSaturationMap(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_saturation_map`."""
        replacement_function = self.new_methods.calculate_saturation_map
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateTorqueEnvelope(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_torque_envelope`."""
        replacement_function = self.new_methods.calculate_torque_envelope
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def SaveResults(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_results`."""
        replacement_function = self.new_methods.save_results
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadResults(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_results`."""
        replacement_function = self.new_methods.load_results
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CalculateIMSaturationModel(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_im_saturation_model`."""
        replacement_function = self.new_methods.calculate_im_saturation_model
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateForceHarmonics_Spatial(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_force_harmonics_spatial`."""
        replacement_function = self.new_methods.calculate_force_harmonics_spatial
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateForceHarmonics_Temporal(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_force_harmonics_temporal`."""
        replacement_function = self.new_methods.calculate_force_harmonics_temporal
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def GetForceFrequencyDomainAmplitude(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_force_frequency_domain_amplitude`."""
        replacement_function = self.new_methods.get_force_frequency_domain_amplitude
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def UpdateForceAnalysisResults(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.update_force_analysis_results`."""
        replacement_function = self.new_methods.update_force_analysis_results
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def DoMultiForceCalculation(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_multi_force_calculation`."""
        replacement_function = self.new_methods.do_multi_force_calculation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoSteadyStateAnalysis(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_steady_state_analysis`."""
        replacement_function = self.new_methods.do_steady_state_analysis
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoTransientAnalysis(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_transient_analysis`."""
        replacement_function = self.new_methods.do_transient_analysis
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoMagneticCalculation(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_magnetic_calculation`."""
        replacement_function = self.new_methods.do_magnetic_calculation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoWeightCalculation(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_weight_calculation`."""
        replacement_function = self.new_methods.do_weight_calculation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def DoMechanicalCalculation(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_mechanical_calculation`."""
        replacement_function = self.new_methods.do_mechanical_calculation
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    # ------------------------------------ Lab ------------------------------------

    def CalculateTestPerformance_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_test_performance_lab`."""
        replacement_function = self.new_methods.calculate_test_performance_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ExportDutyCycle_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.export_duty_cycle_lab`."""
        replacement_function = self.new_methods.export_duty_cycle_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def GetModelBuilt_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.get_model_built_lab`."""
        replacement_function = self.new_methods.get_model_built_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ShowResultsViewer_Lab(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.show_results_viewer_lab`."""
        replacement_function = self.new_methods.show_results_viewer_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportFigure_Lab(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_figure_lab`."""
        replacement_function = self.new_methods.export_figure_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CalculateGenerator_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_generator_lab`."""
        replacement_function = self.new_methods.calculate_generator_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def LoadExternalModel_Lab(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_external_model_lab`."""
        replacement_function = self.new_methods.load_external_model_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ClearModelBuild_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_model_build_lab`."""
        replacement_function = self.new_methods.clear_model_build_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def SetMotorLABContext(self):
        """Deprecated function. Replaced by :func:`MotorCAD.set_motorlab_context`."""
        replacement_function = self.new_methods.set_motorlab_context
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def BuildModel_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.build_model_lab`."""
        replacement_function = self.new_methods.build_model_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateOperatingPoint_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_operating_point_lab`."""
        replacement_function = self.new_methods.calculate_operating_point_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateMagnetic_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_magnetic_lab`."""
        replacement_function = self.new_methods.calculate_magnetic_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateThermal_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_thermal_lab`."""
        replacement_function = self.new_methods.calculate_thermal_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CalculateDutyCycle_Lab(self):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_duty_cycle_lab`."""
        replacement_function = self.new_methods.calculate_duty_cycle_lab
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    # ------------------------------------ Geometry ------------------------------------

    def SetWindingCoil(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_winding_coil`."""
        replacement_function = self.new_methods.set_winding_coil
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetWindingCoil(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_winding_coil`."""
        replacement_function = self.new_methods.get_winding_coil
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CheckIfGeometryIsValid(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.check_if_geometry_is_valid`."""
        replacement_function = self.new_methods.check_if_geometry_is_valid
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ Graphs ------------------------------------

    def LoadMagnetisationCurves(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_magnetisation_curves`."""
        replacement_function = self.new_methods.load_magnetisation_curves
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveMagnetisationCurves(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_magnetisation_curves`."""
        replacement_function = self.new_methods.save_magnetisation_curves
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetMagneticGraphPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_magnetic_graph_point`."""
        replacement_function = self.new_methods.get_magnetic_graph_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetTemperatureGraphPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_temperature_graph_point`."""
        replacement_function = self.new_methods.get_temperature_graph_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetPowerGraphPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_power_graph_point`."""
        replacement_function = self.new_methods.get_power_graph_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetMagnetic3DGraphPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_magnetic_3d_graph_point`."""
        replacement_function = self.new_methods.get_magnetic_3d_graph_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetFEAGraphPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_fea_graph_point`."""
        replacement_function = self.new_methods.get_fea_graph_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ FEA ------------------------------------

    def SetPowerInjectionValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_power_injection_value`."""
        replacement_function = self.new_methods.set_power_injection_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetFixedTemperatureValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_fixed_temperature_value`."""
        replacement_function = self.new_methods.set_fixed_temperature_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ClearFixedTemperatureValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_fixed_temperature_value`."""
        replacement_function = self.new_methods.clear_fixed_temperature_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def DoSlotFiniteElement(self):
        """Deprecated function. Replaced by :func:`MotorCAD.do_slot_finite_element`."""
        replacement_function = self.new_methods.do_slot_finite_element
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def ClearAllData(self):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_all_data`."""
        replacement_function = self.new_methods.clear_all_data
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def AddLine_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_line_xy`."""
        replacement_function = self.new_methods.add_line_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetBndCond(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.set_bnd_cond
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def StoreProblemData(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.store_problem_data
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def Add_Region_Thermal_A(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_region_thermal_a
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddPoint_XY(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_point_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CreateOptimisedMesh(self):
        """Deprecated function. Replaced by :func:`MotorCAD.create_optimised_mesh`."""
        replacement_function = self.new_methods.create_optimised_mesh
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CreateOptimisedMesh_Thermal(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.create_optimised_mesh_thermal
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetMeshGeneratorParam(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.set_mesh_generator_param
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SolveProblem(self):
        """Deprecated function."""
        replacement_function = self.internal_methods.solve_problem
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def Add_Region_Thermal(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_region_thermal
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddCircularConductor_A(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_circular_conductor_a
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddRectangularConductor_A(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_rectangular_conductor_a
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_xy`."""
        replacement_function = self.new_methods.add_arc_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetRegionColour(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.set_region_colour
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddPoint_RT(self, *args):
        """Deprecated function."""
        replacement_function = self.internal_methods.add_point_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddLine_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_line_rt`."""
        replacement_function = self.new_methods.add_line_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_rt`."""
        replacement_function = self.new_methods.add_arc_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_Boundary_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_boundary_rt`."""
        replacement_function = self.new_methods.add_arc_boundary_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_Boundary_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_boundary_xy`."""
        replacement_function = self.new_methods.add_arc_boundary_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddLine_Boundary_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_line_boundary_rt`."""
        replacement_function = self.new_methods.add_line_boundary_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddLine_Boundary_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_line_boundary_xy`."""
        replacement_function = self.new_methods.add_line_boundary_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def InitiateGeometryFromScript(self):
        """Deprecated function. Replaced by :func:`MotorCAD.initiate_geometry_from_script`."""
        replacement_function = self.new_methods.initiate_geometry_from_script
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def AddPoint_Magnetic_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_point_magnetic_rt`."""
        replacement_function = self.internal_methods.add_point_magnetic_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddPoint_Magnetic_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_point_magnetic_xy`."""
        replacement_function = self.internal_methods.add_point_magnetic_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_CentreStartEnd_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_centre_start_end_rt`."""
        replacement_function = self.new_methods.add_arc_centre_start_end_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddArc_CentreStartEnd_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_arc_centre_start_end_xy`."""
        replacement_function = self.new_methods.add_arc_centre_start_end_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetFEAPathPoint(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_fea_path_point`."""
        replacement_function = self.new_methods.set_fea_path_point
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetFEAPathArc(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_fea_path_arc`."""
        replacement_function = self.new_methods.set_fea_path_arc
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetFEAPathLine(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_fea_path_line`."""
        replacement_function = self.new_methods.set_fea_path_line
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveFEAData(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_fea_data`."""
        replacement_function = self.new_methods.save_fea_data
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddPoint_CustomMaterial_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_point_custom_material_xy`."""
        replacement_function = self.new_methods.add_point_custom_material_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetRegionValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_region_value`."""
        replacement_function = self.new_methods.get_region_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetRegionLoss(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_region_loss`."""
        replacement_function = self.new_methods.get_region_loss
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def EditMagnetRegion(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.edit_magnet_region`."""
        replacement_function = self.new_methods.edit_magnet_region
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddRegion_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_region_xy`."""
        replacement_function = self.new_methods.add_region_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddRegion_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_region_rt`."""
        replacement_function = self.new_methods.add_region_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def DeleteRegions(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.delete_regions`."""
        replacement_function = self.new_methods.delete_regions
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ResetRegions(self):
        """Deprecated function. Replaced by :func:`MotorCAD.reset_regions`."""
        replacement_function = self.new_methods.reset_regions
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def AddMagnetRegion_RT(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_magnet_region_rt`."""
        replacement_function = self.new_methods.add_magnet_region_rt
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def AddMagnetRegion_XY(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.add_magnet_region_xy`."""
        replacement_function = self.new_methods.add_magnet_region_xy
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetPointValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_point_value`."""
        replacement_function = self.new_methods.get_point_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ Thermal ------------------------------------

    def SetResistanceValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_resistance_value`."""
        replacement_function = self.new_methods.set_resistance_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetResistanceMultiplier(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_resistance_multiplier`."""
        replacement_function = self.new_methods.set_resistance_multiplier
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ClearExternalCircuit(self):
        """Deprecated function. Replaced by :func:`MotorCAD.clear_external_circuit`."""
        replacement_function = self.new_methods.clear_external_circuit
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function()

    def CreateNewNode(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.create_new_node`."""
        replacement_function = self.new_methods.create_new_node
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ModifyNode(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.modify_node`."""
        replacement_function = self.new_methods.modify_node
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetCapacitanceValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_capacitance_value`."""
        replacement_function = self.new_methods.set_capacitance_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetPowerSourceValue(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_power_source_value`."""
        replacement_function = self.new_methods.set_power_source_value
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def LoadExternalCircuit(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.load_external_circuit`."""
        replacement_function = self.new_methods.load_external_circuit
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveExternalCircuit(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_external_circuit`."""
        replacement_function = self.new_methods.save_external_circuit
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveTransientPowerValues(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_transient_power_values`."""
        replacement_function = self.new_methods.save_transient_power_values
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveTransientTemperatures(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_transient_temperatures`."""
        replacement_function = self.new_methods.save_transient_temperatures
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def RemoveExternalComponent(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.remove_external_component`."""
        replacement_function = self.new_methods.remove_external_component
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetNodeTemperature(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_node_temperature`."""
        replacement_function = self.new_methods.get_node_temperature
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetNodeCapacitance(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_node_capacitance`."""
        replacement_function = self.new_methods.get_node_capacitance
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetNodePower(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_node_power`."""
        replacement_function = self.new_methods.get_node_power
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetNodeToNodeResistance(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_node_to_node_resistance`."""
        replacement_function = self.new_methods.get_node_to_node_resistance
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetNodeExists(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_node_exists`."""
        replacement_function = self.new_methods.get_node_exists
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetOffsetNodeNumber(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_offset_node_number`."""
        replacement_function = self.new_methods.get_offset_node_number
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    # ------------------------------------ Materials ------------------------------------

    def SetFluid(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_fluid`."""
        replacement_function = self.new_methods.set_fluid
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SetComponentMaterial(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.set_component_material`."""
        replacement_function = self.new_methods.set_component_material
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def GetComponentMaterial(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.get_component_material`."""
        replacement_function = self.new_methods.get_component_material
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ImportSolidMaterial(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.import_solid_material`."""
        replacement_function = self.new_methods.import_solid_material
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def ExportSolidMaterial(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.export_solid_material`."""
        replacement_function = self.new_methods.export_solid_material
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def DeleteSolidMaterial(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.delete_solid_material`."""
        replacement_function = self.new_methods.delete_solid_material
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CalculateIronLossCoefficients(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_iron_loss_coefficients`."""
        replacement_function = self.new_methods.calculate_iron_loss_coefficients
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveIronLossCoefficients(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_iron_loss_coefficients`."""
        replacement_function = self.new_methods.save_iron_loss_coefficients
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def CalculateMagnetParameters(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.calculate_magnet_parameters`."""
        replacement_function = self.new_methods.calculate_magnet_parameters
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)

    def SaveMagnetParameters(self, *args):
        """Deprecated function. Replaced by :func:`MotorCAD.save_magnet_parameters`."""
        replacement_function = self.new_methods.save_magnet_parameters
        deprecation_warning(_getframe().f_code.co_name, replacement_function.__name__)
        return replacement_function(*args)
