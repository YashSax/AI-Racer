import numpy as np
import pygame
from CarEnvironment import CarEnvironment
from car import Car
import sys
import random

GAME_SIZE = 500
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GRASS = (156, 175, 136)
BLOCK_SIZE = 2
ROAD = (105, 105, 105)
COLOR_RADIUS = 10
MOVE_SPEED = 0.05
TURN_SPEED = 0.1
CENTER_OFFSET = 15

GAME_DIM = (1250, 630)
START_POS = (20, GAME_DIM[0] - 20)

GRASS_CODE = 0
ROAD_CODE = 1

BASE_DIR = "./boards/" + sys.argv[1] + "/"
board = np.load(BASE_DIR + sys.argv[1] + "_board.npy")
waypoints = np.load(BASE_DIR + sys.argv[1] + "_waypoints.npy")
bg = pygame.image.load(BASE_DIR + sys.argv[1] + ".jpeg")


def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode(GAME_DIM)
    # must be at least 10 waypoints before end
    startingWaypoint = 0 # random.randint(5, len(waypoints) - 1 - 10)
    # print("choosing waypoint between 5 and", len(waypoints) - 1 - 10)
    # startingAngle = random.randint(0, 360)
    # print("StartingWaypoint:", startingWaypoint)  # waypoints[startingWaypoint]s
    # startPos =  (waypoints[startingWaypoint][0]*BLOCK_SIZE, waypoints[startingWaypoint][1]*BLOCK_SIZE)
    c = Car(0.4, 0.4, START_POS, board, waypoints, bg,
            BLOCK_SIZE, GAME_DIM, user="HUMAN", SCREEN=SCREEN, START_ANGLE=0, START_WAYPOINT=startingWaypoint)
    env = CarEnvironment(c)
    done = False
    while not done:
        SCREEN.blit(bg, (0, 0))
        ev = pygame.event.get()
        keys = pygame.key.get_pressed()
        valid_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
        actions = [key for key in valid_keys if keys[key]]
        observation, reward, done, info = env.step(actions, visualizeObservations=False)
        # print("Current Waypoint", env.car.currWaypoint)
        env.render()
    print("Score:", reward)


if __name__ == "__main__":
    main()
