"""Unit containing region drawing functions."""
from copy import deepcopy

from ansys.motorcad.core.geometry import Arc, Coordinate, Line

try:
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class _RegionDrawing:
    def __init__(self, ax, stored_coords):
        self.ax = ax
        self.stored_coords = stored_coords

    def _find_coord_no_overlap(self, entity_coord):
        overlap_tol = 1
        result = deepcopy(entity_coord)
        for stored_coord in self.stored_coords:
            difference = entity_coord - stored_coord

            if abs(difference) == 0:
                # Handle case where coordinates are exactly the same
                # Set to very small amount
                difference = Coordinate(0.00001, 0.00001)

            unit_vector = difference / abs(difference)

            if abs(difference) < overlap_tol:
                result += unit_vector * overlap_tol * 1.1
                result = self._find_coord_no_overlap(result)
                break
        return result

    def _plot_text_no_overlap(self, point, text, colour):
        new_coord = self._find_coord_no_overlap(point)
        self.stored_coords += [new_coord]
        self.ax.annotate(
            text,
            xy=(point.x, point.y),
            xytext=(new_coord.x + 1, new_coord.y + 1),
            ha="right",
            arrowprops=dict(arrowstyle="->", shrinkA=0, color=colour, alpha=0.5),
            color=colour,
        )

    def draw_region(self, region, colour):
        """Draw a region."""
        entity_coords = []

        for entity in region.entities:
            mid_point = Coordinate(
                (entity.end.x + entity.start.x) / 2, (entity.end.y + entity.start.y) / 2
            )

            entity_coords += [Coordinate(mid_point.x, mid_point.y)]

            if isinstance(entity, Line):
                plt.plot(
                    [entity.start.x, entity.end.x], [entity.start.y, entity.end.y], color=colour
                )

            elif isinstance(entity, Arc):
                width = abs(entity.radius * 2)
                height = abs(entity.radius * 2)
                centre = entity.centre.x, entity.centre.y
                rad1, angle1 = entity.start.get_polar_coords_deg()
                rad2, angle2 = entity.end.get_polar_coords_deg()

                min_ang = min(angle1, angle2)
                max_ang = max(angle1, angle2)
                arc = mpatches.Arc(
                    centre, width, height, theta1=min_ang, theta2=max_ang, color=colour
                )
                self.ax.plot(marker="-o")
                self.ax.add_patch(arc)

        for entity_num, entity_coord in enumerate(entity_coords):
            text = "e{}".format(entity_num)
            self._plot_text_no_overlap(entity_coord, text, colour)

        points = region.entities.get_points()
        for point_num, point in enumerate(points):
            text = "p{}".format(point_num)
            self._plot_text_no_overlap(point, text, colour)

        self._plot_text_no_overlap(region.centroid, region.name, colour)

        self.ax.set_aspect("equal", adjustable="box")


def show_entities(regions):
    """Draw regions on plot.

    Parameters
    ----------
    regions : Region or list of Region
        entities to draw
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("Failed to draw geometry. Please ensure MatPlotLib is installed.")

    if not isinstance(regions, list):
        # Given a single region not a list - reformat
        regions = [regions]

    stored_coords = []

    # Some basic colours
    colours = ["red", "blue", "green", "purple"]

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    region_drawing = _RegionDrawing(ax, stored_coords)
    for i, region in enumerate(regions):
        # loop through colours once end of list reached
        while i > len(colours) - 1:
            i -= len(colours)

        region_drawing.draw_region(region, colours[i])

    plt.show()
