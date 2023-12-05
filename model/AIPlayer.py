from typing import List
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
from keras.models import Sequential
from keras.layers import Dense, Activation

from poker_game.Player import Player

class AIPlayer(Player):
    
    _model:Sequential

    _raise_intervals:List[float]
    _n_actions:int

    def __init__(self, player_id:int, stack:int, raise_interval:float):
        assert raise_interval > 0 and raise_interval <= 1
        super().__init__(player_id, stack)
        self._raise_intervals = [i*raise_interval for i in range(0, int(1/raise_interval))]

        # Array from 0 to 1 by raise_interval
        self._raise_intervals = [i*raise_interval for i in range(0, int(1/raise_interval))]
        self.n_actions = 3 + len(self._raise_intervals) # fold, call, check and the raise intervals

    def build_model(self):
        model: Sequential = Sequential()
        model.add(Dense(16, input_shape=(1,)))
        model.add(Activation('relu'))
        model.add(Activation('relu'))
        ...

    def build_agent(self):
        policy = BoltzmannQPolicy()
        memory = SequentialMemory(limit=50000, window_length=1)
        dqn = DQNAgent(model=self._model, memory=memory, policy=policy, nb_actions=3, nb_steps_warmup=10, target_model_update=1e-2)



