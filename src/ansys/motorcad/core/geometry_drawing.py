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

"""Unit containing region drawing functions."""
from copy import deepcopy
import warnings
from warnings import warn

from ansys.motorcad.core.geometry import GEOM_TOLERANCE, Arc, Coordinate, Entity, Line, Region
from ansys.motorcad.core.methods.geometry_tree import GeometryNode, GeometryTree
from ansys.motorcad.core.rpc_client_core import is_running_in_internal_scripting

try:
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

_MAX_RECURSION = 100


class _RegionDrawing:
    def __init__(self, ax, stored_coords):
        self.ax = ax
        self.stored_coords = stored_coords

    def _get_plot_range(self):
        # plot should be square so get_xlim() == get_ylim()
        x_min, x_max = self.ax.get_xlim()
        return x_max - x_min

    def _find_coord_no_overlap(self, entity_coord, tried_coords, modifier):
        # adjust depending on text size
        # 0.04 good compromise
        overlap_tol = 0.04
        result = deepcopy(entity_coord)

        recursion_depth = len(tried_coords)

        if recursion_depth > _MAX_RECURSION:
            return None

        if entity_coord in tried_coords:
            # Already tried this coordinate
            # Might be flip-flopping between 2 points
            # Add a small amount to how far we move the coord to try and force out of pattern
            modifier += 0.01

        tried_coords += [entity_coord]

        for stored_coord in self.stored_coords:
            difference = (entity_coord - stored_coord) / self._get_plot_range()

            if abs(difference) == 0:
                # Handle case where coordinates are exactly the same
                # Set to very small amount
                difference = Coordinate(0.00001, 0.00001)

            unit_vector = difference / abs(difference)

            if abs(difference) < overlap_tol:
                result += unit_vector * overlap_tol * self._get_plot_range() * (1.1 + modifier)
                result = self._find_coord_no_overlap(result, tried_coords, modifier)
                break
        return result

    def _plot_text_no_overlap(self, point, text, colour):
        # Reset params for recursive function
        tried_coords = []
        modifier = 0

        new_coord = self._find_coord_no_overlap(point, tried_coords, modifier)

        if new_coord is None:
            warning_str = "Failed to plot all labels on graph"
            warnings.warn(warning_str)
            self.ax.set_title("Warning : " + warning_str, color="red")
        else:
            self.stored_coords += [new_coord]
            self.ax.annotate(
                text,
                xy=(point.x, point.y),
                xytext=(
                    new_coord.x + 0.04 * self._get_plot_range(),
                    new_coord.y + 0.04 * self._get_plot_range(),
                ),
                ha="right",
                arrowprops=dict(arrowstyle="->", shrinkA=0, color=colour, alpha=0.5),
                color=colour,
            )

    def draw_region_old(self, region, colour):
        """Draw a region."""
        for entity in region.entities:
            self.draw_entity_old(entity, colour)

        for entity_num, entity in enumerate(region.entities):
            text = "e{}".format(entity_num)
            self._plot_text_no_overlap(entity.midpoint, text, colour)

        points = region.entities.points
        for point_num, point in enumerate(points):
            text = "p{}".format(point_num)
            self._plot_text_no_overlap(point, text, colour)

        self._plot_text_no_overlap(region.centroid, region.name, colour)

    def draw_entity_old(self, entity, colour, debug=False):
        """Draw entity onto plot."""
        entity_coords = []

        mid_point = Coordinate(
            (entity.end.x + entity.start.x) / 2, (entity.end.y + entity.start.y) / 2
        )

        entity_coords += [Coordinate(mid_point.x, mid_point.y)]

        if isinstance(entity, Line):
            if debug:
                plt.plot(
                    [entity.start.x, entity.end.x], [entity.start.y, entity.end.y], color=colour
                )
            else:
                plt.plot(
                    [entity.start.x, entity.end.x],
                    [entity.start.y, entity.end.y],
                    color=colour,
                    lw=0.6,
                )

        elif isinstance(entity, Arc):
            width = abs(entity.radius * 2)
            height = abs(entity.radius * 2)
            centre = entity.centre.x, entity.centre.y
            rad1, angle1 = (entity.start - entity.centre).get_polar_coords_deg()
            rad2, angle2 = (entity.end - entity.centre).get_polar_coords_deg()

            if entity.radius > 0:
                start_angle = angle1
                end_angle = angle2
            else:
                start_angle = angle2
                end_angle = angle1
            if debug:
                arc = mpatches.Arc(
                    centre, width, height, theta1=start_angle, theta2=end_angle, color=colour
                )
            else:
                arc = mpatches.Arc(
                    centre, width, height, theta1=start_angle, theta2=end_angle, color=colour, lw=2
                )
            self.ax.plot(marker="-o")
            self.ax.add_patch(arc)

        self.ax.set_aspect("equal", adjustable="box")

    def draw_coordinate(self, coordinate, colour):
        """Draw coordinate onto plot."""
        plt.plot(coordinate.x, coordinate.y, "x", color=colour)

    def draw_duplicates(self, region: GeometryNode, colour, labels, depth):
        duplication_angle = 360 / region.duplications
        origin = Coordinate(0, 0)

        for duplicate_number in range(0, region.duplications):
            duplicate = deepcopy(region)
            duplicate.rotate(Coordinate(0, 0), duplication_angle * duplicate_number)
            self.draw_region(duplicate, colour, labels, depth, full_geometry=True)

    def draw_region(self, region, colour, labels, depth, full_geometry=False, draw_points=False):
        duplication_angle = 360 / region.duplications
        colour = tuple(channel / 255 for channel in colour)
        fill_points_x = []
        fill_points_y = []
        for entity in region.entities:
            point_0 = entity.start
            fill_points_x.append(point_0.x)
            fill_points_y.append(point_0.y)
            for i in range(1, int(entity.length / 0.1)):
                point_i = entity.get_coordinate_from_distance(point_0, distance=i * 0.1)
                fill_points_x.append(point_i.x)
                fill_points_y.append(point_i.y)
            if not (
                isinstance(entity, Line)
                and (
                    ((entity.angle % duplication_angle) < GEOM_TOLERANCE)
                    or ((entity.angle % duplication_angle) - duplication_angle < GEOM_TOLERANCE)
                )
                and entity.get_coordinate_distance(Coordinate(0, 0)) < GEOM_TOLERANCE
                and full_geometry
            ):
                self.draw_entity(
                    entity,
                    "black",
                    depth=depth,
                )

        plt.fill(fill_points_x, fill_points_y, color=colour, zorder=depth)
        self.ax.set_aspect("equal", adjustable="box")

        if draw_points:
            for entity_num, entity in enumerate(region.entities):
                text = "e{}".format(entity_num)
                self._plot_text_no_overlap(entity.midpoint, text, "black")

            points = region.entities.points
            for point_num, point in enumerate(points):
                text = "p{}".format(point_num)
                self._plot_text_no_overlap(point, text, "black")

        if labels:
            self._plot_text_no_overlap(region.centroid, region.name, "black")

    def draw_entity(self, entity, colour, depth=0, draw_points=False):
        """Draw entity onto plot."""
        entity_coords = []

        mid_point = Coordinate(
            (entity.end.x + entity.start.x) / 2, (entity.end.y + entity.start.y) / 2
        )

        entity_coords += [Coordinate(mid_point.x, mid_point.y)]

        if isinstance(entity, Line):
            plt.plot(
                [entity.start.x, entity.end.x],
                [entity.start.y, entity.end.y],
                color=colour,
                lw=2,
                zorder=depth,
            )

        elif isinstance(entity, Arc):
            width = abs(entity.radius * 2)
            height = abs(entity.radius * 2)
            centre = entity.centre.x, entity.centre.y
            rad1, angle1 = (entity.start - entity.centre).get_polar_coords_deg()
            rad2, angle2 = (entity.end - entity.centre).get_polar_coords_deg()

            if entity.radius > 0:
                start_angle = angle1
                end_angle = angle2
            else:
                start_angle = angle2
                end_angle = angle1
            arc = mpatches.Arc(
                centre,
                width,
                height,
                theta1=start_angle,
                theta2=end_angle,
                color=colour,
                lw=2.5,
                zorder=depth,
            )
            self.ax.plot(marker="-o")
            self.ax.add_patch(arc)

        if draw_points:
            self._plot_text_no_overlap(entity.start, "s", colour)
            self._plot_text_no_overlap(entity.midpoint, "m", colour)
            self._plot_text_no_overlap(entity.end, "e", colour)

        self.ax.set_aspect("equal", adjustable="box")


