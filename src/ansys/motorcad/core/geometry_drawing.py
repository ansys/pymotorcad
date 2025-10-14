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
from ansys.motorcad.core.geometry_tree import GeometryNode, GeometryTree
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


class BiDict:
    """Simple bi-directional dictionary for use with legend labels."""

    def __init__(self):
        """Initialize a bi-directional dictionary."""
        self.forward = dict()
        self.backward = dict()

    def insert(self, key, value):
        """Insert key-value pair."""
        if key in self.forward:
            old_value = self.forward[key]
            del self.backward[old_value]
        if value in self.backward:
            old_key = self.backward[value]
            del self.forward[old_key]

        self.forward[key] = value
        self.backward[value] = key

    def get_forward(self, key):
        """Get a dictionary with keys as keys."""
        return self.forward.get(key)

    def get_backward(self, value):
        """Get a dictionary with keys as values."""
        return self.backward.get(value)

    def remove_by_key(self, key):
        """Remove a key-value pair from the dictionary, by key."""
        value = self.forward.pop(key, None)
        if value:
            self.backward.pop(value, None)

    def remove_by_value(self, value):
        """Remove a key-value pair from the dictionary, by value."""
        key = self.backward.pop(value, None)
        if key:
            self.forward.pop(key, None)


class _RegionDrawing:
    def __init__(self, fig, ax, stored_coords):
        self.fig = fig
        self.ax = ax
        self.stored_coords = stored_coords
        self.legend_objects = dict()
        self.object_states = dict()
        self.keys_and_labels = BiDict()
        # Dict containing the maximum radius of each region
        self.bounds = dict()
        self.full_geometry = False

    @property
    def states_list(self):
        return list(self.object_states.values())

    @staticmethod
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

    def enable_legend(self):
        self.fig.set_size_inches(10, 6)
        # Size the legend based on the length of the longest label
        x_boundary = 0.01 * max(len(label) for label in self.keys_and_labels.backward) + 0.05

        rax = plt.axes([0.05, 0.2, x_boundary, 0.6])
        self.rax = rax
        self.box_size = min(len(self.object_states), 12)
        self.current_index = 0

        # Create the CheckButtons object that makes up the actual legend
        self.check = CheckButtons(
            rax,
            list(self.keys_and_labels.backward)[0 : self.box_size],
            self.states_list[0 : self.box_size],
        )

        # Shift the original plot aside to make room
        self.ax.set_position(transforms.Bbox.from_extents(x_boundary + 0.1, 0, 1, 1), which="both")

        # Link the above function to the CheckButtons object
        self.check.on_clicked(self.func)

        # Link the direction keys and scroll wheel to the cycling function
        def on_press(event):
            self.cycle_check(event.key)
            self.fig.canvas.draw()

        self.fig.canvas.mpl_connect("key_press_event", on_press)

        def on_scroll(event):
            self.cycle_check(event.button)
            self.fig.canvas.draw()

        self.fig.canvas.mpl_connect("scroll_event", on_scroll)

        rax.annotate(
            "",
            (0.96, 0.1),
            xytext=(0.96, 0.9),
            xycoords="axes fraction",
            arrowprops=dict(arrowstyle="<->", color="gray"),
        )
        if self.box_size != len(self.object_states):
            scroll_bar_bottom = 0.8
            self.scroll_bar = rax.annotate(
                "",
                (0.96, scroll_bar_bottom),
                xytext=(0.96, 0.9),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="<|-|>", color="black"),
            )

    # Function that cycles the labels displayed on the CheckButtons object up or down
    def cycle_check(self, direction):
        if self.box_size == len(self.object_states):
            return
        check = self.check
        current_index = self.current_index
        number = len(self.object_states)
        labels = list(self.keys_and_labels.backward)
        if direction == "down":
            # Don't scroll if at the bottom
            if self.current_index == (number - self.box_size):
                return
            for i in range(0, self.box_size):
                new_index = (current_index + i + 1) % number
                check.labels[i % self.box_size].set_text(labels[new_index])
                # Avoid actually modifying data with just a scrolling action
                check.eventson = False
                check.set_active(i % self.box_size, self.states_list[new_index])
                # Make certain changes can occur once scrolling is done
                check.eventson = True
            self.current_index += 1

        if direction == "up":
            # Don't scroll if at the top
            if self.current_index == 0:
                return
            for i in range(0, self.box_size):
                new_index = (current_index + i - 1) % number
                check.labels[i % self.box_size].set_text(labels[new_index])
                check.eventson = False
                check.set_active(i % self.box_size, self.states_list[new_index])
                check.eventson = True
            self.current_index -= 1

        scroll_size = number - self.box_size
        scroll_bar_top = 0.9 - ((0.7 / scroll_size) * self.current_index)
        scroll_bar_bottom = scroll_bar_top - 0.1
        self.scroll_bar.xy = (0.96, scroll_bar_bottom)
        self.scroll_bar.xyann = (0.96, scroll_bar_top)

    # Define the behaviour of a checkbox upon being clicked
    def func(self, label):
        key = self.keys_and_labels.backward[label]
        self.object_states[key] = not self.object_states[key]
        for region_object in self.legend_objects[key]:
            region_object.set_visible(self.object_states[key])
        self.resize_drawing()
        plt.draw()

    def resize_drawing(self):
        if self.full_geometry:
            margin = self.max_drawn_radius() * 0.05
            lim = self.max_drawn_radius() + margin
            self.ax.set(xlim=(-lim, lim), ylim=(-lim, lim))
        else:
            bounds = self.max_x_and_y()
            margin = max(abs(bounds[0] - bounds[1]), abs(bounds[2] - bounds[3])) * 0.05
            self.ax.set(
                xlim=(bounds[1] - margin, bounds[0] + margin),
                ylim=(bounds[3] - margin, bounds[2] + margin),
            )

    def _get_plot_range(self):
        # plot should be square so get_xlim() == get_ylim()
        x_min, x_max = self.ax.get_xlim()
        return x_max - x_min

    def max_x_and_y(self):
        max_x = 0
        min_x = 1000000
        max_y = 0
        min_y = 1000000

        for key in self.object_states:
            if self.object_states[key] and self.bounds[key][1] > max_x:
                max_x = self.bounds[key][1]
            if self.object_states[key] and self.bounds[key][2] < min_x:
                min_x = self.bounds[key][2]
            if self.object_states[key] and self.bounds[key][3] > max_y:
                max_y = self.bounds[key][3]
            if self.object_states[key] and self.bounds[key][4] < min_y:
                min_y = self.bounds[key][4]

        return max_x, min_x, max_y, min_y

    def max_drawn_radius(self):
        max_rad = 0
        for key in self.object_states:
            if self.object_states[key] and self.bounds[key][0] > max_rad:
                max_rad = self.bounds[key][0]
        return max_rad

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
            legend_key = region.key
        else:
            legend_key = region.name
        entity_bounds = []

        for entity in region.entities:
            entity_bounds.append(entity.get_bounds())
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
                self.legend_objects[legend_key].append(
                    self._draw_entity(
                        entity,
                        "black",
                    )
                )
        # Add bounds to region_drawing for later sizing
        region_bound = []
        region_bound.append(max(entity_bound[0] for entity_bound in entity_bounds))
        region_bound.append(max(entity_bound[1] for entity_bound in entity_bounds))
        region_bound.append(min(entity_bound[2] for entity_bound in entity_bounds))
        region_bound.append(max(entity_bound[3] for entity_bound in entity_bounds))
        region_bound.append(min(entity_bound[4] for entity_bound in entity_bounds))
        self.bounds[legend_key] = region_bound

        # Draw region's colouring and add it to legend_objects in the appropriate list for
        # later access
        self.legend_objects[legend_key].append(
            plt.fill(fill_points_x, fill_points_y, color=colour, label=legend_key, lw=0.45)[0]
        )

        self.ax.set_aspect("equal", adjustable="box")

        # Draw midpoints and endpoints, place them in a region's list in legend_objects
        if draw_points:
            for entity_num, entity in enumerate(region.entities):
                text = "e{}".format(entity_num)
                point = self._plot_text_no_overlap(entity.midpoint, text, "black")
                if point is not None:
                    self.legend_objects[legend_key].append(point)

            points = region.entities.points
            for point_num, point in enumerate(points):
                text = "p{}".format(point_num)
                point = self._plot_text_no_overlap(point, text, "black")
                if point is not None:
                    self.legend_objects[legend_key].append(point)
        if labels:
            point = self._plot_text_no_overlap(region.centroid, region.name, "black")
            if point is not None:
                self.legend_objects[legend_key].append(point)

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
                lw=0.45,
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
                lw=0.45,
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
    label_regions=False,
    full_geometry=False,
    draw_points=None,
    save=None,
    dpi=None,
    legend=None,
    axes=True,
    toggle_regions=None,
    title=None,
    optimise=False,
    expose_region_drawing=False,
    draw_internal=False,
    display=True,
):
    """Draw geometry objects on a plot.

    Parameters
    objects : List of objects
        Objects to draw
    labels : bool
        Whether labels should be drawn. Default is False
    full_geometry : bool
        Whether duplications of regions should be drawn
    draw_points : bool
        Whether to draw end and mid points of entities. Default is False, except for sole entities.
    save: str
        Path to save file to. Default is None.
    dpi : int
        Resolution of figure (used primarily when exporting images as pngs)
    legend : bool
        Whether interactable legend should be drawn
    axes : bool
        Whether axes should be drawn
    toggle_regions : list of str
        Used for GeometryTrees: provided regions will be drawn if not already, and not if
        already drawn.
    title: str
        Title of figure
    optimise: bool
        Whether geometry tree drawing should be optimized or not. Default is False. Incompatible
        with toggle_regions, as prevents regions that are not by default displayed from being
        calculated.
    expose_region_drawing : bool
        Whether _RegionDrawing object should be returned (which allows access to the axes and
         figure). Default is False.
    draw_internal : bool
        Whether to draw interactive region drawing when running internally. Has no effect if saving
         to file. Default is False.
    display:
        Whether to draw interactive plot. Useful to set as false when planning on further
        modifications to the figure before drawing.
    """
    if (not draw_internal) and is_running_in_internal_scripting() and save is None:
        return

    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "Failed to draw geometry. Please ensure MatPlotLib and a suitable backend "
            "e.g. PyQt5 are installed"
        )

    stored_coords = []
    fig, ax = plt.subplots(figsize=(8, 8))
    region_drawing = _RegionDrawing(fig, ax, stored_coords)
    region_drawing.full_geometry = full_geometry

    # Determine a label that portrays appropriate positional information in the tree (if, indeed,
    # a tree is supplied)

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
                    drawn_nodes.add(subnode.key)

        if optimise:
            for node in objects:
                if not node.key in drawn_nodes and node.key != "root":
                    objects.remove_node(node)

        for node in objects:
            legend_key = node.key
            if legend_key != "root":
                # Establish a place to store all the drawn entities composing an object, for
                # later use in toggling visibility
                region_drawing.legend_objects[legend_key] = []
                region_drawing.keys_and_labels.insert(legend_key, region_drawing.get_label(node))

                if full_geometry:
                    region_drawing._draw_duplicates(node, node.colour, label_regions)

                else:
                    if draw_points is not None:
                        region_drawing._draw_region(
                            node, node.colour, label_regions, draw_points=draw_points
                        )
                    else:
                        region_drawing._draw_region(node, node.colour, label_regions)

            # Assign each region an appropriate visibility state based on what should be by default
            # displayed
            if legend_key in drawn_nodes:
                region_drawing.object_states[legend_key] = True
            elif node.key != "root":
                region_drawing.object_states[legend_key] = False
            if node.key in toggle_regions:
                region_drawing.object_states[legend_key] = not region_drawing.object_states[
                    legend_key
                ]

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
                legend_key = region.name
                region_drawing.legend_objects[legend_key] = []
                region_drawing.object_states[legend_key] = True
                region_drawing.keys_and_labels.insert(legend_key, region_drawing.get_label(region))
                region_drawing._draw_region(
                    region, region.colour, label_regions, draw_points=draw_points
                )

        if all(isinstance(object, Entity) for object in objects):
            for i, entity in enumerate(objects):
                legend_key = str(entity.__class__).split(".")[-1][0:-2] + str(i)
                region_drawing.legend_objects[legend_key] = []
                region_drawing.object_states[legend_key] = True
                region_drawing.keys_and_labels.insert(legend_key, legend_key)
                region_drawing.legend_objects[legend_key].append(
                    region_drawing._draw_entity(entity, "black", draw_points)
                )
                region_drawing.bounds[legend_key] = entity.get_bounds()

    # Draw a sole region/node
    if isinstance(objects, Region) or isinstance(objects, GeometryNode):
        if draw_points is None:
            draw_points = False
        if isinstance(objects, Region):
            legend_key = objects.name
        else:
            legend_key = objects.key
        region_drawing.legend_objects[legend_key] = []
        region_drawing.object_states[legend_key] = True
        region_drawing.keys_and_labels.insert(legend_key, legend_key)
        region_drawing._draw_region(objects, objects.colour, label_regions, draw_points=draw_points)

    # Draw a sole entity
    if isinstance(objects, Entity):
        if draw_points is None:
            draw_points = True
        legend_key = str(objects.__class__).split(".")[-1][0:-2]
        region_drawing.legend_objects[legend_key] = []
        region_drawing.object_states[legend_key] = True
        region_drawing.keys_and_labels.insert(legend_key, legend_key)
        region_drawing.legend_objects[legend_key].append(
            region_drawing._draw_entity(objects, "black", draw_points)
        )
        region_drawing.bounds[legend_key] = objects.get_bounds()

    # Create an interactable legend to label and change displayed regions
    if legend:
        region_drawing.enable_legend()
    region_drawing.resize_drawing()

    if not axes:
        ax.axis("off")
    if title is not None:
        ax.set_title(title)
    if save:
        plt.savefig(save, dpi=dpi)
    elif display:
        plt.show()
    if expose_region_drawing:
        return region_drawing
