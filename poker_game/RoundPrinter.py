from typing import List, Dict
from .Player import Player
from .types import MoveDetails
from .types import Move
from treys import Card, Evaluator

round_names = {
    0: "Pre-Flop",
    1: "Flop",
    2: "Turn",
    3: "River"
}

class RoundPrinter:
    player_ids: List[int]
    pots: List[int]
    stacks: List[int]
    moves: List[MoveDetails]
    player_hands: Dict[int, List[int]]

    def __init__(self, player_hands: Dict[int, List[int]]):
        self.player_ids = []
        self.pots = []
        self.stacks = []
        self.moves = []
        self.player_hands = player_hands
    
    def write_round(self, player_id:int, stack:int, pot:int, move_details:MoveDetails):
        self.player_ids.append(player_id)
        self.pots.append(pot)
        self.stacks.append(stack)
        self.moves.append(move_details)

    def print_round(self, round_num:int, board:List[int]):

        print(f"=========================")
        print(f" {round_names[round_num]}")
        if round_num > 0:
            Card.print_pretty_cards(board)
        print(f"=========================")
        for i in range(len(self.player_ids)):
            player_id = self.player_ids[i]
            player_hand = Card.ints_to_pretty_str(self.player_hands[player_id])
            player_str = f"Player {self.player_ids[i]} with{player_hand}{self.moves[i].move.value}s"
            if self.moves[i].move == Move.FOLD:
                print(f"{player_str}. Their stack is {self.stacks[i]}.")
            elif self.moves[i].move == Move.CHECK:
                print(f"{player_str}. Their stack is {self.stacks[i]}.")
            elif self.moves[i].move == Move.CALL:
                print(f"{player_str} {self.moves[i].call_amount}. The pot is now {self.pots[i]}. Their stack is now {self.stacks[i]}.")
            elif self.moves[i].move == Move.RAISE:
                print(f"{player_str} {self.moves[i].raise_amount}. The pot is now {self.pots[i]}. Their stack is now {self.stacks[i]}.")


    def print_winners(self, winners: List[Player], board: List[int]):
        eval = Evaluator()
        print()
        print("Winners:")
        for winner in winners:
            hand = self.player_hands[winner.player_id]
            hand_result = eval.class_to_string(eval.get_rank_class(eval.evaluate(hand, board)))
            print(f"Player {winner.player_id} with {hand_result} ending with a stack of {winner.stack}")
        print()
