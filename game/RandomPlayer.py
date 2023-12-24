
import random
from game.Player import Player
from game.types import Players

class RandomPlayer(Player):
    type = Players.RANDOM

    def __init__(self, player_id, stack):
        super().__init__(player_id, stack, Players.RANDOM)

    def _select_move(self, moves):
        random_move = random.choice(moves)
        return random_move
