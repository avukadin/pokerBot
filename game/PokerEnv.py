from collections import deque
import random
from typing import Dict, List, Optional

import numpy as np
import requests
from treys import Card

from game.AITrainer import AITrainer
from game.Dealer import Dealer
from game.Player import Player
from game.RandomPlayer import RandomPlayer
from game.RoundPrinter import (
    print_game_start,
    print_player_move,
    print_round,
    print_winners,
)
from game.params import (
    MAX_PLAYERS,
    MIN_PLAYERS,
    MODE,
    Modes,
    OPONENT_HISTORY,
    START_STACK,
)
from game.pre_flop_rankings import PREFLOP_RANKINGS
from game.types import Move, MoveDetails, Players, Turn
import gymnasium as gym
from gymnasium import spaces
from pydantic import BaseModel, confloat, conint

prob_range = confloat(ge=-1.0, le=1.0)
one_hot_range = conint(ge=0, le=1)
chips_range = conint(ge=0, le=MAX_PLAYERS*START_STACK)
opponent_range = conint(ge=0, le=MAX_PLAYERS)

# Models the state of the game and the player
class PreActionState(BaseModel):
    pre_flop_strength: prob_range = -1.0
    flop_strength: prob_range = -1.0
    turn_strength: prob_range = -1.0
    river_strength: prob_range = -1.0
    turn: one_hot_range = [0, 0, 0, 0]      
    stack: chips_range = 0
    pot: chips_range = 0
    money_in_pot: chips_range = 0
    call_amount: chips_range = 0
    oponent_money_in_pot: chips_range = [0] * MAX_PLAYERS
    oponent_stack: chips_range = [0] * MAX_PLAYERS
    oponent_has_move_left: one_hot_range = [0] * MAX_PLAYERS
    legal_moves: one_hot_range = [0]*4 # [Fold, Check, Call, Raise]

# Models the play history of the oponent
class OpponentModel(BaseModel):
    player_id: opponent_range = deque([[0]*MAX_PLAYERS]*OPONENT_HISTORY)
    preflop_strength: prob_range = deque([0.0]*OPONENT_HISTORY)
    flop_strength: prob_range = deque([0.0]*OPONENT_HISTORY)
    turn_strength: prob_range = deque([0.0]*OPONENT_HISTORY)
    river_strength: prob_range = deque([0.0]*OPONENT_HISTORY)

class MoveHistory(BaseModel):
    player_id: opponent_range = deque([[0]*MAX_PLAYERS]*OPONENT_HISTORY)
    move: one_hot_range = deque([[0]*4]*OPONENT_HISTORY) # [Fold, Check, Call, Raise]
    raise_amount: chips_range = deque([0]*OPONENT_HISTORY)
    call_amount: chips_range = deque([0]*OPONENT_HISTORY)
    stack_after_move: chips_range = deque([0]*OPONENT_HISTORY)
    chips_in_pot_after_move: chips_range = deque([0]*OPONENT_HISTORY)

