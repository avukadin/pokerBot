from game.Player import Player
from game.types import Move, Players
from typing import List
from keras.models import load_model
import numpy as np
import random
from game.params import BIG_BLIND
from ml.params import HS_MODEL_PATH, MOVE_MODEL_PATH


class AIPlayer(Player):
    def __init__(self, player_id, stack):
        self.type = Players.AI
        print("Loading models...")
        self.hs_model = load_model(HS_MODEL_PATH)
        self.move_model = load_model(MOVE_MODEL_PATH)
        print("Done")
        super().__init__(player_id, stack)

    def _select_move(self, valid_moves:List[Move], board:List[int], **kwargs) -> Move:

        X = np.array([[0]*330])
        move_probs = self.move_model.predict(X, verbose=0)
        likely_move = np.argmax(move_probs)
        move = Move(likely_move)
        if move not in valid_moves:
            move = random.choice(valid_moves)
        return move

    def _get_raise_amount(self, last_raise_amount:int, max_opponent_stack:int) -> int:
        assert self._stack > self._to_call

        max_raise = self._stack - self._to_call
        max_raise = min(max_raise, max_opponent_stack)

        last_raise_or_big_blind = max(last_raise_amount, BIG_BLIND)
        min_raise = min(last_raise_or_big_blind, self._stack - self._to_call)
        min_raise = min(min_raise, max_opponent_stack)

        assert min_raise <= max_raise and min_raise > 0

        return random.randint(min_raise, max_raise)

