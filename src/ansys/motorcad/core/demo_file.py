"""Function for ``Motor-CAD geometry`` not attached to Motor-CAD instance."""


class Region:
    """Python representation of Motor-CAD geometry region."""

    def __init__(self):
        """Create geometry region and set parameters to defaults."""
        self.name = ""
        self.material = "air"
        self.colour = (0, 0, 0)
        self.area = 0.0
        self.centroid = Coordinate(0, 0)
        self.region_coordinate = Coordinate(0, 0)
        self.duplications = 1
        self.entities = []
