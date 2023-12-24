import random
from game.PokerEnv import PokerEnv
from game.train import train
from typing import List, Dict, Deque

from pydantic import BaseModel, conlist
if __name__ == '__main__':  

    train()
    # env = PokerEnv()
    # env.reset()
    # while True:
    #     _,_,done,_,_ = env.step(random.randint(0,12))
    #     if done:
    #         env.reset()
