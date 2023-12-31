
import random
from typing import List
from game.Player import Player
from game.types import Move, Players
from game.params import BIG_BLIND

class RandomPlayer(Player):

    def __init__(self, player_id, stack):
        self.type = Players.RANDOM
        super().__init__(player_id, stack)

    def _select_move(self, valid_moves:List[Move], board:List[int]) -> Move:
        random_move = random.choice(valid_moves)
        return random_move

    def _get_raise_amount(self, last_raise_amount:int, max_opponent_stack:int) -> int:
        assert self._stack > self._to_call

        max_raise = self._stack - self._to_call
        max_raise = min(max_raise, max_opponent_stack)

        last_raise_or_big_blind = max(last_raise_amount, BIG_BLIND)
        min_raise = min(last_raise_or_big_blind, self._stack - self._to_call)
        min_raise = min(min_raise, max_opponent_stack)

        assert min_raise <= max_raise and min_raise > 0

        return random.randint(min_raise, max_raise)

