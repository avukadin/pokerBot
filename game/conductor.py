from game.Dealer import Dealer
from game.Player import Player
import random
from game.RandomPlayer import RandomPlayer
from game.AIPlayer import AIPlayer
from game.params import START_STACK
from typing import List, Dict
from game.types import Move, MoveDetails
from game.RoundPrinter import print_game_start, print_round, print_winners, print_player_move
from collections import deque
from ml.make_train_data import MOVES
from ml.model import Hand, Meta, PlayerInfo
from datetime import datetime
from treys import Card


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
    hand_data = get_new_hand_data(players)

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
            update_hand_data(hand_data, player, move_history, i)

            print_player_move(player, move_history, dealer.pot, start_hands[player.player_id])
 
        dealer.setup_for_next_round(player_queue, players)

    winners = dealer.distribute_pot(players)
    print_winners(winners, dealer.board, start_hands)

    remaining_players: List[Player] = [player for player in players if player.stack>0]

    end_amount = sum([player.stack for player in players])
    assert start_amount == end_amount, f"Start amount: {start_amount}, end amount: {end_amount}"

    # Rotate players
    remaining_players = remaining_players[1:] + remaining_players[:1]
    return remaining_players

def get_new_hand_data(players: List[Player]) -> Hand:

    player_meta:Dict[str, PlayerInfo] = {}
    for player in players:
        player_meta[str(player.player_id)] = PlayerInfo(
            pocket_cards=[],
            bankroll=player.stack
        )
    meta = Meta(
        players=player_meta,
        board=[]
    )

    hand_data = Hand(
        player_order=[],
        moves=[],
        stage=[],
        bets=[],
        to_call=[],
        raise_amount=[],
        hand_strength=[],
        meta=meta,
        time=datetime.now().isoformat()
    )

    return hand_data

move_map = {
    Move.FOLD: 'f',
    Move.CALL: 'c',
    Move.RAISE: 'r',
    Move.CHECK: 'k'
}
def update_hand_data(hand_data:Hand, player:Player, move_history:MoveDetails, stage:int) -> None:
    hand_data.player_order.append(str(player.player_id))
    hand_data.moves.append(move_map[move_history.move])
    hand_data.stage.append(stage)
    hand_data.bets.append(move_history.raise_amount + move_history.call_amount)
    hand_data.to_call.append(player.to_call)
    hand_data.raise_amount.append(move_history.raise_amount)
    hand_data.hand_strength.append(-1)
    
def play(min_players: int, max_players: int, games: int):
    assert min_players > 1
    assert max_players >= min_players

    for i in range(games):
        n_players = random.randint(min_players, max_players)
        print_game_start(i, n_players)
        players: List[Player] = [AIPlayer(0,START_STACK)] + [RandomPlayer(i, START_STACK) for i in range(1, n_players)]
        random.shuffle(players)

        while len(players) >= 2:
            players = play_next_hand(players)

if __name__ == "__main__":
    play(2, 8, 10)
