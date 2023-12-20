from collections import deque
from enum import Enum
import random
from typing import Dict, List

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pydantic import BaseModel, confloat, conint

from game.AITrainer import AITrainer
from game.Player import Player
from game.Dealer import Dealer
from game.RandomPlayer import RandomPlayer

from game.RoundPrinter import (
    print_game_start,
    print_player_move,
    print_round,
    print_winners,
)
from game.params import MAX_PLAYERS, MIN_PLAYERS, MODE, Modes, START_STACK, OPONENT_HISTORY
from game.types import Turn, Move

prob_range = confloat(ge=0.0, le=1.0)
one_hot_range = conint(ge=0, le=1)
chips_range = conint(ge=0, le=MAX_PLAYERS*START_STACK)

# Models the state of the game and the player
class PreActionState(BaseModel):
    pre_flop_strength: prob_range = 0.0
    flop_strength: prob_range = 0.0
    turn_strength: prob_range = 0.0
    river_strength: prob_range = 0.0
    turn: List[one_hot_range] = [0, 0, 0, 0]      
    stack: chips_range = 0
    pot: chips_range = 0
    money_in_pot: chips_range = 0
    call_amount: chips_range = 0
    oponent_money_in_pot: List[chips_range] = [0] * MAX_PLAYERS
    oponent_stack: List[chips_range] = [0] * MAX_PLAYERS
    oponent_has_move_left: List[one_hot_range] = [0] * MAX_PLAYERS

# Models the play history of the oponent
class OponentModel(BaseModel):
    player_id: List[conint(ge=0, le=12)] = [0]*OPONENT_HISTORY
    pre_flop_strength: List[prob_range] = [0.0]*OPONENT_HISTORY
    flop_strength: List[prob_range] = [0.0]*OPONENT_HISTORY
    turn_strength: List[prob_range] = [0.0]*OPONENT_HISTORY
    river_strength: List[prob_range] = [0.0]*OPONENT_HISTORY
    move: List[one_hot_range] = [0]*OPONENT_HISTORY # One-hot encoding of the move [fold, check, call, raise]
    raise_amount: List[chips_range] = [0]*OPONENT_HISTORY

class PokerEnv(gym.Env):

    game:int = 0
    players:List[Player]
    player_queue:deque[Player]
    dealer:Dealer
    start_new_game:bool = True
    start_hands:Dict[int, List[int]]

    def __init__(self):
        super(PokerEnv, self).__init__()

        self.action_space = spaces.Discrete(13) #[Fold, Call/Check, Raise 1/10, Raise 2/10, ... Raise 10/10]
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)

    def step(self, action):
        while turn := self.dealer.get_next_turn():
            if turn != Turn.PREFLOP:
                self.dealer.deal_board()

            print_round(turn, self.dealer.board)
            start_round_players = len(self.player_queue)
            while len(self.player_queue) > 0 and start_round_players>1:
                player = self.player_queue.popleft()
                
                move_history = player.make_move(
                    self.dealer.last_raise,
                    self.dealer.max_opponent_stack(self.player_queue),
                    self.dealer.board,
                    action=action,
                )

                self.dealer.add_to_pot(move_history.raise_amount + move_history.call_amount)
                
                if move_history.move == Move.RAISE:
                    self.dealer.update_after_raise(self.player_queue, self.players, move_history)

                print_player_move(player, move_history, self.dealer.pot, self.start_hands[player.player_id])
            
            self.dealer.setup_for_next_round(self.player_queue, self.players)

        winners = self.dealer.distribute_pot(self.players)
        print_winners(winners, self.dealer.board, self.start_hands)

        players: List[Player] = [player for player in self.players if player.stack>0]
        self.players = players[1:] + [players[0]]
        if len(players)<=1:
            self.start_new_game = True

        return np.array([0.0, 0.0]), 0.0, True, False, {}
        
    def reset(self, seed=None):
        if self.start_new_game:
            self.start_new_game = False
            self.game += 1
            n_players = random.randint(MIN_PLAYERS, MAX_PLAYERS)
            if MODE == Modes.RANDOM_PLAY:
                self.players = [RandomPlayer(i, START_STACK) for i in range(n_players)]
            else: 
                self.players = [AITrainer(0, START_STACK)] + [RandomPlayer(i, START_STACK) for i in range(1, n_players)]
            print_game_start(self.game, n_players)

        self.dealer = Dealer()
        self.player_queue = deque(self.players)
        for player in self.player_queue:
            player.prepare_for_new_hand()

        self.dealer.collect_blinds(self.player_queue)
        self.dealer.deal_player_cards(self.player_queue)
        self.start_hands = {player.player_id: player.cards for player in self.player_queue} # For printing

        return np.array([0.0, 0.0]), {}

    def render(self, mode='human'):
        pass

    def close(self):
        pass
