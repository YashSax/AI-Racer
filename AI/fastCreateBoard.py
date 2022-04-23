from turtle import color
import pygame
from pygame import draw
import numpy as np
import sys
import time
import os

GAME_DIM = (1250, 630)
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GRASS = (156, 175, 136)
ROAD = (105, 105, 105)
BLOCK_SIZE = 2
COLOR_RADIUS = 20

GRASS_CODE = 0
ROAD_CODE = 1

colorMap = {GRASS_CODE: GRASS, ROAD_CODE: ROAD}

board = np.zeros(GAME_DIM)
waypoints = []

FPS_CLOCK = pygame.time.Clock()

def colorBlock(row, col, color):
    board[row][col] = color

def drawPath():
    rows = []
    cols = []
    for row in range(GAME_DIM[1]):
        for col in range(GAME_DIM[0]):
            color = board[int(row // BLOCK_SIZE)][int(row // BLOCK_SIZE)]
            if color == ROAD_CODE:
                rows.append(row)
                cols.append(col)

def main():
    name = sys.argv[1]
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode(GAME_DIM)
    print("Press and hold right click to save board and waypoints")
    SCREEN.fill(colorMap[GRASS_CODE])
    while True:
        ev = pygame.event.get()
        if (pygame.mouse.get_pressed()[0] == 1):
            xPos, yPos = pygame.mouse.get_pos()
            xPos //= BLOCK_SIZE
            yPos //= BLOCK_SIZE
            waypoints.append([xPos, yPos])
            colorNear(xPos, yPos, ROAD_CODE)
        if (pygame.mouse.get_pressed()[2] == 1):
            break
        pygame.display.update()
        FPS_CLOCK.tick(10)
    drawPath()
    if not os.path.isdir("./boards/" + name):
        os.mkdir("./boards/"+name)
    print("Saving board and waypoints")
    np.save("./boards/" + name + "/" + name + "_board.npy", board)
    print("Board dim: " + str(board.shape))
    np.save("./boards/" + name + "/" + name + "_waypoints.npy", np.array(waypoints))
    pygame.image.save(SCREEN, "./boards/" + name + "/" + name + ".jpeg")

def colorNear(xPos, yPos, color):
    for row in range(xPos - COLOR_RADIUS, xPos + COLOR_RADIUS):
        for col in range(yPos - COLOR_RADIUS, yPos + COLOR_RADIUS):
            if (col >= 0 and col < len(board[0]) and row >= 0 and row < len(board)):
                if ((xPos - row)**2 + (yPos - col)**2) <= COLOR_RADIUS**2:
                    colorBlock(row, col, color)
                    pygame.draw.rect(SCREEN, colorMap[color], pygame.Rect(row * BLOCK_SIZE, col * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 2, 1)


if __name__ == "__main__":
    main()
