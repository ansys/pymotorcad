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

from ansys.motorcad.core.geometry import Arc, Coordinate, Entity, Line, Region
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

    def draw_region(self, region, colour):
        """Draw a region."""
        for entity in region.entities:
            self.draw_entity(entity, colour)

        for entity_num, entity in enumerate(region.entities):
            text = "e{}".format(entity_num)
            self._plot_text_no_overlap(entity.midpoint, text, colour)

        points = region.entities.points
        for point_num, point in enumerate(points):
            text = "p{}".format(point_num)
            self._plot_text_no_overlap(point, text, colour)

        self._plot_text_no_overlap(region.centroid, region.name, colour)

    def draw_coordinate(self, coordinate, colour):
        """Draw coordinate onto plot."""
        plt.plot(coordinate.x, coordinate.y, "x", color=colour)

    def draw_entity(self, entity, colour):
        """Draw entity onto plot."""
        entity_coords = []

        mid_point = Coordinate(
            (entity.end.x + entity.start.x) / 2, (entity.end.y + entity.start.y) / 2
        )

        entity_coords += [Coordinate(mid_point.x, mid_point.y)]

        if isinstance(entity, Line):
            plt.plot([entity.start.x, entity.end.x], [entity.start.y, entity.end.y], color=colour)

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
                centre, width, height, theta1=start_angle, theta2=end_angle, color=colour
            )
            self.ax.plot(marker="-o")
            self.ax.add_patch(arc)

        self.ax.set_aspect("equal", adjustable="box")


def draw_objects_debug(objects):
    """Draw regions on plot if not being run in Motor-CAD.

    Parameters
    ----------
    objects : List of objects
        entities to draw
    """
    if not is_running_in_internal_scripting():
        draw_objects(objects)


def draw_objects(objects):
    """Draw geometry objects on a plot."""
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Failed to draw geometry. Please ensure MatPlotLib and a suitable backend "
            "e.g. PyQt5 are installed"
        )

    if not isinstance(objects, list):
        # Given a single region not a list - reformat
        objects = [objects]

    stored_coords = []

    # Some basic colours
    colours = ["red", "blue", "green", "purple"]
    entity_no_region_colour = "grey"
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    region_drawing = _RegionDrawing(ax, stored_coords)
    for i, object in enumerate(objects):
        # loop through colours once end of list reached
        while i > len(colours) - 1:
            i -= len(colours)
        if object is None:
            continue
        if isinstance(object, Region):
            region_drawing.draw_region(object, colours[i])
        elif isinstance(object, Entity):
            region_drawing.draw_entity(object, entity_no_region_colour)
        elif isinstance(object, Coordinate):
            region_drawing.draw_coordinate(object, entity_no_region_colour)
        else:
            raise TypeError("Object cannot be drawn")
    plt.show()


def draw_regions(regions):
    """WILL BE DEPRECATED SOON - USE geometry_drawing.draw_objects() instead.

    Draw regions on plot.

    Parameters
    ----------
    regions : Region or list of Region
        entities to draw
    """
    warn(
        "draw_regions() WILL BE DEPRECATED SOON - USE geometry_drawing.draw_objects instead",
        DeprecationWarning,
    )
    draw_objects(regions)
