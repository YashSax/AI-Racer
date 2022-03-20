from CarEnvironment import CarEnvironment
from car import Car
import numpy as np
import multiprocessing
import os
import pickle
import neat
from tqdm import tqdm
import pygame
pygame.init()

GAME_SIZE = 500
START_POS = (20, GAME_SIZE - 30)
BLOCK_SIZE = 2
GAME_DIM = (GAME_SIZE, GAME_SIZE)

board = np.load("./AI/boards/curved/curved_board.npy")
waypoints = np.load("./AI/boards/curved/curved_waypoints.npy")
bg = pygame.image.load('./AI/boards/curved/curved.jpeg')
SCREEN = pygame.display.set_mode(GAME_DIM)

runs_per_net = 1
generations = 10

def eval_genome(genome, config):
    # create the network based off the config file
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    fitnesses = []

    for runs in range(runs_per_net):
        c = Car(0.2, 0.2, START_POS, board, waypoints, bg, BLOCK_SIZE, GAME_DIM, user="AI", SCREEN=SCREEN)
        sim = CarEnvironment(c)
        done = False
        obs = sim.reset()

        while not done:
            actions = np.array(net.activate(obs))
            actuate = lambda a: a >= 0.5
            obs, reward, done, info = sim.step(actuate(actions))
            sim.render()
        fitnesses.append(reward)
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
    
    NUM_CPU_CORES = 1
    pe = neat.ParallelEvaluator(NUM_CPU_CORES, eval_genome)
    winner = pop.run(pe.evaluate,generations)

    # Save the winner.
    with open('winner', 'wb') as f:
        pickle.dump(winner, f)

    # Show winning neural network
    print(winner)

if __name__ == "__main__":
    main()