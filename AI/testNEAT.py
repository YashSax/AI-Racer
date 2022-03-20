from CarEnvironment import CarEnvironment
from car import Car
import numpy as np
import pygame

import pickle
import neat
import os

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

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

with open("./winner-feedforward", 'rb') as f:
    genome = pickle.load(f)
net = neat.nn.FeedForwardNetwork.create(genome, config)


def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))

    c = Car(0.2, 0.2, START_POS, board, waypoints,
            bg, BLOCK_SIZE, GAME_DIM, user="AI")
    sim = CarEnvironment(c)
    done = False
    obs = sim.reset()

    while not done:
        actions = np.array(net.activate(obs))
        def actuate(a): return a >= 0.5
        obs, reward, done, info = sim.step(actuate(actions))
        sim.render()
        print("Reward:", reward)


if __name__ == "__main__":
    main()
