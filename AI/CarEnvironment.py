import gym
from gym import spaces
from wandb import visualize
from car import Car
import pygame


class CarEnvironment(gym.Env):
    metadata = {'render.modes':['human']}
    NUM_ACTIONS = 3

    def __init__(self, car):
        super(CarEnvironment, self).__init__()

        '''
        Action space:
            - 0: left arrow
            - 1: up arrow
            - 2: right arrow
        '''
        self.action_space = spaces.MultiBinary(self.NUM_ACTIONS)

        '''
        Observation space:
            - pixels on left until grass
            - pixels on right until grass
            - pixels on top left until grass
            - pixels on top right until grass
            - pixels straight until grass
        '''
        self.observation_space = spaces.Tuple(spaces=(
            spaces.Box(low=0, high=500, shape=(1,)), # straight distance
            spaces.Box(low=0, high=500, shape=(1,)), # left distance
            spaces.Box(low=0, high=500, shape=(1,)), # right distance
            spaces.Box(low=0, high=500, shape=(1,)), # left diagonal distance
            spaces.Box(low=0, high=500, shape=(1,)), # right diagonal distance
        ))
        self.car = car
    
    def step(self, action, visualizeObservations = False):
        self.car.step(action)
        observation = self.car.observe(visualizeObservations=visualizeObservations)
        reward = self.car.reward()
        done = self.car.checkTerminal() != "NONE"
        
        return observation, reward, done, {}

    def reset(self):
        self.car.reset()
        observation = self.car.observe()
        return observation

    def render(self, mode='human', close=False):
        self.car.draw()
        pygame.display.update()