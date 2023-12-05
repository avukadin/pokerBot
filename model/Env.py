import gym
from gym import spaces
from typing import Tuple, Any
import numpy as np
import rl.agents
import tensorflow as tf
from .params import RAISE_INTERVAL

class PokerEnv(gym.Env):
    def __init__(self, n_opponents) -> None:
        super(PokerEnv, self).__init__()
        n_actions = 3 + int(1/RAISE_INTERVAL)

        self.action_space: spaces.Space = spaces.Discrete(n_actions)

        self.observation_space = spaces.MultiDiscrete([n_opponents, n_actions])

    def step(self, action: int) -> Tuple[np.array, float, bool, dict]:
        # Implement step logic
        ...
        observation: np.array = ...
        reward: float = ...
        done: bool = ...
        info: dict = {}
        return observation, reward, done, info

    def reset(self) -> np.array:
        # Reset environment
        ...
        observation: np.array = ...
        return observation

    def render(self, mode: str = 'human') -> None:
        # Render the environment
        pass

    def close(self) -> None:
        pass

# Create and test your environment
env: CustomEnv = CustomEnv()
...

# Integrate with Keras-RL2
agent: keras_rl2.agents.DQNAgent = keras_rl2.agents.DQNAgent(...)
agent.compile(...)
agent.fit(env, ...)

