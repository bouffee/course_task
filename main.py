# используемые модули
import sys
import time
from collections import defaultdict
from copy import deepcopy

import pygame

from grid_defs import Grid, Neighbours
from tkinter import filedialog

iterationNum = 0 # число итераций

# константы

TIME = 0.3 # время смены кадров

# размеры окна

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# цвета

GRID_COLOR = (230, 230, 230)
BACKGROUND_COLOR = (253, 246, 227)
CELL_COLOR = (143, 177, 204)
TEXT_COLOR = (68, 44, 46)
BORDERS_COLOR = (204, 153, 102)
BUTTON_BACKGROUND_COLOR = (255, 221, 187)
FONT_STYLE = None

# размер  клетки

CELL_SIZE = 15

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
    global iterationNum
    newCells = deepcopy(grid.cells)
    undead = defaultdict(int)
    iterationNum = iterationNum + 1

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
    for x, y in grid.cells:
        pygame.draw.rect(
            screen,
            CELL_COLOR,
            (
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            ),
        )


def makeSquares(surface: pygame.Surface):
    """
        Рисует сетку на поле
    """
    blockSize = CELL_SIZE  # Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            shapeSurf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    surface.blit(shapeSurf, rect)


def saveToFile(grid: Grid) -> None:
    """
        Сохраняет конфигурацию сетки в файл
    """
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename:
        with open(filename, "w") as f:
            for x, y in grid.cells:
                f.write(f"{x},{y}\n")

def loadFromFile(grid: Grid) -> None:
    """
        Загружает конфигурацию из сохраненного текствого файла
    """
    filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if filename:
        with open(filename, "r") as f:
            lines = f.readlines()
            newCells = set()
            for line in lines:
                coords = line.strip().split(",")
                if len(coords) == 2:
                    x, y = int(coords[0]), int(coords[1])
                    newCells.add((x, y))
            grid.dim = (WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10)
            grid.cells = newCells


