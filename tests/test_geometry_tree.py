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


from copy import deepcopy

import pytest

from ansys.motorcad.core import MotorCAD
from ansys.motorcad.core.geometry import Coordinate, Line, Region, RegionType
from ansys.motorcad.core.methods.geometry_tree import GeometryNode, GeometryTree

mc = MotorCAD(open_new_instance=False)

mc.set_variable("MessageDisplayState", 2)
mc.set_visible(True)
mc.load_template("e9")
mc.display_screen("Geometry;Radial")

sample_json1 = {
    "regions": {
        "ArmatureSlotL1": {
            "adaptive_entities": False,
            "area": 54.1336003515254,
            "centroid": {"x": 77.6745925290051, "y": 3.69028322112561},
            "child_names": [],
            "colour": {"b": 0, "g": 255, "r": 255},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "type": "line",
                },
                {
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.8936835106122, "y": 4.25000000000002},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": 2.00000000000001,
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Copper (Pure)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Copper_Active",
            "mesh_length": 0,
            "name": "ArmatureSlotL1",
            "name_unique": "ArmatureSlotL1",
            "parent_name": "",
            "region_coordinate": {"x": 82.6541179328448, "y": 3.97003612151121},
            "region_temperature": 20,
            "region_type": "Split Slot",
            "region_type_mapped": "No type",
            "singular": True,
            "thermal_loss": 0,
            "use_in_weight_calculation": False,
            "weight_reduction_factor": 1,
        },
        "ArmatureSlotR1": {
            "adaptive_entities": False,
            "area": 54.1336003515217,
            "centroid": {"x": 77.4917542392541, "y": 6.47985645845607},
            "child_names": [],
            "colour": {"b": 0, "g": 215, "r": 255},
            "duplications": 48,
            "entities": [
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133569},
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623458},
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "line",
                },
                {
                    "end": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623458},
                    "type": "line",
                },
                {
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "start": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Copper (Pure)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Copper_Active",
            "mesh_length": 0,
            "name": "ArmatureSlotR1",
            "name_unique": "ArmatureSlotR1",
            "parent_name": "",
            "region_coordinate": {"x": 84.3322623694114, "y": 7.19305649200386},
            "region_temperature": 20,
            "region_type": "Split Slot",
            "region_type_mapped": "No type",
            "singular": True,
            "thermal_loss": 0,
            "use_in_weight_calculation": False,
            "weight_reduction_factor": 1,
        },
        "Housing": {
            "adaptive_entities": False,
            "area": 188.495559215387,
            "centroid": {"x": 119.725253764956, "y": 7.84720771818839},
            "child_names": [],
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 126, "y": 0}, "start": {"x": 114, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 124.9220525331, "y": 16.4463002197265},
                    "radius": 126,
                    "start": {"x": 126, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 113.024714196614, "y": 14.8799859130859},
                    "start": {"x": 124.9220525331, "y": 16.4463002197265},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 114, "y": 0},
                    "radius": -114,
                    "start": {"x": 113.024714196614, "y": 14.8799859130859},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Aluminium (Alloy 195 Cast)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Housing_Active",
            "mesh_length": 0,
            "name": "Housing",
            "name_unique": "Housing",
            "parent_name": "",
            "region_coordinate": {"x": 119.725253764956, "y": 7.84720771818839},
            "region_temperature": 20,
            "region_type": "Housing",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Housing_1": {
            "adaptive_entities": False,
            "area": 72.9765793490131,
            "centroid": {"x": 111.170714519021, "y": 7.28651359322089},
            "child_names": [],
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 114, "y": 0}, "start": {"x": 109, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 113.024714196614, "y": 14.8799859130859},
                    "radius": 114,
                    "start": {"x": 114, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 108.067489889745, "y": 14.2273549519856},
                    "start": {"x": 113.024714196614, "y": 14.8799859130859},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 109, "y": 0},
                    "radius": -109,
                    "start": {"x": 108.067489889745, "y": 14.2273549519856},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Aluminium (Alloy 195 Cast)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Housing_Active",
            "mesh_length": 0,
            "name": "Housing",
            "name_unique": "Housing_1",
            "parent_name": "",
            "region_coordinate": {"x": 111.170714519021, "y": 7.28651359322089},
            "region_temperature": 20,
            "region_type": "Housing",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Housing_2": {
            "adaptive_entities": False,
            "area": 136.135681655558,
            "centroid": {"x": 103.755368536621, "y": 6.80048613956137},
            "child_names": [],
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 109, "y": 0}, "start": {"x": 99, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 108.067489889745, "y": 14.2273549519856},
                    "radius": 109,
                    "start": {"x": 109, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "start": {"x": 108.067489889745, "y": 14.2273549519856},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 99, "y": 0},
                    "radius": -99,
                    "start": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Aluminium (Alloy 195 Cast)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Housing_Active",
            "mesh_length": 0,
            "name": "Housing",
            "name_unique": "Housing_2",
            "parent_name": "",
            "region_coordinate": {"x": 103.755368536621, "y": 6.80048613956137},
            "region_temperature": 20,
            "region_type": "Housing",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Impreg": {
            "adaptive_entities": False,
            "area": 97.2839971133977,
            "centroid": {"x": 77.5396239396489, "y": 5.08221545839593},
            "child_names": [],
            "colour": {"b": 48, "g": 224, "r": 48},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.2985091364678, "y": 2.5},
                    "start": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "type": "line",
                },
                {
                    "end": {"x": 84.8936835106123, "y": 2.5},
                    "start": {"x": 67.2985091364678, "y": 2.5},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.8936835106122, "y": 4.25},
                    "end": {"x": 86.6414946417131, "y": 4.3375},
                    "radius": 1.75,
                    "start": {"x": 84.8936835106123, "y": 2.5},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "radius": 86.75,
                    "start": {"x": 86.6414946417131, "y": 4.3375},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "radius": 86.75,
                    "start": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133571},
                    "end": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "radius": 1.75,
                    "start": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "start": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Impreg_Active",
            "mesh_length": 0,
            "name": "Impreg",
            "name_unique": "Impreg",
            "parent_name": "",
            "region_coordinate": {"x": 82.3420980203589, "y": 5.55860429566785},
            "region_temperature": 20,
            "region_type": "Stator Impreg",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 0.8,
        },
        "L1_1Magnet1": {
            "adaptive_entities": False,
            "area": 96.0000000000001,
            "centroid": {"x": 56.040689756688, "y": 11.8668792573194},
            "child_names": [],
            "colour": {"b": 0, "g": 212, "r": 0},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "start": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "type": "line",
                },
                {
                    "end": {"x": 53.550658345492, "y": 20.0399902666754},
                    "start": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "type": "line",
                },
                {
                    "end": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "start": {"x": 53.550658345492, "y": 20.0399902666754},
                    "type": "line",
                },
                {
                    "end": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "start": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 63.3333333333333,
                    "extrusion_block_start": 55,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 71.6666666666667,
                    "extrusion_block_start": 63.3333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 80,
                    "extrusion_block_start": 71.6666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 88.3333333333333,
                    "extrusion_block_start": 80,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 96.6666666666667,
                    "extrusion_block_start": 88.3333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 105,
                    "extrusion_block_start": 96.6666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 113.333333333333,
                    "extrusion_block_start": 105,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 121.666666666667,
                    "extrusion_block_start": 113.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 130,
                    "extrusion_block_start": 121.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 138.333333333333,
                    "extrusion_block_start": 130,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 146.666666666667,
                    "extrusion_block_start": 138.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 155,
                    "extrusion_block_start": 146.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 163.333333333333,
                    "extrusion_block_start": 155,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 171.666666666667,
                    "extrusion_block_start": 163.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 180,
                    "extrusion_block_start": 171.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 188.333333333333,
                    "extrusion_block_start": 180,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 196.666666666667,
                    "extrusion_block_start": 188.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 196.666666666667,
                },
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_angle": 37.5,
            "magnet_br_value": 1.06425,
            "magnet_magfactor": 1,
            "magnet_polarity": "N",
            "magnet_temp_coeff_method": 0,
            "material": "N30UH",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Magnet",
            "mesh_length": 0,
            "name": "L1_1Magnet1",
            "name_unique": "L1_1Magnet1",
            "parent_name": "Rotor",
            "region_coordinate": {"x": 56.040689756688, "y": 11.8668792573194},
            "region_temperature": 65,
            "region_type": "Magnet",
            "region_type_mapped": "No type",
            "singular": True,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "L1_1Magnet2": {
            "adaptive_entities": False,
            "area": 96.0000000000001,
            "centroid": {"x": 48.0179025436981, "y": 31.2356009549531},
            "child_names": [],
            "colour": {"b": 0, "g": 212, "r": 0},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "start": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "type": "line",
                },
                {
                    "end": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "start": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "type": "line",
                },
                {
                    "end": {"x": 52.03644666558, "y": 23.6956206406228},
                    "start": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "type": "line",
                },
                {
                    "end": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "start": {"x": 52.03644666558, "y": 23.6956206406228},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 63.3333333333333,
                    "extrusion_block_start": 55,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 71.6666666666667,
                    "extrusion_block_start": 63.3333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 80,
                    "extrusion_block_start": 71.6666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 88.3333333333333,
                    "extrusion_block_start": 80,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 96.6666666666667,
                    "extrusion_block_start": 88.3333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 105,
                    "extrusion_block_start": 96.6666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 113.333333333333,
                    "extrusion_block_start": 105,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 121.666666666667,
                    "extrusion_block_start": 113.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 130,
                    "extrusion_block_start": 121.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 138.333333333333,
                    "extrusion_block_start": 130,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 146.666666666667,
                    "extrusion_block_start": 138.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 155,
                    "extrusion_block_start": 146.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 163.333333333333,
                    "extrusion_block_start": 155,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 171.666666666667,
                    "extrusion_block_start": 163.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 180,
                    "extrusion_block_start": 171.666666666667,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 188.333333333333,
                    "extrusion_block_start": 180,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 196.666666666667,
                    "extrusion_block_start": 188.333333333333,
                },
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 196.666666666667,
                },
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_angle": 7.5,
            "magnet_br_value": 1.06425,
            "magnet_magfactor": 1,
            "magnet_polarity": "N",
            "magnet_temp_coeff_method": 0,
            "material": "N30UH",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Magnet",
            "mesh_length": 0,
            "name": "L1_1Magnet2",
            "name_unique": "L1_1Magnet2",
            "parent_name": "Rotor",
            "region_coordinate": {"x": 48.0179025436981, "y": 31.2356009549531},
            "region_temperature": 65,
            "region_type": "Magnet",
            "region_type_mapped": "No type",
            "singular": True,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Liner": {
            "adaptive_entities": False,
            "area": 10.983203589653,
            "centroid": {"x": 77.968913664417, "y": 5.11035259350818},
            "child_names": [],
            "colour": {"b": 0, "g": 128, "r": 0},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 84.8936835106123, "y": 2.25},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.8936835106123, "y": 4.25},
                    "end": {"x": 86.8911819461561, "y": 4.35},
                    "radius": 2,
                    "start": {"x": 84.8936835106123, "y": 2.25},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995537},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133571},
                    "end": {"x": 84.4610902121862, "y": 8.85009831408333},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995537},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623492},
                    "start": {"x": 84.4610902121862, "y": 8.85009831408333},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623492},
                    "type": "line",
                },
                {
                    "end": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "start": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133571},
                    "end": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "radius": -1.75,
                    "start": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "radius": -86.75,
                    "start": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.6414946417131, "y": 4.3375},
                    "radius": -86.75,
                    "start": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.8936835106122, "y": 4.25},
                    "end": {"x": 84.8936835106123, "y": 2.5},
                    "radius": -1.75,
                    "start": {"x": 86.6414946417131, "y": 4.3375},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.2985091364678, "y": 2.5},
                    "start": {"x": 84.8936835106123, "y": 2.5},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.2985091364678, "y": 2.5},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Slot_Liner",
            "mesh_length": 0,
            "name": "Liner",
            "name_unique": "Liner",
            "parent_name": "",
            "region_coordinate": {"x": 79.4399567850703, "y": 8.04005751741874},
            "region_temperature": 20,
            "region_type": "Stator Liner",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Rotor": {
            "adaptive_entities": False,
            "area": 1030.83508945915,
            "centroid": {"x": 48.1444344595077, "y": 19.9420777059107},
            "child_names": ["Rotor Pocket", "L1_1Magnet1", "L1_1Magnet2", "Rotor Pocket_1"],
            "colour": {"b": 240, "g": 240, "r": 0},
            "duplications": 8,
            "entities": [
                {"end": {"x": 65, "y": 0}, "start": {"x": 40, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 45.9619407771256, "y": 45.9619407771256},
                    "radius": 65,
                    "start": {"x": 65, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "start": {"x": 45.9619407771256, "y": 45.9619407771256},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 40, "y": 0},
                    "radius": -40,
                    "start": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 55,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "Laminated",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "M250-35A",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Rotor_Lam_Back_Iron",
            "mesh_length": 0,
            "name": "Rotor",
            "name_unique": "Rotor",
            "parent_name": "",
            "region_coordinate": {"x": 47.7895021472478, "y": 21.7999639468195},
            "region_temperature": 20,
            "region_type": "Rotor",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 0.97,
        },
        "Rotor Pocket": {
            "adaptive_entities": False,
            "area": 27.2374304690439,
            "centroid": {"x": 47.559936471459, "y": 31.1704313411946},
            "child_names": [],
            "colour": {"b": 240, "g": 241, "r": 241},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 43.8010694495415, "y": 38.7494760308394},
                    "start": {"x": 43.7358063534315, "y": 39.2451984615263},
                    "type": "line",
                },
                {
                    "end": {"x": 45.8894885250623, "y": 22.8863582488585},
                    "start": {"x": 43.8010694495415, "y": 38.7494760308394},
                    "type": "line",
                },
                {
                    "end": {"x": 45.9547516211724, "y": 22.3906358181716},
                    "start": {"x": 45.8894885250623, "y": 22.8863582488585},
                    "type": "line",
                },
                {
                    "centre": {"x": 48.8451677068426, "y": 24.1857684321305},
                    "end": {"x": 52.10170976169, "y": 23.1998982099359},
                    "radius": 3.4025,
                    "start": {"x": 45.9547516211724, "y": 22.3906358181716},
                    "type": "arc",
                },
                {
                    "end": {"x": 52.03644666558, "y": 23.6956206406228},
                    "start": {"x": 52.10170976169, "y": 23.1998982099359},
                    "type": "line",
                },
                {
                    "end": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "start": {"x": 52.03644666558, "y": 23.6956206406228},
                    "type": "line",
                },
                {
                    "end": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "start": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "type": "line",
                },
                {
                    "end": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "start": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "type": "line",
                },
                {
                    "end": {"x": 49.8827644939491, "y": 40.0544608532907},
                    "start": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "type": "line",
                },
                {
                    "centre": {"x": 46.9923484082789, "y": 38.2593282393317},
                    "end": {"x": 43.7358063534315, "y": 39.2451984615263},
                    "radius": 3.4025,
                    "start": {"x": 49.8827644939491, "y": 40.0544608532907},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 55,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Air (Motor-CAD model)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_RotorPocket",
            "mesh_length": 0,
            "name": "Rotor Pocket",
            "name_unique": "Rotor Pocket",
            "parent_name": "Rotor",
            "region_coordinate": {"x": 45.8272822054961, "y": 39.6065511007121},
            "region_temperature": 20,
            "region_type": "Rotor Pocket",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Rotor Pocket_1": {
            "adaptive_entities": False,
            "area": 27.2374304690439,
            "centroid": {"x": 55.6707769656374, "y": 11.5891302179014},
            "child_names": [],
            "colour": {"b": 240, "g": 241, "r": 241},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "start": {"x": 63.5952219241359, "y": 6.94966015187003},
                    "type": "line",
                },
                {
                    "end": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "start": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "type": "line",
                },
                {
                    "end": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "start": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "type": "line",
                },
                {
                    "end": {"x": 53.550658345492, "y": 20.0399902666754},
                    "start": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "type": "line",
                },
                {
                    "end": {"x": 53.2462776309876, "y": 20.436666936821},
                    "start": {"x": 53.550658345492, "y": 20.0399902666754},
                    "type": "line",
                },
                {
                    "centre": {"x": 51.6406701802695, "y": 17.4368284471355},
                    "end": {"x": 48.327486921182, "y": 16.662346076967},
                    "radius": 3.4025,
                    "start": {"x": 53.2462776309876, "y": 20.436666936821},
                    "type": "arc",
                },
                {
                    "end": {"x": 48.6318676356863, "y": 16.2656694068213},
                    "start": {"x": 48.327486921182, "y": 16.662346076967},
                    "type": "line",
                },
                {
                    "end": {"x": 58.3720504998259, "y": 3.57201596216157},
                    "start": {"x": 48.6318676356863, "y": 16.2656694068213},
                    "type": "line",
                },
                {
                    "end": {"x": 58.6764312143302, "y": 3.17533929201596},
                    "start": {"x": 58.3720504998259, "y": 3.57201596216157},
                    "type": "line",
                },
                {
                    "centre": {"x": 60.2820386650483, "y": 6.17517778170145},
                    "end": {"x": 63.5952219241359, "y": 6.94966015187003},
                    "radius": 3.4025,
                    "start": {"x": 58.6764312143302, "y": 3.17533929201596},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 55,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Air (Motor-CAD model)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_RotorPocket",
            "mesh_length": 0,
            "name": "Rotor Pocket",
            "name_unique": "Rotor Pocket_1",
            "parent_name": "Rotor",
            "region_coordinate": {"x": 61.753742604451, "y": 4.70347384229879},
            "region_temperature": 20,
            "region_type": "Rotor Pocket",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Shaft": {
            "adaptive_entities": False,
            "area": 628.318530717959,
            "centroid": {"x": 24.0007863180929, "y": 9.94145120057268},
            "child_names": [],
            "colour": {"b": 160, "g": 160, "r": 160},
            "duplications": 8,
            "entities": [
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "radius": 40,
                    "start": {"x": 40, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 0, "y": 0},
                    "start": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "type": "line",
                },
                {"end": {"x": 40, "y": 0}, "start": {"x": 0, "y": 0}, "type": "line"},
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 205,
                    "extrusion_block_start": 55,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Shaft_Active",
            "mesh_length": 0,
            "name": "Shaft",
            "name_unique": "Shaft",
            "parent_name": "",
            "region_coordinate": {"x": 24.7487373415292, "y": 10.6066017177982},
            "region_temperature": 20,
            "region_type": "Shaft",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
        "Stator": {
            "adaptive_entities": False,
            "area": 243.916173195236,
            "centroid": {"x": 86.1706272589501, "y": 5.64792130351275},
            "child_names": [],
            "colour": {"b": 16, "g": 0, "r": 240},
            "duplications": 48,
            "entities": [
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "radius": 99,
                    "start": {"x": 99, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 65.4353608506715, "y": 8.6147286865234},
                    "start": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "radius": -66,
                    "start": {"x": 65.4353608506715, "y": 8.6147286865234},
                    "type": "arc",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321394},
                    "start": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.555605986235},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321394},
                    "type": "line",
                },
                {
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "start": {"x": 67.0326906763158, "y": 6.555605986235},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133569},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": -2,
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": -87,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": -87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.8936835106122, "y": 4.25000000000002},
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "radius": -2.00000000000001,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "line",
                },
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "end": {"x": 65.939782471702, "y": 2.81870317426794},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 66, "y": 0},
                    "radius": -66,
                    "start": {"x": 65.939782471702, "y": 2.81870317426794},
                    "type": "arc",
                },
                {"end": {"x": 99, "y": 0}, "start": {"x": 66, "y": 0}, "type": "line"},
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 210,
                    "extrusion_block_start": 50,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "Laminated",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "M250-35A",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Stator_Lam_Back_Iron",
            "mesh_length": 0,
            "name": "Stator",
            "name_unique": "Stator",
            "parent_name": "",
            "region_coordinate": {"x": 97.7405934251342, "y": 6.46104651489255},
            "region_temperature": 20,
            "region_type": "Stator",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 0.97,
        },
        "StatorAir": {
            "adaptive_entities": False,
            "area": 2.96590380676454,
            "centroid": {"x": 66.4303884745974, "y": 4.35407769678662},
            "child_names": [],
            "colour": {"b": 240, "g": 240, "r": 239},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349813},
                    "start": {"x": 65.939782471702, "y": 2.81870317426794},
                    "type": "line",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321392},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349813},
                    "type": "line",
                },
                {
                    "end": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321392},
                    "type": "line",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 65.939782471702, "y": 2.81870317426794},
                    "radius": -66,
                    "start": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "type": "arc",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 210,
                    "extrusion_block_start": 50,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Air",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Air_TSupply",
            "mesh_length": 0,
            "name": "StatorAir",
            "name_unique": "StatorAir",
            "parent_name": "",
            "region_coordinate": {"x": 66.340607239476, "y": 4.60980564066148},
            "region_temperature": 20,
            "region_type": "Stator Air",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": False,
            "weight_reduction_factor": 1,
        },
        "StatorSlot": {
            "adaptive_entities": False,
            "area": 108.267200703049,
            "centroid": {"x": 77.5831733841295, "y": 5.08506983979084},
            "child_names": [],
            "colour": {"b": 16, "g": 240, "r": 240},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.8936835106122, "y": 4.25000000000002},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": 2.00000000000001,
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": 0, "y": 0},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.7221425966263, "y": 6.86720859133569},
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623481},
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623481},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "Copper (Pure)",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_Copper_Active",
            "mesh_length": 0,
            "name": "StatorSlot",
            "name_unique": "StatorSlot",
            "parent_name": "",
            "region_coordinate": {"x": 83.5757121546551, "y": 5.55860429566783},
            "region_temperature": 65,
            "region_type": "Stator Slot Area",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": False,
            "weight_reduction_factor": 1,
        },
        "StatorWedge": {
            "adaptive_entities": False,
            "area": 1.22513893654097,
            "centroid": {"x": 67.0166785354928, "y": 4.39250517759192},
            "child_names": [],
            "colour": {"b": 192, "g": 192, "r": 160},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.3148950021716, "y": 2.25},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623498},
                    "start": {"x": 67.3148950021716, "y": 2.25},
                    "type": "line",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321414},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623498},
                    "type": "line",
                },
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321414},
                    "type": "line",
                },
            ],
            "entities_internal": [],
            "entities_polyline_type": 2,
            "extrusion_blocks": [
                {
                    "extrusion_block_angle_step": 0,
                    "extrusion_block_end": 210,
                    "extrusion_block_start": 50,
                }
            ],
            "incl_region_id": True,
            "lamination_type": "",
            "linked_regions": [],
            "magnet_temp_coeff_method": 0,
            "material": "",
            "material_weight_component_type": 1,
            "material_weight_field": "Weight_Total_SlotWedge",
            "mesh_length": 0,
            "name": "StatorWedge",
            "name_unique": "StatorWedge",
            "parent_name": "",
            "region_coordinate": {"x": 67.0166785354928, "y": 4.39250517759192},
            "region_temperature": 20,
            "region_type": "Wedge",
            "region_type_mapped": "No type",
            "singular": False,
            "thermal_loss": 0,
            "use_in_weight_calculation": True,
            "weight_reduction_factor": 1,
        },
    }
}

