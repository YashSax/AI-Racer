from flask import Flask, render_template, url_for, send_from_directory, request
from flask_bootstrap import Bootstrap
import neat
import os
import pickle

BLOCK_SIZE = 2
GAME_DIM = (1280, 656)
board = None

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config-feedforward')
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)
try:
    with open("./fixed_pos_winner", 'rb') as f:
        genome = pickle.load(f)
except Exception as e:
    print("File not found in base directory, using full path")
    with open("./WebVisualization/fixed_pos_winner", 'rb') as f:
        genome = pickle.load(f)

net = neat.nn.FeedForwardNetwork.create(genome, config)

app = Flask(__name__)
bootstrap = Bootstrap(app)

obs = [0, 0, 0, 0, 0];
actions = [-1, -2, -3]
startPredictions = False

def actuate(a):
    return [bool(i >= 0.5) for i in a]

@app.route('/')
def home():
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
    actions = actuate(net.activate(obs))
    return render_template("index.html")

@app.route("/predictions", methods=['GET', 'POST'])
def predict():
    return render_template("predictions.html", python_input=actions);

if __name__ == "__main__":
    app.run(debug=True)