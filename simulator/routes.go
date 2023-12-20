package main

import (
	"github.com/go-chi/chi"
	chimiddle "github.com/go-chi/chi/middleware"
)

type SimulationResponse struct {
	WinRate float64 `json:"winRate"`
}

type SimulationParams struct {
	StartBoard []string
	Hand []string
	Opponents int
	MaxBoardSize int
}

func Handler(r *chi.Mux) {
	r.Use(chimiddle.StripSlashes)
	r.Route("/", func(router chi.Router) {
		router.Post("/simulate", RunSimulation)
	})
}
