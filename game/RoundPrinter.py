from typing import List, Dict
from .Player import Player
from .types import MoveDetails, Turn, Winner
from .types import Move
from treys import Card, Evaluator
from .params import PRINTER

round_names = {
    0: "Pre-Flop",
    1: "Flop",
    2: "Turn",
    3: "River"
}

move_names = {
    Move.FOLD: "Fold",
    Move.CHECK: "Check",
    Move.CALL: "Call",
    Move.RAISE: "Raise"
}

eval = Evaluator()

def print_game_start(game_number:int, n_players:int):
    if not PRINTER:
        return
    print("=========================")
    print(f"        Game {game_number}")
    print(f"      Players: {n_players}")
    print("=========================")

def print_player_move(player:Player, move:MoveDetails, pot:int, player_hand:List[int]):
    if not PRINTER:
        return
    player_hand_str = Card.ints_to_pretty_str(player_hand)
    player_str = f"Player {player.player_id} with{player_hand_str}{move_names[move.move]}s"
    if move.move in [Move.FOLD, Move.CHECK]:
        print(f"{player_str} Their stack is {player.stack}.")
    elif move.move == Move.CALL:
        print(f"{player_str} {move.call_amount}. The pot is now {pot}. Their stack is now {player.stack}.")
    elif move.move in [Move.CALL, Move.RAISE]:
        call_str = f" and calls {move.call_amount}" if move.call_amount > 0 else ""
        print(f"{player_str} {move.raise_amount}{call_str}. The pot is now {pot}. Their stack is now {player.stack}.")

def print_round(turn:Turn, board:List[int]):
    if not PRINTER:
        return
    print(f"=========================")
    print(f" {round_names[turn.value]}")
    if turn != Turn.PREFLOP:
        Card.print_pretty_cards(board)
    print(f"=========================")


def print_winners(winners: List[Winner], board: List[int], player_hands: Dict[int, List[int]]):
    if not PRINTER:
        return
    print()
    print("Winners:")
    for winner in winners:
        hand = player_hands[winner.player_id]
        hand_result = eval.class_to_string(eval.get_rank_class(eval.evaluate(hand, board)))
        print(f"Player {winner.player_id} won {winner.win_amount} with {hand_result}, ending with a stack of {winner.end_stack}")
    print()
