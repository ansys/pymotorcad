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

class ExtrusionBlock:
    """Generic class for storing 3D extrusion data."""

    def __init__(self, start_pos=0, end_pos=0, angle_step=0, angle_continuous=0):
        """Initialise extrusion block."""
        self._start_pos = start_pos
        self._end_pos = end_pos
        self._angle_step = angle_step
        self._angle_continuous = angle_continuous

    def __eq__(self, other):
        """Compare equality of 2 ExtrusionBlock objects."""
        return (
            isinstance(other, ExtrusionBlock)
            & (self.start_pos == other.start_pos)
            & (self.end_pos == other.end_pos)
            & (self.angle_step == other.angle_step)
            & (self.angle_continuous == other.angle_continuous)
        )

    @property
    def start_pos(self):
        """Get start position of block."""
        return self._start_pos

    @start_pos.setter
    def start_pos(self, pos):
        """Set start position of block."""
        self._start_pos = pos

    @property
    def end_pos(self):
        """Get end position of block."""
        return self._end_pos

    @end_pos.setter
    def end_pos(self, pos):
        """Set start position of block."""
        self._end_pos = pos

    @property
    def angle_step(self):
        """Get end position of block."""
        return self._angle_step

    @angle_step.setter
    def angle_step(self, pos):
        """Set start position of block."""
        self._angle_step = pos

    @property
    def angle_continuous(self):
        """Get end position of block."""
        return self._angle_continuous

    @angle_continuous.setter
    def angle_continuous(self, pos):
        """Set start position of block."""
        self._angle_continuous = pos

    def _from_json(self, json):
        """Convert the class from a JSON object.

        Parameters
        ----------
        json: dict
            Dictionary representing the extrusion block.
        """
        self._start_pos = json["extrusion_block_start"]
        self._end_pos = json["extrusion_block_end"]
        self._angle_step = json["extrusion_block_angle_step"]
        self._angle_continuous = json["extrusion_block_continuous_rotation"]

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        dict
            Dictionary of the extrusion block represented as JSON.
        """
        block_dict = {
            "extrusion_block_start": self.start_pos,
            "extrusion_block_end": self.end_pos,
            "extrusion_block_angle_step": self.angle_step,
            "extrusion_block_continuous_rotation": self.angle_continuous
        }

        return block_dict

    @property
    def extrusion_length(self):
        """Return extrusion length between start and end positions.

        Returns
        -------
        float
           Block extrusion length.
        """
        return abs(self.end_pos - self.start_pos)


class ExtrusionBlockList(list):
    """Generic class for list of Entities."""

    def __eq__(self, other):
        """Compare equality of 2 ExtrusionBlockList objects."""
        if isinstance(other, ExtrusionBlockList):
            is_equal = True
            for block_1, block_2 in zip(self, other):
                if block_1 != block_2:
                    is_equal = False
                    break
            return is_equal
        else:
            return False

    def _to_json(self):
        """Convert from a Python class to a JSON object.

        Returns
        -------
        list
            List of the extrusion blocks represented as JSON.
        """
        return [block._to_json() for block in self]

    def _from_json(self, json_list):
        """Convert the class from a JSON object.

        Parameters
        ----------
        json: list
            List of extrusion blocks in json.
        """
        for json_object in json_list:
            block = ExtrusionBlock()
            block._from_json(json_object)
            self.append(block)