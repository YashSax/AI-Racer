import pygame
from pygame import draw
import numpy as np
import sys

GAME_SIZE = 500
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GRASS = (156, 175, 136)
BLOCK_SIZE = 2
NUM_BLOCKS = GAME_SIZE / BLOCK_SIZE
ROAD = (105, 105, 105)
COLOR_RADIUS = 20

GRASS_CODE = 0
ROAD_CODE = 1

colorMap = {GRASS_CODE: GRASS, ROAD_CODE: ROAD}

board = np.zeros((GAME_SIZE, GAME_SIZE))
waypoints = []

FPS_CLOCK = pygame.time.Clock()

def drawGrid():
    for row in range(GAME_SIZE):
        for col in range(GAME_SIZE):
            color = board[row][col]
            colorBlock(row, col, color)

def colorBlock(row, col, color):
    board[row][col] = color
    baseRowCoord = row * BLOCK_SIZE
    baseColCoord = col * BLOCK_SIZE
    pygame.draw.rect(SCREEN, colorMap[color], pygame.Rect(baseRowCoord, baseColCoord,
                                                          baseRowCoord + BLOCK_SIZE, baseColCoord + BLOCK_SIZE))

def main():
    name = sys.argv[1]
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
    print("Press and hold right click to save board and waypoints")
    while True:
        ev = pygame.event.get()
        if (pygame.mouse.get_pressed()[0] == 1):
            xPos, yPos = pygame.mouse.get_pos()
            xPos //= BLOCK_SIZE
            yPos //= BLOCK_SIZE
            waypoints.append([xPos, yPos])
            colorNear(xPos, yPos, ROAD_CODE)
        if (pygame.mouse.get_pressed()[2] == 1):
            print("Saving board and waypoints")
            np.save(name + "_board.npy", board)
            print("Board dim: " + str(board.shape))
            np.save(name + "_waypoints.npy", np.array(waypoints))
            pygame.image.save(SCREEN, name + ".jpeg")
        drawGrid()
        pygame.display.update()
        FPS_CLOCK.tick(60)

def colorNear(xPos, yPos, color):
    for row in range(len(board)):
        for col in range(len(board[0])):
            if ((xPos - row)**2 + (yPos - col)**2) <= COLOR_RADIUS**2:
                colorBlock(row, col, color)


if __name__ == "__main__":
    main()