simple_json = {
    "regions": {
        "Triangle": {
            "area": 0.5,
            "child_names": [],
            "name_unique": "Triangle",
            "centroid": {"x": 0.333333333333333, "y": 0.333333333333333},
            "colour": {"b": 0, "g": 0, "r": 0},
            "duplications": 1,
            "entities": [
                {"end": {"x": 1, "y": 0}, "start": {"x": 0, "y": 0}, "type": "line"},
                {"end": {"x": 0, "y": 1}, "start": {"x": 1, "y": 0}, "type": "line"},
                {"end": {"x": 0, "y": 0}, "start": {"x": 0, "y": 1}, "type": "line"},
            ],
            "lamination_type": "",
            "material": "air",
            "mesh_length": 0,
            "name": "Triangle",
            "on_boundary": False,
            "parent_name": "",
            "region_coordinate": {"x": 0.25, "y": 0.25},
            "region_type": "Airgap",
            "singular": False,
        }
    }
}
sample_json2 = {
    "regions": {
        "ArmatureSlotL1": {
            "area": 54.1336003515254,
            "centroid": {"x": 77.6745925290051, "y": 3.69028322112561},
            "colour": {"b": 0, "g": 255, "r": 255},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "type": "line",
                },
                {
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.89368351061226, "y": 4.25000000000003},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": 2.00000000000001,
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": 1.1368683772161603e-13, "y": -1.8181012251261564e-12},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Copper (Pure)",
            "mesh_length": 0,
            "name": "ArmatureSlotL1",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 82.6541179328448, "y": 3.97003612151121},
            "region_type": "Split Slot",
            "singular": True,
        },
        "ArmatureSlotR1": {
            "area": 54.1336003515217,
            "centroid": {"x": 77.4917542392541, "y": 6.47985645845607},
            "colour": {"b": 0, "g": 215, "r": 255},
            "duplications": 48,
            "entities": [
                {
                    "centre": {"x": -1.2789769243681803e-13, "y": 1.7390533457728452e-12},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.72214259662634, "y": 6.867208591335685},
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623458},
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "line",
                },
                {
                    "end": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623458},
                    "type": "line",
                },
                {
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "start": {"x": 67.1737928392437, "y": 4.40280299311749},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "Copper (Pure)",
            "mesh_length": 0,
            "name": "ArmatureSlotR1",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 84.3322623694114, "y": 7.19305649200386},
            "region_type": "Split Slot",
            "singular": True,
        },
        "Housing": {
            "area": 188.495559215387,
            "centroid": {"x": 119.725253764956, "y": 7.84720771818839},
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 126, "y": 0}, "start": {"x": 114, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0.0, "y": -8.668621376273222e-13},
                    "end": {"x": 124.9220525331, "y": 16.4463002197265},
                    "radius": 126,
                    "start": {"x": 126, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 113.024714196614, "y": 14.8799859130859},
                    "start": {"x": 124.9220525331, "y": 16.4463002197265},
                    "type": "line",
                },
                {
                    "centre": {"x": 0.0, "y": -2.9203306439740118e-12},
                    "end": {"x": 114, "y": 0},
                    "radius": -114,
                    "start": {"x": 113.024714196614, "y": 14.8799859130859},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Aluminium (Alloy 195 Cast)",
            "mesh_length": 0,
            "name": "Housing",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 119.725253764956, "y": 7.84720771818839},
            "region_type": "Housing",
            "singular": False,
        },
        "Housing_1": {
            "area": 72.9765793490131,
            "centroid": {"x": 111.170714519021, "y": 7.28651359322089},
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 114, "y": 0}, "start": {"x": 109, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0.0, "y": -2.8919089345436078e-12},
                    "end": {"x": 113.024714196614, "y": 14.8799859130859},
                    "radius": 114,
                    "start": {"x": 114, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 108.067489889745, "y": 14.2273549519856},
                    "start": {"x": 113.024714196614, "y": 14.8799859130859},
                    "type": "line",
                },
                {
                    "centre": {"x": 0.0, "y": -2.5712765250318625e-12},
                    "end": {"x": 109, "y": 0},
                    "radius": -109,
                    "start": {"x": 108.067489889745, "y": 14.2273549519856},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Aluminium (Alloy 195 Cast)",
            "mesh_length": 0,
            "name": "Housing",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 111.170714519021, "y": 7.28651359322089},
            "region_type": "Housing",
            "singular": False,
        },
        "Housing_2": {
            "area": 136.135681655558,
            "centroid": {"x": 103.755368536621, "y": 6.80048613956137},
            "colour": {"b": 253, "g": 231, "r": 229},
            "duplications": 48,
            "entities": [
                {"end": {"x": 109, "y": 0}, "start": {"x": 99, "y": 0}, "type": "line"},
                {
                    "centre": {"x": -1.4210854715202004e-14, "y": -2.5446311724408588e-12},
                    "end": {"x": 108.067489889745, "y": 14.2273549519856},
                    "radius": 109,
                    "start": {"x": 109, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "start": {"x": 108.067489889745, "y": 14.2273549519856},
                    "type": "line",
                },
                {
                    "centre": {"x": 0.0, "y": -2.7000623958883807e-13},
                    "end": {"x": 99, "y": 0},
                    "radius": -99,
                    "start": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Aluminium (Alloy 195 Cast)",
            "mesh_length": 0,
            "name": "Housing",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 103.755368536621, "y": 6.80048613956137},
            "region_type": "Housing",
            "singular": False,
        },
        "Impreg": {
            "area": 97.2839971133977,
            "centroid": {"x": 77.5396239396489, "y": 5.08221545839593},
            "colour": {"b": 48, "g": 224, "r": 48},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.2985091364678, "y": 2.5},
                    "start": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "type": "line",
                },
                {
                    "end": {"x": 84.8936835106123, "y": 2.5},
                    "start": {"x": 67.2985091364678, "y": 2.5},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.89368351061225, "y": 4.25},
                    "end": {"x": 86.6414946417131, "y": 4.3375},
                    "radius": 1.75,
                    "start": {"x": 84.8936835106123, "y": 2.5},
                    "type": "arc",
                },
                {
                    "centre": {"x": -1.8474111129762605e-13, "y": 3.5207392556912964e-12},
                    "end": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "radius": 86.75,
                    "start": {"x": 86.6414946417131, "y": 4.3375},
                    "type": "arc",
                },
                {
                    "centre": {"x": 4.263256414560601e-14, "y": -1.0391687510491465e-13},
                    "end": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "radius": 86.75,
                    "start": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.72214259662638, "y": 6.867208591335713},
                    "end": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "radius": 1.75,
                    "start": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "start": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "",
            "mesh_length": 0,
            "name": "Impreg",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 82.3420980203589, "y": 5.55860429566785},
            "region_type": "Stator Impreg",
            "singular": False,
        },
        "L1_1Magnet1": {
            "area": 96.0000000000001,
            "centroid": {"x": 56.040689756688, "y": 11.8668792573194},
            "colour": {"b": 0, "g": 212, "r": 0},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "start": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "type": "line",
                },
                {
                    "end": {"x": 53.550658345492, "y": 20.0399902666754},
                    "start": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "type": "line",
                },
                {
                    "end": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "start": {"x": 53.550658345492, "y": 20.0399902666754},
                    "type": "line",
                },
                {
                    "end": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "start": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "N30UH",
            "mesh_length": 0,
            "name": "L1_1Magnet1",
            "on_boundary": False,
            "parent_name": "Rotor",
            "region_coordinate": {"x": 56.040689756688, "y": 11.8668792573194},
            "region_type": "Magnet",
            "singular": True,
        },
        "L1_1Magnet2": {
            "area": 96.0000000000001,
            "centroid": {"x": 48.0179025436981, "y": 31.2356009549531},
            "colour": {"b": 0, "g": 212, "r": 0},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "start": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "type": "line",
                },
                {
                    "end": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "start": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "type": "line",
                },
                {
                    "end": {"x": 52.03644666558, "y": 23.6956206406228},
                    "start": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "type": "line",
                },
                {
                    "end": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "start": {"x": 52.03644666558, "y": 23.6956206406228},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "N30UH",
            "mesh_length": 0,
            "name": "L1_1Magnet2",
            "on_boundary": False,
            "parent_name": "Rotor",
            "region_coordinate": {"x": 48.0179025436981, "y": 31.2356009549531},
            "region_type": "Magnet",
            "singular": True,
        },
        "Liner": {
            "area": 10.983203589653,
            "centroid": {"x": 77.968913664417, "y": 5.11035259350818},
            "colour": {"b": 0, "g": 128, "r": 0},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 84.8936835106123, "y": 2.25},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.89368351061228, "y": 4.25},
                    "end": {"x": 86.8911819461561, "y": 4.35},
                    "radius": 2,
                    "start": {"x": 84.8936835106123, "y": 2.25},
                    "type": "arc",
                },
                {
                    "centre": {"x": 1.1368683772161603e-13, "y": -1.7896795156957523e-12},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35},
                    "type": "arc",
                },
                {
                    "centre": {"x": -1.2789769243681803e-13, "y": 1.865174681370263e-12},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995537},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.72214259662634, "y": 6.867208591335713},
                    "end": {"x": 84.4610902121862, "y": 8.85009831408333},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995537},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623492},
                    "start": {"x": 84.4610902121862, "y": 8.85009831408333},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623492},
                    "type": "line",
                },
                {
                    "end": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "start": {"x": 67.0490765420196, "y": 6.30560598623492},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.72214259662638, "y": 6.867208591335713},
                    "end": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "radius": -1.75,
                    "start": {"x": 84.4937217602412, "y": 8.60223709873987},
                    "type": "arc",
                },
                {
                    "centre": {"x": 4.263256414560601e-14, "y": -1.2523315717771766e-13},
                    "end": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "radius": -86.75,
                    "start": {"x": 86.4664220030275, "y": 7.00859229762791},
                    "type": "arc",
                },
                {
                    "centre": {"x": -1.8474111129762605e-13, "y": 3.4994229736184934e-12},
                    "end": {"x": 86.6414946417131, "y": 4.3375},
                    "radius": -86.75,
                    "start": {"x": 86.5642615909489, "y": 5.67372146071491},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.89368351061225, "y": 4.25},
                    "end": {"x": 84.8936835106123, "y": 2.5},
                    "radius": -1.75,
                    "start": {"x": 86.6414946417131, "y": 4.3375},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.2985091364678, "y": 2.5},
                    "start": {"x": 84.8936835106123, "y": 2.5},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.2985091364678, "y": 2.5},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "",
            "mesh_length": 0,
            "name": "Liner",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 79.4399567850703, "y": 8.04005751741874},
            "region_type": "Stator Liner",
            "singular": False,
        },
        "Rotor": {
            "area": 1030.83508945915,
            "centroid": {"x": 48.1444344595077, "y": 19.9420777059107},
            "colour": {"b": 240, "g": 240, "r": 0},
            "duplications": 8,
            "entities": [
                {"end": {"x": 65, "y": 0}, "start": {"x": 40, "y": 0}, "type": "line"},
                {
                    "centre": {"x": 0.0, "y": 1.0658141036401503e-14},
                    "end": {"x": 45.9619407771256, "y": 45.9619407771256},
                    "radius": 65,
                    "start": {"x": 65, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "start": {"x": 45.9619407771256, "y": 45.9619407771256},
                    "type": "line",
                },
                {
                    "centre": {"x": 0.0, "y": -5.329070518200751e-15},
                    "end": {"x": 40, "y": 0},
                    "radius": -40,
                    "start": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "M250-35A",
            "mesh_length": 0,
            "name": "Rotor",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 47.7895021472478, "y": 21.7999639468195},
            "region_type": "Rotor",
            "singular": False,
        },
        "Rotor Pocket": {
            "area": 27.2374304690439,
            "centroid": {"x": 47.559936471459, "y": 31.1704313411946},
            "colour": {"b": 240, "g": 241, "r": 241},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 43.8010694495415, "y": 38.7494760308394},
                    "start": {"x": 43.7358063534315, "y": 39.2451984615263},
                    "type": "line",
                },
                {
                    "end": {"x": 45.8894885250623, "y": 22.8863582488585},
                    "start": {"x": 43.8010694495415, "y": 38.7494760308394},
                    "type": "line",
                },
                {
                    "end": {"x": 45.9547516211724, "y": 22.3906358181716},
                    "start": {"x": 45.8894885250623, "y": 22.8863582488585},
                    "type": "line",
                },
                {
                    "centre": {"x": 48.84516770684258, "y": 24.185768432130544},
                    "end": {"x": 52.10170976169, "y": 23.1998982099359},
                    "radius": 3.4025,
                    "start": {"x": 45.9547516211724, "y": 22.3906358181716},
                    "type": "arc",
                },
                {
                    "end": {"x": 52.03644666558, "y": 23.6956206406228},
                    "start": {"x": 52.10170976169, "y": 23.1998982099359},
                    "type": "line",
                },
                {
                    "end": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "start": {"x": 52.03644666558, "y": 23.6956206406228},
                    "type": "line",
                },
                {
                    "end": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "start": {"x": 46.0877774973371, "y": 22.9124634873025},
                    "type": "line",
                },
                {
                    "end": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "start": {"x": 43.9993584218163, "y": 38.7755812692834},
                    "type": "line",
                },
                {
                    "end": {"x": 49.8827644939491, "y": 40.0544608532907},
                    "start": {"x": 49.9480275900591, "y": 39.5587384226037},
                    "type": "line",
                },
                {
                    "centre": {"x": 46.99234840827894, "y": 38.259328239331715},
                    "end": {"x": 43.7358063534315, "y": 39.2451984615263},
                    "radius": 3.4025,
                    "start": {"x": 49.8827644939491, "y": 40.0544608532907},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Air (Motor-CAD model)",
            "mesh_length": 0,
            "name": "Rotor Pocket",
            "on_boundary": False,
            "parent_name": "Rotor",
            "region_coordinate": {"x": 45.8272822054961, "y": 39.6065511007121},
            "region_type": "Rotor Pocket",
            "singular": False,
        },
        "Rotor Pocket_1": {
            "area": 27.2374304690439,
            "centroid": {"x": 55.6707769656374, "y": 11.5891302179014},
            "colour": {"b": 240, "g": 241, "r": 241},
            "duplications": 8,
            "entities": [
                {
                    "end": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "start": {"x": 63.5952219241359, "y": 6.94966015187003},
                    "type": "line",
                },
                {
                    "end": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "start": {"x": 63.2908412096315, "y": 7.34633682201565},
                    "type": "line",
                },
                {
                    "end": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "start": {"x": 58.5307211678841, "y": 3.69376824796331},
                    "type": "line",
                },
                {
                    "end": {"x": 53.550658345492, "y": 20.0399902666754},
                    "start": {"x": 48.7905383037446, "y": 16.3874216926231},
                    "type": "line",
                },
                {
                    "end": {"x": 53.2462776309876, "y": 20.436666936821},
                    "start": {"x": 53.550658345492, "y": 20.0399902666754},
                    "type": "line",
                },
                {
                    "centre": {"x": 51.64067018026958, "y": 17.436828447135458},
                    "end": {"x": 48.327486921182, "y": 16.662346076967},
                    "radius": 3.4025,
                    "start": {"x": 53.2462776309876, "y": 20.436666936821},
                    "type": "arc",
                },
                {
                    "end": {"x": 48.6318676356863, "y": 16.2656694068213},
                    "start": {"x": 48.327486921182, "y": 16.662346076967},
                    "type": "line",
                },
                {
                    "end": {"x": 58.3720504998259, "y": 3.57201596216157},
                    "start": {"x": 48.6318676356863, "y": 16.2656694068213},
                    "type": "line",
                },
                {
                    "end": {"x": 58.6764312143302, "y": 3.17533929201596},
                    "start": {"x": 58.3720504998259, "y": 3.57201596216157},
                    "type": "line",
                },
                {
                    "centre": {"x": 60.28203866504834, "y": 6.175177781701426},
                    "end": {"x": 63.5952219241359, "y": 6.94966015187003},
                    "radius": 3.4025,
                    "start": {"x": 58.6764312143302, "y": 3.17533929201596},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Air (Motor-CAD model)",
            "mesh_length": 0,
            "name": "Rotor Pocket",
            "on_boundary": False,
            "parent_name": "Rotor",
            "region_coordinate": {"x": 61.753742604451, "y": 4.70347384229879},
            "region_type": "Rotor Pocket",
            "singular": False,
        },
        "Shaft": {
            "area": 628.318530717959,
            "centroid": {"x": 24.0007863180929, "y": 9.94145120057268},
            "colour": {"b": 160, "g": 160, "r": 160},
            "duplications": 8,
            "entities": [
                {
                    "centre": {"x": -7.105427357601002e-15, "y": 1.7763568394002505e-15},
                    "end": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "radius": 40,
                    "start": {"x": 40, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 0, "y": 0},
                    "start": {"x": 28.2842712474619, "y": 28.2842712474619},
                    "type": "line",
                },
                {"end": {"x": 40, "y": 0}, "start": {"x": 0, "y": 0}, "type": "line"},
            ],
            "lamination_type": "",
            "material": "",
            "mesh_length": 0,
            "name": "Shaft",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 24.7487373415292, "y": 10.6066017177982},
            "region_type": "Shaft",
            "singular": False,
        },
        "Stator": {
            "area": 243.916173195236,
            "centroid": {"x": 86.1706272589501, "y": 5.64792130351275},
            "colour": {"b": 16, "g": 0, "r": 240},
            "duplications": 48,
            "entities": [
                {
                    "centre": {"x": 0.0, "y": -2.469136006766348e-13},
                    "end": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "radius": 99,
                    "start": {"x": 99, "y": 0},
                    "type": "arc",
                },
                {
                    "end": {"x": 65.4353608506715, "y": 8.6147286865234},
                    "start": {"x": 98.1530412760072, "y": 12.9220930297851},
                    "type": "line",
                },
                {
                    "centre": {"x": -7.105427357601002e-14, "y": 7.123190925995004e-13},
                    "end": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "radius": -66,
                    "start": {"x": 65.4353608506715, "y": 8.6147286865234},
                    "type": "arc",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321394},
                    "start": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.555605986235},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321394},
                    "type": "line",
                },
                {
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "start": {"x": 67.0326906763158, "y": 6.555605986235},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.72214259662634, "y": 6.867208591335685},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": -2,
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "arc",
                },
                {
                    "centre": {"x": -1.1368683772161603e-13, "y": 1.7177370637000422e-12},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": -87,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "centre": {"x": 1.1368683772161603e-13, "y": -1.8394175071989594e-12},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": -87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.89368351061226, "y": 4.25000000000003},
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "radius": -2.00000000000001,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "line",
                },
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "end": {"x": 65.939782471702, "y": 2.81870317426794},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "type": "line",
                },
                {
                    "centre": {"x": 1.4210854715202004e-14, "y": 1.2376766278521245e-12},
                    "end": {"x": 66, "y": 0},
                    "radius": -66,
                    "start": {"x": 65.939782471702, "y": 2.81870317426794},
                    "type": "arc",
                },
                {"end": {"x": 99, "y": 0}, "start": {"x": 66, "y": 0}, "type": "line"},
            ],
            "lamination_type": "",
            "material": "M250-35A",
            "mesh_length": 0,
            "name": "Stator",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 97.7405934251342, "y": 6.46104651489255},
            "region_type": "Stator",
            "singular": False,
        },
        "StatorAir": {
            "area": 2.96590380676454,
            "centroid": {"x": 66.4303884745974, "y": 4.35407769678662},
            "colour": {"b": 240, "g": 240, "r": 239},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349813},
                    "start": {"x": 65.939782471702, "y": 2.81870317426794},
                    "type": "line",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321392},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349813},
                    "type": "line",
                },
                {
                    "end": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321392},
                    "type": "line",
                },
                {
                    "centre": {"x": 1.1368683772161603e-13, "y": -1.5827339439056232e-12},
                    "end": {"x": 65.939782471702, "y": 2.81870317426794},
                    "radius": -66,
                    "start": {"x": 65.7435730840115, "y": 5.81227994398376},
                    "type": "arc",
                },
            ],
            "lamination_type": "",
            "material": "Air",
            "mesh_length": 0,
            "name": "StatorAir",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 66.340607239476, "y": 4.60980564066148},
            "region_type": "Stator Air",
            "singular": False,
        },
        "StatorSlot": {
            "area": 108.267200703049,
            "centroid": {"x": 77.5831733841295, "y": 5.08506983979084},
            "colour": {"b": 16, "g": 240, "r": 240},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "start": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "type": "line",
                },
                {
                    "centre": {"x": 84.89368351061226, "y": 4.25000000000003},
                    "end": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "radius": 2.00000000000001,
                    "start": {"x": 84.8936835106123, "y": 2.25000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": 1.1368683772161603e-13, "y": -1.8181012251261564e-12},
                    "end": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "radius": 87,
                    "start": {"x": 86.8911819461561, "y": 4.35000000000002},
                    "type": "arc",
                },
                {
                    "centre": {"x": -1.2789769243681803e-13, "y": 1.7390533457728452e-12},
                    "end": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "radius": 87,
                    "start": {"x": 86.8137263217585, "y": 5.69007224302245},
                    "type": "arc",
                },
                {
                    "centre": {"x": 84.72214259662634, "y": 6.867208591335685},
                    "end": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "radius": 2,
                    "start": {"x": 86.7156047753705, "y": 7.02878996995535},
                    "type": "arc",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623481},
                    "start": {"x": 84.4610902121862, "y": 8.8500983140833},
                    "type": "line",
                },
                {
                    "end": {"x": 67.3148950021716, "y": 2.24999999999998},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623481},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "Copper (Pure)",
            "mesh_length": 0,
            "name": "StatorSlot",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 83.5757121546551, "y": 5.55860429566783},
            "region_type": "Stator Slot Area",
            "singular": False,
        },
        "StatorWedge": {
            "area": 1.22513893654097,
            "centroid": {"x": 67.0166785354928, "y": 4.39250517759192},
            "colour": {"b": 192, "g": 192, "r": 160},
            "duplications": 48,
            "entities": [
                {
                    "end": {"x": 67.3148950021716, "y": 2.25},
                    "start": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "type": "line",
                },
                {
                    "end": {"x": 67.0326906763158, "y": 6.55560598623498},
                    "start": {"x": 67.3148950021716, "y": 2.25},
                    "type": "line",
                },
                {
                    "end": {"x": 66.7414320072501, "y": 5.87768307321414},
                    "start": {"x": 67.0326906763158, "y": 6.55560598623498},
                    "type": "line",
                },
                {
                    "end": {"x": 66.9376413949405, "y": 2.88410630349807},
                    "start": {"x": 66.7414320072501, "y": 5.87768307321414},
                    "type": "line",
                },
            ],
            "lamination_type": "",
            "material": "",
            "mesh_length": 0,
            "name": "StatorWedge",
            "on_boundary": False,
            "parent_name": "root",
            "region_coordinate": {"x": 67.0166785354928, "y": 4.39250517759192},
            "region_type": "Wedge",
            "singular": False,
        },
    }
}

