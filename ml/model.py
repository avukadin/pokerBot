from pydantic import BaseModel
from typing import List, Dict

class PlayerInfo(BaseModel):
    pocket_cards: List[str]
    bankroll: int

class Meta(BaseModel):
    players: Dict[str, PlayerInfo]
    board: List[str]

class Hand(BaseModel):
    player_order: List[str]
    moves: List[str]
    stage: List[int]
    bets: List[int]
    to_call: List[int]
    raise_amount: List[int]
    hand_strength: List[float]
    meta: Meta
    time: str