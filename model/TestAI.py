from keras.models import Sequential
from keras.layers import Dense, Activation
from rl.agents import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

class TestAI:

    def __init__(self, n_actions:int):
      self.build_model(n_actions)

    def build_model(self, n_actions:int):
        model: Sequential = Sequential()
        model.add(Dense(16, input_shape=(1,)))
        model.add(Activation('relu'))
        model.add(Dense(n_actions))

        self._model = model
 
    def build_agent(self):
        policy = BoltzmannQPolicy()
        memory = SequentialMemory(limit=50000, window_length=1)
        dqn = DQNAgent(model=self._model, memory=memory, policy=policy, nb_actions=3, nb_steps_warmup=10, target_model_update=1e-2)

        return dqn
