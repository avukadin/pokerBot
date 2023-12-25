
from typing import List
from game.Player import Player
from game.hand_strength import get_hand_strength
from game.types import Move, MoveDetails, Players


class OddsPlayer(Player):

    default_raise = 0.8
    default_call = 0.5
    strength = 0.0

    def __init__(self, player_id:int, stack:int):
        super().__init__(player_id, stack, Players.ODDS_PLAYER)

    def _select_move(self, moves:List[Move], board:List[int]) -> Move:
        self.strength = get_hand_strength(self.cards, board, len(board))
        if self.strength >= self.default_raise:
            if Move.RAISE in moves:
                return Move.RAISE
            elif Move.CALL in moves:
                return Move.CALL
            elif Move.CHECK in moves:
                return Move.CHECK
            else:
                return Move.FOLD
        elif self.strength >= self.default_call:
            if Move.CALL in moves:
                return Move.CALL
            elif Move.CHECK in moves:
                return Move.CHECK
            else:
                return Move.FOLD
        else:
            if Move.CHECK in moves:
                return Move.CHECK
            else:
                return Move.FOLD

    def _get_raise_amount(self, min_raise:int, max_raise:int) -> int:
        raise_amount = min_raise + round((max_raise - min_raise) * (self.strength - self.default_raise) / (1 - self.default_raise))
        return raise_amount
