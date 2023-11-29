from collections import deque
from typing import List, Dict, Optional, Set
from treys import Deck
import random
from .Player import Player
from .types import Move, MoveDetails
from typing import List
from treys import Card, Evaluator
from .pre_flop_rankings import PREFLOP_RANKINGS
import numpy as np
from .params import BIG_BLIND, SMALL_BLIND
from queue import Queue



class Dealer():
    _deck: Deck
    _board: List[int]
    _last_raise: int
    _pot: int

    _evaluator = Evaluator()

    def __init__(self):
        self._deck = Deck()
        self._board = []
        self._last_raise = 0
        self._pot = 0

    def deal_player_cards(self, players:deque[Player]):
        for player in players:
            player.cards = self._deck.draw(2)

    def collect_blinds(self, players:deque[Player]):
        small_blind = -2%len(players)
        big_blind = -1%len(players)

        amount = players[small_blind].post_small_blind(BIG_BLIND, SMALL_BLIND)
        self.add_to_pot(amount)
            
        amount = players[big_blind].post_big_blind(BIG_BLIND)
        self.add_to_pot(amount)

        for i in range(len(players)):
            if i in [small_blind, big_blind]:
                continue
            players[i].add_to_call(BIG_BLIND)

    def deal_board(self):
        assert len(self._board) in [0, 3, 4]

        if len(self._board) == 0:
            self._board += self._deck.draw(3)
        else:
            self._board += self._deck.draw(1)

    def add_to_pot(self, amount: int):
        assert amount >= 0
        self._pot += amount

    def determine_winners(self, players: List[Player]) -> List[Player]:
        potential_winners = [player for player in players if player.last_move != Move.FOLD]

        if len(potential_winners) == 1:
            return potential_winners

        best_rank = np.inf
        ranks:Dict[int, float] = {}
        for player in potential_winners:
            rank = self.eval_hand(player.cards, self._board)
            ranks[player.player_id] = rank
            if rank < best_rank:
                best_rank = rank

        assert best_rank != np.inf
        
        winners:List[Player] = []
        for player in potential_winners:
            if ranks[player.player_id] == best_rank:
                winners.append(player)

        assert len(winners) > 0

        return winners

    def eval_hand(self, hand:List[int], board:List[int]) -> float:
        assert len(hand) == 2
        assert len(board)>= 0 and len(board) <= 5
        if len(board) == 0:
            hand_sorted = sorted([hand[0], hand[1]], reverse=True)

            card_1 = Card.int_to_pretty_str(hand_sorted[0])[1:3]
            card_2 = Card.int_to_pretty_str(hand_sorted[1])[1:3]

            if card_1[1] != card_2[1]:
                return PREFLOP_RANKINGS[card_1[0] + card_2[0]]
            else:
                return PREFLOP_RANKINGS[card_1[0] + card_2[0] + "s"]

        else:
            value = self._evaluator.evaluate(hand, board)
            return self._evaluator.get_five_card_rank_percentage(value)

    def distribute_pot(self, winners: List[Player]):
        assert len(winners) > 0
        pot_split = self._pot // len(winners)
        remainder = self._pot - pot_split * len(winners)
        for winner in winners:
            winner.stack += pot_split
        remainder_winner = random.choice(winners)
        remainder_winner.stack += remainder

    def get_next_player_turn(self, players:deque[Player]) -> Player:
        return players.popleft()

    def setup_for_next_round(self, player_queue:deque[Player], players:List[Player]):
        players_in_queue:Set[int] = {player.player_id for player in player_queue}
        for player in players:
            if player.stack > 0 and player.last_move != Move.FOLD:
                player.set_new_round_state()
                if player.player_id not in players_in_queue:
                    player_queue.append(player)
        self._last_raise = 0

    def update_after_raise(self, player_queue:deque[Player], players:List[Player], move_details:MoveDetails):
        players_in_queue:Set[int] = {player.player_id for player in player_queue}
        for player in players:
            if player.player_id != move_details.player_id and player.stack > 0 and player.last_move != Move.FOLD:
                player.last_move = Move.NIL
                player.add_to_call(move_details.raise_amount)
                if player.player_id not in players_in_queue:
                    player_queue.append(player)
        self._last_raise = move_details.raise_amount

    @property
    def board(self):
        return self._board
    
    @property
    def last_raise(self):
        return self._last_raise

    @property
    def pot(self):
        return self._pot

    @last_raise.setter
    def last_raise(self, value: int):
        assert value > 0
        self._last_raise = value
