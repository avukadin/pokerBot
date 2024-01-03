import json
from typing import Dict, List
import os
import requests
import time
import random
from ml.params import MAX_SAMPLES, PROCESSED_DATA_PATH, VALID_HANDS_PATH
from ml.model import Hand, Meta

def next_hand():
    with open(VALID_HANDS_PATH, 'r') as file:
        total_lines = sum(1 for _ in file)
    print("Total lines in file:" + str(total_lines))

    indexes = set(random.sample(range(total_lines), MAX_SAMPLES))
    skip = set(["tourney", "holdempot"])
    with open(VALID_HANDS_PATH, 'r') as file:
        for index, line in enumerate(file):
            if index not in indexes:
                continue
            hand = json.loads(line)
            if hand["game"] not in skip:
                yield hand

def get_pot_change(hand:Dict):
    pots = [p["size"] for p in hand["pots"]]
    for i in range(-1, -len(pots), -1):
        pots[i] -= pots[i-1]
    return pots

def process_hand(hand:Dict) -> Dict:
    actions = []
    player_order = []
    stages = []
    for action, player, stage in get_action_in_order(hand):
        actions.append(action) 
        player_order.append(player)
        stages.append(stage)
    
    bets = []
    calls = []
    raises = []
    pot_changes = get_pot_change(hand)
    for i in range(4):
        players_round = [p[0] for p in zip(player_order, stages) if p[1] == i]
        actions_round = [a[0] for a in zip(actions, stages) if a[1] == i]
        bet_amount, call_amount, raise_amount = get_bet_sizes(players_round, actions_round, pot_changes[i])
        bets.extend(bet_amount)
        calls.extend(call_amount)
        raises.extend(raise_amount)

    player_meta = {}
    for player in hand["players"]:
        player_meta[player["user"]] = {"pocket_cards":player.get("pocket_cards", []), "bankroll":player["bankroll"]}
    meta = {"board":hand["board"], "players":player_meta}

    hand_strength = []
    for i in range(len(stages)):
        player = player_order[i]
        pocket_cards = player_meta[player]["pocket_cards"]
        board = meta["board"]
        stage = stages[i]
        opponents = len(set([p for p,s in zip(player_order, stages) if s == stage]))-1
        if opponents == 0:
            hand_strength.append(1)
        elif len(pocket_cards) == 0:
            hand_strength.append(-1)
        else:
            hand_strength.append(get_hand_strength(pocket_cards, board, stage, opponents))

    data = Hand(
        player_order = player_order,
        moves = actions,
        stage = stages,
        bets = bets,
        to_call = calls,
        raise_amount = raises,
        hand_strength =hand_strength,
        meta = Meta(**meta),
        time = hand[time]
    )
    
    return data.model_dump()

memo = {}
def get_hand_strength(pocket_cards:List[str], board:List[str], stage:int, opponents:int):
    if stage == 0:
        board_cards = []
    elif stage == 1:
        board_cards = board[0:3]
    elif stage == 2:
        board_cards = board[0:4]
    else:
        board_cards = board
    key = "".join(sorted(pocket_cards)+sorted(board_cards)) + str(opponents)
    if key in memo:
        return memo[key]
    
    payload = {
        "hand":pocket_cards,
        "opponents": opponents,
        "startBoard":board_cards,
        "maxBoardSize":5
    }
        
    response = requests.post("http://localhost:8000/simulate", json=payload)
    win_rate = round(response.json()["winRate"], 2)
    memo[key] = win_rate
    return win_rate

def get_bet_sizes(player_order:List[str], moves:List[str], pot_change:int):
    bets = [0]*len(player_order)
    # Blinds
    to_call = [0]*len(player_order)
    if moves[0] == "B":
        bets[0] = 1
        bets[1] = 2
        sb_player = player_order[0]

        # SB to call 1
        for i in range(2, len(moves)):
            if player_order[i] == sb_player:
                to_call[i] = 1
                break
            else:
                to_call[i] = 2

    for i in range(len(moves)):
        if moves[i] in ["r", "b"]:
            raise_player = player_order[i]
            for j in range(i+1, len(moves)):
                if player_order[j] == raise_player:
                    break
                to_call[j] += 2

    raise_amount = [0]*len(moves)
    for i in range(len(moves)):
        if moves[i] == "c":
            bets[i] = to_call[i]
        elif moves[i] in ["r", "b"]:
            bets[i] = to_call[i] + 2
            raise_amount[i] = 2

    total = sum(bets)
    if total > 0:
        factor = pot_change / total
        bets = [round(bet*factor) for bet in bets]
        to_call = [round(call*factor) for call in to_call]
        raise_amount = [round(raise_amount*factor) for raise_amount in raise_amount]
    return bets, to_call, raise_amount

def get_normalizing_factor(hand:Dict):
    players = hand["players"]
    max_stack = 0
    for player in players:
        max_stack = max(max_stack, player["bankroll"])
    return max(1/max_stack*1000, 1)

def get_start_stacks(hand:Dict):
    players = hand["players"]
    normalizing_factor = get_normalizing_factor(hand)
    stacks = [round(player["bankroll"]*normalizing_factor) for player in players]
    return stacks

def get_action_in_order(hand:Dict):
    players = hand["players"]
    players.sort(key=lambda x: x["pos"])
    
    for n, stage in enumerate(["p", "f", "t", "r"]):
        stage_bet_count = 0
        for player in players:
            for bet in player["bets"]:
                if bet["stage"] == stage:
                    stage_bet_count = max(stage_bet_count, len(bet["actions"]))
        
        for i in range(stage_bet_count):
            for player in players:
                for bet in player["bets"]:
                    if bet["stage"] == stage and len(bet["actions"]) > i:
                        yield bet["actions"][i], player["user"], n

def print_json(hand:Dict):
    json_formatted_str = json.dumps(hand, indent=2)
    print(json_formatted_str)

if __name__ == "__main__":
    # if os.path.exists(PROCESSED_DATA_PATH):
    #     os.remove(PROCESSED_DATA_PATH)
    
    t0 = time.time()
    data = []
    try:
        for hand in next_hand():
            data.append(process_hand(hand))
            if len(data)%50 == 0:
                time_left = (time.time()-t0)/len(data)*(MAX_SAMPLES-len(data))
                print(f"Hands Processed {round(100*len(data)/MAX_SAMPLES,2)}%, Minutes Left: {round(time_left/60,1)}", end="\r") 
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")

    # with open(PROCESSED_DATA_PATH, "a") as file:
    #     file.write(json.dumps(data))
