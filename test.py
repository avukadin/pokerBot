from poker_game.conductor import play
from time import time

if __name__ == '__main__':  
    start = time()
    play(3,6,10, printer=True)
    end = time()

    # Print total seconds passed
    print("Total time taken in seconds: ", end - start)
