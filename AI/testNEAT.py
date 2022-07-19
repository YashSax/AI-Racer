from CarEnvironment import CarEnvironment
from car import Car
import numpy as np
import pygame

import pickle
import neat
import os

import sys
import keyboard

BLOCK_SIZE = 2
GAME_DIM = (1250, 630)
START_POS = (20, GAME_DIM[0] - 30)

BASE_DIR = "./boards/" + sys.argv[2] + "/"
board = np.load(BASE_DIR + sys.argv[2] + "_board.npy")
waypoints = np.load(BASE_DIR + sys.argv[2] + "_waypoints.npy")
bg = pygame.image.load(BASE_DIR + sys.argv[2] + ".jpeg")

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

with open("./models/" + sys.argv[1], 'rb') as f:
    genome = pickle.load(f)
net = neat.nn.FeedForwardNetwork.create(genome, config)

def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode(GAME_DIM)

    c = Car(0.4, 0.4, START_POS, board, waypoints,
            bg, BLOCK_SIZE, GAME_DIM, user="AI")
    sim = CarEnvironment(c)
    done = False
    obs = sim.reset()

    while not done:
        actions = np.array(net.activate(obs))
        def actuate(a): return a >= 0.5
        obs, reward, done, info = sim.step(actuate(actions))
        # print("Action:", actuate(actions))
        # sim.render()
    print("Reward:", reward)

if __name__ == "__main__":
    main()