def main():
    """
        Основная часть
    """
    grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + 20))  
    pygame.display.set_caption('Игра "Жизнь"')

    # переменные состояния
    isRunning = False
    mouseButtonDown = False
    allowCellPlacement = True
    status = "Заполните поле"
    global iterationNum

    # Дизайн кнопки "Старт/стоп"
    startGenerationButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 10, 170, 30)
    startGenerationButton_text = "Старт/Cтоп"

    # Дизайн кнопки "Сброс"
    resetButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 50, 170, 30)
    resetButton_text = "Сброс"

    # Дизайн кнопки "Сохранить в файл"
    saveToFileButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 90, 170, 30)
    saveToFileButton_text = "Сохранить в файл"

    loadFromFileButton_rect = pygame.Rect(WINDOW_WIDTH - 180, 130, 170, 30)
    loadFromFileButton_text = "Загрузить из файла"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if startGenerationButton_rect.collidepoint(event.pos):
                        isRunning = not isRunning
                        allowCellPlacement = False
                        status = "Идет генерация. Итераций: " if isRunning else "Пауза. Итерация: "
                    elif resetButton_rect.collidepoint(event.pos):
                        iterationNum = 0
                        isRunning = False
                        allowCellPlacement = True
                        grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())
                        status = "Заполните поле"
                    elif saveToFileButton_rect.collidepoint(event.pos):
                        if len(grid.cells) > 0:
                            saveToFile(grid)
                        else:
                            status = "Ошибка: сетка пуста"
                    elif loadFromFileButton_rect.collidepoint(event.pos):
                        iterationNum = 0
                        loadFromFile(grid)
                    else:
                        if allowCellPlacement:
                            mouseButtonDown = True
                            mousePos = pygame.mouse.get_pos()
                            cell_x = mousePos[0] // CELL_SIZE
                            cell_y = mousePos[1] // CELL_SIZE
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
                    status = "Пауза. Итерация: "

        # Заполнение фона, прорисовка сетки, заполнение сетки
        screen.fill(BACKGROUND_COLOR)
        drawGrid(screen, grid)
        makeSquares(screen)

        # кнопка "старт/стоп"
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, startGenerationButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, startGenerationButton_rect, 2)
        
        startGeneration_font = pygame.font.Font(FONT_STYLE, 24)
        startGeneration_text_surface = startGeneration_font.render(startGenerationButton_text, True, TEXT_COLOR)
        startGeneration_text_x = (startGenerationButton_rect.x + (startGenerationButton_rect.width - startGeneration_text_surface.get_width()) // 2)
        startGeneration_text_y = (startGenerationButton_rect.y + (startGenerationButton_rect.height - startGeneration_text_surface.get_height()) // 2)
        screen.blit(startGeneration_text_surface, (startGeneration_text_x, startGeneration_text_y))
        
        #кнопка "сброс"
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, resetButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, resetButton_rect, 2)

        resetButton_font = pygame.font.Font(FONT_STYLE, 24)
        resetButton_text_surface = resetButton_font.render(resetButton_text, True, TEXT_COLOR)
        resetButton_text_x = resetButton_rect.x + (resetButton_rect.width - resetButton_text_surface.get_width()) // 2
        resetButton_text_y = resetButton_rect.y + (resetButton_rect.height - resetButton_text_surface.get_height()) // 2
        screen.blit(resetButton_text_surface, (resetButton_text_x, resetButton_text_y))
        
        # кнопка "сохранить в файл"
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, saveToFileButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, saveToFileButton_rect, 2)

        saveToFile_font = pygame.font.Font(FONT_STYLE, 24)
        saveToFile_text_surface = saveToFile_font.render(saveToFileButton_text, True, TEXT_COLOR)
        saveToFile_text_x = saveToFileButton_rect.x + (saveToFileButton_rect.width - saveToFile_text_surface.get_width()) // 2
        saveToFile_text_y = saveToFileButton_rect.y + (saveToFileButton_rect.height - saveToFile_text_surface.get_height()) // 2
        screen.blit(saveToFile_text_surface, (saveToFile_text_x, saveToFile_text_y))
        
        # кнопка "загрузить из файла"
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, loadFromFileButton_rect)
        pygame.draw.rect(screen, BORDERS_COLOR, loadFromFileButton_rect, 2)

        loadFromFileButton_font = pygame.font.Font(FONT_STYLE, 24)
        loadFromFileButton_text_surface = loadFromFileButton_font.render(loadFromFileButton_text, True, TEXT_COLOR)
        loadFromFileButton_text_x = loadFromFileButton_rect.x + (loadFromFileButton_rect.width - loadFromFileButton_text_surface.get_width()) // 2
        loadFromFileButton_text_y = loadFromFileButton_rect.y + (loadFromFileButton_rect.height - loadFromFileButton_text_surface.get_height()) // 2
        screen.blit(loadFromFileButton_text_surface, (loadFromFileButton_text_x, loadFromFileButton_text_y))

        if isRunning:
            grid = updateGrid(grid)

        # Вывод статуса игры вниз экрана. 3 статуса: "заполните поле", "Пауза. Итерация: " и "Идет генерация. Итерация: " 
        statusFont = pygame.font.Font(FONT_STYLE, 24)

        # Проверка статуса для вывода числа итераций, если это необходимо
        if status is "Пауза. Итерация: " or status is "Идет генерация. Итераций: ":
            statusText_surface = statusFont.render(status + str(iterationNum), True, TEXT_COLOR)
        else:
            statusText_surface = statusFont.render(status, True, TEXT_COLOR)

        statusText_x = 10
        statusText_y = WINDOW_HEIGHT + 3
        screen.blit(statusText_surface, (statusText_x, statusText_y))

        pygame.display.flip()
        time.sleep(TIME)


if __name__ == "__main__":
    main()
