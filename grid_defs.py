from collections import namedtuple

class Grid:
    def __init__(self, dim, cells):
        self.dim = dim
        self.cells = cells

    def set_dimensions(self, new_dim):
        self.dim = new_dim


Dim = namedtuple("Dimension", ["width", "height"])
Neighbours = namedtuple("Neighbours", ["alive", "dead"])