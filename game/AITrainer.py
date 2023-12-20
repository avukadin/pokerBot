from typing import List

from game.Player import Player
from game.types import Actions, Move, MoveDetails, Players


class AITrainer(Player):
    chosen_action:int
    chosen_raise_amount: int

    type = Players.AI_TRAINER

    def __init__(self, player_id, stack):
        super().__init__(player_id, stack)

    def make_move(self, last_raise_amount:int, max_opponent_stack:int, board:List[int], **kwargs) -> MoveDetails:
        self.chosen_action = kwargs['action']
        return super().make_move(last_raise_amount, max_opponent_stack, board, **kwargs)

    def _select_move(self, moves:List[Move]) -> Move:
        action_chosen = self.chosen_action
        move_chosen:Move
        if action_chosen == Actions.FOLD.value:
            if Move.FOLD in moves:
                move_chosen = Move.FOLD
            elif Move.CHECK in moves:
                move_chosen = Move.CHECK
            else:
                raise Exception("Invalid action chosen")
        elif action_chosen == Actions.CALL.value:
            if Move.CALL in moves:
                move_chosen = Move.CALL
            elif Move.CHECK in moves:
                move_chosen = Move.CHECK
            else:
                raise Exception("Invalid action chosen")
        elif action_chosen >= Actions.RAISE_1.value:
            if Move.RAISE in moves:
                move_chosen = Move.RAISE
            elif Move.CALL in moves:
                move_chosen = Move.CALL
            elif Move.CHECK in moves:
                move_chosen = Move.CHECK
            else:
                raise Exception("Invalid action chosen")
            self.chosen_raise_amount = int(round(float(self._stack)*(float(action_chosen)-1)/10,0))

        return move_chosen

    def _get_raise_amount(self, min_raise, max_raise) -> int:
        return max(min_raise, min(max_raise, self.chosen_raise_amount))
