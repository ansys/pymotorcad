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

from ansys.motorcad.core.geometry_extrusion import ExtrusionBlock, ExtrusionBlockList


def test_extrusion_block_to_json():
    block_dict = {
        "extrusion_block_start": 100.1,
        "extrusion_block_end": 200.2,
        "extrusion_block_angle_step": 1.5,
        "extrusion_block_continuous_rotation": 0
    }

    block = ExtrusionBlock()
    block.start_pos = 100.1
    block.end_pos = 200.2
    block.angle_step = 1.5
    block.angle_continuous = 0

    assert block._to_json() == block_dict


def test_extrusion_block_from_json():
    block_dict = {
        "extrusion_block_start": 100,
        "extrusion_block_end": 200,
        "extrusion_block_angle_step": 0,
        "extrusion_block_continuous_rotation": 20
    }
    block = ExtrusionBlock()
    block._from_json(block_dict)
    block_actual = ExtrusionBlock(start_pos=100, end_pos=200, angle_continuous=20)

    assert block == block_actual


def test_extrusion_block_list_to_json():
    blocks_array = [
        {
            "extrusion_block_start": 100,
            "extrusion_block_end": 200,
            "extrusion_block_angle_step": 0,
            "extrusion_block_continuous_rotation": 10
        }
    ]

    blocks = ExtrusionBlockList()
    blocks.append(ExtrusionBlock(start_pos=100, end_pos=200, angle_continuous=10))

    for block_1, block_2 in zip(blocks._to_json(), blocks_array):
        assert block_1 == block_2


def test_extrusion_block_list_from_json():
    blocks_array = [
        {
            "extrusion_block_start": 100,
            "extrusion_block_end": 200,
            "extrusion_block_angle_step": 0,
            "extrusion_block_continuous_rotation": 20
        }
    ]
    blocks = ExtrusionBlockList()
    blocks._from_json(blocks_array)
    blocks_actual = ExtrusionBlockList()
    blocks_actual.append(ExtrusionBlock(start_pos=100, end_pos=200, angle_continuous=20))

    assert blocks == blocks_actual


def test_block_extrusion_length():
    block = ExtrusionBlock(start_pos=100, end_pos=200.5, angle_continuous=0)
    assert block.extrusion_length == 100.5