sample_tree = GeometryTree.from_json(mc.get_geometry_tree())


def get_simple_tree():
    """Return a simple GeometryTree for the purposes of testing"""
    p1 = Coordinate(0, 0)
    p2 = Coordinate(1, 0)
    p3 = Coordinate(0, 1)
    line1 = Line(p1, p2)
    line2 = Line(p2, p3)
    line3 = Line(p3, p1)
    triangle = Region(region_type=RegionType.airgap)
    triangle.__class__ = GeometryNode
    triangle.entities.append(line1)
    triangle.entities.append(line2)
    triangle.entities.append(line3)
    triangle.name = "Triangle"
    triangle.key = "Triangle"
    triangle.children = []

    tree = GeometryTree()

    triangle.parent = tree["root"]
    tree["root"].children.append(triangle)
    tree["Triangle"] = triangle

    return tree


def test_get_json():
    test_json = mc.get_geometry_tree()
    assert test_json == sample_json1


def test_from_json():
    test_tree = get_simple_tree()
    assert test_tree == GeometryTree.from_json(simple_json)


def test_to_json():
    test_json = sample_tree.to_json()
    assert test_json == sample_json2


def test_get_node():
    assert sample_tree.get_node("rotor") == sample_tree["Rotor"]


def test_add_node():
    # Tests the basic functionality of adding a node
    test_tree = deepcopy(get_simple_tree())
    new_node = GeometryNode(parent=test_tree["root"])
    new_node.name = "node"
    new_node.key = "node"
    test_tree["node"] = new_node

    function_tree = deepcopy(get_simple_tree())
    new_node2 = GeometryNode(parent=function_tree["root"])
    new_node2.name = "node"
    function_tree.add_node(new_node2)

    assert test_tree == function_tree


