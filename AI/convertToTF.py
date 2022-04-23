import pickle
import os
import sys
import neat
from tf_neat.recurrent_net import RecurrentNet

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

with open("./models/" + sys.argv[1], 'rb') as f:
    genome = pickle.load(f)

from tf_neat.cppn import create_cppn

cppn_nodes = create_cppn(genome, config, ["left","right","top_left","top_right","straight"], ["left_arr","up_arr","right_arr"])
print(cppn_nodes)