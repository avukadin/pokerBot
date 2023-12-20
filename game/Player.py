import random
from typing import List, Tuple

from game.params import BIG_BLIND
from game.types import Move, MoveDetails

class Player:
    player_id: int

    _stack: int
    _chips_in_pot: int = 0
    _cards: List[int] = []
    _last_move: Move = Move.NIL
    _to_call: int = 0
    _is_big_blind: bool = False
    _is_small_blind: bool = False

    def __init__(self, player_id:int, stack: int):
        self.player_id = player_id
        self._stack = stack

    def make_move(self, last_raise_amount:int, max_opponent_stack:int, board:List[int], **kwargs) -> MoveDetails:

        moves = self._get_available_moves(max_opponent_stack)
        move = self._select_move(moves)

        move_details = MoveDetails(self.player_id, move)
        if move == Move.RAISE:
            min_raise, max_raise = self._get_raise_range(last_raise_amount, max_opponent_stack)
            raise_amount = self._get_raise_amount(min_raise, max_raise)
            assert raise_amount > 0

            self._stack -= (raise_amount + self._to_call)
            assert self._stack >= 0
            move_details.raise_amount = raise_amount
            move_details.call_amount = self._to_call
            self._to_call = 0

        elif move == Move.CALL:
            assert self._to_call > 0

            self._stack -= self._to_call
            assert self._stack >= 0
            move_details.call_amount = self._to_call
            self._to_call = 0

        elif move == Move.FOLD:
            self._to_call = 0
            self._cards = []

        self._last_move = move
        self._chips_in_pot += move_details.call_amount + move_details.raise_amount

        return move_details

    def set_new_round_state(self):
        self._to_call = 0
        self._last_move = Move.NIL

    def prepare_for_new_hand(self):
        self._cards = []
        self._to_call = 0
        self._last_move = Move.NIL
        self._chips_in_pot = 0

    def _get_available_moves(self, max_opponent_stack:int) -> List[Move]:
        available_moves = []

        if self._to_call == 0:
            available_moves.append(Move.CHECK)
        else:
            available_moves.append(Move.CALL)

        if self._stack > self._to_call and max_opponent_stack > 0:
            available_moves.append(Move.RAISE)

        if self._to_call > 0:
            available_moves.append(Move.FOLD)

        return available_moves

    def _select_move(self, moves: List[Move]) -> Move:
        raise NotImplementedError

    def _get_raise_range(self, last_raise_amount:int, max_opponent_stack:int) -> Tuple[int, int]:
        assert self._stack > self._to_call

        max_raise = self._stack - self._to_call
        max_raise = min(max_raise, max_opponent_stack)

        last_raise_or_big_blind = max(last_raise_amount, BIG_BLIND)
        min_raise = min(last_raise_or_big_blind, self._stack - self._to_call)
        min_raise = min(min_raise, max_opponent_stack)

        assert min_raise <= max_raise and min_raise > 0
        return min_raise, max_raise

    def _get_raise_amount(self, min_raise:int, max_raise:int) -> int:
        raise_amount = random.randint(min_raise, max_raise)
        return raise_amount

    def post_big_blind(self, big_blind: int) -> int:
        self._last_move = Move.RAISE
        amount = self.safe_take_from_stack(big_blind)
        self._chips_in_pot += amount
        return amount

    def post_small_blind(self, big_blind: int, small_blind: int) -> int:
        amount = self.safe_take_from_stack(small_blind)
        self.add_to_call(big_blind-small_blind)
        self._last_move = Move.RAISE
        self._chips_in_pot += amount
        return amount
    
    def safe_take_from_stack(self, amount: int):
        assert amount >= 0
        amount = min(amount, self._stack)
        self._stack -= amount
        return amount

    def add_to_call(self, amount: int):
        assert amount >= 0
        remaining = self._stack - self._to_call
        assert remaining>=0
        amount = min(amount, remaining)
        self._to_call += amount
        return amount

    # Getters and Setters
    @property
    def stack(self) -> int:
        return self._stack
 
    @stack.setter
    def stack(self, stack: int):
        self._stack = stack
        assert self._stack >= 0

    @property
    def cards(self) -> List[int]:
        return self._cards
    
    @cards.setter
    def cards(self, cards: List[int]):
        self._cards = cards

    @property
    def last_move(self) -> Move:
        return self._last_move

    @last_move.setter
    def last_move(self, last_move: Move):
        self._last_move = last_move

    @property
    def to_call(self) -> int:
        return self._to_call

    @to_call.setter
    def to_call(self, to_call: int):
        self._to_call = min(to_call, self.stack)
