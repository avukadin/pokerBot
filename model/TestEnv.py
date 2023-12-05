import gym
from gym.spaces import Discrete, Box, Tuple, Space
from typing import Tuple, Any
import numpy as np
from numpy.random import random
import rl.agents
import tensorflow as tf


class TestEnv(gym.Env):
    total_steps: int

    def __init__(self, max_stair_size, max_steps_per_move) -> None:
        super(TestEnv, self).__init__()

        self.action_space: Space = Discrete(max_steps_per_move)

        current_step = Discrete(max_steps_on_stair)
        n_steps = Discrete(max_steps_on_stair)

        self.observation_space = Tuple([current_step, n_steps])

        self.current_step = 0

    def step(self, action: int) -> Tuple[np.array, float, bool, dict]:
        # Implement step logic
        self.current_step += action + 1

        reward = 0
        if self.current_step == self.total_steps-1:
            reward = 1
        
        done = self.current_step >= self.total_steps

        
        observation = np.array([self.current_step, self.total_steps])
        return observation, reward, done, {}

    def reset(self) -> np.array:
        self.total_steps = random.randint(1, self.action_space.n)
        self.current_step = 0


    def render(self, mode: str = 'human') -> None:
        # Render the environment
        pass

    def close(self) -> None:
        pass

