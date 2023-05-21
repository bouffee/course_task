"""
    Pygame of life module. Contains the short engine
    to simluate the grid of life.
"""

import sys
import time
from collections import defaultdict
from copy import deepcopy

import pygame

from input_grid import FIELD
from grid_defs import Grid, Neighbours

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_COLOR = (0,104,90)
BACKGROUND_COLOR = (0, 160, 138)
CELL_COLOR = (246,0,24)

def get_neighbours(grid: Grid, x: int, y: int) -> Neighbours:
    """
        Gets the neighbour states for a particular cell in
        (x, y) on the grid.
    """
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    possible_neighbours = {(x + x_add, y + y_add) for x_add, y_add in offsets}
    alive = {(pos[0], pos[1]) for pos in possible_neighbours if pos in grid.cells}
    return Neighbours(alive, possible_neighbours - alive)


def update_grid(grid: Grid) -> Grid:
    """
        Given a grid, this function returns the next iteration
        of the game of life.
    """
    new_cells = deepcopy(grid.cells)
    undead = defaultdict(int)

    for x, y in grid.cells:
        alive_neighbours, dead_neighbours = get_neighbours(grid, x, y)
        if len(alive_neighbours) not in [2, 3]:
            new_cells.remove((x, y))

        for pos in dead_neighbours:
            undead[pos] += 1

    for pos, _ in filter(lambda elem: elem[1] == 3, undead.items()):
        new_cells.add((pos[0], pos[1]))

    return Grid(grid.dim, new_cells)


def draw_grid(screen: pygame.Surface, grid: Grid) -> None:
    """
        This function draws the game of life on the given
        pygame.Surface object.
    """
    # cell_width = screen.get_width() / grid.dim.width
    # cell_height = screen.get_height() / grid.dim.height
    cell_size = 10 
    border_size = 0

    for x, y in grid.cells:
        pygame.draw.rect(
            screen,
            CELL_COLOR,
            (
                x * cell_size,
                y * cell_size,
                cell_size,
                cell_size
            ),
        )
    
def make_squares (surface:pygame.Surface):
    blockSize = 10 #Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            shape_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    surface.blit(shape_surf, rect)

def main():
    """
        Main entry point
    """
    grid = FIELD

    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption('Игра "Жизнь"')

    while True:
        if pygame.QUIT in [e.type for e in pygame.event.get()]:
            sys.exit(0)

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen, grid)
        make_squares(screen)
        grid = update_grid(grid)
        pygame.display.flip()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
