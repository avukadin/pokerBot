from typing import List
from stable_baselines3.common.env_checker import check_env
from game.PokerEnv import PokerEnv

from stable_baselines3 import PPO

from stable_baselines3.common.callbacks import BaseCallback


env = PokerEnv()
# check_env(env)

class CustomMetricCallback(BaseCallback):
    is_win:List[int] = []
    def __init__(self, verbose=0):
        self.render_mode = 'human'
        super(CustomMetricCallback, self).__init__(verbose)
        self.metadata = {'render_modes': ['human', 'ansi']}
        # Initialize any variables you need
        self.episodic_reward = 0

    def _on_step(self) -> bool:
        # Accumulate rewards or other metrics at each step
        reward = self.locals["rewards"][0]
        if reward == 0:
            return True
        if reward > 0:
            self.is_win.append(1)
        elif reward < 0:
            self.is_win.append(0)
        self.is_win = self.is_win[-100:]

        avg_win = float(sum(self.is_win))/float(len(self.is_win))
        self.logger.record('step/avg_win_rate', avg_win)
        print("avg_win_rate: ", avg_win)
        return True

def train():

    # Create the callback instance
    custom_callback = CustomMetricCallback()
    model = PPO("MlpPolicy", env, verbose=0,tensorboard_log="./logs/")
    model.learn(total_timesteps=100000, callback=custom_callback, log_interval=1)
