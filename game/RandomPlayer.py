
import random
from game.Player import Player
from game.types import Players

class RandomPlayer(Player):
    type = Players.RANDOM

    def _select_move(self, moves):
        random_move = random.choice(moves)
        return random_move
