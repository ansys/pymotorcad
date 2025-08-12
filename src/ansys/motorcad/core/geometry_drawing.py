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
    import matplotlib.transforms as transforms

    # Flake8 incorrectly flagged this as unused
    from matplotlib.widgets import CheckButtons  # noqa: F401

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

_MAX_RECURSION = 100


class _RegionDrawing:
    def __init__(self, ax, stored_coords):
        self.ax = ax
        self.stored_coords = stored_coords
        self.legend_objects = dict()
        self.object_states = dict()

    @property
    def states_list(self):
        return list(self.object_states.values())

    @property
    def labels_list(self):
        return list(self.legend_objects)

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
            return self.ax.annotate(
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

    def _draw_duplicates(self, region: GeometryNode, colour, labels):
        """Draw all region duplications."""
        duplication_angle = 360 / region.duplications

        for duplicate_number in range(0, region.duplications):
            duplicate = region.duplicate()
            duplicate.parent = region.parent
            duplicate.rotate(Coordinate(0, 0), duplication_angle * duplicate_number)
            self._draw_region(duplicate, colour, labels, full_geometry=True)

    def _draw_region(self, region, colour, labels=False, full_geometry=False, draw_points=False):
        # Draw region onto a plot
        duplication_angle = 360 / region.duplications
        colour = tuple(channel / 255 for channel in colour)
        fill_points_x = []
        fill_points_y = []
        if isinstance(region, GeometryNode):
            label = ""
            label += "│   " * (region.depth - 2)
            if region.depth == 1:
                cap = ""
            elif region.name == region.parent.children[-1].name:
                cap = "└── "
            else:
                cap = "├── "
            label += cap
            label += region.key
        else:
            label = region.name

        for entity in region.entities:
            if entity.length == 0:
                continue
            if isinstance(entity, Line):
                num_points = 2
            else:
                num_points = int(
                    720
                    * (entity.length / (2 * 3.14159265358979323846264338327950288 * entity.radius))
                )
                if num_points < 2 or (1 / (num_points - 1)) * entity.length < 0.05:
                    num_points = int(entity.length / 0.05 + 1)

            for i in range(0, num_points):
                fractional_distance = i / (num_points - 1)
                point_i = entity.get_coordinate_from_distance(
                    entity.start, fraction=fractional_distance
                )
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
                # Draw entity and add it to legend_objects in the appropriate region's list for
                # later access
                self.legend_objects[label].append(
                    self._draw_entity(
                        entity,
                        "black",
                    )
                )
        # Draw region's colouring and add it to legend_objects in the appropriate list for
        # later access
        self.legend_objects[label].append(
            plt.fill(fill_points_x, fill_points_y, color=colour, label=label, lw=0.4)[0]
        )

        self.ax.set_aspect("equal", adjustable="box")

        # Draw midpoints and endpoints, place them in a region's list in legend_objects
        if draw_points:
            for entity_num, entity in enumerate(region.entities):
                text = "e{}".format(entity_num)
                point = self._plot_text_no_overlap(entity.midpoint, text, "black")
                if point is not None:
                    self.legend_objects[label].append(point)

            points = region.entities.points
            for point_num, point in enumerate(points):
                text = "p{}".format(point_num)
                point = self._plot_text_no_overlap(point, text, "black")
                if point is not None:
                    self.legend_objects[label].append(point)
        if labels:
            point = self._plot_text_no_overlap(region.centroid, region.name, "black")
            if point is not None:
                self.legend_objects[label].append(point)

    def _draw_entity(self, entity, colour, draw_points=False):
        """Draw entity onto plot.

        Entities are drawn with relatively large line width, so that they do not end up covered
        by the region's filled interior colours.
        """
        if isinstance(entity, Line):
            drawn_entity = plt.plot(
                [entity.start.x, entity.end.x],
                [entity.start.y, entity.end.y],
                color=colour,
                lw=0.4,
                zorder=2,
            )[0]

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
            drawn_entity = mpatches.Arc(
                centre,
                width,
                height,
                theta1=start_angle,
                theta2=end_angle,
                color=colour,
                lw=0.4,
                zorder=2,
            )
            self.ax.plot(marker="-o")
            self.ax.add_patch(drawn_entity)

        if draw_points:
            self._plot_text_no_overlap(entity.start, "s", colour)
            self._plot_text_no_overlap(entity.midpoint, "m", colour)
            self._plot_text_no_overlap(entity.end, "e", colour)

        self.ax.set_aspect("equal", adjustable="box")

        return drawn_entity


def draw_objects_debug(objects):
    """Draw regions on plot if not being run in Motor-CAD.

    Parameters
    ----------
    objects : List of objects
        entities to draw
    """
    warn(
        "draw_objects_debug() WILL BE DEPRECATED SOON - Use geometry_drawing.draw_objects instead",
        DeprecationWarning,
    )
    if not is_running_in_internal_scripting():
        draw_objects(objects)


def draw_objects(
    objects,
    labels=False,
    full_geometry=False,
    draw_points=None,
    save=None,
    dpi=None,
    legend=None,
    axes=True,
    toggle_regions=None,
    title=None,
    optimize=False,
):
    """Draw geometry objects on a plot.

    Parameters
    objects : List of objects
        objects to draw
    labels : bool
        whether labels should be drawn. Default is False
    full_geometry : bool
        Whether duplications of regions should be drawn
    draw_points : bool
        Whether to draw end and mid points of entities. Default is False, except for sole entities.
    dpi : int
        resolution of figure (used primarily when exporting images as pngs)
    legend : bool
        whether interactable legend should be drawn
    axes : bool
        whether axes should be drawn
    toggle_regions : list of str
        used for GeometryTrees: provided regions will be drawn if not already, and not if
        already drawn.
    optimize: bool
        whether geometry drawing should be optimized or not. Default is False. Incompatible with
        toggle_regions, as prevents regions that are not by default displayed from being calculated.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Failed to draw geometry. Please ensure MatPlotLib and a suitable backend "
            "e.g. PyQt5 are installed"
        )

    stored_coords = []
    fig, ax = plt.subplots(figsize=(10, 6))
    region_drawing = _RegionDrawing(ax, stored_coords)

    # Determine a label that portrays appropriate positional information in the tree (if, indeed,
    # a tree is supplied)
    def get_label(object):
        # Make certain label is appropriate for regions that might not be a part of trees
        if isinstance(object, Region) and not isinstance(object, GeometryNode):
            return object.name
        # Tuples used to draw lists of entities. The second value input is an integer used to
        # grant unique labels
        if isinstance(object, tuple):
            return str(object[0]).split(".")[-1][0:-2] + str(object[1])

        if object.key == "root":
            return "root"
        label = ""
        label += "│   " * (object.depth - 2)
        if object.depth == 1:
            cap = ""
        elif object == object.parent.children[-1]:
            cap = "└── "
        else:
            cap = "├── "
        label += cap
        label += object.key
        return label

    # Draw a geometry tree
    if isinstance(objects, GeometryTree):
        if toggle_regions is None:
            toggle_regions = list()
        # Set legend to by default be drawn if showing defining geometry
        if legend is None and not full_geometry:
            legend = True
        # The list below determines which objects types (and children) are by default drawn.
        region_types = [
            "Stator",
            "Split Slot",
            "Wedge",
            "Stator Air",
            "Rotor",
            "Shaft",
            "Banding",
            "Magnet",
            "Coil Separator",
            "Rotor Slot",
        ]

        # A set is used to avoid elements that are both of an appropriate type and children of
        # an appropriate type being listed twice
        drawn_nodes = set()
        for starting_node in objects:
            if starting_node.region_type.value in region_types and starting_node.key != "root":
                for subnode in objects.get_subtree(starting_node):
                    drawn_nodes.add(get_label(subnode))
        if optimize:
            for node in objects:
                if not get_label(node) in drawn_nodes and node.key != "root":
                    objects.remove_node(node)

        for node in objects:
            label = get_label(node)
            if node.key != "root":
                # Establish a place to store all the drawn entities composing an object, for
                # later use in toggling visibility
                region_drawing.legend_objects[label] = []

                if full_geometry:
                    region_drawing._draw_duplicates(node, node.colour, labels)

                else:
                    if draw_points is not None:
                        region_drawing._draw_region(
                            node, node.colour, labels, draw_points=draw_points
                        )
                    else:
                        region_drawing._draw_region(node, node.colour, labels)

            # Assign each region an appropriate visibility state based on what should be by default
            # displayed
            if label in drawn_nodes:
                region_drawing.object_states[label] = True
            elif node.key != "root":
                region_drawing.object_states[label] = False
            if node.key in toggle_regions:
                region_drawing.object_states[label] = not region_drawing.object_states[label]

        # Enforce initial visibility
        for drawn_region in region_drawing.legend_objects:
            for drawn_object in region_drawing.legend_objects[drawn_region]:
                drawn_object.set_visible(region_drawing.object_states[drawn_region])

    # Draw a list of entities or nodes
    elif isinstance(objects, list):
        if all(isinstance(object, Region) for object in objects):
            if draw_points is None:
                draw_points = False
            for region in objects:
                label = get_label(region)
                region_drawing.legend_objects[label] = []
                region_drawing.object_states[label] = True
                region_drawing._draw_region(region, region.colour, labels, draw_points=draw_points)

        if all(isinstance(object, Entity) for object in objects):
            for i, entity in enumerate(objects):
                label = get_label((type(entity), i))
                region_drawing.legend_objects[label] = []
                region_drawing.object_states[label] = True
                region_drawing.legend_objects[label].append(
                    region_drawing._draw_entity(entity, "black", draw_points)
                )

    # Draw a sole region/node
    if isinstance(objects, Region) or isinstance(objects, GeometryNode):
        if draw_points is None:
            draw_points = False
        label = get_label(objects)
        region_drawing.legend_objects[label] = []
        region_drawing.object_states[label] = True
        region_drawing._draw_region(objects, objects.colour, labels, draw_points=draw_points)

    # Draw a sole entity
    if isinstance(objects, Entity):
        if draw_points is None:
            draw_points = True
        label = get_label((type(objects), 1))
        region_drawing.legend_objects[label] = []
        region_drawing.object_states[label] = True
        region_drawing.legend_objects[label].append(
            region_drawing._draw_entity(objects, "black", draw_points)
        )

    # Create an interactable legend to label and change displayed regions
    if legend:
        # Size the legend based on the length of the longest label
        x_boundary = 0.01 * max(len(label) for label in region_drawing.labels_list) + 0.05

        rax = plt.axes([0.05, 0.2, x_boundary, 0.6])
        box_size = min(len(region_drawing.object_states), 10)
        region_drawing.current_index = 0

        # Create the CheckButtons object that makes up the actual region
        check = CheckButtons(
            rax, region_drawing.labels_list[0:box_size], region_drawing.states_list[0:box_size]
        )

        # Shift the original plot aside to make room
        ax.set_position(transforms.Bbox.from_extents(x_boundary + 0.1, 0, 1, 1), which="both")

        # Define the behaviour of a checkbox upon being clicked
        def func(label):
            region_drawing.object_states[label] = not region_drawing.object_states[label]
            for region_object in region_drawing.legend_objects[label]:
                region_object.set_visible(region_drawing.object_states[label])
            plt.draw()

        # Link the above function to the CheckButtons object
        check.on_clicked(func)

        # Function that cycles the labels displayed on the CheckButtons object up or down
        def cycle_check(check, direction):
            current_index = region_drawing.current_index
            number = len(region_drawing.object_states)
            labels = region_drawing.labels_list
            if direction == "down":
                for i in range(0, box_size):
                    new_index = (current_index + i + 1) % number
                    check.labels[i % box_size].set_text(labels[new_index])
                    # Avoid actually modifying data with just a scrolling action
                    check.eventson = False
                    check.set_active(i % box_size, region_drawing.states_list[new_index])
                    # Make certain changes can occur once scrolling is done
                    check.eventson = True
                region_drawing.current_index += 1

            if direction == "up":
                for i in range(0, box_size):
                    new_index = (current_index + i - 1) % number
                    check.labels[i % box_size].set_text(labels[new_index])
                    check.eventson = False
                    check.set_active(i % box_size, region_drawing.states_list[new_index])
                    check.eventson = True
                region_drawing.current_index -= 1

        # Link the direction keys and scroll wheel to the cycling function
        def on_press(event):
            cycle_check(check, event.key)
            fig.canvas.draw()

        fig.canvas.mpl_connect("key_press_event", on_press)

        def on_scroll(event):
            cycle_check(check, event.button)
            fig.canvas.draw()

        fig.canvas.mpl_connect("scroll_event", on_scroll)

    if not axes:
        ax.axis("off")
    if title is not None:
        ax.set_title(title)
    if save is None:
        plt.show()
    else:
        plt.savefig(save, dpi=dpi)
