from tensorflow import keras
import numpy as np
import pygame
from car import Car
import sys
from CarEnvironment import CarEnvironment

global model
model = keras.models.load_model(sys.argv[1])

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

colorMap = {GRASS_CODE: GRASS, ROAD_CODE: ROAD}

board = np.load("./boards/curved/curved_board.npy")
waypoints = np.load("./boards/curved/curved_waypoints.npy")
bg = pygame.image.load('./boards/curved/curved.jpeg')

def predict(obs):
    reshaped_obs = obs.reshape(1,6)
    prediction = np.absolute(model.predict(reshaped_obs)[0])
    norm_prediction = prediction / np.linalg.norm(np.array(prediction))
    binarized_prediction = [1 if i >= 0.5 else 0 for i in norm_prediction]
    return binarized_prediction

def main():
    global SCREEN
    pygame.init()
    SCREEN = pygame.display.set_mode((GAME_SIZE, GAME_SIZE))
    c = Car(0.2, 0.2, START_POS, board, waypoints, bg, BLOCK_SIZE, GAME_DIM, user="AI")
    env = CarEnvironment(c)
    observation = env.reset()
    while True:
        SCREEN.blit(bg, (0,0))
        ev = pygame.event.get()
        predicted_action = predict(observation)
        print("Predicted Action:", predicted_action)
        observation, fitness, done, info = env.step(predicted_action)
        terminal = c.checkTerminal()
        if (terminal != "NONE"):
            print("Terminal state:", terminal)
            break
        c.draw()
        pygame.display.update()

if __name__ == "__main__":
    main()
