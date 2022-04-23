import sys
from CarEnvironment import CarEnvironment
from car import Car
from utils import blit_rotate_center
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

board = np.load("./AI/boards/curved/curved_board.npy")
waypoints = np.load("./AI/boards/curved/curved_waypoints.npy")
bg = pygame.image.load('./AI/boards/curved/curved.jpeg')

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

BASE_DIR = "./AI/models/"
model_dirs = ["player" if model_dir == "player" else BASE_DIR + model_dir for model_dir in sys.argv[1:]]

def actuate(a): return a >= 0.5

def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
   
    sims = []
    nets = []
    for car_dir in model_dirs:
        # Car objects
        player_tag = "player" if car_dir == "player" else "AI"
        c = Car(0.2, 0.2, START_POS, board, waypoints,
            bg, BLOCK_SIZE, GAME_DIM, user=player_tag)
        sim = CarEnvironment(c)
        sims.append(sim)
        
        # Genomes
        with open(car_dir, 'rb') as f:
            genome = pickle.load(f)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
    
    allDone = False
    observations = [sim.reset() for sim in sims]
    statuses = [False for _ in sims]
    while not all(statuses):
        SCREEN.blit(bg, (0, 0))
        for idx, (net, sim) in enumerate(zip(nets, sims)):
            obs = observations[idx]
            actions = np.array(net.activate(obs))
            observations[idx], reward, done, info = sim.step(actuate(actions))
            if done:
                statuses[idx] = True
            # display
            blit_rotate_center(SCREEN, sim.car.img, (sim.car.x, sim.car.y), sim.car.angle)

if __name__ == "__main__":
    main()
