from .Dealer import Dealer
from .Player import Player
import random
from .params import START_STACK
from typing import List, Dict
from .types import Move
from .RoundPrinter import RoundPrinter


def play_next_hand(dealer:Dealer, players: List[Player]) -> bool:
    # Plays a full hand of poker

    for player in players:
        player.set_new_hand_state()

    dealer.setup_table(players)
    start_hands:Dict[int, List[int]] = {}
    for player in players:
        player.cards = dealer.deal_player_cards()
        start_hands[player.player_id] = player.cards

    for i in range(0,4):
        if i >= 1:
            dealer.deal_board()
        printer = RoundPrinter(player_hands=start_hands)
        player = dealer.get_next_player_turn(players)
        remaining_players = dealer.count_remaining_players(players)
        while player is not None and remaining_players > 1:
            move_history = player.make_move(dealer.last_raise, dealer.board)

            dealer.add_to_pot(move_history.raise_amount + move_history.call_amount)
            if move_history.move == Move.RAISE:
                for opponent in players:
                    if opponent.player_id != player.player_id:
                        opponent.update_after_opponent_move(move_history)
                        dealer.last_raise = move_history.raise_amount
            printer.write_round(player.player_id, player.stack, dealer.pot, move_history)
            
            player = dealer.get_next_player_turn(players)

        dealer.setup_for_next_round(players)
        printer.print_round(i, dealer.board)
    
    winners = dealer.determine_winners(players)
    dealer.distribute_pot(winners)

    printer = RoundPrinter(player_hands=start_hands)
    printer.print_winners(winners, dealer.board)

    return dealer.check_game_over(players)
    
def play(min_players: int, max_players: int, games: int):
    assert min_players > 1
    assert max_players >= min_players

    for i in range(games):
        n_players = random.randint(min_players, max_players)

        print("=========================")
        print(f"        Game {i+1}")
        print(f"      Players: {n_players}")
        print("=========================")

        dealer = Dealer(n_players)
        players = [Player(i, START_STACK) for i in range(n_players)]
        
        game_over = False
        while not game_over:
            game_over = play_next_hand(dealer, players)
