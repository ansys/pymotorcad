# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Motor-CAD Thermal Twin Builder ROM
=================================
This example shows how to create the files needed to generate a Motor-CAD Thermal model using the
Twin Builder *Motor-CAD ROM* component.
"""
# %%
# Background
# ----------
# .. note:: The Twin Builder *Motor-CAD ROM* component is available in Twin Builder 2024 R2 or
#    later.
#
# Motor-CAD creates a thermal model of the motor using a Lumped Parameter Thermal Network (LPTN),
# which allows the machine temperatures to be calculated. This LPTN thermal model can be formulated
# as a set of thermal matrices. Motor-CAD provides the capability to export these, allowing the
# thermal model to be imported into other engineering software packages. In general, the exported
# model is accurate at a single speed, housing temperature, and airgap temperature ("operating
# point").
#
# In Twin Builder 2024 R2 and later, a *Motor-CAD ROM* component can be created which extends upon
# this idea, allowing for the creation of a Motor-CAD thermal model that is valid at a range of
# operating points. It does this by utilizing data exported from several discrete operating points
# to generate the component, and then automatically interpolating between these during a solve. The
# component also solves the coolant flow model, ensuring accuracy for Motor-CAD models with cooling
# systems enabled.
#
# .. image:: ../../images/Thermal_Twinbuilder_TwinBuilderROM.png
#
# The *Motor-CAD ROM* component is quick to set up and provides a significantly more accurate model
# compared to the single operating point export. It has a user friendly interface with losses and
# RPM as input pins, and component temperatures as output pins. Once generated, the component is
# standalone (does not require Motor-CAD), thus allowing it to be shared/used in alternate systems
# whilst obscuring the underlying Motor-CAD geometry.

# %%
# Data required to generate a *Motor-CAD ROM* component
# ----------------------------------------
# To generate the component, within Ansys Electronics Desktop, go to the menu bar and select **Twin
# Builder** > **Add Component** > **Add Motor-CAD ROM Component...**. This will present the
# following window:
#
# .. image:: ../../images/Thermal_Twinbuilder_GenerateROM_Blank.png
#
# The **Input Files** must point to the folder which contains the Motor-CAD data at the appropriate
# operating points of interest, formatted in the appropriate manner. The script below is an example
# showing how this can be done.
#
# .. note:: This script is an example of how the data needed to generate a *Motor-CAD ROM* component
#    can be obtained. For details on how the resulting *Motor-CAD ROM* component can be used, please
#    consult the Twin Builder Help Manual.
#
# .. note:: This script is designed to be run using Motor-CAD template "e8". For other models,
#    modification of this script may be required.

# %%
# Perform required imports
# ------------------------

# sphinx_gallery_thumbnail_path = 'images/Thermal_Twinbuilder_TwinBuilderROM_Zoom.png'
import os
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

import ansys.motorcad.core as pymotorcad

# %%
# Define the required Class
# -------------------------
# A ``MotorCADTwinModel`` class has been created to encapsulate the required logic. The resulting
# object contains the data and functions to export the required Motor-CAD in the appropriate format.
# A summary of the operations performed is as follows:

# %%
# 1. The Motor-CAD model calculation settings are configured
# 2. The thermal node numbers, node names and other required node data is determined
# 3. The cooling system nodes and flow path are identified and saved to the ``CoolingSystems.csv``
#    file
# 4. For each desired speed, the thermal model is solved and thermal matrices exported and saved to
#    the ``dpxxx`` folders
# 5. The distribution of the losses onto the individual nodes is determined and saved to the
#    ``LossDistribution.csv`` file
# 6. Natural convection cooling of the Housing is characterized and saved to the
#    ``HousingTempDependency`` folder
# 7. Temperature dependent Airgap heat transfer is characterized and saved to the
#    ``AirGapTempDependency`` folder


class MotorCADTwinModel:
    # Store required constants for the Motor-CAD Node Group names (provided in the ``.nmf`` file),
    # the Motor-CAD loss names (for display in Twinbuilder), and the corresponding Motor-CAD
    # parameter names.
    coolingSystemNodeGroups = [
        "End Space",
        "Ventilated",
        "Housing Water Jacket",
        "Shaft Spiral Groove",
        "Wet Rotor",
        "Spray Cooling",
        "Rotor Water Jacket",
        "Slot Water Jacket",
        "Heat Exchanger",
    ]

    lossNames = [
        "Loss_Armature_Copper_dc",
        "Loss_Armature_Copper_Freq_Comp",
        "Loss_Main_Winding",
        "Loss_Aux_Winding",
        "Loss_Stator_Back_Iron",
        "Loss_Stator_Tooth",
        "Loss_Windage",
        "Loss_Windage_Ext_Fan",
        "Loss_Friction_F_Bearing",
        "Loss_Friction_R_Bearing",
        "Loss_Magnet",
        "Loss_Rotor_Banding",
        "Loss_Stator_Sleeve",
        "Loss_Embedded_Magnet_Pole",
        "Loss_Encoder",
        "Loss_Rotor_Back_Iron",
        "Loss_Rotor_Tooth",
        "Loss_Rotor_Copper",
        "Loss_Stray_Load_Stator_Iron",
        "Loss_Stray_Load_Rotor_Iron",
        "Loss_Stray_Load_Stator_Copper",
        "Loss_Stray_Load_Rotor_Copper",
        "Loss_Brush_Friction",
        "Loss_Brush_VI",
    ]

    lossParameters = [
        "Armature_Copper_Loss_@Ref_Speed",
        "Armature_Copper_Freq_Component_Loss_@Ref_Speed",
        "Main_Winding_Copper_Loss_@Ref_Speed",
        "Aux_Winding_Copper_Loss_@Ref_Speed",
        "Stator_Iron_Loss_@Ref_Speed_[Back_Iron]",
        "Stator_Iron_Loss_@Ref_Speed_[Tooth]",
        "Windage_Loss_@Ref_Speed",
        "Windage_Loss_(Ext_Fan)@Ref_Speed",
        "Friction_Loss_[F]_@Ref_Speed",
        "Friction_Loss_[R]_@Ref_Speed",
        "Magnet_Iron_Loss_@Ref_Speed",
        "Magnet_Banding_Loss_@Ref_Speed",
        "Stator_Bore_Sleeve_Loss_@Ref_Speed",
        "Rotor_Iron_Loss_@Ref_Speed_[Embedded_Magnet_Pole]",
        "Encoder_Loss_@Ref_Speed",
        "Rotor_Iron_Loss_@Ref_Speed_[Back_Iron]",
        "Rotor_Iron_Loss_@Ref_Speed_[Tooth]",
        "Rotor_Copper_Loss_@Ref_Speed",
        "Stator_Iron_Stray_Load_Loss_@Ref_Speed",
        "Rotor_Iron_Stray_Load_Loss_@Ref_Speed",
        "Stator_Copper_Stray_Load_Loss_@Ref_Speed",
        "Rotor_Copper_Stray_Load_Loss_@Ref_Speed",
        "Brush_Friction_Loss_@Ref_Speed",
        "Brush_VI_Loss_@Ref_Speed",
    ]
    # Stator_Iron_Loss_@Ref_Speed_[Tooth_Tip] is not included as this is an unused Motor-CAD
    # parameter

    # Initialization function for objects of this class.
    def __init__(self, inputMotFilePath: str, outputDir: str):
        self.inputMotFilePath = inputMotFilePath
        self.outputDirectory = outputDir
        if not os.path.isdir(self.outputDirectory):
            os.makedirs(self.outputDirectory)

        print("Motor-CAD input file: " + self.inputMotFilePath)
        print("TB data output dir: " + self.outputDirectory)

        self.motFileName = None

        self.nodeNames = []
        self.nodeNumbers = []
        self.nodeGroupings = []
        self.nodeNumbers_fluid = []
        self.nodeNumbers_fluidInlet = []

        self.mcad = pymotorcad.MotorCAD()
        self.mcad.set_variable("MessageDisplayState", 2)
        self.mcad.load_from_file(self.inputMotFilePath)

    # Main function to call which generates the required data for the Twin Builder export
    def generateTwinData(
        self, parameters: dict, housingAmbientTemperatures=None, airgapTemperatures=None
    ):
        self.updateMotfile()

        # calculate self.nodeNames, self.nodeNumbers, self.nodeGroupings, self.nodeNumbers_fluid,
        # and self.nodeNumbers_fluidInlet
        self.getNodeData()

        self.generateCoolingSystemNetwork()

        self.generateSamples(parameters)

        # this changes the losses in the file, so do after samples obtained
        self.generateLossDistribution()

        if housingAmbientTemperatures is not None:
            # uses fixed temperatures, so not dependent on losses
            self.generateHousingTempDependency(housingAmbientTemperatures)

        if airgapTemperatures is not None:
            # uses fixed temperatures, so not dependent on losses
            self.generateAirgapTempDependency(parameters["rpm"], airgapTemperatures)

        # write config file
        with open(os.path.join(self.outputDirectory, "config.txt"), "w") as cf:
            if housingAmbientTemperatures is not None:
                cf.write("HousingTempDependency=1\n")
            else:
                cf.write("HousingTempDependency=0\n")
            if airgapTemperatures is not None:
                cf.write("AirGapTempDependency=1\n")
            else:
                cf.write("AirGapTempDependency=0\n")
            cf.write("CopperLossScaling=0\n")
            cf.write("SpeedDependentLosses=0\n")

    # Helper functions to parse the exported Motor-CAD matrices (``.cmf``, ``.nmf``, ``.pmf``,
    # ``.rmf`` and .``.tmf``)
    def unbracket(self, string):
        val = string.replace("(", "_").replace(")", "").replace(" ", "")
        return val

    def getExportedVector(self, file):
        with open(file, "r") as f:
            lines = f.readlines()[3:]
            vector = []
            for line in lines[:-1]:
                lineSplit = line.split(";")
                vector.append(float(lineSplit[1]))
        return vector

    def getExportedMatrix(self, file):
        with open(file, "r") as f:
            lines = f.readlines()[4:]
            matrix = []
            for line in lines[:-1]:
                row = []
                lineSplit = line.split(";")
                for ind in range(1, len(lineSplit) - 1):
                    row.append(float(lineSplit[ind]))
                matrix.append(row)
        return matrix

    def getPmfData(self, exportDirectory):
        pmfFile = os.path.join(exportDirectory, self.motFileName + ".pmf")
        # exported power vector does not contain ambient, so add on
        powerVector = [0.0] + self.getExportedVector(pmfFile)
        return powerVector

    def getTmfData(self, exportDirectory):
        tmfFile = os.path.join(exportDirectory, self.motFileName + ".tmf")
        temperatureVector = self.getExportedVector(tmfFile)
        return temperatureVector

    def getRmfData(self, exportDirectory):
        rmfFile = os.path.join(exportDirectory, self.motFileName + ".rmf")
        resistanceMatrix = self.getExportedMatrix(rmfFile)
        return resistanceMatrix

    def getNmfData(self, exportDirectory):
        # obtain the node numbers, node names, and node groupings from the nmf file
        nmfFile = os.path.join(exportDirectory, self.motFileName + ".nmf")
        nodeNumbers = []
        nodeNames = []
        nodeGroupings = []
        with open(nmfFile, "r") as fid:
            groupName = ""
            lines = fid.readlines()[2:]
            for line in lines:
                if not len(line.strip()) == 0:
                    if line[0] == "[":
                        # group name found
                        groupName = line[1:-2]
                    else:
                        # node number and node name found
                        lineSplit = line.split(" ", 1)

                        nodeNumbers.append(int(lineSplit[0]))
                        nodeNames.append(lineSplit[1][1:-2])
                        nodeGroupings.append(groupName)

        # sort based on the node numbers
        return (list(t) for t in zip(*sorted(zip(nodeNumbers, nodeNames, nodeGroupings))))

    # Functions to set and get the losses in the model, used to ensure the calculations are
    # performed with the correct losses and to determine the loss distribution
    def setLosses(self, lossVector):
        for index, lossParameter in enumerate(self.lossParameters):
            self.mcad.set_variable(lossParameter, lossVector[index])

    def getLosses(self):
        lossVector = []
        for lossParameter in self.lossParameters:
            lossVector.append(self.mcad.get_variable(lossParameter))
        return lossVector

    # Functions to update any mot file settings that need to be set appropriately
    # to ensure the correct calculations performed
    def updateMotfile(self):
        # update the model settings to those needed for the TB export
        # 1 rpm
        ## N/A no need to set RPM, this is done as required
        # 2 loss values
        ## use a very small loss value
        lossVector = 0.1 * np.ones(len(self.lossParameters))
        self.setLosses(lossVector)
        # 3 speed dep losses
        self.mcad.set_variable("Speed_Dependant_Losses", 0)
        # 4 copper loss variation x2
        ## turn off any temperature scaling losses as will affect loss distribution calculation
        self.mcad.set_variable("StatorCopperLossesVaryWithTemp", 0)
        self.mcad.set_variable("RotorCopperLossesVaryWithTemp", 0)
        # 5 calculation options x3
        ## set calculation type to steadystate thermal-only (no coupling)
        self.mcad.set_variable("ThermalCalcType", 0)
        self.mcad.set_variable("MagneticThermalCoupling", 0)
        self.mcad.set_variable("LabThermalCoupling", 0)
        # 6 matrix separator
        ## export assumes comma is being used TODO use the original separator
        self.mcad.set_variable("ExportTextSeparator", ";")
        # 7 windage losses
        ## TB model will not include this logic
        self.mcad.set_variable("Windage_Loss_Definition", 0)
        # 8 bearing losses
        ## TB model will not include this logic
        self.mcad.set_variable("BearingLossSource", 0)

        # 9 Workaround for models created in Motor-CAD 2025R1 - ensure the old fluid heat flow
        # method is used
        try:
            heatFlowMethod = self.mcad.get_variable("FluidHeatFlowMethod")
            if heatFlowMethod == 1:
                # Revert model to use the old fluid heat flow method
                warnings.warn(
                    "The Improved Fluid Heat Flow Method setting in this .mot file is incompatible "
                    + "with the Twin Builder Thermal ROM. The setting has been changed from "
                    + "Improved to Original."
                )
                self.mcad.set_variable("FluidHeatFlowMethod", 0)
        except:
            # variable does not exist due to using older version of Motor-CAD
            # no need to perform any action
            pass

        # save the updated model so it is clear which Motor-CAD file can be used to validate
        # the Twin Builder Motor-CAD ROM component
        self.motFileName = Path(self.inputMotFilePath).stem + "_TwinModel"
        usedMotFilePath = os.path.join(self.outputDirectory, self.motFileName + ".mot")
        self.mcad.save_to_file(usedMotFilePath)

    # Helper function that solves the Motor-CAD thermal network and exports the matrices,
    # setting any operating-point specific required settings beforehand
    def computeMatrices(self, exportDirectory, rpm=None, lossVector=None):
        if not os.path.isdir(exportDirectory):
            os.makedirs(exportDirectory)

        if rpm is not None:
            self.mcad.set_variable("Shaft_Speed_[RPM]", rpm)

        if lossVector is not None:
            self.setLosses(lossVector)

        self.mcad.do_steady_state_analysis()
        self.mcad.export_matrices(exportDirectory)

    # Function that determines self.nodeNumbers, self.nodeNames, self.nodeGroupings,
    # self.nodeNumbers_fluidInlet and self.nodeNumbers_fluid
    def getNodeData(self):
        print("initialization : compute matrices")
        exportDirectory = os.path.join(self.outputDirectory, "tmp")
        self.computeMatrices(exportDirectory)

        self.nodeNumbers, self.nodeNames, self.nodeGroupings = self.getNmfData(exportDirectory)
        temperatureVector = self.getTmfData(exportDirectory)

        # determine which of the nodes is an inlet node
        coolingSystemsPresent = []

        for index, temperature in enumerate(temperatureVector):
            isInlet_check1 = "inlet".lower() in self.nodeNames[index].lower()
            isInlet_check2 = temperature > -10000000.0
            isInlet_check3 = self.nodeGroupings[index] in self.coolingSystemNodeGroups

            if isInlet_check1 and isInlet_check2 and isInlet_check3:
                self.nodeNumbers_fluidInlet.append(self.nodeNumbers[index])
                coolingSystemsPresent.append(self.nodeGroupings[index])

        self.nodeNumbers_fluid = [
            nodeNumber
            for (index, nodeNumber) in enumerate(self.nodeNumbers)
            if self.nodeGroupings[index] in coolingSystemsPresent
        ]

    # Function that determines the nodes used for the cooling system and their connections. The
    # resulting data is required by Twin Builder to correctly model the fluid flow
    def generateCoolingSystemNetwork(self):
        print("initialization : identifying cooling systems")
        exportDirectory = os.path.join(self.outputDirectory, "tmp")
        self.computeMatrices(exportDirectory)

        if len(self.nodeNumbers_fluid) == 0:
            print("initialization : no cooling systems found")
        else:
            print("initialization : cooling systems found")

            resistanceMatrix = self.getRmfData(exportDirectory)
            graphNodes = []
            graphEdges = []

            for node in self.nodeNumbers_fluid:
                connectedNodes = self.returnConnectedNodes(
                    node, self.nodeNumbers_fluid, resistanceMatrix
                )
                if node not in graphNodes:
                    graphNodes.append(node)
                for connectedNode in connectedNodes:
                    graphEdges.append([node, connectedNode])

            G = nx.DiGraph()
            G.add_nodes_from(graphNodes)
            G.add_edges_from(graphEdges)
            M = nx.adjacency_matrix(G).todense()

            inletNodes = []
            connectedNodesLists = []

            for graphNode in graphNodes:
                if graphNode in self.nodeNumbers_fluidInlet:
                    inletNodes.append(graphNode)

            for index, graphNode in enumerate(inletNodes):
                connectedNodesList = []

                node = graphNode
                next = []
                next.append(node)
                covered = []
                curGraphEdges = []

                while len(next) > 0:
                    node = next[0]
                    line = M[graphNodes.index(node)]
                    for k in range(0, len(line)):
                        if line[k] > 0 and graphNodes[k] not in covered:
                            # don't consider first connection for the power correction
                            if node != graphNode:
                                connectedNodesList.append(
                                    [
                                        self.unbracket(
                                            self.nodeNames[self.nodeNumbers.index(node)]
                                        ),
                                        self.unbracket(
                                            self.nodeNames[self.nodeNumbers.index(graphNodes[k])]
                                        ),
                                    ]
                                )

                            curGraphEdges.append([node, graphNodes[k]])
                            if graphNodes[k] not in next:
                                next.append(graphNodes[k])
                    next.remove(node)
                    covered.append(node)

                curG = nx.DiGraph()
                curG.add_nodes_from(graphNodes)
                curG.add_edges_from(curGraphEdges)
                connectedNodesLists.append(connectedNodesList)

                plt.figure(index)
                nx.draw(curG, with_labels=True)
                plt.savefig(os.path.join(self.outputDirectory, str(graphNode) + "_cooling.png"))

            # write cooling systems config file
            with open(os.path.join(self.outputDirectory, "CoolingSystems.csv"), "w") as outfile:
                k = 0
                for connectedNodesList in connectedNodesLists:
                    outfile.write(
                        "inlet : "
                        + str(inletNodes[k])
                        + " - "
                        + str(self.nodeNames[self.nodeNumbers.index(inletNodes[k])])
                        + "\n"
                    )
                    for connectedNodes in connectedNodesList:
                        outfile.write(str(connectedNodes) + "\n")
                    k = k + 1

    def returnConnectedNodes(self, node, nodeList, resistanceMatrix):
        nodeIndex = self.nodeNumbers.index(node)
        resistanceRow = resistanceMatrix[nodeIndex]

        connectedNodesList = []

        for index, resistance in enumerate(resistanceRow):
            if (resistance > 0) and (resistance < 1000000000.0):
                # there is a connection
                connectedNode = self.nodeNumbers[index]
                if connectedNode in nodeList:
                    connectedNodesList.append(connectedNode)

        return connectedNodesList

    # Function that runs the thermal model at each desired speed, and exports the thermal matrices
    def generateSamples(self, parameters: dict):
        rpmSamples = parameters["rpm"]

        for index, rpm in enumerate(rpmSamples):
            print("DoE : computing sample point rpm = " + str(rpm))
            exportDirectory = os.path.join(self.outputDirectory, "dp" + str(index).zfill(3))
            self.computeMatrices(exportDirectory, rpm=rpm)

        # write doe file
        with open(os.path.join(self.outputDirectory, "doe.csv"), "w") as cf:
            cf.write("Name")
            parameterNames = list(parameters.keys())
            parameterValues = list(parameters.values())
            nbDPs = len(parameterValues[0])
            for parameterName in parameterNames:
                cf.write(", " + str(parameterName))
            cf.write("\n")
            for i in range(0, nbDPs):
                cf.write("dp" + str(i).zfill(3))
                for j in range(0, len(parameterNames)):
                    cf.write(", " + str(parameterValues[j][i]))
                cf.write("\n")

    # Function that extracts the per-node loss distribution for each loss type, allowing the user to
    # specify a loss value using a name (such as Armature Copper Loss) and have Twin Builder
    # automatically distribute this amongst appropriate nodes.
    def generateLossDistribution(self):
        numLossParameters = len(self.lossNames)
        lossDistributionMatrix = np.zeros((numLossParameters, len(self.nodeNames)))

        # use a small loss value of 1W
        inputLoss = 1

        for lossIndex in range(numLossParameters):
            print(
                "power distribution "
                + str(lossIndex + 1)
                + "/"
                + str(numLossParameters)
                + " : "
                + self.lossNames[lossIndex]
            )

            exportDirectory = os.path.join(self.outputDirectory, "tmp", "dis" + str(lossIndex))

            lossVector = np.zeros(numLossParameters)
            lossVector[lossIndex] = inputLoss

            self.computeMatrices(exportDirectory, lossVector=lossVector)

            powerVector = self.getPmfData(exportDirectory)
            for nodeIndex, nodePower in enumerate(powerVector):
                # ignore nodes with negative loss (cooling systems)
                if nodePower > 0:
                    lossDistributionMatrix[lossIndex, nodeIndex] = nodePower / inputLoss

        with open(os.path.join(self.outputDirectory, "LossDistribution.csv"), "w") as outfile:
            outfile.write(" ")
            for nodeName in self.nodeNames:
                outfile.write(", " + nodeName)
            outfile.write("\n")

            for index, lossName in enumerate(self.lossNames):
                outfile.write(str(lossName))
                for nodeLoss in lossDistributionMatrix[index]:
                    outfile.write(", " + str(nodeLoss))
                outfile.write("\n")

    # Function that determines the Housing to Ambient resistances at different housing temperatures,
    # the results of which are used by Twin Builder to take into account external Natural Convection
    # cooling.
    # The input parameter is a dict, format e.g.: {tAmbient1:[tHousing1, ..., tHousingx],
    # tAmbient2:[tHousing1,..., tHousingy], tAmbient3:[tHousing1, ..., tHousingx]}
    def generateHousingTempDependency(self, housingAmbientTemperatures):
        housingNodes = [
            nodeNumber
            for (index, nodeNumber) in enumerate(self.nodeNumbers)
            if self.nodeGroupings[index] == "Housing"
        ]

        fileInd = 0
        for ambientTemperature, fixedHousingTemperatures in housingAmbientTemperatures.items():
            fileInd = fileInd + 1

            print("Tamb: " + str(ambientTemperature))
            self.mcad.set_variable("T_Ambient", ambientTemperature)
            file_content, header_line = self.computeMatricesHousingTemps(
                housingNodes, ambientTemperature, fixedHousingTemperatures
            )

            exportDirectory = os.path.join(self.outputDirectory, "HousingTempDependency")
            if not os.path.isdir(exportDirectory):
                os.makedirs(os.path.join(exportDirectory))

            with open(
                os.path.join(exportDirectory, "Housing_Temp" + str(fileInd) + ".csv"), "w"
            ) as fout:
                fout.write(str(header_line[0]))
                for el in header_line[1:]:
                    fout.write("," + str(el))
                fout.write("\n")
                for key, item in file_content.items():
                    fout.write(str(key))
                    for el in item:
                        fout.write("," + str(el))
                    fout.write("\n")

    def computeMatricesHousingTemps(
        self, housingNodes, ambientTemperature, fixedHousingTemperatures
    ):
        exportDirectory = os.path.join(self.outputDirectory, "tmp")

        file_content = dict()

        for housingTemperature in fixedHousingTemperatures:
            print("HousingTemp: " + str(housingTemperature))

            # Set the fixed temperature
            for housingNode in housingNodes:
                name = "Housing Node " + str(housingNode)
                self.mcad.set_fixed_temperature_value(name, housingNode, housingTemperature, name)

            self.computeMatrices(exportDirectory)

            resistanceMatrix = self.getRmfData(exportDirectory)
            ambientResistances = resistanceMatrix[0]

            housingResistances = []
            for housingNode in housingNodes:
                index = self.nodeNumbers.index(housingNode)
                housingResistances.append(ambientResistances[index])

            file_content.update({housingTemperature + 273.15: housingResistances})

        header_line = []
        header_line.append(ambientTemperature + 273.15)
        for housingNode in housingNodes:
            index = self.nodeNumbers.index(housingNode)
            header_line.append(self.unbracket(self.nodeNames[index]))

        return file_content, header_line

    # Function that determines the Stator to Rotor airgap resistance at different housing
    # temperatures, the results of which are used by Twin Builder to take into account the
    # temperature dependent nature of this resistance
    def generateAirgapTempDependency(self, rpmSamples, airgapTemperatures):
        fileInd = 0

        for rpm in rpmSamples:
            fileInd = fileInd + 1
            print("RPM : " + str(rpm))

            file_content = self.computeMatricesAirgapTemp(airgapTemperatures, rpm)

            exportPath = os.path.join(self.outputDirectory, "AirGapTempDependency")
            if not os.path.isdir(exportPath):
                os.makedirs(os.path.join(exportPath))

            with open(os.path.join(exportPath, "AirGap_Temp" + str(fileInd) + ".csv"), "w") as fout:
                fout.write(str(rpm) + "\n")
                for key, item in file_content.items():
                    fout.write(str(key) + "," + str(item))
                    fout.write("\n")

    def computeMatricesAirgapTemp(self, airgapTemperatures, rpm):
        exportDirectory = os.path.join(self.outputDirectory, "tmp")

        # Airgap nodes between which there is a temperature dependent resistance
        airgapNodeStator, airgapNodeRotor = self.getAirgapNodes()

        file_content = dict()

        # Loop over each airgap average temperature
        for airgapTemperature in airgapTemperatures:
            print("Air Gap average temperature: " + str(airgapTemperature))

            # Set the fixed temperature
            name = "Airgap_Stator_Node_" + str(airgapNodeStator)
            self.mcad.set_fixed_temperature_value(name, airgapNodeStator, airgapTemperature, name)
            name = "Airgap_Rotor_Node_" + str(airgapNodeRotor)
            self.mcad.set_fixed_temperature_value(name, airgapNodeRotor, airgapTemperature, name)

            self.computeMatrices(exportDirectory, rpm=rpm)
            resistanceMatrix = self.getRmfData(exportDirectory)

            index1 = self.nodeNumbers.index(airgapNodeStator)
            index2 = self.nodeNumbers.index(airgapNodeRotor)
            airgapResistance = resistanceMatrix[index1][index2]

            file_content.update({airgapTemperature + 273.15: airgapResistance})

        return file_content

    def getAirgapNodes(self):
        tVent = self.mcad.get_variable("ThroughVentilation")
        sVent = self.mcad.get_variable("SelfVentilation")
        if tVent or sVent:
            statorCoolingOnly = self.mcad.get_variable("TVent_NoAirgapFlow")
            if statorCoolingOnly == False:
                warnings.warn(
                    "Temperature dependent airgap not supported for ventilated cooling with airgap"
                    "flow"
                )

        wetrotor = self.mcad.get_variable("Wet_Rotor")
        if wetrotor:
            warnings.warn("Temperature dependent airgap not supported for wet rotor")

        axialSlices = self.mcad.get_variable("AxialSliceDefinition")
        if axialSlices > 0:
            warnings.warn("Temperature dependent airgap only supported for middle axial slice")

        sleeveThickness = self.mcad.get_variable("Sleeve_Thickness")
        if sleeveThickness > 0:
            # sleeve node present on stator side
            airgapNodeStator = 61
        else:
            airgapNodeStator = 11

        airgapNodeRotor = 12

        return airgapNodeStator, airgapNodeRotor


# %%
# Example use case
# ----------------
# Below is an example of how the above ``MotorCADTwinModel`` class can be used. The .mot file that
# will be used is the ``e8_eMobility`` template.


# %%
# The ``generateTwinData`` method accepts as an optional parameter a dictionary of Housing and
# Ambient temperatures to be investigated. This can be provided if Natural Convection cooling of the
# housing should be modelled in the Twin Builder *Motor-CAD ROM* component. For this example, a
# function has been defined to return this dictionary. As can be seen in the code comments, more
# data points are calculated when the housing and ambient temperatures are close together, as this
# is where the natural convection heat transfer coefficients vary the most.
def temperaturesHousingAmbient():
    # Consider ambient temperature as 20, 40, 65
    # For each ambient temperature run housing nodes sweep between 20 and 100 deg
    # 0<= abs(dT) <= 5 -> 0.5 deg => 10 points
    # 5 < abs(dT) <= 15 -> 1 deg => 10 points
    # 15 < abs(dT) <= 40 -> 5 deg => 5 points
    # 40 < abs(dT) -> 10 deg

    print("Determining Ambient and Housing temperatures to investigate:")
    temperatures = dict()

    ambientTemperatures = [20, 40]
    housingTemperatureMin = 20
    housingTemperatureMax = 100

    for ambientTemperature in ambientTemperatures:
        housingTemperatures = [housingTemperatureMin]
        curTemp = housingTemperatureMin
        while curTemp < housingTemperatureMax:
            curdT = abs(curTemp - ambientTemperature)
            if curdT < 5:
                dT = 0.5
            elif curdT < 15:
                dT = 1
            elif curdT < 40:
                dT = 5
            else:
                dT = 10
            curTemp = curTemp + dT
            housingTemperatures.append(curTemp)

        temperatures.update({ambientTemperature: housingTemperatures})

    print(temperatures)
    return temperatures


# %%
# Specify the input .mot file and the directory to save the output data to. For this example, the
# e8 template model will be used
working_folder = os.getcwd()
mcad_name = "e8_mobility"
inputMotFilePath = os.path.join(working_folder, mcad_name + ".mot")
outputDir = os.path.join(working_folder, "thermal_twinbuilder_" + mcad_name)

# %%
# Create the e8 input file if it does not exist already
if Path(inputMotFilePath).exists() == False:
    motorcad = pymotorcad.MotorCAD()
    motorcad.load_template("e8")
    motorcad.save_to_file(inputMotFilePath)
    motorcad.quit()

# %%
# Choose the speed points that the model should be solved at. The generated *Motor-CAD ROM*
# component will interpolate between these, so it is important to cover the complete speed range
# with the appropriate sampling in order to maintain accuracy. Three points have been chosen here to
# reduce calculation time, but in real use it is recommended that this be greater.
rpms = [200, 500, 1000]

# %%
# Specify the airgap temperatures to investigate, in order for the temperature dependent nature
# of the airgap heat transfer to be included in the *Motor-CAD ROM* component. The generated
# *Motor-CAD ROM* component will interpolate between these, so it is important to cover the complete
# expected airgap temperature range with the appropriate sampling in order to maintain accuracy.
# This parameter can be set to ``None`` should this not be required.
airgapTemps = [40, 50, 65]

# %%
# Specify the housing and ambient temperatures to investigate, in order for the natural
# convection cooling of the housing to be be included in the *Motor-CAD ROM* component. The
# generated *Motor-CAD ROM* component will interpolate between these, so it is important to cover
# the complete expected housing and ambient temperature range with the appropriate sampling in order
# to maintain accuracy. This parameter can be set to ``None`` should this not be required.
housingAmbientTemps = temperaturesHousingAmbient()

# %%
# Create a ``MotorCADTwinModel`` object, passing as arguments the path to the input .mot file as
# well as the directory to which the results should be saved.
MotorCADTwin = MotorCADTwinModel(inputMotFilePath, outputDir)

# %%
# Finally, generate the required data. This function will write the data to the directory
# specified above. The identified cooling system node flow path is automatically plotted.
MotorCADTwin.generateTwinData(
    parameters={"rpm": rpms},
    housingAmbientTemperatures=housingAmbientTemps,
    airgapTemperatures=airgapTemps,
)


# %%
# Generating the *Motor-CAD ROM* component
# ----------------------------------------
# To generate the component, within Ansys Electronics Desktop, go to the menu bar and select **Twin
# Builder** > **Add Component** > **Add Motor-CAD ROM Component...**. Under **Input Files**, press
# the ``...`` icon and choose the ``outputDir`` as specified in the previous step. Then press the
# **Generate** button.
#
# .. image:: ../../images/Thermal_Twinbuilder_GenerateROM_Filled.png
#
# Should the generation be successful, the **Log** will indicate that the SML model has been written
# and the **Select Interfaces** table will be populated.
#
# The resulting *Motor-CAD ROM* component will then be available to use.
#
# .. image:: ../../images/Thermal_Twinbuilder_TwinBuilderROM.png
#
# .. note:: For details on how the resulting *Motor-CAD ROM* component can be used, please consult
#    the Twin Builder Help Manual.
