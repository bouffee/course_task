from collections import namedtuple

class Grid:
    def __init__(self, dim, cells, food=set(), diseased=set()):
        self.dim = dim
        self.cells = cells
        self.food = food  # Позиции еды
        self.diseased = diseased  # Заболевшие клетки

    def set_dimensions(self, new_dim):
        self.dim = new_dim


Dim = namedtuple("Dimension", ["width", "height"])
Neighbours = namedtuple("Neighbours", ["alive", "dead"])