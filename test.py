from game.PokerEnv import PokerEnv
from game.train import train
if __name__ == '__main__':  
    env = PokerEnv()
    env.reset()
    while True:
        _,_,done,_,_ = env.step(0)
        if done:
            env.reset()
