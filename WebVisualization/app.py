from flask import Flask, render_template, url_for, send_from_directory, request
from flask_bootstrap import Bootstrap
import json
import neat
import os
import pickle
import numpy as np
from car import Car
import ast

BLOCK_SIZE = 2
GAME_DIM = (1280, 656)
board = None

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)
try:
    with open("./big_winner", 'rb') as f:
        genome = pickle.load(f)
except Exception as e:
    print("File not found in base directory, using full path")
    with open("./WebVisualization/big2_winner", 'rb') as f:
        genome = pickle.load(f)

net = neat.nn.FeedForwardNetwork.create(genome, config)

app = Flask(__name__)
bootstrap = Bootstrap(app)

obs = [0, 0, 0, 0, 0];
actions = [-1, -2, -3]
startPredictions = False

def actuate(a):
    return np.array([bool(i) for i in a >= 0.5])

@app.route('/')
def home():
    data = {"left":0, "right":0, "up":0}
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/board', methods=['POST'])
def get_board():
    global board
    s = dict(request.form)['javascript_data'].split(",")
    board_str = ",".join(s[0:-3]).split(":")[1]
    board = ast.literal_eval(board_str)
    print(board)
    return

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    global actions
    # s, l, r, ld, rd
    obs_keys = ["angle", "x", "y"]
    s = dict(request.form)["javascript_data"]
    split_string = s.split(",")
    angle = int(split_string[-3].split(":")[-1])
    x = int(split_string[-2].split(":")[1])
    y = int(split_string[-1].split(":")[1][:-1])

    if board is not None:
        player_car = Car(0.4, 0.4, (x, y), board, None,
                None, BLOCK_SIZE, GAME_DIM, user="AI")
        player_car.angle = angle
        player_car.observe()
        actions = actuate(np.array(net.activate(player_car.obs)))
    # print("Observation:", obs)
    # print("Action:", actions)
    return render_template("index.html")

@app.route("/predictions", methods=['GET', 'POST'])
def predict():
    return render_template("predictions.html", python_input=actions);

if __name__ == "__main__":
    app.run(debug=True)