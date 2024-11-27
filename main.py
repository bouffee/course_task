# используемые модули
import sys
import os
import time
import re
from collections import defaultdict
from copy import deepcopy
import pygame
from pygame.locals import *
import random

from grid_defs import Grid, Neighbours
from RLEdecode import decodeRLE
import tkinter as tk
from tkinter import filedialog

# Правила игры
ALIVE_NEIGHBOURS = [2, 3]
REVIVAL_NUMBER = [3]

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
FOOD_COLOR = (141, 205, 137)
PLAGUE_COLOR = (128, 128, 128)
FONT_STYLE = None

# константы
iterationNum = 0 # число итераций
TIME = 0.1 # время смены кадров
CELL_SIZE = 15
MIN_CELL_SIZE = 2
MAX_CELL_SIZE = 50  
SCALE_FACTOR = 1
FOOD_MODE = bool(False)
PLAGUE_MODE = bool(False)
SPREAD_CHANCE = 0.2

# вспомогательные константы для реализации долго нажатия на стрелки для передвижения по карте игры
MOVING_LEFT = False
MOVING_RIGHT = False
MOVING_UP = False
MOVING_DOWN = False


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
    newDiseased = deepcopy(grid.diseased)
    undead = defaultdict(int)
    iterationNum = iterationNum + 1

    for x, y in grid.cells:
        aliveNeighbours, deadNeighbours = getNeighbours(grid, x, y)

        if (PLAGUE_MODE):
            if (x, y) in grid.diseased:
                if random.random() < SPREAD_CHANCE:
                    for nx, ny in aliveNeighbours:
                        if (nx, ny) not in grid.diseased:
                            newDiseased.add((nx, ny))
            newCells.remove((x, y))  
            continue

        isNearFood = any((fx, fy) in grid.food for fx, fy in aliveNeighbours)
        if len(aliveNeighbours) not in ALIVE_NEIGHBOURS and not isNearFood:
            newCells.remove((x, y))

        for pos in deadNeighbours:
            undead[pos] += 1

    for pos, _ in filter(lambda elem: elem[1] in REVIVAL_NUMBER, undead.items()):
        newCells.add((pos[0], pos[1]))

    return Grid(grid.dim, newCells, grid.food, newDiseased)

def drawGrid(screen: pygame.Surface, grid: Grid) -> None:
    """
        Эта функция рисует игру Жизнь на заданной поверхности pygame.Surface.
    """
    for cell in grid.cells:
        cell_x, cell_y = cell
        rect = pygame.Rect(
            cell_x * CELL_SIZE, cell_y * CELL_SIZE, CELL_SIZE, CELL_SIZE
        )

        # Заражённые клетки серые
        if cell in grid.diseased:
            pygame.draw.rect(screen, PLAGUE_COLOR, rect)  # Серый цвет
        elif cell in grid.food:
            pygame.draw.rect(screen, FOOD_COLOR, rect)
        else:
            pygame.draw.rect(screen, CELL_COLOR, rect)  # Голубой цвет (обычная клетка)


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
    filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Text Files", "*.rle")])
    if filename and filename.endswith(".txt"):
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

    if filename and filename.endswith(".rle"):
        with open(filename, "r") as f:
            file = f.readlines()
            selectedLines = str()
            for line in file:
                if line[0:1] == "#" or line[0:1] == "x":
                    continue
                else:
                    selectedLines += line.strip()
            decodedGrid = decodeRLE(selectedLines)
            if decodedGrid:
                grid.dim = (WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10)
                grid.cells = set(decodedGrid)    

def drawButton(screen, rect, text, textSize = 24) :
    """
    Универсальная функция для прорисовки кнопок
    """
    pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, rect)
    pygame.draw.rect(screen, BORDERS_COLOR, rect, 2)

    button_font = pygame.font.Font(FONT_STYLE, textSize)
    text_surface = button_font.render(text, True, TEXT_COLOR)
    text_x = rect.x + (rect.width - text_surface.get_width()) // 2
    text_y = rect.y + (rect.height - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))

