from typing import List, Dict, Optional
from treys import Deck
import random
from .Player import Player
from .types import Move
from typing import List
from treys import Card, Evaluator
from .pre_flop_rankings import PREFLOP_RANKINGS
import numpy as np


class Dealer():
    _deck: Deck
    _board: List[int]
    _n_players: int
    _last_raise: int
    _pot: int
    _button_player_id: int
    _small_player_id: int
    _big_player_id: int
    _player_turn: int

    _evaluator = Evaluator()


    def __init__(self, n_players: int):
        self._n_players = n_players
        self._button_player_id = random.randint(0, n_players - 1)

    def deal_player_cards(self):
        return self._deck.draw(2)

    def setup_table(self, players: List[Player]):
        self._deck = Deck()
        self._board = []
        self._last_raise = 0
        self._pot = 0

        self._button_player_id = self._find_next_active(players, self._button_player_id)
        self._small_player_id = self._find_next_active(players, self._button_player_id)
        self._big_player_id = self._find_next_active(players, self._small_player_id)
        self._player_turn = self._find_next_active(players, self._big_player_id)
        
    def _find_next_active(self, players: List[Player], start_loc: int) -> int:
        for i in range(start_loc + 1, self._n_players + start_loc):
            index = i % self._n_players
            player = players[index]
            if player.needs_to_play():
                return index
        raise Exception("No active players")

    def deal_board(self):
        assert len(self._board) in [0, 3, 4]

        if len(self._board) == 0:
            self._board += self._deck.draw(3)
        else:
            self._board += self._deck.draw(1)

    def add_to_pot(self, amount: int):
        self._pot += amount

    def count_remaining_players(self, players: List[Player]) -> int:
        return len([1 for player in players if player.last_move != Move.FOLD and player.stack > 0])

    def determine_winners(self, players: List[Player]) -> List[Player]:
        remaining_players = [player for player in players if player.last_move != Move.FOLD]
        if len(remaining_players) == 1:
            return remaining_players

        best_rank = np.inf
        ranks:Dict[int, float] = {}
        for player in remaining_players:
            rank = self.eval_hand(player.cards, self._board)
            ranks[player.player_id] = rank
            if rank < best_rank:
                best_rank = rank

        assert best_rank > 0
        
        winners:List[Player] = []
        for player in remaining_players:
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
        for winner in winners:
            winner.stack += pot_split

    def get_next_player_turn(self, players:List[Player]) -> Optional[Player]:
        try:
            index = self._find_next_active(players, self._player_turn)
            self._player_turn = index
            return players[index]
        except:
            return None
        
    def setup_for_next_round(self, players:List[Player]):
        for player in players:
            player.set_new_round_state()
        self._last_raise = 0

    def check_game_over(self, players:List[Player]) -> bool:
        return len([player for player in players if player.stack > 0]) == 1
    
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

