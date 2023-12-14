import gymnasium as gym
import numpy as np
from gymnasium import spaces

class CustomEnv(gym.Env):
    reward = 0
    distance_from_spot = 100
    speed = 0
    reward_history = []
    count = 0

    last_obs = 0
    last_last_obs = 0

    def __init__(self):
        super(CustomEnv, self).__init__()
        self.last_action = None
        self.observation_space = spaces.MultiDiscrete([6, 6])

        self.action_space = spaces.Discrete(2) # [press_gas, press_brake]
        self.render_mode = 'human'
        self.total_reward = 0

    def step(self, action):
        self.count += 1
        # draw a random int the range [0,6]
        done=False
        if self.count == 100:
            done = True
        if action == 0 and self.last_last_obs%2 == 0:
            self.reward = 1
        elif action == 1 and self.last_last_obs%2 == 1:
            self.reward = 1
        else:
            self.reward = 0
        draw = np.random.randint(0, 6)
        self.last_last_obs = self.last_obs
        self.last_obs = draw

        self.total_reward += self.reward

        return np.array([self.last_obs, self.last_last_obs]), self.reward, done, False, {}

    def reset(self, seed=None):
        print(self.total_reward)
        self.total_reward = 0
        self.reward = 0
        self.count = 0
        self.last_obs = 0
        self.last_last_obs = 0
        return np.array([0,0]), {}

    def render(self, mode='human'):
        screen_width = 50
        scale = screen_width / 200.0  # Assuming the total distance range is 200

        car_position = self.distance_from_spot + 100  # Offset by 100 to handle negative distances
        dot_position = int(car_position * scale)

        screen = [" "] * screen_width
        if 0 <= dot_position < screen_width:
            screen[dot_position] = "o"  # Representing the car as 'o'

        print("".join(screen) + "|")

    def close(self):
        print("ended with reward: ", self.reward)
