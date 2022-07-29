'''
TODO: Deal with intersecting paths, when looking to increment currWaypoint, only look for the next
or previous one, not just the one you're in range of

'''

from CarEnvironment import CarEnvironment
from car import Car
import numpy as np
import multiprocessing
import os
import pickle
import neat
from tqdm import tqdm
import pygame
import random

pygame.init()
GAME_DIM = (1250, 630)
START_POS = (20, GAME_DIM[0] - 30)
BLOCK_SIZE = 2

map_names = ["tightCorner", "normal", "forks", "blocks", "loop"]
boards, waypoints_list, bgs = [], [], []

for map in map_names:
    boards.append(np.load(f"./AI/boards/{map}/{map}_board.npy"))
    waypoints_list.append(np.load(f"./AI/boards/{map}/{map}_waypoints.npy"))
    bgs.append(pygame.image.load(f"./AI/boards/{map}/{map}.jpeg"))

runs_per_net = 1
generations = 100

def eval_board(net, board, waypoints, bg):
    c = Car(0.4, 0.4, START_POS, board, waypoints, bg, BLOCK_SIZE, GAME_DIM, user="AI")
    sim = CarEnvironment(c)
    done = False
    obs = sim.reset()
    actuate = lambda a: a >= 0.5

    while not done:
        actions = np.array(net.activate(obs))
        obs, reward, done, info = sim.step(actuate(actions))
    return reward

def eval_genome(genome, config):
    # create the network based off the config file
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []

    for runs in range(runs_per_net):
        total_reward = 0
        for board, waypoints, bg in zip(boards, waypoints_list, bgs):
            total_reward += eval_board(net, board, waypoints, bg)
        fitnesses.append(total_reward)
    return min(fitnesses)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

def main():
    config_path = "./AI/config-feedforward"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))
    
    NUM_CPU_CORES = 4
    pe = neat.ParallelEvaluator(NUM_CPU_CORES, eval_genome)
    winner = pop.run(pe.evaluate,generations)

    # Save the winner.
    with open('./AI/models/multiple_map_winner', 'wb') as f:
        pickle.dump(winner, f)

    # Show winning neural network
    print(winner)

if __name__ == "__main__":
    main()