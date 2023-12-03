from poker_game.conductor import play
from time import time
from poker_game.params import MIN_PLAYERS, MAX_PLAYERS, NUM_GAMES

if __name__ == '__main__':  
    start = time()
    play(MIN_PLAYERS, MAX_PLAYERS, NUM_GAMES)
    end = time()

    # Print total seconds passed
    print("Total time taken in seconds: ", end - start)
