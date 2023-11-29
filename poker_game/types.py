from dataclasses import dataclass
from enum import Enum

# Player Moves
class Move(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    NIL = "nil"

@dataclass
class MoveDetails:
    player_id: int
    move: Move
    call_amount: int = 0
    raise_amount: int = 0
