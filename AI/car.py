import pygame
from utils import blit_rotate_center
import math
import numpy as np

# TODO: make car start facing next waypoint

class Car:
    def __init__(self, max_vel, rotation_vel, startPos, board, waypoints, background, BLOCK_SIZE, GAME_DIM, user="HUMAN", SCREEN=None, START_ANGLE=0, START_WAYPOINT = 0):
        self.startPos = startPos
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = START_ANGLE
        self.x, self.y = startPos
        self.board = board
        self.waypoints = waypoints
        self.background = background
        self.BLOCK_SIZE = BLOCK_SIZE
        # startingWaypoint used for training where cars start at a 
        # random position in the road to avoid overfitting
        self.startingWaypoint = START_WAYPOINT
        self.currWaypoint = 0 

        self.GAME_DIM = GAME_DIM
        self.SCREEN = SCREEN

        self.ROAD_CODE = 1
        self.GRASS_CODE = 0
        
        self.MAX_TIME = 50000
        self.CENTER_OFFSET = 15
        self.acceleration = 0.001
        self.user = user
        if (user == "HUMAN"):
            try:
                self.img = pygame.image.load("./AI/player_car.png")
            except:
                self.img = pygame.image.load("./player_car.png")
            self.keybind_dict = {pygame.K_LEFT:"left", pygame.K_RIGHT:"right", pygame.K_UP:"up"}
        elif (user == "AI"):
            try:
                self.img = pygame.image.load("./AI/car.png")
            except:
                self.img = pygame.image.load("./car.png")
            actions = ["left","right","up"]
            self.actionMap = lambda a : [actions[i] for i in range(len(a)) if a[i] == 1]
        else:
            raise ValueError("Inappropriate USER argument, must be either \"HUMAN\" or \"AI\"")
        
        self.INCREMENT_GRANULARITY = 2 # accuracy of observations - higher = faster but less accurate
        self.timestep = 0
        self.stallingFor = 0 # number of timesteps where no actions have occured   
        self.stallsUntilDone = 2500 # number of timesteps stalled causes sim to end

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel
        self.angle %= 360

    def draw(self):
        if self.SCREEN is None:
            print("self.SCREEN == None, initiating new screen")
            pygame.init()
            self.SCREEN = pygame.display.set_mode(self.GAME_DIM)
        self.SCREEN.blit(self.background, (0,0))
        blit_rotate_center(self.SCREEN, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal
        
        w, h = self.GAME_DIM
        self.y = max(0, self.y)
        self.x = max(0, self.x)
        self.y = min(self.y, h - 30)
        self.x = min(self.x, w - 30)

        WAYPOINT_THRESH = 20
        for idx, waypoint in enumerate(self.waypoints):
            if self.distance((self.x // self.BLOCK_SIZE, self.y // self.BLOCK_SIZE), waypoint) <= WAYPOINT_THRESH:
                self.currWaypoint = idx

        # if self.currWaypoint < len(self.waypoints) and self.distance((self.x // self.BLOCK_SIZE, self.y // self.BLOCK_SIZE), tuple(self.waypoints[self.currWaypoint])) <= 40:
        #     self.currWaypoint += 1

    def reduce_speed(self):
        self.vel -= self.acceleration
        self.vel = max(self.vel, 0)
        self.move()
    
    def step(self, actions):
        prevPos = (self.x, self.y)
        carMoved = False
        mappedActions = actions if self.user == "HUMAN" else self.actionMap(actions)
        for action in mappedActions:
            mappedAction = self.keybind_dict[action] if self.user == "HUMAN" else action
            if mappedAction == "left":
                self.rotate(left=True)
            if mappedAction == "right":
                self.rotate(right=True)
            if mappedAction == "up":
                carMoved = True
                self.move_forward()
        if not carMoved:
            self.reduce_speed()
        self.timestep += 1
        afterPos = (self.x, self.y)
        self.stallingFor = self.stallingFor + 1 if prevPos == afterPos else 0
    
    def reward(self):
        # TODO: reward for facing the direction you're supposed to be going in
        completionPercentage = (self.currWaypoint - self.startingWaypoint) / (len(self.waypoints) - self.startingWaypoint)
        reward = 0
        correctDirection = False
        if self.currWaypoint < len(self.waypoints) - 1: # check if there is a next waypoint
            first_leg = self.distance((self.x // self.BLOCK_SIZE, self.y // self.BLOCK_SIZE), tuple(self.waypoints[self.currWaypoint]))
            second_leg = self.distance(tuple(self.waypoints[self.currWaypoint]), tuple(self.waypoints[self.currWaypoint + 1]))
            reward += second_leg / (second_leg + first_leg)

            targetAngle = math.atan2(self.waypoints[self.currWaypoint + 1][1] - self.waypoints[self.currWaypoint][1], \
                self.waypoints[self.currWaypoint + 1][0] - self.waypoints[self.currWaypoint][0])
            targetAngle = abs(np.rad2deg(targetAngle) - 90) % 180
            angleDiff = abs(targetAngle - self.angle) % 180
            if (angleDiff <= 20 or angleDiff >= 160):
                correctDirection = True
        else:
            correctDirection = True
        winBonus = 20 if self.checkTerminal() == "WIN" else 0
        completionBonus = 20 * completionPercentage
        timePenalty = self.timestep * 0.001
        reward += max(0, winBonus + completionBonus - timePenalty)
        return reward
    
    def checkTerminal(self):
        if self.stallingFor >= self.stallsUntilDone:
            return "LOSE"
        if self.timestep >= self.MAX_TIME:
            return "LOSE"
        if self.board[int((self.x + self.CENTER_OFFSET) // self.BLOCK_SIZE)][int((self.y + self.CENTER_OFFSET) // self.BLOCK_SIZE)] != self.ROAD_CODE:
            return "LOSE"
        xPos = int((self.x + self.CENTER_OFFSET) // self.BLOCK_SIZE)
        yPos = int((self.y + self.CENTER_OFFSET) // self.BLOCK_SIZE)
        if xPos >= (self.GAME_DIM[0] // self.BLOCK_SIZE - 20) and yPos <= 20:
            return "WIN"
        return "NONE"

    def inBoard(self, pos, padded=True):
        w, h = self.GAME_DIM
        paddedVal = 30 if padded else 0
        if (pos[0] >= 0 and pos[0] <= w - paddedVal and pos[1] >= 0 and pos[1] <= h - paddedVal):
            return True
        return False
    
    def observe(self, visualizeObservations=False):
        def getDistanceByIncrement(pos, increment):
            adjustedIncrement = tuple([self.INCREMENT_GRANULARITY * i for i in increment])
            currPos = pos
            while self.inBoard(currPos, padded=False) and self.board[int(currPos[0] // self.BLOCK_SIZE)][int(currPos[1] // self.BLOCK_SIZE)] != self.GRASS_CODE:
                currPos = tuple(map(lambda x, y: x + y, currPos, adjustedIncrement))
            if visualizeObservations:
                pygame.draw.circle(self.SCREEN, (200, 0, 0), currPos, 3)
            return self.distance(pos, currPos) // self.BLOCK_SIZE
        
        straightXIncrement = -1*math.sin(math.radians(self.angle))
        straightYIncrement = -1*math.cos(math.radians(self.angle))
        straightDistance = getDistanceByIncrement((self.x, self.y), (straightXIncrement, straightYIncrement))
        rightDistance = getDistanceByIncrement((self.x, self.y), (-1 * straightYIncrement, straightXIncrement))
        leftDistance = getDistanceByIncrement((self.x, self.y), (straightYIncrement, -1 * straightXIncrement))
        sqrt2by2 = math.sqrt(2) / 2
        rightDiagonalIncrement = (sqrt2by2 * (straightXIncrement - straightYIncrement), sqrt2by2 * (straightXIncrement + straightYIncrement))
        rightDiagonalDistance = getDistanceByIncrement((self.x, self.y), rightDiagonalIncrement)
        leftDiagonalIncrement = (sqrt2by2 * (straightXIncrement + straightYIncrement), -1 * sqrt2by2 * (straightXIncrement - straightYIncrement))
        leftDiagonalDistance = getDistanceByIncrement((self.x, self.y), leftDiagonalIncrement)
        obs = [straightDistance, leftDistance, rightDistance, leftDiagonalDistance, rightDiagonalDistance]
        self.obs = np.array(obs)
        if visualizeObservations:
            for waypoint in self.waypoints:
                adjusted_waypoint = (self.BLOCK_SIZE * waypoint[0], self.BLOCK_SIZE * waypoint[1])
                pygame.draw.circle(self.SCREEN, (0, 0, 200), adjusted_waypoint, 3)
            pygame.display.update()

            if (self.currWaypoint + 1 < len(self.waypoints)):
                a = self.waypoints[self.currWaypoint + 1]
                a[0] *= self.BLOCK_SIZE
                a[1] *= self.BLOCK_SIZE
                pygame.draw.circle(self.SCREEN, (0, 200,200), a, 3)
            pygame.display.update()

        return self.obs
    
    def reset(self):
        self.x, self.y = self.startPos
        self.currWaypoint = 0
        self.angle = 0
        self.timestep = 0
        self.vel = 0
    
    def distance(self, p1, p2):
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5
        
        
