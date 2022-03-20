import numpy as np
import pygame
from CarEnvironment import CarEnvironment
from car import Car

'''
Maybe visualize what the car sees -- different inputs to NN
'''

GAME_SIZE = 500
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
GRASS = (156, 175, 136)
BLOCK_SIZE = 2
NUM_BLOCKS = GAME_SIZE / BLOCK_SIZE
ROAD = (105, 105, 105)
COLOR_RADIUS = 10
MOVE_SPEED = 0.05
TURN_SPEED = 0.1
CENTER_OFFSET = 15

START_POS = (20, GAME_SIZE - 20)
GAME_DIM = (GAME_SIZE, GAME_SIZE)

GRASS_CODE = 0
ROAD_CODE = 1

board = np.load("./boards/curved/curved_board.npy")
waypoints = np.load("./boards/curved/curved_waypoints.npy")
bg = pygame.image.load('./boards/curved/curved.jpeg')

def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
    c = Car(0.2, 0.2, START_POS, board, waypoints, bg, BLOCK_SIZE, GAME_DIM, user="HUMAN", SCREEN=SCREEN)
    env = CarEnvironment(c)
    done = False
    while not done:
        SCREEN.blit(bg, (0,0))
        ev = pygame.event.get()
        keys = pygame.key.get_pressed()
        valid_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
        actions = [key for key in valid_keys if keys[key]]
        observation, reward, done, info = env.step(actions)
        env.render()
    print("Score:", reward)
    
if __name__ == "__main__":
    main()