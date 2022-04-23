from flask import Flask, render_template, url_for, send_from_directory, request
from flask_bootstrap import Bootstrap
import json
import neat
import os
import pickle
import numpy as np

BLOCK_SIZE = 2
GAME_DIM = (1250, 630)
START_POS = (20, GAME_DIM[0] - 30)

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

with open("./big_winner", 'rb') as f:
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

@app.route('/postmethod', methods = ['POST'])
def get_post_javascript_data():
    global actions
    # s, l, r, ld, rd
    obs_keys = ["javascript_data[s]", "javascript_data[l]", "javascript_data[r]", "javascript_data[ld]", "javascript_data[rd]"]
    obs = [float(dict(request.form)[k]) for k in obs_keys]
    print("Python Full Observation:", dict(request.form))
    print("Python Observation:", obs)
    actions = actuate(np.array(net.activate(obs)))
    print("Action:", actions)
    return render_template("index.html")

@app.route("/predictions", methods=['GET', 'POST'])
def predict():
    return render_template("predictions.html", python_input=actions);

if __name__ == "__main__":
    app.run(debug=True)