def test_add_node_with_children():
    # Tests the parent and child reassignment performed when including those values
    test_tree = deepcopy(get_simple_tree())
    new_node = GeometryNode()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "node"
    new_node.key = "node"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["node"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(get_simple_tree())
    new_node2 = Region()
    new_node2.name = "node"
    function_tree.add_node(new_node2, parent="root", children=["Triangle"])

    assert test_tree == function_tree


def test_add_node_with_children_2():
    # Same test as above, but testing different mode of function input
    test_tree = deepcopy(get_simple_tree())
    new_node = GeometryNode()
    new_node.parent = test_tree["root"]
    new_node.children.append(test_tree["Triangle"])
    new_node.name = "node"
    new_node.key = "node1"
    test_tree["root"].children.remove(test_tree["Triangle"])
    test_tree["root"].children.append(new_node)
    test_tree["node1"] = new_node
    test_tree["Triangle"].parent = new_node

    function_tree = deepcopy(get_simple_tree())
    new_node2 = Region()
    new_node2.name = "node"
    function_tree.add_node(
        new_node2, parent=function_tree["root"], children=[function_tree["Triangle"]], key="node1"
    )

    assert test_tree == function_tree


def test_add_node_errors():
    function_tree = deepcopy(get_simple_tree())
    new_node2 = Region()
    new_node2.name = "node"

    with pytest.raises(TypeError, match="Parent must be a GeometryNode or str"):
        function_tree.add_node(new_node2, parent=0)

    with pytest.raises(TypeError, match="Children must be a GeometryNode or str"):
        function_tree.add_node(new_node2, children=[0, "root"])


def test_remove_node():
    test_tree = deepcopy(sample_tree)
    magnet = test_tree["L1_1Magnet1"]
    test_tree["Rotor"].children.remove(magnet)
    test_tree.pop("L1_1Magnet1")

    function_tree = deepcopy(sample_tree)
    function_tree.remove_node("L1_1Magnet1")
    assert test_tree == function_tree


def test_remove_branch():
    test_tree = deepcopy(sample_tree)
    test_tree["root"].children.remove(test_tree["Rotor"])
    for child_key in test_tree["Rotor"].child_keys:
        test_tree.pop(child_key)
    test_tree.pop("Rotor")

    function_tree = deepcopy(sample_tree)
    function_tree.remove_branch("Rotor")

    assert test_tree == function_tree


def test_remove_branch2():
    # Same test, slightly different function input
    test_tree1 = deepcopy(sample_tree)
    test_tree1["root"].children.remove(test_tree1["Rotor"])
    for child_key in test_tree1["Rotor"].child_keys:
        test_tree1.pop(child_key)
    test_tree1.pop("Rotor")

    test_tree2 = deepcopy(sample_tree)
    test_tree2.remove_branch(test_tree2["Rotor"])

    assert test_tree1 == test_tree2


def test_get_parent():
    test_tree = get_simple_tree()

    assert test_tree["root"] == test_tree["Triangle"].parent

    assert test_tree["root"].key == test_tree["Triangle"].parent_key

    assert test_tree["root"].name == test_tree["Triangle"].parent_name


def test_get_children():
    test_tree = get_simple_tree()

    assert test_tree["root"].children == [test_tree["Triangle"]]

    assert test_tree["root"].child_names == ["Triangle"]

    assert test_tree["root"].child_keys == ["Triangle"]
