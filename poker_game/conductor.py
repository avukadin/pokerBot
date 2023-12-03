from .Dealer import Dealer
from .Player import Player
import random
from .params import START_STACK, BIG_BLIND, SMALL_BLIND
from typing import List, Dict
from .types import Move
from .RoundPrinter import print_game_start, print_round, print_winners, print_player_move
from collections import deque


def play_next_hand(players: List[Player]) -> List[Player]:
    # Plays a full hand of poker
    start_amount = sum([player.stack for player in players])

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

        print_round(i, dealer.board)
        start_round_players = len(player_queue)
        while len(player_queue) > 0 and start_round_players>1:
            player = dealer.get_next_player_turn(player_queue)
            move_history = player.make_move(
                dealer.last_raise,
                dealer.max_opponent_stack(player_queue),
                dealer.board
            )
            dealer.add_to_pot(move_history.raise_amount + move_history.call_amount)
             
            if move_history.move == Move.RAISE:
                dealer.update_after_raise(player_queue, players, move_history)

            print_player_move(player, move_history, dealer.pot, start_hands[player.player_id])
 
        dealer.setup_for_next_round(player_queue, players)

    winners = dealer.distribute_pot(players)
    print_winners(winners, dealer.board, start_hands)

    remaining_players: List[Player] = [player for player in players if player.stack>0]

    end_amount = sum([player.stack for player in players])
    assert start_amount == end_amount, f"Start amount: {start_amount}, end amount: {end_amount}"
    return remaining_players
    
def play(min_players: int, max_players: int, games: int):
    assert min_players > 1
    assert max_players >= min_players

    for i in range(games):
        n_players = random.randint(min_players, max_players)
        print_game_start(i, n_players)
        players: List[Player] = [Player(i, START_STACK) for i in range(n_players)]

        while len(players) >= 2:
            players = play_next_hand(players)