def draw_objects_debug(objects):
    """Draw regions on plot if not being run in Motor-CAD.

    Parameters
    ----------
    objects : List of objects
        entities to draw
    """
    warn(
        "draw_objects_debug() WILL BE DEPRECATED SOON - USE geometry_drawing.draw_objects instead",
        DeprecationWarning,
    )
    if not is_running_in_internal_scripting():
        draw_objects(objects)


def draw_objects(objects, labels=False, full_geometry=False, depth=0, draw_points=None):
    """Draw geometry objects on a plot."""
    stored_coords = []
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    region_drawing = _RegionDrawing(ax, stored_coords)

    if isinstance(objects, GeometryTree):
        tree = objects.values()
        # List below determines order in which items are drawn, and therefore which are
        # drawn above when overlaps occur
        region_types = [
            "Stator",
            "Rotor",
            "Stator Slot Area",
            "Stator Slot",
            "Rotor Slot Area",
            "Split Slot",
            "Stator Liner",
            "Rotor Liner",
            "Wedge",
            "Stator Duct",
            "Housing",
            "Magnetic Housing",
            "Stator Impreg",
            "Impreg Gap",
            "Stator Copper",
            "Stator Copper Insulation",
            "Stator Divider",
            "Stator Slot Spacer",
            "Stator slot separator",
            "Coil Insulation",
            "Stator Air",
            "Rotor hub",
            "Rotor Air",
            "Rotor Air (excluding liner area)",
            "Rotor Pocket",
            "Pole Spacer",
            "Rotor Slot",
            "Coil Separator",
            "Damper Bar",
            "Rotor Wedge",
            "Rotor Divider",
            "Rotor Copper Insulation",
            "Rotor Copper",
            "Rotor Impreg",
            "Shaft",
            "Axle",
            "Rotor Duct",
            "Magnet",
            "Barrier",
            "Base Mount",
            "Plate Mount",
            "Endcap",
            "Banding",
            "Sleeve",
            "Rotor Cover",
            "Slot Water Jacket Insulation",
            "Slot Water Jacket Wall",
            "Slot Water Jacket Duct",
            "Slot Water Jacket Duct (no detail)",
            "Cowling",
            "Cowling Grill",
            "Brush",
            "Commutator",
            "Airgap",
            "DXF Import",
            "Stator Proximity Loss Slot",
            "Adaptive Region",
        ]
        excluded_regions = [
            "Housing",
            "Stator Slot Area",
            "Stator Liner",
            "Stator Impreg",
            "Plate Mount",
            "Endcap",
            "Impreg Gap",
        ]
        # excluded_regions = []
        for region_type in excluded_regions:
            region_types.remove(region_type)

        for depth, region_type in enumerate(region_types):
            if region_type == "Shaft":
                pass
            for node in tree:
                if node.region_type.value == region_type:
                    if node.key != "root":
                        if full_geometry:
                            region_drawing.draw_duplicates(node, node.colour, labels, depth=depth)
                        else:
                            if draw_points is not None:
                                region_drawing.draw_region(
                                    node, node.colour, labels, depth=depth, draw_points=draw_points
                                )
                            else:
                                region_drawing.draw_region(node, node.colour, labels, depth=depth)

    elif isinstance(objects, list):
        if all(isinstance(object, Region) for object in objects):
            for region in objects:
                if draw_points is not None:
                    region_drawing.draw_region(
                        region, region.colour, labels, depth=depth, draw_points=draw_points
                    )
                else:
                    region_drawing.draw_region(
                        region, region.colour, labels, depth=depth, draw_points=True
                    )
        if all(isinstance(object, Entity) for object in objects):
            for entity in objects:
                if draw_points is not None:
                    region_drawing.draw_entity(entity, "black", labels, draw_points=draw_points)
                else:
                    region_drawing.draw_entity(entity, "black", labels, draw_points=True)

    if isinstance(objects, Region) or isinstance(objects, GeometryNode):
        region_drawing.draw_region(objects, objects.colour, labels, depth=depth, draw_points=True)

    if isinstance(objects, Entity):
        region_drawing.draw_entity(objects, "black", draw_points=True)
    plt.show()
