# используемые модули
import sys
import time
from collections import defaultdict
from copy import deepcopy

import pygame

from grid_defs import Grid, Neighbours

# константы
# размеры окна

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400

# цвета

GRID_COLOR = (230, 230, 230)
BACKGROUND_COLOR = (253, 246, 227)
CELL_COLOR = (143, 177, 204)
TEXT_COLOR = (68, 44, 46)
BORDERS_COLOR = (204, 153, 102)
BUTTON_BACKGROUND_COLOR = (255, 221, 187)
FONT_STYLE = None

def getNeighbours(grid: Grid, x: int, y: int) -> Neighbours:
    """
        Получает состояния соседних клеток для определенной клетки (x, y) на сетке.
    """
    offsets = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    possibleNeighbours = {(x + x_add, y + y_add) for x_add, y_add in offsets}
    alive = {(pos[0], pos[1]) for pos in possibleNeighbours if pos in grid.cells}
    return Neighbours(alive, possibleNeighbours - alive)


def updateGrid(grid: Grid) -> Grid:
    """
         Для заданной сетки функция возвращает следующую итерацию игры Жизнь.
    """
    newCells = deepcopy(grid.cells)
    undead = defaultdict(int)

    for x, y in grid.cells:
        aliveNeighbours, deadNeighbours = getNeighbours(grid, x, y)
        if len(aliveNeighbours) not in [2, 3]:
            newCells.remove((x, y))

        for pos in deadNeighbours:
            undead[pos] += 1

    for pos, _ in filter(lambda elem: elem[1] == 3, undead.items()):
        newCells.add((pos[0], pos[1]))

    return Grid(grid.dim, newCells)


def drawGrid(screen: pygame.Surface, grid: Grid) -> None:
    """
        Эта функция рисует игру Жизнь на заданной поверхности pygame.Surface.
    """
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


def makeSquares(surface: pygame.Surface):
    """
        Рисует сетку на поле
    """
    blockSize = 10  # Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            shapeSurf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    surface.blit(shapeSurf, rect)


def main():
    """
        Основная часть
    """
    grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + 20))  # Adjusted height for the status code
    pygame.display.set_caption('Игра "Жизнь"')

    # переменные состояния
    isRunning = False
    mouseButtonDown = False
    allowCellPlacement = True
    status = "Заполните поле"  

    # Дизайн кнопки "Старт/стоп"
    startGenerationButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 10, 170, 30)
    startGenerationButton_text = "Старт/Cтоп"

    # Дизайн кнопки "Сброс"
    resetButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 50, 170, 30)
    resetButton_text = "Сброс"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if startGenerationButton_rect.collidepoint(event.pos):
                        isRunning = not isRunning
                        allowCellPlacement = False
                        status = "Идет генерация" if isRunning else "Пауза"
                    elif resetButton_rect.collidepoint(event.pos):
                        isRunning = False
                        allowCellPlacement = True
                        grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())
                        status = "Заполните поле"
                    else:
                        if allowCellPlacement:
                            mouseButtonDown = True
                            mousePos = pygame.mouse.get_pos()
                            cell_x = mousePos[0] // 10
                            cell_y = mousePos[1] // 10
                            if (cell_x, cell_y) in grid.cells:
                                grid.cells.remove((cell_x, cell_y))
                            else:
                                grid.cells.add((cell_x, cell_y))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: 
                    mouseButtonDown = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    isRunning = False
                    allowCellPlacement = True
                    grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())
                    status = "Пауза"

        # Заполнение фона, прорисовка сетки, заполнение сетки
        screen.fill(BACKGROUND_COLOR)
        drawGrid(screen, grid)
        makeSquares(screen)

        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, startGenerationButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, startGenerationButton_rect, 2)

        startGeneration_font = pygame.font.Font(FONT_STYLE, 24)
        startGeneration_text_surface = startGeneration_font.render(
            startGenerationButton_text, True, TEXT_COLOR
        )
        startGeneration_text_x = (
            startGenerationButton_rect.x
            + (startGenerationButton_rect.width - startGeneration_text_surface.get_width()) // 2
        )
        startGeneration_text_y = (
            startGenerationButton_rect.y
            + (startGenerationButton_rect.height - startGeneration_text_surface.get_height()) // 2
        )
        screen.blit(startGeneration_text_surface, (startGeneration_text_x, startGeneration_text_y))

        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, resetButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, resetButton_rect, 2)

        resetButton_font = pygame.font.Font(FONT_STYLE, 24)
        resetButton_text_surface = resetButton_font.render(resetButton_text, True, TEXT_COLOR)
        resetButton_text_x = resetButton_rect.x + (resetButton_rect.width - resetButton_text_surface.get_width()) // 2
        resetButton_text_y = resetButton_rect.y + (resetButton_rect.height - resetButton_text_surface.get_height()) // 2
        screen.blit(resetButton_text_surface, (resetButton_text_x, resetButton_text_y))

        if isRunning:
            grid = updateGrid(grid)

        # Вывод статуса игры вниз экрана. 3 статуса: "заполните поле", "пауза" и "идет генерация" 
        statusFont = pygame.font.Font(FONT_STYLE, 24)
        statusText_surface = statusFont.render(status, True, TEXT_COLOR)
        statusText_x = 10
        statusText_y = WINDOW_HEIGHT + 3
        screen.blit(statusText_surface, (statusText_x, statusText_y))

        pygame.display.flip()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
