package main

import (
	"math"
	"math/rand"
	"sync"

	"github.com/chehsunliu/poker"
)

const SIMULATIONS = 10000
const N_OPPONENTS = 6
const N_THREADS = 10

var wins int

var wg sync.WaitGroup
var m = sync.Mutex{}

func Simulate(params *SimulationParams) float64{
	wins = 0

	wg.Add(N_THREADS)
	for i:=0; i<N_THREADS; i++{
		go simulate(SIMULATIONS/N_THREADS, params)
	}
	wg.Wait()

    	chances := math.Pow(float64(wins)/ float64((SIMULATIONS/N_THREADS)*N_THREADS), float64(params.Opponents))
	return chances
}

func simulate(simulations int, params *SimulationParams) {
	defer wg.Done()

	var deck [52]poker.Card = makeDeck()

	hand := make([]poker.Card, 2, 7)
	opponent := make([]poker.Card, 2, 7)
	board := make([]poker.Card, 5, 7)
	drawnCards := make(map[int]bool)

	for i, card:=range params.Hand {
		hand[i] = poker.NewCard(card)
	}
	for i, card:=range params.StartBoard {
		board[i] = poker.NewCard(card)
	}
	addDrawnCards(drawnCards, hand, board, deck)
	
	variableDrawnCards := make([]int, 5-len(params.StartBoard)+2)
	n := 0
	var ws int
	for i:=0; i<simulations; i++{
		var cardIndex int

		for j:=len(params.StartBoard); j<5; j++ {
			board[j], cardIndex = drawCard(deck, drawnCards)
			variableDrawnCards[n] = cardIndex
			n++
		}

		for j:=0; j<2; j++ {	
			opponent[j], cardIndex = drawCard(deck, drawnCards)
			variableDrawnCards[n] = cardIndex
			n++
		}

		ws += isBestHand(hand, opponent, board)

		n = 0
		for _, index := range variableDrawnCards{
			delete(drawnCards, index)
		} 

	}

	m.Lock()
	wins += ws
	m.Unlock()
}

func makeDeck() [52]poker.Card {
	deck := [52]poker.Card{}
	cards := poker.NewDeck()
	for i:=0; i<len(deck); i++ {
		deck[i] = cards.Draw(1)[0]
	}
	return deck
}

func drawCard(deck [52]poker.Card, drawnCards map[int]bool) (poker.Card, int) {
	for {	
		index := rand.Intn(len(deck))
		if _, ok := drawnCards[index]; !ok {
			drawnCards[index] = true
			return deck[index], index
		}
	}
}

func addDrawnCards(drawnCards map[int]bool, hand []poker.Card, board []poker.Card, deck [52]poker.Card){
	toAdd := make([]poker.Card, len(hand), len(hand) + len(board))
	copy(toAdd, hand)
	toAdd = append(toAdd, board...)

	indexes := make(map[string]int)

	for i, card := range deck{
		indexes[card.String()] = i
	}

	for _, card := range toAdd {
		index := indexes[card.String()]
		drawnCards[index] = true
	}
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

