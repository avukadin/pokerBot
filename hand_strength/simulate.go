package main

import (
	"fmt"
	"math"
	"time"

	"github.com/chehsunliu/poker"
)

const SIMULATIONS = 10000
const N_OPPONENTS = 6

var start_hand = []string{"Kc", "4h"}
var start_board = []string{"2c", "3c", "4c"}

func main(){
	t0 := time.Now()
	simulate()
	fmt.Println(time.Since(t0))
}

func simulate() {

	hand := make([]poker.Card, 2, 7)
	opponent := make([]poker.Card, 2, 7)
	board := make([]poker.Card, 5)
	drawnCards := make([]poker.Card, 9)
	nDrawnCards := 0

	deck := poker.NewDeck()
	for i, card:=range start_hand {
		hand[i] = poker.NewCard(card)
		drawnCards[nDrawnCards] = hand[i]
		nDrawnCards++
	}
	for i, card:=range start_board {
		board[i] = poker.NewCard(card)
		drawnCards[nDrawnCards] = board[i]
		nDrawnCards++
	}

	var wins int = 0
	var played int = 0
	for i:=0; i<SIMULATIONS; i++{

		for j:=len(start_board); j<5; j++ {
			board[j] = drawCard(drawnCards, nDrawnCards, deck)
			drawnCards[nDrawnCards] = board[j]
			nDrawnCards++
		}

		for j:=0; j<2; j++ {	
			opponent[j] = drawCard(drawnCards, nDrawnCards, deck)
			drawnCards[nDrawnCards] = opponent[j]
			nDrawnCards++	
		}

		wins += isBestHand(hand, opponent, board)
		played++

		nDrawnCards = 2 + len(start_board)
	}
	chances := math.Pow(float64(wins)/float64(played), float64(N_OPPONENTS))
	fmt.Println(chances)	
}

func isBestHand(hand []poker.Card, opponent []poker.Card, board []poker.Card) int{
	fullHand := append(hand, board...)
	handRank := poker.Evaluate(fullHand)

	fullOpponent := append(opponent, board...)
	opponentRank := poker.Evaluate(fullOpponent)

	if handRank <= opponentRank {
		return 1
	} else {
		return 0
	}
}

func drawCard(drawnCards []poker.Card, nDrawnCards int, deck *poker.Deck) poker.Card {
	var card poker.Card

	validCard := false

	drawnCardsMap := make(map[int32]int8)
	for i:=0; i<nDrawnCards; i++ {
		card = drawnCards[i]
		drawnCardsMap[card.Rank()] = 1
	}

	for !validCard {
		if deck.Empty() {
			deck = poker.NewDeck()
		}

		card = deck.Draw(1)[0]

		if _, ok := drawnCardsMap[card.Rank()]; !ok {
			validCard = true
		}
	}

	return card
}
