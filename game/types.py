from dataclasses import dataclass
from enum import Enum

class Actions(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2

    RAISE_1 = 3
    RAISE_2 = 4
    RAISE_3 = 5
    RAISE_4 = 6
    RAISE_5 = 7
    RAISE_6 = 8
    RAISE_7 = 9
    RAISE_8 = 10
    RAISE_9 = 11
    RAISE_10 = 12

# Player Moves
class Move(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    NIL = "nil"

class Turn(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

class Modes(Enum):
    TRAIN = 0
    RANDOM_PLAY = 1
    TRAINED_PLAY = 2

class Players(Enum):
    RANDOM = 0
    AI_TRAINER = 1

@dataclass
class MoveDetails:
    player_id: int
    move: Move
    call_amount: int = 0
    raise_amount: int = 0

@dataclass
class TrainingData:
    player_id: int
    turn: Turn
    stack: int
    call_amount: int
    raise_amount: int
    pot: int
    opponent_strength: float = 0.0 # probability opponent has best hand, before reveal
    pre_flop_strength: float = 0.0 # probability player has best hand at the pre-flop
    flop_strength: float = 0.0 # probability player has best hand at the flop
    turn_strength: float = 0.0 # probability player has best hand at the turn
    river_strength: float = 0.0 # probability player has best hand at the river
    won_amount: int = 0
    
@dataclass
class Winner:
    player_id: int
    win_amount: int
    end_stack: int

