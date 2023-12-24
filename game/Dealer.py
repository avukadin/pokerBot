from collections import deque
import random
from typing import Dict, List, Optional, Set

import numpy as np
from treys import Card, Deck, Evaluator

from game.Player import Player
from game.params import BIG_BLIND, SMALL_BLIND
from game.pre_flop_rankings import PREFLOP_RANKINGS
from game.types import Move, MoveDetails, Turn, Winner


class Dealer():
    _deck: Deck
    _board: List[int]
    _last_raise: int
    _pot: int
    _max_raise: int

    _evaluator = Evaluator()
    _turn_queue: deque[Turn]

    _last_delt_turn: Optional[Turn]

    def __init__(self):
        self._deck = Deck()
        self._board = []
        self._last_raise = 0
        self._pot = 0
        self._turn_queue = deque([Turn.PREFLOP, Turn.FLOP, Turn.TURN, Turn.RIVER])
        self._last_delt_turn = None

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

    def deal_board(self, turn:Turn):
        assert len(self._board) in [0, 3, 4, 5]

        if turn == Turn.FLOP and len(self.board) == 0:
            self._board += self._deck.draw(3)
        elif turn == Turn.TURN and len(self.board) == 3:
            self._board += self._deck.draw(1)
        elif turn == Turn.RIVER and len(self.board) == 4:
            self._board += self._deck.draw(1)

    def is_start_of_round(self, turn:Turn) -> bool:
        if turn != self._last_delt_turn:
            self._last_delt_turn = turn
            return True
        return False

    def add_to_pot(self, amount: int):
        assert amount >= 0
        self._pot += amount

    def determine_winners(self, players: List[Player]) -> List[Player]:
        potential_winners = [player for player in players if player.last_move != Move.FOLD]

        if len(potential_winners) <= 1:
            return potential_winners

        ranks:Dict[int, float] = {}
        best_rank = np.inf
        for player in potential_winners:
            rank = self._eval_hand(player.cards, self._board)
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

    def distribute_pot(self, players: List[Player]) -> List[Winner]:
        p = [player for player in players if player._chips_in_pot > 0]
        hand_winnners:Dict[int,Winner] = {}
        while len(p) > 0:
            min_chips = min([player._chips_in_pot for player in p])
            for player in p:
                player._chips_in_pot -= min_chips
                self._pot -= min_chips
            winners = self.determine_winners(p)

            split_pot = len(p)*min_chips // len(winners)
            remainder = len(p)*min_chips % len(winners)
            remainder_winner = random.choice(winners).player_id
            for winner in winners:
                
                win_amount = split_pot + (remainder if winner.player_id == remainder_winner else 0)
                winner.stack += win_amount
                if winner.player_id in hand_winnners:
                    hand_winnners[winner.player_id].win_amount += win_amount
                    hand_winnners[winner.player_id].end_stack = winner.stack
                else:
                    hand_winnners[winner.player_id] = Winner(winner.player_id, win_amount, winner.stack)
 
            p = [player for player in p if player._chips_in_pot > 0] 

        return list(hand_winnners.values())

    def _eval_hand(self, hand:List[int], board:List[int]) -> float:
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

    def max_opponent_stack(self, players:List[Player]) -> int:
        if len(players) == 0:
            return 0
        return max([player.stack for player in players])

    def setup_for_next_round(self, player_queue:deque[Player], players:List[Player]):
        players_in_queue:Set[int] = {player.player_id for player in player_queue}
        for player in players:
            if player.stack > 0 and player.last_move != Move.FOLD:
                player.set_new_round_state()
                if player.player_id not in players_in_queue:
                    player_queue.append(player)
        self._turn_queue.popleft()
        self._last_raise = 0
        self._last_delt_turn = None

    def get_next_turn(self) -> Optional[Turn]:
        if len(self._turn_queue) == 0:
            return None
        return self._turn_queue[0]

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
