from dataclasses import dataclass
from enum import Enum

# Player Moves
class Move(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE = 3
    NIL = 4

class Players(Enum):
    RANDOM = 0
    AI = 1
    EV = 2

@dataclass
class MoveDetails:
    player_id: int
    move: Move
    call_amount: int = 0
    raise_amount: int = 0

@dataclass
class ModelInput:
    player_id:int
    hand_id:int
    move:Move
    raise_amount:int



@dataclass
class Winner:
    player_id: int
    win_amount: int
    end_stack: int