class PokerEnv(gym.Env):

    game:int = 0
    players:List[Player]
    player_queue:deque[Player]
    dealer:Dealer
    start_new_game:bool = True
    start_hands:Dict[int, List[int]]
    start_round_players:int = 0

    flattened_observation:np.ndarray
    move_history:MoveHistory = MoveHistory()
    opponent_model:OpponentModel = OpponentModel()

    players_at_turn:List[int] = [0]*4 # [Pre-flop, Flop, Turn, River]
    start_stack:int = 0
    lower_limits:List[float]
    upper_limits:List[float]

    rewards = []
    def __init__(self):
        super(PokerEnv, self).__init__()

        self.action_space = spaces.Discrete(13) #[Fold, Call/Check, Raise 1/10, Raise 2/10, ... Raise 10/10]
        self.observation_space = self._get_observation_space()

    def step(self, action):
        obs, reward, done = self._itterate_hand(action)
        return obs, reward, done, False, {}
    
    def _get_observation_space(self):
        self.lower_limits = []
        self.upper_limits = [] 

        models = [PreActionState, OpponentModel, MoveHistory]
        for model in models:
            self._get_limits(model)
        return spaces.Box(low=np.array(self.lower_limits), high=np.array(self.upper_limits), dtype=np.float32)
    
    def _get_limits(self, model):
        fields = list(model.model_fields.keys())
        for field in fields:
            field_info = model.model_fields[field]
            value = field_info.default
            self._append_limits(value, field_info)

    def _append_limits(self, value, field_info):
        if type(value) in [list, deque]:
            for v in value:
                self._append_limits(v, field_info)
        else:
            self.lower_limits.append(field_info.metadata[1].ge)
            self.upper_limits.append(field_info.metadata[1].le)


    def _itterate_hand(self, action:Optional[int]=None):
        while turn := self.dealer.get_next_turn():
            self.dealer.deal_board(turn)
            self.players_at_turn[turn.value] = len(self.players)

            if self.dealer.is_start_of_round(turn):
                self.start_round_players = len(self.player_queue)
                print_round(turn, self.dealer.board)
            
            while self.start_round_players > 1 and len(self.player_queue) > 0:
                player = self.player_queue.popleft()
                opponents = [p for p in self.players if p.last_move != Move.FOLD and player.player_id != p.player_id]

                if player.type == Players.AI_TRAINER and action is None:
                    pre_action_state = self._get_pre_action_state(player, self.dealer.board, turn, opponents)
                    self.player_queue.appendleft(player)
                    obs = self._get_flattened_observations(pre_action_state)
                    return obs, 0.0, False
                
                move_history = player.make_move(
                        self.dealer.last_raise,
                        self.dealer.max_opponent_stack(opponents),
                        self.dealer.board,
                        action=action,
                    )
                if player.type == Players.AI_TRAINER:
                    action = None
                    
                self.dealer.add_to_pot(move_history.raise_amount + move_history.call_amount)
                
                if move_history.move == Move.RAISE:
                    self.dealer.update_after_raise(self.player_queue, self.players, move_history)

                print_player_move(player, move_history, self.dealer.pot, self.start_hands[player.player_id])

                self._update_move_history(player, move_history)
    
            self.dealer.setup_for_next_round(self.player_queue, self.players)

        winners = self.dealer.distribute_pot(self.players)
        self._update_opponent_model(self.players, self.dealer.board)
        print_winners(winners, self.dealer.board, self.start_hands)

        players: List[Player] = [player for player in self.players if player.stack>0]
        self.players = players[1:] + [players[0]]
        if len(players)<=1 or 0 not in [player.player_id for player in players]:
            self.start_new_game = True

        pre_action_state = PreActionState()
        obs = self._get_flattened_observations(pre_action_state)
        reward = self.get_stack(self.players, 0) - self.start_stack
        if reward != 0.0:
            self.rewards.append(reward)
            self.rewards = self.rewards[-100:]
            print("avg reward: ", sum(self.rewards)/len(self.rewards))
        return obs, reward, True
    
    def get_stack(self, players:List[Player], player_id:int) -> int:
        stacks = [player.stack for player in players if player.player_id == player_id]
        if len(stacks) == 0:
            return 0
        return stacks[0]

    def _get_pre_action_state(self, player:Player, board:List[int], turn:Turn, opponents:List[Player]) -> PreActionState:
        pre_action_state = PreActionState()

        n_opponents = len(opponents) 
        turns = [i for i in range(4) if i>=turn.value]
        if 0 in turns:
            pre_action_state.pre_flop_strength = self._get_hand_strength(player.cards, board, n_opponents, 0)
        if 1 in turns:
            pre_action_state.flop_strength = self._get_hand_strength(player.cards, board, n_opponents, 3)
        if 2 in turns:
            pre_action_state.turn_strength = self._get_hand_strength(player.cards, board, n_opponents, 4)
        if 3 in turns:
            pre_action_state.river_strength = self._get_hand_strength(player.cards, board, n_opponents, 5)
        pre_action_state.turn[turn.value] = 1
        pre_action_state.stack = player.stack
        pre_action_state.pot = self.dealer.pot
        pre_action_state.money_in_pot = player._chips_in_pot
        pre_action_state.call_amount = player._to_call
        for opponent in opponents:
            pre_action_state.oponent_money_in_pot[opponent.player_id] = opponent._chips_in_pot
            pre_action_state.oponent_stack[opponent.player_id] = opponent.stack
            pre_action_state.oponent_has_move_left[opponent.player_id] = 1 if opponent.stack>0 else 0

        available_moves = player._get_available_moves(self.dealer.max_opponent_stack(opponents))
        for move in available_moves:
            pre_action_state.legal_moves[move.value] = 1

        return pre_action_state

    def _update_move_history(self, player:Player, move_history:MoveDetails):
        # Get all field names of the opponent model
        fields = list(MoveHistory.model_fields.keys())

        # Pop left all fields
        for field in fields:
            getattr(self.move_history, field).popleft()
        move = [0 if move_history.move != Move(i) else 1 for i in range(4)]
        player_id = [1 if player.player_id == i else 0 for i in range(MAX_PLAYERS)]
        
        self.move_history.player_id.append(player_id)
        self.move_history.move.append(move)
        self.move_history.raise_amount.append(move_history.raise_amount)
        self.move_history.call_amount.append(move_history.call_amount)
        self.move_history.stack_after_move.append(player.stack)
        self.move_history.chips_in_pot_after_move.append(player._chips_in_pot)

    def _update_opponent_model(self, players:List[Player], board:List[int]):
        potential_winners = [player for player in players if player.last_move != Move.FOLD]
        fields = list(OpponentModel.model_fields.keys())

        for player in potential_winners:
            for field in fields:
                getattr(self.opponent_model, field).popleft()
            player_id = [1 if player.player_id == i else 0 for i in range(MAX_PLAYERS)]
            self.opponent_model.player_id.append(player_id)

            self.opponent_model.preflop_strength.append(self._get_hand_strength(player.cards, [], self.players_at_turn[0]))
            self.opponent_model.flop_strength.append(self._get_hand_strength(player.cards, board[:3], self.players_at_turn[1]))
            self.opponent_model.turn_strength.append(self._get_hand_strength(player.cards, board[:4], self.players_at_turn[2]))
            self.opponent_model.river_strength.append(self._get_hand_strength(player.cards, board[:5], self.players_at_turn[3]))

    def _get_hand_strength(self, cards:List[int], board:List[int], opponents:int, max_board_size:int=5) -> float:
        if max_board_size == 0:
            return self._get_preflop_strength(cards)
        hand = [Card.int_to_str(card) for card in cards]
        board_cards = [Card.int_to_str(card) for card in board]
        payload = {
            "hand":hand,
            "opponents": opponents,
            "startBoard":board_cards,
            "maxBoardSize":max_board_size
        }
            
        response = requests.post("http://localhost:8000/simulate", json=payload)
        return response.json()["winRate"]

    def _get_preflop_strength(self, cards:List[int]) -> float:
        cards_ordered = sorted(cards, reverse=True)
        hand = [Card.int_to_str(card) for card in cards_ordered]
        hand_str: str = hand[0][0]+hand[1][0]
        if hand[0][1] == hand[1][1]:
            hand_str += "s"
        return 1 - PREFLOP_RANKINGS[hand_str]

    def _get_flattened_observations(self, pre_action_state:PreActionState) -> np.ndarray:
        # Flattening each model instance
        pre_action_state_flat = list(self.flatten(pre_action_state.dict().values()))
        opponent_model_flat = list(self.flatten(self.opponent_model.dict().values()))
        move_history_flat = list(self.flatten(self.move_history.dict().values()))

        # Concatenating all flattened lists and converting to a NumPy array
        combined_flat_array = np.array(pre_action_state_flat + opponent_model_flat + move_history_flat)

        return combined_flat_array

    def flatten(self, container):
        for i in container:
            if isinstance(i, (list, deque)):
                for j in self.flatten(i):
                    yield j
            else:
                yield i
 
    def reset(self, seed=None):
        if self.start_new_game:
            self.opponent_model = OpponentModel()
            self.move_history = MoveHistory()
            self.game += 1
            n_players = random.randint(MIN_PLAYERS, MAX_PLAYERS)
            if MODE == Modes.RANDOM_PLAY:
                self.players = [RandomPlayer(i, START_STACK) for i in range(n_players)]
            else: 
                self.players = [AITrainer(0, START_STACK)] + [RandomPlayer(i, START_STACK) for i in range(1, n_players)]
            print_game_start(self.game, n_players)
            self.start_new_game = False

        self.dealer = Dealer()
        self.player_queue = deque(self.players)
        for player in self.player_queue:
            player.prepare_for_new_hand()

        self.dealer.collect_blinds(self.player_queue)
        self.dealer.deal_player_cards(self.player_queue)
        self.start_hands = {player.player_id: player.cards for player in self.player_queue} # For printing
        self.start_stack = self.get_stack(self.players, 0)

        obs, reward, done = self._itterate_hand(None)

        return obs, {}

    def render(self, mode='human'):
        pass

    def close(self):
        pass