def handleKeyDown(key, grid: Grid) -> None:
    """
    Обработка движения поля
    """
    cellsToRemove = set()  # Создаем множество для отложенного удаления, чтобы избежать ошибок изменения размера во время итерации
    cellsToAdd = set()  # Создаем множество для отложенного добавления
    for cell in grid.cells:
        x, y = cell
        if key == pygame.K_UP:         
            cellsToRemove.add(cell)
            cellsToAdd.add((x, y - 1))
        if key == pygame.K_DOWN:
            cellsToRemove.add(cell)
            cellsToAdd.add((x, y + 1))
        if key == pygame.K_LEFT:
            cellsToRemove.add(cell)
            cellsToAdd.add((x - 1, y))
        if key == pygame.K_RIGHT:
            cellsToRemove.add(cell)
            cellsToAdd.add((x + 1, y))
    grid.cells -= cellsToRemove
    grid.cells |= cellsToAdd


def saveSettings(window, speedScale, gameRuleForm, foodMode, plagueMode):
    global TIME, MIN_CELL_SIZE, MAX_CELL_SIZE, ALIVE_NEIGHBOURS, REVIVAL_NUMBER, PLAGUE_MODE, FOOD_MODE
    
    if (foodMode.get()):
        FOOD_MODE = True
    else:
        FOOD_MODE = False

    if (plagueMode.get()):
        PLAGUE_MODE = True
    else: 
        PLAGUE_MODE = False

    TIME = speedScale.get()

    parsingString = gameRuleForm.get()
    match = re.match(r'^B(\d+)/S(\d+)$', parsingString) 

    if not match:
        errorWindow = tk.Tk()
        errorWindow.bell()
        screen_width = errorWindow.winfo_screenwidth()
        screen_height = errorWindow.winfo_screenheight()
        x = (screen_width/2) - (350/2)
        y = (screen_height/2) - (50/2)
        errorWindow.geometry('%dx%d+%d+%d' % (350, 50, x, y))
        errorWindow.title("Ошибка!")
        errorWindow.minsize(350, 50)
        errorWindow.maxsize(350, 50)

        errorText = tk.Label(errorWindow, text="Некорректный формат строки.\n Пожалуйста, введите правила в формате Bx/Sy.")
        errorText.place(relx=0.5, rely=0.5, anchor='center')
    
    bStr = match.group(1)
    sStr = match.group(2)

    REVIVAL_NUMBER = [int(char) for char in bStr]
    ALIVE_NEIGHBOURS = [int(char) for char in sStr]
    window.destroy()

def openSettingsWindow():
    settingsWindow = tk.Tk()
    settingsWindow.title("Настройки")
    foodMode = tk.BooleanVar(value=False)
    plagueMode = tk.BooleanVar(value=False)
    screen_width = settingsWindow.winfo_screenwidth()
    screen_height = settingsWindow.winfo_screenheight()
    x = (screen_width/2) - (380/2)
    y = (screen_height/2) - (140/2)
    settingsWindow.geometry('%dx%d+%d+%d' % (380, 140, x, y))
    settingsWindow.minsize(380, 140)
    settingsWindow.maxsize(380, 140)
    
    speedLabel = tk.Label(settingsWindow, text="Скорость симуляции (меньше = быстрее)",)
    speedLabel.grid(row=0, column=0, sticky='w')

    speedScale = tk.Scale(settingsWindow, from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, length=122)
    speedScale.set(0.1)
    speedScale.grid(row=0, column=1, sticky='w')

    gameRuleLabel = tk.Label(settingsWindow, text="Правила для симуляции")
    gameRuleLabel.grid(row=1, column=0, sticky='w')

    gameRuleForm = tk.Entry()
    gameRuleForm.insert(0, f"B{"".join([f"{i}" for i in REVIVAL_NUMBER])}/S{"".join([f"{i}" for i in ALIVE_NEIGHBOURS])}")
    gameRuleForm.grid(row=1, column=1, sticky='w')

    foodForm = tk.Checkbutton(settingsWindow, text="Добавить пищу в симуляцию", variable=foodMode)
    foodForm.grid(row=2, column=0, sticky='w')

    plagueForm = tk.Checkbutton(settingsWindow, text="Добавить болезни в симуляцию", variable=plagueMode)
    plagueForm.grid(row=3, column=0, sticky='w')
    
    # кнопка сохранения настроек
    saveButton = tk.Button(settingsWindow, text="Сохранить", command=lambda: saveSettings(settingsWindow, speedScale, gameRuleForm, foodMode, plagueMode))
    saveButton.grid(row=4, columnspan=2)

    settingsWindow.mainloop()

