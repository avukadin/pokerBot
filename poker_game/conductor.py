from .Dealer import Dealer
from .Player import Player
import random
from .params import START_STACK, BIG_BLIND, SMALL_BLIND
from typing import List, Dict
from .types import Move
from .RoundPrinter import RoundPrinter
from collections import deque


def play_next_hand(players: List[Player], to_print:bool) -> List[Player]:
    # Plays a full hand of poker

    dealer = Dealer()
    player_queue = deque(players)

    for player in player_queue:
        player.prepare_for_new_hand()

    dealer.collect_blinds(player_queue)
    dealer.deal_player_cards(player_queue)

    # For printing
    start_hands:Dict[int, List[int]] = {player.player_id: player.cards for player in player_queue}

    for i in range(0,4):
        if i >= 1:
            dealer.deal_board()

        printer = RoundPrinter(player_hands=start_hands, enabled=to_print)
        start_round_players = len(player_queue)
        while len(player_queue) > 0 and start_round_players>1:
            player = dealer.get_next_player_turn(player_queue)
            move_history = player.make_move(dealer.last_raise, dealer.board)
            dealer.add_to_pot(move_history.raise_amount + move_history.call_amount)
            
            printer.write_round(player.player_id, player.stack, dealer.pot, move_history)
            
            if move_history.move == Move.RAISE:
                dealer.update_after_raise(player_queue, players, move_history)
 
        dealer.setup_for_next_round(player_queue, players)
        printer.print_round(i, dealer.board)
    
    winners = dealer.determine_winners(players)
    dealer.distribute_pot(winners)

    printer = RoundPrinter(player_hands=start_hands, enabled=to_print)
    printer.print_winners(winners, dealer.board)
    remaining_players: List[Player] = [player for player in players if player.stack>0]

    return remaining_players
    
def play(min_players: int, max_players: int, games: int, printer: bool = True):
    assert min_players > 1
    assert max_players >= min_players

    for i in range(games):
        n_players = random.randint(min_players, max_players)

        if printer:
            print("=========================")
            print(f"        Game {i+1}")
            print(f"      Players: {n_players}")
            print("=========================")

        players: List[Player] = [Player(i, START_STACK) for i in range(n_players)]

        while len(players) >= 2:
            players = play_next_hand(players, printer)

