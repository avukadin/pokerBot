from typing import List
from stable_baselines3.common.env_checker import check_env
from game.PokerEnv import PokerEnv

from stable_baselines3 import PPO, A2C

from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.logger import configure

tmp_path = "./tmp/sb3_log/"
# set up logger
new_logger = configure(tmp_path, ["stdout", "csv", "tensorboard"])


env = PokerEnv()
check_env(env)

# class CustomMetricCallback(BaseCallback):
#     is_win:List[int] = []
#     def __init__(self, verbose=0):
#         self.render_mode = 'human'
#         super(CustomMetricCallback, self).__init__(verbose)
#         self.metadata = {'render_modes': ['human', 'ansi']}
#         # Initialize any variables you need
#         self.episodic_reward = 0
#
#     def _on_step(self) -> bool:
#         # Accumulate rewards or other metrics at each step
#         reward = self.locals["rewards"][0]
#         if reward == 0:
#             return True
#         if reward > 0:
#             self.is_win.append(1)
#         elif reward < 0:
#             self.is_win.append(0)
#         self.is_win = self.is_win[-100:]
#
#         avg_win = float(sum(self.is_win))/float(len(self.is_win))
#         print(avg_win)
#         self.logger.record('step/avg_win_rate', avg_win)
#         print("avg_win_rate: ", avg_win)
#         return True

def train():

    # Create the callback instance
    # custom_callback = CustomMetricCallback()
    model = A2C("MlpPolicy", env, verbose=1)
    model.set_logger(new_logger)
    model.learn(total_timesteps=100000)
