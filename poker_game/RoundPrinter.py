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

eval = Evaluator()

def print_player_move(player:Player, move:MoveDetails, pot:int, player_hand:List[int]):
    player_hand_str = Card.ints_to_pretty_str(player_hand)
    player_str = f"Player {player.player_id} with{player_hand_str}{move.move.value}s"
    if move.move in [Move.FOLD, Move.CHECK]:
        print(f"{player_str}. Their stack is {player.stack}.")
    elif move.move in [Move.CALL, Move.RAISE]:
        amount = move.call_amount if move.move == Move.CALL else move.raise_amount
        print(f"{player_str} {amount}. The pot is now {pot}. Their stack is now {player.stack}.")

def print_round(round_num:int, board:List[int]):
    print(f"=========================")
    print(f" {round_names[round_num]}")
    if round_num > 0:
        Card.print_pretty_cards(board)
    print(f"=========================")


def print_winners(winners: List[Player], board: List[int], player_hands: Dict[int, List[int]]):
    print()
    print("Winners:")
    for winner in winners:
        hand = player_hands[winner.player_id]
        hand_result = eval.class_to_string(eval.get_rank_class(eval.evaluate(hand, board)))
        print(f"Player {winner.player_id} with {hand_result} ending with a stack of {winner.stack}")
    print()
