import neat
import sys
import pickle
import numpy as np
import pygame
import os
import visualize

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

with open("./models/" + sys.argv[1], 'rb') as f:
    genome = pickle.load(f)
net = neat.nn.FeedForwardNetwork.create(genome, config)

print(genome)

node_names = {-1:"left",-2:"right",-3:"top left",-4:"top right",-5:"front",0:"left_arr",1:"up_arr",2:"right_arr"}
visualize.draw_net(config, genome, True, node_names=node_names)