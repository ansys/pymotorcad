# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

from RPC_Test_Common import almost_equal_percentage, get_dir_path


def test_winding_stranded(mc):
    # Starting from the e9 template, change a bunch of winding parameters
    mc.load_template("e9")
    mc.set_variable("SlotType", 2)
    mc.set_variable("Armature_WindingType", 1)

    # Set rectangular winding definition.
    mc.set_variable("Wire_Type_Stator", 3)
    mc.set_variable("Copper_Width", 0.75)
    mc.set_variable("Copper_Height", 0.65)
    mc.set_variable("Copper_Corner_Radius", 0.2)
    mc.set_variable("Insulation_Thickness", 0.05)
    mc.set_variable("NumberStrandsHand", 14)

    mc.set_variable("Liner_Thickness", 0.15)
    mc.set_variable("Copper_Depth_[%]", 90)
    mc.set_variable("ConductorSeparation", 0.01)
    mc.set_variable("Coil_Divider_Width", 2.2)
    mc.set_variable("CoilDivider_DepthReduction_Stator", 3)

    mc.create_winding_pattern()

    # Compare outputs against UI results
    ui_dict = {
        "WIRE_SLOT_FILL_(WDG_AREA)": 0.5918,
        "SLOT_FILL_(SLOT_AREA)": 0.3552,
        "GrossSlotFillFactor": 0.2757,
        "WINDING_DEPTH": 16.948,
        "Area_CoilDivider": 30.69,
        "Area_Covered_Wire_Total": 49.04,
        "Area_Wire_Ins_Total": 10.9776,
        "Wire_Copper_Factor": 0.81713,
        "Volume_Copper_Active": 416922,
        "Volume_WireIns_A": 93302.58,
        "Weight_Internal_Calc_Copper_Total": 5.801,
    }
    auto_dict = {param: mc.get_variable(param) for param in ui_dict.keys()}

    for param in ui_dict.keys():
        assert almost_equal_percentage(ui_dict[param], auto_dict[param], 10)


def test_winding_hairpin(mc):
    # Starting from the e2 template, change a bunch of winding parameters
    mc.load_template("e2")
    mc.set_variable("Armature_WindingType", 3)  # solid rect upper/lower

    # Set rectangular winding definition.
    mc.set_variable("Armature_Winding_Definition_Hairpin", 1)
    mc.set_variable("ConductorHeightRatio", 0.16)
    mc.set_variable("Liner_Wire_Gap", 0.2)
    mc.set_variable("Copper_Corner_Radius", 0.2)
    mc.set_variable("Insulation_Thickness", 0.15)

    mc.set_variable("Liner_Thickness", 0.25)
    mc.set_variable("Copper_Depth_[%]", 90)
    mc.set_variable("ConductorSeparation", 0.1)
    mc.set_variable("Coil_Divider_Width", 2.4)
    mc.set_variable("CoilDividerOffset", 0.2)

    mc.create_winding_pattern()

    # Compare outputs against UI results
    ui_dict = {
        "WIRE_SLOT_FILL_(WDG_AREA)": 0.8428,
        "SLOT_FILL_(SLOT_AREA)": 0.5976,
        "GrossSlotFillFactor": 0.5045,
        "WINDING_DEPTH": 21.672,
        "Area_CoilDivider": 12,
        "Area_Covered_Wire_Total": 81.22,
        "Area_Wire_Ins_Total": 12.653,
        "Wire_Copper_Factor": 0.9032,
        "Volume_Copper_Active": 427248,
        "Volume_WireIns_A": 457912,
        "Weight_Internal_Calc_Copper_Total": 7.2446,
    }
    auto_dict = {param: mc.get_variable(param) for param in ui_dict.keys()}

    for param in ui_dict.keys():
        assert almost_equal_percentage(ui_dict[param], auto_dict[param], 10)


def test_winding_IM1PH(mc):
    # Load default IM1PH file as there is no template.
    default_file = get_dir_path() + r"\test_files\default_IM1PH.mot"
    mc.load_from_file(default_file)

    mc.set_variable("AWG_WireGaugeIndex", 53)
    mc.set_variable("AWG_WireGaugeIndex_Aux", 50)
    mc.set_variable("NumberStrandsHand", 2)
    mc.set_variable("NumberStrandsHand_Aux", 2)
    mc.set_variable("Liner_Thickness", 0.15)
    mc.set_variable("Copper_Depth_[%]", 90)
    mc.set_variable("ConductorSeparation", 0.2)
    mc.create_winding_pattern()

    # Compare outputs against UI results
    ui_dict = {
        "WIRE_SLOT_FILL_(WDG_AREA)": 0.0949,
        "SLOT_FILL_(SLOT_AREA)": 0.0813,
        "GrossSlotFillFactor": 0.0632,
        "WINDING_DEPTH": 14.348,
        "Area_Covered_Wire_Total": 11.71,
        "Area_Wire_Ins_Total": 2.6076,
        "Wire_Copper_Factor": 0.77728,
        "Volume_Copper_Active": 13104.8,
        "Volume_Copper_Active_Aux": 18450.16,
        "Volume_WireIns_A": 4693.7,
        "Weight_Internal_Calc_Copper_Total": 0.577065,
    }
    auto_dict = {param: mc.get_variable(param) for param in ui_dict.keys()}

    for param in ui_dict.keys():
        assert almost_equal_percentage(ui_dict[param], auto_dict[param], 10)
