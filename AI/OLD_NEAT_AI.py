from CarEnvironment import CarEnvironment
from car import Car
import numpy as np
# import pygame

import multiprocessing
import os
import pickle
import neat

GAME_SIZE = 500
START_POS = (20, GAME_SIZE - 30)
BLOCK_SIZE = 2
GAME_DIM = (GAME_SIZE, GAME_SIZE)

board = np.load("./AI/boards/curved/curved_board.npy")
waypoints = np.load("./AI/boards/curved/curved_waypoints.npy")
bg = None # pygame.image.load('./boards/curved/curved.jpeg')

runs_per_net = 2
generations = 100

bestReward = -1e99

def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitnesses = []
    fitness = 0.0
    
    for runs in range(runs_per_net):
        c = Car(0.2, 0.2, START_POS, board, waypoints, bg, BLOCK_SIZE, GAME_DIM, user="AI")
        sim = CarEnvironment(c)

        done = False
        observation = sim.reset()
        a = True
        while not done:
            prediction = net.activate(observation)
            binarized_prediction = [1 if i > 0.5 else 0 for i in prediction]
            observation, fitness, done, info = sim.step(binarized_prediction)
        fitnesses.append(fitness) # count num timesteps car has been in the middle

    if np.mean(fitnesses) > bestReward:
        file_name = "best_model"
        save_location = "./models/" + file_name
        with open(save_location, 'wb') as f:
            pickle.dump(genome, f)
    return np.mean(fitnesses)

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)

def run():
    # Load the config file, which is assumed to live in
    # the same directory as this script.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    pop = neat.Population(config)
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.StdOutReporter(True))

    pe = neat.ParallelEvaluator(multiprocessing.cpu_count(), eval_genome)
    winner = pop.run(pe.evaluate, generations)

    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    print(winner)


if __name__ == '__main__':
    run()
