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
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

def getNeighbours(grid: Grid, x: int, y: int) -> Neighbours:
    """
        Gets the neighbour states for a particular cell in
        (x, y) on the grid.
    """
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    possibleNeighbours = {(x + x_add, y + y_add) for x_add, y_add in offsets}
    alive = {(pos[0], pos[1]) for pos in possibleNeighbours if pos in grid.cells}
    return Neighbours(alive, possibleNeighbours - alive)


def updateGrid(grid: Grid) -> Grid:
    """
        Given a grid, this function returns the next iteration
        of the game of life.
    """
    newCells = deepcopy(grid.cells)
    undead = defaultdict(int)

    for x, y in grid.cells:
        aliveNeighbours, deadNeighbours = getNeighbours(grid, x, y)
        if len(alive_neighbours) not in [2, 3]:
            newCells.remove((x, y))

        for pos in deadNeighbours:
            undead[pos] += 1

    for pos, _ in filter(lambda elem: elem[1] == 3, undead.items()):
        newCells.add((pos[0], pos[1]))

    return Grid(grid.dim, newCells)


def drawGrid(screen: pygame.Surface, grid: Grid) -> None:
    """
        This function draws the game of life on the given
        pygame.Surface object.
    """
    # cell_width = screen.get_width() / grid.dim.width
    # cell_height = screen.get_height() / grid.dim.height
    cellSize = 10 

    for x, y in grid.cells:
        pygame.draw.rect(
            screen,
            CELL_COLOR,
            (
                x * cellSize,
                y * cellSize,
                cellSize,
                cellSize
            ),
        )
    
def makeSquares (surface:pygame.Surface):
    blockSize = 10 # Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            shapeSurf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    surface.blit(shapeSurf, rect)

def main():
    """
        Main entry point
    """
    grid = FIELD

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_WIDTH, WINDOW_HEIGHT)
    pygame.display.set_caption('Игра "Жизнь"')

    while True:
        if pygame.QUIT in [e.type for e in pygame.event.get()]:
            sys.exit(0)

        screen.fill(BACKGROUND_COLOR)
        drawGrid(screen, grid)
        makeSquares(screen)
        grid = updateGrid(grid)
        pygame.display.flip()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
