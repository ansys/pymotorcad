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
        self.legend_objects = []

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

    def _plot_text_no_overlap(self, point, text, colour, depth=0):
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
                zorder=depth + 1,
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
        """Draw all region duplications."""
        duplication_angle = 360 / region.duplications

        for duplicate_number in range(0, region.duplications):
            duplicate = deepcopy(region)
            duplicate.rotate(Coordinate(0, 0), duplication_angle * duplicate_number)
            self.draw_region(duplicate, colour, labels, depth, full_geometry=True)

    def draw_region(self, region, colour, labels, depth, full_geometry=False, draw_points=False):
        # Draw region onto a plot
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
            # If geometry is full, lines separating region duplications shouldn't be drawn.
            # These are determined by seeing if, for Line entities, the angle
            # (modulo duplication angle) matches zero or the duplication angle, and seeing
            # if they also pass through the origin.
            if not (
                full_geometry
                and isinstance(entity, Line)
                and (
                    ((entity.angle % duplication_angle) < GEOM_TOLERANCE)
                    or ((entity.angle % duplication_angle) - duplication_angle < GEOM_TOLERANCE)
                )
                # Check start and end of a line are not the same, to avoid unsupported
                # operand types in the next line
                and entity.start != entity.end
                and entity.get_coordinate_distance(Coordinate(0, 0)) < GEOM_TOLERANCE
            ):
                self.draw_entity(
                    entity,
                    "black",
                    depth=depth,
                )

        self.legend_objects.append(
            plt.fill(fill_points_x, fill_points_y, color=colour, zorder=depth, label=region.name)[0]
        )
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
            self._plot_text_no_overlap(region.centroid, region.name, "black", depth=depth)

    def draw_entity(self, entity, colour, depth=0, draw_points=False):
        """Draw entity onto plot.

        Entities are drawn with relatively large line width, so that they do not end up covered
        by the region's filled interior colours.
        """
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


def draw_objects(
    objects,
    labels=False,
    full_geometry=False,
    depth=0,
    draw_points=None,
    save=None,
    dpi=None,
    legend=False,
):
    """Draw geometry objects on a plot."""
    if is_running_in_internal_scripting():
        return
    stored_coords = []
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    region_drawing = _RegionDrawing(ax, stored_coords)

    if isinstance(objects, GeometryTree):
        # The list below determines which objects (and children) are by default drawn.

        region_types = ["Stator", "Split Slot", "Wedge", "Stator Air", "Rotor", "Shaft"]
        for starting_node in objects:
            if starting_node.region_type.value in region_types:
                if starting_node.key != "root":
                    subtree = objects.get_subtree(starting_node)
                    for node in subtree:
                        # Draw 360 degrees of each region if requested
                        if full_geometry:
                            region_drawing.draw_duplicates(node, node.colour, labels, depth=0)
                        else:
                            if draw_points is not None:
                                region_drawing.draw_region(
                                    node, node.colour, labels, depth=0, draw_points=draw_points
                                )
                            else:
                                region_drawing.draw_region(node, node.colour, labels, depth=0)

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

    if legend:
        plt.legend(
            handles=region_drawing.legend_objects,
            fontsize="small",
            draggable=True,
            loc="center",
            bbox_to_anchor=(0.9, 0.5),
        )

    if save is None:
        plt.show()
    else:
        plt.savefig(save, dpi=dpi)
