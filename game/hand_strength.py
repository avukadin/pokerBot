
from typing import List
import requests

from treys import Card

from game.pre_flop_rankings import PREFLOP_RANKINGS


def get_hand_strength(cards:List[int], board:List[int], opponents:int, max_board_size:int=5) -> float:
    if max_board_size == 0:
        return get_preflop_strength(cards)
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

def get_preflop_strength(cards:List[int]) -> float:
    cards_ordered = sorted(cards, reverse=True)
    hand = [Card.int_to_str(card) for card in cards_ordered]
    hand_str: str = hand[0][0]+hand[1][0]
    if hand[0][1] == hand[1][1]:
        hand_str += "s"
    return 1 - PREFLOP_RANKINGS[hand_str]