def handleFoodPlacement(grid: Grid, pos) -> None:
    """
    Добавляет или удаляет еду по щелчку мыши.
    """
    cell_x, cell_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
    if (cell_x, cell_y) in grid.food:
        grid.food.remove((cell_x, cell_y))
    else:
        grid.food.add((cell_x, cell_y))

def handleDiseasePlacement(grid: Grid, pos) -> None:
    """
    Делает клетку зараженной по щелчку мыши.
    """
    cell_x, cell_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
    if (cell_x, cell_y) in grid.cells:
        if (cell_x, cell_y) in grid.diseased:
            # Убираем болезнь, если она уже есть
            grid.diseased.remove((cell_x, cell_y))
        else:
            # Добавляем болезнь
            grid.diseased.add((cell_x, cell_y))
    else:
        # Чтобы клетка могла быть зараженной, она должна быть живой
        grid.cells.add((cell_x, cell_y))
        grid.diseased.add((cell_x, cell_y))

def main():
    """
        Основная часть
    """
    global CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, MOVING_DOWN, MOVING_LEFT, MOVING_RIGHT, MOVING_UP, TIME

    grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set())

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), RESIZABLE)
    pygame.display.set_caption('Игра "Жизнь"')

    # переменные состояния
    isRunning = False
    allowCellPlacement = True
    status = "Заполните поле"
    global iterationNum

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Колесо вниз 
                    CELL_SIZE = min(MAX_CELL_SIZE, CELL_SIZE + SCALE_FACTOR)
                elif event.button == 5:  # Колесо вверх
                    CELL_SIZE = max(MIN_CELL_SIZE, CELL_SIZE - SCALE_FACTOR)
                if event.button == 1: 
                    if startButton_rect.collidepoint(event.pos):
                        isRunning = not isRunning
                        allowCellPlacement = False
                        status = "Идет генерация. Итераций: " if isRunning else "Пауза. Итерация: "
                    elif resetButton_rect.collidepoint(event.pos):
                        iterationNum = 0
                        isRunning = False
                        allowCellPlacement = True
                        grid = Grid((WINDOW_WIDTH // 10, WINDOW_HEIGHT // 10), set()) # очищение поля
                        status = "Заполните поле"
                    elif saveToFileButton_rect.collidepoint(event.pos):
                        if len(grid.cells) > 0:
                            saveToFile(grid)
                        else:
                            status = "Ошибка: сетка пуста"
                    elif loadFromFileButton_rect.collidepoint(event.pos):
                        isRunning = False
                        iterationNum = 0
                        loadFromFile(grid)
                    elif settings_rect.collidepoint(event.pos):
                        isRunning = False
                        openSettingsWindow()
                    else:
                        if allowCellPlacement:
                            mousePos = pygame.mouse.get_pos()
                            if FOOD_MODE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                # Добавляем еду при зажатом Shift
                                handleFoodPlacement(grid, mousePos)
                            elif PLAGUE_MODE and pygame.key.get_mods() & pygame.KMOD_CTRL:
                                # Добавляем болезнь при зажатом Ctrl
                                handleDiseasePlacement(grid, mousePos)
                            else:
                                # По умолчанию добавляем обычную клетку
                                cell_x = mousePos[0] // CELL_SIZE
                                cell_y = mousePos[1] // CELL_SIZE
                                if (cell_x, cell_y) in grid.cells:
                                    grid.cells.remove((cell_x, cell_y))
                                    grid.diseased.discard((cell_x, cell_y))  # Удаляем клетку из болезненных, если она есть
                                else:
                                    grid.cells.add((cell_x, cell_y))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    MOVING_LEFT = True
                elif event.key == pygame.K_RIGHT:
                    MOVING_RIGHT = True
                elif event.key == pygame.K_UP:
                    MOVING_UP = True
                elif event.key == pygame.K_DOWN:
                    MOVING_DOWN = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    MOVING_LEFT = False
                elif event.key == pygame.K_RIGHT:
                    MOVING_RIGHT = False
                elif event.key == pygame.K_UP:
                    MOVING_UP = False
                elif event.key == pygame.K_DOWN:
                    MOVING_DOWN = False
            elif event.type == VIDEORESIZE:
                WINDOW_WIDTH, WINDOW_HEIGHT = event.size
                screen = pygame.display.set_mode(event.size, RESIZABLE)
            elif event.type == VIDEOEXPOSE:
                # screen.blit(pygame.transform.scale(event.dict['size']), (0,0))
                screen.fill(BACKGROUND_COLOR)
                makeSquares(screen)
                pygame.display.update()

        if MOVING_LEFT:
            handleKeyDown(pygame.K_LEFT, grid)
        elif MOVING_RIGHT:
            handleKeyDown(pygame.K_RIGHT, grid)
        elif MOVING_UP:
            handleKeyDown(pygame.K_UP, grid)
        elif MOVING_DOWN:
            handleKeyDown(pygame.K_DOWN, grid)
        
        # Заполнение фона, прорисовка сетки, заполнение сетки
        screen.fill(BACKGROUND_COLOR)
        drawGrid(screen, grid)
        makeSquares(screen)

        # кнопка "старт/стоп"
        startButton_rect = pygame.Rect(WINDOW_WIDTH * min(0.9, (WINDOW_WIDTH - 180) / WINDOW_WIDTH), min(WINDOW_HEIGHT * 0.02, 10), 170, 30)
        startButton_text = "Старт/Cтоп"
        drawButton(screen, startButton_rect, startButton_text)
        
        # кнопка "сброс"
        resetButton_rect = pygame.Rect(WINDOW_WIDTH * min(0.9, (WINDOW_WIDTH - 180) / WINDOW_WIDTH), min(WINDOW_HEIGHT * 0.08, 50), 170, 30)
        resetButton_text = "Сброс"
        drawButton(screen, resetButton_rect, resetButton_text)
        
        # кнопка "сохранить в файл"
        saveToFileButton_rect = pygame.Rect(WINDOW_WIDTH * min(0.9, (WINDOW_WIDTH - 180) / WINDOW_WIDTH), min (WINDOW_HEIGHT * 0.14, 90), 170, 30)
        saveToFileButton_text = "Сохранить в файл"
        drawButton(screen, saveToFileButton_rect, saveToFileButton_text)
        
        # кнопка "загрузить из файла"
        loadFromFileButton_rect = pygame.Rect(WINDOW_WIDTH * min(0.9, (WINDOW_WIDTH - 180) / WINDOW_WIDTH), min(WINDOW_HEIGHT * 0.2, 130), 170, 30)
        loadFromFileButton_text = "Загрузить из файла"
        drawButton(screen, loadFromFileButton_rect, loadFromFileButton_text)

        # кнопка "Настройки"
        settings_rect = pygame.Rect(WINDOW_WIDTH * min(0.9, (WINDOW_WIDTH - 180) / WINDOW_WIDTH), min(WINDOW_HEIGHT * 0.26, 170), 170, 30)
        settings_text = "Настройки"
        drawButton(screen, settings_rect, settings_text)

        if isRunning:
            grid = updateGrid(grid)

        # Вывод статуса игры вниз экрана. 3 статуса: "заполните поле", "Пауза. Итерация: " и "Идет генерация. Итерация: " 
        statusFont = pygame.font.Font(FONT_STYLE, 24)

        # Проверка статуса для вывода числа итераций, если это необходимо
        if status == "Пауза. Итерация: " or status == "Идет генерация. Итераций: ":
            statusText_surface = statusFont.render(status + str(iterationNum), True, TEXT_COLOR)
        else:
            statusText_surface = statusFont.render(status, True, TEXT_COLOR)

        statusText_x = WINDOW_WIDTH * 0.01
        statusText_y = WINDOW_HEIGHT - statusText_surface.get_height() - 5

        # фон для статус бара
        status_bar_background = pygame.Surface((WINDOW_WIDTH, statusText_y + 10))
        status_bar_background.fill(BACKGROUND_COLOR)
        screen.blit(status_bar_background, (0, statusText_y - 5))
        screen.blit(statusText_surface, (statusText_x, statusText_y))

        pygame.display.flip()
        time.sleep(TIME)


if __name__ == "__main__":
    main()