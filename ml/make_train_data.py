import json
from typing import Dict, List
import random
import pickle
from ml.model import Hand
from ml.params import PROCESSED_DATA_PATH, MOVE_HISTORY, HS_TRAIN_DATA_PATH, MOVE_TRAIN_DATA_PATH
'''
predicting hand_strength

[fold, check, call, raise, raise_amount, hand_strength, to_call, is_p, is_f, is_t, is_r, chips_in_pot, stack, pot, n_opponents, position]
#Current state
[to_call, is_p, is_f, is_t, is_r, chips_in_pot, stack, pot, n_opponents, position]
train_data = [Current state, 50 past moves]

'''

MOVES = {"f":0, "k":1, "c":2, "b":3, "r":3}

def load_data() -> List[Hand]:
    data = []
    with open(PROCESSED_DATA_PATH, "r") as f:
        for hand in json.load(f):
            data.append(Hand(**hand))
    # order by time field, odlest to newest
    data.sort(key=lambda x: x.time)
    return data

def index_players(hands:List[Hand]):
    player_index = {}
    for i, hand in enumerate(hands):
        for player in hand.meta.players.keys():
            if player not in player_index:
                player_index[player] = [i]
            elif len(player_index[player]) <= 100:
                player_index[player].append(i)
    return player_index

def make_move_history(player:str, hand:Hand):
    """
    Creates an array:
    [is_fold, is_check, is_call, is_raise, raise_amount, hand_strength, to_call, is_p, is_f, is_t, is_r, chips_in_pot, stack, pot, n_opponents, position]
    """
    if sum(hand.to_call) == 0:
        return []
    
    player_turn_index = [i for i,p in enumerate(hand.player_order) if p == player]
    
    player_names = list(hand.meta.players.keys())
    max_stack = max([hand.meta.players[p].bankroll for p in player_names])
    
    normalizing_factor = 1/max_stack*1000
    moves_histories = []
    hand_id = "".join(hand.meta.board) + hand.time
    for index, i in enumerate(player_turn_index):
        move_history = []
        move = hand.moves[i]
        if move not in MOVES:
            continue
        move_one_hot = [0]*4
        move_one_hot[MOVES[move]] = 1
        move_history.extend(move_one_hot)

        move_history.append(round(hand.raise_amount[i]*normalizing_factor))

        move_history.append(hand.hand_strength[i])

        move_history.append(round(hand.to_call[i]*normalizing_factor))
        
        stage = [0]*4
        stage[hand.stage[i]] = 1
        move_history.extend(stage)

        chips_in_pot_before = round(sum([hand.bets[j] for j in player_turn_index[0:index] ])*normalizing_factor)
        move_history.append(chips_in_pot_before)

        start_bankroll = round(hand.meta.players[player].bankroll*normalizing_factor)
        move_history.append(max(start_bankroll-chips_in_pot_before,0))

        pot = round(sum([bet for j, bet in enumerate(hand.bets) if j < i ])*normalizing_factor)
        move_history.append(pot)

        folded_players = set()
        for j in range(i):
            if hand.moves[j] == "f":
                folded_players.add(hand.player_order[j])

        opponents = set([p for p in hand.player_order if p not in folded_players and p != player])
        move_history.append(len(opponents))
        
        position = 0
        for i in range(len(hand.player_order)):
            if hand.player_order[i] == player:
                break
            if hand.moves[i] != "-":
                position += 1
        move_history.append(position)
        move_history.append(hand_id)

        moves_histories.append(move_history)
    return moves_histories
    
def get_move_histories(player:str, hands:List[Hand], player_indexes:List[int]):
    
    move_histories = []
    for index in player_indexes:
        move_histories.extend(make_move_history(player, hands[index]))

    return move_histories
    
def make_train_exampes(move_history_train_data:List[List[float]], train_data:Dict):
    if len(move_history_train_data) == 0:
        return train_data
    ids = []
    for v in move_history_train_data:
        ids.append(v.pop())
    
    expected_length = MOVE_HISTORY*len(move_history_train_data[0])
    for i in range(len(move_history_train_data)):
        v1 =  move_history_train_data[i][6:]
        v2 = move_history_train_data[i-MOVE_HISTORY:i]

        v2_ids = ids[i-MOVE_HISTORY:i]
        hand_id = ids[i]
        
        input_vector = []
        for j in range(len(v2_ids)):
            if v2_ids[j] == hand_id:
                v2[j][5] = -1 # hand strength is unknown
            input_vector.extend(v2[j])
        input_vector += [0]*(expected_length-len(input_vector))
        input_vector = v1 + input_vector

        train_data["move_prediction"]["input"].append(input_vector)
        train_data["move_prediction"]["output"].append(move_history_train_data[i][0:4])

        if move_history_train_data[i][5] != -1:
            train_data["hand_prediction"]["input"].append(input_vector)
            train_data["hand_prediction"]["output"].append(move_history_train_data[i][5])

def shuffle_and_save(train_data:Dict, path:str):
    combined = list(zip(train_data["input"], train_data["output"]))
    random.shuffle(combined)
    train_data["input"][:], train_data["output"][:] = zip(*combined)

    print("Saving data", len(train_data["input"]), "examples")
    with open(path, 'wb') as handle:
        pickle.dump(train_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def make_train_data():
    hands = load_data()
    player_indexs = index_players(hands)
    train_data = {"move_prediction":{"input":[], "output":[]}, "hand_prediction":{"input":[], "output":[]}}
    n_players = len(player_indexs.keys())
    count = 0
    for player in player_indexs.keys():
        move_histories = get_move_histories(player, hands, player_indexs[player])
        make_train_exampes(move_histories, train_data)
        count += 1
        print("Processed", count, "of", n_players, "players", end="\r")
    
    shuffle_and_save(train_data["move_prediction"], MOVE_TRAIN_DATA_PATH)
    shuffle_and_save(train_data["hand_prediction"], HS_TRAIN_DATA_PATH)

if __name__ == "__main__":
    make_train_data()
